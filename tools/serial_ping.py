#!/usr/bin/env python3
"""
USB-serial roundtrip tester: measure write->echo->read latency, throughput, jitter.
Use with a device that echoes back exactly what it receives.
"""
import argparse, time, statistics, sys
import serial

def run(port, baud=1_000_000, iters=500, payload=32, rtscts=False, xonxoff=False, timeout=1.0):
    ser = serial.Serial(port=port, baudrate=baud, timeout=timeout, rtscts=rtscts, xonxoff=xonxoff)
    data = bytes([i % 256 for i in range(payload)])
    # warmup
    for _ in range(5):
        ser.write(data); ser.flush()
        ser.read(len(data))
    samples = []
    for i in range(iters):
        t0 = time.perf_counter()
        ser.write(data); ser.flush()
        got = ser.read(len(data))
        t1 = time.perf_counter()
        if len(got) != len(data):
            print(f"warn: short read at iter {i} ({len(got)}/{len(data)})", file=sys.stderr)
            continue
        samples.append((t1 - t0) * 1000.0)
    ser.close()
    if not samples:
        raise SystemExit("no samples")
    avg = statistics.mean(samples)
    p95 = statistics.quantiles(samples, n=20)[18]
    print(f"roundtrip_ms_avg={avg:.3f} p95={p95:.3f} iters={len(samples)}")
    # serialization estimate
    ser_ms = (payload * 8 / baud) * 1000.0
    print(f"serialization_ms_est={ser_ms:.3f} (payload={payload}B baud={baud})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=1_000_000)
    ap.add_argument("--iters", type=int, default=500)
    ap.add_argument("--payload", type=int, default=32)
    ap.add_argument("--rtscts", action="store_true")
    ap.add_argument("--xonxoff", action="store_true")
    args = ap.parse_args()
    run(args.port, baud=args.baud, iters=args.iters, payload=args.payload, rtscts=args.rtscts, xonxoff=args.xonxoff)
