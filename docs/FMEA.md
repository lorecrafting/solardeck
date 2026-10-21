# FMEA — Failure Modes & Effects Analysis (the "unite the sensors" spine)

Written 2026-10-20 14:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-0731

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).

Read this document when: adding a sensor, an actuator, a repair hatch, or a gate. It is the single
cross-reference that ties **failure family → design countermeasure → telemetry detector → heal
actuator → verification gate**, so every "robustness" decision lands in all five places at once.

This is not a replacement for `LONGEVITY_30Y.md` (the budget), `HARDWARE_SPEC.md` §21 (BIST + self-heal
actuators), `SOFTWARE_SPEC.md` §3.3 (telemetry tables + AI feedback tiers) or `USB_ROBUSTNESS.md`
(the USB failure taxonomy). It is the *index over* them. Every row references those specs; nothing is
claimed here that is not anchored there. Shares are `modelled` (from literature/field data, not from
SolarDeck measurements — see AUDIT_2026-10-20.md for what measured means) and directionally ordered,
not additive to 100%.

---

## 1. The matrix

| # | Failure family | ~Share (modelled) | Root killer | Design countermeasure | Telemetry detector | Heal actuator | Gate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Connector/contact corrosion & fretting** | 30–40% | Oxide films, vibration micro-movement | §21.5 burnish + IP67 gasketed bulkheads + TPS22918 rail isolation (`spec_values.longevity.conformal_coat` reworkable acrylic covers exposed pads) | `thermal_zones` + `sht40_humidity` (SOFTWARE_SPEC §3.3.1); per-rail sense on gated rails | §21.5 load-switch pulse + burnish cycle | hw bench: burnish measured; corrosion modelled (`DEV_KIT_BENCH.md`) |
| 2 | **Humidity & ingress** | 15–20% | Silver migration, dendrite growth, lens fog | IP54 (V1 target; IP67 is the V2 target, ADR-039) + SHT40 RH/dew-point alarm + desiccant sachet with status (§21.1/21.3) | `sht40_humidity`, `dew_point_*`, `module_health` registers | water-lock daemon (airgap to 0 V) | salt-fog 96 h (ASTM B117) + G9 UV/weather |
| 3 | **Thermal cycling fatigue** | 15–20% | Solder joint cracks, delamination, glue creep | Thermal zones + background waveform temp tuning + §21.5 charge-cut | `thermal_zones` (6 zones) + `battery_health.cell_esr_mohm` | waveform temp tuning (Tier 1) + charge management | G8: 500 cycles −40…+85 °C, <10% joint resistance drift |
| 4 | **Battery cell aging** | 10–15% | Capacity fade, ESR rise | BQ27Z561-R2 SOH tracking (ADR-035), charge management, 30-year budget (`LONGEVITY_30Y.md` §1) | `battery_health.*` (SOH, ESR, cycles) | `solardeck-battcare` (50% SOC storage, swap scheduling) | G10 storage survival + swap by data (§4 schedule) |
| 5 | **Soaking/wet conditions** | 5–10% | USB-C port electrolyte, gasket failure | IP68 ports, water-lock daemon, airgap to 0 V | `module_health` + rail current (port drain detection) | water-lock (airgap) | G7 drop + salt-fog (port closure integrity) |
| 6 | **Shock & drop impact** | ~5% | BGA/corner-bond crack, mount fatigue | Corner bond on DSBGA/QFN (reworkable, §7.6.1), M2.5 inserts, TPU bumpers | BMA400 motion (impact logging) | none (passive) | G7: 1.22 m, 26 drops, MIL-STD-810H 516.8 IV, functional after |
| 7 | **NAND / bit-rot (storage death)** | ~5% | Silent write decay over unpowered years | `solardeck-nandcare` quarterly powered scrub while charging | eMMC SMART, NAND scrub status | NAND scrub (rewrite) | G10 storage survival + `nand_scrub_interval_days` compliance |
| 8 | **Everything else** (EMC, firmware, RF) | ~5% | — | Modular swappable (ADR-024 spares), dual-bank A/B, E-fuses | BIST sweeps (§21.1), `power_rails`, RF rail ammeter | dead-socket power cycle + golden-bank revert; TPS22918 rail reset | G11 USB gates + BIST at each boot |

Columns read as the full chain: a failure family is **defeated** only when all five links exist. If any
cell is empty ("—"), the family is "observed and passively survived", not "self-healed" — that is a
deliberate, stated scope choice, never an accident.

---

## 2. The sense points that make the matrix real

The matrix's "telemetry detector" column is only as good as the hardware that feeds it. To give the
LLM the widest possible picture (the `solardeck-correlate` job and the Tier-2/4 loops read **all** of
these), the board must not ship without:

- **Per-rail current sense on every TPS22918-gated peripheral rail** (GNSS, Wi-Fi, audio, expansion),
  not just the 3 INA3221 channels — a second INA3221 or ADC sense taps on the gated rails. Without
  this, row 1's detector is a guess. This is a **quote-line item for the fab**, not an afterthought
  (`90-history/HANDOFF_TO_FABLE_2026-10-19.md` and `DECK_BUILDER_LAYOUT.md` both carry it).
- **Thermal zones at 6 points** (battery, display backplane, SoC die, RF (GNSS; LoRa is V2, ADR-044), charger rail, audio)
  — each a TMP112, all in `thermal_zones` (`SOFTWARE_SPEC.md` §3.3.1).
- **Module health registers** (ok/waning/fault + numeric) per module, written by BIST and read by the
  Tier-2 export — the "cracked pad under a BGA chip" case stays invisible unless the registers exist.
- **The honest ceiling, restated:** no amount of LLM reasoning turns an un-instrumented failure into a
  detected one. The register health + thermal zone items above are exactly the quote lines that close
  that gap — do not let the fab build the board without them.

Every sensor above maps to a `spec_values` budget key and a row in §3.3.1; adding one without both is
a defect under the repo's numbers rules.

---

## 3. What this doc does NOT claim

- The `~share` column is **modelled directionality**, not measured failure data (that arrives from
  bench/field soak in Rev 1 → Rev 2, via Tier 3 analysis in `SOFTWARE_SPEC.md` §3.3.2).
- A green matrix row does not mean the device "cannot fail" — it means the failure family has a
  designed countermeasure, a detector that will see it, an actuator that can react, and a gate that
  has proved the first link. The detector→actuator wiring is the build work ahead (`solardeck-
  correlate`, telemetryd integration), exactly as the AUDIT docs record.
- No row here authorizes new silicon beyond what `HARDWARE_SPEC.md`/`MVP_ARCHITECTURE.md` already list.
  Rows 1 and 3's sense requirements are *already specced* (INA3221 second unit / TMP112 thermal probes); this
  doc only makes their absence a first-class failure.