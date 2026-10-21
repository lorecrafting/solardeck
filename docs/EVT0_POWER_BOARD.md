# EVT-0 Power Board — capture package

Written 2026-10-21 19:12 UTC in Claude Code by anthropic/claude-opus-5-5 (EVT-0 power board, ADR-043).
Revised 2026-10-21 19:42 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

**Status: capture spec only. No schematic, layout or netlist exists for this board.** Every pin
assignment below comes from a datasheet that was open when it was written (Appendix A lists them
with revisions). A value that no open datasheet supports is written **TBD** with what unlocks it.
Values that depend on the cell are in §4, never in the pin tables. Chemistry is 1S Li-ion in a
replaceable smart pack (ADR-048); LiFePO4 is V2. Change class: C2 DESIGN (plus C1
for the new `charger` and `harvester` keys in `spec_values.json`).

---

## 1. Purpose

ADR-043 build order step 2: the power tree on its own board, before the RP2350 minimum system and
the CM5 carrier, because power carries the safety risk and does not wait on the panel. The
co-processor is an external Raspberry Pi Pico 2 on a header (§2.11).

**EVT-0 proves (on the bench, as `measured <date>` entries):**

- the charger stays off until the RP2350 has written and read back VREG = `battery.charge_limit_v`
  (ADR-035), including at first VBUS with no firmware running;
- the register sequence in §3 (watchdog off, VREG, read-back, pack check, CE release, re-check);
- the TS/NTC cutoff suspends charging outside the window (AGENTS §4.1: verify before any charge);
- the pack gauge answers through `J_PACK` on the always-on bus, reads pack voltage and current with
  charge current positive, and a pack whose charge-voltage parameter differs is refused;
- the harvester temperature gate (§2.7.1) switches the harvester off outside the window, with an
  open NTC and with the pack removed;
- the PD sink negotiates a contract inside the BQ25798 input range, and presents Rd at 0 V
  (`USB_ROBUSTNESS.md` R2);
- the always-on rail holds 3.3 V across the pack's range, the 5 V boost under a dummy load, the
  load switches' off-state leakage, and the battery-side floor of the power tree with every
  switched load off (the power-tree part of G12);
- the harvester stops at its VBAT_OV threshold below the charge limit.

**EVT-0 does not prove:** CM5 behaviour (the 5 V rail drives an electronic load), gauge accuracy
(needs the chemistry ID and a learning cycle on the chosen cell, ADR-040/048), the pack protector's
trip thresholds (pack qualification, on the pack board), runtime or pack capacity,
thermal behaviour in the enclosure, EMI/ESD, the carrier layout, the full-device sleep floor, or
anything about the panel.

### 1.1 Block diagram

```
 USB-C sink --VBUS_IN--+-- STUSB4500 PD sink (CC1/CC2; §5)
                       |
                       v
                +-------------+  VSYS   +----------+ VDD_3V3_AON
                |  BQ25798    |---+---->| TPS63900 |---+--> AON pull-ups, INA3221,
                |  charger    |   |     |buck-boost|   |    header, NTC gate (U12)
                |  I2C 0x6B   |   |     +----------+   +--TPS22918--> 3V3_GNSS
                +-------------+   |     +----------+
                   BAT |          +---->| 5 V boost|-5V_SYS-+--> dummy load
                       |                | (TBD, U6)|        +-TPS22918-> 5V_LOAD
  bezel strip          |                +----------+
  -> BQ25504 -[U11]--->+ PACK_P      (U11 on only inside the window, §2.7.1)
                       |
                   [J_IBAT]
                       |
 ==== J_PACK, keyed: PACK+  PACK-(GND)  SDA  SCL  NTC  NTC_GATE ====
 smart pack (§2.3):
   PACK+ -- protector FETs (high side) -- fuse -- CELL+ ; BQ27Z561 BAT/BAT_SNS
   PACK- -- R_SENSE (SRN side | SRP side) -- CELL-     ; BQ27Z561 VSS = CELL-
   1S Li-ion cell between CELL+ and CELL-
```

### 1.2 Topology decisions in this package (owner to confirm)

1. **The always-on buck-boost and the 5 V boost run from the charger's `SYS` (VSYS), not from the
   pack.** VSYS exists whenever VBUS is present, even with a tripped or flat pack, so the CE
   pull-up rail and the RP2350 are up before charging can start. HARDWARE_SPEC §2.3 says the AON
   rail is "powered directly from VBAT"; this package diverges deliberately (open item 1).
2. **Protector and gauge live in the pack, in TI's reference topology** (ADR-048; SLUSCY0C
   Fig. 7-1). The protector's back-to-back FETs switch `PACK+` (high side); R_SENSE sits in the
   negative path between the cell negative and `PACK−`; the gauge's VSS is the cell negative (the
   "device ground reference" of the §7.4.2 layout example). The board's `GND` is `PACK−`, which
   differs from the gauge's VSS only by the R_SENSE drop and stays common when the protector opens,
   so the gauge's I²C keeps the board's ground reference. **SRP/SRN as Fig. 7-1:** SRP through
   RSRP (100 Ω) to the cell-negative end of R_SENSE, SRN through RSRN (100 Ω) to the `PACK−` end.
   Charge current then flows from the cell negative towards `PACK−`, so V(SRP) − V(SRN) > 0, which
   the gauge reports as charge (§6.4.2.1); no sign re-derivation is needed. This closes ADR-047's
   gauge polarity and ground items. A low-side protector (the BQ29706 drives low-side FETs,
   SLUSBU9I Fig. 9-1) would reopen them, so the pack protector must drive high-side FETs.
3. **No input OR-ing on EVT-0.** One USB-C sink receptacle feeds VBUS; VAC1/VAC2 tie to VBUS and
   ACDRV1/2 to GND (BQ25798 pin table). The BQ25798 has its own two-input mux (§7.3.5) which the
   carrier may use instead of the BOM's LM66100 pair (open item 9).

---

## 2. Pin-level connections

Net names follow `PIN_BUDGET.md` where a net exists there. Local nets: `VBUS_IN`, `PMID`, `VSYS`,
`REGN`, `PACK_P`, `VDD_3V3_AON`, `5V_SYS`, `3V3_GNSS`, `5V_LOAD`, `SOLAR_IN`, `HARV_OUT`,
`HARV_EN`, `NTC_GATE`, `PD_ALERT_N`, `LOAD5_EN`, `CHG_STAT`. `GND` is the board ground (`PACK−`).
Pack-board nets (§2.3): `CELL_P`, `CELL_N`.
"Design value" marks a passive chosen here, not taken from a datasheet.

### 2.1 U1 — BQ25798 charger (RQM, VQFN-29)

Source: SLUSDV2C Table 5-1 (pins), §7.3.2 (PROG), §7.3.4.3 (ILIM_HIZ), §8.2.2 (L, C).

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | STAT | `CHG_STAT` | 10 kΩ pull-up to `VDD_3V3_AON` (open drain; not REGN, which is about 5 V and would drive the RP2350/Pico pin above its rail); test point |
| 2, 3 | VBUS | `VBUS_IN` | 2 × 10 µF + 0.1 µF, the 0.1 µF closest to the pins; rated ≥ 25 V (§8.2.2.3) |
| 4 | BTST1 | — | 47 nF, ≥ 10 V, BTST1 to SW1 |
| 5 | REGN | `REGN` | 4.7 µF, 10 V, to GND. Feeds only STAT, TS and ILIM_HIZ dividers (§7.3.4.1) |
| 6 | D+ | `USB_DP` | receptacle D+ (A6/B6); the STUSB4500 has no D+/D− pins, so the charger owns them |
| 7 | D− | `USB_DM` | receptacle D− (A7/B7) |
| 8 | VAC2 | `VBUS_IN` | no ACFET2/RBFET2 fitted (pin table) |
| 9 | VAC1 | `VBUS_IN` | no ACFET1/RBFET1 fitted (pin table) |
| 10 | ACDRV2 | `GND` | pin table: tie to GND if no FETs |
| 11 | ACDRV1 | `GND` | pin table: tie to GND if no FETs |
| 12 | QON | test point | internal pull-up (RQON, §6.5); pad to GND for a manual ship-exit/reset button, DNP |
| 13 | CE | `CHG_CE_N` | **10 kΩ pull-up to `VDD_3V3_AON`** (design value, §3); to header |
| 14 | SCL | `I2C_AON_SCL` | bus pull-up §2.12 |
| 15 | SDA | `I2C_AON_SDA` | bus pull-up §2.12 |
| 16 | TS | `CHG_TS` | RT1 from `REGN`, RT2 to GND, pack NTC (`J_PACK` NTC, to `PACK−`) to GND. Values: §4 |
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

### 2.2 Pack protector (on the pack board)

Not on the EVT-0 board: the protector ships in the pack (ADR-048) and is chosen with the cell. Part
**TBD** (open item 17); no protector datasheet for a high-side 1S Li-ion part is in hand, so no pin
table here. Requirements: drives back-to-back FETs in `PACK+` as SLUSCY0C Fig. 7-1 (§1.2 item 2),
Li-ion 1S thresholds, and the OVP rule in §4. A pack fuse is mandatory (ADR-048), rating with the
cell (§4).

### 2.3 Pack board — BQ27Z561 gauge (WCSP-12) and pack connector

Source: SLUSCY0C Table 4-1, §6.3.2.6, §6.4.2.1, §7.2 (Fig. 7-1), §7.4.1–7.4.2; the -R2 Technical
Reference Manual SLUUC54C (rev. March 2024) for the address (§10.2), commands and data flash. This is the reference topology the pack must follow, whoever builds the pack board.

| Ball | Name | Net (pack board) | Passives / notes |
| :-- | :-- | :-- | :-- |
| A1 | INT | — | not on `J_PACK`; no connection. The host polls `InterruptStatus()` (0x6E), readable while sealed, which carries the same flags (SLUUC54C §6.1, §12.1.38); INT would only save a wake-up. On the -R2 it is open-drain by default (IO Config `INT_PUP` = 0, §6.4) |
| A2 | PULS | — | not used, no connection |
| A3 | SDA/HDQ | `J_PACK` SDA | never switch to HDQ: the change is irreversible (§6.3.4) |
| B1 | TS | pack thermistor to VSS | 10 kΩ NTC (Fig. 7-1), the gauge's own; internal 18 kΩ pull-up (§6.3.2.6) |
| B2 | VSS | `CELL_N` | device ground reference (§7.4.2) |
| B3 | SCL | `J_PACK` SCL | — |
| C1 | SRN | `PACK−` end of R_SENSE | through RSRN 100 Ω; Kelvin (Fig. 7-1) |
| C2 | BAT_SNS | `CELL_P` | Kelvin to the cell positive, no shared path with BAT (§7.4.1) |
| C3 | NU | — | no connection |
| D1 | SRP | `CELL_N` end of R_SENSE | through RSRP 100 Ω; Kelvin. 0.1 µF from SRP to SRN on the gauge side (Fig. 7-1) |
| D2 | BAT | `CELL_P` | 1 µF to VSS, close to the gauge (Fig. 7-1) |
| D3 | CE | `CELL_P` | active high; tied on (Fig. 7-1's CPU-control option is not on the connector) |

- **R_SENSE** between `CELL_N` and `PACK−`: 1–3 mΩ, ≤ 50 ppm/°C, as small as the current ranges
  allow, because a short drives VSS negative and VSS has an absolute minimum of −0.3 V (§7.4.1).
  Value: §4. Positive V(SRP) − V(SRN) is charge (§6.4.2.1).
- **I²C at pack removal:** SDA and SCL have internal pull-downs; with both low the gauge
  auto-calibrates and sleeps (§7.4.1). The board's pull-ups (§2.12) are its only pull-ups.

**`J_PACK` — keyed, locking, 6 positions** (ADR-048: 5–6 pins; screws and pull tab, no adhesive):

| Pos | Net | Notes |
| :-- | :-- | :-- |
| 1 | `PACK+` | to `J_IBAT`, then `PACK_P`; contact rating ≥ the pack's peak current (connector part TBD, with the cell) |
| 2 | `PACK−` | board `GND` |
| 3 | SDA | `I2C_AON_SDA` |
| 4 | SCL | `I2C_AON_SCL` |
| 5 | NTC | pack thermistor to `PACK−`, for the charger's TS (U1 pin 16) |
| 6 | `NTC_GATE` | second pack thermistor to `PACK−`, for the harvester gate (§2.7.1); see open item 15 |

Two pack thermistors reach the board because the charger's TS divider is biased from REGN, and
REGN is off on battery alone (SLUSDV2C §7.3.3) unless firmware turns on OTG or the ADC's TS channel
(§7.3.4.1); the harvester charges without VBUS and without firmware.

### 2.4 U4 — STUSB4500 USB-PD sink (QFN-24; decided, ADR-048)

Source: DS12499 Rev 4 Table 1, §2.2, §3.5, Fig. 9.

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

### 2.5 U5 — TPS63900 always-on buck-boost (DSK, WSON-10)

Source: SLVSET3D Table 5-1, §6.3, §7.3.6 (Table 7-2, Table 7-3), page-1 simplified schematic.
The rail holds 3.3 V to an empty pack (ADR-048).

| Pin | Name | Net | Passives / notes |
| :-- | :-- | :-- | :-- |
| 1 | EN | `VSYS` | always on; must not be left open (pin table) |
| 2 | SEL | `GND` | selects VO(1), set by CFG3; must not be left open (pin table) |
| 3 | CFG1 | — | 36.5 kΩ ±1 % to GND: VO(2) = 3.3 V (Table 7-2), so SEL at either level gives 3.3 V |
| 4 | CFG2 | — | 0 Ω to GND: input current limit unlimited (Table 7-2); must not be left open |
| 5 | CFG3 | — | 16.2 kΩ ±1 % to GND: VO(1) = 3.3 V (Table 7-3) |
| 6 | VOUT | `VDD_3V3_AON` | 22 µF (page-1 schematic); ≥ 10 µF effective after DC bias (§6.3 CO) |
| 7 | LX2 | L2 pin 2 | boost-stage switch node |
| 8 | GND | `GND` | — |
| 9 | LX1 | L2 pin 1 | buck-stage switch node |
| 10 | VIN | `VSYS` via J_IAON | 10 µF (page-1 schematic); ≥ 5 µF effective (§6.3 CI) |
| pad | — | `GND` | thermal pad to ground (pin table) |

- **L2 = 2.2 µH**, saturation rating ≥ 2 A at the unlimited input-current setting (§6.3 ISAT).
- CFG resistors ±1 %, ≤ ±200 ppm/°C, < 10 pF on each CFG node (§6.3, §7.3.6); read once at
  start-up.
- Input range 1.8–5.5 V (§6.3). VSYS with a 1s PROG setting stays below the BQ25798's
  VSYSMAX_REG_ACC maximum (SLUSDV2C §6.5), inside that range. Output > 400 mA for VI ≥ 2.0 V
  (SLVSET3D §1). Orderable: TPS63900DSKR (orderable addendum).

### 2.6 U6 — 5 V boost (part TBD, re-selection open)

The TPS61088 is dropped (ADR-048): its datasheet SLVSCM8D and product page were unavailable, so it
cannot be shown to be in production. The replacement is re-selected from an in-production part with
a datasheet in hand; its pin table is **TBD** until then. Requirements carried over: `EN_5V_SYS`
with a pull-down so the rail is off while the host is in reset; output disconnected (or a load
switch added) when EN is low (open item 10); input range covering VSYS; current limit sized to the
CM5 peak once known (open item 13).

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
| 6 | VBAT_OV | — | ROV1 = `harvester.rov1_mohm` to GND, ROV2 = `harvester.rov2_mohm` to VRDIV, 1 % or better (`harvester.resistor_tol_pct`) |
| 7 | VRDIV | — | top of the OV and UV dividers |
| 8 | VBAT_UV | — | RUV1 5.60 MΩ to GND, RUV2 4.42 MΩ to VRDIV (§9.2.1.2) |
| 9 | OK_HYST | `GND` | VBAT_OK not used (pin table) |
| 10 | OK_PROG | `GND` | VBAT_OK not used (pin table) |
| 11 | VBAT_OK | — | floating (pin table) |
| 12 | AVSS | `GND` | thermal pad |
| 13 | VSS | `GND` | thermal pad |
| 14 | VBAT | `HARV_OUT` | ≥ 100 µF to GND (pin table, §6.3 CBAT), since U11 disconnects the pack; the pack is the storage element when U11 is on |
| 15 | VSTOR | — | ≥ 4.7 µF ∥ 0.1 µF to pin 1 |
| 16 | LBST | L4 | L4 = 22 µH, > 300 mA peak (§9.1.2) |

**VBAT_OV is a charge limit.** The harvester charges the cell without the CE gate, so its OV
threshold must stay below `battery.charge_limit_v` at its worst-case accuracy:
VBAT_OV = 3/2 × VBIAS × (1 + ROV2/ROV1) (Eq. 3) gives `harvester.vbat_ov_v`, and
`harvester.vbat_ov_v` × (1 + `harvester.threshold_accuracy_pct`) ≤ `battery.charge_limit_v`.
Phase 14 checks both. VIN_DC operates from 130 mV to 3.0 V after cold start (§7.5 VIN(DC)): the
bezel strip's open-circuit voltage must stay inside that (open item 11).

#### 2.7.1 Harvester temperature gate (ADR-048, `harvester.temperature_gate`)

The BQ25504 has no NTC input (OT_PROG senses its own die) and charges without the CE gate, so it
could charge a frozen pack. A hardware gate, no firmware:

- **Sensor:** the pack's `NTC_GATE` thermistor (`J_PACK` pos. 6) to `GND`, biased by a resistor
  from `VDD_3V3_AON`.
- **Window comparator U12:** two comparators compare `NTC_GATE` with a cold and a hot threshold
  taken from a divider on the same `VDD_3V3_AON`, so the window is ratiometric and the rail's
  tolerance cancels. Outputs open-drain, wired-AND on `HARV_EN` with one pull-up to `VDD_3V3_AON`:
  `HARV_EN` is high only inside the cell's charge-temperature window. Thresholds are the
  `NTC_GATE` voltages at the window edges, with hysteresis (§4). Part **TBD**: no comparator
  datasheet is in hand (open item 18); it must run from `VDD_3V3_AON` with rail-to-rail inputs,
  and its supply current counts in the battery-side floor (§7 step 10).
- **Switch U11** between `HARV_OUT` (VIN) and `PACK_P` (VOUT), ON = `HARV_EN`. Part **TBD**
  (open item 18); a TPS22918 is a candidate, with its QOD pin **left floating** (SLVSD76C
  §8.3.2, third option), because QOD tied to VOUT would discharge the pack through RPD while off.
  Whether a candidate blocks `PACK_P` → `HARV_OUT` current when off must come from its datasheet;
  SLVSD76C does not state reverse-current blocking, so it is not assumed. With U11 off the
  harvester charges its 100 µF to VBAT_OV and stops (`harvester.vbat_ov_v`).
- **Not a chemistry check:** the gate does not see §3.2 step 6a, so a wrong-chemistry pack inside
  the window still takes solar charge up to `harvester.vbat_ov_v`. Only that pack's own protector
  or connector keying stops it (open item 15).
- **Fails off:** an open NTC or a removed pack reads as cold (`NTC_GATE` pulled to the rail), a
  shorted NTC reads as hot, and with `VDD_3V3_AON` down the pull-up cannot raise `HARV_EN`.

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

### 2.10 Pack connector and current jumpers

| Ref | Connects | Notes |
| :-- | :-- | :-- |
| J_PACK | `PACK+`, `PACK−`, SDA, SCL, NTC, `NTC_GATE` | keyed, locking, 6 positions (§2.3); the fuse and both protector FETs are in the pack |
| J_IBAT | `J_PACK` `PACK+` → `PACK_P` | 2-pin jumper; open = DMM in series for the battery-side floor |
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
| 7 | NC (gauge INT not on `J_PACK`) | 8 | `SENSOR_ALERT_N` |
| 9 | `EN_5V_SYS` | 10 | `GNSS_EN` |
| 11 | `PD_ALERT_N` | 12 | `LOAD5_EN` |
| 13 | `SOLAR_ADC` | 14 | `CHG_STAT` |
| 15 | `GND` | 16 | `GND` |

`SOLAR_ADC`: from `SOLAR_IN` through a divider footprint, values TBD with the strip (open item 11).
On the carrier, `CHG_INT_N`, `GNSS_EN` and `SENSOR_ALERT_N` go to the GPIO expander
(PIN_BUDGET §4); EVT-0 brings them straight out. `GAUGE_INT` has no pack contact (open item 15).

### 2.12 Always-on I²C bus

One pair of 10 kΩ pull-ups to `VDD_3V3_AON` (BQ25798 pin table value) for SCL and SDA. The bus runs
at 100 kHz (HARDWARE_SPEC §2.9); every device here allows 400 kHz. The pack gauge joins the bus
through `J_PACK` and shares its ground through `PACK−` (§1.2 item 2).

---

## 3. Charger hold-off (ADR-035)

### 3.1 Hardware

- `CHG_CE_N` has a 10 kΩ pull-up to `VDD_3V3_AON`. Charging needs CE low **and** EN_CHG = 1
  (pin table); EN_CHG resets to 1, so CE is the only gate at power-up. CE must never float
  (pin table); VIH_CE ≥ 1.3 V, VIL_CE ≤ 0.4 V (§6.5).
- While the RP2350 is in reset its pad pull-down fights the 10 kΩ. CE stays high while
  V_AON × R_pd / (R_pd + 10 kΩ) ≥ 1.3 V, which needs R_pd ≥ 6.5 kΩ at a 3.3 V rail (regulated by
  the buck-boost, §2.5). **Verified:** the RP2350 pad pull-down is 36 kΩ minimum at IOVDD 3.3 V
  (RP2350 datasheet, build 2026-01-10, Table 1683, §14.9.4), so CE sits at about 2.6 V or more. At
  reset the pad output is high-impedance, its input disabled and its pull-down on (§9.3, Table 885).
  Erratum RP2350-E9 (Appendix D) needs the input enabled, which it is not at reset, and acts as a
  pull-up, so it cannot drag CE low.
- **Pad isolation hazard (firmware rule).** The RP2350 latches each pad's output and pulls while its
  isolation bit is set (§9.7): if the core powers down while driving `CHG_CE_N` low, the pad holds
  it low and charging continues with no firmware watching. Firmware must release `CHG_CE_N` (let it
  go high) before any RP2350 power-domain transition; EVT-0 step 5 checks it. A firmware rule is not
  a hardware gate: open item 19.
- **No ship FET.** VBAT_UVLOZ (the battery voltage at which I²C comes alive with no VBUS) is
  3.25–3.55 V with a ship FET and 2.50–2.71 V without (§6.5). With a ship FET the RP2350 could not
  reach the charger on a deeply discharged pack (`charger.ship_fet`; ADR-048 keeps this).
- **Known gap (open item 3):** with a flat or tripped pack, `VDD_3V3_AON` only rises after the
  charger starts switching into SYS, so CE reads low for that interval. Measure it at EVT-0
  (§7, step 4).

### 3.2 Register sequence (I²C 0x6B, SLUSDV2C §7.5)

16-bit registers are assumed MSB first at the lower offset. SLUSDV2C does not state the byte order:
§7.3.14.3 gives bit order within a byte, §7.3.14.7 sends data to Addr, Addr+1, and Fig. 7-27 draws
bits 15:8 first without naming their address. **Bench check before step 5:** with PROG strapped for
1s, REG01 resets to 0x01A4 (the 1s POR VREG); a 2-byte read from 0x01 must return 0x01 then 0xA4. Read-modify-write every register that holds other fields.

| Step | Register | Field | Value | Why |
| :-- | :-- | :-- | :-- | :-- |
| 0 | — | — | wait for I²C | registers are accessible about 20 ms after VBAT or VBUS is valid (§7.3.3, §7.3.4) |
| 1 | REG48 (0x48) | PN_2:0 | must read 011b | it is a BQ25798 (Table 7-70); stop otherwise |
| 2 | REG0A (0x0A) | CELL_1:0 | must read 0h (1s) | `battery.charge_limit_v` is inside the 1s VREG range of 3.0–4.99 V (Table 7-2); other CELL settings ignore the write |
| 3 | REG10 (0x10) | WATCHDOG_2:0 | 000b (disable) | the first write puts the charger in host mode and starts the watchdog (§7.4.1), so the first write disables it. Reset value 0x85 becomes 0x80 |
| 4 | §4 | ICHG, IPRECHG, ITERM, VSYSMIN, JEITA | cell values | TBD until the cell is chosen (§4) |
| 5 | REG01 (0x01–0x02) | VREG_10:0 | VREG_10:0 = 0x1A4 | `battery.charge_limit_v` / 10 mV, offset 0 mV (Table 7-15). Bytes: 0x01, 0xA4 |
| 6 | REG01 | VREG_10:0 | read back | firmware sets `charger_vreg_mv` from this read; `solardeck_charge_enable_allowed()` (firmware test 7) |
| 6a | pack gauge 0x55, `ChargingVoltage()` (0x30/0x31) | charge voltage, mV | read; must equal `battery.charge_limit_v` | ADR-048: refuse any pack built for another chemistry or limit; leave `CHG_CE_N` high and report. `ChargingVoltage()` is the only charge-voltage value readable while the pack is SEALED (SLUUC54C §12.1.20; data flash is not, §8.3.1). It follows temperature (§9.5), so compare it only while the gauge reports the standard-temperature range, and require ≤ the limit in every range. Not "Design Voltage", a gauging parameter |
| 7 | — | `CHG_CE_N` | drive low | only if step 6 equals step 5 and step 6a passed |
| 8 | REG10, REG01 | WATCHDOG (primary), VREG | re-read on every `CHG_INT_N` pulse and periodically | WATCHDOG comes up enabled after any charger reset, so it is the reset detector (on Li-ion VREG's POR value equals the limit and cannot reveal a reset; firmware gate `charger_wdt_off`); if either changed, the charger was reset (POR, REG_RST or a watchdog that something re-enabled): stop charging at once by letting `CHG_CE_N` go high (stop driving it low), then restart at step 1 |

Rules that follow from the datasheet:

- **Disable the watchdog; never rely on feeding it.** On expiry the charger returns to default mode
  (§7.4.1), and §7.3.2 says VREG returns to the 1s POR value with it. Table 7-15 lists VREG as reset
  only by REG_RST, which contradicts §7.3.2; the safe reading is §7.3.2. ADR-035's "fed or disabled"
  becomes "disabled" (`charger.watchdog`).
- **The 1s POR VREG is 4.2 V (Table 7-2), equal to `battery.charge_limit_v`.** A charger reset no
  longer raises the charge voltage on the right pack. A POR or REG_RST does put ICHG and VSYSMIN
  back to their 1s defaults (1 A, 3.5 V, Table 7-2), and the §4 cell values with them, and it
  would charge a wrong-chemistry pack (for example a future LiFePO4 pack, ADR-048) to a Li-ion
  voltage. So the hold-off now guards the pack identity and the cell settings, not the voltage
  of the right pack.
- **In default mode the charger keeps charging** with its default timers (§7.4.1). After any charger
  reset with CE still low it charges at POR settings, so step 8 must first let `CHG_CE_N` go high
  (charging off), then re-run the sequence including step 6a. The hardware backstop is each pack's
  own protector, chosen for that pack's cell (§4).
- **Never write REG_RST** (REG09 bit 6) while CE is low.
- Software is frozen (ADR-046): the firmware today implements only the step-6/7 gate. Steps 1–3, 6a
  and 8 are requirements for when firmware work resumes; nothing is coded here.

---

## 4. TBD until the cell is chosen (ADR-040, ADR-048)

**Protector OVP rule (not cell-dependent).** ADR-047's rule "OVP above the limit and below the
charger's 1s POR VREG" cannot be met for Li-ion: the POR VREG equals the limit (§3.2). It is
replaced by the usual Li-ion margin: the pack protector's minimum OVP threshold (from its datasheet)
must sit above `battery.charge_limit_v` × (1 + VREG_ACC max at 4.2 V, SLUSDV2C §6.5), so normal
charging never trips it, and as close above that as the protector's options allow. The 1s POR
VREG equals the limit, so it sits below that OVP by the same margin. It is a backstop
for a charger fault, not for a charger reset. Verify in the protector's datasheet before the pack
is built.

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
| NTC part | pack NTC, `NTC_GATE` | its R–T curve must be the one used in Eq. 2/3 (TI assumes 103AT) | §7.3.9.5.1 |
| Harvester gate thresholds | U12 divider, bias resistor | `NTC_GATE` voltage at the window edges T1/T5 (the same window as the charger's TS), ratiometric to `VDD_3V3_AON`; hysteresis from the comparator datasheet | NTC curve + comparator datasheet (none in hand) |
| L1 saturation | U1 inductor | ≥ max(IIN, ICHG, IBATDIS, IOTG) + IRIPPLE/2 and ≥ 2 A; IOTG = `power_bank.otg_max_a` | §8.2.2.2, Eq. 4–6 |
| Protector part | pack | Li-ion 1S, drives high-side FETs (§1.2 item 2); OVP per the rule above; UVP above the cell's minimum discharge voltage and below `battery.low_alarm_v` | protector datasheet (none in hand) |
| 0 V charging | pack protector | allowed or inhibited per the cell maker | protector + cell datasheets |
| Pack FETs and OC trips | pack protector | OCD/OCC trips above the peak discharge/charge current with the FETs' R_DS(on) and R_SENSE in the path; short-circuit current within the FETs' pulse rating for the SCD delay | protector datasheet |
| Gauge data flash | pack gauge | Design Capacity, Design Voltage, Device Chemistry, Cell Low Voltage (bqStudio), and the charge-voltage parameter step 6a reads (open item 16) | SLUSCY0C §7.2.2.1 |
| Gauge chemistry ID | pack gauge | the Li-ion ID that matches the chosen cell (bqCHEM in bqStudio) | SLUSCY0C §7.1, §7.2.2.1 |
| R_SENSE | gauge sense | 1–3 mΩ and ≤ 100 mV / I_peak (coulomb counter range ±100 mV) | SLUSCY0C §6.4.2.1, §7.4.1 |
| Pack fuse rating | pack, `CELL_P` | above the maximum continuous discharge current with derating, below the cell's limit, and fast enough to clear a short that the protector fails to stop | cell + fuse datasheets (none in hand) |

---

## 5. USB-PD sink: STUSB4500 (decided, ADR-048)

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

**Decided: STUSB4500 (ADR-048).** The table is kept as the record of why. Every PDO it can request
is inside the charger's input range by construction, it specifies dead-battery Rd, it is
PD-certified, and its status is readable on the always-on bus at no cost to the cell. The CH224K is
cheaper and simpler but leaves Rd-at-0 V unspecified, and its I²C successors can request 28 V.

The STUSB4500 conflicts with two existing rules (open items 5 and 8): `USB_ROBUSTNESS.md` R1 asks for
discrete 5.1 kΩ ±1 % Rd (`usb.sink_cc_rd_tolerance_pct`), which a PD controller's own Rd replaces;
and HARDWARE_SPEC §2.11 gives port 1's CC lines to a TUSB320 and makes port 2 a host port, which
leaves no port for a PD sink.

---

## 6. Always-on I²C address map

| 7-bit address | Device | Source |
| :-- | :-- | :-- |
| 0x28 | STUSB4500, ADDR1:0 = 00 | DS12499 §4.1 (0x28–0x2B) |
| 0x40 | INA3221, A0 = GND | SBOS576C Table 7-1 |
| 0x52 | RV-3028-C7 RTC (carrier, ADR-046) | RV-3028-C7 Application Manual Rev 1.4 §5.6 (fixed) |
| 0x55 | BQ27Z561-R2 pack gauge, via `J_PACK` | SLUUC54C §10.2 (fixed) |
| 0x6B | BQ25798 charger | SLUSDV2C §7.3.14.5 |

No conflicts among these. Carrier devices listed in HARDWARE_SPEC §2.9 (TMP112 0x48/0x49, BMA400
0x15, BMP390 0x76, DS3231 0x68 DNP) were not checked against their datasheets here; the TUSB320
and the GPIO expander (part TBD) still need addresses.

---

## 7. Test points and bring-up order

**Test points** (1.0 mm pads, labelled, as HARDWARE_SPEC §7.8): `VBUS_IN`, `PMID`, `VSYS`,
`REGN`, `PACK_P`, `VDD_3V3_AON`, `5V_SYS`, `3V3_GNSS`, `5V_LOAD`, `SOLAR_IN`, `HARV_OUT`,
`HARV_EN`, `NTC_GATE`, VSTOR (U7 pin 15), `CHG_CE_N`, `CHG_INT_N`, `CHG_STAT`, `CHG_TS`, `CHG_ILIM`,
`I2C_AON_SDA`, `I2C_AON_SCL`, CC1, CC2, U1 SW1 and SW2, U6 SW, and `GND` × 4.

**Bring-up order.** The method for cold resistance checks is `FIRST_BOOT_CHECKLIST.md` §2; the
bench instruments are `DEV_KIT_BENCH.md` (§6 adds EVT-0); what a green suite does and does not
prove is `HARDWARE_VERIFICATION_WORKFLOW.md`. Steps specific to this board:

1. Cold resistance on every rail test point. No pack, no VBUS.
2. Bench supply (current-limited) on `J_PACK` `PACK+`/`PACK−` instead of a pack, NTC positions
   fitted with fixed resistors. Expect `VDD_3V3_AON` at 3.3 V across the supply's sweep down to
   the pack minimum, the charger at 0x6B, and `CHG_CE_N` high.
3. Prototype smart pack on `J_PACK`: the gauge answers (§6), reads pack voltage, and reports a
   positive current while charging (SLUSCY0C §6.4.2.1). The protector's OVP/UVP/OCD/OCC/SCD trips
   are pack qualification, tested on the pack board, not here.
4. Host disconnected. Apply 5 V at `VBUS_IN` with the pack supply at the protector's UVP region and
   at 0 V. Scope `CHG_CE_N`, `VDD_3V3_AON` and SW1 together: record whether CE is ever low while the
   converter switches (open item 3). This is the hold-off proof without firmware.
5. Host connected. Run §3.2 steps 0–7 including 6a; confirm the read-back; measure termination at
   `battery.charge_limit_v` on a cell simulator (supply plus load), then on the one real pack.
   Present a pack (or gauge) whose charge-voltage parameter differs: `CHG_CE_N` must stay high.
5b. CE pad freeze (open item 19): with the host driving `CHG_CE_N` low and the charger charging a
   cell simulator, put the RP2350 into each low-power state its firmware can use (and pull its
   core supply on the Pico 2). Record whether `CHG_CE_N` stays low. Any state that holds it low is
   forbidden while charging until a hardware gate exists.
6. NTC: replace the pack NTC with a resistance decade at the T1/T5 values; confirm charge suspend at
   both (AGENTS §4.1) before leaving a real pack on charge. Repeat on `NTC_GATE` with VBUS absent:
   `HARV_EN` low outside the window, high inside; low with `NTC_GATE` open, shorted, and with the
   pack removed (§2.7.1).
7. PD: probe CC1/CC2 to GND at 0 V for Rd (`USB_ROBUSTNESS.md` R2), then a real PD charger; read
   the contract and confirm `VBUS_IN` and the ILIM clamp.
8. `EN_5V_SYS` high: 5 V rail into an electronic load; load steps up to the CM5 peak once known.
   With EN low, measure `5V_SYS` (open item 10).
9. Load switches: off-state leakage on `3V3_GNSS` and `5V_LOAD`.
10. Floor: every load off, host idle, DMM in J_IBAT; it includes U12 and the `NTC_GATE` bias.
    J_IBAT does not see the pack's own gauge and protector current (they sit on the cell side of
    `J_PACK`); measure those at the cell tabs of the pack before calling the floor `measured`.
    This is the power-tree part of G12, not the device floor.
11. Harvester: supply plus series resistor into `SOLAR_IN`, `NTC_GATE` inside the window; confirm
    charging stops at VBAT_OV, below `battery.charge_limit_v`.
12. INA3221 readings against the DMM on each channel.

---

## 8. Open items

**Host header voltage (bring-up):** power the Pico 2 from `VDD_3V3_AON` with its own regulator
disabled (`3V3_EN` low, external 3.3 V on its `3V3` pin), so its I/O never sits above the AON rail
and back-feeds the gauge, charger and INA3221 through their input clamps.

Items closed by ADR-048 keep their numbers so references stay valid.

1. **AON rail source.** This package feeds the TPS63900 and the 5 V boost from VSYS (§1.2);
   HARDWARE_SPEC §2.3 says VBAT. Owner to confirm.
2. **Closed (ADR-048).** The always-on rail is the TPS63900 buck-boost (§2.5), regulated 3.3 V over
   its whole input range, so the TPS62840 dropout problem is gone.
3. **CE race with a flat pack** (§3.1). If step 4 shows CE low while switching, pull CE up from a
   rail that exists before the charger switches (REGN does, but RP2350 pad tolerance to it is
   unverified) or add a discrete gate. Changes `PIN_BUDGET` polarity only if a FET inverts it.
4. **Closed (ADR-049).** Gauge address 0x55, fixed (SLUUC54C §10.2); chemistry closed by ADR-048.
5. **Rd rule vs a PD controller.** `USB_ROBUSTNESS.md` R1/R2 require discrete 5.1 kΩ ±1 % Rd; the
   STUSB4500's own Rd is ±10 % and a discrete Rd in parallel would halve it. Owner to restate R1.
6. **STUSB4500 on an unpowered I²C bus.** It is powered only from VBUS; its behaviour with SCL/SDA
   pulled up while unpowered is not stated. EVT-0 has 0 Ω links to drop it off the bus; measure.
7. **Closed (ADR-048).** STUSB4500 chosen; it has no D+/D−, so the BQ25798 owns them.
8. **USB-C port roles.** HARDWARE_SPEC §2.11 puts a TUSB320 on port 1's CC and a host switch on
   port 2, yet §2.3 sinks PD and solar on those ports. One CC controller per port: decide which port
   is the PD sink.
9. **Input OR-ing.** The BQ25798 has a native two-input mux (VAC1/VAC2, ACDRV, §7.3.5); the BOM adds
   two LM66100. Decide at carrier capture.
10. **5 V boost off-state.** The re-selected boost (§2.6) must disconnect its output when EN is low,
    or `5V_SYS` sits near VSYS with the CM5 "off", breaking the hard-off rule (AGENTS §4.2); otherwise
    a load switch is needed. Its minimum input must sit below the pack protector's UVP.
11. **Bezel strip.** Its open-circuit voltage must stay within VIN_DC's 3.0 V operating maximum
    (SLUSAH0G §7.5); the `SOLAR_ADC` divider waits for the strip part.
12. **Closed in topology (ADR-048).** The harvester's thermal window is the hardware gate in §2.7.1;
    its parts are open item 18.
13. **5 V boost part.** Re-selection from an in-production part with a datasheet in hand (ADR-048);
    its frequency, compensation and current-limit parts then need the CM5 peak current.
14. **INA3221 shunts** need each rail's maximum current (§2.9).
15. **`J_PACK` sixth pin and gauge INT.** ADR-048 allows 5–6 pins. This package uses the sixth for
    `NTC_GATE`, because the charger's TS bias (REGN) is off on battery alone without firmware (§2.3).
    The alternative is a 5-pin connector with the gate comparator on the pack board, which puts
    harvester circuitry in every replaceable pack. The gauge's INT is not worth a contact: the host
    polls `InterruptStatus()` for the same flags (§2.3). **Recommended (ADR-049): keep `NTC_GATE`
    on pin 6.** Whether the V2 pack is keyed differently, so a wrong-chemistry pack cannot mate (the
    harvester bypasses step 6a, §2.7.1), is also open. Owner to confirm.
16. **Closed in method (ADR-049): pack charge voltage.** The host reads `ChargingVoltage()` (§3.2 step
    6a). It is set at pack programming, unsealed, by the data-flash "Voltage" parameter of each
    Advanced Charge Algorithm temperature subclass (SLUUC54C §9.5, Table 9-2). **TI's defaults are
    4400 mV (low, standard and recovery ranges) and 4100 mV (high), above the Li-ion limit**, so every
    pack must be programmed: standard ranges at `battery.charge_limit_v`, no range above it, then
    sealed. Still open: SLUUC54C §12.8.51 says MAC 0x00B0 `ChargingVoltageOverride` writes these
    values in SEALED mode, while Table 12-2 says it is not available sealed. If §12.8.51 is right, any
    host can rewrite a sealed pack's limit; test it on the first programmed pack.
17. **Pack protector part.** A Li-ion 1S protector that drives high-side FETs (§1.2 item 2, §4); no
    datasheet in hand, chosen with the cell.
18. **Harvester gate parts.** Comparator U12 and switch U11 (§2.7.1) need datasheets in hand:
    comparator supply current, input range and hysteresis; switch off-state blocking in both
    directions.
19. **CE pad frozen low (RP2350 pad isolation, §3.1).** If the RP2350 core powers down while it
    drives `CHG_CE_N` low, the pad latches low (RP2350 datasheet §9.7) and the 10 kΩ pull-up never
    acts, so the charger keeps charging with no firmware watching. The charger's own safety timer,
    JEITA/TS cutoff and VREG still apply, and the pack protector is the backstop, but the hold-off
    is defeated. Fixes, decide at carrier capture: (a) firmware rule: never enter an RP2350
    power-down state while charging, and release CE first (§3.1); (b) hardware gate: drive CE through
    a part that lets CE go high when a firmware heartbeat stops (for example a retriggerable one-shot
    or external watchdog timer gating an open-drain pull-down on CE; part not chosen, no datasheet
    in hand). (a) alone is a firmware promise; (b) closes it in hardware.
    Bench: §7 step 5b.

### 8.1 Existing docs contradicted by the datasheets (not edited here)

| Doc | Says | Datasheet says |
| :-- | :-- | :-- |
| HARDWARE_SPEC §2.3, BOM "Bezel Solar MPPT" (both corrected, ADR-049) | BQ25504 cold-starts at 330 mV, harvests to 100 mV | cold start 600 mV typ / 700 mV max; operates from 130 mV (SLUSAH0G §7.5, revision history) |
| HARDWARE_SPEC §2.3 | NTC NCP18XH103F03RB with β = 3950 K | B25/50 = 3380 K, B25/85 = 3434 K (Murata NCP18XH103F03RB) |
| HARDWARE_SPEC §2.13 | TPS22918 discharges through 470 Ω | internal RPD is tens of ohms (SLVSD76C §6.5 RPD) |
| ADR-035, HARDWARE_SPEC §2.3 | watchdog "fed or disabled" | expiry can restore the Li-ion POR VREG (SLUSDV2C §7.3.2): disable only |
| BOM "Power Gates" vs HARDWARE_SPEC §2.11 | port 2 VBUS on a TPS22918 vs a TPS2051B with a current limit | TPS22918 has no current limit (SLVSD76C), so it cannot meet `usb.port2_current_limit_a` |

Removed as moot under ADR-048: the two TPS62840 rows (part replaced by the TPS63900) and the
BQ27Z561 "TI lists LiFePO4" row (chemistry is now Li-ion).

---

## Appendix A — Datasheets used

| Part | Document | Revision |
| :-- | :-- | :-- |
| BQ25798 | TI SLUSDV2C | May 2020, rev. June 2026 |
| BQ29706 | TI SLUSBU9I (BQ2970 family) | rev. August 2024 (cited only for its low-side FET drive) |
| BQ27Z561 | TI SLUSCY0C | rev. September 2025 (10-page datasheet) |
| BQ27Z561-R2 TRM | TI SLUUC54C | February 2020, rev. March 2024 (address, `ChargingVoltage()`, Advanced Charge Algorithm data flash) |
| RP2350 | Raspberry Pi RP2350 datasheet | build 2026-01-10 (pads §9.3, §9.7, Table 1683; erratum E9) |
| RV-3028-C7 | Micro Crystal Application Manual | Rev 1.4, November 2021 (§5.6 address) |
| STUSB4500 | ST DS12499 | Rev 4, February 2020 (from a mirror; st.com refused the download) |
| CH224K | WCH CH224 datasheet | V2.0 |
| TPS63900 | TI SLVSET3D | March 2020, rev. October 2020 |
| BQ25504 | TI SLUSAH0G | rev. August 2023 |
| TPS22918 | TI SLVSD76C | rev. July 2017 |
| INA3221 | TI SBOS576C | rev. September 2026 |
| NCP18XH103F03RB | Murata product data sheet | as downloaded |
