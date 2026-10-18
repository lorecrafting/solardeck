# SolarDeck Bill of Materials (BOM) & Manufacturing Cost Estimate

Written 2026-10-18 02:58 UTC in the Pi harness by antigravity/gemini-3.8-flash

Comprehensive bill of materials, component part numbers, verified suppliers, and turnkey manufacturing cost projections for the core tablet, the parallel SnapDeck keyboard, and the modular RF backpack.

---

## 1. Core SolarDeck Tablet BOM

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- | :--- |
| **Compute** | Raspberry Pi Compute Module 4 (8GB RAM, 32GB eMMC, Wi-Fi) | DigiKey / Newark / PiShop | CM4108032 (or 4GB CM4104032 @ $55) | $75.00 |
| **Co-Processor** | Dual Cortex-M33 / RISC-V Microcontroller (Power Master) | DigiKey / Mouser / LCSC | Raspberry Pi RP2350B | $1.25 |
| **Co-Proc PSRAM** | 8MB Ultra-Low-Power QSPI PSRAM (Page Double-Buffer) | Mouser / LCSC | APMemory APS6404L-3SQR-SN | $0.75 |
| **Bus Multiplexer**| High-Speed 8-Channel SPDT Display Bus Isolator / Switch | Texas Instruments / Mouser | TMUX1575PWR | $0.55 |
| **RTC** | High-Precision TCXO Real-Time Clock | Mouser / LCSC | DS3231SN# | $2.50 |
| **Display Panel** | 10.3" E-Ink Kaleido 3 (Color) + Capacitive Touch + Wacom EMR Layer | Waveshare / Good-Display / AliExpress | ED103TC2 / GDEW103W32 | $95.00 – $120.00 |
| **EMR Shielding** | 0.1mm High-Permeability Mu-Metal / Ferrite Flux Absorber Sheet | 3M / Wurth / AliExpress | Custom Die-Cut Shield Foil | $1.80 |
| **Controller** | Electronic Paper Display Controller (EPDC) | Waveshare / ITE | IT8951 Board / IC | $18.00 |
| **Stylus** | Wacom EMR Passive Stylus with Eraser | Amazon / B&H | Staedtler Noris Digital or Lamy AL-star | $28.00 |
| **Battery** | 8,000–10,000 mAh 3.7V Li-ion or 3.2V LiFePO4 Prismatic Pack | Batteryhookup / AliExpress | Custom 1S / 1S2P Slim Pack | $16.00 |
| **Power IC** | Synchronous Buck Battery Charger IC (USB-PD 20W) | Texas Instruments / Mouser | BQ25895RTWR | $3.50 |
| **5V Boost Conv**| 3.5A Synchronous Boost Converter (Main CM4/USB Supply) | Texas Instruments / Mouser | TPS61088RHLR | $1.20 |
| **Modem Supply** | 3.8V 2.5A Synchronous Buck-Boost (Anti-Brownout Buffer) | Texas Instruments / Mouser | TPS63020DSJR | $1.10 |
| **Micro-Solar** | Top-Bezel Monocrystalline Trickle Strip (1.0W Peak) | IXYS / DigiKey / Mouser | SM141K06L / PowerFilm | $3.50 |
| **Power Gates** | Ultra-Low Leakage Load Switches (x7) | Texas Instruments / LCSC | TPS22918DBVR (x7) | $1.90 |
| **Cellular Modem**| Worldwide M.2 Key-B 4G/LTE Cat-4 Modem (30+ Bands) | DigiKey / AliExpress | Quectel EG25-G | $29.00 |
| **Onboard eSIM** | Industrial MFF2 (DFN-8, 5x6mm) eUICC Chip | STMicroelectronics / Infineon | ST4SIM-200M / SLM97 | $1.50 |
| **LoRa Mesh** | 915/868 MHz LoRa Transceiver Module (+22dBm) | Mouser / LCSC | Semtech SX1262 (Ebyte E22-900M22S) | $5.50 |
| **GNSS Engine** | Worldwide Multi-Constellation Satellite Receiver | Mouser / DigiKey | u-blox MAX-M10S | $9.00 |
| **LoRa Antenna Mount**| IP67 Bulkhead SMA Female Jack with O-Ring Gasket | LCSC / Amphenol | SMA-KFD08-IP67 | $1.80 |
| **LoRa Antenna** | Tactical 1/2-Wave 915MHz Dipole Whip (Center-Fed, 3.2dBi) | Linx Technologies / Mouser | ANT-916-CW-HWR-SMA | $8.50 |
| **LTE MIMO Antennas**| Ultra-Wideband (698–3000 MHz) Flexible PCB Antennas (x2) | Taoglas / DigiKey | FXUB63.07.0150C (Main + Div) | $8.40 |
| **Wi-Fi/BT Antenna**| Dual-Band (2.4/5GHz) Balanced Dipole FPC with U.FL | Molex / Mouser | 1461530100 | $1.20 |
| **GNSS Antenna** | 15×15mm Ceramic Active GPS/BeiDou Patch Antenna | Taoglas / LCSC | AP.15E | $2.50 |
| **Rear Camera** | 12MP Sony IMX708 with Motorized PDAF Macro Autofocus | Raspberry Pi / DigiKey | Official Cam Module 3 sensor | $12.50 |
| **Front Camera**| 5MP Sony IMX219 / OV5647 1080p Fixed-Focus Camera | Raspberry Pi / LCSC | Official Cam Module 2 sensor | $4.80 |
| **Privacy Shutter**| Mechanical "ThinkShutter" Bezel Sliding Door | Custom / JLC3D | Molded Delrin Slider | $0.80 |
| **Audio** | Single I2S MEMS Mic + I2S 3.2W Class-D Amp + Sealed Speaker | Knowles / Maxim / PUI Audio | SPH0645LM4H + MAX98357A + AS03008MR | $4.00 |
| **Docking Bus** | 5-Pin Hermetic Magnetic Gold Pogo Connector (Front Bezel) | LCSC / AliExpress | Magsafe-style Pogo 2.54mm | $2.50 |
| **Expansion Bus**| 8-Pin Hermetic Magnetic Pogo Connector (Rear Backpack) | LCSC / AliExpress | 8-Pin Spring Pogo Bus | $3.00 |
| **Passives/Ports**| 2x IP68 USB-C Ports, Qwiic Jack, 1,000µF Poly Caps, SMD Passives | LCSC / JLCPCB SMT Library | Standard SMD 0402/0603 | $9.80 |
| **USB-C CC Ctrl** | Type-C Configuration Channel Dual-Role DRP Controller | Texas Instruments / Mouser | TUSB320RWBR | $0.65 |
| **I/O Isolators** | Fail-Safe Cross-Domain Buffers with I_off Partial-Power-Down | Texas Instruments / Mouser | TXU0104PWR (x2) | $0.50 |
| **Motion Sensor** | Ultra-Low-Power 3-Axis Accelerometer (3.5µA Pick-up Wake) | Bosch Sensortec / Mouser | BMA400 | $1.10 |
| **Compass** | High-Precision 3-Axis Digital Magnetometer | Memsic / LCSC | MMC5603NJ | $0.80 |
| **Barometer** | Precision Atmospheric Pressure & Altimeter Sensor | Bosch Sensortec / Mouser | BMP390 | $1.20 |
| **Power Telemetry**| 3-Channel High-Side Current & Power Monitor IC | Texas Instruments / Mouser | INA3221AIRGVR | $1.20 |
| **Coulomb Counter**| Impedance Track™ Battery Fuel Gauge & Health IC | Texas Instruments / Mouser | BQ27441-G1A | $1.10 |
| **Thermal Triad** | Dual Precision Digital Temperature Sensors (Batt + E-Ink) | Texas Instruments / LCSC | TMP112AIDRLR (x2) | $0.60 |
| **Ambient Lux** | Precision Ambient Light & Solar Lux Sensor | Texas Instruments / Mouser | OPT3001DNPR | $0.55 |
| **Piezo Buzzer** | SMT 5.0mm Micro-Acoustic Buzzer (Standby Mesh Chime) | Murata / PUI Audio / LCSC | PKLCS0909E4000-R1 | $0.25 |
| **RGB Beacon** | Common-Anode RGB SMD LED + Frosted Glass Light Pipe | Kingbright / Cree / LCSC | KPF-3224SEBMAPGAC | $0.45 |
| **VBUS OR-ing** | Dual Low-Ron Ideal Diode Power OR-ing Controller (x2) | Texas Instruments / Mouser | LM66100DCKR (x2) | $0.70 |
| **Host VBUS Sw** | 1.5A Current-Limited USB Host Distribution Power Switch | Texas Instruments / Mouser | TPS2051BDBVR | $0.45 |
| **Recovery Sw** | Sub-Miniature IP67 Pinhole Micro-Tactile Switches (x2) | C&K / Panasonic / LCSC | KMR2 / EVQ-P8 | $0.40 |
| **Airgap Switch** | Sub-Miniature 2-Position Gold Contact Slide Switch | C&K / E-Switch / LCSC | JS202011CQN | $0.45 |
| **GORE Vent** | ePTFE Pressure Equalization Vent Plug | W. L. Gore / Amphenol | PMF100396 | $1.50 |
| **Enclosure (PA12)**| SLS 3D-Printed PA12 Nylon Shell + 85A TPU Corner Bumpers | JLC3D / Craftcloud | Custom CAD Housing | $28.00 |
| **Total Core BOM**| | | | **~$365 – $398** |

---

## 2. SnapDeck Detachable Keyboard BOM (Parallel Build)

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Controller** | Multiprotocol Bluetooth 5.0 + USB SoC | Nordic Semiconductor / Mouser | nRF52840-QIAA | $3.20 |
| **Firmware** | Open-Source ZMK Keyboard Firmware | GitHub (ZMK) | Pre-configured Hex | $0.00 |
| **Key Switches** | Kailh X-Switch Ultra-Slim Mechanical Scissor (64 keys) | Kailh / AliExpress | CPG131601D01 | $12.00 |
| **Keycaps** | Low-Profile Chiclet Keycaps Set (PBT/ABS) | Kailh / YMDK | Ultra-thin 60% set | $6.00 |
| **Trackpad** | Blackberry RIM 9900 Optical Trackpad Sensor Module | AliExpress / LCSC | RIM 9900 OFN Sensor | $4.50 |
| **Battery** | 300 mAh 3.7V Ultra-Thin LiPo Pouch Cell | AliExpress / PKCELL | LP302030 | $2.50 |
| **Docking Bus** | 5-Pin Magnetic Pogo Mating Header + N52 Magnets | LCSC / AliExpress | 5-Pin Female Pogo Strip | $3.00 |
| **PCB & Assembly**| Ultra-Thin 0.8mm 2-Layer Keyboard Matrix PCB + SMT | JLCPCB | Turnkey Assembly | $8.00 |
| **Enclosure** | SLS PA12 Nylon Keyboard Backplate & Shell | JLC3D | Custom CAD Shell | $6.50 |
| **Total SnapDeck**| | | | **~$45.70** |

---

## 3. Modular Tactical RF & SIGINT Backpack BOM (Optional Add-on)

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Sub-GHz Radio** | CC1101 300–928MHz Transceiver + Tuned Whip Antenna | Texas Instruments / LCSC | CC1101 Module | $3.50 |
| **NFC Transceiver**| NXP PN532 13.56MHz NFC Controller + PCB Trace Loop | NXP / LCSC | PN5321A3HN | $3.20 |
| **RFID Demod** | EM4095 125kHz Low-Frequency RFID Front-End + Coil | EM Micro / LCSC | EM4095HMS | $2.50 |
| **IR Blaster/RX** | Vishay 38kHz IR Demodulator + Dual High-Power 940nm LEDs | Vishay / LCSC | TSOP4838 + TSAL6200 | $1.20 |
| **Sky-Scan SDR** | RTL2832U + R860 Wideband VHF/UHF SDR Tuner ICs (24–1766 MHz) | Realtek / Rafael Micro / LCSC | RTL2832U + R860 | $9.50 |
| **SDR SMA Mount**| Dedicated IP67 Bulkhead SMA for VHF/UHF Telescopic Antenna | LCSC / Amphenol | SMA-KFD08-IP67 | $1.80 |
| **VHF/UHF Antenna**| Telescopic 20–1300 MHz Retractable Field Antenna | AliExpress / Amazon | Nagoya NA-771 / Telescopic | $4.50 |
| **Connector** | 8-Pin Magnetic Spring-Loaded Pogo Interface + Magnets | LCSC / AliExpress | 8-Pin Mating Header | $3.00 |
| **Enclosure** | Slim SLS PA12 Snap-on Rear Module Shell | JLC3D | Custom CAD Pod | $4.50 |
| **Total Modular Pod**| Complete Multi-Tool + Sky-Scanning SIGINT Backpack | | | **~$33.70** |

---

## 4. Turnkey PCBA Fabrication & Box-Build

Because standard surface-mount components from JLCPCB's / PCBWay's Basic and Extended Parts Library are used, fabrication can be 100% automated:

* **Motherboard PCB:** 4-Layer FR-4, ENIG surface finish, 50Ω controlled impedance traces on RF lines.
* **SMT Turnkey Assembly:** Automated pick-and-place of all passives, ICs, M.2 socket, and Hirose connectors.
* **Turnkey Batch Prototype Costs (5 Units at JLCPCB/PCBWay):**
  * Bare PCBA fabrication (5 boards): $24.00
  * SMT Stencils & Machine Setup: $30.00
  * Motherboard components & assembly: ~$115.00 per board
  * Per-finished-tablet turnkey assembly (excluding CM4/Display): ~$145.00 each.

---

## 5. Value Comparison (SolarDeck vs Commercial Field Tablets)

```
┌─────────────────────────────────────────────────────────────┐
│  SOLARDECK CORE TABLET (8GB + DUAL CAM)    │ ~$365 – $398   │
│  (Or 4GB CM4 Base Config)                  │ ~$345 – $378   │
├─────────────────────────────────────────────────────────────┤
│  SNAPDECK PARALLEL KEYBOARD ADD-ON         │ ~$45.70        │
├─────────────────────────────────────────────────────────────┤
│  reMarkable 2 (Monochrome, No Backlight)   │ $399 – $449    │
│  Kindle Scribe 10.2" (Closed DRM Amazon)   │ $369 – $419    │
│  Onyx Boox Note Air 3C (Color, Android)    │ $499 – $549    │
│  Panasonic Toughbook Rugged Slate          │ $1,800 – $2,500│
└─────────────────────────────────────────────────────────────┘
```
