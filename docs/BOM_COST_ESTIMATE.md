# SolarDeck Bill of Materials (BOM) & Manufacturing Cost Estimate

Comprehensive bill of materials, component part numbers, verified suppliers, and turnkey manufacturing cost projections.

---

## 1. Component Level BOM

| Category | Component Description | Primary Supplier / Manufacturer | Part Number / Model | Est. Unit Cost (Qty 1-5) |
| :--- | :--- | :--- | :--- | :--- |
| **Compute** | Raspberry Pi Compute Module 4 (4GB RAM, 32GB eMMC, Wi-Fi) | DigiKey / Newark / PiShop | CM4104032 | $55.00 |
| **Co-Processor** | Dual Cortex-M0+ Microcontroller | DigiKey / Mouser | RP2040 | $1.00 |
| **RTC** | High-Precision TCXO Real-Time Clock | Mouser / LCSC | DS3231SN# | $2.50 |
| **Display Panel** | 10.3" E-Ink Kaleido 3 (Color) + Capacitive Touch + Wacom EMR Layer | Waveshare / Good-Display / AliExpress | ED103TC2 / GDEW103W32 | $95.00 – $120.00 |
| **Controller** | Electronic Paper Display Controller (EPDC) | Waveshare / ITE | IT8951 Board / IC | $18.00 |
| **Stylus** | Wacom EMR Passive Stylus with Eraser | Amazon / B&H | Staedtler Noris Digital or Lamy AL-star | $28.00 |
| **Battery** | 6,400 mAh 3.2V Prismatic LiFePO4 Cell Pack | Batteryhookup / AliExpress | IFR26650 / Custom Prismatic | $12.00 |
| **Power IC** | Synchronous MPPT Buck Battery Charger IC | Texas Instruments / Mouser | BQ25895RTWR | $3.50 |
| **Power Gates** | Ultra-Low Leakage Load Switches (x4) | Texas Instruments / LCSC | TPS22918DBVR | $1.20 |
| **Cellular** | M.2 Key-B 4G/LTE Cat-4 Modem Module | DigiKey / AliExpress | Quectel EC25-AFX | $28.00 |
| **LoRa Mesh** | 915 MHz LoRa Transceiver Module (+22dBm) | Mouser / LCSC | Semtech SX1262 (Ebyte E22-900M22S) | $5.50 |
| **Sub-GHz RF** | Low-Power Sub-1GHz RF Transceiver | Texas Instruments / LCSC | CC1101RGPR | $2.80 |
| **IR Blaster/RX**| 38kHz IR Receiver + Dual High-Power 940nm LEDs | Vishay / LCSC | TSOP4838 + TSAL6200 | $1.20 |
| **NFC / RFID** | NFC Transceiver IC + 125kHz Analog Front-End | NXP / LCSC | PN532 + EM4095 | $4.50 |
| **Audio** | Dual I2S Digital MEMS Microphones + I2S 3W Amp | InvenSense / Maxim / LCSC | SPH0645LM4H + MAX98357A | $3.00 |
| **Solar Bezel** | SunPower Maxeon Monocrystalline Solar Cut Strips | SunPower / AliExpress | C60 Cut Cells (15x90mm) | $3.00 |
| **Docking Bus** | 5-Pin Gold-Plated Magnetic Pogo Pin Assembly | LCSC / AliExpress | Magsafe-style Pogo 2.54mm | $2.50 |
| **Passive/Misc** | Passives, Connectors (IP68 USB-C, Nano-SIM, Audio) | LCSC / JLCPCB SMT Library | Standard SMD 0402/0603 | $8.00 |
| **GORE Vent** | ePTFE Pressure Equalization Vent Plug | W. L. Gore / Amphenol | PMF100396 | $1.50 |

---

## 2. PCBA & Motherboard Fabrication (Turnkey at JLCPCB / PCBWay)

Because we use standard surface-mount components available in JLCPCB's Parts Library, the custom motherboard can be fabricated and assembled automatically:

* **PCB Fabrication:** 4-Layer FR-4, ENIG (Electroless Nickel Immersion Gold) surface finish, impedance-controlled.
* **SMT Assembly:** Turnkey automated Pick-and-Place of all ICs, connectors, and passives.
* **Cost for Prototype Run (5 Boards):**
  * PCB Bare Boards: $22.00
  * SMT Setup & Stencils: $30.00
  * Components & SMT Assembly: ~$110.00
  * **Per-Board Assembled Cost:** **~$32.00 to $38.00 each**.

---

## 3. Enclosure & Mechanical Tooling

### Option A: Rapid Prototyping (Phase 1)
* **Main Tablet Shell:** SLS (Selective Laser Sintering) 3D-printed **Nylon PA12** (black dyed) via JLC3D or Craftcloud.
  * Extremely strong, chemical resistant, waterproof when vapor-smoothed.
  * Cost: **~$22.00 per shell**.
* **Corner Bumpers:** 85A TPU (3D printed). Cost: **~$6.00**.
* **Seals:** Die-cut silicone flat gaskets or liquid silicone gasket sealant. Cost: **~$3.00**.

### Option B: Production Rugged (Phase 2)
* **Main Tablet Shell:** CNC Machined 6061-T6 Aluminum with Matte Black Hard-Anodized Type III finish (acts as full-body heatsink).
  * Machining via JLC-CNC or RapidDirect in small batches.
  * Cost: **~$65.00 per unit**.

---

## 4. Total Cost Comparison (SolarDeck vs Commercial Tablets)

```
┌─────────────────────────────────────────────────────────────┐
│  SOLARDECK (DIY TURNKEY BUILD)            │ ~$190 – $240    │
├─────────────────────────────────────────────────────────────┤
│  reMarkable 2 (Monochrome, No Backlight)  │ $399 – $449     │
│  Kindle Scribe 10.2" (Closed DRM Amazon)  │ $369 – $419     │
│  Onyx Boox Note Air 3C (Color, Bloated OS)│ $499 – $549     │
│  Panasonic Toughbook Rugged Tablet        │ $1,800 – $2,500 │
└─────────────────────────────────────────────────────────────┘
```

### The Unfair Value Advantage:
For **less than half the price** of an Onyx Boox or reMarkable tablet, SolarDeck delivers:
1. **Full Linux & Native Claude Code** (not locked-down Android).
2. **Dual-Use Ambient Solar Bezel** (perpetual LifeOps desk clock).
3. **Flipper Zero RF Multi-Tool** integrated into the motherboard.
4. **Worldwide 4G/LTE + Meshtastic LoRa** off-grid mesh communications.
5. **Indestructible IP67 Waterproofing** and safe LiFePO4 battery chemistry.
