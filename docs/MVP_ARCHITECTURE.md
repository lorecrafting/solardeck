# SolarDeck MVP & Modular System Architecture

Written 2026-10-17 17:26 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Executive Strategy: Core Tablet MVP vs. Modular Expansion

To minimize first-prototype manufacturing risk, reduce BOM costs, and accelerate software bring-up, the SolarDeck architecture is partitioned into:
1. **The Core MVP Tablet:** The standalone sovereign device containing the essential "Holy Trinity":
   * Bare-metal Linux coding & research computer (CM4)
   * Sunlight-readable 10.3" e-paper reader and Wacom EMR notebook
   * Built-in off-grid mesh communicator (Semtech SX1262 LoRa / Meshtastic)
   * Dual-brain ultra-low-power supervisor (RP2040) for perpetual clock & Kindle modes
   * Safe, high-cycle LiFePO4 battery power
2. **Modular Expansion Packs:** High-complexity, specialized, or regulatory-heavy subsystems offloaded to snap-on or USB-C modules (Flipper Zero RF multi-tool, cellular modem, satellite SOS).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK MVP (THE CORE TABLET)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. BRAIN:     Raspberry Pi CM4 (4GB RAM, 32GB eMMC, Wi-Fi/BT)               │
│ 2. CO-PROC:   RP2040 (24/7 Power Supervisor, Clock Tick, Instant Wake)      │
│ 3. SCREEN:    10.3" E-Ink (Carta 1200 or Kaleido 3) + Wacom EMR + Touch    │
│ 4. COMMS:     Built-In Semtech SX1262 915MHz LoRa (Meshtastic Off-Grid Mesh)│
│ 5. SENSORS:   u-blox GNSS/GPS + 6-Axis IMU (Auto-Rotate & Tap-to-Wake)      │
│ 6. AUDIO:     Sealed Micro-Box Speaker + Smart Amp + MEMS Mic + Mute Switch │
│ 7. POWER:     LiFePO4 6,400mAh Battery (Safe to 65°C) + BQ25895 Charger     │
│ 8. EXPAND:    1x Qwiic (I2C) + 2x IP68 USB-C + 8-Pin Rear Magnetic Pogo Bus │
│ 9. CHASSIS:   SLS 3D-Printed PA12 Nylon + 85A TPU Armor Corners             │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
┌───────────────────────────────┐     ┌───────────────────────────────────────┐
│ FUTURE MODULE 1: RF BACKPACK  │     │ FUTURE MODULE 2: TACTICAL / SATELLITE │
│ • Flipper Zero Sub-GHz CC1101 │     │ • 4G/LTE M.2 Cellular Modem          │
│ • 13.56MHz NFC & 125kHz RFID  │     │ • Centimeter RTK GPS Base Station     │
│ • IR Blaster & Receiver       │     │ • Iridium / Swarm Satellite SOS       │
│ • Connects via USB-C or Pogo  │     │ • CAN Bus 2.0B / Industrial M8 Bridge │
└───────────────────────────────┘     └───────────────────────────────────────┘
```

---

## 2. Why Offloading the RF Multi-Tool (Flipper Zero) Wins

1. **RF Coexistence & EMI Isolation:** Moving the CC1101 (300–928MHz), PN532 (13.56MHz NFC), EM4095 (125kHz RFID), and high-power IR circuitry off the main board prevents digital noise from the CM4 CPU and switching regulators from de-sensing weak RF signals.
2. **Airport & Border Compliance:** A tablet with embedded hardware hacking tools, cloner coils, and sub-GHz replay capabilities triggers security scrutiny. The tablet remains an innocuous e-reader/laptop; the RF cartridge can be detached and packed separately.
3. **Carrier Board Yield & Cost:** Dropping 4 RF ICs and custom antenna loop matching cuts the carrier PCB layer count and SMT placement risk by over 40%.
4. **Wireless / Tethered Flexibility:** Equipped with an ESP32-S3 or nRF52840, the RF pod connects via the rear pogo pins (docked USB mode) or untethered via BLE 5.0 (place the pod near a target while controlling it from 30 feet away).

---

## 3. Hardware Anti-Bricking & Recovery Architecture

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

## 4. Far-Field Audio & Acoustic Engineering

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

## 5. Navigation, Motion & Auto-Rotation (GPS + 6-Axis IMU)

1. **GNSS / GPS Receiver:**
   * **Chip:** u-blox **SAM-M8Q** (integrated patch antenna) or **NEO-M9N** (UART/I2C).
   * **Capability:** Concurrent reception of GPS, Galileo, GLONASS, and BeiDou; supplies NMEA/UBX streams to Linux `gpsd` for Google Maps, OsmAnd, FoxtrotGPS.
2. **6-Axis Motion / IMU:**
   * **Chip:** ST **LSM6DS3TR-C** or **LIS3DH** (I2C, ~4µA standby).
   * **Display Auto-Rotation:** Managed by `iio-sensor-proxy` + Sway Wayland, rotating screen and Wacom digitizer coordinates automatically between landscape and portrait.
   * **Map Heading:** Calculates compass orientation while stationary (solving GPS heading freeze).
   * **Tap-to-Wake:** Hardware double-tap interrupt wakes the system from deep sleep.

---

## 6. Dual-Brain Power Profiles & The "Kindle Mode" Handoff

```
PROFILE            ACTIVE BRAIN      POWER DRAW    BATTERY LIFE     USE CASE
─────────────────────────────────────────────────────────────────────────────────────────────
1. Full Workstation  CM4 Quad-Core   2.5W – 4.5W   7 – 9 Hours      Claude Code, LTE, Meshtastic, Wi-Fi
2. Scholar / Study   CM4 + S2idle    0.015W – 0.5W 12 – 18 Hours    PDFs, Kiwix, Wacom Note-Taking
3. Pure Kindle Mode  RP2040 Only     ~0.001W       3 – 6 MONTHS     EPUB/Text Reading, Zero Distraction
4. Ambient Desk Clock RP2040 + RTC   ~0.008W       3+ MONTHS        Live 1-sec ticking clock on desk
```

### The "Smart-Cache Handoff" Workflow for Month-Long Reading:
1. **Browse on Linux (CM4):** Wake CM4 to search Calibre/KOReader, manage 100GB Kiwix libraries, and select books.
2. **The 0.5-Second Handoff:** Linux slices the book/chapters into pre-rendered, compressed page buffers stored on shared storage (MicroSD) and notifies the RP2040 over I2C.
3. **Linux Powers Off (0 mW):** CM4 completely shuts down.
4. **RP2040 Autonomous Reading:** RP2040 reads pre-rendered page buffers and blits them to the IT8951 over SPI. Between page turns, the RP2040 sleeps at **0.05 mW**.
5. **Quick Shelf:** RP2040 maintains a lightweight list of the 3–5 most recent books without waking Linux.

---

## 7. Expansion Interfaces & Topology

```
INTERFACE             FORM FACTOR           PINOUT / SIGNALS          APPLICATIONS
─────────────────────────────────────────────────────────────────────────────────────────────
Qwiic / STEMMA QT     4-pin JST-SH 1.0mm    3.3V, GND, SDA, SCL       Daisy-chained GPS, BME680, CO2, Geiger
USB-C Port 1 (PD)     IP68 Sealed Type-C    USB 2.0 OTG + 20W PD      Charging, PC rescue, early dmesg UART
USB-C Port 2 (Host)   IP68 Sealed Type-C    USB 2.0 Host (5V @ 2A)    RTL-SDR dongle, thermal camera, flash drive
Rear Expansion Bus    8-pin Magnetic Pogo   VBAT, GND, USB+/-,        Snap-on RF pod, Satellite SOS, RTK GPS
                                            UART TX/RX, I2C, Wake
CAN Bus 2.0B          3-Pin Rugged Jack     CAN_H, CAN_L, GND         Automotive OBD-II, robotics, deck link
Gigabit Ethernet      M8 4-pin or slim RJ45 1000BASE-T (from CM4)     Direct 1 Gbps inter-deck mesh cluster
```

---

## 8. Satellite & Cellular Economics

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

## 9. Bill of Materials: Core MVP vs. Modular Add-ons

### Core Tablet MVP Bill of Materials (Turnkey Qty 1–5):

| Category | Component Description | Primary Supplier / Model | Est. Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- |
| **Compute** | Raspberry Pi CM4 (4GB RAM, 32GB eMMC, Wi-Fi/BT) | PiShop / DigiKey (`CM4104032`) | $55.00 |
| **Co-Processor** | Dual Cortex-M0+ Microcontroller | Raspberry Pi `RP2040` | $1.00 |
| **RTC** | High-Precision TCXO Real-Time Clock | Maxim `DS3231SN#` | $2.50 |
| **Motion / IMU** | 6-Axis Accelerometer / Gyroscope | ST `LSM6DS3TR-C` or `LIS3DH` | $0.85 |
| **Navigation** | Multi-Constellation GNSS Receiver | u-blox `SAM-M8Q` (Patch Ant) | $12.00 |
| **Display Panel** | 10.3" E-Ink (Carta 1200 / Kaleido 3) + Touch + EMR | Good-Display / Waveshare | $110.00 – $135.00 |
| **EPDC Controller**| IT8951 Controller Board & Flat Cable | Waveshare / ITE | $18.00 |
| **Stylus** | Wacom EMR Passive Stylus with Eraser | Staedtler Noris Digital | $25.00 |
| **Off-Grid Radio** | Semtech SX1262 915 MHz LoRa Module (+22dBm) | Ebyte `E22-900M22S` | $5.50 |
| **Battery** | 6,400 mAh 3.2V Prismatic LiFePO4 Pack | Batteryhookup / Custom | $12.00 |
| **Power PMIC** | Synchronous MPPT I2C Buck Charger | Texas Instruments `BQ25895RTWR` | $3.50 |
| **Audio** | Dual AAC Micro-Box Speakers + TI TAS2563 Amp | PUI Audio / TI `TAS2563` | $7.30 |
| **Mics & Switch** | Dual I2S MEMS Mics + Hardware Mute Switch | Knowles `SPH0645` + C&K Slide | $3.00 |
| **Connectors** | Qwiic JST-SH + 2x IP68 USB-C + 8-Pin Rear Pogo | LCSC / Amphenol | $6.50 |
| **Carrier PCBA** | 4-Layer ENIG Motherboard + SMT Assembly | JLCPCB Turnkey | ~$25.00 |
| **Chassis** | SLS 3D-Printed PA12 Nylon + TPU Bumpers | JLC3D / Craftcloud | $25.00 |
| **TOTAL CORE MVP**| *(Everything to build the fully functional tablet)* | | **~$312 – $337** *(Qty 1)*<br>**~$230 – $260** *(Batch Qty 5)* |

### Modular Add-On Packs (Optional / Phase 2):

| Add-On Pack | Components Included | Est. Module Cost |
| :--- | :--- | :--- |
| **RF Multi-Tool Pod** | ESP32-S3 + CC1101 Sub-GHz + PN532 NFC + EM4095 RFID + IR TX/RX + LiPo | ~$28.00 |
| **Cellular M.2 Pod** | Quectel EC25-AFX Cat-4 LTE + Nano-SIM Tray + FPC Antennas | ~$38.00 |
| **Satellite SOS Pod** | RockBLOCK 9603 (Iridium) or Swarm M138 IoT Transceiver | ~$115.00 – $260.00 |
| **Industrial / CAN Pod**| Microchip MCP2515 CAN controller + M8 Gigabit Ethernet receptacle | ~$18.00 |
