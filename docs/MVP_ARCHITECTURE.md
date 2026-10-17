# SolarDeck MVP & Modular System Architecture

Written 2026-10-17 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Executive Strategy: Core Tablet MVP vs. Modular Expansion

SolarDeck is a sovereign, general-purpose open-hardware computing platform designed for AI-assisted development, field reading/writing, and off-grid communication. The architecture cleanly separates the core platform from specialized add-on modules:

1. **The Core MVP Tablet:** The standalone sovereign device containing the essential platform:
   * Bare-metal Linux coding & computing platform (Raspberry Pi CM4)
   * Sunlight-readable 10.3" e-paper reader and Wacom EMR digitizer slate
   * Built-in off-grid mesh communicator (Semtech SX1262 LoRa / Meshtastic)
   * Worldwide Multi-Constellation Satellite Navigation (u-blox MAX-M10S: GPS + BeiDou-3 + Galileo + QZSS + GLONASS)
   * Dual-brain ultra-low-power supervisor (RP2040) for perpetual desk clock & Kindle modes
   * Maximum-capacity **10,000 mAh (32 Wh) LiFePO4** battery (safe to 65°C, 3,000+ cycles, airline-compliant)
   * Lightweight, rugged SLS 3D-printed PA12 Nylon enclosure
2. **Modular Expansion Packs:** High-complexity or specialized payloads offloaded to snap-on or USB-C modules:
   * **RF Multi-Tool Pod:** Flipper Zero suite (Sub-GHz CC1101, NFC, RFID, IR blaster)
   * **Cellular M.2 Pod:** Worldwide Quectel EG25-G (30+ global LTE bands) + onboard eSIM
   * **Satellite SOS Pod:** Commercial two-way satellite transceivers (RockBLOCK 9603 Iridium / Swarm)
   * **Industrial Deck Link:** CAN Bus 2.0B / M8 Gigabit Ethernet bridge

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK MVP (THE CORE TABLET)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. BRAIN:     Raspberry Pi CM4 (4GB RAM, 32GB eMMC, Wi-Fi/BT)               │
│ 2. CO-PROC:   RP2040 (24/7 Power Supervisor, Clock Tick, Instant Wake)      │
│ 3. SCREEN:    10.3" E-Ink (Carta 1200 or Kaleido 3) + Wacom EMR + Touch    │
│ 4. COMMS:     Built-In Semtech SX1262 LoRa (868–928MHz Global Wideband)     │
│ 5. GNSS:      u-blox MAX-M10S (GPS, BeiDou-3, Galileo, QZSS, GLONASS)       │
│ 6. MOTION:    6-Axis IMU (ST LSM6DS3: Auto-Rotate, Heading, Tap-to-Wake)    │
│ 7. AUDIO:     Sealed Micro-Box Speaker + Smart Amp + MEMS Mic + Mute Switch │
│ 8. BATTERY:   10,000 mAh (32 Wh) LiFePO4 (200g, 65°C Safe, 3,000+ Cycles)   │
│ 9. EXPAND:    1x Qwiic (I2C) + 2x IP68 USB-C + 8-Pin Rear Magnetic Pogo Bus │
│ 10. CHASSIS:  SLS 3D-Printed PA12 Nylon + 85A TPU Armor Corners (~510g total)│
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────┐     ┌───────────────────────────────────────┐
│ FUTURE MODULE 1: RF BACKPACK  │     │ FUTURE MODULE 2: TACTICAL / SATELLITE │
│ • Flipper Zero Sub-GHz CC1101 │     │ • Worldwide 4G/LTE (Quectel EG25-G)   │
│ • 13.56MHz NFC & 125kHz RFID  │     │ • Onboard eSIM (eUICC) + Nano-SIM     │
│ • IR Blaster & Receiver       │     │ • Iridium / Swarm Satellite SOS       │
│ • Connects via USB-C or Pogo  │     │ • CAN Bus 2.0B / Industrial M8 Bridge │
└───────────────────────────────┘     └───────────────────────────────────────┘
```

---

## 2. Battery Sizing & Weight Optimization

To achieve the absolute maximum field battery life without creating an excessively heavy device:

### The Engineering Sweet Spot: 10,000 mAh (32 Watt-hours) LiFePO4
* **Configuration:** 1S2P prismatic pouch cell pack (two flat 5,000 mAh 3.2V cells in parallel with integrated hardware PCM protection circuit).
* **Dimensions:** ~5.5 mm thick × 130 mm × 130 mm (occupies the flat recessed cavity directly behind the 10.3" e-paper display).
* **Weight:** **~200 grams** (~7.0 oz).
* **Total Tablet Device Weight:** **~510 grams** (1.12 lbs). For comparison:
  * iPad Pro 11" with case: ~680 grams
  * Onyx Boox Note Air 3C: ~430 grams (with small 3,700 mAh battery)
  * Panasonic Toughbook tablet: ~1,100 grams
* **FAA / TSA Airline Compliance:** The international limit for passenger aircraft is **100 Watt-hours (Wh)**. At 32 Wh, SolarDeck is less than 1/3 of the legal threshold, flying on all commercial airlines worldwide without restrictions.
* **Extreme Heat Safety:** Unlike standard Lithium-Polymer (which swells and risks thermal runaway above 45°C), **LiFePO4 is rated safe up to 65°C (149°F)** with zero fire hazard. The tablet can sit in direct tropical sunlight or on a vehicle dashboard safely.

### Real-World Runtime on 10,000 mAh (32 Wh):
* **Full AI Workstation Mode (CM4 Quad-Core @ ~3.0W):** **10.5 to 11 Hours** of continuous Claude Code development, compilation, and terminal work.
* **Scholar / Study Mode (CM4 with S2idle @ ~0.3W avg):** **100+ Hours** of active reading and Wacom stylus note-taking.
* **Pure Kindle Mode (RP2040 Driven @ ~0.001W):** **6 to 9 MONTHS** of daily book reading (2 hours/day) on a single charge.
* **Ambient Desk Clock Mode (RP2040 1-Sec Tick @ ~0.008W):** **166 DAYS (5.5 Months)** of a live ticking desk clock without ever plugging into a wall.

---

## 3. Global Satellite Navigation & Multi-Region Wireless

To ensure SolarDeck works natively in the Americas, Europe, and Asia:

1. **Global Multi-Constellation GNSS (u-blox MAX-M10S):**
   * Concurrent reception of **all 4 global constellations**: US GPS, Chinese **BeiDou-3**, European **Galileo**, and Russian **GLONASS**, plus Japanese **QZSS (Michibiki)**.
   * BeiDou-3 and QZSS provide superior coverage across East Asia, Southeast Asia, Hawaii, and the Pacific basin, delivering instant fixes even in urban canyons or mountainous terrain.
   * 15 mW ultra-low-power operation; feeds standard NMEA data to Linux `gpsd` for Google Maps, OsmAnd, and FoxtrotGPS.
2. **Worldwide Off-Grid Mesh (Semtech SX1262 LoRa):**
   * Equipped with a **wideband 868–928 MHz tuned antenna**.
   * Software-switchable between **US915** (Americas/Hawaii), **EU868** (Europe), and **AS923** (Asia/Oceania) with zero hardware modifications (`meshtastic --set-region <REGION>`).
3. **Worldwide Cellular Compatibility (Add-On / Tethering):**
   * Cellular carrier lines: T-Mobile Essentials phone hotspot provides $0 free data sharing. For dedicated SIMs, **Tello** provides 2GB LTE for $6/month on the T-Mobile network.
   * Modular cellular pod utilizes the global **Quectel EG25-G** (30+ global LTE bands) with physical Nano-SIM and onboard MFF2 **eSIM (eUICC)** for instant local digital data plans in 150+ countries.

---

## 4. Hardware Anti-Bricking & Recovery Architecture

To ensure experimental kernel hacking, DRM waveform tuning, and firmware updates cannot permanently brick the sealed device:

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
│    • CM4 UART0 (GPIO 14/15) routes to RP2040 UART.                          │
│    • RP2040 exposes a USB CDC serial port (`/dev/ttyACM0`) over USB-C.      │
│    • Stream early kernel dmesg / panic logs even if screen is dead.         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. RP2040 ROM `BOOTSEL` Recovery:                                           │
│    • External button / pin pull drops RP2040 into `RPI-RP2` USB drive mode  │
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
│ 6. IT8951 EPDC DC-Bias Guard:                                               │
│    • 200ms hardware watchdog discharges high-voltage VCOM/gate rails to     │
│      ground if Linux hangs mid-refresh, preventing pigment burn-in.         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 7. Autonomous PMIC Safety:                                                  │
│    • TI BQ25895 50-second I2C watchdog resets to conservative autonomous    │
│      LiFePO4 charging defaults if OS kernel crashes.                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Far-Field Audio & Acoustic Engineering

To enable rich voice interaction with Claude Code and far-field voice recognition (10–15 ft):

1. **Acoustic Output (Speakers):**
   * **Drivers:** Dual pre-engineered sealed acoustic micro-box speakers (PUI Audio `AS03008MR-5-R` or AAC `1524`). Pre-welded airtight 1.0cc resonant chambers provide clean low-frequency vocal body without chassis rattle.
   * **Smart Amplifier:** Texas Instruments **TAS2563** (5.7W Class-D with integrated boost converter and real-time IV-sense coil protection).
2. **Acoustic Input (Far-Field Beamforming):**
   * **Mics:** Dual Knowles `SPH0645LM4H-B` or InvenSense `ICS-43434` I2S digital MEMS microphones spaced 180mm apart on the top bezel.
   * **Isolation:** Mounted inside molded silicone acoustic boots to decouple speaker vibrations from the chassis.
   * **Barge-In DSP:** Linux PipeWire WebRTC acoustic echo cancellation (`module-echo-cancel`) subtracts the tablet's voice output in real-time, allowing interruptions mid-sentence.
3. **Physical Privacy:** Hardware 2-pole slide switch physically cuts VDD to the microphones.

---

## 6. The "Smart-Cache Handoff" Kindle Reading Mode

To achieve month-long e-reader battery life without sacrificing full Linux library management:

```
[STEP 1: BROWSE ON FULL LINUX (CM4)]
• User wakes CM4 (0.3s resume).
• Full Linux manages Calibre, KOReader, or custom UI across 100GB+ storage.
• User selects book to read.
                              │
                              ▼
[STEP 2: 0.5-SECOND HANDOFF]
• Linux pre-renders the book/chapters into compressed page buffers on MicroSD.
• CM4 updates RP2040 via I2C: "Reading Book X, Page Y".
• CM4 Linux powers completely down (0.000 mW).
                              │
                              ▼
[STEP 3: AUTONOMOUS RP2040 READING]
• RP2040 reads page buffers from SD card and pushes them over SPI to IT8951.
• Between page turns, RP2040 sleeps at 0.05 mW.
• Screen draws 0 mW while reading.
• Battery life: 6 to 9 MONTHS on single charge!
                              │
                              ▼
[STEP 4: SWITCH BOOKS]
• Tap "Library" or double-tap chassis (IMU interrupt).
• CM4 resumes in 0.3s to pick another book or start coding.
```

---

## 7. The Magnetic "SnapDeck" Hybrid Keyboard System (On-Screen & Propped-Up Modes)

To solve the fatal flaw of commercial e-paper tablets—where typing on flat glass lacks tactile feedback and carrying an external laptop keyboard is cumbersome—SolarDeck introduces the **SnapDeck** detachable mechanical keyboard system.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE 4 OPERATING POSTURES                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 1: ON-SCREEN LAPDECK (LANDSCAPE)                                    │
│ • Keyboard rests magnetically on bottom 1/3 of the landscape screen.        │
│ • Hall sensor triggers Sway Wayland to resize workspace to top 2/3          │
│   (1872 × 950 px). Bottom 1/3 screen goes dormant (0W).                     │
│ • Use Case: Typing on lap, in bed, on a bus, or airplane tray table.        │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 2: PROPPED-UP LAPTOP (LANDSCAPE)                                    │
│ • Rear friction kickstand props tablet upright at 65°–75° on desk.          │
│ • Keyboard sits detached on the desk in front of the screen.                │
│ • Sway expands display to full 1872 × 1404 pixels over BLE 5.0.             │
│ • Use Case: Traditional laptop workstation at a coffee shop or desk.        │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 3: VERTICAL CODER WORKSTATION (PORTRAIT)                            │
│ • Kickstand props tablet upright in tall Portrait orientation.              │
│ • 80+ lines of code visible vertically (like a programmer's vertical screen).│
│ • Full-width keyboard sits detached on the desk.                            │
│ • Use Case: Reading long source files, logs, and technical documentation.   │
├─────────────────────────────────────────────────────────────────────────────┤
│ POSTURE 4: PURE SLATE / SCRIBE MODE                                         │
│ • Keyboard snaps magnetically onto the REAR of the tablet chassis.          │
│ • Rear Hall sensor disables key presses to prevent accidental clicks.       │
│ • Use Case: Lightweight handheld e-reader, PDF annotation, Wacom sketching. │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Mechanical & Electrical Design:
1. **Key Switches:** Ultra-slim (3.5mm total thickness) Kailh X-Switch or scissor-switch mechanical keys with 1.2mm travel and crisp tactile actuation.
2. **Controller & Firmware:** Powered by an **nRF52840** running open-source **ZMK Firmware**, supporting sub-millisecond wireless latency and multi-device Bluetooth switching.
3. **Power & Docking:** Contains a thin 150 mAh LiPo cell that charges automatically via two magnetic gold pogo pins on the tablet bezel whenever docked on-screen or stored on the rear.
4. **Dual Hall-Effect Interlocks:**
   * **Front Bezel Hall Sensor:** Trips when keyboard is on the screen, instantly instructing Wayland to repartition the display to the top 2/3.
   * **Rear Chassis Hall Sensor:** Trips when keyboard is snapped to the back, sleeping the keys so your fingers can grip the tablet firmly while reading.

---

## 8. Expansion Interfaces & Topology

```
INTERFACE             FORM FACTOR           PINOUT / SIGNALS          APPLICATIONS
─────────────────────────────────────────────────────────────────────────────────────────────
Qwiic / STEMMA QT     4-pin JST-SH 1.0mm    3.3V, GND, SDA, SCL       Daisy-chained environmental sensors, CO2
USB-C Port 1 (PD)     IP68 Sealed Type-C    USB 2.0 OTG + 20W PD      Charging, PC rescue, early dmesg UART
USB-C Port 2 (Host)   IP68 Sealed Type-C    USB 2.0 Host (5V @ 2A)    RTL-SDR radio dongle, thermal camera, drives
Rear Expansion Bus    8-pin Magnetic Pogo   VBAT, GND, USB+/-,        Snap-on RF pod, Satellite SOS, RTK GPS
                                            UART TX/RX, I2C, Wake
CAN Bus 2.0B          3-Pin Rugged Jack     CAN_H, CAN_L, GND         Automotive OBD-II, robotics, deck link
Gigabit Ethernet      M8 4-pin or slim RJ45 1000BASE-T (from CM4)     Direct 1 Gbps inter-deck mesh cluster
```

---

## 9. Turnkey Manufacturing in Shenzhen & Delivery to Honolulu

A prototype can be 100% manufactured, clean-room assembled, QA tested, and boxed in Shenzhen, then shipped via DHL Express directly to Honolulu:

* **Turnkey Box-Build Vendors:** PCBWay, Seeed Studio Fusion, Makerfab.
* **Battery Shipping Advantage (UN3481):** Because the 10,000 mAh LiFePO4 battery is pre-installed inside the assembled enclosure, it qualifies under UN3481 (Lithium batteries contained in equipment, Section II). It ships via standard commercial air cargo without hazardous materials surcharges.
* **Lead Time:** ~3 weeks from file submission to delivery in Honolulu.
* **Prototype Costs Delivered to Honolulu:**
  * **Qty 1 (Single Turnkey Prototype):** **~$430 – $480 total out-of-pocket**
  * **Qty 5 (Small Batch Run):** **~$1,250 – $1,350 total** (~$250 – $270 per finished tablet)

---

## 10. Satellite & Cellular Economics

1. **Cellular Connectivity on T-Mobile Essentials Choice 55:**
   * Standalone T-Mobile tablet add-on costs $15/mo ($20 without AutoPay); the $5 tier is restricted to Go5G Next.
   * **Zero-Cost Path:** Tether to phone Wi-Fi/Bluetooth hotspot ($0/mo, included with Essentials).
   * **Low-Cost Dedicated SIM:** **Tello** (runs on T-Mobile network) data SIM at **$6/month for 2GB LTE**.
2. **Satellite Transceiver Economics:**
   * **Downlink (Receiving): 100% FREE.** Using an RTL-SDR dongle on USB-C, SolarDeck decodes live NOAA-15/18/19 weather imagery (137 MHz APT), Meteor-M2 digital Earth photos, and GNSS atomic time worldwide for $0.
   * **Uplink (Commercial): Paid.** RockBLOCK 9603 (Iridium) costs ~$250 hardware + $15/mo line rental + $0.06–$0.12/msg; Swarm (SpaceX IoT) costs ~$5/mo.
   * **Uplink (Amateur Radio / Ham): 100% FREE.** With a standard Technician license, users can transmit digital APRS packets and text messages through the International Space Station (145.825 MHz digipeater) and amateur cubesats for $0.
   * **Local Off-Grid Mesh: 100% FREE.** The internal Semtech SX1262 LoRa radio (915 MHz) provides perpetual, encrypted, license-free messaging across 5–15 miles via Meshtastic.

---

## 11. Bill of Materials: Core MVP vs. Modular Add-ons

### Core Tablet MVP Bill of Materials (Turnkey Qty 1–5):

| Category | Component Description | Primary Supplier / Model | Est. Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- |
| **Compute** | Raspberry Pi CM4 (4GB RAM, 32GB eMMC, Wi-Fi/BT) | PiShop / DigiKey (`CM4104032`) | $55.00 |
| **Co-Processor** | Dual Cortex-M0+ Microcontroller | Raspberry Pi `RP2040` | $1.00 |
| **RTC** | High-Precision TCXO Real-Time Clock | Maxim `DS3231SN#` | $2.50 |
| **Motion / IMU** | 6-Axis Accelerometer / Gyroscope | ST `LSM6DS3TR-C` or `LIS3DH` | $0.85 |
| **Navigation** | Multi-Constellation GNSS Receiver | u-blox `MAX-M10S` (Wideband Ant) | $14.00 |
| **Display Panel** | 10.3" E-Ink (Carta 1200 / Kaleido 3) + Touch + EMR | Good-Display / Waveshare | $110.00 – $135.00 |
| **EPDC Controller**| IT8951 Controller Board & Flat Cable | Waveshare / ITE | $18.00 |
| **Stylus** | Wacom EMR Passive Stylus with Eraser | Staedtler Noris Digital | $25.00 |
| **Off-Grid Radio** | Semtech SX1262 868–928 MHz LoRa Module (+22dBm) | Ebyte `E22-900M22S` | $5.50 |
| **Battery** | 10,000 mAh 3.2V (32 Wh) Prismatic LiFePO4 Pack | Batteryhookup / Custom (1S2P) | $16.00 |
| **Power PMIC** | Synchronous MPPT I2C Buck Charger | Texas Instruments `BQ25895RTWR` | $3.50 |
| **Audio** | Dual AAC Micro-Box Speakers + TI TAS2563 Amp | PUI Audio / TI `TAS2563` | $7.30 |
| **Mics & Switch** | Dual I2S MEMS Mics + Hardware Mute Switch | Knowles `SPH0645` + C&K Slide | $3.00 |
| **Connectors** | Qwiic JST-SH + 2x IP68 USB-C + 8-Pin Rear Pogo | LCSC / Amphenol | $6.50 |
| **Carrier PCBA** | 4-Layer ENIG Motherboard + SMT Assembly | JLCPCB Turnkey | ~$25.00 |
| **Chassis** | SLS 3D-Printed PA12 Nylon + TPU Bumpers | JLC3D / Craftcloud | $25.00 |
| **TOTAL CORE MVP**| *(Everything to build the fully functional tablet)* | | **~$318 – $343** *(Qty 1)*<br>**~$235 – $265** *(Batch Qty 5)* |

### Modular Add-On Packs (Optional / Phase 2):

| Add-On Pack | Components Included | Est. Module Cost |
| :--- | :--- | :--- |
| **RF Multi-Tool Pod** | ESP32-S3 + CC1101 Sub-GHz + PN532 NFC + EM4095 RFID + IR TX/RX + LiPo | ~$28.00 |
| **Worldwide Cellular Pod** | Quectel EG25-G Global LTE + eSIM + Nano-SIM Tray + Antennas | ~$38.00 |
| **Satellite SOS Pod** | RockBLOCK 9603 (Iridium) or Swarm M138 IoT Transceiver | ~$115.00 – $260.00 |
| **Industrial / CAN Pod**| Microchip MCP2515 CAN controller + M8 Gigabit Ethernet receptacle | ~$18.00 |
