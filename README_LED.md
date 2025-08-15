# 🔦 LED Latency Tester (ESP32‑C3 / Arduino)

Gebruik deze sketch om een LED te sturen voor end‑to‑end video‑latency metingen.

## Flashen
1. Open `tools/led_latency_tester.ino` in de **Arduino IDE** (of PlatformIO).
2. Board: **ESP32C3 Dev Module** (of passend board).
3. Poort: kies je USB‑poort (bv. `/dev/ttyACM0` / `COM5`).
4. Upload.

> **Pin:** standaard `LED_PIN = 8` en **active‑low** (0 = aan, 1 = uit). Pas aan indien nodig.

## Bediening (via USB‑serial, 115200 bps)
Stuur 1 karakter‑commando’s:

- `0` → LED **aan** (active‑low)
- `1` → LED **uit** (active‑low)
- `B` → **knipperen** (500 ms aan/uit)
- `S` → knipperen **stoppen**

Voorbeelden (Linux/macOS):
```bash
# LED aan
echo -n "1" > /dev/ttyACM0
# LED uit
echo -n "0" > /dev/ttyACM0
# Start knipperen
echo -n "B" > /dev/ttyACM0
# Stop knipperen
echo -n "S" > /dev/ttyACM0
```

Windows (PowerShell):
```powershell
# Installeer 'SerialPort' module of gebruik Arduino Serial Monitor voor snelle tests.
# Of gebruik Python:
#   py - <<'PY'
#   import serial; ser=serial.Serial('COM5',115200); ser.write(b'1')
#   PY
```

## Meten met high‑speed video
1. Zet de LED en je **scherm** samen in beeld.
2. Laat de LED aan/uit gaan (handmatig via serial of knipperstand).
3. Neem op met **240 fps** (smartphone kan vaak 240fps slo‑mo).
4. Analyseer met:
```bash
python tools/video_led_tester.py --video clip.mp4   --led-roi X,Y,W,H --scr-roi X2,Y2,W2,H2 --threshold 200 --fps 240
```

De tool rapporteert `latency_ms` = (frame_index_scherm − frame_index_led) × (1000 / fps).
