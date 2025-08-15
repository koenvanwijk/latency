#!/usr/bin/env python3
"""
Generate a teleop latency swimlane diagram from the Excel Inputs sheet.

Usage:
  python src/make_swimlane_from_excel.py examples/Teleop_Latency_Model_SO100_WebRTC_v3.xlsx out.png
If arguments are omitted, defaults are used.
"""
import sys
from pathlib import Path
import pandas as pd
from graphviz import Digraph

def build_diagram(excel_path, out_png, use_column="Typical"):
    excel_path = Path(excel_path)
    df = pd.read_excel(excel_path, sheet_name="Inputs", header=5, usecols="A:H").rename(columns={
        "Parameter":"param","Description":"desc","Best":"best","Typical":"typical","Worst":"worst","Selected":"sel","Notes":"notes","Cost Type":"cost"
    })
    col = {"Best":"best","Typical":"typical","Worst":"worst","Selected":"sel"}[use_column]

    def get_val(name: str):
        row = df.loc[df["param"] == name]
        if row.empty:
            raise KeyError(f"Parameter not found: {name}")
        v = row[col].values[0]
        if pd.isna(v):
            raise ValueError(f"Value for '{name}' in column '{use_column}' is empty.")
        return float(v)

    # Leader
    leader_stages = [
        ("Leader sensor sampling", get_val("Leader sensor sampling (ms)")),
        ("Control loop sched avg", (1000.0/get_val("Control loop rate (Hz)"))/2.0),
        ("OS scheduling jitter", get_val("OS scheduling jitter (ms)")),
        ("Leader USB serialization", (get_val("Leader USB payload size (bytes)")*8.0)/get_val("Leader USB serial baud rate (bps)")*1000.0),
        ("Leader USB overhead", get_val("Leader USB overhead (ms)")),
        ("Command packetization", get_val("Command packetization (ms)")),
    ]

    # Command network one-way
    cmd_net_one_way = (
        (get_val("Straight-line distance (km)") * get_val("Distance routing factor")) / get_val("Fiber speed (km/ms)")
        + (get_val("Command network extra (ms)"))
    )

    # Follower
    follower_stages = [
        ("Follower USB serialization", (get_val("Follower USB payload size (bytes)")*8.0)/get_val("Follower USB serial baud rate (bps)")*1000.0),
        ("Follower USB overhead", get_val("Follower USB overhead (ms)")),
        ("Control loop sched avg", (1000.0/get_val("Control loop rate (Hz)"))/2.0),
        ("OS scheduling jitter", get_val("OS scheduling jitter (ms)")),
        ("Motor driver processing", get_val("Motor driver processing (ms)")),
        ("Servo command deadband", get_val("Servo command deadband (ms)")),
        ("Mechanical backlash/slop", get_val("Mechanical backlash/slop (ms)")),
        ("Motor accel to visible motion", get_val("Motor accel to visible motion (ms)")),
    ]

    # Video
    video_net_one_way = (
        (get_val("Straight-line distance (km)") * get_val("Distance routing factor")) / get_val("Fiber speed (km/ms)")
        + get_val("Extra network overhead (ms)") + get_val("TURN/SFU extra hops (ms)")
    )
    video_stages = [
        ("Sensor exposure", get_val("Exposure/rolling-shutter share (ms)")),
        ("Frame period avg wait", (1000.0/get_val("Camera FPS (Hz)"))/2.0),
        ("Sensor to memory/ISP", get_val("Sensor → memory/ISP (ms)")),
        ("Capture buffer", get_val("Capture buffer (ms)")),
        ("Encode latency", get_val("Encode latency (ms)")),
        ("Packetization", get_val("Packetization (ms)")),
        ("FEC/RED overhead", get_val("FEC/RED overhead (ms)")),
        ("Network one-way (video)", video_net_one_way),
        ("Jitter buffer target", get_val("Jitter buffer target (ms)")),
        ("Decode latency", get_val("Decode latency (ms)")),
        ("Renderer/compositor", get_val("Renderer/compositor (ms)")),
        ("Vsync avg wait", get_val("Vsync avg wait (ms)")),
    ]

    lanes = {"Leader": leader_stages, "Network":[("Command network one-way", cmd_net_one_way)], "Follower": follower_stages, "Video": video_stages}
    totals = {k: sum(v for _, v in steps) for k, steps in lanes.items()}
    overall = sum(totals.values())

    g = Digraph("SwimlaneFromExcel", format="png")
    g.attr(rankdir="LR")

    for lane, steps in lanes.items():
        with g.subgraph(name=f"cluster_{lane}") as c:
            c.attr(label=f"{lane} (total {totals[lane]:.1f} ms)", style="filled", color="lightgrey", fontsize="20")
            prev = None
            for i, (nm, ms) in enumerate(steps):
                nid = f"{lane}_{i}"
                c.node(nid, f"{nm}\\n{ms:.1f} ms", shape="box", style="filled", fillcolor="white")
                if prev:
                    c.edge(prev, nid)
                prev = nid

    g.edge("Leader_5", "Network_0")
    g.edge("Network_0", "Follower_0")
    g.edge("Follower_7", "Video_0")
    g.edge("Leader_0", "Follower_0", style="dashed", label="Direct timing")
    g.edge("Video_0", "Video_11", style="dashed", label="Video-only")

    g.node("TotalNode", f"Overall Command→Photon\\n{overall:.1f} ms", shape="note", style="filled", fillcolor="lightyellow")
    g.edge("Video_11", "TotalNode", style="bold")

    out = Path(out_png)
    g.render(str(out.with_suffix("")), cleanup=True)
    return str(out)

if __name__ == "__main__":
    excel = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("examples/Teleop_Latency_Model_SO100_WebRTC_v3.xlsx")
    out_png = sys.argv[2] if len(sys.argv) > 2 else "teleop_latency_swimlane_from_excel.png"
    col = sys.argv[3] if len(sys.argv) > 3 else "Typical"  # Best|Typical|Worst|Selected (Selected needs Excel calc)
    print("Using:", excel, "->", out_png, "| column:", col)
    p = build_diagram(excel, out_png, use_column=col)
    print("Wrote:", p)
