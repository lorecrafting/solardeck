# SolarDeck (Codename: XuanDeck / KoaDeck)

> **The Sovereign, Sunlight-Readable 10.3" Color E-Ink Field Workstation & Tactical LifeOps Terminal.**
> 
> *Open-Hardware Linux • AI Coding Terminal • Wacom Stylus Slate • Flipper Zero Multi-Tool • Meshtastic Mesh Node • Perpetual Ambient Solar Clock • IP67 Rugged Clamshell.*

---

## 1. Executive Summary

**SolarDeck** is a sovereign, distraction-free, sunlight-readable personal computing terminal engineered for writing, AI-assisted software development (Claude Code), medical practice, and emergency off-grid communication. 

Unlike commercial e-readers (Kindle, Boox, reMarkable) that are locked behind closed proprietary Android runtimes, SolarDeck runs **pure, bare-metal Linux** on an open-hardware carrier board, granting total low-level control over display waveforms, kernel drivers, and power management.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DISPLAY:     10.3" Color E-Ink (Kaleido 3 / Carta 1200) + Wacom EMR      │
│ 2. INPUT:       Detachable Magnetic Pogo-Pin Keyboard + Blackberry Trackpad │
│ 3. BRAIN:       Raspberry Pi CM4 (Linux) + RP2040 (Ultra-Low-Power Co-Proc) │
│ 4. AI VOICE:    Dual I2S Digital MEMS Mic Array + Hardware Mute Switch      │
│ 5. NETWORKS:    Worldwide 4G/LTE (Nano-SIM) + 915MHz LoRa (Meshtastic)      │
│ 6. MULTI-TOOL:  Flipper Zero Suite (Sub-GHz, IR Blaster, NFC, 125kHz RFID)  │
│ 7. POWER:       LiFePO4 Chemistry (3,000+ Cycles, 65°C Safe) + Micro-Solar  │
│ 8. DUAL BEZEL:  Solar Ambient Harvester + Capacitive Touch Shortcut Bar     │
│ 9. ENCLOSURE:   IP67 Waterproof CNC Anodized Aluminum + GORE Pressure Vent  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The 3 Core Personas of SolarDeck

### A. The "Workhorse" (Mobile AI Coding & Writing Station)
* Dock the magnetic keyboard, enable 4G/LTE, and launch **Claude Code** in the terminal.
* High-speed **20ms 1-bit monochrome typing mode** on e-paper eliminates typing lag.
* Talk directly to Claude through the digital microphone array with local speech-to-text (`whisper.cpp`) or streaming cloud API.
* Full-day battery life (7–9 hours of continuous AI coding and cellular connection).

### B. The "Zen Reader & Scribe" (Field Medical Tablet)
* Detach the keyboard. The device becomes a lightweight 10.3" slate.
* **1:1 scale rendering** of medical textbooks, pathology slides, and acupuncture charts.
* Battery-free **Wacom EMR stylus** with 4,096 levels of pressure and hardware palm rejection. Annotate margins and draw clinical patient intake diagrams directly into Obsidian.
* **100GB Offline Kiwix Library:** Complete Wikipedia, classical Chinese medical canon (*Neijing*, *Shanghan Lun*), and Western medical databases fully searchable off-grid.

### C. The "Perpetual Desk Clock & LifeOps Dashboard"
* Set the tablet on a desk kickstand or mount it to a wall dock.
* The main Linux processor enters deep sleep (0.005W).
* The **RP2040 co-processor** ticks a live 1-second clock using a tiny bounding-box partial E-ink refresh, pulling weather and HECO solar data over Wi-Fi every 15 minutes.
* **Total power draw: 8.5 milliwatts.**
* The **front-facing micro-solar bezel** harvests 10–50mW from ambient room light, making it a **perpetual-motion desk dashboard that never needs to be plugged into a wall**.

---

## 3. Specifications Quick-Reference

| Subsystem | Specification |
| :--- | :--- |
| **Main Compute** | Raspberry Pi Compute Module 4 (CM4) — Quad-core Cortex-A72 @ 1.8GHz, 4GB/8GB LPDDR4, 32GB eMMC |
| **Co-Processor** | Raspberry Pi RP2040 (Dual-core Cortex-M0+ @ 12MHz power-save) + DS3231 High-Precision RTC |
| **Display Panel** | 10.3" E-Ink Kaleido 3 (Color 150 PPI / B&W 300 PPI, 1872×1404) or Carta 1200 |
| **Digitizer** | Laminated Wacom EMR (battery-free stylus) + Capacitive Multi-touch |
| **Detachable Dock** | 5-Pin Hermetic Magnetic Gold Pogo-Pin Bus (USB 2.0 D+/D-, 5V, GND, Sense) + N52 Magnets |
| **Cellular Internet**| M.2 Key-B 3042 Socket + Push-Push Nano-SIM Tray (Quectel EC25-AFX Cat-4 LTE, AT&T/T-Mobile/Verizon) |
| **Mesh Radio** | Semtech SX1262 LoRa 915 MHz (Meshtastic firmware support) |
| **RF / Hardware Hacking**| TI CC1101 (300–928MHz Sub-GHz) + Vishay IR Blaster/Receiver + NXP PN532 NFC + EM4095 125kHz RFID |
| **Battery Chemistry**| 6,000 to 8,000 mAh **LiFePO4** (Lithium Iron Phosphate) — safe to 65°C / 149°F, 3,000+ cycles |
| **Solar Harvesting** | Front Bezel Monocrystalline Strip + TI BQ25895 MPPT Solar Charge Controller |
| **Ruggedization** | IP67 Waterproof & Dustproof, CNC 6061-T6 Aluminum, TPU armor corners, GORE ePTFE pressure vent |
| **Fast Wake-Up** | Suspend-to-RAM (S2idle): **0.3-second instant resume** |

---

## 4. Repository Structure

```
/Users/raymondluong/dev/solardeck/
├── README.md                  <- Master architectural overview
└── docs/
    ├── HARDWARE_SPEC.md       <- Complete schematic, pinout, and component documentation
    ├── SOFTWARE_SPEC.md       <- Linux kernel, E-ink waveform drivers, power profiles & apps
    └── BOM_COST_ESTIMATE.md   <- Bill of Materials, supplier links, and manufacturing breakdown
```
