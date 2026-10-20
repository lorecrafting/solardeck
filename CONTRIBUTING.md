# Contributing to SolarDeck

Written 2026-10-20 04:13 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

## The one rule that matters

SolarDeck does not accept a claim without a way to check it. Every quantitative statement in `docs/`
must agree with `docs/spec_values.json`, and every artifact must have a runnable verifier. If you
cannot check your change, say so in the PR instead of asserting it.

```bash
python3 scripts/verify_all.py     # 11 phases, ~1.2s. Must be green before you push.
```

## What a good change looks like

1. **One number, one place.** Dimensions, capacities, PPI, pillar and phase counts live in
   `docs/spec_values.json`. Prose references them; nothing restates them. If you add a new numeric
   claim, add the constant and extend `docs/HARDWARE_VERIFICATION_WORKFLOW.md`.
2. **Smallest working diff.** No speculative features, no abstraction for a single caller, no new
   dependency where the standard library or a kernel interface already does the job. Delete before
   you add.
3. **One runnable check.** Non-trivial logic (state machine, parser, power path, money/security
   path) needs an `assert`-based self-test or a small `test_*.c`/`test_*.py`. Trivial one-liners
   do not.
4. **Label your certainty.** Use the vocabulary in `docs/README.md`:
   `measured <date>` / `datasheet` / `modelled` / `aspirational`. Anything unlabelled is assumed
   aspirational.
5. **Delete superseded text.** Do not leave "descoped" text next to its own full specification.
   Move the reasoning to `docs/90-history/decisions.md` as an ADR and delete the stale section.

## Categories of contribution

| Want to help with | Start at | Gate |
| :--- | :--- | :--- |
| Schematic capture (20/61 parts done) | `hardware/*.kicad_sch` | `kicad-cli sch erc` + `verify_schematics.py` |
| Routing the board | `hardware/solardeck-carrier.kicad_pcb` | `kicad-cli pcb drc` with 0 errors |
| Firmware / daemons | `firmware/rp2350/`, `src/daemons/` | `python3 scripts/verify_all.py` Phases 3, 4a, 4b |
| Mechanical / enclosure | `hardware/enclosure/` | `verify_enclosure.py` reads `spec_values.json` |
| Documentation | `docs/` | Phase 9 (links, attribution) + Phase 10 (numbers) |
| Bench measurements | `docs/FIRST_BOOT_CHECKLIST.md` | Replace a constant with a measured value and a date |

## Hardware safety is not optional

This project specifies a LiFePO4 pack, mains-adjacent USB-PD, an E-Ink high-voltage charge pump, and
sub-GHz transmitters. Changes touching those paths need a second reviewer and a stated failure mode.
Never change a charge voltage, cutoff threshold, or waveform LUT without a written rationale in the
ADR log and an accompanying assertion. LiFePO4 charges to 3.65 V; a 4.2 V Li-ion profile damages the
cell and is a fire hazard.

## Commits and attribution

Use the harness trailers required by `AGENTS.md` (`Co-Authored-By:` and `Harness:`). Documents you
add get a `Written <date> UTC in the Pi harness by <provider>/<model>` line.

## Licensing

Contributions are accepted under the license of the path you touch (`LICENSES/PATHS.md`):
CERN-OHL-S-2.0 for hardware, MIT for software, CC-BY-SA-4.0 for documentation. By submitting a PR you
agree to those terms for that contribution.
