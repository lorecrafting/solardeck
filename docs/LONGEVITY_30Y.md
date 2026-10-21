# LONGEVITY_30Y.md — A Tablet That Still Works in 2056

Written 2026-10-20 06:10 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
Revised 2026-10-21 15:59 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:23 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044).
Revised 2026-10-21 17:53 UTC in Claude Code by anthropic/claude-opus-5-5 (RTC chip, jack removed, ADR-046).
Revised 2026-10-21 19:44 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

Second audit round, scoped to one question: **what breaks over 30 years, and is the current design
built to survive it?** The existing audit asked "is the documentation true". This one asks "will the
object still be useful", which is a different failure mode: nothing here is a wiring error, and a
green CI run says nothing about any of it.

Machine-readable constraints: `docs/spec_values.json` → `longevity`.
Enforced by `scripts/check_longevity.py` (CI Phase 13).

---

## 1. The 30-year failure budget

Twelve mechanisms actually kill long-lived electronics. Each row states the physics, what the current
design does, and the required change. **"Gap" means the design as written does not survive the row.**

| # | Mechanism | Physics | Current design (as written) | Verdict |
| :-- | :--- | :--- | :--- | :--- |
| 1 | **Electrolytic dry-out** | Electrolyte loss doubles every ~10 °C; a 105 °C/2000 h part is ~8 years at 40 °C | Zero wet electrolytics; tantalum-polymer + X7R, 10–16 V on 3.3 V rails, 25–50 V on 5 V/solar (`HARDWARE_SPEC.md` §7.1, §7.5) | ✅ **Handled** — keep the 2× DC-bias margin rule, it is what makes X7R survive |
| 2 | **Solder-joint fatigue** | −40…+85 °C cycling, CTE mismatch; DSBGA (TMUX1575 ×2) and WQFN crack first | Nothing. No corner bond, no underfill, no thermal-cycle gate | ❌ **Gap** — corner bond on DSBGA/QFN, and a 500-cycle qualification gate |
| 3 | **Battery wear-out** | Li-ion loses capacity with cycles and calendar age, faster when hot; the cell is the first hard wear-out (`reliability.first_wearout_years`, modelled) | 1S Li-ion in a user-replaceable smart pack (ADR-048): screws, pull tab, keyed connector, no adhesive; pack-side gauge reports state-of-health; Poron swelling relief (§7.4, 0.80 mm) | ⚠ **Service item** — the pack is replaced over the device's life, scheduled by `solardeck-battcare` data; no cell is expected to last 30 years |
| 4 | **Elastomer compression set** | VMQ takes a set; a TPU bumper is impact protection, not a seal | Perimeter 1.5 mm hollow-core silicone gasket, "compressed 30 %" (§4), **no gasket line item in the BOM**, no service interval | ⚠ **Gap** — P/N the gasket as a wear item at 27 % compression (`spec_values.longevity`) |
| 5 | **Adhesive creep / yellowing** | VHB and LOCA migrate and yellow; taped cells are the classic 10-year failure | VHB 5952 used for **glass** (correct: no plastic film, §4.0); battery retention relies on cavity fit only | ⚠ **Gap** — VHB on glass is fine; a taped or untethered cell is not |
| 6 | **NAND retention** | Client SSD unpowered retention ≈1 year at 30 °C; eMMC similar | 64 GB eMMC + 2 TB NVMe, no scrub, no archive warning | ❌ **Gap** — quarterly powered scrub; state plainly that the NVMe is not an archive |
| 7 | **RTC backup cell** | Lithium coin cells leak; rechargeables lose capacity | RV-3028-C7-class RTC (ADR-046) + Seiko MS621FE rechargeable (in BOM), **no documented replacement interval** | ⚠ **Gap** — a 10-year service item, not a redesign |
| 8 | **Display aging** | Charge trapping in capsules; Kaleido colour-filter dye fades under UV | 395 nm UV cut-off in the LOCA (§7.5.3), acid-etched glass, no glued film | ❓ **Unknown** — the only panel is the Kaleido 4 (ADR-032); its colour-filter dye lifespan is `null` (`spec_values.panel_sku.kaleido4_dye_lifespan_years`) until E Ink publishes it |
| 9 | **Connector cycles** | USB-C rated ~10 k cycles; daily charging for 30 years ≈ 11 k | IP68 mid-mount receptacles, 4 through-hole stake tabs, >50 N, **10 000 cycles** | ⚠ **Gap** — raise to ≥20 k cycles and state strain relief |
| 10 | **Fastener/insert creep** | Brass inserts in PA12 creep; over-torque strips the thread | 12 × M2.5 into knurled brass inserts, 500 teardowns, **0.45 N·m**, no threadlocker, screw types uncounted | ⚠ **Gap** — lock the torque in one place, add low-strength threadlocker, cap screw types |
| 11 | **Internal humidity** | Sealed volume still outgasses; condensation on cold-soak | Sensirion SHT40 dew-point telemetry (§7.4.6), GORE vent, rechargeable desiccant pocket (§4.6) | ✅ **Handled** — the best-specified row in the set |
| 12 | **Software rot** | Toolchains, signing keys, and CA certs do not live 30 years | Offline-first, no cloud dependency, source in repo; **no archival build container, no key custody, no cert expiry audit** | ❌ **Gap** — archival container + printed key shares |

Three hard gaps (2, 6, 12) reduce real 30-year survival; five soft ones (4, 5, 7, 9, 10) are
paperwork plus one BOM line. Row 3 is a planned replacement, not a design gap (ADR-048). Rows 1 and 11 are already better specified than most commercial
tablets ever are — do not touch them. Row 8 stays open until the Kaleido 4 datasheet (ADR-032).None of this is exotic: it is all materials, process, and service paperwork, which is exactly why a
schematic/netlist audit could not see it.

---

## 1b. Reliability arithmetic: random failure is not the risk (modelled)

`python3 scripts/reliability_model.py` sums ~935 FIT across 13 categories (V1 parts only; the V2 modem and LoRa rows left with ADR-034/044) (Telcordia SR-332-class
rates at 40 °C, placement counts estimated from `HARDWARE_SPEC.md`):

**MTBF ≈ 1,070,000 h ≈ 122 years.** Compare that with the first *hard* wear-out item:

| Item | Years to 70–80 % of spec | Kind |
| :--- | ---: | :--- |
| Li-ion cell (smart pack) | 3 | user-replaceable pack, swapped on `solardeck-battcare` data (ADR-048) |
| Silicone gasket | 8 | wear part in the service kit |
| RTC backup cell | 10 | socketed |
| Frontlight LED string (L70) | 15 | 3 h/day at 40 % |
| Display capsules | 20 | ghosting budget, not failure |

**Conclusion: a 30-year life is limited by wear-out and availability, never by random failure.** That
settles a design argument cheaply — do not add redundancy, add spares and service intervals. It also
means an FIT argument for a redundant charger or dual RTC would be spending money on the wrong curve.

The model is `modelled`, not measured, and it is deliberately one number per category so a reviewer can
attack a single assumption rather than the total. Phase 16 fails if this page and `spec_values.json`
disagree.

---

## 2. What to add (all cheap, all checkable)

### 2.1 Materials and process constraints (now in `spec_values.longevity`)
- **Keep the capacitor rule** already in `HARDWARE_SPEC.md` §7.1: no wet electrolytic, 10–16 V on
  3.3 V rails. Add the missing half: **≥2× rated-DC-bias margin**, because X7R can lose 50–70 % of its
  capacitance at rated voltage, and a rail that "passes" on paper is decoupled by a capacitor that is
  effectively absent.
- **Corner bond** (reworkable epoxy at DSBGA/QFN corners), not full underfill — you still want to
  rework a $2 switch in year 12.
- **Conformal coat:** acrylic, reworkable, connectors masked. Not potting: potting makes the device
  unrepairable, which defeats the point.
- **Gasket:** the silicone gasket is already designed (§4); it is missing from the **BOM** and from the
  service kit. P/N it, state 27 % compression (one number, not "30 %" here and 27 % there), and list it
  as a wear item. TPU bumpers are impact protection, not sealing.
- **Fasteners:** 0.45 N·m in exactly one place, low-strength threadlocker, two screw types maximum.
  Thread-forming screws into polymer are limited to ≤5 cycles; everything the user opens uses brass inserts.
- **Surface:** Type III hard anodise, sealed, for salt spray. Salt fog 96 h (ASTM B117) as a gate.

### 2.2 Serviceability as a design input
A 30-year device is a *maintained* device. Add:
- **Service hatch with torque map** — every wear item reachable with one driver.
- **Service kit:** gasket set, battery pack, RTC cell, bumper set, stylus nibs, desiccant. All P/N'd.
- **Maintenance schedule** (see §4) written into the field guide, not left to folklore.
- **3D-printable spares** in-repo as STEP, so bumpers and grips can be remade in 2046.

### 2.3 Two daemons that make aging observable
Only two are needed. Humidity, dew point and temperature logging already exist in
`solardeck-telemetryd` (§7.4.6 / `SOFTWARE_SPEC.md`); a third daemon would duplicate it.

| Daemon | Why 30 years needs it |
| :--- | :--- |
| `solardeck-battcare` | Holds 50 % SOC in storage, logs capacity fade and internal resistance so a pack swap is scheduled by data, not by surprise |
| `solardeck-nandcare` | Quarterly powered scrub of eMMC/NVMe while charging; the only thing that prevents silent bit rot in an unpowered year |

### 2.4 Four acceptance gates
| Gate | Threshold | Why |
| :--- | :--- | :--- |
| **G7** Transit drop | 1.22 m, 26 drops, MIL-STD-810H 516.8 procedure IV, functional after | Corner-drop is the #1 field death |
| **G8** Thermal cycling | 500 cycles −40…+85 °C, no joint resistance drift >10 % | Proves the corner bond |
| **G9** UV/weather | ASTM G154 1000 h, ΔE < 3 and no crazing | PA12 + anodise credibility |
| **G10** Storage survival | 12 months unpowered, then boot + data integrity of OS volumes | NAND reality check |

---

## 3. What to descope

| Item | Why cutting it makes the device live longer | Delta |
| :--- | :--- | :--- |
| **4× TDK PowerHap 0904H014V060 + 2× BOS1901** → demoted to DNP option (ADR-020) | Adhesive-mounted ceramic actuators crack, and four of them are four failure points. The base build uses the single TI DRV2605L + 8 mm LRA footprint that already existed as the DNP fallback. | **−$5.55**, −4 failure modes |
| **Always-on thermal viscosity assist** | Heating the panel accelerates dye fade and the battery's calendar aging. Keep it as opt-in burst mode only. | −$0, −aging |
| **"2 TB NVMe as cold storage"** | It is a working drive, not an archive. Sell the vault microSD + printed/paper archive as the archival path; keep NVMe for LLM weights. | −$0, −false claim |
| **IP67-with-TPU-bumpers claim** | Replace with "IP54 (V1 target), IP67 (V2 target) with the specified gasket; bumpers are impact only" (ADR-039). | −$0, −over-claim |
| **1.0 F supercapacitor zombie mode as a headline** | Supercaps age ~10 years and their ESR doubles. Keep as an accessory capability, not a pillar. | −$0, −claim |

Net: **−$5.55 of BOM is certain** and four failure modes leave with it. The NVMe line is a
positioning change, not a cost saving.

---

## 4. The 30-year maintenance schedule

| Interval | Action | Owner |
| :--- | :--- | :--- |
| Monthly | `solardeck-diag` sweep; env log reviewed only on anomaly | automatic |
| Quarterly | Powered NAND scrub (`solardeck-nandcare`); capacity fade logged | automatic while charging |
| Annually | Gasket compression check, desiccant swap, bumper inspection, torque check | user, 20 min, one driver |
| Every 3 years | Salt/UV inspection of anodise and TPU; stylus nib; vent membrane | user |
| On battcare notice | Li-ion smart pack swap when the gauge's state of health falls below `longevity.battery_soh_service_pct`; typically about 3 years (`longevity.battery_service_interval_years`, modelled; ADR-048) | user, screws + keyed connector |
| Every 10 years | RTC cell, gasket set, bumper set | service kit |
| As needed | Display module (bonded unit), USB-C receptacle | module swap |

Storage rule: if the device will sit unused for months, `solardeck-battcare` parks it at
`spec_values.longevity.storage_soc_pct` and the user is told to power it on once a year.

---

## 5. Drop physics (why the numbers are what they are)

620 g at 1.22 m gives an impact velocity of √(2·9.81·1.22) ≈ **4.9 m/s**. Absorbed over a 2 mm bumper
stroke that is ≈ 600 g; over 4 mm, ≈ 300 g. Therefore:

- **Battery retention must survive 600 g.** A VHB-taped 130 g pouch is 78 N of peel demand — that is
  the single most common "my tablet died" failure on the market. Mechanical clamp + bracket.
- **Glass survives by load path, not by thickness.** Corners 1.2 mm proud of the glass, glass inset
  1.5 mm behind the frame lip, 4+ PCB standoffs so the board cannot cantilever.
- **No unsupported mass over ~5 g** — the cell and NVMe are the candidates and each needs its
  own retention, not connector friction.

---

## 6. The software half of 30 years

Hardware that boots into a dead toolchain is e-waste. Add, in order of cost:

1. **Archival build container** in-repo (`tools/archival/`): pinned base image + toolchain digests, plus
   a `BUILD_FROM_SOURCE.md` that works with no network. This is cheap now and impossible to reconstruct later.
2. **No expiring dependencies:** no TLS certs the device must validate, no DNS dependencies, no
   licence-server calls. `SECURITY.md` states it; a Phase 13 token check enforces the statement exists.
3. **Key custody:** two offline key shares, one printed in the physical vault, one with the owner.
   A 30-year device cannot depend on a forgotten CI secret.
4. **Data format durability:** export paths to plain text/PDF/SQLite only. No proprietary journals.
5. **The firmware is the product.** Ship the source of every binary on the device, and make the golden
   A/B image reproducible from it.

---

## 7. Verdict

The architecture is unusually well suited to 30 years: module sockets, a physical airgap, a
maintenance hatch, an offline-first stack, a capacitor rule that already bans wet electrolytics, and
RH/dew-point telemetry. What is missing is the **process layer** — corner bond and its thermal-cycle
gate, a mechanically retained cell, a gasket line item, a NAND scrub, and an archival build — plus one
false comfort: a "cold storage" NVMe that is not an archive.

Close the four hard gaps in §1, delete two BOM lines of piezo, get a dye lifespan for the Kaleido 4 (ADR-032), and this
moves from "specified" to "plausibly a 30-year object". Nothing on that list needs a new IC.
