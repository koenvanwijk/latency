#!/usr/bin/env python3
"""
jetson_webrtc_server.py
-----------------------
Eenvoudige WebRTC streamer (lokaal) met software encode (aiortc).
Niet NVENC: voor lage CPU en ultralage latency op Jetson liever GStreamer + webrtcbin.

Gebruik:
  pip install aiortc aiohttp opencv-python
  python tools/jetson_webrtc_server.py --device /dev/video0 --width 640 --height 480 --fps 30 --host 0.0.0.0 --port 8080
Open dan http://<host>:8080/ in de browser en klik 'Start'.

"""
import argparse, asyncio, json, os
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.signaling import BYE
from av import VideoFrame
import cv2, numpy as np, time

class CameraTrack(VideoStreamTrack):
    kind = "video"
    def __init__(self, device, width, height, fps):
        super().__init__()
        self.cap = cv2.VideoCapture(device)
        if width and height:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if fps:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.fps = fps or 30
        self._last = time.time()

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ok, frame = self.cap.read()
        if not ok:
            img = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            img = frame
        now_ms = int(time.time()*1000) % 100000
        cv2.putText(img, f"{now_ms} ms", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        video_frame = VideoFrame.from_ndarray(img, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        await asyncio.sleep(max(0, 1.0/self.fps - (time.time()-self._last)))
        self._last = time.time()
        return video_frame

INDEX_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Jetson WebRTC (aiortc)</title>
  <style> body{font-family:sans-serif;margin:24px} video{max-width:100%} </style>
</head>
<body>
  <h1>Jetson WebRTC (aiortc)</h1>
  <p>Druk op Start om de stream te starten.</p>
  <button id="start">Start</button>
  <div><video id="v" autoplay playsinline></video></div>
<script>
async function start() {
  const pc = new RTCPeerConnection();
  pc.ontrack = (ev) => { document.getElementById('v').srcObject = ev.streams[0]; };
  const offer = await pc.createOffer({offerToReceiveVideo: true});
  await pc.setLocalDescription(offer);
  const resp = await fetch('/offer', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({sdp: pc.localDescription.sdp, type: pc.localDescription.type})});
  const answer = await resp.json();
  await pc.setRemoteDescription(answer);
}
document.getElementById('start').onclick = start;
</script>
</body>
</html>"""

pcs = set()
camera_track = None

async def index(request):
    return web.Response(content_type="text/html", text=INDEX_HTML)

async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    pc = RTCPeerConnection()
    pcs.add(pc)

    pc.addTrack(camera_track)

    @pc.on("iceconnectionstatechange")
    def on_ice():
        if pc.iceConnectionState in ["failed", "closed", "disconnected"]:
            pcs.discard(pc)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return web.json_response({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})

async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default=0, help="OpenCV device index or /dev/videoX")
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--height", type=int, default=480)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()

    global camera_track
    camera_track = CameraTrack(args.device, args.width, args.height, args.fps)

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)
    web.run_app(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
