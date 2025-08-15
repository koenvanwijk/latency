#!/usr/bin/env python3
import sys, json
from pathlib import Path
import pandas as pd

COST_COLOR = {"Software":"#E2EFDA", "Config":"#E2EFDA", "Hardware":"#F8CBAD", "Infra":"#F4CCCC"}

def extract(excel_path: Path, scenario: str):
    df = pd.read_excel(excel_path, sheet_name="Inputs", header=5, usecols="A:H").rename(columns={
        "Parameter":"param","Description":"desc","Best":"best","Typical":"typical","Worst":"worst","Selected":"sel","Notes":"notes","Cost Type":"cost"
    })
    col = {"Best":"best","Typical":"typical","Worst":"worst","Selected":"sel"}[scenario]

    def get(name):
        row = df.loc[df["param"] == name]
        if row.empty: raise KeyError(f"Param '{name}' not found")
        v = row[col].values[0]
        if pd.isna(v): raise ValueError(f"Param '{name}' is empty for {scenario}")
        return float(v)

    def cost(name, default="Software"):
        row = df.loc[df["param"] == name, "cost"]
        if row.empty or pd.isna(row.values[0]): return default
        return str(row.values[0])

    # Leader
    leader = [
        {"name":"Leader sensor sampling", "ms": get("Leader sensor sampling (ms)"), "color": COST_COLOR.get(cost("Leader sensor sampling (ms)"))},
        {"name":"Control loop sched avg", "ms": (1000.0/get("Control loop rate (Hz)"))/2.0, "color": COST_COLOR.get(cost("Control loop rate (Hz)"))},
        {"name":"OS scheduling jitter", "ms": get("OS scheduling jitter (ms)"), "color": COST_COLOR.get(cost("OS scheduling jitter (ms)"))},
        {"name":"Leader USB serialization", "ms": (get("Leader USB payload size (bytes)")*8.0)/get("Leader USB serial baud rate (bps)")*1000.0, "color": COST_COLOR.get(cost("Leader USB payload size (bytes)"))},
        {"name":"Leader USB overhead", "ms": get("Leader USB overhead (ms)"), "color": COST_COLOR.get(cost("Leader USB overhead (ms)"))},
        {"name":"Command packetization", "ms": get("Command packetization (ms)"), "color": COST_COLOR.get(cost("Command packetization (ms)"))},
    ]

    # Network cmd
    cmd_net = (get("Straight-line distance (km)")*get("Distance routing factor"))/get("Fiber speed (km/ms)") + get("Command network extra (ms)")

    # Follower
    follower = [
        {"name":"Follower USB serialization", "ms": (get("Follower USB payload size (bytes)")*8.0)/get("Follower USB serial baud rate (bps)")*1000.0, "color": COST_COLOR.get(cost("Follower USB payload size (bytes)"))},
        {"name":"Follower USB overhead", "ms": get("Follower USB overhead (ms)"), "color": COST_COLOR.get(cost("Follower USB overhead (ms)"))},
        {"name":"Control loop sched avg", "ms": (1000.0/get("Control loop rate (Hz)"))/2.0, "color": COST_COLOR.get(cost("Control loop rate (Hz)"))},
        {"name":"OS scheduling jitter", "ms": get("OS scheduling jitter (ms)"), "color": COST_COLOR.get(cost("OS scheduling jitter (ms)"))},
        {"name":"Motor driver processing", "ms": get("Motor driver processing (ms)"), "color": COST_COLOR.get(cost("Motor driver processing (ms)"))},
        {"name":"Servo command deadband", "ms": get("Servo command deadband (ms)"), "color": COST_COLOR.get(cost("Servo command deadband (ms)"))},
        {"name":"Mechanical backlash/slop", "ms": get("Mechanical backlash/slop (ms)"), "color": COST_COLOR.get(cost("Mechanical backlash/slop (ms)"))},
        {"name":"Motor accel to visible motion", "ms": get("Motor accel to visible motion (ms)"), "color": COST_COLOR.get(cost("Motor accel to visible motion (ms)"))},
    ]

    # Video
    video_net = (get("Straight-line distance (km)")*get("Distance routing factor"))/get("Fiber speed (km/ms)") + get("Extra network overhead (ms)") + get("TURN/SFU extra hops (ms)")
    video = [
        {"name":"Sensor exposure", "ms": get("Exposure/rolling-shutter share (ms)"), "color": COST_COLOR.get(cost("Exposure/rolling-shutter share (ms)"))},
        {"name":"Frame period avg wait", "ms": (1000.0/get("Camera FPS (Hz)"))/2.0, "color": COST_COLOR.get(cost("Camera FPS (Hz)"))},
        {"name":"Sensor to memory/ISP", "ms": get("Sensor → memory/ISP (ms)"), "color": COST_COLOR.get(cost("Sensor → memory/ISP (ms)"))},
        {"name":"Capture buffer", "ms": get("Capture buffer (ms)"), "color": COST_COLOR.get(cost("Capture buffer (ms)"))},
        {"name":"Encode latency", "ms": get("Encode latency (ms)"), "color": COST_COLOR.get(cost("Encode latency (ms)"))},
        {"name":"Packetization", "ms": get("Packetization (ms)"), "color": COST_COLOR.get(cost("Packetization (ms)"))},
        {"name":"FEC/RED overhead", "ms": get("FEC/RED overhead (ms)"), "color": COST_COLOR.get(cost("FEC/RED overhead (ms)"))},
        {"name":"Network one-way (video)", "ms": video_net, "color": "#F4CCCC"},
        {"name":"Jitter buffer target", "ms": get("Jitter buffer target (ms)"), "color": COST_COLOR.get(cost("Jitter buffer target (ms)"))},
        {"name":"Decode latency", "ms": get("Decode latency (ms)"), "color": COST_COLOR.get(cost("Decode latency (ms)"))},
        {"name":"Renderer/compositor", "ms": get("Renderer/compositor (ms)"), "color": COST_COLOR.get(cost("Renderer/compositor (ms)"))},
        {"name":"Vsync avg wait", "ms": get("Vsync avg wait (ms)"), "color": COST_COLOR.get(cost("Vsync avg wait (ms)"))},
    ]

    lanes = {"Leader": leader, "Network":[{"name":"Command network one-way", "ms": cmd_net, "color":"#F4CCCC"}], "Follower": follower, "Video": video}
    totals = {k: round(sum(s["ms"] for s in v), 3) for k, v in lanes.items()}
    overall = round(sum(totals.values()), 3)
    return {"lanes": lanes, "totals": totals, "overall": overall}

def main():
    excel = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/Teleop_Latency_Model_SO100_WebRTC_v3.xlsx")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("site/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    for scenario in ["Best","Typical","Worst"]:
        data = extract(excel, scenario)
        (out_dir / f"latency_{scenario}.json").write_text(json.dumps(data, indent=2))
    print("Wrote JSON to", out_dir)

if __name__ == "__main__":
    main()
