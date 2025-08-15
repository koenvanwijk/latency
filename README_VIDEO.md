# 📹 Video Path – Meten en Draaien op één plek

Deze sectie helpt je om **end-to-end video-latency** te meten en lokaal te draaien (Jetson ↔ browser).

## A) LED‑flash methode (full path, goedkoop)
1. Laat een LED nabij de camera **aan/uit** gaan (bijv. via ESP32‑C3).
2. Stream naar je browser (zie C).
3. Neem met een **high‑speed camera** (bv. 240 fps) LED + scherm tegelijk op.
4. Analyseer:
   ```bash
   python tools/video_led_tester.py --video clip.mp4 \
     --led-roi 50,200,40,40 --scr-roi 900,300,60,60 --threshold 200 --fps 240
   ```
   Output geeft `latency_ms`.

## B) WebRTC stats (componenten in de browser)
- Open `tools/webrtc_stats.html` en plak de JSON van `RTCPeerConnection.getStats()` uit je app.
- Het script vat o.a. **jitterBuffer_ms, decode_ms, encode_ms** samen.

## C) Jetson → browser via WebRTC (1 plek, lokaal)
### Optie 1 — Snel starten (Python, software‑encode)
Werkt ook op Jetson. Goed voor **functionele** tests (geen NVENC).

Installeren:
```bash
pip install aiortc aiohttp opencv-python
```

Start server (op Jetson of op je laptop met camera):
```bash
python tools/jetson_webrtc_server.py --device /dev/video0 --width 640 --height 480 --fps 30 --host 0.0.0.0 --port 8080
```
Open in je browser: `http://<JETSON_IP>:8080/` en klik **Start**.

**Tip:** Verlaag resolutie/FPS als CPU het zwaar krijgt.

### Optie 2 — Jetson NVENC (GStreamer, H.264)
Gebruik de NVENC pipeline voor **lage latency** hardware-encode (H.264):

```bash
sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-{base,good,bad}   gstreamer1.0-plugins-ugly gstreamer1.0-libav gir1.2-gst-plugins-bad-1.0

# Voor USB camera:
./tools/gst_jetson_stream.sh /dev/video0 1280x720 30 out.sdp
```

Voor echte WebRTC heb je een signaling + `webrtcbin` pipeline nodig. Zeg het als je
een **webrtcbin + signaling** voorbeeld wilt; ik lever dan een kant‑en‑klare sender/viewer.

---

## D) Meetdelen koppelen aan Excel
- **Exposure/rolling-shutter (ms)**: LED‑flash (A) of cameraspec.
- **Encode (ms)**: `webrtc_stats.html` → `derived.encode_ms`.
- **Jitter buffer target (ms)**: `webrtc_stats.html` → `derived.jitterBuffer_ms` (gemiddeld).
- **Decode (ms)**: `webrtc_stats.html` → `derived.decode_ms`.
- **VSync gemiddeld (ms)**: ≈ 8.3 @ 60 Hz (pas aan per monitor).
