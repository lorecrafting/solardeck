# Seeed Studio Fusion — Turnkey PCBA & Box-Build Assembly Instructions

**Project:** SolarDeck V1 Mobile Workstation  
**Target:** Seeed Fusion Turnkey PCBA + Box-Build Kitting & Functional Testing  
**Destination:** Honolulu, Hawaii, USA (via DHL Express / FedEx Priority)  
**Date:** 2026-10-19  

---

## 1. Scope of Work

Seeed Studio is requested to execute a complete **Turnkey Box-Build Assembly** comprising:
1. **6-Layer PCB Fabrication:** Manufacture the carrier board from `solardeck_gerbers.zip`.
2. **Turnkey SMT Assembly:** Source and solder all SMT components (Items 1–19 in `seeed_fusion_bom.csv`) using pick-and-place centroid data in `solardeck_cpl.csv`.
3. **Turnkey Module Sourcing (Box-Build):** Source the 5 module items (Raspberry Pi CM4, 10.3" E-Ink Display Kit, Quectel EG25-G, 8000mAh LiFePO4 battery, and SLS PA12 3D-printed enclosure).
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
* All PMICs (TI BQ25895, TPS62840, TPS61088, TPS63020, BQ25504).
* RP2350B co-processor, APS6404L PSRAM, W25Q128 Flash, DS3231 RTC.
* Hirose DF40C-100DS-0.4V CM4 dual sockets (J1, J2).
* TMUX1575PWR display bus multiplexer & FH12-40S-0.5SH FPC connector.
* VL805-Q6 PCIe USB Host, M.2 Key-M (NVMe), M.2 Key-B (Modem), ST4SIM eSIM, and Nano-SIM slot.

### Box-Build Sourced Modules (Items 20–24)
1. **Compute Module (Item 20):** Raspberry Pi CM4 (Model `CM4104000`: 4GB RAM, WiFi, Lite).
2. **Display Assembly (Item 21):** 10.3" Color E-Ink **Kaleido 4** Panel with Laminated **Wacom EMR Digitizer** (Model `ED103TC4-WACOM` or DKE / Good Display / Waveshare equivalent, 1872×1404, 40,000+ colors + IT8951 controller board + 40-pin FPC cable; Kaleido 3 fallback if Kaleido 4 lead time > 3 weeks).
3. **Cellular Modem (Item 22):** Quectel EG25-G (M.2 Key-B form factor, LTE Cat-4 Worldwide + GNSS).
4. **Battery Pack (Item 23):** 3.2V Nominal 8,000–10,000 mAh LiFePO4 pouch cell with 10k NTC thermistor and JST-PH 2.0 connector.
5. **Chassis Shell (Item 24):** 3D printed in **SLS PA12 Nylon (Black)** via Seeed Fusion 3D printing service using `solardeck_chassis.stl`.

---

## 4. Final Box-Build Assembly Procedure

1. **Install Heat-Set Inserts:**  
   Heat-press 4x M2.5 × 4.0 mm brass threaded inserts into the internal mounting bosses of the SLS PA12 chassis shell.
2. **Mate Compute Module:**  
   Align the Raspberry Pi CM4 onto Hirose sockets J1 and J2. Press firmly until both 100-pin connectors audibly snap into full engagement.
3. **Connect Display FPC:**  
   Insert the 40-pin ribbon cable from the 10.3" E-Ink panel into connector `J_EPDC` on the carrier board; lock the flip-actuator.
4. **Mount Carrier Board:**  
   Lower the assembled carrier board into the chassis cavity. Secure with 4x M2.5 × 6.0 mm Torx screws into the heat-set inserts.
5. **Install M.2 Cellular Modem:**  
   Insert the Quectel EG25-G into socket `J_MODEM` and tighten the M2.5 retention standoff screw.
6. **Connect Battery:**  
   Plug the LiFePO4 battery pack into the JST-PH battery header. Place the battery into the dedicated 140 × 95 mm cavity with pre-installed double-sided foam tape.
7. **Seal M.2 Service Hatch:**  
   Place the M.2 service hatch door over the rear cavity and secure with 4x M2.5 flush Torx screws.

---

## 5. Factory Functional Test Protocol (Pass/Fail)

Before packing, the Seeed quality technician must perform this 3-minute check:

1. **USB-PD Power & Charge Test:**  
   Connect a 20W USB-C PD power supply.  
   * **Pass:** Board power LEDs illuminate (`3V3_AON` and `5V_SYS` active). BQ25895 charge indicator turns on. Cell charges toward 3.65V cutoff.
2. **Boot & Display Initialization Test:**  
   Insert factory test MicroSD card containing the SolarDeck hardware test image.  
   * **Pass:** Within 5 seconds, the 10.3" E-Ink display initiates a waveform clear and renders the high-contrast factory diagnostic splash screen (showing CPU OK, RAM 4GB OK, RP2350 OK).
3. **Current Draw Verification:**  
   * Active idle power: $\le 3.5\text{ W}$.
   * Display update peak: $\le 5.5\text{ W}$.

---

## 6. Packaging & Honolulu Air Shipping

* **ESD Protection:** Wrap the assembled SolarDeck tablet in an anti-static bubble bag.
* **Drop Protection:** Pack in rigid corrugated shipping box with 25 mm high-density EPE foam surrounding all edges.
* **Aviation Regulatory Compliance:**  
  * Mark shipping carton with **UN3481** label: *"Lithium ion batteries contained in equipment"*.
  * Include Section II packing declaration (Watt-hour rating is ~26 Wh to ~32 Wh, well under the 100 Wh airline threshold).
* **Carrier & Destination:**  
  * Ship via **DHL Express International Priority** or **FedEx International Priority** direct to Honolulu, Hawaii, USA.
  * Transit time: 3–4 business days directly to Honolulu International Airport (HNL).
