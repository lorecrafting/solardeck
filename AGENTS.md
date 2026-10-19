# AGENTS.md — SolarDeck Engineering Guide

Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Project Overview

**SolarDeck** (Codename: *XuanDeck* / *KoaDeck*) is an open-hardware, sunlight-readable 10.3" Color E-Ink mobile workstation and tactical terminal running mainline bare-metal Linux.

### Key Architecture Tenets
* **Compute Split ("Dual-Brain"):**
  * **Main Processor:** Raspberry Pi Compute Module 4 (CM4: Quad Cortex-A72 @ 1.8GHz, 4GB/8GB RAM, 32GB eMMC) running Linux 6.6 LTS, Sway/Wayland, Claude Code CLI, offline Kiwix, and Neovim.
  * **Ultra-Low-Power Co-Processor:** Raspberry Pi RP2350B (Dual Cortex-M33 / Hazard3 RISC-V @ 150MHz, 10 µA sleep / 4.5 mW Zen reader mode) running bare-metal C for perpetual RTC clock ticks, ambient solar voltage sampling (ADC shadow gestures), 8MB QSPI PSRAM framebuffer caching, and 0.3s S2idle instant-wake triggering via GPIO interrupt.
* **Display & Waveform:** 10.3" E-Ink Kaleido 3 / Carta 1200 (1872×1404, 227 PPI) via IT8951 EPDC isolated by TI TMUX1575 8-channel SPDT bus switch, with customized 1-bit 20ms fast-typing waveforms and an asynchronous anti-ghosting daemon (`eink-refreshd`). Laminated Wacom EMR digitizer with battery-free stylus for sub-20ms pen latency.
* **Power & Energy Harvesting:** 8,000–10,000 mAh LiFePO4 chemistry (26–32 Wh, 3.2V nominal, -10°C to +65°C safe, 3,000+ cycle life) managed by TI BQ25895 buck charger with dedicated USB-PD sink controller (STUSB4500 / CH224K for 20W PD), front-facing monocrystalline micro-solar bezel strip (IXYS SM141K06L, 0.15W peak trickle top-up), dedicated Always-On 3.3V low-IQ buck-boost (TI TPS62840, 60 nA IQ), and TPS22918 peripheral power load switches.
* **Comms & Hardware Multi-Tool:** M.2 Key-B 4G/LTE (Quectel EG25-G Global), 915 MHz LoRa (SX1262 / Meshtastic dedicated to RP2350), and rear 8-pin hermetic magnetic pogo bus mating to Modular RF Backpack with onboard bridge MCU and USB hub driving RTL2832U SDR, TI CC1101 Sub-GHz, Vishay IR TX/RX, NXP PN532 NFC, and EM4095 125kHz RFID.
* **Mounting & Open Keyboard Architecture:** Descoping the custom keyboard from the V1 release allows developers to connect any standard Bluetooth or USB-C keyboard (ThinkPad, Corne, Keychron, Apple, or $20 handheld BlackBerry Q20 thumb keyboards). The rear chassis integrates **Universal M2.5 Threaded Brass Inserts & a MagSafe-Compatible Magnetic Anchor Array** for snapping on 3D-printed handheld thumb grips, camera tripods, and desk easel arms. IP67 CNC 6061 aluminum or PA12 SLS enclosure with GORE ePTFE pressure vent and 85A TPU bumpers.

---

## 2. Repository Layout

```
.
├── README.md                  # Executive overview, core personas, specs table
├── AGENTS.md                  # Developer & AI agent instructions (this document)
├── docs/
│   ├── MVP_ARCHITECTURE.md    # Dual-brain architecture, power state transitions, block diagrams
│   ├── HARDWARE_SPEC.md       # Carrier board schematic, bus topology, pinouts, RF & power
│   ├── SOFTWARE_SPEC.md       # Linux kernel, DRM waveform drivers, power profiles, daemons
│   └── BOM_COST_ESTIMATE.md   # Bill of materials, supplier sourcing, turnkey cost breakdown
└── (Planned tree additions)
    ├── hardware/              # KiCad schematics, PCB layout, Gerber/BOM exports, STEP 3D models
    ├── firmware/
    │   ├── rp2350/            # Bare-metal C/Pico-SDK co-processor firmware (RTC, ADC, S2idle wake)
    │   └── keyboard/          # ZMK / QMK keyboard firmware for nRF52840
    └── src/
        ├── drivers/           # Custom IT8951 LUTs, DRM/KMS patches
        └── daemons/           # eink-refreshd, solar gesture listener, solardeck-telemetryd
```

---

## 3. Agent Operating Rules & Discipline

### 3.1 Global Coding & Search Guidelines
* **Structural Search:** Always prefer `ast-grep` (`sg`) with `--json` for structural syntax queries in supported languages; do not use raw text search (`rg` / `grep`) unless plain-text search is strictly requested.
* **Ponytail Philosophy:** Apply the Ponytail discipline to all changes. Enforce the ladder:
  1. YAGNI: Skip speculative features.
  2. Reuse existing helpers and patterns.
  3. Prefer standard library and native Linux kernel/system interfaces.
  4. Minimal dependencies, minimal working diffs.
  5. Provide a single, runnable verification check (`assert`-based self-test or targeted test) for any non-trivial logic.
* **Self-Review:** Before completing code tasks, run a self-review pass on the actual `git diff` for correctness, edge cases, and safety.

### 3.2 Attribution & Stamping Standards
When operating under the Pi harness:
* **Git Commits:** Append commit trailers using `git commit --trailer`:
  ```
  Co-Authored-By: <model display name> <noreply@anthropic.com>
  Harness: pi (<provider>/<model>, session <id>)
  ```
* **Documents & Technical Records:** Add the mandatory attribution line in the header or section start:
  `Written <YYYY-MM-DD HH:MM> UTC in the Pi harness by <provider>/<model>`
* **Issue / PR Comments:** Prefix with `[Pi · <provider>/<model> · session <id>]`.

---

## 4. Engineering & Safety Constraints

1. **Battery Management & Thermal Safety:** LiFePO4 operates at 3.2V nominal (3.65V charge limit). Never configure charging parameters for standard 3.7V Li-ion/LiPo (4.2V), which creates severe over-voltage hazards. Always verify NTC thermistor cutoffs.
2. **Peripheral Power Gating:** The TPS22918 load switches must be kept in hard cut-off state during sleep to maintain the 15 mW S2idle power envelope.
3. **EPDC & E-Ink Waveform Caution:** Improper voltage LUT cycling on electrophoretic displays can cause permanent DC pigment burn-in. Waveform alterations must ensure net DC bias across refresh cycles averages to 0V.
4. **RF Multi-Tool Emission Safety:** Sub-GHz (CC1101) and LoRa (SX1262) transmissions must respect regional ISM band limits and maximum EIRP rules (e.g. 915 MHz North America, 868 MHz Europe).
