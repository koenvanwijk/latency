#!/usr/bin/env bash
# setup_net_probe_server.sh - Setup iperf3/mtr/jq/chrony for latency measurement server
set -euo pipefail
PORT="${PORT:-5201}"
need_root() { if [ "$(id -u)" -ne 0 ]; then echo "Run as root (sudo)"; exit 1; fi; }
pkg_detect() {
  if command -v apt-get >/dev/null 2>&1; then PKG=apt; return; fi
  if command -v dnf >/dev/null 2>&1; then PKG=dnf; return; fi
  if command -v yum >/dev/null 2>&1; then PKG=yum; return; fi
  echo "Unsupported distro"; exit 1
}
install_pkgs() {
  case "$PKG" in
    apt) apt-get update -y && apt-get install -y iperf3 mtr-tiny jq chrony && systemctl enable --now chrony || true;;
    dnf|yum) $PKG -y install epel-release || true; $PKG -y install iperf3 mtr jq chrony && systemctl enable --now chronyd || true;;
  esac
}
install_service() {
  cat > /etc/systemd/system/iperf3@.service <<EOF
[Unit]
Description=iperf3 server on port %%i
After=network-online.target
[Service]
Type=simple
ExecStart=/usr/bin/iperf3 -s -p %i
Restart=on-failure
[Install]
WantedBy=multi-user.target
EOF
  systemctl daemon-reload
  systemctl enable --now "iperf3@${PORT}.service"
}
open_fw() {
  if command -v ufw >/dev/null 2>&1; then ufw allow "${PORT}"/tcp && ufw allow "${PORT}"/udp
  elif command -v firewall-cmd >/dev/null 2>&1; then firewall-cmd --add-port=${PORT}/tcp --permanent; firewall-cmd --add-port=${PORT}/udp --permanent; firewall-cmd --reload
  elif command -v iptables >/dev/null 2>&1; then iptables -I INPUT -p tcp --dport ${PORT} -j ACCEPT; iptables -I INPUT -p udp --dport ${PORT} -j ACCEPT; fi
}
status() {
  PUBIP=$(curl -fsSL https://ifconfig.me || echo "<IP>")
  echo "Server reachable at: ${PUBIP}:${PORT}"
}
need_root; pkg_detect; install_pkgs; install_service; open_fw; status
