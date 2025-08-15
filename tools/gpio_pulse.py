#!/usr/bin/env python3
"""
Jetson GPIO pulse generator/listener.
- TX mode: toggles a pin around a software event (e.g., just before USB write).
- RX mode: timestamps pulses from a sensor/driver pin to correlate with scope/LA.
Requires Jetson.GPIO (or adjust for RPi.GPIO).
"""
import argparse, time, statistics, sys

def tx(pin=18, hz=0, duration=1.0):
    import Jetson.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    t_end = time.time() + duration
    if hz <= 0:
        # single strobe
        GPIO.output(pin, GPIO.HIGH); time.sleep(0.001); GPIO.output(pin, GPIO.LOW)
    else:
        period = 1.0/hz
        while time.time() < t_end:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(period/2)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(period/2)
    GPIO.cleanup()

def rx(pin=16, duration=2.0):
    import Jetson.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.IN)
    edges = []
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=lambda ch: edges.append(time.perf_counter()))
    time.sleep(duration)
    GPIO.cleanup()
    if edges:
        diffs = [ (edges[i]-edges[i-1])*1000.0 for i in range(1,len(edges)) ]
        print(f"edges={len(edges)} diff_ms_avg={statistics.mean(diffs):.3f}")
    else:
        print("no edges captured")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["tx","rx"], required=True)
    ap.add_argument("--pin", type=int, default=18)
    ap.add_argument("--hz", type=float, default=0)
    ap.add_argument("--duration", type=float, default=1.0)
    args = ap.parse_args()
    if args.mode == "tx":
        tx(pin=args.pin, hz=args.hz, duration=args.duration)
    else:
        rx(pin=args.pin, duration=args.duration)
