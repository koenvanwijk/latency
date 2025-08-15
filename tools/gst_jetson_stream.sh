#!/usr/bin/env bash
set -euo pipefail
DEV="${1:-/dev/video0}"
RES="${2:-1280x720}"
FPS="${3:-30}"
SINK="${4:-autovideosink}"  # of fakesink/udpsink/...
WIDTH="${RES%x*}"; HEIGHT="${RES#*x}"

have(){ gst-inspect-1.0 "$1" >/dev/null 2>&1; }

# Encoder kiezen (NVENC zodra aanwezig, anders x264)
if have nvv4l2h264enc; then
  ENC="nvv4l2h264enc preset-level=1 maxperf-enable=true zerolatency=true bitrate=4000000 iframeinterval=$FPS insert-sps-pps=true"
elif have x264enc; then
  ENC="x264enc tune=zerolatency speed-preset=veryfast key-int-max=$FPS bitrate=4000"
else
  echo "Geen H.264 encoder (nvv4l2h264enc/x264enc) gevonden"; exit 1
fi

# Probeer eerst generieke raw pad; als dat faalt kun je MJPEG proberen met arg 'mjpeg'
MODE="${5:-auto}"   # auto|mjpeg|yuy2

if [ "$MODE" = "mjpeg" ]; then
  SRC="v4l2src device=$DEV io-mode=2 ! image/jpeg,framerate=${FPS}/1 ! jpegdec"
elif [ "$MODE" = "yuy2" ]; then
  SRC="v4l2src device=$DEV io-mode=2 ! video/x-raw,format=YUY2,framerate=${FPS}/1"
else
  SRC="v4l2src device=$DEV io-mode=2"
fi

echo "Device=$DEV Res=${WIDTH}x${HEIGHT} FPS=$FPS Encoder=[$ENC] Sink=$SINK Mode=$MODE"

gst-launch-1.0 -e \
  $SRC ! \
  videoconvert ! videoscale ! video/x-raw,width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1 ! \
  timeoverlay font-desc="Sans 24" shaded-background=true halignment=right valignment=bottom ! \
  $ENC ! h264parse config-interval=1 ! \
  $SINK
