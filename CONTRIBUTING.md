# Contributing to SolarDeck

Written 2026-11-02 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-0731

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:52 UTC in Claude Code by anthropic/claude-opus-5-5 (owner decisions, ADR-046).

SolarDeck is open hardware: a sunlight-readable 10.3″ colour E-Ink mobile workstation running
mainline, bare-metal Linux. Contributions are welcome from hardware engineers, embedded C
developers, Linux/daemon folk, docs writers, and testers who like asserting things. You do not need
to own a prototype to contribute — most contributions verify better than they build.

## The one rule that matters

SolarDeck does not accept a claim without a way to check it. Every quantitative statement in `docs/`
must agree with `docs/spec_values.json`, and every artifact must have a runnable verifier. If you
cannot check your change, say so in the PR instead of asserting it.

```bash
python3 scripts/verify_all.py     # 16 phases, ~2.5s. Must be green before you push.
```

## Reading order (start here, ~20 minutes)

1. `docs/README.md` — what the project claims and the claim-status vocabulary
   (`measured <date>` / `datasheet` / `modelled` / `aspirational` — an unlabelled number is a defect)
2. `docs/AUDIT_6_2026-10-21.md` — the latest audit: the repo checked against the datasheets, and what is broken
3. `docs/WORKFLOW.md` — tags, change classes (C1–C5), the intent→ledger lifecycle, definition of done
4. `AGENTS.md` — the map and the hard rules

Everything quantitative lives in one file: `docs/spec_values.json`. Prose references keys; nothing
restates numbers.

## What a good change looks like

1. **One number, one place.** Dimensions, capacities, PPI, pillar and phase counts live in
   `docs/spec_values.json`. Prose references them; nothing restates them. If you add a new numeric
   claim, add the constant and extend `docs/HARDWARE_VERIFICATION_WORKFLOW.md`.
2. **Smallest working diff.** No speculative features, no abstraction for a single caller, no new
   dependency where the standard library, a kernel interface, or KiCad's own libraries already do
   the job. Delete before you add.
3. **One runnable check.** Non-trivial logic (state machine, parser, power path, money/security
   path) needs an `assert`-based self-test or a small `test_*.c`/`test_*.py`. Trivial one-liners
   do not.
4. **Label your certainty.** `measured <date>` / `datasheet` / `modelled` / `aspirational`.
   Anything unlabelled is assumed aspirational.
5. **Delete superseded text.** Do not leave "descoped" text next to its own full specification.
   Move the reasoning to `docs/90-history/decisions.md` as an ADR and delete the stale section.
6. **Generated files, generated correctly.** Netlists, BOM exports and `docs/STATUS.md` are
   generated. Regenerate from source in the same commit (`python3 scripts/gen_status.py` after doc
   changes). Never hand-edit them. No Gerbers or fab bundles until the PCB is routed (ADR-046).

## Categories of contribution

| Want to help with | Start at | Gate |
| :--- | :--- | :--- |
| Schematic capture (30/62 line items captured) | `hardware/*.kicad_sch`, `hardware/solardeck-carrier.net` | Phase 1 + Phase 11 (`netlist == BOM == CPL`); `kicad-cli sch erc` when installed |
| Routing the board | `hardware/solardeck-carrier.kicad_pcb` | Phase 6 (footprint labels + centroids inside 222×160 mm); `kicad-cli pcb drc` when installed |
| Hardware trap audit (8 rules: islands, galvanic isolation, power domains, banned nets) | `hardware/audit_hardware_traps.py` | Phase 2 — zero traps |
| Firmware / RP2350 co-processor | `firmware/rp2350/` | Phase 3 (contract tests) |
| Host daemons (eink-refreshd, telemetryd, correlate, battcare) | `src/daemons/` | Phase 4 (`test_*.c`), Phase 14 (derived numbers) |
| Mechanical / enclosure | `hardware/enclosure/` | `verify_enclosure.py` reads `spec_values.json` |
| Documentation | `docs/` | Phase 9 (links, attribution), Phase 10 (numbers), Phase 12 (STATUS.json regen) |
| Bench measurements | `docs/FIRST_BOOT_CHECKLIST.md` | Replace a modelled/aspirational constant with a measured value and a date |
| Reliability / longevity / self-diagnosis | `docs/LONGEVITY_30Y.md`, `docs/FMEA.md` | Phases 13 and 16 |

The CI summary prints which phases you gate. A green run means *internally consistent* — never
design-approved. Fabrication status is not implied by green CI; see
`docs/AUDIT_6_2026-10-21.md`.

## Good first issues

These need only `docs/` + a GitHub issue, no board in hand — pick the one that fits your shelf of
interests:

- **Bench-measure a spec value.** Pick an entry in `docs/spec_values.json` tagged `modelled`
  (e.g. `solar_w.bezel_strip`, or the `sleep_ladder.solar_strip_wh_per_day` strip-harvest budget and
  the RP2350 ambient-mode floor; `sleep_ladder` R2 is `null` because the CM5 has no S2idle, ADR-036) and write the measurement procedure + expected-result assertion so
  someone who owns hardware can run it.
- **Close a Phase-11 coverage gap.** The netlist agrees with the BOM and CPL (30 designators), but
  32 line items are still uncaptured. Each one follows `scripts/capture_schematic_parts.py`:
  datasheet-anchored footprint, real LCSC part number, symbol + comp + centroids in lockstep.
  The script enforces the contract; you supply the datasheet.
- **Harden `check_docs_numbers.py`.** Cross-reference a numerical pattern NOT yet enforced
  (e.g. a specific `%` or `Wh` recurrence) with an added test case.
- **Write an ADR from a debate in the issues.** If a decision thread ends in "we should go with X
  because…", capture it as ADR-N+1 in `docs/90-history/decisions.md` and link it from the spec text.
- **Add a trap rule.** `hardware/audit_hardware_traps.py` has 8 rules; see
  `docs/AUDIT_2026-10-20.md` §5 (fix plan) for the next candidate trap.

Always check the issue tracker first — someone may already own it. Say "I'm taking this" on the
issue and reference it in your PR.

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
CERN-OHL-S-2.0 for hardware, MIT for software, CC-BY-SA-4.0 for documentation. By submitting a PR
you agree to those terms for that contribution. If you machine-generate a contribution (LLM, CAD
macro, script), say so — we track attribution honestly and it costs you nothing.