# SolarDeck Documentation — Read This First

Written 2026-10-20 04:13 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

## Read in this order

| # | Document | Why |
| :-- | :--- | :--- |
| 0 | `../README.md` | What the product is, in 5 minutes |
| 0.5 | `WORKFLOW.md` | **The method.** Claim tags, change classes, lifecycle, non-negotiables, done criteria. Read before your first change. |
| 1a | `AUDIT_2026-10-20_3.md` | **Cost, energy and regulatory truth.** The BOM does not sum; the solar budget is 3-4x optimistic; nothing is certified. Read with 1. |
| 1b | `LONGEVITY_30Y.md` | 30-year failure budget, maintenance schedule, drop physics |
| 1 | `AUDIT_4_2026-10-20.md` | **Latest.** Buildability, supply, reliability, coverage — and the 2034 problem. Read this before the older audit. |
| 1b | `AUDIT_2026-10-20.md` | **What is actually built versus what is written.** 10 blockers, 20 contradictions, the fix plan. Read before trusting anything else. |
| 2 | `MVP_ARCHITECTURE.md` | Dual-brain split, power tiers, state transitions |
| 3 | `HARDWARE_SPEC.md` | Carrier board, buses, pinouts, RF, power |
| 4 | `SOFTWARE_SPEC.md` | Kernel, E-Ink pipeline, power profiles, daemons |
| 5 | `MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md` | XY/Z budgets, tolerances, the actual enclosure |
| 6a | `REGULATORY.md` | Certification matrix — **no certificate, no ship** |
| 6b | `FIRMWARE_INTERFACE.md` | The CM4 <-> RP2350 register contract (header is canonical) |
| 6c | `USB_ROBUSTNESS.md` | Every USB-C failure mode and the rules that close them (gate G11) |
| 6d | `ARCHIVAL_BUILD.md` | Toolchain survival, offline reproducible build |
| 6 | `HARDWARE_VERIFICATION_WORKFLOW.md` | What each verification phase proves, and what it does not |
| 7 | `BOM_COST_ESTIMATE.md` | $385.40-$410.40 across 61 line items, supplier sourcing |
| 7b | `LONGEVITY_30Y.md` | The 30-year failure budget, service kit, maintenance schedule, gates G7-G10 |
| 8 | `OFFGRID_TACTICAL_SENSORS.md` | Field/maritime/foraging sensing, 7 Hotpacks, daemon catalog |
| 9 | `STANDOUT_FEATURES.md` | The 7 product pillars and 7 feature chapters |
| 10 | `FIRST_BOOT_CHECKLIST.md` | Bench bring-up and acceptance gates |
| 11 | `INDEX.md` | Cross-reference table: claim → file § |
| 12 | `90-history/decisions.md` | Why things were dropped. ADR-001…ADR-016. |
| 12b | `REVIEW_PACKET.md` | What to ask an external reviewer, and in what order |
| 13 | `HANDOFF_TO_FABLE.md` | Reviewer checklist before any purchase |

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
4. `python3 scripts/verify_all.py` before every push (16 phases, ~1.2 s).

## Deliberately not split (yet)

`HARDWARE_SPEC.md` (1,427 lines) and `SOFTWARE_SPEC.md` (1,333 lines) are monolithic on purpose.
Roughly 200 cross-references in this repo cite them as `docs/HARDWARE_SPEC.md §2.5`, so a physical
split would silently break every one of them. The proposed per-subsystem split and the rules for doing
it safely are in `AUDIT_2026-10-20.md` §4. Add per-file tables of contents now; split when the
reference count drops or the refs are rewritten as anchors.
