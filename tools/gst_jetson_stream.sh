# tools/gst_jetson_stream.sh
#!/usr/bin/env bash
set -euo pipefail
SRC="${1:-usb}"            # usb|csi
RES="${2:-1280x720}"
FPS="${3:-30}"
SINK="${4:-autovideosink}" # of fakesink/udpsink/etc
DEV="${5:-/dev/video0}"    # voor usb

WIDTH="${RES%x*}"; HEIGHT="${RES#*x}"
have(){ gst-inspect-1.0 "$1" >/dev/null 2>&1; }

# Kies encoder
if   have nvv4l2h264enc; then ENC="nvv4l2h264enc preset-level=1 maxperf-enable=true zerolatency=true bitrate=4000000 iframeinterval=$FPS insert-sps-pps=true"
elif have x264enc;        then ENC="x264enc tune=zerolatency speed-preset=veryfast key-int-max=$FPS bitrate=4000"
else echo "Geen H.264 encoder (nvv4l2h264enc/x264enc) gevonden"; exit 1; fi

# Kies bron + converter
if [ "$SRC" = "csi" ]; then
  if have nvarguscamerasrc && have nvvidconv; then
    SRC_PIPE="nvarguscamerasrc ! video/x-raw(memory:NVMM),width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1 ! nvvidconv ! video/x-raw,format=NV12"
  else
    echo "CSI gekozen maar nvarguscamerasrc/nvvidconv niet compleet"; exit 1
  fi
else
  SRC_PIPE="v4l2src device=${DEV} io-mode=2 ! video/x-raw,format=NV12,width=${WIDTH},height=${HEIGHT},framerate=${FPS}/1"
fi

echo "SRC=$SRC RES=${WIDTH}x${HEIGHT} FPS=$FPS ENC=[$ENC] SINK=$SINK"
gst-launch-1.0 -e \
  ${SRC_PIPE} ! \
  timeoverlay font-desc="Sans 24" shaded-background=true halignment=right valignment=bottom ! \
  ${ENC} ! h264parse ! \
  ${SINK}
