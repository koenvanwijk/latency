#!/usr/bin/env python3
"""
video_led_tester.py
-------------------
Meet end-to-end videolatentie uit een high‑speed opname (bijv. smartphone @240fps)
waarin tegelijk de fysieke LED (bij de camera) en jouw scherm te zien zijn.

Werkwijze:
1) Neem een korte clip op waarin de LED snel aan/uit gaat en de browser (weergave) in beeld is.
2) Geef twee ROI's op: één rond de LED, één rond het schermgebied waar de LED zichtbaar wordt.
3) Script detecteert de eerste "aan" overgang in LED-ROI en de eerste "helder" frame in scherm-ROI.
4) Delta_frames × (1000 / fps) = latency (ms).

Gebruik:
  python tools/video_led_tester.py --video path/to/clip.mp4 \
      --led-roi x,y,w,h --scr-roi x,y,w,h --threshold 200 --fps 240

Opmerkingen:
- Als de video geen FPS meldt, geef je zelf --fps.
- Demp je omgeving (geen grote lichtschommelingen).
- Voor rolling‑shutter/exposure beïnvloeding kan je meerdere toggles doen en mediane waarde nemen.
"""
import argparse, cv2, numpy as np

def parse_roi(s):
    x,y,w,h = map(int, s.split(','))
    return (x,y,w,h)

def avg_luma(img):
    # Y' from BGR approx
    return float(0.114*img[:,:,0].mean() + 0.587*img[:,:,1].mean() + 0.299*img[:,:,2].mean())

def detect_first_on(cap, roi, thresh, warm=5):
    """Return (frame_index, luma_series) of first frame crossing threshold."""
    x,y,w,h = roi
    lumas = []
    idx = -1
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok: break
        if i < warm:
            i += 1
            continue
        crop = frame[y:y+h, x:x+w]
        l = avg_luma(crop)
        lumas.append(l)
        if idx < 0 and l >= thresh:
            idx = i - warm
            break
        i += 1
    return idx, lumas

def main(args):
    cap = cv2.VideoCapture(args.video)
    if not cap.isOpened():
        raise SystemExit(f"Cannot open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        if not args.fps:
            raise SystemExit("Video FPS unknown; provide --fps")
        fps = args.fps
    # Read whole video into frames? No, we do two passes by reopening.
    # Pass 1: LED ROI
    cap1 = cv2.VideoCapture(args.video); cap2 = cv2.VideoCapture(args.video)
    led_idx, _ = detect_first_on(cap1, args.led_roi, args.threshold, warm=args.warmup)
    scr_idx, _ = detect_first_on(cap2, args.scr_roi, args.threshold, warm=args.warmup)
    cap1.release(); cap2.release()

    if led_idx < 0 or scr_idx < 0:
        print(f"no transition detected. led_idx={led_idx}, scr_idx={scr_idx}")
        return
    delta_frames = scr_idx - led_idx
    delta_ms = (delta_frames / fps) * 1000.0
    print(f"led_frame={led_idx} screen_frame={scr_idx} delta_frames={delta_frames} fps={fps:.2f} latency_ms={delta_ms:.2f}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="pad naar hs-opname (mp4/mov)")
    ap.add_argument("--led-roi", type=parse_roi, required=True, help="x,y,w,h rondom fysieke LED")
    ap.add_argument("--scr-roi", type=parse_roi, required=True, help="x,y,w,h rondom LED op het scherm")
    ap.add_argument("--threshold", type=float, default=200.0, help="luma drempel voor 'aan' (0..255)")
    ap.add_argument("--fps", type=float, default=0.0, help="overschrijf fps als container onjuist is")
    ap.add_argument("--warmup", type=int, default=5, help="frames overslaan aan het begin")
    args = ap.parse_args()
    main(args)
