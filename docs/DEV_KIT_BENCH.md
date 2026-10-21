# SolarDeck Dev-Kit Bench (Breadboard) Plan & Sourcing

Written 2026-10-20 21:55 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731

Revised 2026-10-21 16:02 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).

Revised 2026-10-21 19:12 UTC in Claude Code by anthropic/claude-opus-5-5 (EVT-0 power board, ADR-043).

Revised 2026-10-21 19:44 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

Purpose: buy the minimum bench hardware that proves the three make-or-break gate claims (G1, G2,
G12) and the Li-ion charge path (ADR-035, ADR-048) as **measured** values, before any PCB fabrication money is spent. This is the physical
companion to `HARDWARE_VERIFICATION_WORKFLOW.md` — that file owns the *method*, this file owns
the *bill*. Bench data graduates into the `measured <date>` claim tier in
`docs/spec_values.json`; until then every figure below is **quoted price (2026-10-20 research)**
or **modelled**, not measured.

---

## 1. What the bench must prove (and what it can't)

| Gate | Claim (source) | Bench instrument | Verdict |
| :--- | :--- | :--- | :--- |
| **G1** | <20 ms typewriter DU ink latency | Bench stand-in panel + IT8951 (ADR-025) + CM5, low-latency DU waveform | PASS = frame swap + partial update under 20 ms |
| **G2** | Linux resumes from off/hibernate in seconds (`sleep_ladder.r3_resume_s`); the S2idle target is withdrawn (R2 `null`, ADR-036) | Same rig, wake-trigger timing loop | PASS = resume time measured and recorded; ambient modes stay instant on the RP2350 |
| **G12** | Ambient (CM5-off) floor < 25 mW with TPS22918 loads hard off, R3 hibernate 0.000 W idle | **µA-resolution DMM** on the always-on rail | PASS = measured floor within spec_values.safety/sleep gate |
| **Charge path** (ADR-035) | Charging held off until VREG = `battery.charge_limit_v` is written; JEITA zones and NTC cutoff behave on a real cell | BQ25798 evaluation board + one Li-ion cell (with protector) + NTC, DMM on VBAT | PASS = no charge current before VREG is written; VREG read back; termination at the limit; NTC cutoff trips |
| Color (Kaleido 4) | fps is `null` (vendor-TCON-dependent, ADR-017/018) | **Not provable on this bench** — the IT8951 cannot drive Kaleido 4 (ADR-025, ADR-032) | Bench uses the Carta stand-in panel; Kaleido 4 colour stays `null` |

The board-level gates (thermal, EMI, mechanical, a fully populated carrier) are explicitly NOT in
this bench's scope — they need the PCB. The bench exists to answer "do the signature numbers even
exist on real silicon" for a bench total that is TBD (§2) before a ~$1.5 k PCB turnkey.

---

## 2. The bench bill (quoted prices, 2026-10-20 research)

| # | Item | Why it's on the bench | Use | Price (USD) | Where to buy *(Honolulu-friendly)* | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Waveshare 10.3" e-Paper HAT (IT8951 + Carta panel)** | The display controller + panel pair. Every G1/G2/ink-latency number runs through this | Display + EPDC | **$198** | Waveshare official / AliExpress flagship / Amazon reseller | Mono Carta, 1872×1404 — **bench stand-in only** (ADR-025, ADR-032): the product is Kaleido 4, which the IT8951 cannot drive; results are tagged with the stand-in panel and never promoted to Kaleido 4 numbers; colour fps stays `null` (ADR-017) |
| 2 | **Raspberry Pi CM5 (CM5116064 / SC1608, ADR-031)** | The Linux brain — runs the daemons under test; same module as production | Host compute | **$375** (`spec_values.cm5.price_usd`) | Raspberry Pi approved resellers | Stock and HI shipping TBD |
| 3 | **Raspberry Pi CM5 IO Board** | Carrier for the CM5 on the bench | Bench carrier | **TBD** | Raspberry Pi approved resellers | Not the production carrier — bench only |
| 4a | **Pimoroni PGA2350 — the actual RP2350B + 8 MB PSRAM** (DigiKey PIM722) | This is the real co-processor silicon the spec names (RP2350B, 48 GPIO, PSRAM frame cache) — flash **our own firmware** on it, tweak power-sipping modes (1 M Hz sleep, reader/dashboard states) on production-identical silicon | Co-proc bring-up + power-tuning | **$12 (PIM722)** | Pimoroni (UK), PiShop.us, DigiKey | Real dev board for the B chip: no USB-C (BOOTSEL bridging + jumper wiring to program), SWD probe for debug — slightly more friction than a Pico, but this is the chip that ships. Available in single unit, no MOQ |
| 4b | **Raspberry Pi Pico 2 (RP2350A) (SC1631)** | Same RP2350 core as (4a) but plug-and-play USB-C + MicroPython/C out of the box — the low-friction daily driver for first bring-up before touching the PGA | Bring-up speed | **$6 (SC1631)** | DigiKey | Kept because it is the zero-friction path for initial bring-up; 4a is the fidelity target. Total co-proc spend **$18** |
| 5 | **UNI-T UT61E+ DMM** | µA resolution + data logging — *the* G12 instrument | Sleep-current measurement | **$80** | Amazon / UNI-T direct | Do **not** buy a Fluke 115 — 1 mA resolution cannot read a µA sleep floor; high-burden volts also reset the DUT (see §4) |
| 6 | 5 V / 3 A bench PSU w/ current display | Wall power + coarse current for bring-up | Power | **$20** | Amazon | Powers the CM5/display side; the Li-ion cell (item 10) feeds only the charger board (see §5) |
| 7 | Protoboard, jumpers, duponts, 40-pin GPIO extender, assorted | Wiring everything loose | Interconnect | **$25** | Amazon / local | |
| 8 | USB-C hub + cables (CM5 eMMC is flashed over USB with `rpiboot`/usbboot — TBD, verify CM5 procedure) | Flashing, debug console | Tooling | **$20** | Amazon | |
| 9 | **TI BQ25798 evaluation board** | The production charger (ADR-035): proves VREG hold-off, the charge limit, JEITA and NTC cutoff before EVT-0 | Charge-path gate | **TBD** | TI store / DigiKey | First item of the build order (ADR-043): power carries the safety risk |
| 10 | **One protected Li-ion cell** (the candidate for ADR-040/048) + NTC thermistor | A real cell on the charger board; its datasheet also unlocks `battery_wh.li_ion` | Charge-path gate | **TBD** | US-side cell vendor (UN38.3 shipping, §5) | Wh stays `null` until its datasheet is in hand (ADR-040) |
| 11 | **u-blox MAX-M10S breakout** | The V1 GNSS (ADR-038): RP2350 UART bring-up and tracking power vs `gnss.tracking_mw` | GNSS bring-up | **TBD** | DigiKey / SparkFun | Wired to item 4a; passive antenna |
| | **Bench total** | | | **TBD** (CM5 IO board and items 9–11 TBD) | | Shipped total TBD (2–3 vendors, HI freight) |

**What is deliberately NOT on the bench:** the panel's Wacom EMR (pen arbiter comes later, after the
core gates pass), the audio array, LoRa (V2, ADR-044), and the solar strip
(0.15 W trickle is a charge-tree question, not a gate). LTE, camera and NFC are V2 (ADR-034) and have no
bench item.

**Sum total, all-in, Honolulu:** **TBD** until the CM5 IO board and items 9–11 are quoted (parts + HI shipping, two small
orders — DigiKey ships free over $99 and Waveshare direct ships US-side; worst case one Amazon order to fill gaps).
Instruments for the *second* bench round (EMR + USB-C PD meter at ~$160) are deferred until the
gates above are green — see §5.

---

## 3. The soldering question (the 4 spare boards, cold solder, precision tools)

The Seeed turnkey quote (`90-history/HANDOFF_TO_FABLE_2026-10-19.md:22`) is **1 assembled board + 4 bare boards**. The
bare boards are *not* meant to be hand-soldered as the cheap path — they are insurance: spare
populated attempts, donor boards, and (later) unpopulated carriers you can hand-populate once the
design has been through a DFM-for-hand pass. Here is the honest ladder:

1. **Do not hand-solder the QFN/BGA-class ICs by default.** The carrier has
   TMUX1575, BQ25798, TPS-family — these are *not* hand-friendly at hobbyist skill. The bench
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
     the V2 SX1262 footprint, ADR-045): each IC gets a castellated footprint with a sacrificial trace ring — a
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

1. **Resolution:** the ambient gate is < 25 mW, but R4 keep-alive is **<0.2 mW**
   → **<60 µA average**. A Fluke 115 (1 mA resolution, no µA range) reads this as 0.000 — useless.
   The UNI-T UT61E+ (µA range, USB logging, ~$80) or a Brymen BM869s (nA-class, ~$280 if budget
   allows) is the floor instrument.
2. **Burden voltage:** cheap meters drop many mV at µA ranges, which can *reset the DUT* mid-
   measurement. UT61E+ class is fine; if the DUT resets, add a shunt and compute.
3. **Averaged peaks lie:** DMMs average fast pulses. For the CM5 boot / hibernate-write burst use short
   logging intervals and cross-check against the wall-PSU readout.

Method per WORKFLOW claim rules: same instrument, logged file, date stamped; the measured numbers
then go into `spec_values.json` under a `measured <date>` tag — this bench's whole point.

---

## 5. Ordering strategy — all at once?

**Partially, not fully.**

| Tranche | Contents | Why |
| :--- | :--- | :--- |
| **1 — now (total TBD, §2)** | §2 items 1–11 | One ordering pass is cheaper on HI freight and gets you to first data fast; also the parts with real stock risk (CM5, panel) benefit from earliest ordering |
| **2 — on green gates (~$160)** | Wacom EMR panel variant + stylus, USB-C PD power meter | Costs money you shouldn't spend if G1/G2/G12 fail; EMR arbiter work is gated on the core gates anyway |
| **3 — only after board-stage quotes** | PCB turnkey (1 assembled + 4 bare, ~$1.5 k) + hand-rework kit (~$250, only if the DFM-for-hand path is chosen) | The bench answers whether the ~$1.5 k is worth spending, and what pad/DFM changes to *request* in that quote |

Battery: **one real protected Li-ion cell, on the charger board only.** G12's *idle* numbers are rail-side (wall
PSU is fine); the cell exists to prove the charge path (items 9–10) before EVT-0 (ADR-043). Verify NTC
cutoff before leaving it on charge (AGENTS §4.1). Shipping a cell to HI has UN38.3 friction — buy one
single cell from a US-side vendor, not a pack.

**Bottom line:** yes, buy Tranche 1 all at once (landed total TBD, §2); defer Tranche 2 until the
gates pass; do not hand-solder anything until a DFM-for-hand pass makes it sensible.

---

## 6. After the bench: EVT-0, the power-only board (ADR-043 step 2)

The bench proves the charge path on an evaluation board; EVT-0 proves it on our own power tree
(charger, protector, gauge, PD sink, rails, harvester, load switches) with a Pico 2 on a header as the
co-processor. The capture package, the charger hold-off register sequence and the board-specific
bring-up order are in [`EVT0_POWER_BOARD.md`](EVT0_POWER_BOARD.md) (§3 and §7); this file does not
repeat them. EVT-0 reuses this bench's instruments: the µA-resolution DMM (§4) for the battery-side
floor, the real Li-ion cell for termination, and the Pico 2 as the host. It cannot start until
the open items in its §8 that block capture are decided. ADR-048 set the direction for several of
them (a TPS63900-class buck-boost for the always-on rail, the STUSB4500 PD sink, a hardware
temperature gate on the harvester, a pack-side gauge sharing the pack ground); those parts still need
confirming from their datasheets, alongside CE behaviour with a flat cell and port roles (ADR-047).
