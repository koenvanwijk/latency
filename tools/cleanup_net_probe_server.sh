#!/usr/bin/env bash
# cleanup_net_probe_server.sh - Remove iperf3 server and related packages/firewall rules
set -euo pipefail
PORT="${PORT:-5201}"
REMOVE_PKGS="${REMOVE_PKGS:-false}"
need_root() { if [ "$(id -u)" -ne 0 ]; then echo "Run as root (sudo)"; exit 1; fi; }
pkg_detect() {
  if command -v apt-get >/dev/null 2>&1; then PKG=apt; return; fi
  if command -v dnf >/dev/null 2>&1; then PKG=dnf; return; fi
  if command -v yum >/dev/null 2>&1; then PKG=yum; return; fi
  PKG=unknown
}
remove_service() {
  systemctl disable --now "iperf3@${PORT}.service" || true
  rm -f /etc/systemd/system/iperf3@.service
  systemctl daemon-reload || true
}
close_fw() {
  if command -v ufw >/dev/null 2>&1; then ufw delete allow "${PORT}"/tcp || true; ufw delete allow "${PORT}"/udp || true
  elif command -v firewall-cmd >/dev/null 2>&1; then firewall-cmd --remove-port=${PORT}/tcp --permanent; firewall-cmd --remove-port=${PORT}/udp --permanent; firewall-cmd --reload
  elif command -v iptables >/dev/null 2>&1; then iptables -D INPUT -p tcp --dport ${PORT} -j ACCEPT || true; iptables -D INPUT -p udp --dport ${PORT} -j ACCEPT || true; fi
}
remove_pkgs() {
  [ "$REMOVE_PKGS" != "true" ] && return
  case "$PKG" in
    apt) apt-get remove -y iperf3 mtr-tiny jq chrony || true;;
    dnf|yum) $PKG -y remove iperf3 mtr jq chrony || true;;
  esac
}
need_root; pkg_detect; remove_service; close_fw; remove_pkgs
