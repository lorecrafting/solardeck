# Hardware Verification & Pre-Fabrication Workflow

Written 2026-10-19 08:45 UTC in the Pi harness by antigravity/gemini-3.8-flash

Revised 2026-10-21 16:03 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

---

## 1. Overview & Objective

To prevent costly silicon destruction, "painted-into-a-corner" dead-ends, and multi-week prototype delays, SolarDeck enforces a strict **5-Stage Pre-Fabrication Verification Ladder**. Every circuit block, firmware state transition, and mechanical dimension must pass verification in software simulation before sending files to Shenzhen for physical fabrication.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 5-STAGE PRE-FABRICATION VERIFICATION LADDER                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Stage 1: Static Netlist & Electrical Trap Audit (Automated Python Linter)  │
│   • Verifies back-powering isolation, pull-ups, power domains, and shorts.  │
│                                                                             │
│ Stage 2: SPICE Analog & Power Integrity Simulation (ngspice / LTspice)      │
│   • Simulates transient CM5 load steps, battery sag, and MPPT slew rates.   │
│                                                                             │
│ Stage 3: Virtual Firmware & Silicon Co-Simulation (Renode & QEMU)          │
│   • Runs RP2350 bare-metal C in Renode; boots CM5 Linux 6.6 LTS in QEMU.    │
│                                                                             │
│ Stage 4: 3D Mechanical Envelope & Collision Analysis (OpenSCAD / STEP)      │
│   • Checks Z-stackup clearances, port alignment, and cable bend radii.      │
│                                                                             │
│ Stage 5: Foundry DFM & Design Rule Check Sign-off (JLCPCB / PCBWay DRC)     │
│   • Validates copper clearance, annular rings, and solder mask dams.        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Static Netlist & Hardware Trap Audit

Before routing copper or ordering parts, the netlist is validated by `hardware/audit_hardware_traps.py` to intercept the 10 classic beginner and professional hardware traps. The placeholder netlist still lists
pre-V1 parts (modem rail, CHEM_SEL strap), so the auditor still checks them; both go with the first real
capture (ADR-034, AUDIT 6 X8). The table below states the V1 design:

| Trap # | Trap Name | Physics / Failure Mode | SolarDeck Hardware Safeguard | Automated Audit Rule |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Phantom Back-Powering** | Unpowered CM5 CPU receives 3.3V GPIO leakage via display bus, destroying internal ESD diodes. | **TI TMUX1575** SPDT switch with fail-safe $I_{\text{off}}$ circuit isolation. | Check display nets pass through TMUX isolation when CM5 is 0V. |
| **02** | **Floating Open-Drain Bus** | I2C SDA/SCL lines float without pull-up resistors, causing bus hangs. | Dedicated 4.7 kΩ pull-ups to `VDD_3V3_AON`. | Verify pull-up resistance paths exist on all open-drain nets. |
| **03** | **LTE Burst Brown-Out** | Deferred to V2 (ADR-034). | — | — |
| **04** | **LiFePO4 Over-Voltage** | Applying standard 4.2V Li-ion charge voltage causes thermal runaway in 3.2V LiFePO4 cells. | One chemistry, no strap (ADR-035): the **BQ25798** enable pin holds charging off until the RP2350 writes VREG = `battery.charge_limit_v`; a BQ29706-class protector backs it up. | Verify the charger enable net is driven by the RP2350 and defaults to charge-off. |
| **05** | **Power Rail Collision** | Accidentally tying 5.0V system rail to a 3.3V logic line. | Distinct power net naming (`VDD_5V_SYS`, `VDD_3V3_AON`). | Assert 0 ohm shorts do not exist between separate voltage codes. |
| **06** | **Floating Reset Pins** | Active-low RESET lines float and trigger random spurious resets. | Hardware 10 kΩ pull-ups to appropriate local rail. | Check all active-low `#RESET` pins have pull-ups or active drivers. |
| **07** | **Unbuffered ADC Clipping** | Solar panel Voc exceeds 3.3V ADC pin rating, burning co-processor ADC. | Resistor voltage divider (1/2 scaling) protecting RP2350 ADC0. | Check maximum Vin does not exceed $V_{\text{ref}} = 3.3\text{V}$. |
| **08** | **Net Netname Typo Island** | Slight spelling difference creates an un-driven floating net island. | Netlist parser flags single-node nets (`pin count == 1`). | Flag any net with only 1 connected node. |
| **09** | **Ground Loop Disconnect** | Separate analog and digital grounds without single-point star ground. | Unified low-impedance ground plane on Layers 2 and 5. | Assert all component grounds route to master `GND`. |
| **10** | **Reverse Battery Polarity** | Inserting LiFePO4 cell backward blows input buck PMIC. | Reverse-polarity protection on `VBAT` (part chosen at schematic capture with the protector, ADR-035). | Verify reverse battery protection present on `VBAT` input. |

---

## 3. Stage 2: SPICE Analog & Power Integrity Simulation

Using KiCad's integrated **ngspice** engine:
1. **Transient Load Step Test:**
   * Apply a simulated 0.1A $\rightarrow$ 2.5A pulse (10 µs rise time) to `VDD_5V_SYS`.
   * **Pass Criteria:** Voltage sag $\Delta V \le 150\text{ mV}$; rail settles within 200 µs without ringing.
2. **LiFePO4 Power-Fail Hold-Up Slew Rate:**
   * Simulate battery cutoff at 2.85V.
   * **Pass Criteria:** `VDD_3V3_AON` stays within 3.1V–3.3V for $\ge 150\text{ ms}$ under 20 mA RP2350 load, allowing emergency NVMe/eMMC cache sync.
3. **Solar Energy Harvester MPPT Tracking:**
   * Sweep light levels from 200 lux (cloudy room) to 80,000 lux (direct sun).
   * **Pass Criteria:** BQ25504 tracks optimal $V_{\text{mpp}} \approx 78\% V_{\text{oc}}$ and trickles current without oscillating.

---

## 4. Stage 3: Virtual Firmware & Silicon Co-Simulation

Test firmware logic on desktop before flashing target silicon:

```
[ Developer Terminal ]
       │
       ├─── Host Assert Tests (test_rp2350_sm, test_refreshd) ────> Instant Logic Verification (<50ms)
       │
       ├─── Renode Virtual Board (RP2350 Cortex-M33) ─────────────> Emulated I2C/SPI Bus & Inter-Brain UART
       │
       └─── QEMU ARM64 (Linux 6.6 LTS CM5) ───────────────────────> Mainline Kernel, Sway, & inkd Daemon
```

### 4.1 Native Host Assert-Based Tests
Compile C state machines directly with host GCC/Clang:
```bash
# RP2350 State Machine & Power Fail Cutoff
gcc -Wall -Wextra -I firmware/rp2350/include firmware/rp2350/src/solardeck_sm.c firmware/rp2350/test/test_rp2350_sm.c -o /tmp/test_sm && /tmp/test_sm

# eink-refreshd Anti-Ghosting Cadence Engine
gcc -Wall -Wextra -I src/daemons/eink-refreshd src/daemons/eink-refreshd/refreshd.c src/daemons/eink-refreshd/test_refreshd.c -o /tmp/test_rf && /tmp/test_rf
```

### 4.2 Renode Co-Simulation Configuration
SolarDeck uses Renode scripts (`.resc`) to model:
* Dual-core Cortex-M33 RP2350 target.
* Virtual BQ25798 I2C peripheral reporting battery millivolts.
* Virtual IT8951 SPI peripheral receiving display packets (bench stand-in model, ADR-025; the Kaleido 4 controller is TBD, ADR-032).
* GPIO wake triggers simulated via Renode monitor commands.

---

## 5. Stage 4: 3D Mechanical Clearance & Collision Analysis

To ensure internal electronics mate with the unibody chassis without mechanical pinching:
1. **Export STEP Models:**
   * Export `solardeck-carrier.step` from KiCad (including component 3D heights).
   * Export `solardeck_chassis.step` from OpenSCAD.
2. **Clearance Rules:**
   * **Component-to-Chassis Roof Clearance:** $\ge 0.8\text{ mm}$ (except thermal interface pads).
   * **Thermal Interface Contact:** CM5 SoC pedestal must compress thermal pad by exactly $0.3\text{ mm} \pm 0.1\text{ mm}$.
   * **Display FPC Bend Radius:** $\ge 1.5\text{ mm}$ minimum curvature radius to prevent conductor fatigue.
   * **Battery Pouch Swell Allowance:** $\ge 0.8\text{ mm}$ Z-clearance above LiFePO4 pouch cell to accommodate normal 3,000-cycle pouch swelling.
3. **Automated Verification:**
   ```bash
   python3 hardware/enclosure/verify_enclosure.py
   ```

---

## 6. Stage 5: Foundry DFM & Design Rule Check Sign-Off

Before uploading Gerbers to JLCPCB or PCBWay:
* **Trace Width / Spacing:** Minimum 0.127 mm (5 mil) signal, 0.40 mm for high-current power nets.
* **Annular Rings:** Minimum 0.13 mm annular ring on via drills.
* **BGA / QFN Solder Mask Dams:** Minimum 0.10 mm mask bridge between adjacent pads on the RP2350 QFN-80 and BQ25798 QFN to eliminate solder bridging.
* **Impedance Control:** JLC06161H-3313 stackup verified for 90 Ω USB differential pairs and 100 Ω PCIe Gen 2 lanes.

---

## 7. Pre-Fabrication Sign-Off Checklist

Before releasing purchase orders or fab files, all boxes must be checked:

- [x] **Trap Audit:** `hardware/audit_hardware_traps.py` passes with 0 errors and 0 single-node nets.
- [x] **KiCad Schematics:** All 5 hierarchical sheets structurally verified (`hardware/verify_schematics.py`).
- [x] **Firmware Logic:** RP2350 host tests pass (`test_rp2350_sm`); the wake time they check is a placeholder constant until Linux resume is measured (ADR-036).
- [x] **Cadence Daemon:** Anti-ghosting lockout and scrub verified (`test_refreshd`).
* [x] **Chassis Fit:** OpenSCAD envelope verified against `docs/spec_values.json` (232 × 170 × 14.0 mm, 12.5 mm cavity) by `verify_enclosure.py`.
- [ ] **Physical PCB Layout:** 6-layer routing completed and DRC clean.
- [ ] **BOM / CPL Alignment:** Turnkey Pick-and-Place centroid file matches BOM LCSC part numbers 1:1.
