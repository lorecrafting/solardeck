# SolarDeck Bill of Materials (BOM) & Manufacturing Cost Estimate

Written 2026-10-18 17:31 UTC in the Pi harness by antigravity/gemini-3.8-flash

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:52 UTC in Claude Code by anthropic/claude-opus-5-5 (owner decisions, ADR-046).
Revised 2026-10-21 19:46 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).
Revised 2026-10-21 20:42 UTC in Claude Code by anthropic/claude-opus-5-5 (10 TBD rows priced, part picks, port roles, ADR-049).

Comprehensive bill of materials, component part numbers, verified suppliers, and turnkey manufacturing cost projections for the core tablet and the modular RF backpack. The SnapDeck keyboard is an optional Phase 2 accessory (§2), not part of the V1 BOM.

---

## 1. Core SolarDeck Tablet BOM

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- | :--- |
| **Compute** | Raspberry Pi Compute Module 5 (16GB RAM, 64GB eMMC, Wi-Fi/BT) — ADR-031 | Raspberry Pi approved resellers | CM5116064 (SC1608) | $375.00 |
| **Co-Processor** | Dual Cortex-M33 / RISC-V Microcontroller (Power Master) | DigiKey / Mouser / LCSC | Raspberry Pi RP2350B | $1.25 |
| **Co-Proc PSRAM** | 8MB Ultra-Low-Power QSPI PSRAM (Page Double-Buffer) | Mouser / LCSC | APMemory APS6404L-3SQR-SN | $0.75 |
| **Co-Proc Flash** | 16 MB QSPI NOR flash: RP2350B firmware (two slots) + reader content; the RP2350B has no internal flash (ADR-046). DigiKey 2026-10-21 qty 1 | Winbond / DigiKey | W25Q128JVSIQ | $5.99 |
| **Bus Multiplexer**| Display Bus Isolator, 2 × 4-channel SPDT switch (ADR-004) | Texas Instruments / Mouser | TMUX1575YCJR (x2) | $0.55 |
| **Display Panel** | 10.3" E Ink Kaleido 4 (colour) + Capacitive Touch + Wacom EMR — ADR-032 | E Ink (sole source) | Kaleido 4 10.3" (P/N on release) | TBD |
| **EMR Shielding** | 0.1mm High-Permeability Mu-Metal / Ferrite Flux Absorber Sheet | 3M / Wurth / AliExpress | Custom Die-Cut Shield Foil | $1.80 |
| **Controller** | Kaleido 4 display controller / TCON (the IT8951 cannot drive Kaleido 4 — ADR-025, ADR-032) | TBD with E Ink | TBD | TBD |
| **Stylus** | Wacom EMR Passive Stylus with Eraser | Amazon / B&H | Staedtler Noris Digital or Lamy AL-star | $28.00 |
| **Battery** | 1S2P Li-ion user-replaceable smart pack: 2× EEMB LP7545135 (`battery_wh.li_ion`) + pack board (protector, FETs, fuse, gauge), keyed connector, screws, no adhesive; built by EEMB, quote and pack-level UN38.3 requested (ADR-048, ADR-049) | EEMB | 2× LP7545135, custom pack | TBD |
| **Power IC** | 1S Li-ion buck-boost charger, VREG 3.0–18.8 V; OTG unused (ADR-035, ADR-049). DigiKey 2026-10-21 qty 1 | Texas Instruments / DigiKey | BQ25798RQMR | $5.90 |
| **USB-PD Sink Ctrl**| Standalone USB-PD sink controller on port 1, the only power input (ADR-048, ADR-049). DigiKey 2026-10-21 qty 1 | STMicroelectronics / DigiKey | STUSB4500QTR | $2.22 |
| **AON 3.3V Supply**| Low-IQ buck-boost for the always-on rail, holds 3.3 V to an empty pack (ADR-048; pins in docs/EVT0_POWER_BOARD.md). DigiKey 2026-10-21 qty 1; 0 in stock, Mouser on order | Texas Instruments / DigiKey | TPS63900DSKR | $3.10 |
| **5V Boost Conv**| Synchronous boost with true output disconnect, 5 V CM5 / port 2 supply (ADR-049, docs/EVT0_POWER_BOARD.md §2.6). DigiKey 2026-10-21 qty 1; 0 in stock | Texas Instruments / DigiKey | TPS61022RWUR | $2.38 |
| **Micro-Solar** | Top-Bezel Monocrystalline Trickle Strip (~0.15W Peak, 50-120mW Real)| IXYS / DigiKey / Mouser | SM141K06L / PowerFilm | $3.50 |
| **Power Gates** | Ultra-Low Leakage Load Switches (Airgap Cut + Port 2 VBUS + radio MCU rail, ADR-055) | Texas Instruments / LCSC | TPS22918DBVR (x3) | $1.20 |
| **GNSS Receiver**| Standalone multi-constellation GNSS, integrated LNA, on the RP2350 UART (ADR-038). DigiKey 2026-10-21 qty 1 | u-blox / DigiKey | MAX-M10S-00B | $11.42 |
| **Wi-Fi/BT Antenna**| Dual-Band (2.4/5GHz) Balanced Dipole FPC with U.FL | Molex / Mouser | 1461530100 | $1.20 |
| **GNSS Antenna** | Passive Internal FPC GPS/GLONASS Antenna (for MAX-M10S; integrated LNA) | Molex / Taoglas / LCSC | 1461860100 | $0.90 |
| **Audio** | Dual-MEMS Acoustic Array (2x SPH0645) + I2S Class-D Amp + Speaker| Knowles / Maxim Integrated / PUI Audio | SPH0645LM4H (x2) + MAX98357A + AS03008MR | $5.10 |
| **Mechanical Mount**| Universal M2.5 Brass Heat-Set Inserts (x4) + MagSafe Magnetic Array | McMaster / LCSC / Custom | M2.5 Inserts + N52 Ring | $0.90 |
| **Passives/Ports**| 2x IP68 USB-C Ports, 1,000µF Poly Caps, SMD Passives | LCSC / JLCPCB SMT Library | Standard SMD 0402/0603 | $9.40 |
| **USB-C CC Ctrl** | Type-C CC controller for port 2, strapped source-only (ADR-049) | Texas Instruments / Mouser | TUSB320RWBR | $0.65 |
| **I/O Isolators** | Fail-Safe Cross-Domain Buffers with I_off Partial-Power-Down | Texas Instruments / Mouser | TXU0104PWR (x2) | $0.50 |
| **Rail Gates** | Single-gate I_off buffers powered from the GNSS and radio MCU rails, for the lines a CM5-rail TXU0104 cannot isolate (ADR-055, `pins.gate_buffers`) | Texas Instruments | SN74LVC1G125 (x3) | TBD |
| **Motion Sensor** | Ultra-Low-Power 3-Axis Accelerometer (3.5µA Pick-up Wake) | Bosch Sensortec / Mouser | BMA400 | $1.10 |
| **Barometer** | Precision Atmospheric Pressure & Altimeter Sensor | Bosch Sensortec / Mouser | BMP390 | $1.20 |
| **5-Way Rocker** | IP67 Sealed Micro Navigation Joystick (Up/Down/Left/Right/Press)| ALPS / Panasonic / Mouser | SKRHABE010 | $0.85 |
| **Power Telemetry**| 3-Channel High-Side Current & Power Monitor IC (Rail Logging)| Texas Instruments / Mouser | INA3221AIRGVR | $1.20 |
| **GPIO Expander** | 16-bit low-quiescent I²C GPIO expander with interrupt, on the always-on bus at 0x20/0x21 (ADR-045, ADR-049, docs/PIN_BUDGET.md §4). DigiKey 2026-10-21 qty 1 | NXP / DigiKey | PCAL6416AHF,128 | $1.61 |
| **Coulomb Counter**| Pack-side Impedance Track fuel gauge on the pack board, characterised on the chosen cell (ADR-035, ADR-048). DigiKey 2026-10-21 qty 1 | Texas Instruments / DigiKey | BQ27Z561YPHR-R2 | $2.23 |
| **Thermal Triad** | Dual Precision Digital Temperature Sensors (Batt + E-Ink Logs)| Texas Instruments / LCSC | TMP112AIDRLR (x2) | $0.60 |
| **Ambient Lux Sensing**| Integrated via Solar Strip & RP2350 12-Bit ADC (Zero-BOM Innovation)| IXYS / RP2350 Subsystem | ADC Channel 3 ($0 Added Silicon) | $0.00 |
| **Host VBUS Sw** | 1.5A Current-Limited USB Host Distribution Power Switch | Texas Instruments / Mouser | TPS2051BDBVR | $0.45 |
| **Recovery Sw** | Single Sub-Miniature IP67 Pinhole Micro-Tactile Switch | C&K / Panasonic / LCSC | KMR2 / EVQ-P8 | $0.20 |
| **Voice Button** | Hold-to-talk tactile switch: wakes the RP2350, which starts audio capture while the CM5 boots (ADR-036) | C&K / Panasonic / LCSC | KMR2 / EVQ-P8 | $0.20 |
| **Harvester Gate** | Hardware temperature gate for the solar harvester: dual open-drain comparator + load switch (ADR-048, ADR-049, docs/EVT0_POWER_BOARD.md §2.7.1). DigiKey 2026-10-21 qty 1 (1.86 + 0.63) | Texas Instruments / DigiKey | TLV7042DDFR + TPS22916CNYFPR | $2.49 |
| **Pack Connector** | Keyed, locking 6-position pack connector: header + receptacle + 6 crimps (ADR-049, docs/EVT0_POWER_BOARD.md §2.3); the priced crimp is 20–22 AWG, the 8 A rating needs 18 AWG (open item 20). DigiKey 2026-10-21 qty 1 (0.85 + 0.49 + 6 × 0.22) | Hirose / DigiKey | DF63-6P-3.96DSA + DF63-6S-3.96C + DF63A-2022SCF | $2.66 |
| **Bezel Solar MPPT**| Nano-Power Solar Boost Harvester IC (cold start and MPPT per SLUSAH0G §7.5, docs/EVT0_POWER_BOARD.md §2.7)| Texas Instruments / Mouser | BQ25504RGTR | $1.80 |
| **Frontlight Driver**| Dual-Channel Constant-Current Step-Up LED Driver (2048-step CCT)| Texas Instruments / Mouser | TPS61163YFFR | $0.65 |
| **Battery PCM** | Pack-side high-side Li-ion protector + common-drain N-FET pair on the pack board (ADR-049, docs/EVT0_POWER_BOARD.md §2.2). The pack fuse is not priced: its rating must sit below the FET and connector ratings, which the Nano2 family cannot (EVT-0 open item 20). DigiKey 2026-10-21 qty 1 (0.63 + 1.04) | Texas Instruments / DigiKey | BQ298216RUGR + CSD83325L | $1.67 |
| **ESD Suppression** | Low-Capacitance TVS Diode Arrays for USB & Pogo Pins (x4) | Texas Instruments / Mouser | TPD4E05U06 (x4) + SMAJ5.0A | $0.80 |
| **RTC** | Always-on I²C real-time clock with its own crystal and backup switchover, on the RP2350 bus at 0x52 — no GPIO (ADR-046). DigiKey 2026-10-21 qty 1; 0 in stock at DigiKey/Mouser/LCSC, Mouser expects April 2027 | Micro Crystal / DigiKey | RV-3028-C7 32.768KHZ 1PPM-TA-QC | $2.41 |
| **RTC Backup Battery**| 3.3V Rechargeable Lithium Micro-Battery (5.5 mAh, >100 days hold)| Seiko Instruments / Mouser | MS621FE-FL11E | $0.65 |
| **JEITA Resistors** | 0.1% Precision Resistors for the BQ25798 TS NTC network (values per BQ25798 datasheet) | Yageo / Panasonic 0603 | Precision Thin-Film (x2)| $0.15 |
| **CM5 Retention** | CNC Aluminum CM5 Retention Bracket & Thermal Interface Pad | Custom CNC / Laird | Custom Bracket + Tflex | $1.80 |
| **RF Pi-Matching** | Precision 0402 RF Inductors & C0G/NP0 Capacitors (5 nets) | Murata / TDK / LCSC | 0402 Precision RF Kit | $0.40 |
| **Solar Aerogel** | 0.5mm Die-Cut Pyrogel Aerogel / Kapton Thermal Barrier | Aspen Aerogels / 3M | Pyrogel Insulation Strip | $0.60 |
| **Privacy Switch** | Sealed (IP67 terminals) 2-pole 3-position on-off-on slide switch: normal / mic mute (centre) / full blackout (HARDWARE_SPEC §2.25, ADR-049). Mouser 2026-10-21 qty 1 | E-Switch / Mouser | 600DP3S2M4R | $4.78 |
| **GORE Vent** | ePTFE Pressure Equalization Vent Plug | W. L. Gore / Amphenol | PMF100396 | $1.50 |
| **Haptic Engine** | Wideband Haptic Driver + frame-mounted Z-Axis LRA, core part (ADR-037; piezo array = DNP) | Texas Instruments / Vybronics | DRV2605L + 8mm Z-Axis LRA | $2.35 |
| **Perimeter Gasket** | Die-Cut VMQ Silicone O-Ring, 27% Compression (Service Item) | Custom / Rogers | Custom Die-Cut VMQ | $2.10 |
| **Enclosure (PA12)**| SLS 3D-Printed PA12 Nylon Shell + 85A TPU Corner Bumpers | JLC3D / Craftcloud | Custom CAD Housing (Streamlined)| $25.00 |
| **Conformal Coat** | IPC-CC-830 Reworkable Acrylic Conformal Coating, Connector-Masked (spec_values.longevity.conformal_coat) | PSI / Applied Post-SMT | IPC-CC-830 (UC-2605) | $2.00 – $4.00 |
| **LoRa Radio** | 915/868 MHz LoRa Transceiver Module (+22dBm), on the radio MCU's SPI bus (ADR-055) | Mouser / LCSC | Semtech SX1262 (Ebyte E22-900M22S) | $5.50 |
| **LoRa Antenna Mount**| IP67 Bulkhead SMA Female Jack with O-Ring Gasket | LCSC / Amphenol | SMA-KFD08-IP67 | $1.80 |
| **LoRa Antenna** | Tactical 1/2-Wave 915MHz Dipole Whip (Center-Fed, 3.2dBi) | Linx Technologies / Mouser | ANT-916-CW-HWR-SMA | $8.50 |
| **Radio MCU (BLE)** | Always-on Bluetooth LE MCU module (nRF52840 class) that owns the LoRa radio and talks to the RP2350 over UART (ADR-055) | TBD | TBD | TBD |
| **Total Core BOM**| **(Sum of 58 V1 Line Items, excluding 5 TBD parts: the mono panel, its controller, the battery pack, the radio MCU, the rail gates — a floor, not a price; distributor prices at qty 1, before tariffs; see docs/AUDIT_6_2026-10-21.md H22)** | | | **$540.96 – $542.96 + TBD** |

### Deferred to V2 (ADR-034) — not summed

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- | :--- |
| **Modem Supply** | 3.8V 2.5A Synchronous Buck-Boost (Anti-Brownout Buffer) | Texas Instruments / Mouser | TPS63020DSJR | $1.10 |
| **Cellular Modem**| Worldwide M.2 Key-B 4G/LTE Cat-4 Modem with Nano-SIM Tray | DigiKey / AliExpress | Quectel EG25-G | $29.00 |
| **MFF2 eSIM Chip** | Consumer eUICC (GSMA SGP.22) Micro-eSIM, MFF2 DFN-8 — ADR-033 | TBD | TBD (ST4SIM-200M rejected: M2M SGP.02) | TBD |
| **LTE MIMO Antennas**| Ultra-Wideband (698–3000 MHz) Flexible PCB Antennas (x2) | Taoglas / DigiKey | FXUB63.07.0150C (Main + Div) | $8.40 |
| **Rear Camera** | 12MP Sony IMX708 Flush PDAF Scanner (Multimodal AI Vision & OCR)| Raspberry Pi / DigiKey | Official Cam Module 3 sensor + Sapphire | $14.50 |
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
│  SOLARDECK V1 TABLET (excl. 5 TBD parts)    │ $541 – $543    │
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
