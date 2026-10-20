# SolarDeck Dev-Kit Bench (Breadboard) Plan & Sourcing

Written 2026-10-20 21:55 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731

Purpose: buy the minimum bench hardware that proves the three make-or-break gate claims (G1, G2,
G12) as **measured** values, before any PCB fabrication money is spent. This is the physical
companion to `HARDWARE_VERIFICATION_WORKFLOW.md` — that file owns the *method*, this file owns
the *bill*. Bench data graduates into the `measured <date>` claim tier in
`docs/spec_values.json`; until then every figure below is **quoted price (2026-10-20 research)**
or **modelled**, not measured.

---

## 1. What the bench must prove (and what it can't)

| Gate | Claim (source) | Bench instrument | Verdict |
| :--- | :--- | :--- | :--- |
| **G1** | <20 ms typewriter DU ink latency | Breadboard panel + IT8951 + CM4, low-latency DU waveform | PASS = frame swap + partial update under 20 ms |
| **G2** | <400 ms S2idle → glass (target 0.3 s) | Same rig, wake-trigger timing loop | PASS = user-visible frame <400 ms from tap |
| **G12** | S2idle ≈15 mW floor, R3 hibernate 0.000 W idle | **µA-resolution DMM** on the always-on rail | PASS = measured floor within spec_values.safety/sleep gate |
| Color (K3/K4) | fps is `null` (vendor-TCON-dependent, ADR-017/018) | **Not provable on this bench** — no retail K3 10.3" IT8951 dev panel exists | Bench uses the 1872×1404 Carta panel; color stays `null` |

The board-level gates (thermal, EMI, mechanical, a fully populated carrier) are explicitly NOT in
this bench's scope — they need the PCB. The bench exists to answer "do the signature numbers even
exist on real silicon" for ~$550 before a ~$1.5 k PCB turnkey.

---

## 2. The bench bill (quoted prices, 2026-10-20 research)

| # | Item | Why it's on the bench | Use | Price (USD) | Where to buy *(Honolulu-friendly)* | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Waveshare 10.3" e-Paper HAT (IT8951 + Carta panel)** | The display controller + panel pair. Every G1/G2/ink-latency number runs through this | Display + EPDC | **$198** | Waveshare official / AliExpress flagship / Amazon reseller | Mono Carta, 1872×1404 — same resolution & IT8951 as the colour panel would use; colour fps stays `null` (ADR-017) |
| 2 | **Raspberry Pi CM4 8 GB (CM4108032 / DigiKey SC0678)** | The Linux brain — runs the daemons under test | Host compute | **$195** (retail; $75 is a bulk-wish from the BOM — do not plan on it) | DigiKey/Mouser (watch stock), PiShop.us, Amazon | Often OOS at DigiKey; Newark/Seattle-distributed resellers ship to HI |
| 3 | **Waveshare CM4 Nano Base Board (B)** | Carrier for CM4 on the bench (has GbE + HDMI + USB) | Bench carrier | **$18** | Waveshare / PiShop.us / Amazon | Not the production carrier — bench only |
| 4 | **Raspberry Pi Pico 2 (RP2350A)** | Stand-in for the RP2350B co-processor (identical RP2350 core; B adds PSRAM/GPIO count) | Co-proc firmware bring-up | **$6 (SC1631)** | DigiKey | Validate the sleep-ladder + wake path; the 0.000 W R3 rung is CM4-side anyway |
| 5 | **UNI-T UT61E+ DMM** | µA resolution + data logging — *the* G12 instrument | Sleep-current measurement | **$80** | Amazon / UNI-T direct | Do **not** buy a Fluke 115 — 1 mA resolution cannot read a µA sleep floor; high-burden volts also reset the DUT (see §4) |
| 6 | 5 V / 3 A bench PSU w/ current display | Wall power + coarse current for bring-up | Power | **$20** | Amazon | Wall-powered bench: no LiFePO₄ pack yet (UN38.3 + no need — see §5) |
| 7 | Protoboard, jumpers, duponts, 40-pin GPIO extender, assorted | Wiring everything loose | Interconnect | **$25** | Amazon / local | |
| 8 | USB-C hub + cables + microSD (CM4 eMMC is fine but USB flash convenience) | Flashing, debug console | Tooling | **$20** | Amazon | |
| | **Bench total** | | | **≈ $362** | | ≈ **$400 shipped** (2–3 vendors, HI freight) |

**What is deliberately NOT on the bench:** the panel's Wacom EMR (pen arbiter comes later, after the
core gates pass), the audio array, LoRa/EG25-G (standard radios — board-stage), the solar strip
(0.15 W trickle is a charge-tree question, not a gate), and the BQ charger (charging safety gates
come after the bench answers).

**Sum total, all-in, Honolulu:** **≈ $400–430** (parts + HI shipping, two small orders — DigiKey
ships free over $99 and Waveshare direct ships US-side; worst case one Amazon order to fill gaps).
Instruments for the *second* bench round (EMR + USB-C PD meter at ~$160) are deferred until the
gates above are green — see §5.

---

## 3. The soldering question (the 4 spare boards, cold solder, precision tools)

The Seeed turnkey quote (`HANDOFF_TO_FABLE.md:22`) is **1 assembled board + 4 bare boards**. The
bare boards are *not* meant to be hand-soldered as the cheap path — they are insurance: spare
populated attempts, donor boards, and (later) unpopulated carriers you can hand-populate once the
design has been through a DFM-for-hand pass. Here is the honest ladder:

1. **Do not hand-solder the QFN/BGA-class ICs by default.** The carrier has VL805 (BGA),
   TMUX1575, BQ25895, TPS-family — these are *not* hand-friendly at hobbyist skill. The bench
   doesn't need them anyway: it runs a Nano board + Pico, both pre-assembled.
2. **Cold solder (conductive silver epoxy, e.g. CircuitWorks CW2400)** is a **repair** tool, not a
   mounting one: high contact resistance, weak mechanically, fails thermal cycling. Useful for
   tacking a debug lead or re-bonding a lifted pad **on a broken spare**, never for a current-
   carrying IC that must hold a waveform spec.
3. **If you do want to hand-populate spares later, the pre-requisite is the fab making it
   possible**, not you getting better with an iron:
   - **Bigger pads & spacing is a real request** — any KiCad footprint's pads can be enlarged and
     clearances widened (e.g. 0.4 mm pad / 0.3 mm gap → 0.6/0.7 mm when the part allows). Specify
     *DFM-for-hand-assembly* pads at quoting time; JLCPCB/Seeed will happily fab enlarged-pad
     variants.
   - **Castellated SMD modules** (KiCad 8 feature, already referenced in `HARDWARE_SPEC.md:793` for
     the SX1262): each IC gets a castellated footprint with a sacrificial trace ring — a
     hand-solder pattern that drags tin across pads and is then cleaned off. This is the *right*
     hand-assembly answer for the RF/co-proc parts.
   - **Precision tools, when you do it:** hot-air rework station (~$120–250, the solder sucker +
     flux pen combo), digital microscope 10–100× (~$40–80), fine-tip iron + 0.3 mm tip
     (~$30), solder wick/braid + tip-tinner, ESD mat. Budget **~$250** for a real rework kit.

**Recommendation:** take the **1 assembled board** from Seeed for the gates now. Re-purpose the 4
bare boards as (a) spare for fab defects, (b) DFM-for-hand test pieces on the *next* request
(castellated footprints, enlarged pads), (c) donor board for connectors when the prototype rig
grows. Hand-soldering is a *later* option gated on a DFM pass — not the path to first data.

---

## 4. G12 measuring truth: the DMM is the tool, cheap meters are a trap

Measuring a µA-scale sleep floor has three traps (checked 2026-10-20 against instrument
capability data):

1. **Resolution:** the floor is ~15 mW / 3.3 V ≈ **4.5 mA peak**, but R4 keep-alive is **<0.2 mW**
   → **<60 µA average**. A Fluke 115 (1 mA resolution, no µA range) reads this as 0.000 — useless.
   The UNI-T UT61E+ (µA range, USB logging, ~$80) or a Brymen BM869s (nA-class, ~$280 if budget
   allows) is the floor instrument.
2. **Burden voltage:** cheap meters drop many mV at µA ranges, which can *reset the DUT* mid-
   measurement. UT61E+ class is fine; if the DUT resets, add a shunt and compute.
3. **Averaged peaks lie:** DMMs average fast pulses. For the R2→R3 transition burst use short
   logging intervals and cross-check against the wall-PSU readout.

Method per WORKFLOW claim rules: same instrument, logged file, date stamped; the measured numbers
then go into `spec_values.json` under a `measured <date>` tag — this bench's whole point.

---

## 5. Ordering strategy — all at once?

**Partially, not fully.**

| Tranche | Contents | Why |
| :--- | :--- | :--- |
| **1 — now (~$400)** | §2 items 1–8 | One ordering pass is cheaper on HI freight and gets you to first data fast; also the parts with real stock risk (CM4, panel) benefit from earliest ordering |
| **2 — on green gates (~$160)** | Wacom EMR panel variant + stylus, USB-C PD power meter | Costs money you shouldn't spend if G1/G2/G12 fail; EMR arbiter work is gated on the core gates anyway |
| **3 — only after board-stage quotes** | PCB turnkey (1 assembled + 4 bare, ~$1.5 k) + hand-rework kit (~$250, only if the DFM-for-hand path is chosen) | The bench answers whether the ~$1.5 k is worth spending, and what pad/DFM changes to *request* in that quote |

Battery: **no LiFePO₄ pack on this bench.** G12's *idle* numbers are rail-side (wall PSU is fine);
the pack's charge-tree (BQ, NTC cutoff) is a board-stage/bench-2 question, and shipping a bare
LiFePO₄ pack to HI has UN38.3 friction — skip until it earns its place.

**Bottom line:** yes, buy Tranche 1 all at once (~$400 landed, HI); defer Tranche 2 until the
gates pass; do not hand-solder anything until a DFM-for-hand pass makes it sensible.