# SolarDeck Hardware Specification

Detailed hardware architecture, component selection, bus topology, and electrical requirements for the custom carrier board and mechanical enclosure.

---

## 1. System Block Diagram

```
                                  [ 10.3" E-INK PANEL (KALEIDO 3 / CARTA 1200) ]
                                  [ + CAPACITIVE TOUCH + WACOM EMR DIGITIZER    ]
                                                        ▲
                                                        │ (MIPI DSI / Parallel EPDC)
                                                        │
┌───────────────────────────┐         SPI / USB         │
│  TI BQ25895 MPPT CHARGER  ├───────────────────────────┼───────────────────────────┐
│  • Micro-Solar Bezel      │                           │                           │
│  • USB-C PD 20W Charge    │             ┌─────────────┴─────────────┐             │
│  • LiFePO4 Battery Pack   │             │   RASPBERRY PI CM4 BOARD  │             │
└─────────────┬─────────────┘             │  • 4x Cortex-A72 @ 1.8GHz │             │
              │ 3.8V Rail                 │  • 4GB/8GB LPDDR4         │             │
              ▼                           │  • Linux OS / Claude Code │             │
┌───────────────────────────┐   I2C/GPIO  └─────────────┬─────────────┘             │
│   RP2040 CO-PROCESSOR     ├───────────────────────────┤                           │
│  • 12MHz Ultra-Low Power  │  (Wake Interrrupts)       │ PCIe / USB                │
│  • DS3231 Precision RTC   │                           │                           │
│  • 1-Sec Partial Clock    │             ┌─────────────▼─────────────┐             │
│  • Solar Bezel ADC & Touch│             │  PERIPHERALS & NETWORKING │             │
└───────────────────────────┘             │  • Quectel EC25-AFX 4G    │             │
                                          │  • SX1262 LoRa 915MHz     │             │
                                          │  • Flipper Zero Multi-Tool│             │
                                          │  • Dual I2S MEMS Mic Array│             │
                                          └─────────────┬─────────────┘             │
                                                        │                           │
                                                        ▼ (5-Pin Pogo Bus)          │
                                          ┌───────────────────────────┐             │
                                          │ DETACHABLE KEYBOARD DOCK  │             │
                                          │ • Molded Silicone Scissor │             │
                                          │ • Blackberry Trackpad     │             │
                                          │ • Nordic nRF52840 BLE     │             │
                                          └───────────────────────────┘             │
```

---

## 2. Component Selection & Electrical Interfaces

### 2.1 Compute & Low-Power Co-Processing
* **Main Compute Module:** Raspberry Pi Compute Module 4 (CM4104032 — Wi-Fi, 4GB RAM, 32GB eMMC).
  * Pin-to-pin compatible with Raspberry Pi CM5 for future upgrades.
  * Connects via dual Hirose DF40 high-density 100-pin board-to-board connectors.
* **Low-Power Co-Processor:** Raspberry Pi **RP2040** (Dual Cortex-M0+).
  * Clock: Dynamically throttled down to **12 MHz** in ambient mode for 2.0 mW power draw.
  * Connected to main CM4 via **I2C bus (Address `0x42`)** and dedicated **Hardware Wake Interrupt line (GPIO 17)**.
* **Real-Time Clock (RTC):** Maxim **DS3231** temperature-compensated crystal oscillator (TCXO).
  * Drift: < 2 minutes per year. Powered by a coin cell (CR1220) or supercapacitor.

### 2.2 Display & Digitizer Assembly
* **Display Panel:** 10.3-inch E-Ink **Kaleido 3** (Color) or **Carta 1200** (Monochrome).
  * Resolution: 1872 × 1404 pixels (300 PPI black/white, 150 PPI color).
  * Active Area: 209.66 mm × 157.25 mm.
  * Contrast Ratio: 15:1.
* **EPDC (Electronic Paper Display Controller):** ITE **IT8951** or integrated Rockchip RK3566 EPDC.
  * Direct 1-bit / 8-bit waveform LUT support.
  * USB 2.0 / I80 16-bit parallel / MIPI interface to CM4.
* **Stylus Digitizer:** Genuine **Wacom EMR (Electro-Magnetic Resonance)** sensor board laminated behind the e-paper.
  * Resolution: 0.005 mm; Pressure: 4,096 levels.
  * Pen: Battery-free (Lamy AL-star EMR, Staedtler Noris Digital, or reMarkable Marker).
  * Interface: I2C HID controller (`wacom_w9013` driver).
* **Touch Panel:** Capacitive multi-touch glass overlay with anti-glare, anti-fingerprint etched matte finish.

### 2.3 Power Subsystem & Ambient Solar
* **Battery Chemistry:** **LiFePO4 (Lithium Iron Phosphate)** 3.2V nominal, 3.65V peak.
  * Capacity: 10,000 mAh (32 Watt-hours) 1S2P prismatic pack (safe to 65°C / 149°F, airline-compliant <100Wh).
  * Safe Operating Temperature: **-10°C to +65°C (14°F to 149°F)** with zero risk of thermal runaway.
  * Cycle Life: 3,000 to 5,000 full discharge cycles to 80% health.
* **Solar Charge Controller:** Texas Instruments **BQ25895** or **BQ24650** Synchronous MPPT Buck Charger.
  * Dynamic Power Management (DPM).
  * High-efficiency synchronous rectification (>92%).
  * NTC thermistor input glued directly to the LiFePO4 cells for automatic thermal cutoff.
* **Front-Bezel Micro-Solar Strip:**
  * Dimensions: 15 mm × 90 mm (placed on top bezel).
  * Cell Type: SunPower Maxeon Monocrystalline (22.8% efficiency).
  * Yield: 15 mW (indoor ambient light) to 120 mW (window daylight).
* **Power Gating (Physical Cutoff Switches):**
  * Texas Instruments **TPS22918** ultra-low leakage load switches on the power rails feeding the 4G modem, Wi-Fi, and Flipper Zero sub-modules. When sleeping, leakage current is **0.000 mA**.

### 2.4 Wireless & Radio Multi-Tool Engine
* **Cellular Modem:** **M.2 Key-B (3042)** socket connected to internal USB lines.
  * Card: **Quectel EC25-AFX** (Cat 4 LTE) or **EM06-A** (Cat 6 LTE).
  * Bands: B2, B4, B5, B12, B13, B14, B66, B71 (North America / Hawaii AT&T, T-Mobile, Verizon certified).
  * SIM: Push-push Nano-SIM tray on the chassis edge.
* **LoRa Mesh Radio:** **Semtech SX1262** 915 MHz transceiver (up to +22 dBm output).
  * Connects via SPI to CM4; compatible with **Meshtastic** firmware.
* **Sub-GHz Radio:** Texas Instruments **CC1101** transceiver (300–348 MHz, 387–464 MHz, 779–928 MHz).
  * Replays/decodes 315/433 MHz remotes, gates, sensors, weather stations.
* **Infrared Engine:**
  * Receiver: Vishay **TSOP4838** 38 kHz demodulator.
  * Transmitter: Dual high-power Vishay **TSAL6200** 940 nm LEDs driven by 2N7002 MOSFET for 15-meter range.
* **NFC & RFID:**
  * 13.56 MHz NFC: NXP **PN532** (SPI/I2C) with PCB loop antenna.
  * 125 kHz RFID: **EM4095** demodulator with ferrite resonant coil antenna.

### 2.5 Audio & Voice Subsystem
* **Microphone Array:** Dual Knowles or InvenSense **SPH0645LM4H-B** I2S digital MEMS microphones.
  * Dynamic range: 65 dB SNR.
  * Placement: Left and right upper bezel for stereo acoustic beamforming.
* **Physical Privacy Switch:** Hardware 2-pole slide switch that physically cuts the VDD line to both microphones (hardware-guaranteed un-hackable mute).
* **Audio Output:** Texas Instruments **MAX98357A** I2S mono Class-D amplifier driving an internal 1W sealed acoustic chamber speaker.

---

## 3. The Detachable Keyboard & Magnetic Dock

### 3.1 Pogo-Pin Interface
* **Connector:** 5-pin hermetic magnetic spring-loaded gold Pogo connector (2.54 mm pitch).
* **Pinout:**
  1. `VBUS` (+5.0V Power from tablet to keyboard)
  2. `USB_D-` (USB 2.0 Differential Data Negative)
  3. `USB_D+` (USB 2.0 Differential Data Positive)
  4. `GND` (Ground)
  5. `ID_SENSE` (Grounded inside keyboard for hardware insertion detection)

### 3.2 Keyboard Mechanics & Fallback Wireless
* **Key Switches:** Scissor-switch chiclet keyboard with a continuous silicone rubber membrane underneath (spill-proof, IP67).
* **Navigation:** Built-in **Blackberry Trackpad (RIM 9900 optical sensor)** or mini center trackpoint below the spacebar.
* **Microcontroller:** Nordic **nRF52840** (runs ZMK / QMK open-source keyboard firmware).
  * Automatically switches to ultra-low latency **Bluetooth LE 5.0** when detached from the magnetic pins.
  * Internal 600 mAh LiPo pouch cell provides 3 months of wireless typing.

---

## 4. Mechanical Enclosure & Ingress Protection (IP67)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 3M 5952 VHB Waterproof Acrylic Foam Tape around Glass   │
├─────────────────────────────────────────────────────────────┤
│ 2. CNC 6061-T6 Anodized Aluminum Uni-Body (Heatsink)       │
├─────────────────────────────────────────────────────────────┤
│ 3. Continuous Tongue-and-Groove Hollow Silicone O-Ring     │
├─────────────────────────────────────────────────────────────┤
│ 4. GORE Protective ePTFE Pressure Equalization Vent        │
├─────────────────────────────────────────────────────────────┤
│ 5. Overmolded 85A TPU Shock-Absorbing Armor Corners        │
└─────────────────────────────────────────────────────────────┘
```

1. **Waterproofing Seams:** Continuous perimeter channel with 1.5 mm hollow-core silicone gasket, compressed 30% by 12 stainless steel M2.5 Torx screws.
2. **Glass Bonding:** Front glass is recessed 1 mm below an aluminum lip and bonded from behind with 3M 5952 VHB tape.
3. **Pressure Equalization:** A **Gore-Tex ePTFE vent plug** on the bottom plate allows internal air pressure to equalize during temperature swings (preventing vacuum moisture suction) while blocking 100% of liquid water and humidity.
4. **Drop Armor:** 85A durometer TPU rubber bumpers permanently molded around all four corners to absorb 4-foot drops onto concrete or rock.
