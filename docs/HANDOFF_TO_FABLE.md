# SolarDeck V1 — Engineering Handover for Fable

Written 2026-10-19 09:49 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Executive Summary & Purpose

**SolarDeck** is an open-hardware, sunlight-readable 10.3" Color E-Ink mobile workstation and tactical terminal running mainline bare-metal Linux.

This document serves as the master engineering handover for **Fable** to conduct the full system audit on Wednesday (2026-10-21). It summarizes the current state across all three engineering tracks, details the submitted manufacturing package at Seeed Studio, documents the master verification pipeline, and provides an actionable audit checklist.

---

## 2. Current Manufacturing Status: Seeed Studio Fusion

On 2026-10-19, the complete Turnkey PCBA and Box-Build quotation package was officially submitted to **Seeed Studio Fusion** (Shenzhen, China) and is currently in the **"Waiting for Quotation"** review queue.

### Sourcing & Assembly Parameters
* **Circuit Board:** 6 Layers, standard FR-4 TG130, 1.6 mm thickness, **ENIG (Electroless Nickel Immersion Gold)**, Matte Black solder mask, white silkscreen, 5/5 mil trace width/spacing, 0.3 mm minimum drill hole.
* **Fabrication Quantity:** **5 bare PCBs** (standard minimum panel run).
* **PCBA Assembly Quantity:** **1 assembled board** (keeps initial prototype chip cost minimal; 4 spare bare boards).
* **Display Specification:** Locked to the **10.3" E Ink Kaleido 4 Color Display with Laminated Wacom EMR Digitizer & IT8951 EPDC** (40,000+ colors, +15% whiter reflectance, +50% contrast, 18 FPS Oxide TFT refresh, zero parallax). Sourced via Guangdong DKE / Good Display (with standard Kaleido 3 as fallback if lead time > 3 weeks).
* **Destination:** Honolulu, Hawaii, USA (Air Freight via DHL Express International Priority / FedEx, Section II UN3481 Lithium Battery declaration).

---

## 3. Repository Architecture & Delivered Tracks

```
.
├── config/
│   ├── sway/config                         # Monochrome high-contrast Sway window manager
│   └── waybar/                             # Status bar with solar/battery telemetry widget
├── docs/
│   ├── INDEX.md                            # Documentation index & project roadmap
│   ├── HARDWARE_SPEC.md                    # Carrier board schematic & power topology
│   ├── SOFTWARE_SPEC.md                    # Kernel DRM waveforms & daemon specs
│   ├── BOM_COST_ESTIMATE.md                # Component pricing & sourcing breakdown
│   ├── HARDWARE_VERIFICATION_WORKFLOW.md   # 5-stage pre-fab verification guide
│   ├── MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md # 4-step screen/board/box mechanical fit guide
│   ├── OFFGRID_TACTICAL_SENSORS.md         # Off-grid power, RF, SIGINT, Hotpacks & GPU catalog
│   └── HANDOFF_TO_FABLE.md                 # This handover document
├── firmware/
│   └── rp2350/                             # Bare-metal C co-processor state machine
│       ├── include/solardeck_state.h       # Power states, ADC sampling & wake triggers
│       ├── src/solardeck_sm.c              # State machine implementation
│       ├── src/main.c                      # Pico SDK entrypoint
│       └── test/test_rp2350_sm.c           # Assert-based self-test (<300ms S2idle wake)
├── hardware/
│   ├── solardeck-carrier.kicad_pro         # KiCad 8 project file
│   ├── solardeck-carrier.kicad_sch         # Root master hierarchical schematic
│   ├── power.kicad_sch                     # BQ25895 + TPS62840 + TPS61088 + BQ25504
│   ├── compute.kicad_sch                   # Hirose DF40 CM4 + RP2350B + PSRAM + Flash + RTC
│   ├── display.kicad_sch                   # TMUX1575 SPDT Mux + IT8951 40-pin FPC
│   ├── io.kicad_sch                        # VL805 PCIe USB, M.2 NVMe, M.2 Modem, Dual-SIM
│   ├── solardeck-carrier.net               # Complete 20-component electrical netlist
│   ├── solardeck-carrier.kicad_pcb         # 6-layer PCB layout with ENIG stackup
│   ├── audit_hardware_traps.py             # 7-rule electrical netlist trap auditor
│   ├── export_production_zip.py            # RS-274X Gerber & binary STL exporter
│   ├── enclosure/
│   │   ├── solardeck_chassis.scad          # Parametric OpenSCAD 227×165×9.8mm IP67 chassis
│   │   └── verify_enclosure.py             # CAD envelope assertion check
│   └── production/                         # Manufacturing export assets
│       ├── solardeck_gerbers.zip           # 6-Layer KiCad 8 RS-274X Gerber files
│       ├── seeed_pcba_bom.csv              # Formatted SMT BOM (19 soldered chips)
│       ├── seeed_fusion_bom.csv            # Master Box-Build BOM (includes modular items)
│       ├── solardeck_cpl.csv               # Pick-and-Place automated centroid coordinates
│       ├── solardeck_chassis.stl           # SLS PA12 3D enclosure mesh
│       ├── solardeck_assembly_package.zip  # Assembly instructions & 3D models bundle
│       ├── solardeck_test_plan.zip         # Functional test plan bundle
│       └── SEEED_FUSION_BOX_BUILD_INSTRUCTIONS.md # Complete assembly & DHL guide
├── scripts/
│   └── verify_all.py                       # 7-Phase Master Verification Engine
└── src/
    ├── daemons/
    │   ├── eink-refreshd/                  # Cadence-aware anti-ghosting engine
    │   └── solardeck-telemetryd/           # RP2350 UART telemetry bridge daemon
    └── dts/
        └── solardeck-cm4.dts               # Linux Device Tree Overlay
```

---

## 4. Master Verification Engine (`verify_all.py`)

All engineering tracks are continuously tested by a single, zero-dependency master verification runner:

```bash
python3 scripts/verify_all.py
```

### Verification Pipeline Breakdown:
1. **Phase 1: KiCad Schematics & Netlist Structure:** Validates syntax of all 4 sub-sheets, root sheet, and 20 components.
2. **Phase 2: Electrical Netlist Trap Audit (7 Rules):**
   * Rule 1: No unpulled open-drain lines (I2C SDA/SCL have 4.7kΩ pullups).
   * Rule 2: Zero single-node floating nets.
   * Rule 3: Single master per bus (TMUX1575 SPI isolation).
   * Rule 4: Clean power domain isolation (no back-powering between AON 3.3V and SYS 5V).
   * Rule 5: RP2350 brownout prevention (dedicated TPS62840 Always-On rail).
   * Rule 6: S2idle GPIO wake connectivity.
   * Rule 7: LiFePO4 chemistry protection (hard cutoff at 3.65V).
3. **Phase 3: RP2350 Co-Processor State Machine:** Compiles and runs `test_rp2350_sm.c` with native C assertions (verifies <300ms S2idle wake, solar MPPT sampling, and battery cutoff in <150ms).
4. **Phase 4a: `eink-refreshd` Cadence Engine:** Compiles and runs `test_refreshd.c` (verifies <800ms fast-typing lockout, >1.2s pause scrub, and 30-frame auto-scrub).
5. **Phase 4b: `solardeck-telemetryd` Telemetry Bridge:** Compiles and runs `test_telemetryd.c` (verifies UART packet framing, CRC-8 validation, and JSON generation).
6. **Phase 5: OpenSCAD Mechanical Envelope:** Validates 227×165×9.8 mm unibody dimensions, 10.3" screen cutout, Cold Storage Vault (3x MicroSD pockets), camera port, GORE vent, and M2.5 75×75mm VESA inserts.
7. **Phase 6 & 7: SMT PCBA & Seeed Fusion Turnkey Assets:** Verifies CPL coordinates, BOM row counts, Gerber zip layer integrity, and box-build documentation.

*Execution Time:* **~1.5 seconds**, fully automated in GitHub Actions CI (`.github/workflows/verify.yml`).

---

## 5. Wednesday Audit Checklist for Fable

When auditing the design on Wednesday, focus on the following verification points:

### 1. Review Seeed Studio Fusion Quotation
* Log into the Seeed Studio account and inspect the draft quote in the shopping cart.
* Verify the pricing and lead times for the 7 manually checked components:
  * `U2`: TI TPS62840DLYR
  * `U14`: TI TMUX1575PWR
  * `U16`: VIA VL805-Q6
  * `J_NVME`: Amphenol / LOTES M.2 Key-M
  * `J_MODEM`: JAE / LOTES M.2 Key-B
  * `U18`: STMicroelectronics ST4SIM-200M00T
  * `J_SIM`: Molex 1051681206
* Verify the itemized Box-Build addition for the **10.3" Kaleido 4 + Wacom EMR kit** (`ED103TC4-WACOM`). If Seeed indicates Kaleido 4 sample lead times exceed 3 weeks, approve the fallback to **Kaleido 3 / Carta 1200**.

### 2. Verify Component Clearances, Mechanical Stackup & Thermal Path
* **Mechanical Fit & Enclosure Verification (See `docs/MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md`):**
  * **Screen XY Tolerance:** Confirm the $+0.40\,\text{mm}$ perimeter clearance in the chassis pocket ($228.5 \times 166.6\,\text{mm}$ pocket for $227.7 \times 165.8\,\text{mm}$ glass) with a $0.3\,\text{mm}$ Poron foam shock gasket.
  * **Z-Stackup Thickness Budget:** Confirm the $12.55\,\text{mm}$ nominal total thickness budget (bezel, OCA, display, Poron gasket, aluminum midframe, PCB, Hirose DF40 standoff, CM4, rear wall).
  * **FPC Ribbon Bend Slot:** Verify the aluminum midframe features a through-slot with CNC-filleted edges ($R \ge 1.5\,\text{mm}$) so the $180^\circ$ flex tail does not pinch or fatigue against sharp metal.
  * **Pre-Metal Sanity Checks:** Run the Tier-1 1:1 scale paper DXF printout ($0) and Tier-2 $15 3D-printed PLA/PETG skeleton test fit before releasing the design for $150+ CNC 6061-T6 aluminum machining.
* **CM4 SoC Thermal Dissipation:** Confirm that the CM4 SoC mates via a 1.0 mm thermal silicone pad directly to the 1.5 mm unibody backplate (374 cm² effective heatsink area; no fan required).
* **LiFePO4 Pouch Cavity:** Verify that the 140 × 95 × 4.2 mm internal cavity allows 10% volumetric expansion for the 8,000–10,000 mAh pouch cell across 3,000+ thermal charge cycles.
* **M.2 2242 NVMe SSD:** Verify single-sided SSD clearance under the rear service hatch.

### 3. Review Modular Architecture & Hotpack Allocations (See `docs/OFFGRID_TACTICAL_SENSORS.md`)
* **Descoped Custom Flipper Zero Clone:** Operators connect their physical **Flipper Zero** to USB-C Port 2 or Bluetooth 5.0, running `qflipper-cli` and `flipperzero-protobuf` on SolarDeck's 10.3" screen.
* **Pure USB-C Port 2 (Host) Expansion:** All modular packs connect via recessed right-angle USB-C and rear MagSafe / M2.5 anchors, eliminating fragile pogo pins that fail in sand/salt spray.
* **4 Modular USB-C Hotpacks Defined:**
  * **Hotpack 1: Doomsday Sky-Scan & SIGINT:** RTL-SDR v4 (24MHz–1.76GHz), dual top SMA ports, 137MHz/1090MHz SAW filters for direct weather satellite (`satdump`) and air radar (`readsb`).
  * **Hotpack 2: Tactical Dual-Mesh & HF Transceiver:** Dedicated 2nd SX1262 LoRa (MeshCore/Reticulum) running concurrently with internal Meshtastic radio; QRP 5W HF transceiver for JS8Call 2,000-mile text over ionosphere; 3.5mm TRRS APRS TNC.
  * **Hotpack 3: CBRN & SAR Environmental:** PocketGeiger Type 5 radiation dosimeter, FLIR Lepton 3.5 / InfiRay P2 thermal camera (smoke/darkness penetration), Sensirion SCD41 CO2/VOC sensor.
  * **Hotpack 4: Precision RTK Survey:** u-blox ZED-F9P (1.4cm RTK) + Galileo HAS (20cm satellite-direct positioning with zero internet).
* **Hawaii Sun Thermal Management:** Integrated solar smart cover descoped due to +70°C surface baking; use separate 15W–28W folding USB-C solar panel in direct sun with a 3m cable to SolarDeck in ambient shade.

### 3. Review Firmware Sleep Timers & Wake Thresholds
* In `firmware/rp2350/include/solardeck_state.h`:
  * `SOLAR_V_MIN_HARVEST_MV = 1200` (1.2V minimum solar trickle threshold).
  * `S2IDLE_WAKE_TIMEOUT_MS = 300` (<300ms instant wake trigger).
  * `BATTERY_LIFEPO4_MAX_MV = 3650` (3.65V strict charge ceiling).
  * `BATTERY_LIFEPO4_CUTOFF_MV = 2500` (2.50V emergency brownout shutdown).

### 4. Updating and Re-Exporting Assets (If Revisions Are Made)
If Fable makes any adjustments to schematics, CAD dimensions, or BOM items:
```bash
# 1. Re-generate all production assets (Gerbers, BOM, STL):
python3 hardware/export_production_zip.py

# 2. Re-run master verification:
python3 scripts/verify_all.py

# 3. Re-upload updated zip files to Seeed Studio cart via:
open hardware/production/
```

---

## 6. Next Steps Following the Audit

Once the design is confirmed and the quote is locked:
1. **Automated OS Provisioning Script (`tools/provision/setup_solardeck_os.sh`):**
   * Pre-bake the Raspberry Pi OS Lite setup script (compiling `solardeck-cm4.dtbo`, configuring `eink-refreshd.service`, `solardeck-telemetryd.service`, Sway, Alacritty, and Wacom udev rules).
2. **Offline Sovereign Stack:**
   * Download and format the 3x Cold Storage Vault MicroSD cards with Kiwix (English Wikipedia, ArchWiki, StackExchange, OpenStreetMap).
3. **Approve Production:**
   * Authorize Seeed Studio Fusion to proceed with fabrication and DHL priority shipping to Honolulu.
