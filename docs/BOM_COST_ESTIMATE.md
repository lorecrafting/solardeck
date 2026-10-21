# SolarDeck Bill of Materials (BOM) & Manufacturing Cost Estimate

Written 2026-10-18 17:31 UTC in the Pi harness by antigravity/gemini-3.8-flash

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:52 UTC in Claude Code by anthropic/claude-opus-5-5 (owner decisions, ADR-046).

Comprehensive bill of materials, component part numbers, verified suppliers, and turnkey manufacturing cost projections for the core tablet and the modular RF backpack. The SnapDeck keyboard is an optional Phase 2 accessory (§2), not part of the V1 BOM.

---

## 1. Core SolarDeck Tablet BOM

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- | :--- |
| **Compute** | Raspberry Pi Compute Module 5 (16GB RAM, 64GB eMMC, Wi-Fi/BT) — ADR-031 | Raspberry Pi approved resellers | CM5116064 (SC1608) | $375.00 |
| **Co-Processor** | Dual Cortex-M33 / RISC-V Microcontroller (Power Master) | DigiKey / Mouser / LCSC | Raspberry Pi RP2350B | $1.25 |
| **Co-Proc PSRAM** | 8MB Ultra-Low-Power QSPI PSRAM (Page Double-Buffer) | Mouser / LCSC | APMemory APS6404L-3SQR-SN | $0.75 |
| **Co-Proc Flash** | 16 MB QSPI NOR flash: RP2350B firmware (two slots) + reader content; the RP2350B has no internal flash (ADR-046) | Winbond / LCSC | W25Q128JV class | TBD |
| **Bus Multiplexer**| Display Bus Isolator, 2 × 4-channel SPDT switch (ADR-004) | Texas Instruments / Mouser | TMUX1575YCJR (x2) | $0.55 |
| **Display Panel** | 10.3" E Ink Kaleido 4 (colour) + Capacitive Touch + Wacom EMR — ADR-032 | E Ink (sole source) | Kaleido 4 10.3" (P/N on release) | TBD |
| **EMR Shielding** | 0.1mm High-Permeability Mu-Metal / Ferrite Flux Absorber Sheet | 3M / Wurth / AliExpress | Custom Die-Cut Shield Foil | $1.80 |
| **Controller** | Kaleido 4 display controller / TCON (the IT8951 cannot drive Kaleido 4 — ADR-025, ADR-032) | TBD with E Ink | TBD | TBD |
| **Stylus** | Wacom EMR Passive Stylus with Eraser | Amazon / B&H | Staedtler Noris Digital or Lamy AL-star | $28.00 |
| **Battery** | LiFePO4 1S pouch cell, chosen from a buyable datasheet (ADR-040) | TBD | TBD | TBD |
| **Power IC** | LiFePO4-capable buck-boost charger, VREG 3.0–18.8 V, OTG capped at 2 A (ADR-035) | Texas Instruments / Mouser | BQ25798 | TBD |
| **USB-PD Sink Ctrl**| Standalone USB-PD 20W Fast Charge Sink Controller (9V/12V Contract)| WCH / STMicroelectronics / LCSC | CH224K / STUSB4500 | $0.45 |
| **AON 3.3V Supply**| 60 nA IQ Synchronous Buck-Boost Converter (Perpetual 3.3V Rail) | Texas Instruments / Mouser | TPS62840DLYR | $0.85 |
| **5V Boost Conv**| 3.5A Synchronous Boost Converter (Main CM5/USB Supply) | Texas Instruments / Mouser | TPS61088RHLR | $1.20 |
| **Micro-Solar** | Top-Bezel Monocrystalline Trickle Strip (~0.15W Peak, 50-120mW Real)| IXYS / DigiKey / Mouser | SM141K06L / PowerFilm | $3.50 |
| **Power Gates** | Ultra-Low Leakage Load Switches (Airgap Cut + Port 2 VBUS) | Texas Instruments / LCSC | TPS22918DBVR (x2) | $0.80 |
| **GNSS Receiver**| Standalone multi-constellation GNSS, integrated LNA, on the RP2350 UART (ADR-038) | u-blox / Mouser | MAX-M10S | TBD |
| **Wi-Fi/BT Antenna**| Dual-Band (2.4/5GHz) Balanced Dipole FPC with U.FL | Molex / Mouser | 1461530100 | $1.20 |
| **GNSS Antenna** | Passive Internal FPC GPS/GLONASS Antenna (for MAX-M10S; integrated LNA) | Molex / Taoglas / LCSC | 1461860100 | $0.90 |
| **Audio** | Dual-MEMS Acoustic Array (2x SPH0645) + I2S Class-D Amp + Speaker| Knowles / Maxim Integrated / PUI Audio | SPH0645LM4H (x2) + MAX98357A + AS03008MR | $5.10 |
| **Mechanical Mount**| Universal M2.5 Brass Heat-Set Inserts (x4) + MagSafe Magnetic Array | McMaster / LCSC / Custom | M2.5 Inserts + N52 Ring | $0.90 |
| **Passives/Ports**| 2x IP68 USB-C Ports, 1,000µF Poly Caps, SMD Passives | LCSC / JLCPCB SMT Library | Standard SMD 0402/0603 | $9.40 |
| **USB-C CC Ctrl** | Type-C Configuration Channel Dual-Role DRP Controller | Texas Instruments / Mouser | TUSB320RWBR | $0.65 |
| **I/O Isolators** | Fail-Safe Cross-Domain Buffers with I_off Partial-Power-Down | Texas Instruments / Mouser | TXU0104PWR (x2) | $0.50 |
| **Motion Sensor** | Ultra-Low-Power 3-Axis Accelerometer (3.5µA Pick-up Wake) | Bosch Sensortec / Mouser | BMA400 | $1.10 |
| **Barometer** | Precision Atmospheric Pressure & Altimeter Sensor | Bosch Sensortec / Mouser | BMP390 | $1.20 |
| **5-Way Rocker** | IP67 Sealed Micro Navigation Joystick (Up/Down/Left/Right/Press)| ALPS / Panasonic / Mouser | SKRHABE010 | $0.85 |
| **Power Telemetry**| 3-Channel High-Side Current & Power Monitor IC (Rail Logging)| Texas Instruments / Mouser | INA3221AIRGVR | $1.20 |
| **GPIO Expander** | 16-bit low-quiescent I²C GPIO expander with interrupt, on the always-on bus (ADR-045, docs/PIN_BUDGET.md §4) | TBD | TBD | TBD |
| **Coulomb Counter**| LiFePO4-capable Impedance Track fuel gauge, characterised on the chosen cell (ADR-035) | Texas Instruments / Mouser | BQ27Z561-R2 | TBD |
| **Thermal Triad** | Dual Precision Digital Temperature Sensors (Batt + E-Ink Logs)| Texas Instruments / LCSC | TMP112AIDRLR (x2) | $0.60 |
| **Ambient Lux Sensing**| Integrated via Solar Strip & RP2350 12-Bit ADC (Zero-BOM Innovation)| IXYS / RP2350 Subsystem | ADC Channel 3 ($0 Added Silicon) | $0.00 |
| **VBUS OR-ing** | Dual Low-Ron Ideal Diode Power OR-ing Controller (x2) | Texas Instruments / Mouser | LM66100DCKR (x2) | $0.70 |
| **Host VBUS Sw** | 1.5A Current-Limited USB Host Distribution Power Switch | Texas Instruments / Mouser | TPS2051BDBVR | $0.45 |
| **Recovery Sw** | Single Sub-Miniature IP67 Pinhole Micro-Tactile Switch | C&K / Panasonic / LCSC | KMR2 / EVQ-P8 | $0.20 |
| **Voice Button** | Hold-to-talk tactile switch: wakes the RP2350, which starts audio capture while the CM5 boots (ADR-036) | C&K / Panasonic / LCSC | KMR2 / EVQ-P8 | $0.20 |
| **Bezel Solar MPPT**| Nano-Power Solar Boost Harvester IC (Cold-Start 330mV, 80% FOCV)| Texas Instruments / Mouser | BQ25504RGTR | $1.80 |
| **Frontlight Driver**| Dual-Channel Constant-Current Step-Up LED Driver (2048-step CCT)| Texas Instruments / Mouser | TPS61163YFFR | $0.65 |
| **Battery PCM** | LiFePO4 protector (3.85 V OVP / 2.50 V UVP class) + back-to-back N-FET pair (ADR-035) | Texas Instruments / Mouser | BQ29706 + dual N-FET (TBD) | TBD |
| **ESD Suppression** | Low-Capacitance TVS Diode Arrays for USB & Pogo Pins (x4) | Texas Instruments / Mouser | TPD4E05U06 (x4) + SMAJ5.0A | $0.80 |
| **RTC** | Always-on I²C real-time clock with its own crystal and backup switchover, on the RP2350 bus — no GPIO (ADR-046) | Micro Crystal / Mouser | RV-3028-C7 class | TBD |
| **RTC Backup Battery**| 3.3V Rechargeable Lithium Micro-Battery (5.5 mAh, >100 days hold)| Seiko Instruments / Mouser | MS621FE-FL11E | $0.65 |
| **JEITA Resistors** | 0.1% Precision Resistors for the BQ25798 TS NTC network (values per BQ25798 datasheet) | Yageo / Panasonic 0603 | Precision Thin-Film (x2)| $0.15 |
| **CM5 Retention** | CNC Aluminum CM5 Retention Bracket & Thermal Interface Pad | Custom CNC / Laird | Custom Bracket + Tflex | $1.80 |
| **RF Pi-Matching** | Precision 0402 RF Inductors & C0G/NP0 Capacitors (5 nets) | Murata / TDK / LCSC | 0402 Precision RF Kit | $0.40 |
| **Solar Aerogel** | 0.5mm Die-Cut Pyrogel Aerogel / Kapton Thermal Barrier | Aspen Aerogels / 3M | Pyrogel Insulation Strip | $0.60 |
| **Privacy Switch** | Sealed (IP67-rated) sub-miniature 3-position slide switch, multi-pole: normal / mic mute / full blackout (HARDWARE_SPEC §2.25, ADR-046) | C&K / E-Switch | TBD (3-position) | TBD |
| **GORE Vent** | ePTFE Pressure Equalization Vent Plug | W. L. Gore / Amphenol | PMF100396 | $1.50 |
| **Haptic Engine** | Wideband Haptic Driver + frame-mounted Z-Axis LRA, core part (ADR-037; piezo array = DNP) | Texas Instruments / Vybronics | DRV2605L + 8mm Z-Axis LRA | $2.35 |
| **Perimeter Gasket** | Die-Cut VMQ Silicone O-Ring, 27% Compression (Service Item) | Custom / Rogers | Custom Die-Cut VMQ | $2.10 |
| **Enclosure (PA12)**| SLS 3D-Printed PA12 Nylon Shell + 85A TPU Corner Bumpers | JLC3D / Craftcloud | Custom CAD Housing (Streamlined)| $25.00 |
| **Conformal Coat** | IPC-CC-830 Reworkable Acrylic Conformal Coating, Connector-Masked (spec_values.longevity.conformal_coat) | PSI / Applied Post-SMT | IPC-CC-830 (UC-2605) | $2.00 – $4.00 |
| **Total Core BOM**| **(Sum of 52 V1 Line Items, excluding 11 TBD parts: Kaleido 4 panel, its controller, cell, charger, gauge, protector, GNSS, GPIO expander, RTC, co-processor flash, privacy switch — a floor, not a price; see docs/AUDIT_6_2026-10-21.md H22)** | | | **$479.10 – $481.10 + TBD** |

### Deferred to V2 (ADR-034, LoRa ADR-044) — not summed

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- | :--- |
| **Modem Supply** | 3.8V 2.5A Synchronous Buck-Boost (Anti-Brownout Buffer) | Texas Instruments / Mouser | TPS63020DSJR | $1.10 |
| **Cellular Modem**| Worldwide M.2 Key-B 4G/LTE Cat-4 Modem with Nano-SIM Tray | DigiKey / AliExpress | Quectel EG25-G | $29.00 |
| **MFF2 eSIM Chip** | Consumer eUICC (GSMA SGP.22) Micro-eSIM, MFF2 DFN-8 — ADR-033 | TBD | TBD (ST4SIM-200M rejected: M2M SGP.02) | TBD |
| **LTE MIMO Antennas**| Ultra-Wideband (698–3000 MHz) Flexible PCB Antennas (x2) | Taoglas / DigiKey | FXUB63.07.0150C (Main + Div) | $8.40 |
| **Rear Camera** | 12MP Sony IMX708 Flush PDAF Scanner (Multimodal AI Vision & OCR)| Raspberry Pi / DigiKey | Official Cam Module 3 sensor + Sapphire | $14.50 |
| **LoRa Mesh** | 915/868 MHz LoRa Transceiver Module (+22dBm) | Mouser / LCSC | Semtech SX1262 (Ebyte E22-900M22S) | $5.50 |
| **LoRa Antenna Mount**| IP67 Bulkhead SMA Female Jack with O-Ring Gasket | LCSC / Amphenol | SMA-KFD08-IP67 | $1.80 |
| **LoRa Antenna** | Tactical 1/2-Wave 915MHz Dipole Whip (Center-Fed, 3.2dBi) | Linx Technologies / Mouser | ANT-916-CW-HWR-SMA | $8.50 |
| **NFC Controller** | 13.56 MHz NFC / Smartcard Reader & Crypto Signer + FPC Antenna | NXP Semiconductors / LCSC | PN5321A3HN / ST25R3916 | $2.40 |


---

## 2. Optional Phase 2 Accessory: SnapDeck Detachable Keyboard (Future Add-On)

*(Note: Descoped from the V1 core tablet. Developers connect any Bluetooth or USB-C keyboard, or a 3D-printed $20 BlackBerry Q20 handheld thumb keyboard).*

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Controller** | Multiprotocol Bluetooth 5.0 + USB SoC | Nordic Semiconductor / Mouser | nRF52840-QIAA | $3.20 |
| **Firmware** | Open-Source ZMK Keyboard Firmware | GitHub (ZMK) | Pre-configured Hex | $0.00 |
| **Key Switches** | Kailh X-Switch Ultra-Slim Mechanical Scissor (64 keys) | Kailh / AliExpress | CPG131601D01 | $12.00 |
| **Keycaps** | Low-Profile Chiclet Keycaps Set (PBT/ABS) | Kailh / YMDK | Ultra-thin 60% set | $6.00 |
| **Trackpad** | Blackberry RIM 9900 Optical Trackpad Sensor Module | AliExpress / LCSC | RIM 9900 OFN Sensor | $4.50 |
| **Battery** | 300 mAh 3.7V Ultra-Thin LiPo Pouch Cell | AliExpress / PKCELL | LP302030 | $2.50 |
| **Battery Charger** | Dedicated 1S LiPo Linear Charge IC (150mA 4.2V Termination) | Microchip / Mouser / LCSC | MCP73831T-2ACI/OT | $0.25 |
| **Battery PCM** | Miniature Hardware LiPo Protection IC & Dual N-MOSFET | Texas Instruments / LCSC | BQ2970 + CSD87330Q3D | $0.20 |
| **Docking Bus** | 5-Pin Magnetic Pogo Mating Header + N52 Magnets | LCSC / AliExpress | 5-Pin Female Pogo Strip | $3.00 |
| **PCB & Assembly**| Ultra-Thin 0.8mm 2-Layer Keyboard Matrix PCB + SMT | JLCPCB | Turnkey Assembly | $8.00 |
| **Enclosure** | SLS PA12 Nylon Keyboard Backplate & Shell | JLC3D | Custom CAD Shell | $6.50 |
| **Ergonomic Cant** | Magnetic Hinge Flap (7° Typing Cant) + Dual Alignment Pins | Custom Tooling / 304 SS | Custom Hinge + Pins | $1.40 |
| **Total SnapDeck**| | | | **$47.55** |

---

## 3. Modular Tactical RF & SIGINT USB-C Multi-Tool Dongle / Backpack (External Add-on)

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Sub-GHz Radio** | CC1101 300–928MHz Transceiver + Tuned Whip Antenna | Texas Instruments / LCSC | CC1101 Module | $3.50 |
| **NFC Transceiver**| NXP PN532 13.56MHz NFC Controller + PCB Trace Loop | NXP / LCSC | PN5321A3HN | $3.20 |
| **RFID Demod** | EM4095 125kHz Low-Frequency RFID Front-End + Coil | EM Micro / LCSC | EM4095HMS | $2.50 |
| **IR Blaster/RX** | Vishay 38kHz IR Demodulator + Dual High-Power 940nm LEDs | Vishay / LCSC | TSOP4838 + TSAL6200 | $1.20 |
| **Bridge MCU** | Dual Cortex-M0+ Controller (SPI/Analog/PWM Bridge) | Raspberry Pi / Mouser / LCSC| RP2040 | $0.70 |
| **USB 2.0 Hub IC** | 2-Port High-Speed USB 2.0 Hub (Splits SDR & Bridge MCU) | Genesys Logic / LCSC | GL850G / FE1.1s | $0.35 |
| **Sky-Scan SDR** | RTL2832U + R860 Wideband VHF/UHF SDR Tuner ICs (24–1766 MHz) | Realtek / Rafael Micro / LCSC | RTL2832U + R860 | $9.50 |
| **SDR SMA Mount**| Dedicated IP67 Bulkhead SMA for VHF/UHF Telescopic Antenna | LCSC / Amphenol | SMA-KFD08-IP67 | $1.80 |
| **VHF/UHF Antenna**| Telescopic 20–1300 MHz Retractable Field Antenna | AliExpress / Amazon | Nagoya NA-771 / Telescopic | $4.50 |
| **Interface Port**| Low-Profile Sealed USB-C Male Plug (Mates to USB-C Port 2) | LCSC / AliExpress | Type-C Male Right-Angle | $1.20 |
| **Enclosure** | Slim SLS PA12 Snap-on Rear Module Shell | JLC3D | Custom CAD Pod | $4.50 |
| **Total Modular Pod**| Complete Multi-Tool + Sky-Scanning SIGINT Add-on | | | **$32.95** |

---

## 4. Turnkey PCBA Fabrication & Box-Build

Because standard surface-mount components from JLCPCB's / PCBWay's Basic and Extended Parts Library are used, fabrication can be 100% automated:

* **Motherboard PCB:** Professional 6-Layer JLC2313 / Isola FR408HR stackup, ENIG surface finish, 100Ω differential pairs for USB 3 and the PCIe lane to the M.2 NVMe socket (ADR-042; the camera is V2, ADR-034) and 50Ω coplanar waveguides for RF antennas.
* **SMT Turnkey Assembly:** Automated pick-and-place of all passives, ICs, M.2 socket, and Hirose connectors.
* **Turnkey Batch Prototype Costs (5 Units at JLCPCB/PCBWay):**
  * Bare PCBA fabrication (5 boards, 6-Layer): $32.00
  * SMT Stencils & Machine Setup: $30.00
  * Motherboard components & assembly: ~$122.00 per board
  * Per-finished-tablet turnkey assembly (excluding CM5/Display): ~$152.00 each.

---

## 5. Value Comparison (SolarDeck vs Commercial Field Tablets)

```
┌─────────────────────────────────────────────────────────────┐
│  SOLARDECK V1 TABLET (excl. 11 TBD parts)   │ $479 – $481    │
├─────────────────────────────────────────────────────────────┤
│  OPTIONAL SNAPDECK KEYBOARD (PHASE 2)      │ $47.55         │
├─────────────────────────────────────────────────────────────┤
│  MODULAR TACTICAL RF & SIGINT POD          │ $32.95         │
├─────────────────────────────────────────────────────────────┤
│  reMarkable 2 (Monochrome, No Backlight)   │ $399 – $449    │
│  Kindle Scribe 10.2" (Closed DRM Amazon)   │ $369 – $419    │
│  Onyx Boox Note Air 3C (Color, Android)    │ $499 – $549    │
│  Panasonic Toughbook Rugged Slate          │ $1,800 – $2,500│
└─────────────────────────────────────────────────────────────┘
```
