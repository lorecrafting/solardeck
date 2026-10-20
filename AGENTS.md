# AGENTS.md — SolarDeck Engineering Guide

Written 2026-10-20 05:10 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

**Read `docs/WORKFLOW.md` before your first change.** It is the operating procedure: claim tags,
change classes, the intent→ledger lifecycle, the 13 non-negotiables from the audit, and the
definition of done. This file is the map and the hard rules; that file is the method.

Start here, in order: `docs/README.md` → `docs/AUDIT_2026-10-20.md` → the spec you touch →
`docs/WORKFLOW.md`.

---

## 1. What SolarDeck is

An open-hardware, sunlight-readable 10.3" colour E-Ink mobile workstation and tactical terminal
running mainline bare-metal Linux. Open hardware; CERN-OHL-S-2.0 + MIT, see `LICENSES/PATHS.md`.

| Subsystem | Design | Spec |
| :--- | :--- | :--- |
| **Dual-brain compute** | Raspberry Pi CM4 (quad A72, 4/8 GB, 32 GB eMMC) running Linux; RP2350B co-processor at 10 µA sleep / 4.5 mW reader mode handling RTC, ADC solar sampling, PSRAM frame cache and S2idle wake. Bus isolation via a pair of TI TMUX1575 4-channel switches (two devices = 8 channels). | `docs/MVP_ARCHITECTURE.md` |
| **Display** | 10.3" Kaleido 3 / Kaleido 4 (colour) or Carta 1200 (mono), 1872×1404, driven by an IT8951 EPDC. Frame rates are per-rectangle, not per-screen; colour motion is unsupported. All figures: `spec_values.refresh_modes`. On-top Wacom EMR variants require the pen/refresh arbiter. | `docs/HARDWARE_SPEC.md` §2.2, `docs/SOFTWARE_SPEC.md` §51–52 |
| **Power** | LiFePO4 26–32 Wh, BQ25895 charger + USB-PD sink, 0.15 W solar bezel strip (larger harvest is an accessory), TPS62840 always-on rail, TPS22918 peripheral load switches | `docs/HARDWARE_SPEC.md` §3 |
| **Comms** | M.2 Key-B LTE (EG25-G), SX1262 LoRa on the RP2350, USB-C only (the pogo bus is descoped) | `docs/HARDWARE_SPEC.md` §2.5 |
| **Ergonomics** | External USB-C/BT keyboard only — no keyboard firmware in this repo (ADR-001). Rear M2.5 inserts + MagSafe anchor array for grips, tripods, easel arms. | `docs/MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md` |

Fabrication status is **not** implied by a green CI run. See `docs/AUDIT_2026-10-20.md`.

---

## 2. Repository layout

```
.
├── README.md                  # Executive overview, pillars, specs table
├── AGENTS.md                  # This file: map + hard rules
├── CONTRIBUTING.md            # How to propose, build, verify, submit
├── SECURITY.md                # Threat model, key handling, disclosure
├── LICENSE, LICENSES/         # CERN-OHL-S-2.0 / MIT / CC-BY-SA, per-path map
├── CHANGELOG.md
├── docs/
│   ├── README.md              # Reading order + claim-status vocabulary (start here)
│   ├── WORKFLOW.md            # THE METHOD: tags, classes, lifecycle, done criteria
│   ├── spec_values.json       # Single source of truth for every quantitative claim
│   ├── AUDIT_2026-10-20.md    # What is measured/modelled/aspirational, and what is broken
│   ├── INDEX.md               # Generated cross-reference table
│   ├── MVP_ARCHITECTURE.md    # Dual-brain split, power tiers, state transitions
│   ├── HARDWARE_SPEC.md       # Carrier board, buses, pinouts, RF, power
│   ├── SOFTWARE_SPEC.md       # Kernel, E-Ink pipeline, power profiles, daemons
│   ├── BOM_COST_ESTIMATE.md   # 61 line items, supplier sourcing
│   ├── MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md
│   ├── HARDWARE_VERIFICATION_WORKFLOW.md   # What each phase proves, and what it does not
│   ├── OFFGRID_TACTICAL_SENSORS.md         # Field/maritime/foraging sensing, 7 Hotpacks
│   ├── STANDOUT_FEATURES.md
│   ├── FIRST_BOOT_CHECKLIST.md
│   ├── HANDOFF_TO_FABLE.md    # Reviewer checklist before any purchase
│   └── 90-history/decisions.md             # ADR-001…019, why things were dropped
├── hardware/                  # KiCad 8 (partial capture), netlist, trap audits
│   ├── verify_schematics.py, audit_hardware_traps.py, export_production_zip.py
│   ├── enclosure/             # solardeck_chassis.scad + verify_enclosure.py
│   └── production/            # generated bundles + verify_manufacturing_package.py
├── firmware/rp2350/           # Bare-metal C (Pico SDK): state machine, ADC, RTC, wake
├── src/daemons/, src/dts/     # eink-refreshd, telemetryd, device-tree overlay
├── config/                    # sway, waybar, foot, mako, gammastep
├── tools/provision/           # setup_solardeck_os.sh (--test)
└── scripts/                   # verify_all.py, check_docs_numbers.py, check_bom_coverage.py
```

---

## 3. Hard rules

### 3.1 Numbers
One file: `docs/spec_values.json`. Never hard-code a dimension, capacity, PPI, count or fps in prose or
in a test. Reference the key; `scripts/check_docs_numbers.py` (Phase 10) enforces it. `verify_enclosure.py`
reads the same file, so CAD and spec cannot disagree.

### 3.2 Claims
Every figure is `measured <date>`, `datasheet`, `modelled`, `aspirational`, or `null`/TBD. Untagged =
defect. Unknown numbers stay `null` with an ADR saying what unlocks them — never an estimate dressed as
a spec. Details: `docs/WORKFLOW.md` §1 and §5.

### 3.3 Search
`ast-grep`/`sg --json` for structural code queries; `rg` for config and prose; `kicad-cli` for
hardware. Do not text-grep a syntax tree.

### 3.4 Change discipline
Classify as C1 CLAIM / C2 DESIGN / C3 SOFTWARE / C4 HYGIENE / C5 RELEASE (`docs/WORKFLOW.md` §2) and
supply that class's evidence. Non-trivial logic ships with one runnable `assert`-based check. Ponytail
ladder: YAGNI → reuse → stdlib → native platform → existing dependency → one line → minimum code.

### 3.5 Verification
`python3 scripts/verify_all.py` before every push. Green means *internally consistent*, never
design-approved. If the suite cannot catch your change, the assertion you add is part of the change.
Never lower a threshold to pass; raise the artifact or downgrade the claim.

### 3.6 Generated files
Netlists, gerbers, BOM exports, bundles, `docs/INDEX.md` and BOM tables are generated. Regenerate from
source in the same commit. Never hand-edit them.

### 3.7 Self-review
One pass over the real `git diff` for correctness, edge cases, safety, leftover superseded prose, and
attribution before you call the task done.

---

## 4. Safety constraints (never trade these for a smaller diff)

1. **LiFePO4 only.** 3.2 V nominal, 3.65 V charge limit. Never configure 4.2 V Li-ion parameters.
   Verify NTC cutoff behaviour before any charging change.
2. **Sleep power.** TPS22918 loads hard off in S2idle; the gate is measured (<25 mW), not assumed
   (`docs/FIRST_BOOT_CHECKLIST.md` §5b).
3. **Waveform DC balance.** Any LUT change must keep net DC bias ≈ 0 V across refresh cycles. Fast-mode
   bursts need a forced balanced cycle; pigment burn-in is permanent (`docs/SOFTWARE_SPEC.md` §52).
4. **RF limits.** CC1101/SX1262 respect regional ISM bands and EIRP (915 MHz NA, 868 MHz EU). No
   transmission config ships without the region.
5. **Input validation at trust boundaries** and error handling that prevents data loss are never
   simplified away.

---

## 5. Attribution (required)

- **Commits:** `Co-Authored-By: <model display name> <noreply@anthropic.com>` and
  `Harness: pi (<provider>/<model>, session <8-char id>)`, added with `git commit --trailer`.
- **Documents/records:** `Written <YYYY-MM-DD HH:MM> UTC in the Pi harness by <provider>/<model>` in the
  header or at the start of the appended section.
- **Tracker comments:** `[Pi · <provider>/<model> · session <id>]`.
- Subagents and reviewers you launch inherit these rules — put them in the prompt.
