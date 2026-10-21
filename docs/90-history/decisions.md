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
