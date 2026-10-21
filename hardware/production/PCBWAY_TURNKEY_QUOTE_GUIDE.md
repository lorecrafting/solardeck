# PCBWay Turnkey PCBA & Box-Build Quoting Guide

*Written 2026-10-19 17:00 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Revised 2026-10-21 16:03 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

This quick-reference guide enables instant, 3-minute submission of SolarDeck V1 to PCBWay for a parallel turnkey PCBA and Box-Build quotation.

---

## 1. Why Getting a Parallel PCBWay Quote is Recommended

1. **Competitive Pricing Leverage:** Benchmarking PCBWay against Seeed Studio Fusion eliminates supplier markups on high-value components (e.g. 10.3" E-Ink kit, CM5).
2. **Component Sourcing Reach:** PCBWay has deep supply-chain integration with Huaqiangbei spot markets and LCSC, often securing specialized parts (like the 10.3" Kaleido 4 panel once released) with zero minimum order quantities.
3. **Chassis Machining Strengths:** While Seeed excels at SLS PA12 3D printing, PCBWay is an industry leader in rapid **CNC 6061-T6 Aluminum Milling with Type III Hard Anodizing** for rugged unibody prototypes.

---

## 2. PCBWay Online Quoting Parameters

Navigate to [PCBWay.com > PCB Instant Quote](https://www.pcbway.com/orderonline.aspx) and configure:

### Step 1: Bare PCB Specifications
| Parameter | Value to Select | Notes |
| :--- | :--- | :--- |
| **Board Type** | Single Pieces | Dimensions: 222.0 × 160.0 mm |
| **Quantity** | 5 pcs (standard prototype minimum) | Yields best price break |
| **Layer Count** | **6 Layers** | |
| **Material** | FR-4 TG150 | Lead-free RoHS |
| **Thickness** | 1.6 mm | |
| **Surface Finish** | **ENIG (Immersion Gold)** | Mandatory for DF40 & QFN pads |
| **Copper Weight** | 1 oz outer / 0.5 oz inner | Standard |
| **Solder Mask** | Matte Black (or Blue) | |
| **Silkscreen** | White | |
| **Impedance Control**| Yes | 90 Ω USB differential, 100 Ω PCIe |

Upload: `hardware/production/solardeck_gerbers.zip`.

---

### Step 2: PCB Assembly (SMT Turnkey)
Select **"SMT Assembly" > "Turnkey" (PCBWay sources components)**:
* **Assembly Side:** Top side only (all active SMT components are on Top layer).
* **Unique Parts:** 20 unique items.
* **SMD Parts:** ~45 solder joints.
* **Upload BOM:** `hardware/production/solardeck_bom.csv` (contains exact LCSC Part Numbers for auto-quoting).
* **Upload Centroid (CPL):** `hardware/production/solardeck_cpl.csv`.
* **Placeholder warning:** the placeholder netlist and these CSVs still list pre-V1 parts (BQ25895, TPS63020, VL805,
  modem socket, eSIM, Nano-SIM slot). They are replaced by the first real schematic capture (ADR-034, AUDIT 6 X8),
  not edited by hand; quote them only as a process dry run.

---

### Step 3: Box-Build & Sourced Modules (RFQ Note)
In the order comments / RFQ special instructions box, paste the following note:

```text
Please quote full turnkey box-build sourcing and assembly for SolarDeck V1:
1. SMT Assembly of carrier board from uploaded Gerbers, BOM, and CPL.
2. Sourcing of 4 modular items (no cellular modem in V1, ADR-034):
   - Compute: Raspberry Pi CM5 (Model CM5116064: 16GB RAM, 64GB eMMC, Wi-Fi/BT — ADR-031)
   - Display: 10.3" Color E-Ink Kaleido 4 panel with Wacom EMR (E Ink part number TBD on release) + Kaleido 4 display controller (TBD, ADR-032)
   - Battery: 3.2V LiFePO4 pouch cell (capacity TBD until the cell is chosen, ADR-040) with 10k NTC thermistor (JST-PH 2.0)
   - Enclosure: CNC 6061-T6 Aluminum (or SLS PA12 Black) from attached solardeck_chassis.stl
3. Destination: DHL Express / FedEx Priority to Honolulu, Hawaii, USA.
```

Attach: `hardware/production/SEEED_FUSION_BOX_BUILD_INSTRUCTIONS.md` and `hardware/production/solardeck_chassis.stl`.
