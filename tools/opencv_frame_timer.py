#!/usr/bin/env python3
"""
Measure app-side frame arrival intervals and jitter from a camera/URL.
Useful for sanity-checking FPS and arrival jitter. For WebRTC, prefer getStats.
Requires: opencv-python
"""
import argparse, time, statistics, cv2

def main(src=0, warmup=30, samples=300):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open source: {src}")
    for _ in range(warmup):
        ret, _ = cap.read()
        if not ret: break
    times = []
    last = time.perf_counter()
    for i in range(samples):
        ret, frame = cap.read()
        if not ret: break
        now = time.perf_counter()
        times.append((now - last)*1000.0)
        last = now
    cap.release()
    if not times:
        print("no frames"); return
    mean = statistics.mean(times)
    p95 = statistics.quantiles(times, n=20)[18]
    print(f"inter_frame_ms_avg={mean:.2f} p95={p95:.2f} n={len(times)}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=0, help="camera index or URL")
    ap.add_argument("--samples", type=int, default=300)
    ap.add_argument("--warmup", type=int, default=30)
    a = ap.parse_args()
    main(a.src, a.warmup, a.samples)
