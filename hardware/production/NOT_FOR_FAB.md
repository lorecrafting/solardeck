# NOT FOR FABRICATION

Written 2026-10-21 UTC in Claude Code by anthropic/claude-opus-5-5 (ADR-046).

Nothing in this directory can be ordered. The schematic is a partial capture with no wired
connectivity and the PCB is unrouted (AUDIT 6 X8).

`solardeck_bom.csv` and `solardeck_cpl.csv` mirror the placeholder netlist so Phases 6 and 11 can
check that the three agree. They still list pre-V1 parts (ADR-034, ADR-044) and are replaced by the
first real capture, not edited by hand.

The synthetic Gerbers, turnkey bundles, quote guides and the hand-generated chassis STL were removed
(ADR-046): they looked fabrication-ready and were not. The enclosure source is
`hardware/enclosure/solardeck_chassis.scad`. Phase 7 fails if any fab bundle (`*.zip`, `*.gbr`,
`*.drl`) appears here while this file exists. Delete this file only in the same change that adds
Gerbers exported by KiCad from a routed board that passed DRC.
