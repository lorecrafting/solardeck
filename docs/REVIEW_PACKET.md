# REVIEW_PACKET.md — What to Ask Opus and Fable, and in What Order

Written 2026-10-20 13:55 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Revised 2026-10-21 16:03 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

Revised 2026-10-21 18:51 UTC in Claude Code by anthropic/claude-opus-5-5 (checkpoint after ADR-044–046; Q6 added).

Revised 2026-10-21 19:45 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

Revised 2026-10-21 20:42 UTC in Claude Code by anthropic/claude-opus-5-5 (pre-bench close-out and freeze, ADR-049).

Revised 2026-10-21 20:54 UTC in Claude Code by anthropic/claude-opus-5-5 (EMR inquiry policy, ADR-050).

Five internal audit rounds are done, the last against the datasheets (AUDIT 6). Further internal reading has near-zero yield; the open questions
are judgement calls that need an outside opinion. This is the brief for that review.

State of the repo at this checkpoint (2026-10-21): every verification phase green, run locally before
every push (no hosted CI, ADR-046); **nothing measured** (`docs/STATUS.md`); the schematic is an unwired
placeholder; every CM5/RP2350 pin is budgeted and checked (`docs/PIN_BUDGET.md`); no fabrication files;
software frozen until hardware exists; every EVT-0 part picked from a datasheet and every BOM row priced
except the panel, its controller and the battery pack (ADR-049); the repo is frozen until bench parts, E Ink
and the EMR quote arrive; the reliability model (`spec_values.reliability`) puts random
failure far beyond the first hard wear-out.

---

## Read this first (20 minutes, in order)

1. `docs/AUDIT_6_2026-10-21.md` — the repo checked against the datasheets; blockers and decisions.
2. `docs/STATUS.md` — the honest evidence page. Note `measured: 0`.
3. `docs/90-history/decisions.md` — ADR-001…050. **This is the highest-signal document in the repo**:
   it records decisions reversed by evidence, the V1 scope cut (ADR-034, ADR-044) and the pin budget (ADR-045).
4. `docs/LONGEVITY_30Y.md` §1b — the reliability arithmetic.
5. `docs/FIRMWARE_INTERFACE.md` + `firmware/rp2350/include/solardeck_regs.h` — the only artifact that
   proves a firmware behaviour.

Do **not** start with `HARDWARE_SPEC.md` (1,500 lines) or `SOFTWARE_SPEC.md` (1,400 lines). They are
internally consistent and already machine-checked; reading them line by line is the lowest-yield thing
an expensive reviewer can do.

---

## The six questions, in priority order

### Q1 — Is the 30-year claim defensible, or is this a 10-year device?
Facts: the compute is the CM5 (ADR-031); Raspberry Pi has not published its end-of-production year
(`supply_chain.cm5_production_commitment_year` is `null`). The design claims 30 years (to 2056).
Mitigation adopted: socketed DF40 module, published pinout contract, three spare modules (cost at
`spec_values.cm5.price_usd` each).
**Attack:** is that mitigation credible, or is the honest product a 10-year device with a 30-year
maintenance story? What would you need to see to believe the longer claim? Is a socketed module with a
successor-module escape hatch ever actually exercised by real products, or does it always die at the
first silicon change?

### Q2 — Which daemons should never be built?
41 daemons are specified, 2 exist, and a 30-year device with 41 daemons is a maintenance liability.
Software is frozen until hardware exists (ADR-046), so this is the moment to cut the list, not build it.
**Attack:** pick the cut. Which 8–10 earn their place for a survival/tactical/field user, and which are
speculative? Use `docs/STATUS.md` and `docs/OFFGRID_TACTICAL_SENSORS.md` §8. Be brutal; the current
catalogue was written by someone who likes features.

### Q3 — What is the shortest path to three measured numbers?
The pillars (Linux resume from off/hibernate in seconds — S2idle is withdrawn, ADR-036 — typewriter
latency, ambient-mode floor `<25 mW` with the CM5 off) have no measurements and no test points. **Attack:** design the cheapest dev-kit experiment that produces those three numbers
without a full carrier spin. Which can be measured on the display eval board alone? Which need the CM5
and the panel in the same rig? Is a two-board lash-up acceptable for a pillar claim?

### Q4 — Battery, UN38.3, and shipping
1S Li-ion in a user-replaceable smart pack (ADR-048): two EEMB LP7545135 cells in parallel (1S2P,
`battery_wh.li_ion`), BQ298216 high-side protector, fuse and pack-side BQ27Z561-R2 gauge, keyed
Hirose DF63 connector, screws, no adhesive (ADR-049). EEMB claims UN38.3 and IEC 62133 for the cell
but publishes no report; pack-level reports are requested. LiFePO4 is V2. UN38.3 is the longest-lead
gate in the programme (~$8–15 k, 6–10 weeks) and has no owner; a spare pack sold on its own needs it
too. TI's gauge ships with a 4.4 V charge-voltage default, so pack programming is a safety step.
The pack current path is still open (`docs/EVT0_POWER_BOARD.md` open item 20): the protector's OCD
and any off-the-shelf pack fuse sit above the 8 A FET and connector ratings.
**Attack:** does the chosen pack pass UN38.3 and IEC 62133-2, and does the screw-retained pack meet
the EU Battery Regulation's user-replaceability requirement (applicability to confirm)? Which test
house, which schedule, and what does a failed UN38.3 cost?

### Q5 — The piezo reversal (ADR-020)
Audit 2 descoped 4× TDK PowerHap + 2× BOS1901 to a DNP option, on the grounds that adhesively bonded
ceramics at the highest-strain point of a corner drop are the worst fatigue site in the device, costing
localized haptics.
**Attack:** was that the right trade for a field device used with gloves, in sunlight, often one-handed?
If localized haptics matter, is there a non-fatiguing way to get them?

### Q6 — Which display controller, and does a 10.3″ Kaleido 4 exist?
Facts (2026-10-21): E Ink announced Kaleido 4 on 2026-10-15 without public sizes, resolution or a
sampling programme; the only announced device (Hanvon M10C II, China, December) uses E Ink's T2000
timing controller, for which no small-company sampling route was found. The IT8951 drives mono Carta
only. An open FPGA controller (Modos Glider / Caster) already drives Kaleido 3. The CM5 has no built-in
e-paper controller. EMR: Wacom is OEM/NDA-only (W9013 over I²C is proven on mainline Linux); Hanvon
Ugee sells custom EMR modules to businesses but also ships its own Kaleido 4 device, so EMR quotes wait
for the panel and go to several vendors with a neutral inquiry (ADR-050). An E Ink sales inquiry was
sent 2026-10-21.
**Attack:** should V1 commit to the T2000 route (needs E Ink), an open FPGA controller (needs Kaleido 4
waveforms), or keep 10.3″ only if E Ink confirms it — and what is the fallback if Kaleido 4 is not
offered at 10.3″?

---

## What is already settled — don't spend review budget on it

| Topic | Status |
| :--- | :--- |
| TMUX1575 channel count | Fixed; it is 4-channel, two devices are used (ADR-004) |
| Video / 24 fps on E-Ink | Not achievable on this panel; honest ~6 fps mono (ADR-005, `HARDWARE_SPEC.md` §2.5b) |
| Doc/number/BOM consistency | Machine-enforced by Phases 10, 11, 14 |
| USB-C interoperability | 8 rules + 10-row test matrix (`USB_ROBUSTNESS.md`) |
| Materials/30-year process layer | Corner bond, gasket, capacitor policy, torque (§7.6) |
| Firmware contract | Register map + wire test + bidirectional doc check (Phase 15) |
| Redundancy | Rejected on arithmetic; spares instead (ADR-024) |

Known-open, already documented, no opinion needed: thermal model, ergonomics
(one vs two hands), schematic capture (placeholder, 40 of 52 parts, no wires), `tools/archival/` container, RMA/spares/warranty model.

---

## How to report back usefully

For each question: **a verdict, the one fact that changed your mind, and the cost of the change in
dollars and weeks.** A review that produces five verdicts with costs is worth more than twenty
observations. Anything that can be turned into a check belongs in `scripts/verify_all.py` as a new
phase — that is how a finding stops being a comment.
