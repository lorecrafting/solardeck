# SolarDeck Documentation — Read This First

Written 2026-10-20 04:13 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
Revised 2026-10-21 17:52 UTC in Claude Code by anthropic/claude-opus-5-5 (owner decisions, ADR-046).

## Read in this order

| # | Document | Why |
| :-- | :--- | :--- |
| 0 | `../README.md` | What the product is and where it stands, in 5 minutes |
| 1 | `AUDIT_6_2026-10-21.md` | **Latest audit — the repo checked against the datasheets.** Blockers (charger, sleep, panel fit, cell, no wired schematic) and the decisions they need. Read before trusting any number. |
| 2 | `WORKFLOW.md` | **The method.** Claim tags, change classes, lifecycle, non-negotiables, done criteria. Read before your first change. |
| 3 | `STATUS.md` | Generated status of every pillar, gate and feature |
| 4 | `MVP_ARCHITECTURE.md` | Dual-brain split, power tiers, state transitions |
| 5 | `HARDWARE_SPEC.md` | Carrier board, buses, pinouts, RF, power |
| 6 | `SOFTWARE_SPEC.md` | Kernel, E-Ink pipeline, power profiles, daemons |
| 7 | `FIRMWARE_INTERFACE.md` | The CM5 <-> RP2350 register contract (header is canonical) |
| 7b | `PIN_BUDGET.md` | Every CM5 and RP2350 pin, V1 uses and V2 reservations (ADR-045; Phase 15 checks it) |
| 8 | `MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md` | XY/Z budgets, tolerances, the enclosure |
| 9 | `BOM_COST_ESTIMATE.md` | $531.68-$533.68 across 53 line items, before 3 TBD parts (panel, controller, battery pack); a floor — AUDIT 6 H22 |
| 10 | `REGULATORY.md` | Certification matrix — **no certificate, no ship** |
| 11 | `USB_ROBUSTNESS.md` | Every USB-C failure mode and the rules that close them (gate G11) |
| 12 | `LONGEVITY_30Y.md` | 30-year failure budget, service kit, maintenance schedule, gates G7-G10 |
| 13 | `FMEA.md` | Failure family → countermeasure → detector → actuator → gate |
| 14 | `HARDWARE_VERIFICATION_WORKFLOW.md` | What each verification phase proves, and what it does not |
| 15 | `DEV_KIT_BENCH.md` | The bench that turns `modelled` numbers into `measured` ones — the next step |
| 16 | `FIRST_BOOT_CHECKLIST.md` | Bench bring-up and acceptance gates |
| 16b | `EVT0_POWER_BOARD.md` | EVT-0 power-only board (ADR-043, ADR-048): pin-level capture tables, Li-ion smart-pack interface and gauge topology, the charger hold-off register sequence, harvester temperature gate, cell-dependent TBDs, open items |
| 17 | `CO_PROCESSOR_SURVEY.md` | Why RP2350, and the reader frame format |
| 18 | `ARCHIVAL_BUILD.md` | Toolchain survival, offline reproducible build |
| 19 | `STANDOUT_FEATURES.md` | The product pillars in full |
| 20 | `OFFGRID_TACTICAL_SENSORS.md` | Field/maritime/foraging sensing, Hotpacks, daemon catalog |
| 21 | `DECK_BUILDER_LAYOUT.md` | Who can build what: snap-in vs soldered vs fab |
| 22 | `REVIEW_PACKET.md` | What to ask an external reviewer, and in what order |
| 23 | `90-history/decisions.md` | Why things were chosen or dropped (the ADR log) |
| — | `90-history/HANDOFF_TO_FABLE_2026-10-19.md` | The 2026-10-19 reviewer checklist, kept as history (ADR-043) |
| — | `AUDIT_2026-10-20.md`, `AUDIT_2026-10-20_3.md`, `AUDIT_4_2026-10-20.md`, `AUDIT_5_2026-10-20.md` | Earlier audits (repo checked against itself). Historical; AUDIT 6 §5 corrects three of their verdicts. |

## The status vocabulary

Every claim is one of these. Anything unlabelled is **aspirational**.

| Tag | Meaning |
| :--- | :--- |
| `measured <date>` | Bench value, with the instrument and date |
| `datasheet` | Vendor-published figure, sourced to a datasheet |
| `modelled` | Arithmetic or simulation, not yet measured |
| `aspirational` | A design goal. Do not quote it as a capability. |

## How to keep these docs honest

1. Numbers live in `spec_values.json`. Prose references them; nothing restates them.
   `python3 scripts/check_docs_numbers.py` is the enforcement.
2. **Delete superseded text.** Move the reasoning into `90-history/decisions.md` as an ADR. Never
   leave a "descoped" note next to the full spec of the descoped thing.
3. Generated content (BOM tables, phase lists, production bundles) is generated, not authored.
4. `python3 scripts/verify_all.py` before every push (16 phases, a few seconds).

## Deliberately not split (yet)

`HARDWARE_SPEC.md` and `SOFTWARE_SPEC.md` (each ~1,500 lines) are monolithic on purpose.
Roughly 200 cross-references in this repo cite them as `docs/HARDWARE_SPEC.md §2.5`, so a physical
split would silently break every one of them. The proposed per-subsystem split and the rules for doing
it safely are in `AUDIT_2026-10-20.md` §4. Add per-file tables of contents now; split when the
reference count drops or the refs are rewritten as anchors.
