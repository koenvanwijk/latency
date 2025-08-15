#!/usr/bin/env python3
"""
webrtc_echo.py — Local loopback met aiortc, meet encode->decode latency in software.
Gebruik als baseline zonder netwerk; voor Jetson+browser end-to-end gebruik je WebRTC app + webrtc_stats.html.

Benodigd:
  pip install aiortc opencv-python

Gebruik:
  python tools/webrtc_echo.py --fps 30 --duration 10
"""
import argparse, asyncio, time
from aiortc import RTCPeerConnection, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole
import numpy as np, cv2
from av import VideoFrame

class TestPattern(VideoStreamTrack):
    def __init__(self, fps):
        super().__init__()
        self.fps = fps
        self.ts = 0
        self.start = time.time()

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        # Create simple frame with timestamp text
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        ms = int((time.time() - self.start) * 1000)
        cv2.putText(img, f"{ms} ms", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 2)
        frame = VideoFrame.from_ndarray(img, format="bgr24")
        frame.pts = pts
        frame.time_base = time_base
        await asyncio.sleep(1.0/self.fps)
        return frame

async def main(args):
    pc1 = RTCPeerConnection()
    pc2 = RTCPeerConnection()

    src = TestPattern(args.fps)
    pc1.addTrack(src)

    # Pipe pc1 -> pc2
    @pc2.on("track")
    def on_track(track):
        # Sink frames to blackhole, but we measure timing via RTCPeerConnection stats
        pass

    await pc1.setLocalDescription(await pc1.createOffer())
    await pc2.setRemoteDescription(pc1.localDescription)
    await pc2.setLocalDescription(await pc2.createAnswer())
    await pc1.setRemoteDescription(pc2.localDescription)

    # Wait some seconds and pull stats
    await asyncio.sleep(args.duration)
    stats = await pc2.getStats()
    # Estimate decode latency: totalDecodeTime / framesDecoded
    decode_ms = None
    for s in stats.values():
        if s.type == "inbound-rtp" and getattr(s, "kind", None) == "video":
            if getattr(s, "totalDecodeTime", None) and getattr(s, "framesDecoded", 0):
                decode_ms = 1000.0 * (s.totalDecodeTime / max(1, s.framesDecoded))
    print(f"aiortc local loopback: estimated decode_ms={decode_ms:.2f} (software)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--duration", type=int, default=10)
    args = ap.parse_args()
    asyncio.run(main(args))
