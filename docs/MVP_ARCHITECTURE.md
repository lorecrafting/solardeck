# SolarDeck MVP & Modular System Architecture

Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash
Revised 2026-10-21 15:59 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).
Revised 2026-10-21 17:53 UTC in Claude Code by anthropic/claude-opus-5-5 (RTC chip, jack removed, ADR-046).

---

## 1. Executive Strategy: Core Tablet MVP vs. Modular Expansion

SolarDeck is a sovereign, general-purpose open-hardware computing platform designed for AI-assisted development, field reading/writing, and off-grid communication. The architecture cleanly separates the core platform from specialized add-on modules:

1. **The Core MVP Tablet (Standalone Survival Terminal & Daily Driver):**
   * Bare-metal Linux coding & computing platform (Raspberry Pi CM5)
   * Sunlight-readable 10.3" e-paper reader and Wacom EMR digitizer slate
   * Connectivity: Wi-Fi/BT on the CM5 plus phone tethering. Cellular (LTE modem, nano-SIM tray, soldered eSIM, LTE antennas, modem supply): deferred to V2 (ADR-034); the V2 eSIM requirement is a consumer SGP.22 eUICC (ADR-033)
   * Mesh: the CM5 talks to a paired external Meshtastic node over Bluetooth LE (software only). On-board LoRa: deferred to V2 (ADR-044); the V1 board reserves the footprint and pins (ADR-045, docs/PIN_BUDGET.md)
   * NFC: deferred to V2 (ADR-034)
   * Standalone GNSS: **u-blox MAX-M10S** on an RP2350 UART behind a load switch, passive antenna at the top edge; tracking power `spec_values.gnss.tracking_mw` (ADR-038)
   * Dual-brain ultra-low-power supervisor (RP2350B + 8MB PSRAM) with **2× TI TMUX1575 (4-channel each, 8 total) display bus isolation** for 4.5 mW 30ms Zen reading and desk clock modes
   * Rear camera: deferred to V2 (ADR-034)
   * **Core Internal Tactical Sensor Cluster:** RV-3028-C7-class RTC (ADR-046), Bosch BMI270 + BMM350 9-DOF IMU (compass & Stellarium), Bosch BMP390 Barometer (10cm altimeter & weather storm barograph), VEML7700 / Solar ADC ambient light sensor
   * **Voice (ADR-036):** two MEMS mics, speaker with echo-cancel reference, hardware mute, and a hold-to-talk voice button (RP2350 captures into PSRAM at press while the CM5 boots)
   * **Haptics (ADR-037):** DRV2605L + frame-mounted LRA; every keystroke fires a tap and optional typewriter sound at key-down
   * LiFePO4 battery, capacity TBD until the cell is chosen (ADR-040) (airline-compliant <100Wh)
   * Lightweight, rugged SLS 3D-printed PA12 Nylon prototypes, PC/ABS production (ADR-039); ingress IP54 (V1 target), IP67 (V2 target)
2. **Modular Expansion ("Hotpacks"):** Deferred to V2 (ADR-034).
   * **Descoped Flipper Zero Clone:** Redundant over-engineering. Operators simply attach their physical **Flipper Zero** to the rear M2.5/MagSafe anchor, plug into USB-C Port 2 or pair via Bluetooth, and control it through `qflipper-cli` and `flipperzero-protobuf` on SolarDeck's 10.3" E-Ink screen.
3. **Descoping Note (Integrated Solar Smart Cover):**
   * *The Hawaii / Tropical Sun Reality:* In direct tropical sun (+30°C to +40°C ambient), dark tablet surfaces hit +70°C. E-Ink microcapsules degrade above +60°C, and LiFePO4 charging must throttle above +45°C.
   * *Decision:* The integrated solar smart cover is descoped. Operators use standard off-the-shelf folding USB-C solar panels (15W–28W) positioned on hot rocks in direct sunlight, connected via a 3-meter high-visibility USB-C cable to SolarDeck resting safely in the ambient shade.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK MVP (THE CORE TABLET)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. BRAIN:     Raspberry Pi CM5 CM5116064 (16GB RAM, 64GB eMMC, Wi-Fi/BT)    │
│ 2. CO-PROC:   RP2350B (Cortex-M33/RISC-V) + 8MB PSRAM (Zen Reader)          │
│ 3. DISPLAY BUS: K4 display controller (TBD, ADR-032) + 2x TMUX1575          │
│ 4. SCREEN:    10.3" E Ink Kaleido 4 (resolution/PPI TBD, ADR-032) + EMR     │
│ 5. CAMERA:    Deferred to V2 (ADR-034)                                      │
│ 6. CELLULAR:  Deferred to V2 (ADR-034); V2 eSIM = SGP.22 eUICC (ADR-033)    │
│ 7. MESH/GNSS: BLE Meshtastic node (LoRa V2, ADR-044) + MAX-M10S (ADR-038)   │
│ 8. NFC:       Deferred to V2 (ADR-034)                                      │
│ 9. ANTENNAS:  passive GNSS (top edge); LoRa SMA boss plugged (V2, ADR-045)  │
│ 10. SENSORS:  RV-3028-C7 RTC + BMI270/BMM350 9-DOF IMU + BMP390 Baro        │
│ 11. AIRGAP SW: Physical Hardware RF Kill Switch (Zero EMF / 0.000 dBm Cutoff)│
│ 12. VOICE:    2 MEMS Mics + Speaker (AEC ref) + Mute SW + Voice Button      │
│ 13. BATTERY:  LiFePO4 1S, capacity TBD until the cell is chosen (ADR-040)   │
│ 14. EXPAND:   2x IP68 USB-C (Monitor Sink + Host Expand with USB-to-I2C)     │
│ 15. CHASSIS:  SLS 3D-Printed PA12 Nylon + 85A TPU Armor Corners (~510g total)│
│ 16. HAPTICS:  DRV2605L + frame-mounted LRA (ADR-037)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Battery Sizing & Weight Optimization

To achieve maximum field battery life without an excessively heavy device:

### Capacity: TBD until the cell is chosen (ADR-040)
* **Configuration:** 1S LiFePO4 only (3.2V nominal, charge limit `battery.charge_limit_v`); there is no Li-ion option (ADR-035). Protection is a BQ29706-class protector with a back-to-back N-FET pair; the gauge is a BQ27Z561-R2 characterised on the chosen cell.
* **Dimensions:** ~5.5 mm thick × 130 mm × 130 mm (occupies the flat recessed cavity coplanar with the PCBA directly behind the 10.3" e-paper display).
* **Weight:** **~200 grams** (~7.0 oz).
* **Total Tablet Device Weight:** **~510 grams** (1.12 lbs). For comparison:
  * iPad Pro 11" with case: ~680 grams
  * Onyx Boox Note Air 3C: ~430 grams (with small 3,700 mAh battery)
  * Panasonic Toughbook tablet: ~1,100 grams
* **FAA / TSA Airline Compliance:** The international limit for passenger aircraft is **100 Watt-hours (Wh)**. A 1S pack that fits this cavity sits far below it.
* **Extreme Heat Safety:** Rated safe up to 65°C (149°F). The tablet can sit in direct sunlight or on a vehicle dashboard safely.

### Runtime per power tier: TBD until the cell is chosen (ADR-040)
The tier draws below are the modelled loads; runtimes are re-derived from the chosen cell.
* **Tier 0: Dormant Standby (< 0.1 mW)**
* **Tier 1: Zen Reader Mode (RP2350 Driven @ ~4.5 mW)** with 30ms page turns.
* **Tier 2: LoRa mesh repeater:** deferred to V2 (ADR-044).
* **Tier 3: Paper-Feel Scribe Slate (CM5 1-Core @ ~0.60W)**
* **Tier 4: Adaptive Mixed Workstation (Web/Discord/Claude @ ~1.40W avg)**
* **Tier 5: Audio-First Conferencing (Mic array + Opus + inbound dither @ ~1.30W)** (no outbound video; USB-C UVC webcam optional via Port 2).
* **Tier 5b: High-Motion Screen Work (GPU dithering + repeated partial refresh @ ~1.6W–2.2W)** (images, maps, rapid pagination; not video — see ADR-005).
* **Tier 6: AI Compile Turbo (CM5 Quad @ ~3.2W)** continuous parallel compiling.

### Battery Longevity: High-Motion vs. Static & 10–15 Year Cell Lifespan
* **During High-Motion Screen Work (images, maps, rapid pagination):** GPU blue-noise dithering, NEON differencing, and repeated full-frame transfers draw **1.6W to 2.2W** (runtime TBD, ADR-040). There is no video-playback tier: the panel link and its frame rate depend on the Kaleido 4 display controller (TBD, ADR-032), so V1 does not promise cinema (ADR-005).
* **When Idle or Static** (Writing, Coding, Reading, Ambient Clock):**
  * **0.000W Bi-Stable Physics:** Unlike OLED or LCD screens that draw 1.5W–3.0W just keeping pixels backlit, E-Ink uses **0.000 Watts** to display a static page. Once particles move into position, they remain physically locked in place indefinitely without electrical power.
  * **Interactive Terminal & Coding:** In Neovim and Claude Code CLI, the screen only consumes power during partial update pulses (timing TBD, ADR-032) when keys are pressed. Total system draw drops to **~1.1W–1.4W** (runtime TBD until the cell is chosen, ADR-040).
  * **Zen Reading Mode:** With the CM5 unpowered and the RP2350 flipping pages in 30ms, battery runtime is TBD until the cell is chosen (ADR-040).
  * **Ambient Desk Clock & Weather Station:** The top-bezel micro-solar strip tops up the idle co-processor outdoors only (ADR-041).
  * **Chemical Cycle Life (10–15 Years):** Standard consumer Li-ion batteries degrade after 500 charge cycles (~2 years). In contrast, SolarDeck's LiFePO4 chemistry provides **3,000 to 5,000+ full cycles**. Because non-video workflows require charging only once every few days or weeks, the physical battery pack lasts **10 to 15+ years** before reaching 80% health.

---

## 3. Connectivity & RF Antenna Engineering

V1 connectivity is Wi-Fi/BT on the CM5 plus phone tethering (ADR-034).

### 3.1 Cellular Modem, SIM/eSIM, NFC & Headphone Jack
* **Cellular modem, nano-SIM tray and soldered eSIM:** Deferred to V2 (ADR-034); the V2 requirement is a consumer SGP.22 eUICC (ADR-033).
* **NFC:** Deferred to V2 (ADR-034).
* **3.5 mm headphone jack:** Removed from V1 (ADR-046): use USB-C or Bluetooth audio; one less aperture for the IP54 target.

### 3.2 Antenna Architecture & Reception Optimization
1. **LoRa Mesh:** Deferred to V2 (ADR-044); the V1 board reserves the footprint and pins (ADR-045, docs/PIN_BUDGET.md). V1 mesh is a paired external Meshtastic node over Bluetooth LE.
2. **Cellular LTE antennas:** Deferred to V2 (ADR-034).
   * **GNSS (ADR-038):** passive GNSS antenna at the top edge feeding the u-blox MAX-M10S (integrated LNA), which sits on an RP2350 UART behind a load switch. Receive-only.
3. **Wi-Fi 5 & Bluetooth 5.0:**
   * Internal **Molex `1461530100`** balanced dual-band (2.4/5.8 GHz) dipole FPC connected to the CM5 antenna connector (TBD — verify on CM5). Balanced dipole tuning prevents hand-grip detuning.
4. **RF Windowing (Physics Constraint):**
   * In PA12 SLS Nylon, RF radiates freely through the chassis.
   * In CNC 6061 Aluminum, the top 25mm bezel is a modular PA12/Delrin "RF Window" cap to prevent Faraday cage attenuation.

---

## 4. Hardware Anti-Bricking & Recovery Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       7-TIER ANTI-BRICKING PROTECTION                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Broadcom ROM `rpiboot` Mode:                                             │
│    • Grounding `nRPIBOOT` forces CM5 into USB boot mode.                    │
│    • Internal 64GB eMMC mounts as a USB drive on a host laptop via USB-C.   │
│    • Triggered without opening case via external magnetic reed switch.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Microcontroller UART Console Bridge:                                     │
│    • CM5 UART0 (GPIO 14/15, TBD — verify on CM5) routes to RP2350 UART.     │
│    • RP2350 USB CDC serial on the recovery header (docs/PIN_BUDGET.md).     │
│    • Stream early kernel dmesg / panic logs even if screen is dead.         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. RP2350 ROM `BOOTSEL` Recovery:                                           │
│    • External button / pin pull drops RP2350 into `RPI-RP2` USB drive mode  │
│      for instant drag-and-drop `.uf2` firmware recovery.                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. A/B Dual-Root Partitioning:                                              │
│    • U-Boot with hardware watchdog rollback: failsafe boot to Partition A   │
│      if experimental Partition B panics within 30 seconds.                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. Hardware Power Override:                                                 │
│    • 10-second power button hold physically bypasses software load switches,│
│      forcing clean 5V/3.3V power rails to CM5.                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 6. Display Bus Multiplexer & Bias Guard (TMUX1575):                         │
│    • Physical isolation of CM5 lines in sleep; discharges VCOM/gate rails   │
│      if host crashes mid-refresh, preventing pigment burn-in.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 7. Autonomous Charger Safety (ADR-035):                                     │
│    • TI BQ25798 charging is held off by its enable pin until the RP2350     │
│      has written the LiFePO4 VREG (POR defaults are a Li-ion voltage).      │
│    • The charger watchdog is disabled before VREG is written (ADR-047).     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Audio & Acoustic Engineering

To enable clean voice interaction with Claude Code and dictation:

1. **Acoustic Output (Speaker):**
   * Single pre-engineered sealed acoustic micro-box speaker (PUI Audio `AS03008MR-5-R` or AAC `1524`). Pre-welded airtight 1.0cc resonant chamber provides clean vocal reproduction without chassis buzz.
   * **Amplifier:** Maxim Integrated / Analog Devices **MAX98357A** (I2S Class-D mono amplifier, 3.2W into 4Ω).
2. **Acoustic Input (ADR-036):**
   * Two I2S digital MEMS microphones (Knowles **SPH0645LM4H-B** or InvenSense `ICS-43434`), with the speaker output looped back as the echo-cancel reference for barge-in.
   * Mounted inside molded silicone acoustic boots to decouple chassis vibrations.
   * **Voice button:** hold-to-talk is always available and costs nothing in standby; the RP2350 starts capturing into PSRAM at press while the CM5 boots, so no words are lost. A hands-free wake word is opt-in, with its measured battery cost shown.
3. **Physical Privacy:** The single 3-position privacy switch (normal / mic mute / full blackout, HARDWARE_SPEC §2.25) stops the microphones in hardware: mute breaks their clock, blackout also cuts their supply.

---

## 6. Dual-Brain Direct Drive & Low-Power Sipping Pipeline

```
[STEP 1: BROWSE ON FULL LINUX (CM5)]
• User wakes CM5 (Linux resumes from off/hibernate in seconds, ADR-036).
• Full Linux manages Calibre, KOReader, or terminal workspace.
• User selects book or activates ambient dashboard.
                              │
                              ▼
[STEP 2: 0.5-SECOND HANDOFF & ISOLATION]
• Linux renders page buffers to shared storage.
• CM5 signals RP2350 via I2C: "Taking over display".
• CM5 toggles TMUX1575 SELECT line to RP2350 and cuts CM5 power (0.000 mW).
• TMUX1575 completely isolates all 6 CM5 lines, preventing leakage into unpowered SoC.
                              │
                              ▼
[STEP 3: AUTONOMOUS RP2350 SIPPING MODE]
• RP2350 pushes pages/digits to the Kaleido 4 display controller (TBD, ADR-032) from 8MB PSRAM double-buffer.
• Between updates, RP2350 deep-sleeps at 10 µA.
• Display controller sleep power TBD (ADR-032). Total system draw: ~4.5 mW.
• Battery runtime: TBD until the cell is chosen (ADR-040).
                              │
                              ▼
[STEP 4: RESUME FULL LINUX]
• Tap key, touch screen, or double-tap IMU.
• RP2350 asserts GPIO 17 wake line to CM5.
• TMUX1575 switches bus back to CM5. Linux resumes from off/hibernate in seconds (ADR-036).
```

---

## 7. Input Architecture: Universal Mechanical Mount & Open Keyboards (V1)

For V1, descoping the proprietary SnapDeck keyboard eliminates $25,000+ in custom injection tooling and 6 months of firmware bring-up. The core tablet features **Universal M2.5 Threaded Brass Inserts and a MagSafe-Compatible Magnetic Array** on the rear shell, allowing users to pair any Bluetooth or USB-C keyboard (ThinkPad TrackPoint, Keychron, Corne, Apple Magic Keyboard) or snap on an open-source 3D-printed $20 BlackBerry Q20 handheld thumb keyboard.

*(Note: The custom SnapDeck scissor keyboard specification below is preserved as an optional Phase 2 accessory design).*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE 4 OPERATING POSTURES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 1: HANDHELD THUMB-TYPING CYBERDECK                                  │
│ • Snaps into an open-source 3D-printed handheld ergonomic grip.             │
│ • Integrates an inexpensive $20 USB-C/BLE BlackBerry Q20 thumb keyboard     │
│   beneath the 10.3" screen for two-thumb terminal typing while walking.     │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 2: PROPPED-UP WORKSTATION (LANDSCAPE)                               │
│ • MagSafe / OEM stand props tablet upright at 65°–75° on desk.              │
│ • Keyboard sits detached on the desk in front of the screen.                │
│ • Sway expands display to full panel resolution (TBD, ADR-032).             │
│ • Use Case: Traditional laptop workstation at a coffee shop or desk.        │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 3: VERTICAL CODER WORKSTATION (PORTRAIT)                            │
│ • MagSafe / OEM stand props tablet upright in tall Portrait orientation.    │
│ • 80+ lines of code visible vertically (like a programmer's vertical screen).│
│ • Full-width keyboard sits detached on the desk.                            │
│ • Use Case: Reading long source files, logs, and technical documentation.   │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 4: PURE SLATE / SCRIBE MODE                                         │
│ • Detached from all stands, held in one hand as a pure 510g tablet.         │
│ • Use Case: Lightweight handheld e-reader, PDF annotation, Wacom sketching. │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Optional Phase 2 Accessory: SnapDeck Scissor Keyboard Specifications
1. **Key Switches:** Ultra-slim (3.5mm total thickness) Kailh X-Switch tactile scissor keys with 1.2mm travel.
2. **Trackpad:** Blackberry RIM 9900 optical trackpad centered directly below the spacebar for thumb cursor control without lifting hands.
3. **Controller & Firmware:** Nordic **nRF52840** running open-source **ZMK Firmware**, supporting wired USB and sub-millisecond BLE 5.0 wireless.
4. **Docking Bus:** 5-pin hermetic magnetic gold pogo pins (5V, GND, USB D+, USB D-, ID_SENSE). Automatically charges internal 300 mAh LiPo via onboard MCP73831T linear charger with PCM while docked.

---

## 8. Turnkey Manufacturing in Shenzhen & Delivery to Honolulu

A prototype can be 100% manufactured, clean-room assembled, QA tested, and boxed in Shenzhen, then shipped via DHL Express directly to Honolulu:

* **Turnkey Box-Build Vendors:** PCBWay, Seeed Studio Fusion, Makerfab.
* **Battery Shipping Advantage (UN3481):** Because the LiFePO4 battery is pre-installed inside the assembled enclosure, it qualifies under UN3481 (Lithium batteries contained in equipment, Section II). It ships via standard commercial air cargo without hazardous materials surcharges.
* **Lead Time:** ~3 weeks from file submission to delivery in Honolulu.
* **Prototype Costs Delivered to Honolulu:**
  * **Qty 1 (Single Turnkey Prototype):** **TBD — the V1 BOM is a floor until the panel, cell and power parts are priced (`docs/BOM_COST_ESTIMATE.md`)**
  * **Qty 5 (Small Batch Run):** **~$1,150 – $1,250 total** (~$230 – $250 per finished tablet)
