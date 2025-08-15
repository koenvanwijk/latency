# Teleop Latency Diagram

> **CI status:** ![CI](https://github.com/koenvanwijk/latency/actions/workflows/ci.yml/badge.svg)

Swimlane-diagram generator voor een SO100↔SO100 teleoperatieketen (Python USB-serial, WebRTC op Jetson).
Leest **Inputs** uit een Excel-model en bouwt een **Command→Photon** flow met totaaltijden.

## Snel starten

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Zorg dat het Graphviz 'dot' programma is geïnstalleerd (Linux: apt-get install graphviz, macOS: brew install graphviz, Windows: choco install graphviz)
python src/make_swimlane_from_excel.py examples/Teleop_Latency_Model_SO100_WebRTC_v3.xlsx out.png Typical
```

- `Best|Typical|Worst|Selected` mogelijk als derde argument (default **Typical**).
- Gebruik **Selected** als je Excel de gekozen scenario-kolom laat uitrekenen in de ‘Selected’ kolom (vereist recalculatie in Excel).

## Projectstructuur

```
.
├── src/
│   └── make_swimlane_from_excel.py
├── examples/
│   └── Teleop_Latency_Model_SO100_WebRTC_v3.xlsx
├── .github/workflows/
│   └── ci.yml
├── requirements.txt
├── Makefile
├── LICENSE
├── .gitignore
└── README.md
```

## CI (GitHub Actions)

- Installeert Python + Graphviz
- Voert het script uit op het voorbeeld-Excel
- Publiceert het **PNG-diagram als build-artifact**

## Licentie

MIT

## Website (GitHub Pages)

![Pages](https://github.com/koenvanwijk/latency/actions/workflows/pages.yml/badge.svg)

De interactieve site (D3) wordt automatisch gebouwd uit het Excel-bestand en via GitHub Pages gedeployed.

**Na push:**
1. Ga naar *Settings → Pages* en kies *GitHub Actions* als bron (of laat de workflow dit afhandelen).
2. De site staat op: `https://OWNER.github.io/REPO/` (vervang koenvanwijk/latency).

