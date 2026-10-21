# Seeed Studio Fusion — Turnkey PCBA & Box-Build Assembly Instructions

**Project:** SolarDeck V1 Mobile Workstation  
**Target:** Seeed Fusion Turnkey PCBA + Box-Build Kitting & Functional Testing  
**Destination:** Honolulu, Hawaii, USA (via DHL Express / FedEx Priority)  
**Date:** 2026-10-19  

Revised 2026-10-21 16:03 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

> **Placeholder artifacts.** The placeholder netlist, `seeed_fusion_bom.csv` and `solardeck_cpl.csv` still list
> pre-V1 parts (BQ25895, TPS63020, VL805, modem socket, eSIM, Nano-SIM slot). They are replaced by the first
> real schematic capture (ADR-034, AUDIT 6 X8), not edited by hand. This document states the V1 design.

---

## 1. Scope of Work

Seeed Studio is requested to execute a complete **Turnkey Box-Build Assembly** comprising:
1. **6-Layer PCB Fabrication:** Manufacture the carrier board from `solardeck_gerbers.zip`.
2. **Turnkey SMT Assembly:** Source and solder all SMT components (Items 1–19 in `seeed_fusion_bom.csv`) using pick-and-place centroid data in `solardeck_cpl.csv`.
3. **Turnkey Module Sourcing (Box-Build):** Source the 4 V1 module items (Raspberry Pi CM5, 10.3" Kaleido 4 display kit, LiFePO4 battery, and SLS PA12 3D-printed enclosure). The cellular modem (Item 22) is deferred to V2 (ADR-034).
4. **Final Mechanical & Electrical Integration (Box-Build):** Hand-assemble all modules into the chassis.
5. **Factory Functional Test:** Power on the unit, confirm charging, and verify E-Ink display initialization.
6. **Air Freight Logistics:** Package as UN3481 equipment and ship directly to Honolulu, Hawaii.

---

## 2. PCB Manufacturing Specifications

| Parameter | Specification | Notes |
| :--- | :--- | :--- |
| **Layer Count** | 6 Layers | Standard Seeed 6-layer 3313 / 7628 stackup |
| **Board Dimensions** | 222.0 mm × 160.0 mm | Corner radius: 4.0 mm |
| **Material / Base** | FR-4 Standard TG150 | Lead-free RoHS compliant |
| **Board Thickness** | 1.6 mm ± 10% | |
| **Surface Finish** | **ENIG (Immersion Gold)** | Required for fine-pitch Hirose DF40 & QFN-80 pads |
| **Copper Weight** | 1 oz outer / 0.5 oz inner | |
| **Solder Mask** | Matte Black (or Gloss Black) | Both sides |
| **Silkscreen** | White | Both sides |
| **Impedance Control** | Yes (Seeed 6-Layer Standard) | 90 Ω USB differential, 100 Ω PCIe lanes |

---

## 3. SMT & Box-Build Component Sourcing

Refer to `hardware/production/seeed_fusion_bom.csv` for exact manufacturer part numbers.

### SMT On-Board Components (Items 1–19)
* All PMICs: TI BQ25798 charger, BQ29706-class protector + back-to-back N-FET pair, BQ27Z561-R2 gauge (ADR-035), TPS62840, TPS61088, BQ25504.
* RP2350B co-processor, APS6404L PSRAM, W25Q128 Flash, DS3231 RTC.
* Hirose DF40C-100DS-0.4V CM5 dual sockets (J1, J2).
* TMUX1575YCJR (DSBGA-16, ×2) display bus multiplexer (the production CSV still lists a non-existent PWR/TSSOP part — AUDIT 6 §5) & display FPC connector (TBD with the Kaleido 4, ADR-032).
* M.2 NVMe socket on the CM5 PCIe lane; no external USB host controller (CM5 native USB 3, ADR-042).
* u-blox MAX-M10S GNSS on an RP2350 UART behind a load switch, passive antenna at the top edge (ADR-038).
* Modem socket, eSIM and Nano-SIM slot: deferred to V2 (ADR-034); the V2 eSIM requirement is a consumer SGP.22 eUICC (ADR-033).

### Box-Build Sourced Modules (Items 20–24)
1. **Compute Module (Item 20):** Raspberry Pi CM5 (Model `CM5116064`: 16GB RAM, 64GB eMMC, Wi-Fi/BT — ADR-031).
2. **Display Assembly (Item 21):** 10.3" Color E-Ink **Kaleido 4** Panel with Laminated **Wacom EMR Digitizer** (E Ink sole source; part number, resolution and FPC TBD on release, ADR-032) + the Kaleido 4 display controller (TBD, ADR-032). No substitute panel: V1 waits for Kaleido 4 (ADR-032).
3. **Cellular Modem (Item 22):** Deferred to V2 (ADR-034).
4. **Battery Pack (Item 23):** 3.2V nominal LiFePO4 pouch cell (capacity TBD until the cell is chosen, ADR-040) with 10k NTC thermistor and JST-PH 2.0 connector.
5. **Chassis Shell (Item 24):** 3D printed in **SLS PA12 Nylon (Black)** via Seeed Fusion 3D printing service using `solardeck_chassis.stl`.

---

## 4. Final Box-Build Assembly Procedure

1. **Install Heat-Set Inserts:**  
   Heat-press 4x M2.5 × 4.0 mm brass threaded inserts into the internal mounting bosses of the SLS PA12 chassis shell.
2. **Mate Compute Module:**  
   Align the Raspberry Pi CM5 onto Hirose sockets J1 and J2. Press firmly until both 100-pin connectors audibly snap into full engagement.
3. **Connect Display FPC:**  
   Insert the ribbon cable from the 10.3" Kaleido 4 panel into connector `J_EPDC` on the carrier board; lock the flip-actuator.
4. **Mount Carrier Board:**  
   Lower the assembled carrier board into the chassis cavity. Secure with 4x M2.5 × 6.0 mm Torx screws into the heat-set inserts.
5. **Install M.2 Cellular Modem:**  
   Deferred to V2 (ADR-034).
6. **Connect Battery:**  
   Plug the LiFePO4 battery pack into the JST-PH battery header. Place the battery into the dedicated 140 × 95 mm cavity with pre-installed double-sided foam tape.
7. **Seal M.2 Service Hatch:**  
   Place the M.2 service hatch door over the rear cavity and secure with 4x M2.5 flush Torx screws.

---

## 5. Factory Functional Test Protocol (Pass/Fail)

Before packing, the Seeed quality technician must perform this 3-minute check:

1. **USB-PD Power & Charge Test:**  
   Connect a 20W USB-C PD power supply.  
   * **Pass:** Board power LEDs illuminate (`3V3_AON` and `5V_SYS` active). Charging stays off until the RP2350 test firmware has written the BQ25798 VREG to `battery.charge_limit_v` (enable pin held off, ADR-035); then the charge indicator turns on and the cell charges toward that limit. **Fail** if charge current flows before VREG is written.
2. **Boot & Display Initialization Test:**  
   Boot the SolarDeck hardware test image from the CM5 eMMC (flashed over USB with `rpiboot`/usbboot — TBD, verify CM5 procedure).  
   * **Pass:** Within 5 seconds, the 10.3" E-Ink display initiates a waveform clear and renders the high-contrast factory diagnostic splash screen (showing CPU OK, RAM 16GB OK, RP2350 OK).
3. **Current Draw Verification:**  
   * Active idle power: $\le 3.5\text{ W}$.
   * Display update peak: $\le 5.5\text{ W}$.

---

## 6. Packaging & Honolulu Air Shipping

* **ESD Protection:** Wrap the assembled SolarDeck tablet in an anti-static bubble bag.
* **Drop Protection:** Pack in rigid corrugated shipping box with 25 mm high-density EPE foam surrounding all edges.
* **Aviation Regulatory Compliance:**  
  * Mark shipping carton with **UN3481** label: *"Lithium ion batteries contained in equipment"*.
  * Include Section II packing declaration (Watt-hour rating TBD until the cell is chosen, ADR-040; state the chosen cell's datasheet figure, which must be under the 100 Wh airline threshold).
* **Carrier & Destination:**  
  * Ship via **DHL Express International Priority** or **FedEx International Priority** direct to Honolulu, Hawaii, USA.
  * Transit time: 3–4 business days directly to Honolulu International Airport (HNL).
