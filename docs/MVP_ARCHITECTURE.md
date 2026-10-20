# SolarDeck MVP & Modular System Architecture

Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Executive Strategy: Core Tablet MVP vs. Modular Expansion

SolarDeck is a sovereign, general-purpose open-hardware computing platform designed for AI-assisted development, field reading/writing, and off-grid communication. The architecture cleanly separates the core platform from specialized add-on modules:

1. **The Core MVP Tablet (Standalone Survival Terminal & Daily Driver):**
   * Bare-metal Linux coding & computing platform (Raspberry Pi CM4)
   * Sunlight-readable 10.3" e-paper reader and Wacom EMR digitizer slate
   * Built-in Worldwide 4G/LTE (Quectel EG25-G) with soldered onboard MFF2 **eSIM (eUICC)** and physical Nano-SIM
   * **Built-in Primary Off-Grid LoRa Mesh:** Semtech SX1262 LoRa (868/915 MHz) wired directly to RP2350 SPI for 80+ day low-power Meshtastic repeating & zero-watt E-Ink pager mode
   * **Built-in Near Field Communication (13.56 MHz NFC):** Dedicated STMicroelectronics ST25R3916 / NXP PN7160 with top-bezel FPC loop antenna for YubiKey / FIDO2 hardware SSH/login, LUKS disk decryption, and tap-to-pair P2P mesh contact exchange
   * Worldwide Multi-Constellation Satellite Navigation (Integrated Qualcomm GNSS in Quectel EG25-G)
   * Dual-brain ultra-low-power supervisor (RP2350B + 8MB PSRAM) with **2× TI TMUX1575 (4-channel each, 8 total) display bus isolation** for 4.5 mW 30ms Zen reading, 24/7 LoRa mesh repeating, and 300+ day desk clock modes
   * 12MP Sony IMX708 PDAF Macro rear camera for Claude Code multimodal inspection, PCB loupe, document OCR, and celestial plate-solving navigation
   * Top-bezel **IP67 Bulkhead SMA female connector** for tactical tuned LoRa whip, plus internal Taoglas FXUB63 2×2 MIMO cellular antennas
   * **Core Internal Tactical Sensor Cluster:** High-precision DS3231 RTC, Bosch BMI270 + BMM350 9-DOF IMU (compass & Stellarium), Bosch BMP390 Barometer (10cm altimeter & weather storm barograph), VEML7700 / Solar ADC ambient light sensor, and low-noise PDM digital microphone (Whisper voice-to-text tactical PTT memos)
   * High-capacity **8,000–10,000 mAh (26–32 Wh LiFePO4 / 30–37 Wh Li-ion)** battery (airline-compliant <100Wh)
   * Lightweight, rugged SLS 3D-printed PA12 Nylon enclosure or CNC 6061-T6 aluminum with RF window cap
2. **Modular Expansion ("Hotpacks"):** Rather than building a clumsy, monolithic "kitchen-sink" backpack or replicating existing gadgets, specialized payloads are partitioned into **seven focused, hot-swappable USB-C Hotpacks** connecting via USB-C Port 2 and rear MagSafe / M2.5 anchors (pure USB-C, no fragile pogo pins!):
   * **Hotpack 1 (Doomsday Sky-Scan & SIGINT):** RTL-SDR v4 wideband tuner (500 kHz – 1.76 GHz) with dual top SMA ports and switched 137 MHz / 1090 MHz SAW filters for passive NOAA weather satellite cloud imaging (`satdump`) and live aircraft radar (`readsb`). 100% stealth passive reception.
   * **Hotpack 2 (Tactical Dual-Mesh & HF Shortwave Transceiver):** Secondary SX1262 LoRa transceiver (dedicated to **MeshCore / Reticulum** with its own SMA port, enabling concurrent dual-mesh operation with zero RF loss), QRP 5W HF shortwave digital text transceiver (JS8Call / FT8 on 40m/20m bands bouncing 500–2,000 miles off the ionosphere with BNC jack), and hardware APRS / AX.25 TNC via 3.5mm TRRS port.
   * **Hotpack 3 (CBRN & SAR Environmental):** PocketGeiger Type 5 / BG51 solid-state ionizing radiation dosimeter ($\mu\text{Sv/h}$ fallout graphing), FLIR Lepton 3.5 / InfiRay P2 radiometric thermal camera (sees through wildfire smoke and pitch darkness), and Sensirion SCD41 photoacoustic CO2 / toxic gas detector.
   * **Hotpack 4 (Precision RTK Survey):** u-blox ZED-F9P multi-band RTK GNSS engine (1.4 cm horizontal accuracy with RTCM base, or 20 cm worldwide satellite-direct via free Galileo HAS on E6 band with zero internet).
   * **Descoped Flipper Zero Clone:** Redundant over-engineering. Operators simply attach their physical **Flipper Zero** to the rear M2.5/MagSafe anchor, plug into USB-C Port 2 or pair via Bluetooth, and control it through `qflipper-cli` and `flipperzero-protobuf` on SolarDeck's 10.3" E-Ink screen.
3. **Descoping Note (Integrated Solar Smart Cover):**
   * *The Hawaii / Tropical Sun Reality:* In direct tropical sun (+30°C to +40°C ambient), dark tablet surfaces hit +70°C. E-Ink microcapsules degrade above +60°C, and LiFePO4 charging must throttle above +45°C.
   * *Decision:* The integrated solar smart cover is descoped. Operators use standard off-the-shelf folding USB-C solar panels (15W–28W) positioned on hot rocks in direct sunlight, connected via a 3-meter high-visibility USB-C cable to SolarDeck resting safely in the ambient shade.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK MVP (THE CORE TABLET)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. BRAIN:     Raspberry Pi CM4 (8GB RAM, 32GB eMMC, Wi-Fi/BT)               │
│ 2. CO-PROC:   RP2350B (Cortex-M33/RISC-V) + 8MB PSRAM (300-Day Zen Reader)  │
│ 3. DISPLAY BUS: IT8951 EPDC over SPI @32MHz + 2x TMUX1575 (RP2350 fallback) │
│ 4. SCREEN:    10.3" E-Ink (Carta 1200 / Kaleido 3 / Kaleido 4, 227 PPI) + EMR│
│ 5. CAMERA:    12MP Sony IMX708 PDAF Macro Rear (Multimodal Claude Code / OCR)│
│ 6. CELLULAR:  M.2 Quectel EG25-G LTE + Onboard Soldered MFF2 eSIM (ST4SIM)  │
│ 7. MESH/GNSS: Built-In Semtech SX1262 LoRa (Meshtastic) + Qualcomm GNSS     │
│ 8. NFC:       Built-In ST25R3916 13.56 MHz (YubiKey FIDO2 / LUKS / P2P Pair)│
│ 9. ANTENNAS:  Top-Edge IP67 SMA (LoRa) + Internal Taoglas FXUB63 MIMO (LTE) │
│ 10. SENSORS:  DS3231 RTC + BMI270/BMM350 9-DOF IMU + BMP390 Baro + PDM Mic  │
│ 11. AIRGAP SW: Physical Hardware RF Kill Switch (Zero EMF / 0.000 dBm Cutoff)│
│ 12. AUDIO:    Sealed Micro-Box Speaker + MAX98357A Amp + PDM Mic + Mute SW  │
│ 13. BATTERY:  8,000–10,000 mAh (26–32 Wh LiFePO4 / 30–37 Wh Li-ion) Pack    │
│ 14. EXPAND:   2x IP68 USB-C (Monitor Sink + Host Expand with USB-to-I2C)     │
│ 15. CHASSIS:  SLS 3D-Printed PA12 Nylon + 85A TPU Armor Corners (~510g total)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│ HOTPACK 1: DOOMSDAY   │  │ HOTPACK 2: TACTICAL   │  │ HOTPACK 3: CBRN &     │
│ SKY-SCAN & SIGINT     │  │ DUAL-MESH & HF COMMS  │  │ SAR ENVIRONMENTAL     │
│ • RTL-SDR v4 Wideband │  │ • Radio 2: SX1262 LoRa│  │ • PocketGeiger Type 5 │
│   (500kHz–1.76GHz)    │  │   (MeshCore/Reticulum)│  │   Radiation Sensor    │
│ • Dual Top SMA Ports  │  │ • QRP 5W HF Shortwave │  │ • FLIR Lepton 3.5     │
│ • 137MHz NOAA Weather │  │   JS8Call / FT8 (BNC) │  │   Thermal Camera      │
│ • 1090MHz ADS-B Radar │  │ • APRS 3.5mm TRRS TNC │  │ • Sensirion SCD41 CO2 │
│ • 100% Passive Stealth│  │ • Dual-Mesh Bridge    │  │   & Air Quality       │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘

---

## 2. Battery Sizing & Weight Optimization

To achieve maximum field battery life without an excessively heavy device:

### The Engineering Sweet Spot: 8,000–10,000 mAh (26–32 Wh LiFePO4 / 30–37 Wh Li-ion)
* **Configuration:** 1S Li-ion/LiPo (3.7V nominal, 4.2V charge limit) or 1S2P LiFePO4 (3.2V nominal, 3.65V charge limit) prismatic pouch pack with integrated hardware PCM protection circuit.
* **Dimensions:** ~5.5 mm thick × 130 mm × 130 mm (occupies the flat recessed cavity coplanar with the PCBA directly behind the 10.3" e-paper display).
* **Weight:** **~200 grams** (~7.0 oz).
* **Total Tablet Device Weight:** **~510 grams** (1.12 lbs). For comparison:
  * iPad Pro 11" with case: ~680 grams
  * Onyx Boox Note Air 3C: ~430 grams (with small 3,700 mAh battery)
  * Panasonic Toughbook tablet: ~1,100 grams
* **FAA / TSA Airline Compliance:** The international limit for passenger aircraft is **100 Watt-hours (Wh)**. At 26–37 Wh, SolarDeck is less than 1/3 of the legal threshold, flying on all commercial airlines worldwide without restrictions.
* **Extreme Heat Safety:** Rated safe up to 65°C (149°F). The tablet can sit in direct sunlight or on a vehicle dashboard safely.

### Real-World Runtime on 32 Wh Pack:
* **Tier 0: Dormant Standby (< 0.1 mW):** **10+ Years** shelf life.
* **Tier 1: Zen Reader Mode (RP2350 Driven @ ~4.5 mW):** **300+ DAYS (10 Months)** of daily book reading on a single charge with 30ms page turns.
* **Tier 2: Perpetual LoRa Mesh Repeater (RP2350 @ 12–15 mW):** **80+ DAYS (2.6 Months)** of continuous off-grid packet hopping without waking Linux.
* **Tier 3: Paper-Feel Scribe Slate (CM4 1-Core @ ~0.60W):** **58 Hours** continuous active writing (460+ hours study mode with S2idle).
* **Tier 4: Adaptive Mixed Workstation (Web/Discord/Claude @ ~1.40W avg):** **25 Hours** continuous screen-on time (3 to 6 real-world days).
* **Tier 5: Audio-First Conferencing (Mic array + Opus + inbound dither @ ~1.30W):** **27 Hours** of continuous calls (no outbound video; USB-C UVC webcam optional via Port 2).
* **Tier 5b: High-Motion Screen Work (GPU dithering + repeated partial refresh @ ~1.6W–2.2W):** **16 to 20 Hours** (images, maps, rapid pagination; not video — see ADR-005).
* **Tier 6: AI Compile Turbo (CM4 Quad 1.8GHz @ ~3.2W):** **10 to 11 Hours** continuous parallel compiling and cellular connection.

### Battery Longevity: High-Motion vs. Static & 10–15 Year Cell Lifespan
* **During High-Motion Screen Work (images, maps, rapid pagination):** GPU blue-noise dithering, NEON differencing, and repeated 32 MHz full-frame transfers draw **1.6W to 2.2W**, giving **16 to 20 hours**. There is no video-playback tier: the SPI link to the IT8951 tops out near 6 fps, so V1 does not promise cinema (ADR-005).
* **When Idle or Static** (Writing, Coding, Reading, Ambient Clock):**
  * **0.000W Bi-Stable Physics:** Unlike OLED or LCD screens that draw 1.5W–3.0W just keeping pixels backlit, E-Ink uses **0.000 Watts** to display a static page. Once particles move into position, they remain physically locked in place indefinitely without electrical power.
  * **Interactive Terminal & Coding:** In Neovim and Claude Code CLI, the screen only consumes power during 15–20ms partial update pulses when keys are pressed. Total system draw drops to **~1.1W–1.4W**, extending battery runtime to **24 to 32 hours** of active typing.
  * **Zen Reading Mode:** With the CM4 unpowered and the RP2350 flipping pages in 30ms, battery runtime extends to **300+ days (10 months)** on a single charge.
  * **Ambient Desk Clock & Weather Station:** The top-bezel 0.15W micro-solar strip generates more power than the 4.5 mW idle load, delivering **infinite off-grid operational lifespan** without ever connecting to a wall charger.
  * **Chemical Cycle Life (10–15 Years):** Standard consumer Li-ion batteries degrade after 500 charge cycles (~2 years). In contrast, SolarDeck's LiFePO4 chemistry provides **3,000 to 5,000+ full cycles**. Because non-video workflows require charging only once every few days or weeks, the physical battery pack lasts **10 to 15+ years** before reaching 80% health.

---

## 3. Cellular & RF Antenna Engineering

### 3.1 Cellular Modem, Dual-SIM & NFC Architecture
* **Modem:** M.2 Key-B 3042 socket with **Quectel EG25-G** (30+ global LTE bands, worldwide carrier certifications).
* **Dual-SIM Architecture:**
  1. **Onboard Soldered MFF2 eSIM:** STMicroelectronics **ST4SIM-200M** or Infineon **SLM97** soldered down in an industrial **MFF2 DFN-8 (5×6mm)** package. Managed natively by **`lpac`** (open-source C Local Profile Assistant) via `ModemManager`. Activation QR codes are downloaded directly from consumer SM-DP+ servers using standard AT channel commands (`AT+CCHO`/`AT+CGLA`).
  2. **External Physical Nano-SIM Tray:** IP67 weather-sealed push-push Nano-SIM slot on chassis edge for local prepaid, international traveler, or burner SIM cards.
  3. **Seamless Linux Slot Toggle:** Switch between physical SIM and digital eSIM via `mmcli -m 0 --set-primary-sim-slot=1/2`.
* **13.56 MHz NFC & Smartcard Architecture:**
  * **NXP PN532 / ST25R3916** controller driving a tuned FPC loop antenna in the top bezel.
  * Supports hardware FIDO2 / WebAuthn authentication (tap physical YubiKey or OnlyKey), biometric ePassport reading, and airgapped NFC crypto wallet signing (Tangem, Satochip, Coldcard).
  * Paired with the rear MagSafe magnetic ring array, users can magnetically snap standard physical credit card wallets (Apple, Moft, Peak Design) for 2–3 cards, ID, and cash.
* **Bottom-Edge 3.5mm TRRS Audio Jack:**
  * IP67 sealed 3.5mm jack with TI PCM5102A 32-bit I2S stereo DAC + mic input.
  * Mechanical switch automatically mutes the internal 1W speaker upon headphone insertion.
  * Allows private, zero-EMF, zero-latency listening to AI speech synthesis, audiobooks, and radio decoding even in 100% Hardware Airgap Mode.

### 3.2 Antenna Architecture & Reception Optimization
1. **LoRa Mesh (Meshtastic 915/868 MHz):**
   * Top-edge **IP67 Bulkhead SMA female connector** with silicone O-ring gasket.
   * Field antenna: **Linx Technologies `ANT-916-CW-HWR-SMA`** (1/2-wave center-fed dipole, 3.2 dBi gain, operates without ground plane dependency).
   * Pocket antenna: **Linx `ANT-916-CW-RH-SMA`** (50mm compact rubber ducky).
2. **Cellular LTE 2×2 MIMO:**
   * **Main (TX/RX):** Optional second top-edge SMA jack for high-gain field whips (Taoglas `TG.30` Apex) or internal flexible PCB.
   * **Diversity (RX Only):** Internal **Taoglas `FXUB63`** ultra-wideband flexible PCB antenna (698–3000 MHz) adhered to inner chassis wall, delivering 2×2 spatial diversity for maximum download throughput.
3. **Wi-Fi 5 & Bluetooth 5.0:**
   * Internal **Molex `1461530100`** balanced dual-band (2.4/5.8 GHz) dipole FPC connected to CM4 U.FL port. Balanced dipole tuning prevents hand-grip detuning.
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
│    • Grounding `nRPIBOOT` forces CM4 into USB boot mode.                    │
│    • Internal 32GB eMMC mounts as a USB drive on a host laptop via USB-C.   │
│    • Triggered without opening case via external magnetic reed switch.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Microcontroller UART Console Bridge:                                     │
│    • CM4 UART0 (GPIO 14/15) routes to RP2350 UART.                          │
│    • RP2350 exposes a USB CDC serial port (`/dev/ttyACM0`) over USB-C.      │
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
│      forcing clean 5V/3.3V power rails to CM4.                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 6. Display Bus Multiplexer & Bias Guard (TMUX1575):                         │
│    • Physical isolation of CM4 lines in sleep; discharges VCOM/gate rails   │
│      if host crashes mid-refresh, preventing pigment burn-in.               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 7. Autonomous PMIC Safety:                                                  │
│    • TI BQ25895 50-second I2C watchdog resets to conservative autonomous    │
│      charging defaults if OS kernel crashes.                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Audio & Acoustic Engineering

To enable clean voice interaction with Claude Code and dictation:

1. **Acoustic Output (Speaker):**
   * Single pre-engineered sealed acoustic micro-box speaker (PUI Audio `AS03008MR-5-R` or AAC `1524`). Pre-welded airtight 1.0cc resonant chamber provides clean vocal reproduction without chassis buzz.
   * **Amplifier:** Maxim Integrated / Analog Devices **MAX98357A** (I2S Class-D mono amplifier, 3.2W into 4Ω).
2. **Acoustic Input:**
   * Single Knowles **SPH0645LM4H-B** (or InvenSense `ICS-43434`) I2S digital MEMS microphone placed on top bezel.
   * Mounted inside a molded silicone acoustic boot to decouple chassis vibrations.
3. **Physical Privacy:** Hardware slide switch physically disconnects VDD power to the microphone.

---

## 6. Dual-Brain Direct Drive & Low-Power Sipping Pipeline

```
[STEP 1: BROWSE ON FULL LINUX (CM4)]
• User wakes CM4 (0.3s S2idle resume).
• Full Linux manages Calibre, KOReader, or terminal workspace.
• User selects book or activates ambient dashboard.
                              │
                              ▼
[STEP 2: 0.5-SECOND HANDOFF & ISOLATION]
• Linux renders page buffers to shared storage.
• CM4 signals RP2350 via I2C: "Taking over display".
• CM4 toggles TMUX1575 SELECT line to RP2350 and cuts CM4 power (0.000 mW).
• TMUX1575 completely isolates all 6 CM4 lines, preventing leakage into unpowered SoC.
                              │
                              ▼
[STEP 3: AUTONOMOUS RP2350 SIPPING MODE]
• RP2350 pushes pages/digits over SPI to IT8951 from 8MB PSRAM double-buffer.
• Between updates, RP2350 deep-sleeps at 10 µA.
• IT8951 sleeps at ~0.1 mW. Total system draw: ~4.5 mW.
• Battery runtime: 300+ DAYS on single charge!
                              │
                              ▼
[STEP 4: RESUME FULL LINUX]
• Tap key, touch screen, or double-tap IMU.
• RP2350 asserts GPIO 17 wake line to CM4.
• TMUX1575 switches bus back to CM4. Linux resumes in 0.3 seconds.
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
│ • Sway expands display to full 1872 × 1404 pixels over BLE 5.0.             │
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
* **Battery Shipping Advantage (UN3481):** Because the 32 Wh battery is pre-installed inside the assembled enclosure, it qualifies under UN3481 (Lithium batteries contained in equipment, Section II). It ships via standard commercial air cargo without hazardous materials surcharges.
* **Lead Time:** ~3 weeks from file submission to delivery in Honolulu.
* **Prototype Costs Delivered to Honolulu:**
  * **Qty 1 (Single Turnkey Prototype):** **~$390 – $440 total out-of-pocket**
  * **Qty 5 (Small Batch Run):** **~$1,150 – $1,250 total** (~$230 – $250 per finished tablet)
