## 🌍 Netwerkmetingen met BG-server

Om de latency tussen jouw locatie en een server in Bulgarije nauwkeurig te meten, bevat deze toolkit nu twee scripts:

### 1. BG-server klaarmaken
Op de server in Bulgarije (Ubuntu/Debian of CentOS/RHEL/Alma/Rocky):

```bash
curl -fsSLO https://raw.githubusercontent.com/koenvanwijk/latency/main/tools/setup_net_probe_server.sh
sudo bash setup_net_probe_server.sh