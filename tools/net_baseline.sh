#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-8.8.8.8}"
DUR="${2:-15}"
echo "=== MTR (100 pings) to $TARGET ==="
(mtr -rwzc 100 "$TARGET" || mtr -rwzc 100 -4 "$TARGET") || true
echo "=== iperf3 up/down (server required) ==="
echo "Run iperf3 -s on the other end, then:"
echo "  iperf3 -c <server> -t $DUR"
echo "  iperf3 -c <server> -t $DUR -R"
