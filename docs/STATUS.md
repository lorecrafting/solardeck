# STATUS.md — What This Project Actually Delivers, and How Sure We Are

Written 2026-10-20 05:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

**Generated file — do not edit.** Source: `docs/spec_values.json` → `features`.
Regenerate: `python3 scripts/gen_status.py`. CI Phase 12 fails if this page is stale.

## Status vocabulary

| Status | Means |
| :--- | :--- |
| `measured` | A bench value from this build or an equivalent dev kit, with an instrument and a date. Nothing here yet. |
| `modelled` | Arithmetic, CAD, or simulation closes. Believable, not proven. |
| `specified` | Designed and documented in a spec section. **No artifact proves it.** |
| `aspirational` | A design goal. Do not quote it as a capability. |
| `TBD` | Unknown, and we refuse to guess. |

`specified` is the honest default for this repo: 55 BOM lines, 40 captured in schematics, 0 board nets.
Read `docs/AUDIT_6_2026-10-21.md` before treating any row here as a purchase decision.

## Totals

| Status | Count |
| :--- | ---: |
| `measured` | 0 |
| `modelled` | 2 |
| `specified` | 58 |
| `aspirational` | 24 |
| `TBD` | 0 |
| **total** | **84** |

## Product pillars

What the product is judged on (`README.md`, “Product pillars”).

| ID | Feature | Status |
| :--- | :--- | :--- |
| P1 | Dual-brain handoff: instant ambient modes on the RP2350, Linux resume in seconds (ADR-036) | `aspirational` |
| P2 | Typewriter-on-paper latency (1-bit DU keystroke, EMR ink, LRA haptics) | `aspirational` |
| P3 | Sunlight-readable; solar tops up the idle co-processor outdoors (ADR-041) | `aspirational` |
| P4 | Form-morphology: 620 g slate, desk easel, modular grips | `modelled` |
| P5 | Field hardening: airgap, LoRa mesh, GNSS, IP54 (V1) / IP67 (V2), rain-lock | `aspirational` |
| P6 | Modular upgrade bridge: ARM/RISC-V SOM, RAM, NVMe | `specified` |
| P7 | Voice-first control: hold-to-talk button, opt-in hands-free wake word, barge-in (ADR-036) | `aspirational` |

## Engineering pillars

The architectural bets that make the pillars possible (`README.md`, “Engineering pillars”).

| ID | Feature | Status |
| :--- | :--- | :--- |
| E1 | Dual-brain display mux (TMUX1575 pair, RP2350 frame cache) | `specified` |
| E2 | Page-turn S2idle ramping and instant turbo | `aspirational` |
| E3 | Universal mechanical anchor (M2.5 inserts + MagSafe array) | `modelled` |
| E4 | Hardware airgap switch with I_off isolation | `specified` |
| E5 | Driverless USB-C external monitor sink | `specified` |
| E6 | Backpack isolation over one recessed USB-C | `specified` |
| E7 | Self-observant hardware: LLM consumes BIST telemetry | `specified` |
| E8 | Thermal viscosity assist (explicitly not a video engine) | `aspirational` |
| E9 | Zero-cost convenience combinations | `specified` |

## Daemons

Host software specified in `SOFTWARE_SPEC.md`. Evidence is derived from `src/daemons/`.

| ID | Daemon | Status | Spec | Evidence |
| :--- | :--- | :--- | :--- | :--- |
| D01 | `solardeck-beacond` | `specified` | §8 | spec only (§8) |
| D02 | `eink-refreshd` | `specified` | §11 | code + test (§11) |
| D03 | `solardeck-covert` | `specified` | §12 | spec only (§12) |
| D04 | `solardeck-vault` | `specified` | §13 | spec only (§13) |
| D05 | `solardeck-sinkd` | `specified` | §15 | spec only (§15) |
| D06 | `solardeck-voiced` | `specified` | §17 | spec only (§17) |
| D07 | `solardeck-dockd` | `specified` | §18 | spec only (§18) |
| D08 | `solardeck-sosd` | `specified` | §19 | spec only (§19) |
| D09 | `solardeck-caliper` | `specified` | §20 | spec only (§20) |
| D10 | `solardeck-diag` | `specified` | §21 | spec only (§21) |
| D11 | `solardeck-inkd` | `specified` | §22 | spec only (§22) |
| D12 | `solardeck-tripwired` | `specified` | §23 | spec only (§23) |
| D13 | `solardeck-sunaim` | `specified` | §24 | spec only (§24) |
| D14 | `solardeck-blackboxd` | `specified` | §25 | spec only (§25) |
| D15 | `solardeck-ghostnavd` | `specified` | §26 | spec only (§26) |
| D16 | `solardeck-sweeperd` | `specified` | §27 | spec only (§27) |
| D17 | `solardeck-soundbridged` | `specified` | §28 | spec only (§28) |
| D18 | `solardeck-stormd` | `specified` | §29 | spec only (§29) |
| D19 | `solardeck-stegod` | `specified` | §30 | spec only (§30) |
| D20 | `solardeck-satweathd` | `specified` | §31 | spec only (§31) |
| D21 | `solardeck-traumad` | `specified` | §32 | spec only (§32) |
| D22 | `solardeck-alternatord` | `specified` | §33 | spec only (§33) |
| D23 | `solardeck-logicanalyzerd` | `specified` | §34 | spec only (§34) |
| D24 | `solardeck-foxhuntd` | `specified` | §35 | spec only (§35) |
| D25 | `solardeck-nvgd` | `specified` | §36 | spec only (§36) |
| D26 | `solardeck-trailboxd` | `specified` | §37 | spec only (§37) |
| D27 | `solardeck-stealthluks` | `specified` | §38 | spec only (§38) |
| D28 | `solardeck-stingrayd` | `specified` | §39 | spec only (§39) |
| D29 | `solardeck-epassport` | `specified` | §40 | spec only (§40) |
| D30 | `solardeck-lensworld` | `specified` | §41 | spec only (§41) |
| D31 | `solardeck-evacd` | `specified` | §42 | spec only (§42) |
| D32 | `solardeck-parasited` | `specified` | §43 | spec only (§43) |
| D33 | `solardeck-soild` | `specified` | §44 | spec only (§44) |
| D34 | `solardeck-timberd` | `specified` | §45 | spec only (§45) |
| D35 | `solardeck-microbed` | `specified` | §46 | spec only (§46) |
| D36 | `solardeck-zen-clock` | `specified` | §47 | spec only (§47) |
| D37 | `solardeck-zen-games` | `specified` | §48 | spec only (§48) |
| D38 | `solardeck-zen-oracle` | `specified` | §49 | spec only (§49) |
| D39 | `solardeck-biked` | `specified` | §50 | spec only (§50) |
| D40 | `solardeck-penarb` | `specified` | §51 | spec only (§51) |
| D41 | `solardeck-refreshd` | `specified` | §52 | spec only (§52) |
| D53 | `solardeck-battcare` | `specified` | §53 | spec only (§53) |
| D54 | `solardeck-nandcare` | `specified` | §54 | spec only (§54) |
| D55 | `solardeck-readerd` | `specified` | §55 | spec only (§55) |

## USB-C Hotpacks

Field expansion modules (`OFFGRID_TACTICAL_SENSORS.md` §8).

| ID | Feature | Status |
| :--- | :--- | :--- |
| H1 | Doomsday sky-scan and SIGINT (passive all-band receiver) (V2, ADR-034) | `aspirational` |
| H2 | Tactical dual-mesh and HF shortwave transceiver (V2, ADR-034) | `aspirational` |
| H3 | CBRN and search-and-rescue environmental pack (V2, ADR-034) | `aspirational` |
| H4 | Precision RTK centimetre survey pack (V2, ADR-034) | `aspirational` |
| H5 | 15 g thermal night-vision and electrical inspection pack (V2, ADR-034) | `aspirational` |
| H6 | 3GPP NTN satellite (Skylo) transceiver and global SAR (V2, ADR-034) | `aspirational` |
| H7 | Sub-surface acoustic and perimeter geophone module (V2, ADR-034) | `aspirational` |

## Accessories

Sold separately; not required for the core tablet.

| ID | Feature | Status |
| :--- | :--- | :--- |
| A1 | Solar Armor 7.13 W MagSafe backplate with 2.5 m shade tether | `specified` |
| A2 | Detached 15-28 W folding solar panel | `specified` |
| A3 | IBC bezel solar upgrade | `specified` |
| A4 | DarkBox faraday pouch | `specified` |
| A5 | 3D-printed thumb grips, tripods and easel arms | `specified` |

## Acceptance gates

The numbers that decide whether a build is field-ready (`STANDOUT_FEATURES.md`).

| ID | Feature | Status |
| :--- | :--- | :--- |
| G1 | Linux resume to first keystroke (target set from the dev-kit bench; ADR-036) | `aspirational` |
| G2 | 1-bit fast-typing latency < 20 ms | `aspirational` |
| G3 | Zen reading power < 5.0 mW | `aspirational` |
| G4 | Outdoor solar top-up of RP2350 idle (indoor 500-lux claim withdrawn, ADR-041) | `aspirational` |
| G5 | Airgap RF radiation 0.000 dBm, 50 MHz-6 GHz | `aspirational` |
| G6 | Zero-brick watchdog rollback < 2.5 ms | `aspirational` |
| G7 | Transit drop survival (1.22 m, 26 orientations) | `aspirational` |
| G8 | Thermal-cycle joint integrity (500 cycles, dR<10%) | `aspirational` |
| G9 | UV & weather durability (ASTM G154 1000 h, dE<3) | `aspirational` |
| G10 | Unpowered storage survival (12 months, data intact) | `aspirational` |
| G11 | USB-C interoperability (10-row matrix, incl. dead-battery Rd) | `specified` |
| G12 | Sleep-ladder energy & resume integrity (R3 hibernate, R4 keep-alive <0.2mW; R2 null per ADR-036) | `specified` |

## How this page stays true

1. A new daemon with a `SOFTWARE_SPEC` heading but no status fails Phase 12 — you cannot add
   a feature without declaring how sure you are about it.
2. Daemon counts, pillar counts and hotpack counts are checked against `spec_values.json`.
3. Evidence is derived from `src/daemons/`, not written by hand. When code lands, the column
   changes by itself; nobody can claim code exists that isn't there.
4. Promotion out of `specified` requires the evidence named in `docs/WORKFLOW.md` §1.
