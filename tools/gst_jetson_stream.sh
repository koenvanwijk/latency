#!/usr/bin/env bash
# gst_jetson_stream.sh — Low-latency H.264 stream op Jetson (NVENC) met meetbare timestamps.
# Vereist: GStreamer + NV plugins (nvv4l2h264enc), en een camera (CSI of USB).
# Voorbeeld gebruik:
#   ./gst_jetson_stream.sh /dev/video0 1280x720 30 out.sdp
#   (client kan met VLC/ffplay rtsp/sdp bekijken; voor WebRTC, gebruik een aparte pipeline)
set -euo pipefail
DEV="${1:-/dev/video0}"
RES="${2:-1280x720}"
FPS="${3:-30}"
SDP_OUT="${4:-out.sdp}"

echo "Device=$DEV Res=$RES FPS=$FPS"
# Kies bron (v4l2src) en caps
WIDTH="${RES%x*}"; HEIGHT="${RES#*x}"
# Pipeline: capture -> conv -> timeoverlay -> NVENC -> RTP pay -> SDP
gst-launch-1.0 -e \
  v4l2src device="$DEV" io-mode=2 ! video/x-raw,format=NV12,width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1 ! \
  queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 leaky=downstream ! \
  timeoverlay font-desc="Sans 24" shaded-background=true halignment=right valignment=bottom ! \
  videoconvert ! \
  nvv4l2h264enc iframeinterval=$((FPS*2)) insert-sps-pps=true control-rate=1 bitrate=4000000 preset-level=1 maxperf-enable=true zerolatency=true ! \
  h264parse config-interval=1 ! rtph264pay pt=96 config-interval=1 ! \
  gdppay ! filesink location="${SDP_OUT}"

# Opmerking:
# - Voor echte end-to-end latencytests met WebRTC, gebruik een WebRTC pipeline + signaling.
# - Deze pipeline schrijft een SDP-compatibele H264 stream; je kunt ook naar udpsink sturen.
