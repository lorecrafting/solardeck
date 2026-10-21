# SolarDeck

**A sunlight-readable 10.3″ Kaleido 4 colour E-Ink Linux slate you own outright: an AI coding terminal, a LifeOps
dashboard that lives on your desk for months, and hardware built to diagnose and heal itself for
decades.**

*Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash.
Revised 2026-10-20 14:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731.
Rewritten 2026-10-21 16:05 UTC in Claude Code by anthropic/claude-opus-5-5.*

> [!WARNING]
> **Status (2026-10-21): concept / reference architecture. Nothing here is ready to build or buy.**
> Schematic capture covers 40 of 62 core BOM parts and has no wired connectivity; the PCB is unrouted;
> production files are placeholders; nothing has been measured. Checked against the datasheets, the charger
> cannot charge LiFePO4 and the CM5 has no low-power state that keeps RAM alive. The display standard,
> Kaleido 4, is not yet released, so its size, resolution and controller are unknown. See [Where things stand](#where-things-stand)
> and [`docs/AUDIT_6_2026-10-21.md`](docs/AUDIT_6_2026-10-21.md) before quoting any number.

---

## What it is

SolarDeck is one open-hardware slate that does three jobs:

- **A terminal you can take outside.** Sway, a terminal and Claude Code on a matte E-Ink screen that
  gets *better* in direct sun. Bring your own Bluetooth or USB-C keyboard; add LTE, a camera and a pen.
- **A LifeOps dashboard that never needs a socket.** On a desk or shelf it shows weather, calendar,
  solar harvest and device health, and costs nothing to hold a page. The dashboard is rendered by the
  same on-device LLM you talk to, so it reads *your* life rather than a stock widget grid.
- **A device that looks after itself.** Per-rail current sense, a battery gauge, thermal zones and
  module-health registers let it notice what is failing, and an on-device LLM can reason about why.
  It then heals through load switches: power-cycling a stuck modem, clearing a ghosted panel, backing
  off charge on a hot cell. Each action is cross-checked by a second sensor first. It is open and
  modular (socketed compute module, replaceable battery), and it carries a 30-year failure budget
  ([`docs/LONGEVITY_30Y.md`](docs/LONGEVITY_30Y.md)) as a design goal, not a warranty.

The trick that makes all three fit in one device is **two brains sharing one screen**. A small
always-on RP2350 co-processor runs the clock, dashboard, page-flip reader and LoRa mesh radio while
the Linux computer is off. Linux wakes only when you need a real computer, then goes back to sleep.

**Who it is for:** developers who want an outdoor terminal, field users who want an off-grid
reader/notebook/mesh radio, and anyone who wants an ambient dashboard that runs for months.

---

## How it works

```
                 ┌──────────────────────────── SolarDeck ────────────────────────────┐
  USB-C PD ────► │ charger + LiFePO4 ──► always-on rail ──► RP2350 co-processor       │ ◄── bezel solar strip
                 │                            │             clock · dashboard · reader │
                 │                      load switches        LoRa mesh · supervisor    │
                 │                            ▼                      │                 │
                 │        Raspberry Pi CM5 · Linux · Sway            │                 │
                 │        LTE · Wi-Fi/BT · camera · NVMe ───┐        │                 │
                 │                                          ▼        ▼                 │
                 │                         bus switch ─► display controller (TBD) ─► 10.3″ Kaleido 4 + Wacom EMR
                 └─────────────────────────────────────────────────────────────────────┘
```

A bus switch hands the display controller to whichever brain is awake. The controller is chosen once
E Ink publishes the Kaleido 4 datasheet (ADR-032). Specialist radios and
sensors (SDR, satellite, RTK, thermal…) are **Hotpacks** that snap on over USB-C rather than living on
the main board, which keeps the core cool, certifiable and cheap
([`docs/OFFGRID_TACTICAL_SENSORS.md`](docs/OFFGRID_TACTICAL_SENSORS.md)). The full architecture is in
[`docs/MVP_ARCHITECTURE.md`](docs/MVP_ARCHITECTURE.md).

---

## Product pillars

These are what the product is judged on. Every one is a **target** until its acceptance gate is
measured; live status is generated into [`docs/STATUS.md`](docs/STATUS.md), and the full specification
is in [`docs/STANDOUT_FEATURES.md`](docs/STANDOUT_FEATURES.md).

| # | Pillar | What it promises | Status |
| :-- | :--- | :--- | :--- |
| P1 | **Dual-brain instant handoff** | Linux returns to your exact session fast enough to feel instant | aspirational |
| P2 | **Typewriter-on-paper** | Keystrokes and ink with no perceptible lag and no flashing while you type | aspirational |
| P3 | **Sunlight-readable, solar-topped** | Readable in direct sun; the bezel strip sustains the idle co-processor | aspirational |
| P4 | **Field-ready form** | Thin slate, desk easel, modular grips (`chassis_mm`, `mass_g`) | modelled |
| P5 | **Field hardening** | Hardware airgap switch, LoRa mesh node, IP67 target, rain-lock touch cutoff | aspirational |
| P6 | **Modular upgrade bridge** | Socketed compute module, RAM by module swap, M.2 NVMe | specified |
| P7 | **Local voice agent** | Wake word without waking Linux, barge-in, push-to-talk | aspirational |

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

## Key parts

Numbers live in [`docs/spec_values.json`](docs/spec_values.json). This table names parts and keys
rather than restating values.

| Subsystem | Current design |
| :--- | :--- |
| Compute | Raspberry Pi CM5 (CM5116064: 16 GB RAM, 64 GB eMMC, Wi-Fi/BT), socketed — ADR-031 (`cm5`) |
| Co-processor | RP2350B + 8 MB QSPI PSRAM |
| Display | 10.3″ E Ink Kaleido 4 colour, the only SKU; specs pending E Ink's release — ADR-032 (`panel_sku`) |
| Display controller | TBD with the Kaleido 4 datasheet (the IT8951 cannot drive it; it is the bench stand-in) |
| Pen / touch | Wacom EMR + capacitive touch, pen-proximity palm blanking |
| Battery | LiFePO4 1S (`battery_wh`, `battery_cell_mm`) |
| Charging & power | USB-PD sink, charger, pack protector, fuel gauge, TPS22918 load switches |
| Solar | Bezel strip + BQ25504 harvester (`solar_w`) |
| Radios | LTE with GNSS, nano-SIM + soldered eSIM, Wi-Fi/BT, SX1262 LoRa on an external SMA, NFC |
| Camera | Sony IMX708 12 MP, rear |
| Storage | eMMC + M.2 NVMe + microSD |
| Enclosure | `chassis_mm`, `mass_g`; IP67 target |

---

## Where things stand

| Area | State |
| :--- | :--- |
| Specs & decisions | Extensive, with an ADR log ([`docs/90-history/decisions.md`](docs/90-history/decisions.md)) and one source of truth for numbers. |
| Schematic / PCB | Placeholder: symbols without wires, unrouted board, script-written netlist. |
| Firmware & daemons | Host-tested C for the RP2350 state machine, `eink-refreshd` and `telemetryd`; the firmware does not yet drive its output pins. |
| Measurements | None. Every performance figure is modelled or aspirational. |
| Certification | Not started ([`docs/REGULATORY.md`](docs/REGULATORY.md)). |

**Open decisions** ([AUDIT 6 §7](docs/AUDIT_6_2026-10-21.md)), each blocking one or more pillars:

1. **Charger, protector and gauge.** The current BQ25895 / BQ2970x / BQ27441 parts are all Li-ion
   parts and cannot serve LiFePO4. BQ25798 is the leading charger candidate.
2. **Sleep architecture (P1).** The CM5 cannot keep RAM alive at low power, so the RP2350 must own
   every mode that has to feel instant, and Linux resumes from off or hibernate in seconds.
3. **Display (P2, P4).** Waiting on the Kaleido 4 release: resolution, outline, controller and
   waveform timings are `null` until E Ink's datasheet exists. Typing latency is re-derived from that
   datasheet, and the chassis is closed around its drawing.
4. **Cell and enclosure (P4).** No buyable LiFePO4 cell matches the specified size and capacity; the
   enclosure material is undecided.
5. **Modem and eSIM.** There is no M.2 EG25-G, so the modem module must change. The soldered eSIM
   stays, but as a consumer SGP.22 part, because the one specified was M2M-only (ADR-033).

**Next step:** a dev-kit bench (CM5 IO board, a 10.3″ IT8951 module as the display stand-in, Pico 2,
a charger EVM and a real LiFePO4 cell) to measure the numbers every pillar depends on before any
board is drawn: [`docs/DEV_KIT_BENCH.md`](docs/DEV_KIT_BENCH.md).

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
