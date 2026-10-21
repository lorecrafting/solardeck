# SolarDeck

**A sunlight-readable 10.3″ Kaleido 4 colour E-Ink Linux slate you own outright: a voice-driven AI
terminal, a LifeOps dashboard that lives on your desk for months, and hardware built to diagnose and
heal itself for decades.**

*Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash.
Revised 2026-10-20 14:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731.
Rewritten 2026-10-21 16:05 UTC and revised 16:55 UTC in Claude Code by anthropic/claude-opus-5-5.*

> [!WARNING]
> **Status (2026-10-21): concept / reference architecture. Nothing here is ready to build or buy.**
> Schematic capture covers 40 of 55 core BOM parts and has no wired connectivity; the PCB is unrouted;
> production files are placeholders; nothing has been measured. V1 scope and parts were re-decided on
> 2026-10-21 (ADR-031 to ADR-043). The display, Kaleido 4, is not yet released, so its size,
> resolution and controller are unknown. See [Where things stand](#where-things-stand) and
> [`docs/AUDIT_6_2026-10-21.md`](docs/AUDIT_6_2026-10-21.md) before quoting any number.

---

## What it is

SolarDeck is one open-hardware slate that does three jobs:

- **An AI terminal you drive by voice, pen and keys.** Talk to it, write on it, or type on the glass,
  a snap-on thumb keyboard or any Bluetooth/USB-C keyboard. Sway, a terminal and Claude Code run on a
  matte E-Ink screen that gets *better* in direct sun.
- **A LifeOps dashboard that never needs a socket.** On a desk or shelf it shows weather, calendar,
  solar harvest and device health, and costs nothing to hold a page. The dashboard is rendered by the
  same on-device LLM you talk to, so it reads *your* life rather than a stock widget grid.
- **A device that looks after itself.** Per-rail current sense, a battery gauge, thermal zones and
  module-health registers let it notice what is failing, and an on-device LLM can reason about why.
  It then heals through load switches: power-cycling a stuck radio, clearing a ghosted panel, backing
  off charge on a hot cell. Each action is cross-checked by a second sensor first. It is open and
  modular (socketed compute module, replaceable battery), and it carries a 30-year failure budget
  ([`docs/LONGEVITY_30Y.md`](docs/LONGEVITY_30Y.md)) as a design goal, not a warranty.

The trick that makes all three fit in one device is **two brains sharing one screen**. A small
always-on RP2350 co-processor runs the clock, dashboard, page-flip reader, GPS and LoRa mesh radio
while the Linux computer is off. Linux wakes in seconds when you need a real computer, then goes back
off.

**Who it is for:** developers who want an outdoor AI terminal, field users who want an off-grid
reader/notebook/mesh radio, and anyone who wants an ambient dashboard that runs for months.

---

## Talking and typing

**Voice is a first-class way to drive the tablet** (ADR-036):
- **Hold the voice button** and speak. The co-processor starts recording the instant you press, while
  Linux wakes, so nothing you say is lost to boot time. The microphones are live only while you hold
  it, and it costs nothing in standby.
- **Hands-free "Hey Deck"** is an opt-in mode. The device shows what it costs in battery before you
  turn it on.
- Two microphones with echo cancellation let you talk over its replies. Replies stream as text on the
  page and can be spoken aloud. A hardware switch mutes the microphones.

**Typing feels like a typewriter** (ADR-037): every keystroke fires a haptic tap and an optional
typewriter sound at key-down, long before the E-Ink finishes drawing, so the feedback hides the
panel's refresh time.

---

## How it works

```
                 ┌──────────────────────────── SolarDeck ────────────────────────────┐
  USB-C PD ────► │ charger + LiFePO4 ──► always-on rail ──► RP2350 co-processor       │ ◄── bezel solar strip
                 │                            │        clock · dashboard · reader       │
                 │                      load switches   GPS · LoRa mesh · voice button │
                 │                            ▼                      │                 │
                 │        Raspberry Pi CM5 · Linux · Sway            │                 │
                 │        Wi-Fi/BT · mics · speaker · NVMe ──┐       │                 │
                 │                                           ▼       ▼                 │
                 │                          bus switch ─► display controller (TBD) ─► 10.3″ Kaleido 4 + Wacom EMR
                 └─────────────────────────────────────────────────────────────────────┘
```

A bus switch hands the display controller to whichever brain is awake. The controller is chosen once
E Ink publishes the Kaleido 4 datasheet (ADR-032). V1 connects over Wi-Fi or by tethering to your
phone; cellular is a V2 feature (ADR-034). Specialist radios and sensors (SDR, satellite, RTK,
thermal…) are **Hotpacks** that snap on over USB-C in a later version
([`docs/OFFGRID_TACTICAL_SENSORS.md`](docs/OFFGRID_TACTICAL_SENSORS.md)). The full architecture is in
[`docs/MVP_ARCHITECTURE.md`](docs/MVP_ARCHITECTURE.md).

---

## Product pillars

These are what the product is judged on. Every one is a **target** until its acceptance gate is
measured; live status is generated into [`docs/STATUS.md`](docs/STATUS.md), and the full specification
is in [`docs/STANDOUT_FEATURES.md`](docs/STANDOUT_FEATURES.md).

| # | Pillar | What it promises | Status |
| :-- | :--- | :--- | :--- |
| P1 | **Dual-brain handoff** | Ambient modes are instant on the co-processor; Linux is back in seconds | aspirational |
| P2 | **Typewriter-on-paper** | Instant haptic and audio feedback per keystroke; ink with no flashing while you type | aspirational |
| P3 | **Sunlight-readable, solar-topped** | Readable in direct sun; outdoors the bezel strip tops up the idle co-processor | aspirational |
| P4 | **Field-ready form** | Thin slate, desk easel, modular grips (`chassis_mm`, `mass_g`) | modelled |
| P5 | **Field hardening** | Hardware airgap switch, LoRa mesh, GPS, IP54 in V1 (IP67 in V2), rain-lock touch cutoff | aspirational |
| P6 | **Modular upgrade bridge** | Socketed compute module, RAM by module swap, M.2 NVMe | specified |
| P7 | **Voice-first control** | Hold-to-talk button, opt-in hands-free wake word, barge-in | aspirational |

## Engineering pillars

These are the architectural bets that make the product pillars possible (`features.engineering_pillars`).

| # | Bet | Status |
| :-- | :--- | :--- |
| E1 | Dual-brain display mux: bus switch, RP2350 frame cache in PSRAM | specified |
| E2 | Sleep ramping: Linux sleeps between page turns and ramps to full speed on input | aspirational |
| E3 | Universal mechanical anchor: rear M2.5 inserts + MagSafe array for grips, stands, tripods | modelled |
| E4 | Hardware airgap switch that cuts radio power, with I_off buffers against back-powering | specified |
| E5 | Driverless USB-C external monitor sink (in practice a USB gadget plus a host screen-share app — AUDIT 6 H14) | specified |
| E6 | Hotpack isolation: everything exotic behind one recessed USB-C port | specified |
| E7 | Self-observant hardware: the LLM consumes BIST telemetry | specified |
| E8 | Thermal viscosity assist (AUDIT 6 H9 recommends withdrawing it in favour of temperature-indexed waveforms) | aspirational |
| E9 | Zero-cost combinations: solar strip as light meter, reverse-charge power bank, airgapped signing station | specified |

---

## V1 parts

Numbers live in [`docs/spec_values.json`](docs/spec_values.json). This table names parts and keys
rather than restating values.

| Subsystem | V1 design |
| :--- | :--- |
| Compute | Raspberry Pi CM5 (CM5116064: 16 GB RAM, 64 GB eMMC, Wi-Fi/BT), socketed — ADR-031 (`cm5`) |
| Co-processor | RP2350B + 8 MB QSPI PSRAM |
| Display | 10.3″ E Ink Kaleido 4 colour, the only SKU; specs pending E Ink's release — ADR-032 (`panel_sku`) |
| Display controller | TBD with the Kaleido 4 datasheet (the IT8951 cannot drive it; it is the bench stand-in) |
| Pen / touch | Wacom EMR + capacitive touch, pen-proximity palm blanking |
| Voice | Two MEMS mics, speaker + amp, hold-to-talk button, mute switch — ADR-036 |
| Haptics | DRV2605L + frame-mounted LRA, plus typewriter sound — ADR-037 |
| Battery | LiFePO4 1S; cell chosen from a real datasheet before capacity is claimed — ADR-040 (`battery_wh`) |
| Charging & power | BQ25798 charger, BQ29706-class protector, BQ27Z561-R2 gauge, USB-PD sink, power bank capped at 2 A — ADR-035 (`charger`, `battery`) |
| Solar | Bezel strip + BQ25504 harvester, outdoor top-up only — ADR-041 (`solar_w`) |
| Radios | Wi-Fi/BT on the CM5, SX1262 LoRa on an external SMA, u-blox MAX-M10S GPS — ADR-038 (`gnss`) |
| Storage | eMMC + M.2 NVMe on the CM5's PCIe lane + microSD; USB 3 native on the CM5 — ADR-042 |
| Enclosure | PA12 prototypes, PC/ABS production, IP54 in V1 — ADR-039 (`chassis_mm`, `ingress`) |
| **V2** | LTE, nano-SIM and SGP.22 eSIM (ADR-033), NFC, rear camera, Hotpacks — ADR-034 |

---

## Where things stand

| Area | State |
| :--- | :--- |
| Specs & decisions | Extensive, with an ADR log ([`docs/90-history/decisions.md`](docs/90-history/decisions.md)) and one source of truth for numbers. |
| Schematic / PCB | Placeholder: symbols without wires, unrouted board, script-written netlist that still lists pre-V1 parts. |
| Firmware & daemons | Host-tested C for the RP2350 state machine, `eink-refreshd` and `telemetryd`; the firmware does not yet drive its output pins. |
| Measurements | None. Every performance figure is modelled or aspirational. |
| Certification | Not started ([`docs/REGULATORY.md`](docs/REGULATORY.md)). |

**What's waiting on what:**
1. **Kaleido 4 (E Ink).** Resolution, outline, controller and waveform timings are `null` until E Ink's
   datasheet exists; the chassis and display circuit wait on it. Next action: ask E Ink for it under NDA.
2. **A real LiFePO4 cell.** Capacity and runtime are re-derived from its datasheet (ADR-040).
3. **Bench numbers.** Linux resume time, wake-word power on the RP2350, CM5 heat in the shell and
   charge termination with the protector in circuit all come from the dev-kit bench.

**Next step:** the dev-kit bench (CM5 IO board, a 10.3″ IT8951 module as the display stand-in, Pico 2,
a BQ25798 evaluation board and a real LiFePO4 cell), then a power-only board before the full carrier
(ADR-043): [`docs/DEV_KIT_BENCH.md`](docs/DEV_KIT_BENCH.md).

---

## Working in this repo

```sh
python3 scripts/verify_all.py   # 16 phases; green = internally consistent, NOT a design sign-off
```

- Start with [`docs/README.md`](docs/README.md) (reading order and claim vocabulary), then
  [`docs/WORKFLOW.md`](docs/WORKFLOW.md) (how changes are made) and [`AGENTS.md`](AGENTS.md) (hard
  rules, including the battery, RF and waveform safety constraints).
- Every number belongs in [`docs/spec_values.json`](docs/spec_values.json) with a tag: `measured`,
  `datasheet`, `modelled`, `aspirational`, or `null`.
- Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md). Security model: [`SECURITY.md`](SECURITY.md).

| Path | Contents |
| :--- | :--- |
| `docs/` | Specs, audits, ADRs, the single source of truth |
| `hardware/` | KiCad sources (partial), enclosure OpenSCAD, production-bundle scripts |
| `firmware/rp2350/` | Co-processor firmware and host tests |
| `src/daemons/`, `src/dts/` | Linux daemons and the CM5 device-tree overlay (not yet ported to RP1) |
| `tools/provision/` | OS provisioning script |
| `scripts/` | The verification suite |

## License

Hardware CERN-OHL-S-2.0, software MIT, documentation CC-BY-SA. The per-path map is in
[`LICENSES/PATHS.md`](LICENSES/PATHS.md).
