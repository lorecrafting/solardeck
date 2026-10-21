# REVIEW_PACKET.md — What to Ask Opus and Fable, and in What Order

Written 2026-10-20 13:55 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Revised 2026-10-21 16:03 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Four internal audit rounds are done. Further internal reading has near-zero yield; the open questions
are judgement calls that need an outside opinion. This is the brief for that review.

State of the repo when this was written: **16 verification phases green in ~1.6 s**, 74 catalogued
features with **0 measured**, 61 BOM line items with 24 captured in schematics, and a reliability model
saying MTBF ≈ 114 years against a first hard wear-out at 8 years.

---

## Read this first (20 minutes, in order)

1. `docs/AUDIT_4_2026-10-20.md` — the current state and the three showstoppers.
2. `docs/STATUS.md` — the honest evidence page. Note `measured: 0`.
3. `docs/90-history/decisions.md` — ADR-001…024. **This is the highest-signal document in the repo**:
   it records two decisions reversed by evidence and three parts descoped for reliability.
4. `docs/LONGEVITY_30Y.md` §1b — the reliability arithmetic.
5. `docs/FIRMWARE_INTERFACE.md` + `firmware/rp2350/include/solardeck_regs.h` — the only artifact that
   proves a firmware behaviour.

Do **not** start with `HARDWARE_SPEC.md` (1,500 lines) or `SOFTWARE_SPEC.md` (1,400 lines). They are
internally consistent and already machine-checked; reading them line by line is the lowest-yield thing
an expensive reviewer can do.

---

## The five questions, in priority order

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
**Attack:** pick the cut. Which 8–10 earn their place for a survival/tactical/field user, and which are
speculative? Use `docs/STATUS.md` and `docs/OFFGRID_TACTICAL_SENSORS.md` §8. Be brutal; the current
catalogue was written by someone who likes features.

### Q3 — What is the shortest path to three measured numbers?
The pillars (`<400 ms` glass-to-glass, typewriter latency, S2idle `<25 mW`) have no measurements and no
test points. **Attack:** design the cheapest dev-kit experiment that produces those three numbers
without a full carrier spin. Which can be measured on the display eval board alone? Which need the CM5
and the panel in the same rig? Is a two-board lash-up acceptable for a pillar claim?

### Q4 — Battery, UN38.3, and shipping
LiFePO4 pouch, ~32 Wh, adhesive-free mechanical retention now. UN38.3 is the longest-lead gate in the
programme (~$8–15 k, 6–10 weeks) and has no owner.
**Attack:** does the chosen cell survive UN38.3, and is a pouch the right form factor for a 30-year
serviceable device? Which test house, which schedule, and what does a failed UN38.3 cost?

### Q5 — The piezo reversal (ADR-020)
Audit 2 descoped 4× TDK PowerHap + 2× BOS1901 to a DNP option, on the grounds that adhesively bonded
ceramics at the highest-strain point of a corner drop are the worst fatigue site in the device, costing
localized haptics.
**Attack:** was that the right trade for a field device used with gloves, in sunlight, often one-handed?
If localized haptics matter, is there a non-fatiguing way to get them?

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
(one vs two hands), schematic capture 24→61, `tools/archival/` container, RMA/spares/warranty model.

---

## How to report back usefully

For each question: **a verdict, the one fact that changed your mind, and the cost of the change in
dollars and weeks.** A review that produces five verdicts with costs is worth more than twenty
observations. Anything that can be turned into a check belongs in `scripts/verify_all.py` as a new
phase — that is how a finding stops being a comment.
