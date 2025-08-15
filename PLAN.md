# Teleop Latency – Measurement Plan

Doel: alle parameters uit de Excel **meten** (ipv schatten) voor jouw SO100↔SO100 teleop met WebRTC/Jetson.

## Volgorde (goedkoop → duur)
1) **Software/Config** (lokaal, goedkoop)
   - Control loop period & jitter (Python timestamps)
   - USB-serial latency + payload/baud invloed (serial ping)
   - Packetization overhead (measure in-process timestamps)
2) **Netwerk** (gratis tooling)
   - RTT/Jitter: ICMP, UDP, MTR
   - Doorvoer & bufferbloat: iperf3 + CAKE/ECN tests
3) **Video-pad** (half goedkoop)
   - Camera → NVENC → WebRTC encode timestamps
   - Jitter buffer/decoder/render via `getStats()`
   - Display vsync (estimate: 8.3 ms @60 Hz)
4) **Mechanica/Actuatie** (lastig/“duur”)
   - Driver processing, deadband
   - Backlash & accel-to-motion (scope/LA + IMU/high-speed camera)

> Tip: werk per stap met **GPIO pulsen** als “truth markers” en een **logic analyzer** of **oscilloscoop**.

---

## Meetcases en targets

### A. Leader (Human → Packet)
- **Leader sensor sampling (ms)**: tijd tussen USB-read calls → sample arrival.
- **Control loop sched avg (ms)**: helft van periode `1000/Hz/2` + jitter logging.
- **OS scheduling jitter (ms)**: p95 van loop-interval – ideale periode.
- **Leader USB serialization (ms)**: `(bytes*8/baud)*1000` → verifieer met ping.
- **Leader USB overhead (ms)**: host timestamps rond write/read (excl. serialization).
- **Command packetization (ms)**: time from ‘control cmd ready’ → ‘datagram sent’.

### B. Command Network (one-way)
- **Geodesic + routing factor** uit model; verifieer met TCP/UDP RTT en MTR (padinflatie).
- **Command network extra (ms)**: pkt-size kleine UDP; p50 one-way ≈ (RTT/2 - fiber time).

### C. Follower (Packet → Motion)
- **Follower USB serialization/overhead**: idem Leader.
- **Motor driver processing (ms)**: USB write GPIO toggle → driver PWM GPIO toggle.
- **Deadband (ms)**: cmd amplitude sweep; tijd tot motion event.
- **Backlash/slop (ms)**: richtingwissel vs eerste beweging (encoder/IMU).
- **Accel to visible motion (ms)**: cmd step → IMU accel onset of HS-camera frame.

### D. Video (Motion → Photon)
- **Exposure/rolling shutter (ms)**: camera spec; valideren via LED-flash test.
- **Frame period avg wait**: `1/(2*FPS)`.
- **Encode latency (ms)**: pre-encode ts → RTP send ts (getStats `framesEncoded` timing).
- **Packetization/FEC**: verschil RTP timestamp vs ICE/DTLS send time.
- **Network (one-way)**: padinflatie uit MTR + extra overhead (queue).
- **Jitter buffer target (ms)**: `getStats` jitterBufferDelay / playoutDelay.
- **Decode/Render**: `getStats` + OS compositor.
- **Vsync avg wait**: ≈ 8.3 ms @60Hz.

---

## Synchronisatie & tools
- **NTP/PTP** op beide kanten; voor one-way geliefd: PTP of GPSDO. Anders focus op RTT/2.
- **GPIO markers** op Jetson + scope/LA om softwareevents tegen fysieke beweging te pinnen.
- **High-speed camera** of IMU om ‘visible motion’ te detecteren.
- **WebRTC getStats** via meegeleverde `webrtc_stats.html` (export JSON).

---

## Logging-formaat (CSV/JSON)
Zet per meet run een JSON:
```json
{
  "run_id": "2025-08-15T14:32Z",
  "scenario": "Typical",
  "leader": {"sensor_ms": 2.1, "loop_avg_ms": 4.2, "jitter_ms_p95": 1.9, "usb_ser_ms": 0.26, "usb_ovh_ms": 1.0, "pkt_ms": 1.2},
  "network": {"rtt_ms_p50": 21.5, "rtt_ms_p95": 37.9, "mtr_hops": 15},
  "follower": {"usb_ser_ms": 0.26, "usb_ovh_ms": 1.0, "driver_ms": 3.0, "deadband_ms": 0.4, "backlash_ms": 9.7, "accel_visible_ms": 24.8},
  "video": {"exposure_ms": 6.0, "frame_half_ms": 16.7, "encode_ms": 12.2, "pkt_ms": 1.3, "fec_ms": 1.0, "net_ms": 22.3, "jitterbuf_ms": 30.0, "decode_ms": 8.1, "render_ms": 4.8, "vsync_ms": 8.3}
}
```
Deze kun je handmatig in de Excel **Typical** kolom zetten of via een import-script (zeg het als je dat wilt).

---

## Veiligheid
- Zet mechanica op **lage snelheid**; noodstop binnen handbereik.
- Gebruik **current limiting** op drivers tijdens test.
- Markeer bewegende delen; gebruik HS-camera i.p.v. hand/ogen dicht bij arm.
