# SolarDeck Architecture Decision Record

Written 2026-10-20 04:13 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Every descoping, re-derivation and reversal in this project lives here. Specs cite them as `ADR-nnn`.
The rule: **a decided-and-dropped idea is deleted from the spec and recorded once, here.** If a spec
section and an ADR disagree, the ADR wins and the spec is a bug.

Format: trigger → decision → what it cost or saved → what still assumes it.

---

## ADR-001 — SnapDeck keyboard descoped from V1

* **Original plan:** proprietary 5-pin magnetic pogo keyboard, custom Kailh X-switches, CNC aluminum
  chassis, ZMK firmware in `firmware/keyboard/` on an nRF52840.
* **Trigger:** $25,000+ in injection-mold tooling plus ~6 months of mechanical and ZMK bring-up, for a
  feature every buyer can already satisfy with a keyboard they own.
* **Decision:** drop it. Universal M2.5 threaded inserts plus a MagSafe-compatible anchor array let
  any Bluetooth or USB-C keyboard attach; a $20 3D-printed BlackBerry Q20 thumb-grip shell covers the
  handheld case.
* **Delta:** −$32.65 BOM per unit, −$25k tooling, −1 firmware target.
* **Still assumes it:** nothing. `firmware/keyboard/` does not exist and must not be recreated.

## ADR-002 — 8-pin pogo expansion bus descoped

* **Original plan:** 8-pin hermetic magnetic pogo bus on the rear chassis for the RF backpack, with a
  4-pin front variant.
* **Trigger:** pogo pins corrode, pit and mechanically jam under beach sand, volcanic dust and salt
  spray; they cannot hold IP67 across repeated mating without a gasket service interval; the flat rear
  face the MagSafe anchor array needs is incompatible with them.
* **Decision:** USB-C Port 2 (IP68 recessed right-angle) carries USB 2.0 + I2C + power. Hotpacks
  attach mechanically with the MagSafe ring and 4× M2.5 inserts.
* **Delta:** −$4.20 BOM, one receptacle instead of two mating systems.
* **Still assumes it:** `HARDWARE_SPEC.md` §5.3 keeps the old pinout only as historical reference and
  is explicitly marked superseded.

## ADR-003 — Standalone GNSS receiver descoped

* **Original plan:** u-blox MAX-M10S.
* **Trigger:** the Quectel EG25-G already integrates a multi-constellation Qualcomm GNSS engine
  (GPS/GLONASS/BeiDou/Galileo).
* **Decision:** use the modem's GNSS. Losing the dedicated receiver costs TTFF in cold start and
  removes the ability to track with the modem rail cut — accepted.
* **Delta:** −$17.00 BOM, −1 antenna feed.

## ADR-004 — Display bus switch is two 4-channel parts, not one 8-channel part

* **Original claim:** a single "TMUX1575 8-channel SPDT" switch isolating 6 EPDC lines.
* **Trigger:** datasheet check (2026-10-20): the TMUX1575 is **4-channel**, 16-bump DSBGA (YCJ),
  1.4 × 1.4 mm, and there is no `PWR`/TSSOP option. The BOM part number was fictional.
* **Decision:** two TMUX1575 devices = 8 SPDT channels (6 used, 2 spare). BOM PN corrected to
  `TMUX1575YCJR`.
* **Delta:** +$0.85 BOM, +1.4 × 1.4 mm placement.
* **Still assumes it:** `HARDWARE_SPEC.md` §2.2 and §2.25, `README.md` specs matrix, `INDEX.md` §4.

## ADR-005 — MIPI-DSI video engine removed (no 24 fps claim)

* **Original plan:** 2-lane MIPI-DSI from the CM4 into a high-speed bridge/EPDC, GPU blue-noise
  dithering, NEON delta extraction, "24 fps cinema".
* **Trigger:** no shipping e-paper panel has an LVDS input; a DSI→LVDS bridge (SN65DSI83) terminates
  in nothing. E-paper particle motion cannot hold video rates regardless. Separately, a 32 MHz SPI
  link moves a full 1-bit 1872×1404 frame in ~82 ms.
* **Decision:** single-path SPI to the IT8951. Honest budget: ~6 fps full-frame, 15–25 fps for small
  rectangles. The daemon is rectangle-driven, not frame-driven. Video decodes dithered at ~6 fps or
  streams audio-only.
* **Delta:** −$12.90 BOM (bridge, crystals, ESD), −1 differential pair.
* **Still assumes it:** `SOFTWARE_SPEC.md` §2.5 keeps only the thermal-viscosity half; MVP Tier 5b is
  re-scoped to high-motion screen work.

## ADR-006 — Forward-facing camera descoped

* **Original plan:** front 5 MP OmniVision OV5647 with a mechanical ThinkShutter, dual MIPI-CSI.
* **Trigger:** video calls look poor on e-paper; MIPI-CSI routing breaks IP67 sealing; the top bezel
  earns more from solar harvesting.
* **Decision:** rear 12 MP IMX708 (PDAF macro) only. Conferencing is audio-first; a UVC webcam over
  USB-C Port 2 is the opt-in path.
* **Delta:** −$8.50 BOM, −$4.10 shutter/lens.
* **Still assumes it:** `HARDWARE_SPEC.md` §2.6 and `SOFTWARE_SPEC.md` §2.4.

## ADR-007 — Solar: base strip is the product, IBC and Solar Armor are accessories

* **Trigger:** three mutually exclusive solar designs were live at once — the $3.50 IXYS SM141K06L
  strip (0.15 W) in the BOM, a dual-bezel IBC upgrade (1.24 W) in §2.28, and a snap-on
  `SOLAR-ARMOR-V1` panel (7.13 W) in §2.29 — while the CAD modelled one 45 × 15 mm recess.
* **Decision:** the 0.15 W strip is the only V1 base-configuration solar part; it is also the ambient
  light meter and the desk-clock trickle source. IBC bezel and Solar Armor ship as separately priced
  accessories with their own BOM blocks, and the CAD keeps the strip recess only.
* **Delta:** base BOM unchanged at $3.50; accessories priced outside the $388.85 V1 total.
* **Still assumes it:** `README.md` specs matrix, `HARDWARE_SPEC.md` §2.28/§2.29 headers, desk-clock
  runtime arithmetic.

## ADR-008 — Enclosure geometry re-derived (chassis could not contain its own panel)

* **Trigger:** audit 2026-10-20. The mechanical workflow claimed a 12.55 mm device, `CHASSIS_DEPTH` was
  9.8 mm, `HARDWARE_SPEC.md` claimed a 6.0 mm cavity, and the 227.0 × 165.0 mm chassis was smaller
  than the 227.7 × 165.8 mm glass it has to hold.
* **Decision:** outer **232.0 × 170.0 × 14.0 mm**; pocket **228.5 × 166.6 mm** (+0.40 mm per side);
  cavity **12.5 mm**; rear wall **1.5 mm**; display stack **2.65 mm**; PCB **1.20 mm**; cell
  **142 × 90 × 8.5 mm**. Binding branch is display + PCB + cell = **12.35 mm**, clearing by 0.15 mm.
  Mass re-derived **620 g** (from 510 g).
* **Delta:** +2.0 mm thickness, +110 g, +5 mm width, +5 mm height versus the older claims.
* **Still assumes it:** `docs/spec_values.json` is the only place these numbers exist;
  `verify_enclosure.py` reads it.

## ADR-009 — 32 Wh LiFePO4 at 14 mm, not 18 Wh at 10.5 mm

* **Trigger:** the 14 mm envelope forces the trade. 32 Wh of LiFePO4 needs ~8.5 mm of cell; a 5.0 mm
  cell caps the pack near 18 Wh.
* **Decision:** V1 keeps 32 Wh at 14.0 mm and 620 g. A 10.5 mm / 18 Wh "thin" variant is a deferred
  SKU, not a free configuration change.
* **Delta:** +3.5 mm thickness in exchange for 78% more capacity and ~300 days of reading.

## ADR-010 — Dedicated ambient-light sensor descoped

* **Original plan:** TI OPT3001.
* **Trigger:** the top-bezel monocrystalline strip is already a large-area photodiode; the RP2350's
  12-bit ADC reads its open-circuit voltage as a 0–120,000 lux meter.
* **Decision:** no dedicated ALS IC. Calibration constants live in `spec_values.json` and are
  refreshed at each boot against the known cell area and temperature.
* **Delta:** −$1.10 BOM.

## ADR-011 — Custom Flipper Zero clone module descoped

* **Original plan:** proprietary RF backpack with CC1101 Sub-GHz, 125 kHz RFID coil and IR emitters.
* **Trigger:** redundant over-engineering. A real Flipper Zero has its own battery, screen and mature
  firmware.
* **Decision:** operators mount their physical Flipper Zero via the rear M2.5/MagSafe anchors and plug
  it into USB-C Port 2 (or pair over BLE), driving it with `qflipper-cli` on the 10.3" screen.
* **Delta:** −$24.00 BOM, −1 RF subsystem to certify.

## ADR-012 — Internal metal kickstand descoped

* **Original plan:** internal folding friction-hinge kickstand.
* **Trigger:** friction hinges fatigue and leak under IP67 submersion.
* **Decision:** the flush M.2 service hatch (with the 3× MicroSD cold-storage vault and SIM ejector)
  replaces it; the device props on any MagSafe stand, tripod or stylus wedge.
* **Delta:** −$8.00 BOM, −150 g.

## ADR-013 — Integrated solar smart cover descoped (thermal)

* **Original plan:** bi-folding solar cover attached to the tablet face.
* **Trigger:** in direct tropical sun (Hawaii/Arizona) dark unibody surfaces bake past +70 °C.
  E-paper microcapsules degrade above +60 °C and LiFePO4 charging must terminate above +45 °C.
* **Decision:** no attached cover. Prescribe a detached 15–28 W folding USB-C panel in direct sun,
  connected by a 3 m cable, with SolarDeck resting in ambient shade.
* **Delta:** −$18.00 BOM, −220 g, avoids a warranty-voiding thermal failure mode.

## ADR-014 — Electronic e-fuses and 3-stage surge suppression over consumable fuses

* **Original plan:** sacrificial melting fuses and single-stage TVS diodes.
* **Trigger:** a blown fuse needs factory desoldering; a lone TVS burns up under sustained lightning
  or high-energy ESD.
* **Decision:** TI TPS259xx e-fuses (500 ns trip, auto-retry) plus a cascaded GDT + choke + TVS
  filter, with 0.2 mm sacrificial trace notches and `SJ1`–`SJ8` solder-bridge bypasses as field
  escape hatches.
* **Delta:** +$3.40 BOM, field-repairable.

## ADR-015 — RGB "Signal Halo" kept (README's descope claim reversed)

* **Trigger:** the audit found §2.7.1 and `SOFTWARE_SPEC.md` §8 fully specifying a ~$0.30 RGB halo
  while `README.md` claimed it had been descoped and the BOM had no line for it.
* **Decision:** keep it. One part solves zero-watt status indication (solar harvest state, radio
  airgap, recording, low battery) that would otherwise cost a second MCU or a screen redraw. Add the
  BOM row; delete the README descope claim.
* **Delta:** +$0.30 BOM.

## ADR-016 — One source of truth for every quantitative claim

* **Trigger:** audit 2026-10-20 found 20 located contradictions (7 vs 9 verification phases, 300 vs
  227 PPI, "5 pillars" over 13, 35 vs 32 Wh, 4 vs 7 Hotpacks, duplicated HANDOFF section numbers).
* **Decision:** `docs/spec_values.json` holds every number; `scripts/check_docs_numbers.py` (CI Phase
  10) fails the build when prose disagrees; `verify_all.py` derives its phase count from a single
  `PHASES` list; `verify_enclosure.py` reads the same JSON. Tests check the source of truth, not a
  duplicated constant.
* **Delta:** zero BOM cost; ~1.3 s added to CI.
* **Still assumes it:** every doc. Add a new number to the JSON first, then reference it.
## ADR-017 — 24 fps is not a pillar; the panel says no and the bus is not the reason

* **Trigger:** repeated "how do we get to 24 fps" pressure on a 32 MHz SPI IT8951 path (`B3`).
* **Numbers:** a 1872x1404 1-bit frame is 2.63 Mbit. At 32 MHz SPI that is 82 ms of pure transfer
  (~6 fps). The IT8951 also has an 8-bit i80 parallel mode that would move the frame in ~13 ms, so
  transfer is fixable for ~$2 of routing. It is not the wall.
* **Real wall:** an electrophoretic update is a field-driven pigment traverse, frame-at-a-time. The
  panels that hit 24-40 fps (Dasung-class) use a custom TCON with a line-interleaved rolling scan and
  accept heavy ghosting plus periodic full flashes. That is a ~$25-35 part and a multi-month waveform
  and DC-balance program, for mono only.
* **Decision:** built-in panel claims full-frame 1-bit at
  `spec_values.refresh_modes.full_frame_1bit_fps`, partial-rectangle latency at
  `spec_values.refresh_modes.partial_rect_latency_ms`, and **no colour motion**
  (`colour_motion_supported: false`). Video-rate on the built-in panel is an ADR-gated option, not a
  feature. Anyone who needs 24 fps sustained gets a reflective panel accessory, not a firmware rewrite.
* **Delta:** $0. Optional FPGA TCON = ~$25-35 BOM + schedule, declined.
* **Kaleido 4:** fps stays `null` in `spec_values` until measured on the dev kit. Oxide TFT mobility
  makes a rolling scan more plausible, not automatic.

## ADR-018 — Kaleido 4 with the Wacom digitizer over the panel: add an arbiter, defer the fps claim

* **Trigger:** "assume Kaleido 4, with the Wacom digitizer on top."
* **What stays true:** colour electrophoretic refresh is seconds
  (`spec_values.refresh_modes.colour_full_refresh_s`); colour motion remains unsupported regardless of
  panel generation.
* **What changes:** the panel generation moves the fps question from us to the TCON vendor. Kaleido 4
  (Oxide TFT backplane, wider colour count, higher white reflectivity and contrast in the same 10.32"
  envelope and FPC) means the LUT and partial-refresh policy live in the TCON. `kaleido4_fps` is
  therefore `null`, never guessed.
* **New constraint:** digitizer **above** the panel means EMR interrogation bursts and EPD drive pulses
  share the same volume. No shield is possible. Mitigation is `solardeck-penarb` (SOFTWARE_SPEC §51):
  mutual gating of drive and sample, with jitter and stall reported instead of hidden. The earlier
  40/50-pin specification places the digitizer rear-laminated; on-top is the tighter-parallax variant
  and the arbiter is mandatory for it.
* **Stack:** on-top digitizer raises `spec_values.display_stack_mm`; the cavity still closes.
* **Delta:** $0 BOM if gating stays in software; +~$3-6 for a CPLD gate if hardware gating is wanted.
  Rejected: metal shielding over the grid (kills the pen), abandoning pen input (drops a pillar).

## ADR-019 — Fast-feel refresh is a policy, not a panel: adopt the Boox-class ladder

* **Trigger:** "how does Boox Air4C speed up refresh, can we do that?"
* **Mechanism, honestly:** Boox Super Refresh does not beat particle physics. It combines
  GPU-side frame pre-composite, dirty-rectangle partial updates, per-region waveform mode selection,
  and a Regal-class ghost ledger that schedules `GC16` clear passes. The panel is unchanged.
* **Why we can copy it:** the IT8951 already exposes exactly that ladder (`DU`, `A2`, `GL16`, `GLR16`,
  `GLD16`, `GC16`, `INIT`). `GLR16`/`GLD16` are the Regal-class incremental modes. Nothing new needs
  buying; the missing piece is the scheduler.
* **Decision:** `solardeck-refreshd` gains the scheduler in SOFTWARE_SPEC §52: dirty-rect transfer,
  monotonic mode picker, bounded per-tile ghost debt, GPU pre-composite, forced balanced cycle after a
  fast-mode burst. Small-region latency is the metric we publish; screen-wide fps is not.
* **Metric shift:** from "fps" to "latency for the rectangle the user is actually touching". That is
  what makes commercial readers feel fast and it is measurable on our own hardware.
* **Delta:** $0 BOM; scheduler code + Phase 4 ladder/ghost-drain assertions.

## ADR-020 — Quad piezo haptics demoted to a DNP option

* **Trigger:** 30-year audit (`docs/LONGEVITY_30Y.md` §1 row 2, §3). Localized piezo haptics were a
  headline feature and are the device's worst drop-fatigue site.
* **Mechanism:** 4× TDK PowerHap actuators are multi-layer ceramics adhesively bonded to the cover-glass
  perimeter — the highest-strain location in a 1.22 m corner drop (600 g peak). Age and thermal cycling
  work on the same bond. A debonded actuator is a rattle the user cannot fix.
* **Decision:** base build = single TI **DRV2605L** + **8 mm Z-axis LRA** ($2.35), chassis-mounted with
  the actuator mass on the metal frame. The full quad-corner PowerHap + dual BOS1901 footprint stays on
  the board as a **DNP option**; `solardeck-hapticd` supports both.
* **What we lose:** localization. An LRA shakes the frame, not the fingertip. Recorded as a real product
  loss, not a rounding error.
* **Delta:** −$5.55 BOM ($7.90 removed, $2.35 added), −4 failure modes, core BOM total
  $388.85 → **$383.30–$408.30** at 61 line items.
* **Reversible:** one BOM line and one daemon flag. If a buyer accepts a 10-year glass-bond service life,
  populate the option.

## ADR-021 — The 30-year constraint set lives in `spec_values.json`, not in prose

* **Trigger:** the first audit found a *documentation* truth problem, but said nothing about the
  *durability* problem: no corner bond, no gasket line item, adhesive-only cell retention, no NAND scrub,
  no stated RTC service interval. None of these is visible to a netlist checker.
* **Decision:** `docs/spec_values.json` → `longevity` holds 23 machine-readable constraints (drop height
  and peak g, thermal cycles, gasket compression, torque, USB-C cycles, scrub interval, storage SOC,
  service-kit contents). `docs/LONGEVITY_30Y.md` holds the failure budget and the maintenance schedule.
  `scripts/check_longevity.py` (Phase 13) fails the build when a constraint is absent from the artifact
  that implements it.
* **Why a checker and not a review:** every item is presence-of-constraint, not a measurement. No bench
  has run, so demanding numbers would force someone to invent them.
* **Enforced consequences:** HARDWARE_SPEC §7.6 states the six process-layer constraints; the gasket is a
  $2.10 BOM line item; the haptic engine is a BOM line; PowerHap/BOS1901 must **not** appear in the BOM
  (a descope that creeps back is a lost decision); gates G7–G10 exist in STANDOUT_FEATURES and in the
  status catalogue.
* **Delta:** +$2.10 gasket; −$5.55 haptics; net −$3.45 core BOM, plus one checker and one new phase.

## ADR-022 — Gasket compression and fastener torque each get exactly one value

* **Trigger:** the same gasket was "compressed 30 %" in §4 and 27 % in the longevity budget; the same M2.5
  joint was 0.45 N·m in §7.4.1 and 0.25 N·m in a draft. Two numbers for one joint is how a build
  instruction becomes folklore.
* **Decision:** `spec_values.longevity.gasket_compression_pct = 27` and
  `fastener_torque_nm = 0.45`. Prose cites them; Phase 13 fails if HARDWARE_SPEC does not state them.
* **Why those values:** 27 % sits inside the 15–30 % usable range for die-cut VMQ with good recovery;
  0.45 N·m is a safe M2.5 steel-into-brass-insert torque with threadlocker.
* **Delta:** $0. Prevents a future build from over-compressing the seal (which takes a permanent set) or
  stripping a brass insert (which ends the teardown story at cycle 3).

## ADR-023 — The CM4 is a socketed, field-replaceable module (2026-10-20)

**Context.** Audit 4 found a 22-year gap between Raspberry Pi's CM4 production commitment (January 2034)
and this design's 30-year claim. No document in the repo mentioned it.

**Decision.** Treat the compute module as a serviceable part: two mezzanine connectors, no adhesive,
reachable from the service hatch; a published module-side pinout contract; a keep-out that leaves room
for a successor connector layout; and three spare modules bought at build time (~$180).

**Why not a soldered module.** Soldered DRAM and CPU is the planned-obsolescence pattern this project
exists to reject (`STANDOUT_FEATURES.md` §5). It also makes the single most valuable part unserviceable.

**Why not "design a custom SoM".** A custom SoM is a 12-month, six-figure programme that solves the
2034 problem by inventing a new one: you now own silicon availability instead of renting it.

**Consequence, stated plainly.** If no successor module exists in 2034, this becomes a 10-year device
with a 30-year maintenance story. Saying so is cheaper than being caught out.

## ADR-024 — Reliability money goes to spares, not redundancy (2026-10-20)

**Context.** `scripts/reliability_model.py` gives ~1,005 FIT, MTBF ≈ 114 years, against a first hard
wear-out (LiFePO4 cell) at 8 years.

**Decision.** No redundant chargers, no dual RTC, no parallel regulators. Spend on spares, service
intervals, and test points instead.

**Why.** Random failure is 14× further out than the first wear-out item. Redundancy would be bought
against the wrong curve, and every redundant part is itself a FIT contribution and a failure mode.

## ADR-025 — Kaleido 4 is not buyable bare; the K3 + IT8951 module is the pipeline test rig (2026-10-20)

**Context.** `spec_values.refresh_modes.kaleido4_fps` stays `null` (ADR-017/018/020), and AUDIT 5 §5.2
said the path to filling it was "buy the dev kit; measure three numbers". The three numbers there
(S2idle power, wake latency, keystroke latency) are *system* numbers and do need the board — but the
Kaleido 4 *display* answers are unobtainable by any purchase today: E Ink ships no bare K4 panel or
module; K4 is locked to first retail devices (Hanvon M10C II, China-first). It is an oxide-TFT backplane
with a T2000-class TCON — **not** the IT8951, which cannot drive it.

**Decision.** Two test rigs, honest about what each measures:

1. **Display pipeline answers** (partial-rect latency, colour-refresh time, ghosting/DC balance, thermal
   LUT switching — the behaviour `eink-refreshd` §52 schedules against): a ~$200–300 following
   10.3" Kaleido 3 + IT8951 HAT module. These answers are generation-stable pipeline facts and they are
   what the software risk actually lives in. Results are tagged `measured <date> (Kaleido 3)` — never
   promoted to K4 numbers.
2. **K4-specific fps**: stays `null`. The only future path is measuring inside a retail K4 device
   (different TCON — partial credit at best), or an E Ink datasheet. E Ink's announcement figures
   (>40k colours, ~18 fps) are marketing until a spec sheet exists; §3.2 forbids them outright.

**Why.** The dev-kit purchase AUDIT 5 recommended for the display half of the question cannot be made —
"buy the K4 dev kit" is chasing a product that does not exist in any channel. The K3-IT8951 module is
real, cheap, and exercises precisely the pipeline the repo ships (`eink-refreshd`, thermal bands,
rectangle scheduler). The system gates (G1–G3) still need the real board; no display answers those.

**Enforced consequences.** `kaleido4_fps` remains `null` in `spec_values`; `SOFTWARE_SPEC.md:1326`
(ADR-020) wording stays; AUDIT 5 §5.2 reworded so the next reader does not chase an unbuyable kit.

**Delta.** $0 hardware decision; optional ~$200–300 if the refresh pipeline is exercised before the
first board rev.

## ADR-026 — The enrolled voiceprint is co-processor-resident, not a Linux file (2026-11-02)

**Status.** Accepted.

**Context.** AUDIT 5 flagged that the speaker-verification enrollment sitting at
`/etc/solardeck/owner_voice.npy` on the CM4 (SOFTWARE_SPEC §17.2) is a root-writable file: a
root-compromised Linux brain can silently swap the voiceprint or re-threshold cosine similarity,
defeating the entire enrollment-and-rejection design. The documented threat model already keeps the
wake-word and ADC on the RP2350 co-processor; the identity verdict should live in the same trusted
domain that cannot be reached by a Linux network stack.

**Decision.** The 256-d Resemblyzer embedding is flashed to RP2350 non-volatile storage at
enrollment time. The CM4 streams the live sample embedding over the existing CM4↔RP2350 interface and
the co-processor returns an owner/not-owner verdict. Verification runs in the same 14 mW sleep tier as
the wake-word, so rejected speech never wakes the CM4 at all. The CM4 holds no reference copy.

**Why RP2350-resident now instead of "tamper-proofing later".** Retrofitting a trust boundary after
first boards is the expensive kind of later: the enrollment format, the flash layout, and the
verification IPC would all be frozen in a Linux-side design first. The RP2350 already exists, already
owns the wake-word trigger, and already has the 16 kHz PIO DMA audio path (§17 pipeline diagram); the
voiceprint is a few KB of flash. The incremental cost is one IPC contract, not a hardware change.

**What voice identity is, and is not.** Identity is conversational access, never authorization. A
recorded owner sample passes cosine ≥ 0.78 (replay) and a cloned voice can be synthesized — no
threshold change fixes either. Consequential operations (crypto sign, wipe) require live liveness
(challenge phrase) plus physical NFC possession; live cloning remains the named residual threat.

**Enforced consequences.** `spec_values.voice.enrollment_resident = "rp2350-flash"`;
`check_docs_numbers.py` BANNED pattern forbids `owner_voice.npy` and `/etc/solardeck/owner_voice.npy`
returning to any non-historical doc (SOFTWARE_SPEC §17.2 states the co-processor-resident design);
DAEMONS catalogue D06 `solardeck-voiced` keeps `spec_section: 17`.

## ADR-027 — "Watching the LLM" is streaming text, and it gets a measured guarantee, not an fps claim (2026-10-21)

**Trigger.** The README asks what happens when someone watches an LLM work on the tablet. Two
temptations looked seductive and were both wrong: claiming a "smooth" frame rate for the e-ink
display, and treating Boox-style video playback as a target to match.

**Mechanism.** Full-screen e-ink is hard-capped by physics and transport: a single 32 MHz SPI link
to the IT8951 EPDC bounds a full-frame 1-bit refresh at ~6 fps (`spec_values.refresh_modes`), and
colour motion is not supported (`colour_motion_supported: false`, a 1.5 s full-colour cycle). But an
LLM token stream is a moving cursor appending characters inside a ~1-line-high dirty rectangle while
the rest of the page stays frozen — the one workload e-ink renders superbly with per-rectangle
partial updates (DU mode, ≤30 ms, zero flash, and a frozen page costs 0 W to hold).

**Decision.** The product promise is a **streaming-text guarantee**, not a video claim:
`spec_values.token_stream` pins ≥120 wpm at ≤30 ms/update latency, zero flash, ghost residue under a
measured threshold, verified by `eink-refreshd --bench stream`. Actual motion content stays off-panel,
routed to the USB-C monitor-sink surface (`STANDOUT_FEATURES.md` Pillar 8), which is a real
contradiction-free answer to "the device that shows a video screen". A cropped talking-head patch is a
tolerated 1-bit mode, never a guarantee.

**Why a guarantee and not a number.** An fps figure cannot be kept honestly on this transport; a
workload-mapped, bench-measured statement can, and it is exactly the ≤30 ms partial-rectangle
latency the scheduler already delivers. Boox "plays video" by aggressive ghost-chasing and GC
flushes; reviewers' honest verdicts put percieved smoothness at ~4-8 fps on small regions with heavy
ghosting. That behaviour is a tolerated mode here, not a design target.

**Enforced consequences.** `check_docs_numbers.py` already bans old video-rate claims (24 FPS / 30-45
FPS / 30-60 FPS, B3 note). `verify_all.py` now asserts the `token_stream` block exists, that its
`update_latency_ms` agrees with `refresh_modes.partial_rect_latency_ms` (a streaming update *is* one
partial rectangle), and that `full_screen_video` names the monitor-sink path — closing the smoke test
on SOFTWARE_SPEC §2.6.

## ADR-028 — Debian stable is the base distribution; Alpine is a measured fallback, not a default (2026-10-21)

**Trigger.** The spec left a pseudo-choice open: `SOFTWARE_SPEC.md` §1 said "Minimal Debian
Bookworm (Raspberry Pi OS Lite) **or** Alpine Linux for sub-3-second boot times." Two bases with
different libc, init, and package ecosystems cannot both be "the base" — every daemon build, CI
image, and provisioning step would need to be dual-targeted forever.

**Mechanism.** The deciding requirements are the device's own: 30-year lifespan, closed-source
binary apps, and the AI/terminal software ecosystem. Debian stable moves glacially and has a
committed LTS window; Alpine ships a musl userspace that breaks glibc binary builds (Obsidian,
URH, most AI toolchains); Arch/NixOS/Fedora are rolling or non-LTS, which makes the owner the
maintainer forever. Alpine's genuine edge is boot time — but with the S2idle tier the OS never
cold-boots in normal use, so a sub-3-second cold boot is a rare first-boot/upgrade/crash path, not
a power tier.

**Decision.** **Debian stable (Raspberry Pi OS Lite base, trimmed) + a custom mainline LTS kernel +
Sway/Cage Wayland** is the SolarDeck base. The kernel choice is distro-agnostic and stays
"custom mainline ARM64 kernel tracking the newest LTS (6.6 today; the repo's `verify_all.py` Phase 8
provisioning script must not pin an EOL kernel)". Alpine remains an engineered *fallback*, used only
if a bench measurement shows the base genuinely loses a power tier or boot target that the
co-processor cannot cover — not as the default, not without a written measurement attached.

**Why a decision and not a fork.** The base is a deliberately commoditized floor. SolarDeck's owned
value lives in the daemon seam (`eink-refreshd`, `telemetryd`, `solardeck-diag/heal/correlate`), the
custom kernel config, and the co-processor. Every distro choice that splits that seam is a tax.

**Enforced consequences.** `SOFTWARE_SPEC.md` §1 updated to name Debian stable as the base with
Alpine listed as measured fallback only; a BANNED pattern stops any *rolling* distro (Arch/NixOS
unstable/Fedora rawhide) from being stated as the base in non-historical prose.

## ADR-029 — Sway and Cage under Wayland; Hyprland explicitly rejected (2026-10-21)

**Trigger.** The spec already chose Wayland (`SOFTWARE_SPEC.md` §1: Sway tiling WM, Cage kiosk
mode). The question was whether the modern dynamic-tiling compositor (Hyprland) should displace
Sway, given its feature richness.

**Mechanism.** Hyprland's flagship features are 60 fps animations, blur, transparency, and
GPU-accelerated effects — every one of which is a *ghosting or flash event* on electrophoretic ink,
the exact things `eink-refreshd` exists to suppress. It is also heavier (effects pipeline RAM/CPU),
younger (breaking config changes between releases), and without the decade of i3-compatible
parameter stability that 30-year maintainers need.

**Decision.** Keep **Sway** (workstation) and **Cage** (single-app kiosk: reader, dashboard) as the
only compositors. Hyprland is rejected by name. The one portable modern habit — hot-reloadable
composable config — is available in sway and is adopted only if a real workflow demands it (YAGNI
until then). X11 apps run through Xwayland; the specc'd app list is Wayland-native or terminal.

**Enforced consequences.** BANNED pattern on the word `Hyprland` in non-historical prose; the
compositor contract in `SOFTWARE_SPEC.md` §1 stays Sway/Cage.

## ADR-030 — Two panel SKUs, one chassis; bonded panel stays bonded in V1 (2026-10-21)

**Trigger.** The 30-year budget (§LONGEVITY_30Y row 8) concluded only monochrome capsules have a
30-year claim; Kaleido colour dye ages under UV/heat/cycles. The README pitching session then asked
whether "modular" means the user can simply swap the display.

**Mechanism.** Kaleido 4 is a monochrome Carta-class layer with a glued colour filter array on top:
same robust B/W capsules, vulnerable CFA dyes. The failure is graceful (colour desaturates toward
sepia; black/white text keeps contrast), but it is real. The panel is currently a **bonded unit** in
the maintenance schedule (`LONGEVITY_30Y.md` "As needed — Display module (bonded unit)") — VHB on
glass is deliberate and is what makes IP67 and drop survival work. A user-swappable panel means a
connectorized EPDC, alignment frame, and a service hatch that stays sealed across hundreds of
open/close cycles — a genuine design change, not a freebie.

**Decision.** Two SKUs share one chassis and one carrier board:
* **Mono SKU (default, 30-year):** Carta 1200, 227 PPI.
* **Colour SKU (option, decade-scale):** Kaleido 4, honest fade, lifespan `null`
  (`spec_values.panel_sku.kaleido4_dye_lifespan_years = null`) until a factory datasheet figure
  exists — no estimate dressed as a spec.

V1 keeps the VHB-bonded panel as a **service-kit part** (module swap at the "As needed" service
interval), not a user hot-swap. The *future* user-serviceable panel becomes a specified requirement
with its cost attached: connectorized EPDC + IP67 service hatch, gasket as a P/N'd wear item
(compatible with the ADR-021 gasket line). This is recorded as a design direction, not a committed
V2 feature — the ADR pins the trade so nobody re-argues it silently.

**Enforced consequences.** `spec_values.panel_sku` introduced (`mono_default_panel`, `kaleido4_*`);
`check_docs_numbers.py` BANNED pattern forbids any concrete "N-year" lifespan for the Kaleido dye in
non-historical prose while the figure is `null`.

---

## ADR-031 — The CM5 is the compute standard; CM4 text is propagation debt (2026-10-21)

Written 2026-10-21 16:05 UTC in Claude Code by anthropic/claude-opus-5-5. Records the owner's decision
("we are standardizing everything on CM5 not cm4") that `spec_values.cm5` (commit `19a789c`) already
assumed but cited as a non-existent ADR-032.

**Trigger.** `spec_values.cm5` moved V1 to CM5116064 with no decision record, while README, AGENTS,
the specs, the DTS, the schematic and the firmware comments still describe a CM4 (AUDIT 6 H23).

**Decision.** Every SolarDeck build uses the **Raspberry Pi CM5, CM5116064 / SC1608** (16 GB RAM,
64 GB eMMC, on-module Wi-Fi/BT). There is no CM4 variant. Values live in `spec_values.cm5`.

**Because.** 16 GB keeps the local 1–3B model resident in RAM; the wireless variant removes a USB
Wi-Fi peripheral; it stays in the same socketed DF40 module family (ADR-023), so the modularity
thesis holds.

**Delta.** Compute line priced at `spec_values.cm5.price_usd` (BOM rows still carry the CM4 price —
Phase 14 totals must be re-derived when the BOM row changes). More heat under load than CM4 (spreader
and power governor are required, AUDIT 6 H20). The device-tree overlay must be rewritten: on CM5,
GPIO, SPI and I2S sit behind the RP1 I/O controller, so the CM4 overlay does not port unchanged.

**Still assumes.** (1) The CM5 does **not** fix the sleep pillar: its datasheet lists only off,
shutdown (DRAM lost) and ~2 W idle, the same structure as CM4 (AUDIT 6 X4). The sleep ladder must be
built around the RP2350 owning the ambient modes and Linux resuming from off/hibernate. (2) The CM5
end-of-production year is unknown (`supply_chain.cm5_production_commitment_year: null`) until Raspberry
Pi publishes it. (3) Whether the carrier still needs a separate USB 3 host controller (VL805) depends
on the CM5's native USB pin-out — verify against the CM5 datasheet before the schematic is captured.

**Enforced consequences.** `spec_values` citations point here; `soc` corrected to BCM2712 (CM5
datasheet). Remaining CM4 references outside `90-history/` and `AUDIT_*` are stale text to be swept,
not a competing design.

---

## ADR-032 — Kaleido 4 is the only panel; V1 waits for its release (2026-10-21)

Written 2026-10-21 16:05 UTC in Claude Code by anthropic/claude-opus-5-5. Records the owner's decision
("let's standardize around Kaleido 4, we will wait for the release"). **Supersedes ADR-030's two-SKU
split**: there is no mono Carta default.

**Trigger.** ADR-030 made mono Carta the default and Kaleido 4 an option. AUDIT 6 found that neither
the named mono panel's outline (X5) nor its resolution matched the repo, and that Kaleido 4 is the
colour product the owner wants to ship.

**Decision.** SolarDeck has one display: the **E Ink Kaleido 4** 10.3" colour panel. Schedule waits for
a buyable panel and a published datasheet rather than shipping an interim panel.

**Because.** One panel means one chassis, one waveform set and one software pipeline to qualify;
colour is the product.

**Delta.** Every panel fact is unknown until E Ink publishes a 10.3" Kaleido 4 datasheet and drawing:
resolution, PPI, module outline and thickness, controller/TCON and its host interface, waveform
timings, price, and dye lifespan. Each stays `null` in `spec_values.panel_sku` (WORKFLOW §5). The
chassis cannot be closed until the drawing exists (AUDIT 6 X5 folds into this). The IT8951 cannot
drive Kaleido 4 (ADR-025), so the carrier's display path, the TMUX1575 hand-over and the RP2350
reader tier must be re-checked against whatever controller E Ink pairs with it.

**Still assumes.** (1) The Kaleido 3 / Carta + IT8951 module stays the **bench stand-in** for the
refresh pipeline (ADR-025); its results are tagged `measured <date> (Kaleido 3)` and never promoted to
Kaleido 4 numbers. (2) The 30-year display claim was built on monochrome capsules (ADR-030); with a
colour-only product, the display row of `LONGEVITY_30Y.md` must quote the dye lifespan as `null`.
(3) `spec_values.ppi` (227) and the prose quoting it describe the stand-in panel and go `null` in the
same sweep that moves every doc to Kaleido 4.

**Unlocks.** E Ink 10.3" Kaleido 4 datasheet + mechanical drawing → fill `panel_sku`, re-derive the
chassis, choose the controller, then capture the display sheet.

---

## ADR-033 — The soldered eSIM stays, and it must be a consumer (SGP.22) eUICC (2026-10-21)

Written 2026-10-21 16:05 UTC in Claude Code by anthropic/claude-opus-5-5. Records the owner's decision
("please keep the esim") after AUDIT 6 H15 and the follow-up recommendation to drop it from V1.

**Trigger.** AUDIT 6 H15: the specified ST4SIM-200M is an M2M eUICC (GSMA SGP.02), so the promised
user QR-code activation through `lpac` (an SGP.22 client) cannot work with it.

**Decision.** V1 keeps a soldered MFF2 eSIM alongside the nano-SIM tray. The part must be a
**consumer eUICC (GSMA SGP.22)** so an owner can download any carrier's profile by QR code. The
ST4SIM-200M is rejected for that reason; the replacement part number is TBD until a datasheet
confirming SGP.22 support (and an MFF2 package) is in hand.

**Because.** The owner wants carrier choice without a physical card; that only exists with SGP.22.

**Delta.** BOM line keeps its slot; part and price become TBD. Dual-SIM switching and `lpac` stay in
the software spec.

**Still assumes.** The chosen modem exposes the logical channels (`AT+CCHO`/`AT+CGLA`) `lpac` needs.

---

## ADR-034 — V1 scope: a voice-first E-Ink slate without cellular (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5. Records the owner's scope
decision after AUDIT 6 §7 ("no LTE or SIMs; voice is a must; haptics if we can").

**Trigger.** AUDIT 6 found 84 catalogued features and no measured number; scope was the largest risk.

**Decision.** V1 is: CM5 (ADR-031), RP2350, Kaleido 4 + Wacom (ADR-032), LiFePO4 power path (ADR-035),
Wi-Fi/BT on the CM5, LoRa mesh, standalone GNSS (ADR-038), first-class voice (ADR-036) and haptic
typing feedback (ADR-037). **Deferred to V2:** LTE modem, nano-SIM tray, soldered eSIM (ADR-033 stays
the V2 requirement), NFC, rear camera, the modem's buck-boost supply, LTE antennas, Hotpacks.

**Because.** Cellular brings the slowest and costliest certification (carrier PTCRB/GCF, SAR) and the
hardest antenna problem behind a full-face panel; voice and typing feel are the product's identity.
Connectivity in V1 is Wi-Fi plus phone tethering.

**Delta.** BOM loses the modem, SIM, eSIM, LTE antennas, modem supply, NFC and camera rows; gains GNSS
and a voice button. The placeholder netlist and production CSVs still list the old parts; they are
replaced by the first real schematic capture (AUDIT 6 X8), not edited by hand.

---

## ADR-035 — LiFePO4 power path: BQ25798, BQ29706-class protector, BQ27Z561-R2 gauge (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Trigger.** AUDIT 6 X1–X3: BQ25895 cannot regulate below 3.84 V; BQ29700 trips at 4.275 V; BQ27441-G1A
has only a LiCoO₂ profile. AGENTS §4.1 (LiFePO4, 3.65 V limit) was violated by the BOM.

**Decision.**
- **Charger: TI BQ25798** (datasheet: VREG 3.0–18.8 V in 10 mV steps; 3.6–24 V input; OTG 0.12–3.32 A;
  JEITA; VOC-scaling MPPT). Charge limit `battery.charge_limit_v` = 3.6 V. Charging is held off with
  the charger's enable pin until the RP2350 has written VREG, because every I²C charger's POR default
  is a Li-ion voltage; the watchdog is fed or disabled after that. The BQ25798's CE pin is active-low,
  so a hardware pull-up keeps charging off at power-up without any firmware; the RP2350 drives CE low
  only once VREG reads back at the limit. The charger sits on the RP2350's always-on I²C bus and
  Linux never binds it.
- **Protector: a BQ29706-class LiFePO4 protector** (3.85 V OVP, 2.50 V UVP) with a back-to-back N-FET
  pair. CSD87330Q3D (a half-bridge power stage) is removed.
- **Gauge: TI BQ27Z561-R2** (TI lists LiFePO4), characterised on the chosen cell (ADR-040).
- **Reverse power bank capped at 2 A** (`power_bank.otg_max_a`); 15.8 W exceeded the cell path.
- **The CHEM_SEL Li-ion/LiFePO4 strap is deleted.** There is one chemistry; a switch that can select
  4.2 V is a hazard, not a feature.

**Enforced consequences.** Phase 14 asserts `charger.vreg_min_v ≤ battery.charge_limit_v ≤
charger.vreg_max_v`, that the limit lies on the VREG step grid, and that the firmware's
`SD_CHARGE_LIMIT_MV` equals it; firmware test 7 checks the CE gate. All red-controlled.

**Still assumes.** Part prices are TBD until quoted; the protector's exact variant and FETs are chosen
at schematic capture against the cell's datasheet.

---

## ADR-036 — Linux wakes in seconds; voice is first-class through a button and an opt-in wake word (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Trigger.** AUDIT 6 X4 (no RAM-retaining low-power state on CM5) and H10 (no VAD in the mic; RP2350
draws 39–51 mW at full speed; no RP2350 wake-word port). Owner: voice must drive the tablet.

**Decision.**
- **P1 is reworded:** ambient modes on the RP2350 are instant; Linux resumes from off/hibernate in
  seconds. `sleep_ladder` R2 (15 mW s2idle, 0.3 s) is `null`.
- **Voice button (always available, zero standby cost).** Press-and-hold starts RP2350 capture into
  PSRAM immediately while the CM5 boots; Linux transcribes the buffer, so no words are lost to boot
  time. The mic is live only while held.
- **Hands-free wake word is opt-in**, shown with its measured battery cost. It runs on the CM5 when
  Linux is up (free) and on the RP2350 when Linux is off (power measured on the bench before any
  claim). A dedicated low-power voice chip is the V2 path if the RP2350 cost is too high.
- Two MEMS mics, speaker with echo-cancel reference, hardware mute switch.

**Still assumes.** Local STT/TTS and barge-in run on the CM5; cloud LLMs over Wi-Fi/tethering.

**Open design item.** Capture-while-booting needs the microphones on the RP2350 (PIO I²S/PDM input)
while the CM5 is off, yet the CM5 needs the same audio when it is up. Decide at schematic capture
between (a) mics always on the RP2350, which streams audio to the CM5 (e.g. as a USB audio device),
and (b) a mic-bus switch shared like the display bus. (a) avoids a second mux and keeps one owner.

---

## ADR-037 — Haptics are core: one LRA plus instant typewriter feedback (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Decision.** People type on the glass and on the thumb-keyboard grip as well as external keyboards,
so the DRV2605L + LRA is a core part, frame-mounted (not on the glass). Every keystroke fires a haptic
pulse and an optional typewriter sound at key-down, independent of the panel refresh, so feedback
lands long before the E-Ink update and masks its latency. The quad piezo array stays DNP (ADR-020).

---

## ADR-038 — Standalone GNSS on the co-processor (supersedes ADR-003) (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Trigger.** GNSS lived inside the LTE modem, which ADR-034 defers.

**Decision.** A **u-blox MAX-M10S** (datasheet: 25 mW continuous tracking, integrated LNA for passive
antennas, UART/I²C, hardware backup and power-save modes) on an RP2350 UART behind a load switch, with
a passive GNSS antenna at the top edge. The RP2350 owns it so the LoRa node has position with Linux off.
Receive-only: no intentional-radiator certification.

---

## ADR-039 — Enclosure, heat and ingress for V1 (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Decision.** PA12 (SLS/MJF) for prototypes, PC/ABS for production, aluminium midframe and graphite
spreader inside; antennas behind plastic. A power governor caps sustained CM5 load at what the shell
sheds (value from the bench). Ingress target **IP54 for V1**, IP67 for V2 once every aperture has a
named sealing part. The outline is not frozen until the Kaleido 4 drawing exists (ADR-032).

**Because.** AUDIT 6 H8/H19/H20: the CM5 draws ~7 W under load, PA12 cannot spread it, and ~24
apertures have no sealing part.

---

## ADR-040 — The cell is chosen before the pack size is claimed (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Decision.** LiFePO4 stays (longevity, thermal safety). `battery_wh.lifepo4` is `null` until a buyable
cell's datasheet is in hand; the Li-ion figure is deleted. Expect ~20–22 Wh in the current envelope
(AUDIT 6 X7) unless the device gets thicker. Runtime claims are re-derived from the chosen cell.

---

## ADR-041 — Solar promises an outdoor top-up only (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Decision.** The bezel strip is crystalline silicon; at 500 lux it yields ~40–80 µW (AUDIT 6 H1). The
indoor net-positive claim (gate G4) is withdrawn. The product claims only that the strip tops up the
idle co-processor outdoors (Phase 14 derives this from outdoor insolation).

---

## ADR-042 — USB on the CM5: no external host controller; PCIe goes to NVMe (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Decision.** The CM5 has two native USB 3.0 ports and one USB 2.0 port (CM5 datasheet §2.4), so the
VL805 / ASM1042A host controller is removed and the single PCIe Gen 2 lane goes to the M.2 NVMe socket.

---

## ADR-043 — Verification that reaches reality, and the build order (2026-10-21)

Written 2026-10-21 16:37 UTC in Claude Code by anthropic/claude-opus-5-5.

**Decision.**
- Phase 14 checks the charger's VREG range against the battery charge limit (added with ADR-035).
- Next gates, in order: KiCad ERC in CI that fails when ERC cannot run; an LCSC C-number → MPN resolver
  for the production BOM.
- Build order: dev-kit bench → power-only board (EVT-0: charger, protector, gauge, rails) → RP2350
  minimum system → CM5 carrier. Power carries the safety risk and does not wait on the panel.
- `HANDOFF_TO_FABLE.md` moves to `90-history/`; `INDEX.md` gets a generator or stops being called
  generated.
- Contact E Ink for the Kaleido 4 datasheet, drawing and controller reference under NDA (ADR-032).

---

## ADR-044 — LoRa moves to V2; V1 talks to an external Meshtastic node over Bluetooth (2026-10-21)

Written 2026-10-21 17:20 UTC in Claude Code by anthropic/claude-opus-5-5. Amends ADR-034 (V1 scope)
and ADR-038 (GNSS rationale). Owner decision: "Should we descope LoRa from V1?" → yes.

**Trigger.** LoRa was the last intentional radiator in V1 besides the CM5's pre-certified Wi-Fi/BT.
It brings Part 15.247 / EN 300 220 testing, a possible SAR evaluation at +22 dBm near the body
(AUDIT 6 H18), an SMA aperture against the IP54 target, and firmware-enforced regional duty cycles.
None of that serves V1's identity (voice, typing, reading).

**Decision.**
- The SX1262 module, its SMA bulkhead and its antenna leave the V1 BOM. Mesh in V1 is a **CM5 software
  feature**: pair any external Meshtastic node over Bluetooth LE.
- The V1 board keeps the V2 radio as a reservation (ADR-045): DNP module footprint, its RP2350 pins in
  the pin budget, a top-edge antenna keep-out and the SMA boss in the enclosure model, plugged.
- `power.lora_repeater_mw_*` and the "80+ days repeating" claim are deleted. The LoRa regulatory rows
  move to V2. The register-map entries for LoRa stay at their offsets, marked reserved, so the
  64-byte frame does not change.
- **GNSS stays on the RP2350 in V1.** ADR-038's reason ("so the LoRa node has position with Linux
  off") is replaced: the RP2350 keeps time and logs position with Linux off, the PPS line disciplines
  its RTC, and the V2 radio inherits it.
- **RF limits (AGENTS §4.4) still bind V1.** The Meshtastic client sets an external node's region
  and transmit power, so the client refuses to configure a node without a region.

**Because.** It removes one certification and one aperture from V1 at no cost to the core features,
and users who need a mesh today already carry a Meshtastic node.

---

## ADR-045 — V1 is a platform board with V2 reservations; the pin budget is enforced (2026-10-21)

Written 2026-10-21 17:20 UTC in Claude Code by anthropic/claude-opus-5-5. Owner question: can the V1
schematic and mechanics be drawn with the full V2 feature set in mind?

**Decision.** Yes. The V1 carrier board and enclosure are drawn once, for V2. V2 parts are DNP
footprints, not omissions:

| V2 feature | Reserved on the V1 board / enclosure |
| :--- | :--- |
| LTE modem | M.2 Key-B socket on CM5 USB 3.0 port 1; modem load switch and control on the always-on GPIO expander; supply headroom for the modem's peak current, sized when the modem is chosen; antenna keep-outs and windows in the shell |
| SIM / eSIM | nano-SIM tray footprint and an MFF2 SGP.22 eUICC footprint (ADR-033), both on the modem's SIM bus |
| LoRa | SX1262 module footprint on the RP-side SPI0 bus, RP2350 GPIO 1, 22, 39, 46, 47 and two expander lines; top-edge SMA boss, plugged (ADR-044) |
| NFC | coil area behind the rear shell; controller footprint on the CM5 host I²C; interrupt on CM5 GPIO 27 |
| Camera | CSI connector footprint on CM5 MIPI 1; lens boss in the rear shell, plugged |

**The pin budget** (`spec_values.pins`, readable copy `docs/PIN_BUDGET.md`) assigns every GPIO on
both processors to a V1 or V2 use. Phase 15 checks it against the datasheet mux tables, uniqueness,
isolation into the unpowered CM5 domain, the TMUX channel count and the firmware's `PIN_*` defines.
The firmware's solar ADC pin was invalid (GPIO 26; the RP2350B ADC is GPIO 40–47) and moved to 40.

**Consequences the budget forced.**
- **Mic routing (ADR-036 open item): the budget assumes option (a); owner to confirm.** The RP2350
  owns both mics and is the I²S clock master; it streams audio to the CM5's I2S1 (the clock-target
  instance; I2S0 is master-only), and the speaker amp and headphone DAC share those clocks. USB audio
  does not fit: the only free CM5 USB port is the V2 modem's, and the OTG port is the CM5 re-flash
  path on USB-C port 1.
- **V1 needs an always-on I²C GPIO expander.** Checked against every signal-bearing V1 BOM part plus
  the notification LED and piezo, V1 alone needs more lines than the RP2350B's 48. Slow enable and
  interrupt lines move to a 16-bit expander on the RP2350's bus (a TBD BOM row); the RP2350 keeps
  buses, PWM, ADC and direct-wake inputs. At V2 the RP2350's pins are full and the expander has two
  spare. The CM5 has two spare GPIO (0/1) in V1 and V2.
- **CM5↔RP2350 link on CM5 SPI3** (GPIO 4–7), not through the TMUX.

**Costs.** Board area and enclosure volume for parts V1 does not ship. High-speed V2 lanes must end
at their footprint with no stubs. V2 still needs its own certification (cellular, LoRa, NFC); a
reserved footprint is not a certified radio.

---

## ADR-046 — Owner decisions after the pin budget; software frozen until hardware exists (2026-10-21)

Written 2026-10-21 17:52 UTC in Claude Code by anthropic/claude-opus-5-5. Owner: "do all of them";
"don't re-enable CI … do all the checks locally before pushing"; "we probably don't need to do any
software right now since we don't have any hardware".

**Decisions.**
- **Mic routing (closes the ADR-036 open item):** the RP2350 owns both mics and is the audio clock
  master; it streams I²S to the CM5's I2S1. ADR-045 recorded this as an assumption; it is now decided.
- **Privacy switch:** one 3-position slide switch (normal / mic mute / full blackout), as
  HARDWARE_SPEC §2.25 and SECURITY describe. The BOM's 2-position part was wrong; the new part is TBD.
- **Timekeeping:** an I²C RTC chip with its own crystal (RV-3028-C7 class) on the always-on bus
  replaces the bare 32.768 kHz crystal, which the RP2350 could not drive and whose clock-input pins are
  all assigned. The DS3231 stays only as the DNP fallback footprint.
- **Co-processor flash:** a 16 MB QSPI NOR (W25Q128JV class) is added. The RP2350B has no internal
  flash, so the BOM had nowhere to store its firmware. 16 MB holds two firmware slots plus reader
  content.
- **Headphone jack and DAC removed from V1** (not deferred): one less aperture against IP54, two fewer
  parts, no headset-mic input to budget. Audio out is the speaker, USB-C or Bluetooth.
- **Quad piezo array stays off the board** unless bench tests show the LRA cannot give the typewriter
  feel (ADR-037). It needs no RP2350 pins, so adding it later costs nothing.
- **No fab bundles until the PCB is routed.** The synthetic Gerbers, turnkey zips, Seeed/PCBWay quote
  guides, the hand-generated chassis STL and `hardware/export_production_zip.py` are deleted;
  `hardware/production/NOT_FOR_FAB.md` stands and Phase 7 fails if a Gerber or bundle appears while it
  does.
- **No hosted CI.** The repo will go private and there is no CI budget. `verify_all.py` runs locally
  before every push through `.githooks/pre-push` (`git config core.hooksPath .githooks`).
- **Low-battery alarm in the spec:** `battery.low_alarm_v` (modelled) replaces the firmware's 2900 mV
  literal; Phase 14 checks `SD_LOW_BATT_ALARM_MV` against it. The simulated 42 ms wake time and its
  "< 300 ms" test are deleted: they asserted a constant, and the CM5 has no fast resume (ADR-036).
- **`docs/INDEX.md` deleted.** It was hand-maintained, stale and duplicated `docs/README.md`.
- **Software is frozen** until there is hardware to run it on. No new work on daemons, the OS image,
  SOFTWARE_SPEC features or firmware features. What stays live: the firmware header constants that
  encode hardware decisions (pins, charge limit, alarm), the charger safety gate and its test, and the
  verification suite. Firmware is not cross-compiled yet; that starts with the RP2350 minimum-system
  board (ADR-043).

**Costs.** Three more TBD BOM rows (privacy switch, RTC, flash) until quoted. Without hosted CI, a
contributor who skips the hook can push red; the hook is the only gate.

---

## ADR-047 — What the EVT-0 datasheet pass changed (2026-10-21)

Written 2026-10-21 19:19 UTC in Claude Code by anthropic/claude-opus-5-5. Source: `docs/EVT0_POWER_BOARD.md`,
built pin by pin from the datasheets (ADR-043 step 2).

**Decided (correctness, not preference).**
- **The BQ25798 watchdog is disabled, never fed** (amends ADR-035's "fed or disabled"). On expiry the
  charger returns to default mode and VREG to its Li-ion POR value (datasheet §7.3.2, §7.4.1).
- **After any charger reset, firmware first stops charging** (lets `CHG_CE_N` go high), then re-runs the
  VREG sequence. Until firmware notices, the BQ29706-class protector's overvoltage trip is the hardware
  backstop.
- **No ship FET on the charger**: with one, I²C stays off below about 3.3–3.55 V, which is where a
  LiFePO4 cell sits (`charger.ship_fet`).
- The always-on regulator's part number is TPS62840DLCR (the BOM's DLYR does not exist).

**Open, for the owner or for capture (not decided here).**
- **The always-on "3.3 V" rail cannot be 3.3 V from a LiFePO4 cell.** The TPS62840 is buck-only, so on
  the cell's plateau it runs in dropout and the rail follows the battery. Either pick a low-quiescent
  buck-boost, or run the always-on domain at a lower voltage (RP2350 I/O allows it) and re-check every
  part on that rail.
- **The solar harvester can charge a frozen cell.** The BQ25504 path has no temperature gate and bypasses
  the charger's CE gate. A fix is needed before EVT-0 is built (AGENTS §4.1).
- **USB-PD sink: STUSB4500 recommended** over CH224K (every requestable voltage is inside the
  charger's input range; defined behaviour at 0 V; status over I²C). Owner to confirm.
- **The 5 V boost (TPS61088) needs re-selection:** its datasheet and product page are unavailable.
- **The gauge topology as drafted cannot be captured:** with low-side protector FETs its sense sign
  inverts and its ground separates from the I²C ground when the protector opens.
- **The protector's OVP must sit below the charger's POR VREG** for the backstop above to hold; a
  Li-ion BQ297xx variant would not.
- The gauge's I²C address and the RTC's address need verification; the gauge datasheet names
  Li-ion/Li-polymer, so LiFePO4 support needs TI confirmation or chemistry characterisation (ADR-040).

---

## ADR-048 — V1 uses Li-ion in a replaceable smart pack; LiFePO4 moves to V2 (2026-10-21)

Written 2026-10-21 19:36 UTC in Claude Code by anthropic/claude-opus-5-5. Owner: "descope LiFePO4 in favour of
normal lithium for V1 … can it be designed so it's easily upgradable or replaceable?" Supersedes the
chemistry parts of ADR-035 and ADR-040; amends ADR-047's open items.

**Trigger.** The cell shortlist found the best datasheet-backed LiFePO4 pouch that fits the battery
envelope well below ADR-040's expectation, quote-only and without verified UN38.3 reports; LiFePO4
also left the always-on rail in dropout and the gauge without a listed chemistry (ADR-047).

**Decision.**
- **Chemistry: 1S Li-ion**, charge limit `battery.charge_limit_v` (4.20 V), one chemistry per hardware
  revision, no selector. The CE hold-off gate (ADR-035) stays: charging is off until VREG reads back at
  the limit. **LiFePO4 is deferred to V2.**
- **Replaceable smart pack.** The cell ships with its own protector and a pack-side BQ27Z561 gauge on a
  small pack board, behind a keyed 5–6-pin connector (pack+, pack−, SDA, SCL, NTC), held by screws
  and a pull tab, no adhesive. The pack is a service part and an upgrade path: a larger pack of the
  same chemistry drops in. Before enabling charge, firmware reads the pack gauge's design charge
  voltage and refuses any pack that does not match `battery.charge_limit_v`.
- **The pack-side gauge resolves ADR-047's gauge topology** (sense, protector and gauge share the pack
  ground, as in TI's reference circuit).
- **Always-on rail:** a low-quiescent buck-boost (TPS63900 class, to be confirmed from its datasheet)
  replaces the buck-only TPS62840, so the rail holds 3.3 V to an empty pack.
- **Solar strip stays in V1** (owner), with a **hardware temperature gate**: a comparator on the pack
  NTC switches the harvester's output off outside the charge-temperature window, no firmware. Its OV
  threshold is re-derived below the Li-ion limit (`harvester`, Phase 14).
- **USB-C power controller: STUSB4500.** The 5 V boost is re-selected from an in-production part.
- **ADR-047's "protector OVP below the charger's POR VREG" is withdrawn for Li-ion:** the BQ25798's 1s
  POR VREG equals the Li-ion limit, so a charger reset no longer overcharges the right pack. The
  protector's OVP sits above the limit with the usual Li-ion margin (`docs/EVT0_POWER_BOARD.md` §4),
  and the hold-off now guards against a wrong pack and reset charge settings.
- **Pack keying is per chemistry.** The solar harvester never sees the firmware's pack check, so a pack
  of another chemistry must not mate with the V1 connector (keyed differently in V2).

**Costs.** Cycle life falls to typical Li-ion ratings, so the pack becomes the first wear-out item
(`reliability`, modelled) and a routine replacement over the device's life. Li-ion has less thermal
margin than LiFePO4: the protector, fuse, JEITA charging and pack NTC are mandatory, not optional.
The EU Battery Regulation's user-replaceability requirement for portable batteries is a further reason
for the pack design; its exact applicability is to be confirmed (REGULATORY).

---

## ADR-049 — Pre-bench close-out: cell, EVT-0 parts, port roles, privacy switch, no batteryless mode (2026-10-21)

Written 2026-10-21 20:42 UTC in Claude Code by anthropic/claude-opus-5-5. Owner: "finish everything
that can be done before the bench test"; owner picks on 2026-10-21: EEMB 1S2P pack, port 1 sink /
port 2 source, keep `NTC_GATE` on `J_PACK` pin 6, no KiCad capture yet. Sources are cited in
`docs/EVT0_POWER_BOARD.md` §2 and Appendix A; prices in `docs/BOM_COST_ESTIMATE.md` (DigiKey/Mouser,
2026-10-21, qty 1, before tariffs).

**Trigger.** ADR-048 left the cell, five EVT-0 parts, three datasheet facts and ten BOM prices open,
plus contradictions in the privacy switch, the solar "zombie mode" and the USB-C port roles.

**Decisions.**
- **Cell (owner):** two EEMB LP7545135 cells in parallel as a 1S2P smart pack built by EEMB
  (`battery.cell_*`, `battery_wh.li_ion`, `battery_cell_mm`, datasheet). No candidate had a public
  UN38.3 or IEC 62133 report; EEMB's are claimed only, so the RFQ asks for pack-level reports. The
  pair is about 1 mm wider than the old 90 mm bay, and the tab fold plus pack board need length the
  old 142 mm bay lacks: the bay is re-cut from EEMB's pack drawing. The single-cell alternative
  (FPbattery 8574133) fit the bay but is 1C, preliminary and uncertified.
- **Pack load (modelled):** the CM5 datasheet publishes no maximum draw, only a 2.5 A design figure
  (App. B.3) and a 5 A PD ceiling (§1). The 5 V rail is budgeted at the CM5 design figure plus the
  port 2 limit (`pack.rail_5v_a`); `pack.peak_a` is that load at `battery.low_alarm_v`. Phase 14
  checks the cells (with `pack.discharge_margin`), the connector and the protector OVP against it.
- **EVT-0 parts:** TPS61022 5 V boost (true output disconnect, closes open item 10; the TPS61088
  is dropped); BQ298216 high-side protector + CSD83325L FETs; the pack fuse stays open (below); TLV7042 + TPS22916CN harvester gate (the LM66100 cannot
  gate: active-low CE against VIN and body-diode conduction when off); Hirose DF63 6-pin pack
  connector; NXP PCAL6416A GPIO expander at 0x20/0x21.
- **Datasheet facts:** gauge 0x55 and RTC 0x52 confirmed. The pack check reads `ChargingVoltage()`,
  the only charge-voltage value readable while sealed; **TI's data-flash default is 4400 mV**, so
  every pack is programmed to the limit before sealing. The RP2350 pad pull-down (36 kΩ min) keeps
  CE high in reset. The BQ25798 16-bit byte order is not stated in the datasheet: a bench read of
  REG01's reset value confirms it before the first VREG write.
- **CE pad freeze (new open item 19):** RP2350 pad isolation can latch `CHG_CE_N` low if the core
  powers down while charging. Firmware rule now, hardware gate decided at carrier capture, bench
  step 5b.
- **USB-C roles (owner):** port 1 is the only power input (STUSB4500) and the CM5's USB device /
  re-flash port; port 2 is host and the only power output (TUSB320 strapped source-only, TPS2051B,
  `usb.port2_current_limit_a`). The BQ25798 OTG mode and the LM66100 OR-ing pair are dropped;
  `power_bank.otg_max_a` is replaced by `power_bank.port`. Supersedes ADR-035's OTG cap.
- **Privacy switch:** one switch everywhere (the separate "airgap switch" text is gone). No sealed
  on-on-on part exists, so it is the E-Switch 600DP3S2M4R (2-pole on-off-on): centre = MIC MUTE,
  an open switch fails to MIC MUTE, and both poles switch logic nets that drive hardware gates. Two
  sense lines on the expander (EXP 2 `PRIVACY_MUTE`, EXP 7 `PRIVACY_BLACKOUT_N`) encode the three
  positions; one line could not.
- **No batteryless mode:** the "zombie mode" supercapacitor boot and the zero-battery SOS are
  withdrawn. No supercapacitor is in the BOM, the harvester's temperature gate reads the pack NTC
  and fails off without a pack, and the gate's rail is down with a tripped pack and no VBUS. The SOS
  placard now fires at the low-battery alarm. HARDWARE_SPEC's BQ25504 cold-start figures now cite
  the datasheet.
- **`J_PACK` pin 6 (owner):** stays `NTC_GATE`; the host polls the gauge's `InterruptStatus()`.
- **Not done:** KiCad capture of EVT-0 (owner: not now; the capture spec is the input when the
  board is ordered). The placeholder schematic and production CSVs still list superseded parts
  (`hardware/production/NOT_FOR_FAB.md`); the first real capture replaces them (ADR-034).

- **Found in review, left open (EVT-0 open item 20):** the pack current path does not yet agree on
  one limit. Phase 14 checks the modelled load at the alarm voltage only; below it the same load
  exceeds the 8 A FETs and connector, the protector's OCD (13–15 A) and any Nano2 fuse (≥ 20 A) would
  not stop a 9–13 A fault, and the TPS61022 falls short near 3.0 V. The fuse is therefore unpriced.
  The privacy switch's FULL BLACKOUT depends on pole B making contact; a failed pole B reads as
  MIC MUTE (HARDWARE_SPEC §2.25).
- **Phase 10** now fails on a backticked spec key that does not exist, and on the stale 510 g mass
  and 142 × 90 envelope.

**Delta.** BOM: 53 rows, 3 TBD (panel, controller, battery pack); total in `bom_total_low/high`.
Stock risks: TPS63900, TPS61022 and RV-3028-C7 had no distributor stock on 2026-10-21 (Mouser
expects the RTC in April 2027).

**Still assumes.** EEMB builds the pack and supplies pack-level UN38.3; TI confirms the BQ2980 and
BQ27Z561 can share one sense resistor; the TPS61022's output at the bottom of the pack's range is
enough for `pack.rail_5v_a` (EVT-0 step 8).

---

## ADR-050 — EMR pen-layer inquiries wait for the panel and go to several vendors (2026-10-21)

Written 2026-10-21 20:54 UTC in Claude Code by anthropic/claude-opus-5-5. Owner: Hanvon Ugee "is coming
up with their own Kaleido 4 thing, wouldn't we be competing?" The drafted Hanvon Ugee inquiry was
deleted unsent.

**Decision.** No EMR quote is requested before a 10.3″ Kaleido 4 is confirmed (the README's original
plan). Then one neutral inquiry (sensor size, controller interface, Linux driver path, samples and
volume pricing) goes to several vendors in parallel: Wacom's OEM channel, Hanvon Ugee and at least
one more. It names no panel model, compute module or schedule.

**Because.** A quote without a panel drawing goes stale before 2027. Hanvon Ugee sells EMR modules to
other device makers, so competition alone would not stop a sale. But Hanvon ships a Kaleido 4 device
(the M10C II, REVIEW_PACKET Q6), and a supplier does not need our roadmap to quote a sensor, and a single source leaves no
alternative.

**Still assumes.** At least two EMR vendors will quote small quantities.

---

## ADR-051 — Mono Carta 1200 is the V1 panel; colour becomes a variant (2026-10-27)

Written 2026-10-27 01:05 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017.

**Owner decision.** "Yes lets just go with mono first."

**Decision.** V1 ships a **10.3″ mono Carta 1200 module, 1872 × 1404, 227 PPI, IT8951-class
controller**, sold as commodity hardware with more than one source. Kaleido 4 (and Kaleido 3) move to
**V2 as a variant SKU on the same chassis**: the EPDC sits on a pluggable daughter board carrying
DSI + SPI + the panel bias rails, so a colour panel is a board swap, not a carrier redesign. This
supersedes ADR-032. It does not revive ADR-030 as written — mono V1 keeps a colour path.

**Because.** (1) K4 cannot be bought as a panel; K3 needs an ODM relationship with one source; a mono
10.3″ IT8951 module is available now from several vendors, which is the difference between a bench and
a product. (2) Colour is what halves the raster, not text: a Kaleido module keeps 227 PPI mono and
roughly 114 PPI colour, so mono at 227 PPI is the sharpest text this project can ship. (3) The 30-year
claim (ADR-030) is only reachable with mono capsules; dye lifespan stays `null`. (4) No colour-filter
array means no frontlight requirement, no colour-quantise/dither path, and single-pass refreshes.

**Costs accepted.** Colour is not a V1 differentiator; colour-coded UI semantics become weight, shape
and position; colour imagery and plant/foraging identification by colour are out of V1 scope. The
`CONTENT_COLOUR` refresh class stays in the scheduler for the V2 variant and is unreachable in V1.

**What would reverse it.** A missing waveform (`.wbf`) file for the chosen module, or VCOM that is
unstable over temperature: that is a different vendor, not a different architecture. If a K4 panel's
outline or raster differ materially from the mono 10.3″ outline, colour is a V2 redesign and not a
swap — check this before any colour commitment.

**Open items this creates.**

- **Panel outline is still unknown, and audit X5 now bites earlier.** `panel_module_outline_mm`,
  `display_active_mm` and `display_stack_mm` stay `null` until the chosen module's drawing is on file;
  never enter an estimate. ED103TC2 measures 216.7 × 174.4 mm (AUDIT_6 §X5) against a 170 mm chassis
  depth, so either the chassis is re-derived or a narrower glass is chosen **before** enclosure
  drawings (gate G2).
- **VCOM trim and VCOM-vs-temperature compensation** become bench bring-up items. `HARDWARE_SPEC.md`
  §2.2 already routes a backplate TMP112 to the controller `TEMP_REG` for waveform pulse voltage; VCOM
  is a separate register and is not yet covered by any procedure.
- **Ghost-ledger thresholds** (`GHOST_DEBT_THRESHOLD`, `GHOST_DEBT_CAP` in
  `src/daemons/eink-refreshd/refreshd.h`) are modelled; measure them on the mono panel before quoting
  any ghosting claim.
- **EMR stack decision** (an EMR-laminated module vs a separate sensor layer) is now due before the
  cavity is drawn. ADR-050 stays in force; it finally has a confirmed panel to quote the sensor against.
