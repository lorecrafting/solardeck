# EVT-0 Power Board — capture package

Written 2026-10-21 19:12 UTC in Claude Code by anthropic/claude-opus-5-5 (EVT-0 power board, ADR-043).

**Status: capture spec only. No schematic, layout or netlist exists for this board.** Every pin
assignment below comes from a datasheet that was open when it was written (Appendix A lists them
with revisions). A value that no open datasheet supports is written **TBD** with what unlocks it.
Values that depend on the cell are in §4, never in the pin tables. Change class: C2 DESIGN (plus C1
for the new `charger` and `harvester` keys in `spec_values.json`).

---

## 1. Purpose

ADR-043 build order step 2: the power tree on its own board, before the RP2350 minimum system and
the CM5 carrier, because power carries the safety risk and does not wait on the panel. The
co-processor is an external Raspberry Pi Pico 2 on a header (§2.11).

**EVT-0 proves (on the bench, as `measured <date>` entries):**

- the charger stays off until the RP2350 has written and read back VREG = `battery.charge_limit_v`
  (ADR-035), including at first VBUS with no firmware running;
- the register sequence in §3 (watchdog off, VREG, read-back, CE release, re-check);
- the TS/NTC cutoff suspends charging outside the window (AGENTS §4.1: verify before any charge);
- the BQ29706 trips at its OVP/UVP/OCD/OCC/SCD thresholds with the chosen FETs (bench supply in place of the cell);
- the gauge answers on the always-on bus and reads cell voltage and current;
- the PD sink negotiates a contract inside the BQ25798 input range, and presents Rd at 0 V
  (`USB_ROBUSTNESS.md` R2);
- the always-on rail, the 5 V boost under a dummy load, the load switches' off-state leakage, and the
  battery-side floor of the power tree with every switched load off (the power-tree part of G12);
- the harvester stops at its VBAT_OV threshold below the charge limit.

**EVT-0 does not prove:** CM5 behaviour (the 5 V rail drives an electronic load), gauge accuracy
(needs the chemistry ID and a learning cycle on the chosen cell, ADR-040), runtime or pack capacity,
thermal behaviour in the enclosure, EMI/ESD, the carrier layout, the full-device sleep floor, or
anything about the panel.

### 1.1 Block diagram

```
 USB-C sink --VBUS_IN--+-- PD sink (CC1/CC2; §5)
                       |
                       v
                +-------------+  VSYS   +----------+ VDD_3V3_AON
                |  BQ25798    |---+---->| TPS62840 |---+--> AON pull-ups,
                |  charger    |   |     |  buck    |   |    INA3221, header
                |  I2C 0x6B   |   |     +----------+   +--TPS22918--> 3V3_GNSS
                +-------------+   |     +----------+
                   BAT |          +---->| TPS61088 |-5V_SYS-+--> dummy load
                       |                |  boost   |        +-TPS22918-> 5V_LOAD
  bezel strip          |                +----------+
  -> BQ25504 -VBAT---->+ PACK_P
                       |
                    [fuse]
                       |
                    CELL_P ---- BQ27Z561 BAT / BAT_SNS ; BQ29706 BAT
                    LiFePO4 cell
                    GND_CELL -- R_SENSE -- N_SNS -- Q_DSG -- Q_CHG -- GND
                               (gauge)             (BQ29706 DOUT/COUT)
```

### 1.2 Topology decisions in this package (owner to confirm)

1. **The always-on buck and the 5 V boost run from the charger's `SYS` (VSYS), not from the cell.**
   VSYS exists whenever VBUS is present, even with a tripped or flat cell, so the CE pull-up rail
   and the RP2350 are up before charging can start. HARDWARE_SPEC §2.3 says the AON rail is "powered
   directly from VBAT"; this package diverges deliberately (open item 1).
2. **Protector FETs are low-side** (BQ29706 drives low-side N-FETs, datasheet §9.1, Fig. 9-1).
   The gauge's sense resistor sits on the cell side of the FETs and the gauge's VSS is `GND_CELL`,
   so the gauge stays powered when the protector opens. TI's gauge example (BQ27Z561 Fig. 7-1) uses
   high-side FETs, so two things are **open before capture** (§8): (a) moving the sense resistor to
   the low side inverts the current sign relative to Fig. 7-1, so the SRP/SRN orientation must be
   re-derived from the TRM's sign convention and confirmed on the first charge at bring-up; (b) with
   the gauge's VSS on `GND_CELL` and its I²C pulled up to an AON rail referenced to board `GND`, the
   two grounds separate when the protector opens, which can push the gauge's I²C pins outside their
   absolute-maximum range. Resolve (b) by moving the protector FETs or the gauge so both share one
   ground, or by isolating its I²C; do not capture this topology as drawn.
3. **No input OR-ing on EVT-0.** One USB-C sink receptacle feeds VBUS; VAC1/VAC2 tie to VBUS and
   ACDRV1/2 to GND (BQ25798 pin table). The BQ25798 has its own two-input mux (§7.3.5) which the
   carrier may use instead of the BOM's LM66100 pair (open item 9).

---

## 2. Pin-level connections

Net names follow `PIN_BUDGET.md` where a net exists there. Local nets: `VBUS_IN`, `PMID`, `VSYS`,
`REGN`, `PACK_P`, `CELL_P`, `GND_CELL`, `N_SNS`, `VDD_3V3_AON`, `5V_SYS`, `3V3_GNSS`, `5V_LOAD`,
`SOLAR_IN`, `PD_ALERT_N`, `LOAD5_EN`, `CHG_STAT`. `GND` is the board ground (PACK−).
"Design value" marks a passive chosen here, not taken from a datasheet.

### 2.1 U1 — BQ25798 charger (RQM, VQFN-29)

Source: SLUSDV2C Table 5-1 (pins), §7.3.2 (PROG), §7.3.4.3 (ILIM_HIZ), §8.2.2 (L, C).

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | STAT | `CHG_STAT` | 10 kΩ pull-up to `VDD_3V3_AON` (open drain; not REGN, which is about 5 V and would drive the RP2350/Pico pin above its rail); test point |
| 2, 3 | VBUS | `VBUS_IN` | 2 × 10 µF + 0.1 µF, the 0.1 µF closest to the pins; rated ≥ 25 V (§8.2.2.3) |
| 4 | BTST1 | — | 47 nF, ≥ 10 V, BTST1 to SW1 |
| 5 | REGN | `REGN` | 4.7 µF, 10 V, to GND. Feeds only STAT, TS and ILIM_HIZ dividers (§7.3.4.1) |
| 6 | D+ | `USB_DP` | receptacle D+ (A6/B6). See §5 for CH224K sharing |
| 7 | D− | `USB_DM` | receptacle D− (A7/B7) |
| 8 | VAC2 | `VBUS_IN` | no ACFET2/RBFET2 fitted (pin table) |
| 9 | VAC1 | `VBUS_IN` | no ACFET1/RBFET1 fitted (pin table) |
| 10 | ACDRV2 | `GND` | pin table: tie to GND if no FETs |
| 11 | ACDRV1 | `GND` | pin table: tie to GND if no FETs |
| 12 | QON | test point | internal pull-up (RQON, §6.5); pad to GND for a manual ship-exit/reset button, DNP |
| 13 | CE | `CHG_CE_N` | **10 kΩ pull-up to `VDD_3V3_AON`** (design value, §3); to header |
| 14 | SCL | `I2C_AON_SCL` | bus pull-up §2.12 |
| 15 | SDA | `I2C_AON_SDA` | bus pull-up §2.12 |
| 16 | TS | `CHG_TS` | RT1 from `REGN`, RT2 to GND, NTC1 (at the cell) to GND. Values: §4 |
| 17 | ILIM_HIZ | `CHG_ILIM` | divider from `REGN`: 30.9 kΩ top, 22.6 kΩ bottom (design value, below) |
| 18 | BATP | `PACK_P` | through 100 Ω series (pin table) |
| 19 | BTST2 | — | 47 nF, ≥ 10 V, BTST2 to SW2 |
| 20 | PROG | — | 4.7 kΩ ±1 % to GND: 1s, 750 kHz (Table 7-1) |
| 21 | INT | `CHG_INT_N` | 10 kΩ pull-up to `VDD_3V3_AON`, not REGN (§7.3.4.1); to header |
| 22, 23 | BAT | `PACK_P` | 2 × 10 µF (pin table) |
| 24 | SDRV | — | 1 nF, 50 V, 0402 to GND; **no ship FET** (`charger.ship_fet`, §3.1) |
| 25 | SYS | `VSYS` | 5 × 10 µF + 0.1 µF, the 0.1 µF closest to the pin |
| 26 | SW2 | L1 pin 2 | — |
| 27 | GND | `GND` | — |
| 28 | SW1 | L1 pin 1 | — |
| 29 | PMID | `PMID` | 3 × 10 µF + 0.1 µF; no backup mode, so no POSCAPs; rated ≥ 25 V (§8.2.2.3) |

- **L1 = 2.2 µH.** The 750 kHz PROG setting only works with 2.2 µH (§8.2.2.2); the 1.5 MHz setting
  (PROG 3.0 kΩ) needs 1 µH instead. Saturation current: §4.
- **ILIM_HIZ clamp.** V(ILIM_HIZ) = 1 V + 0.8 Ω × ILIM (§7.3.4.3, Eq. 1). The clamp is set to the
  PD sink's programmed PDO current so the charger can never draw more than the contract allows,
  firmware or not. With the STUSB4500 default sink PDO current of 1.5 A (DS12499 Table 16) and REGN
  between 4.8 V and 5.2 V (§6.5, REGN at 20 mA), the 30.9 k / 22.6 k divider gives ILIM between
  1.29 A and 1.50 A (modelled). Recompute if the PDO current changes (§5).

### 2.2 U2 — BQ29706 protector (DSE, WSON-6) and Q1/Q2

Source: SLUSBU9I Table 5-1, §5.1, §9.2 (Fig. 9-1), §9.2.2. Thresholds of the BQ29706 variant are in
its Device Comparison Table (§4) and are fixed at the factory.

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | NC | — | no connection (electrically open) |
| 2 | COUT | Q_CHG gate | optional 5 MΩ gate–source (§9.2.2), footprint fitted |
| 3 | DOUT | Q_DSG gate | optional 5 MΩ gate–source (§9.2.2), footprint fitted |
| 4 | VSS | `GND_CELL` | cell negative reference (§5.1.2) |
| 5 | BAT | `CELL_P` | 330 Ω series from CELL_P, 0.1 µF BAT to VSS, close to the pin (§9.2.2, §9.4.1) |
| 6 | V− | `GND` | through 2.2 kΩ to PACK− (§5.1.3) |

- **Q_DSG, Q_CHG:** two N-FETs, drains common, Q_DSG source on `N_SNS`, Q_CHG source on `GND`
  (Fig. 9-1). Part TBD (§4): R_DS(on) must be specified at a gate drive no higher than the cell's
  UVP-region voltage, because COUT/DOUT swing only to BAT (§6.5 VOH).
- **Placement:** keep the two FETs adjacent; their junction trace is part of the sense path
  (§9.4.1 item 2).

### 2.3 U3 — BQ27Z561-R2 gauge (WCSP-12)

Source: SLUSCY0C Table 4-1, §6.3.2.6, §7.2 (Fig. 7-1), §7.4.1. The SLUSCY0C datasheet does not give
the I²C address; it is in the Technical Reference Manual, which is not in hand (§6).

| Ball | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| A1 | INT | `GAUGE_INT` | output type not stated in SLUSCY0C; 10 kΩ pull-up to `VDD_3V3_AON` footprint, DNP until the TRM says open-drain |
| A2 | PULS | — | not used, no connection |
| A3 | SDA/HDQ | `I2C_AON_SDA` | never switch to HDQ: the change is irreversible (§6.3.4) |
| B1 | TS | NTC2 to `GND_CELL` | 10 kΩ NTC (103AT class) at the cell; internal 18 kΩ pull-up (§6.3.2.6) |
| B2 | VSS | `GND_CELL` | — |
| B3 | SCL | `I2C_AON_SCL` | — |
| C1 | SRN | `N_SNS` | through 100 Ω; Kelvin at R_SENSE |
| C2 | BAT_SNS | `CELL_P` | Kelvin to the cell positive, no current (§6.3.3) |
| C3 | NU | — | no connection |
| D1 | SRP | `GND_CELL` | through 100 Ω; Kelvin at R_SENSE. 0.1 µF from SRP to SRN on the gauge side |
| D2 | BAT | `CELL_P` | 1 µF to VSS, close to the gauge |
| D3 | CE | `CELL_P` | active high; tied on (Fig. 7-1 allows CPU control; not needed on EVT-0) |

- **R_SENSE** between `GND_CELL` and `N_SNS`: 1–3 mΩ, ≤ 50 ppm/°C (§7.4.1). Value: §4.

### 2.4 U4 — USB-PD sink (part undecided, §5)

Footprints for **one** of the two; the recommendation is the STUSB4500.

**Option A — STUSB4500 (QFN-24).** Source: DS12499 Rev 4 Table 1, §2.2, §3.5, Fig. 9.

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | CC1DB | CC1 | dead-battery Rd on CC1 (§2.2.2, §3.5) |
| 2 | CC1 | receptacle A5 | TVS per Fig. 9 (ESDA25W class) |
| 3 | NC | — | floating |
| 4 | CC2 | receptacle B5 | TVS per Fig. 9 |
| 5 | CC2DB | CC2 | dead-battery Rd on CC2 |
| 6 | RESET | — | 100 kΩ to GND (Fig. 9); test point |
| 7 | SCL | `I2C_AON_SCL` | through a 0 Ω link, DNP-able (open item 6) |
| 8 | SDA | `I2C_AON_SDA` | through a 0 Ω link, DNP-able |
| 9 | DISCH | `VBUS_IN` | through 1 kΩ (Fig. 9, R2) |
| 10 | GND | `GND` | — |
| 11 | ATTACH | test point | open drain, unused on EVT-0 |
| 12 | ADDR0 | — | 100 kΩ to GND (Fig. 9) → address 0x28 (§4.1) |
| 13 | ADDR1 | — | 100 kΩ to GND (Fig. 9) |
| 14 | POWER_OK3 | test point | open drain, unused |
| 15 | GPIO | test point | open drain, unused |
| 16 | VBUS_EN_SNK | test point | no sink PMOS on EVT-0; 100 kΩ pull-up to `VBUS_IN` (as Fig. 9 R10) |
| 17 | A_B_SIDE | test point | open drain, unused |
| 18 | VBUS_VS_DISCH | `VBUS_IN` | through 1 kΩ (Fig. 9, R4) |
| 19 | ALERT | `PD_ALERT_N` | 10 kΩ pull-up to `VDD_3V3_AON` behind the same 0 Ω links; to header |
| 20 | POWER_OK2 | test point | high-voltage open drain, unused |
| 21 | VREG_1V2 | — | 1 µF to GND |
| 22 | VSYS | `GND` | powered from VDD only, so no battery drain (§6.1.1) |
| 23 | VREG_2V7 | — | 1 µF to GND |
| 24 | VDD | `VBUS_IN` | 1 µF to GND (Fig. 9) |
| EP | EP | `GND` | — |

`VBUS_IN` at the receptacle: 4.7 µF and a VBUS TVS (Fig. 9, C50 and ESDA25P35 class). There is no
sink-path PMOS: VBUS goes straight to the BQ25798, whose input range covers every STUSB4500 PDO.

**Option B — CH224K (ESSOP-10).** Source: WCH CH224 datasheet V2.0, Table 4-2, §6.2.

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 0 | GND (EPAD) | `GND` | — |
| 1 | VDD | — | 1 kΩ from `VBUS_IN`, 1 µF to GND (shunt regulator, §8.2.3) |
| 2 | CFG2 | strap | level per the §6.2 table |
| 3 | CFG3 | strap | level per the §6.2 table |
| 4 | DP | `USB_DP` | shared with BQ25798 D+ (open item 7) |
| 5 | DM | `USB_DM` | shared with BQ25798 D− |
| 6 | CC2 | receptacle B5 | — |
| 7 | CC1 | receptacle A5 | — |
| 8 | VBUS | — | 10 kΩ from `VBUS_IN` (§6.2) |
| 9 | CFG1 | strap | 10 kΩ to VBUS for 5 V-only, else per the §6.2 table |
| 10 | PG | test point | open drain, active low |

### 2.5 U5 — TPS62840DLC always-on buck (SON-8)

Source: SLVSEC6D Pin Functions, Table 1 (VSET), §8.4.3, Table 2, §9.2.2.

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | GND | `GND` | — |
| 2 | VIN | `VSYS` via J_IAON | 4.7 µF required (pin table) |
| 3 | MODE | `GND` | power-save (pin table: must be terminated) |
| 4 | EN | `VSYS` | always on |
| 5 | VSET | — | 267 kΩ E96 to GND = 3.3 V on the TPS62840 (Table 1); < 100 pF on the node (§8.3.4). See open item 2 |
| 6 | STOP | `GND` | — |
| 7 | SW | L2 | L2 = 2.2 µH (Table 3); saturation current ≥ the high-side current limit ILIMF (§9.2.2.1, §7.5) |
| 8 | VOS | `VDD_3V3_AON` | at the output capacitor; CO = 10 µF (Table 3) |

The orderable part is **TPS62840DLCR** (orderable addendum). It is a step-down converter: below
VOUT plus the drop VINmin = VOUT + IOUT × (RDS(on) + RL) (§8.4.3) it runs at 100 % duty and the rail
follows VSYS.

### 2.6 U6 — TPS61088 5 V boost (RHL, VQFN-20)

The TPS61088 datasheet (SLVSCM8D) could not be downloaded: ti.com returns 404 for the product page
and the PDF. Pins and values below come from the EVM user's guide **SLVUAF2** (Fig. 7 schematic,
Table 2, Table 3 BOM, Eq. 1–2). Everything the EVM guide does not cover is TBD.

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | VCC | — | 4.7 µF to AGND (C14) |
| 2 | EN | `EN_5V_SYS` | 100 kΩ to GND (design value) so the rail is off while the host is in reset |
| 3 | FSW | — | R_FSW **TBD**: the frequency equation is in SLVSCM8D, not in hand. The EVM's 255 kΩ is for its 3.3 V → 9 V point |
| 4–7 | SW | L3 | L3 = 1.2 µH, ≥ 12.9 A rated (EVM: CDMC8D28NP-1R2MC) |
| 8 | BOOT | — | 0.1 µF BOOT to SW (C1) |
| 9 | VIN | `VSYS` | 0.1 µF at the pin (C16); 2 × 22 µF at L3's input (C9, C10) |
| 10 | SS | — | 47 nF (C15) |
| 11, 12 | NC | `GND` | tied to ground as on the EVM |
| 13 | MODE | — | floating = PFM (SLVUAF2 §2.1); 0 Ω to GND footprint, DNP, for PWM |
| 14–16 | VOUT | `5V_SYS` | 4 × 22 µF + 1 µF (C3–C7) |
| 17 | FB | — | 357 kΩ VOUT→FB, 115 kΩ FB→AGND: 5 V in PFM (SLVUAF2 Table 2) |
| 18 | COMP | — | R_C/C_C **TBD**: the EVM's 17.4 kΩ + 4.7 nF compensate its 9 V output |
| 19 | ILIM | — | R_ILIM **TBD**: ILIM = 1 190 000 / R (PFM), worst case 1.3 A lower (SLVUAF2 Eq. 2); sized when the CM5 peak load is known |
| 20 | AGND | `GND` | — |
| 21 | PGND | `GND` | with the thermal pad |

### 2.7 U7 — BQ25504 bezel harvester (RGT, VQFN-16)

Source: SLUSAH0G Table 6-1, §8.3.2–8.3.3, §9.1, §9.2.1. The resistor sums are 10 MΩ (OV, UV) and
20 MΩ (MPPT) per the recommended operating conditions.

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | VSS | `GND` | thermal pad |
| 2 | VIN_DC | `SOLAR_IN` | ≥ 4.7 µF to pin 1 |
| 3 | VOC_SAMP | — | ROC2 4.42 MΩ from VIN_DC, ROC1 15.6 MΩ to GND: MPP at 78 % of VOC (§9.2.1.2) |
| 4 | VREF_SAMP | — | 10 nF low-leakage to GND (CREF) |
| 5 | OT_PROG | `GND` | lower over-temperature setting (pin table: 60 °C; §7.5 TSD_PROTL: 65 °C) |
| 6 | VBAT_OV | — | ROV1 = `harvester.rov1_mohm` to GND, ROV2 = `harvester.rov2_mohm` to VRDIV, 0.1 % |
| 7 | VRDIV | — | top of the OV and UV dividers |
| 8 | VBAT_UV | — | RUV1 5.60 MΩ to GND, RUV2 4.42 MΩ to VRDIV (§9.2.1.2) |
| 9 | OK_HYST | `GND` | VBAT_OK not used (pin table) |
| 10 | OK_PROG | `GND` | VBAT_OK not used (pin table) |
| 11 | VBAT_OK | — | floating (pin table) |
| 12 | AVSS | `GND` | thermal pad |
| 13 | VSS | `GND` | thermal pad |
| 14 | VBAT | `PACK_P` | the cell is the storage element |
| 15 | VSTOR | — | ≥ 4.7 µF ∥ 0.1 µF to pin 1 |
| 16 | LBST | L4 | L4 = 22 µH, > 300 mA peak (§9.1.2) |

**VBAT_OV is a charge limit.** The harvester charges the cell without the CE gate, so its OV
threshold must stay below `battery.charge_limit_v` at its worst-case accuracy:
VBAT_OV = 3/2 × VBIAS × (1 + ROV2/ROV1) (Eq. 3) gives `harvester.vbat_ov_v`, and
`harvester.vbat_ov_v` × (1 + `harvester.threshold_accuracy_pct`) ≤ `battery.charge_limit_v`.
Phase 14 checks both. VIN_DC operates from 130 mV to 3.0 V after cold start (§7.5 VIN(DC)): the
bezel strip's open-circuit voltage must stay inside that (open item 11).

### 2.8 U8, U9 — TPS22918 load switches (DBV, SOT-23-6)

Source: SLVSD76C Pin Functions, §6.3, §8.3.2. One per input rail type; the carrier repeats them.

| Pin | Name | U8 (GNSS) | U9 (5 V load) | Notes |
| :-- | :-- | :-- | :-- | :-- |
| 1 | VIN | `VDD_3V3_AON` | `5V_SYS` | 1 µF (§6.3 CIN) |
| 2 | GND | `GND` | `GND` | — |
| 3 | ON | `GNSS_EN` | `LOAD5_EN` | 100 kΩ to GND (design value; never floating, pin table) |
| 4 | CT | — | — | floating = fastest slew (pin table); 0402 footprint, DNP |
| 5 | QOD | `3V3_GNSS` | `5V_LOAD` | tied to VOUT: internal RPD discharges the rail when off |
| 6 | VOUT | `3V3_GNSS` | `5V_LOAD` | load test points |

### 2.9 U10 — INA3221 rail monitor (RGV, VQFN-16)

Source: SBOS576C Table 5-1, Table 7-1, §7.3.2.3 (PV), §9.2 (supply bypass).

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | IN−3 | `3V3_GNSS` load side of RS3 | — |
| 2 | IN+3 | U8 output side of RS3 | — |
| 3 | GND | `GND` | — |
| 4 | VS | `VDD_3V3_AON` | 0.1 µF close to the pin |
| 5 | A0 | `GND` | address 0x40 (Table 7-1) |
| 6 | SCL | `I2C_AON_SCL` | — |
| 7 | SDA | `I2C_AON_SDA` | — |
| 8 | Warning | `SENSOR_ALERT_N` | open drain, wired-OR (PIN_BUDGET EXP 8); 10 kΩ pull-up to `VDD_3V3_AON` |
| 9 | Critical | `SENSOR_ALERT_N` | open drain, wired-OR |
| 10 | PV | — | unused, no connection |
| 11 | IN−1 | `5V_SYS` load side of RS1 | — |
| 12 | IN+1 | U6 output side of RS1 | — |
| 13 | TC | — | unused, no connection |
| 14 | IN−2 | `VDD_3V3_AON` load side of RS2 | — |
| 15 | IN+2 | U5 output side of RS2 | — |
| 16 | VPU | `VDD_3V3_AON` | as Fig. 7-2 |
| pad | — | `GND` | — |

Shunts RS1–RS3: R ≤ 163.8 mV / I_max of the rail (full-scale, §8.2.2); values **TBD** with
each rail's maximum current (CM5 peak is TBD, HARDWARE_SPEC §2.3). The µA-level sleep floor is
measured with a DMM at J_IBAT/J_IAON, not with the INA3221.

### 2.10 Battery connector, fuse and NTCs

| Ref | Connects | Notes |
| :-- | :-- | :-- |
| J_CELL | `CELL_P`, `GND_CELL`, NTC1 (2 wires), NTC2 (2 wires) | locking, keyed; two thermistors at the cell, one per IC (charger TS to GND, gauge TS to GND_CELL) |
| F1 | `CELL_P` → `PACK_P` | rating TBD (§4) |
| J_IBAT | in series with F1 | 2-pin jumper; open = DMM in series for the battery-side floor |
| J_IAON | `VSYS` → U5 VIN | 2-pin jumper for the AON rail current |

### 2.11 J_HOST — header to the external RP2350 (Pico 2), 2 × 8, 2.54 mm

The nets are the carrier's (PIN_BUDGET). The Pico 2 carries the RP2350A, not the RP2350B, and
does not expose every PIN_BUDGET GPIO (verify against the Pico 2 datasheet, not in hand), so the
Pico-side GPIO numbers are a bring-up wiring choice; PIN_BUDGET applies to the carrier.

| Pin | Net | Pin | Net |
| :-- | :-- | :-- | :-- |
| 1 | `GND` | 2 | `VDD_3V3_AON` (reference only; do not feed the Pico's 3V3 into it) |
| 3 | `I2C_AON_SDA` | 4 | `I2C_AON_SCL` |
| 5 | `CHG_CE_N` | 6 | `CHG_INT_N` |
| 7 | `GAUGE_INT` | 8 | `SENSOR_ALERT_N` |
| 9 | `EN_5V_SYS` | 10 | `GNSS_EN` |
| 11 | `PD_ALERT_N` | 12 | `LOAD5_EN` |
| 13 | `SOLAR_ADC` | 14 | `CHG_STAT` |
| 15 | `GND` | 16 | `GND` |

`SOLAR_ADC`: from `SOLAR_IN` through a divider footprint, values TBD with the strip (open item 11).
On the carrier, `CHG_INT_N`, `GAUGE_INT`, `GNSS_EN` and `SENSOR_ALERT_N` go to the GPIO expander
(PIN_BUDGET §4); EVT-0 brings them straight out.

### 2.12 Always-on I²C bus

One pair of 10 kΩ pull-ups to `VDD_3V3_AON` (BQ25798 pin table value) for SCL and SDA. The bus runs
at 100 kHz (HARDWARE_SPEC §2.9); every device here allows 400 kHz.

---

## 3. Charger hold-off (ADR-035)

### 3.1 Hardware

- `CHG_CE_N` has a 10 kΩ pull-up to `VDD_3V3_AON`. Charging needs CE low **and** EN_CHG = 1
  (pin table); EN_CHG resets to 1, so CE is the only gate at power-up. CE must never float
  (pin table); VIH_CE ≥ 1.3 V, VIL_CE ≤ 0.4 V (§6.5).
- While the RP2350 is in reset its pad pull-down fights the 10 kΩ. CE stays high while
  V_AON × R_pd / (R_pd + 10 kΩ) ≥ 1.3 V, which needs R_pd ≥ 6.5 kΩ at a 3.3 V rail and more as the
  rail falls in 100 % mode (§2.5). Verify against the RP2350 pad pull-down (datasheet not in hand).
- **No ship FET.** VBAT_UVLOZ (the battery voltage at which I²C comes alive with no VBUS) is
  3.25–3.55 V with a ship FET and 2.50–2.71 V without (§6.5). With a ship FET the RP2350 could not
  reach the charger on a LiFePO4 cell sitting on its plateau (`charger.ship_fet`).
- **Known gap (open item 3):** with a flat or tripped cell, `VDD_3V3_AON` only rises after the
  charger starts switching into SYS, so CE reads low for that interval. Measure it at EVT-0
  (§7, step 4).

### 3.2 Register sequence (I²C 0x6B, SLUSDV2C §7.5)

16-bit registers are written MSB first at the lower offset (Fig. 7-27 shows bits 15:8 first; confirm
with the read-back in step 6). Read-modify-write every register that holds other fields.

| Step | Register | Field | Value | Why |
| :-- | :-- | :-- | :-- | :-- |
| 0 | — | — | wait for I²C | registers are accessible about 20 ms after VBAT or VBUS is valid (§7.3.3, §7.3.4) |
| 1 | REG48 (0x48) | PN_2:0 | must read 011b | it is a BQ25798 (Table 7-70); stop otherwise |
| 2 | REG0A (0x0A) | CELL_1:0 | must read 0h (1s) | 3.6 V is inside the 1s VREG range of 3.0–4.99 V (Table 7-2); other CELL settings ignore the write |
| 3 | REG10 (0x10) | WATCHDOG_2:0 | 000b (disable) | the first write puts the charger in host mode and starts the watchdog (§7.4.1), so the first write disables it. Reset value 0x85 becomes 0x80 |
| 4 | §4 | ICHG, IPRECHG, ITERM, VSYSMIN, JEITA | cell values | TBD until the cell is chosen (§4) |
| 5 | REG01 (0x01–0x02) | VREG_10:0 | VREG_10:0 = 0x168 | `battery.charge_limit_v` / 10 mV, offset 0 mV (Table 7-15). Bytes: 0x01, 0x68 |
| 6 | REG01 | VREG_10:0 | read back | firmware sets `charger_vreg_mv` from this read; `solardeck_charge_enable_allowed()` (firmware test 7) |
| 7 | — | `CHG_CE_N` | drive low | only if step 6 equals step 5 |
| 8 | REG01, REG10 | VREG, WATCHDOG | re-read on every `CHG_INT_N` pulse and periodically | if either changed, the charger was reset (POR, REG_RST or a watchdog that something re-enabled): stop charging at once by letting `CHG_CE_N` go high (stop driving it low), then restart at step 1 |

Rules that follow from the datasheet:

- **Disable the watchdog; never rely on feeding it.** On expiry the charger returns to default mode
  (§7.4.1), and §7.3.2 says VREG returns to the 1s POR value with it, which is a Li-ion voltage.
  Table 7-15 lists VREG as reset only by REG_RST, which contradicts §7.3.2; the safe reading is
  §7.3.2. ADR-035's "fed or disabled" becomes "disabled" (`charger.watchdog`).
- **In default mode the charger keeps charging** with its default timers (§7.4.1). After any charger
  reset with CE still low it charges at the POR VREG, so step 8 must first let `CHG_CE_N` go high
  (charging off). The protector's overvoltage trip is the hardware backstop for the interval before
  firmware notices (ADR-047).
- **Never write REG_RST** (REG09 bit 6) while CE is low.
- Software is frozen (ADR-046): the firmware today implements only the step-6/7 gate. Steps 1–3 and 8
  are requirements for when firmware work resumes; nothing is coded here.

---

## 4. TBD until the cell is chosen (ADR-040)

**Protector constraint (not cell-dependent):** the protector's overvoltage trip must sit above
`battery.charge_limit_v` and below the charger's 1s POR VREG, so that a charger reset with CE low is
stopped in hardware (ADR-047). A BQ29706-class LiFePO4 variant satisfies this; a Li-ion BQ297xx variant
does not. Verify the chosen variant's OVP in its datasheet before capture.

Formulas and where they come from; no numbers until the cell datasheet is in hand.

| Item | Where it is set | Formula / rule | Source |
| :-- | :-- | :-- | :-- |
| ICHG | REG03, 50–5000 mA in 10 mA steps | ≤ the cell's maximum charge current, and ≤ (ILIM × V_BUS × efficiency) / VREG minus system load | SLUSDV2C Table 7-16 |
| IPRECHG, VBAT_LOWV | REG08 | precharge current and the precharge→fast threshold (a fraction of VREG) per the cell's low-voltage charge rule | Table 7-19 |
| ITERM | REG09, 40–1000 mA | the cell's cut-off current at CV | Table 7-20 |
| VRECHG | REG0A | recharge offset below VREG | Table 7-21 |
| VSYSMIN | REG00, from 2.5 V in 250 mV steps | < VREG (Table 7-14); high enough that VSYS keeps the 5 V boost above its minimum input during charging | Table 7-14 |
| TS network RT1/RT2 | U1 pin 16 | RT2 and RT1 from Eq. 2 and Eq. 3 with the NTC's resistance at T1 and T5 and the VT1/VT5 percentages of REGN (§6.5); T1/T5 = the cell's charge-temperature window | §7.3.9.5.1, Fig. 7-12 |
| JEITA zones | REG17 (JEITA_VSET, ISETH, ISETC), REG18 (TS_COOL, TS_WARM) | current and voltage per zone from the cell datasheet; the HARDWARE_SPEC §2.3 ladder is a placeholder until then | Tables 7-33, 7-34 |
| NTC part | NTC1, NTC2 | its R–T curve must be the one used in Eq. 2/3 (TI assumes 103AT) | §7.3.9.5.1 |
| L1 saturation | U1 inductor | ≥ max(IIN, ICHG, IBATDIS, IOTG) + IRIPPLE/2 and ≥ 2 A; IOTG = `power_bank.otg_max_a` | §8.2.2.2, Eq. 4–6 |
| Protector variant | U2 | the BQ29706's fixed OVP/UVP must sit outside the cell's charge limit and above its minimum discharge voltage; if not, pick another BQ297xy code (factory options, §4 table, last row) | SLUSBU9I §4 |
| 0 V charging | U2 variant | allowed or inhibited per the cell maker (§8.4.6–8.4.7); the comparison table does not say which BQ29706 does | SLUSBU9I §8.4.6–8.4.7 |
| Q_DSG, Q_CHG and OC trips | U2 FETs | I_OCD = V_OCD / (R_DS(on),DSG + R_DS(on),CHG + R_SENSE) above the peak discharge current; I_OCC likewise for charge; short-circuit current I = V_pack / (R_cell + 2 R_DS(on) + R_trace) within the FET's pulse rating for the SCD delay | §9.2.2 |
| Gauge data flash | U3 | Design Capacity, Design Voltage, Device Chemistry, Cell Low Voltage (bqStudio) | SLUSCY0C §7.2.2.1 |
| Gauge chemistry ID | U3 | SLUSCY0C names only Li-ion/Li-polymer. Whether TI has a LiFePO4 chemistry ID for this gauge, or the cell needs a GPCCHEM characterisation run, is **unverified** (open item 4) | SLUSCY0C §7.1 |
| R_SENSE | gauge sense | 1–3 mΩ and ≤ 100 mV / I_peak (coulomb counter range ±100 mV) | SLUSCY0C §6.4.2.1, §7.4.1 |
| F1 rating | `CELL_P` | above the maximum continuous discharge current with derating, below the cell's limit, and fast enough to clear a short that the protector fails to stop | cell + fuse datasheets (none in hand) |

---

## 5. USB-PD sink: CH224K vs STUSB4500

The BQ25798 accepts 3.6–24 V at VBUS (SLUSDV2C §6.3); VBUS_OVP is 25.2–26.2 V (§6.5).

| | CH224K (WCH datasheet V2.0) | STUSB4500 (DS12499 Rev 4) |
| :-- | :-- | :-- |
| Configuration | three strap pins or one resistor; no I²C on the K (I²C exists on CH224Q/CH224A only) | NVM programmed over I²C; works standalone after that (auto-run, §3.3) |
| Runtime visibility | PG pin only | I²C status registers, ALERT, ATTACH (§2.2) |
| Voltage range | 5/9/12/15/20 V by strap (§6.2). CH224Q/A can request 28 V (Table 5-2), above the BQ25798's input range | PDO1 fixed 5 V; PDO2/PDO3 5–20 V in 50 mV steps (§3.3.1): all inside 3.6–24 V |
| Dead-battery Rd | not stated in the datasheet | specified: CCxDB tied to CCx gives Rd unpowered (§3.5); Rd 5.1 kΩ ±10 % (§7.3) |
| Standby drain on the cell | none: powered from VBUS (VDD shunt) | none with VSYS grounded: powered from VBUS (§6.1.1). Idle on VBUS 110–210 µA (§7.3) |
| Certification | none claimed in the datasheet | USB Type-C rev 1.2 and USB PD rev 2.0 certified (TID listed on page 1) |
| Vendor direction | WCH recommends CH224Q/CH224A for new designs (Table 3-1 note) | — |
| Availability / price | not quoted (BOM row is shared at the CH224K price) | not quoted; the datasheet in hand is Rev 4 (2020), a later revision exists |

**Recommendation (for the owner to decide): STUSB4500.** Every PDO it can request is inside the
charger's input range by construction, it specifies dead-battery Rd, it is PD-certified, and its
status is readable on the always-on bus at no cost to the cell. The CH224K is cheaper and simpler
but leaves Rd-at-0 V unspecified, and its I²C successors can request 28 V.

Both options conflict with two existing rules (open items 5 and 8): `USB_ROBUSTNESS.md` R1 asks for
discrete 5.1 kΩ ±1 % Rd (`usb.sink_cc_rd_tolerance_pct`), which a PD controller's own Rd replaces;
and HARDWARE_SPEC §2.11 gives port 1's CC lines to a TUSB320 and makes port 2 a host port, which
leaves no port for a PD sink.

---

## 6. Always-on I²C address map

| 7-bit address | Device | Source |
| :-- | :-- | :-- |
| 0x28 | STUSB4500, ADDR1:0 = 00 (if chosen) | DS12499 §4.1 (0x28–0x2B) |
| 0x40 | INA3221, A0 = GND | SBOS576C Table 7-1 |
| 0x52 | RV-3028-class RTC (carrier, ADR-046) | **from memory — verify** against the RTC datasheet |
| 0x55 | BQ27Z561-R2 gauge | **verify** in the BQ27Z561 TRM; SLUSCY0C does not state it |
| 0x6B | BQ25798 charger | SLUSDV2C §7.3.14.5 |

No conflicts among these. Carrier devices listed in HARDWARE_SPEC §2.9 (TMP112 0x48/0x49, BMA400
0x15, BMP390 0x76, DS3231 0x68 DNP) were not checked against their datasheets here; the TUSB320
and the GPIO expander (part TBD) still need addresses. If the CH224Q/CH224A were chosen, its fixed
0x22/0x23 (CH224 §5.2.3) falls inside the address range common to 16-bit GPIO expanders: check
when the expander is picked.

---

## 7. Test points and bring-up order

**Test points** (1.0 mm pads, labelled, as HARDWARE_SPEC §7.8): `VBUS_IN`, `PMID`, `VSYS`,
`REGN`, `PACK_P`, `CELL_P`, `GND_CELL`, `N_SNS`, `VDD_3V3_AON`, `5V_SYS`, `3V3_GNSS`, `5V_LOAD`,
`SOLAR_IN`, VSTOR (U7 pin 15), `CHG_CE_N`, `CHG_INT_N`, `CHG_STAT`, `CHG_TS`, `CHG_ILIM`,
`I2C_AON_SDA`, `I2C_AON_SCL`, CC1, CC2, U1 SW1 and SW2, U6 SW, and `GND` × 4.

**Bring-up order.** The method for cold resistance checks is `FIRST_BOOT_CHECKLIST.md` §2; the
bench instruments are `DEV_KIT_BENCH.md` (§6 adds EVT-0); what a green suite does and does not
prove is `HARDWARE_VERIFICATION_WORKFLOW.md`. Steps specific to this board:

1. Cold resistance on every rail test point. No cell, no VBUS.
2. Bench supply (current-limited) on `CELL_P`/`GND_CELL` instead of a cell. Expect `VDD_3V3_AON`,
   the charger at 0x6B and the gauge on the bus; `CHG_CE_N` high.
3. Sweep the supply through the BQ29706 OVP and UVP (SLUSBU9I §4 thresholds and delays); watch
   COUT/DOUT. Repeat OCD/OCC with an electronic load through the FETs.
4. Host disconnected. Apply 5 V at `VBUS_IN` with the cell supply at the protector's UVP region and
   at 0 V. Scope `CHG_CE_N`, `VDD_3V3_AON` and SW1 together: record whether CE is ever low while the
   converter switches (open item 3). This is the hold-off proof without firmware.
5. Host connected. Run §3.2 steps 0–7; confirm the read-back; measure termination at
   `battery.charge_limit_v` on a cell simulator (supply plus load), then on the one real cell.
6. NTC: replace NTC1 with a resistance decade at the T1/T5 values; confirm charge suspend at both
   (AGENTS §4.1) before leaving a real cell on charge.
7. PD: probe CC1/CC2 to GND at 0 V for Rd (`USB_ROBUSTNESS.md` R2), then a real PD charger; read
   the contract and confirm `VBUS_IN` and the ILIM clamp.
8. `EN_5V_SYS` high: 5 V rail into an electronic load; load steps up to the CM5 peak once known.
   With EN low, measure `5V_SYS` (open item 10).
9. Load switches: off-state leakage on `3V3_GNSS` and `5V_LOAD`.
10. Floor: every load off, host idle, DMM in J_IBAT. J_IBAT does not see the gauge's and protector's
    own current (they sit on `CELL_P` ahead of it); measure those separately or at the cell terminals
    before calling the floor `measured`. This is the power-tree part of G12, not the
    device floor.
11. Harvester: supply plus series resistor into `SOLAR_IN`; confirm charging stops at VBAT_OV, below
    `battery.charge_limit_v`.
12. INA3221 readings against the DMM on each channel.

---

## 8. Open items

**Host header voltage (bring-up):** power the Pico 2 from `VDD_3V3_AON` with its own regulator
disabled (`3V3_EN` low, external 3.3 V on its `3V3` pin), so its I/O never sits above the AON rail
and back-feeds the gauge, charger and INA3221 through their input clamps.

1. **AON rail source.** This package feeds the TPS62840 and TPS61088 from VSYS (§1.2); HARDWARE_SPEC
   §2.3 says VBAT. Owner to confirm.
2. **The "3.3 V always-on rail" is a buck from a LiFePO4 cell.** The TPS62840 is a step-down
   converter (SLVSEC6D title), not the buck-boost HARDWARE_SPEC §2.3 and the BOM describe. With a
   3.3 V setting it is in 100 % mode across most of the LiFePO4 plateau and the rail follows the cell
   down to the protector's UVP. Options: accept a tracking rail (every AON part must run to the cell
   minimum; the INA3221 needs VS ≥ 2.7 V, SBOS576C §6.3), or set a lower regulated VSET from Table 1.
3. **CE race with a flat cell** (§3.1). If step 4 shows CE low while switching, pull CE up from a
   rail that exists before the charger switches (REGN does, but RP2350 pad tolerance to it is
   unverified) or add a discrete gate. Changes `PIN_BUDGET` polarity only if a FET inverts it.
4. **Gauge chemistry.** ADR-035 and HARDWARE_SPEC say "TI lists LiFePO4" for the BQ27Z561-R2; the
   SLUSCY0C datasheet says Li-ion/Li-polymer only. Confirm with TI's chemistry list or a GPCCHEM run
   before relying on the gauge. Also confirm the I²C address in the TRM.
5. **Rd rule vs a PD controller.** `USB_ROBUSTNESS.md` R1/R2 require discrete 5.1 kΩ ±1 % Rd; the
   STUSB4500's own Rd is ±10 % and a discrete Rd in parallel would halve it. Owner to restate R1.
6. **STUSB4500 on an unpowered I²C bus.** It is powered only from VBUS; its behaviour with SCL/SDA
   pulled up while unpowered is not stated. EVT-0 has 0 Ω links to drop it off the bus; measure.
7. **D+/D− with a CH224K.** Both it and the BQ25798 use D+/D−; pick one owner if CH224K is chosen.
8. **USB-C port roles.** HARDWARE_SPEC §2.11 puts a TUSB320 on port 1's CC and a host switch on
   port 2, yet §2.3 sinks PD and solar on those ports. One CC controller per port: decide which port
   is the PD sink.
9. **Input OR-ing.** The BQ25798 has a native two-input mux (VAC1/VAC2, ACDRV, §7.3.5); the BOM adds
   two LM66100. Decide at carrier capture.
10. **5 V boost off-state.** Whether the TPS61088 disconnects its output when EN is low is in
    SLVSCM8D, which could not be downloaded. If it does not, `5V_SYS` sits near VSYS with the CM5
    "off", breaking the hard-off rule (AGENTS §4.2); a load switch would be needed. Also confirm the
    part is still active (its TI product page returned 404) and its minimum input (the EVM is labelled
    2.7 V, above the protector's UVP).
11. **Bezel strip.** Its open-circuit voltage must stay within VIN_DC's 3.0 V operating maximum
    (SLUSAH0G §7.5); the `SOLAR_ADC` divider waits for the strip part.
12. **Harvester bypasses the thermal window.** The BQ25504 charges the cell with no NTC input
    (OT_PROG senses its own die), so it can charge a cell below 0 °C. Decide whether the RP2350 must
    be able to stop it (no enable pin; a switch in the VBAT path would need a net).
13. **TPS61088 FSW, COMP and ILIM** resistors (§2.6) need SLVSCM8D and the CM5 peak current.
14. **INA3221 shunts** need each rail's maximum current (§2.9).

### 8.1 Existing docs contradicted by the datasheets (not edited here)

| Doc | Says | Datasheet says |
| :-- | :-- | :-- |
| HARDWARE_SPEC §2.3, BOM "AON 3.3V Supply" | TPS62840 is a buck-boost | step-down converter (SLVSEC6D) |
| BOM "AON 3.3V Supply" | TPS62840DLYR | orderable is TPS62840DLCR (SLVSEC6D addendum) |
| HARDWARE_SPEC §2.3, BOM "Bezel Solar MPPT" | BQ25504 cold-starts at 330 mV, harvests to 100 mV | cold start 600 mV typ / 700 mV max; operates from 130 mV (SLUSAH0G §7.5, revision history) |
| HARDWARE_SPEC §2.3 | NTC NCP18XH103F03RB with β = 3950 K | B25/50 = 3380 K, B25/85 = 3434 K (Murata NCP18XH103F03RB) |
| HARDWARE_SPEC §2.13 | TPS22918 discharges through 470 Ω | internal RPD is tens of ohms (SLVSD76C §6.5 RPD) |
| ADR-035, HARDWARE_SPEC §2.3 | watchdog "fed or disabled" | expiry can restore the Li-ion POR VREG (SLUSDV2C §7.3.2): disable only |
| ADR-035, HARDWARE_SPEC §2.3 | BQ27Z561-R2: "TI lists LiFePO4" | SLUSCY0C covers Li-ion/Li-polymer; LiFePO4 unverified |
| BOM "Power Gates" vs HARDWARE_SPEC §2.11 | port 2 VBUS on a TPS22918 vs a TPS2051B with a current limit | TPS22918 has no current limit (SLVSD76C), so it cannot meet `usb.port2_current_limit_a` |

---

## Appendix A — Datasheets used

| Part | Document | Revision |
| :-- | :-- | :-- |
| BQ25798 | TI SLUSDV2C | May 2020, rev. June 2026 |
| BQ29706 | TI SLUSBU9I (BQ2970 family) | rev. August 2024 |
| BQ27Z561 | TI SLUSCY0C | rev. September 2025 (10-page datasheet; the TRM was not in hand) |
| STUSB4500 | ST DS12499 | Rev 4, February 2020 (from a mirror; st.com refused the download) |
| CH224K | WCH CH224 datasheet | V2.0 |
| TPS62840 | TI SLVSEC6D | rev. March 2020 |
| TPS61088 | TI SLVUAF2 (EVM user's guide) | June 2015 — the datasheet SLVSCM8D was not retrievable |
| BQ25504 | TI SLUSAH0G | rev. August 2023 |
| TPS22918 | TI SLVSD76C | rev. July 2017 |
| INA3221 | TI SBOS576C | rev. September 2026 |
| NCP18XH103F03RB | Murata product data sheet | as downloaded |
