# SolarDeck

**An open-hardware 10.3″ colour E-Ink slate you can read in full sun, talk to, write on and type on —
a calm Linux machine for working with AI, built to be repaired and upgraded instead of replaced.**

*Written 2026-10-18 17:35 UTC in the Pi harness by antigravity/gemini-3.8-flash.
Revised 2026-10-20 14:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731.
Rewritten 2026-10-21 16:05 UTC and revised 16:55, 17:30 and 19:38 UTC in Claude Code by anthropic/claude-opus-5-5.*

> [!NOTE]
> **Status (2026-10-21): design stage.** The architecture, parts and pin budget are worked out and
> machine-checked; there is no board yet and nothing has been measured. The display, E Ink's Kaleido 4,
> was announced on 2026-10-15 and we are waiting on its datasheet. Every figure in this repo is tagged
> `datasheet`, `modelled`, `aspirational` or `null` — see [Where things stand](#where-things-stand).

---

## Why build this

Most of what we now do with AI is reading and writing: prompts, answers, documents, code. That work
doesn't need a bright, power-hungry screen, and it's better away from one. E-Ink is easy on the eyes,
gets *more* readable in sunlight, and holds a page for free.

What's missing is an E-Ink device that is a real computer — full Linux, a proper terminal, your own
tools — instead of a locked-down reader. SolarDeck is that device, with three more convictions built
in: **voice should be first-class**, **typing should feel good even on a slow screen**, and **you should
be able to open it, fix it and keep it for years.**

---

## What it does

- **An AI terminal you drive by voice, pen and keys.** Talk to it, write on it with a battery-free pen,
  or type on the glass, a thumb-keyboard grip or any Bluetooth/USB-C keyboard. Sway, a terminal and
  tools like Claude Code run on a matte screen that's comfortable for hours, indoors or out.
- **A dashboard that lives on your desk.** Weather, calendar, tasks and device health on a screen that
  costs nothing to hold, refreshed by a low-power co-processor while the main computer sleeps.
- **A device that keeps an eye on itself.** Per-rail current sensing, a battery gauge and thermal sensors
  let it notice what's going wrong, explain it, and act through hardware switches — power-cycling a
  stuck peripheral or backing off charge on a hot battery — after a second sensor agrees.

---

## Talk, write, type

**Voice comes first** (ADR-036). Hold the voice button and speak: the co-processor starts recording
the instant you press, while Linux wakes, so nothing you say is lost. The microphones are live only
while you hold it. A hands-free wake word is opt-in, and the device shows its battery cost before you
turn it on. Echo cancellation lets you talk over replies; a hardware switch cuts the microphones.

**Typing feels like a typewriter** (ADR-037). Every keystroke gets a haptic tap and an optional
typewriter click at key-down, before the E-Ink finishes drawing, so the screen's refresh time
disappears behind the feedback.

**Writing feels like paper.** A Wacom-class EMR pen layer sits behind the panel, with palm rejection
handled in hardware.

---

## How it works

The core idea is **two brains sharing one screen**. A tiny always-on co-processor (RP2350) runs the
clock, dashboard, page-turn reader, GPS and voice-button recording on almost no power. When you need a
full computer, a Raspberry Pi CM5 running Linux takes over the display within seconds, then powers off
again when you're done.

```
                 ┌──────────────────────────── SolarDeck ────────────────────────────┐
  USB-C PD ────► │ charger + Li-ion ───► always-on rail ──► RP2350 co-processor       │ ◄── bezel solar strip
                 │                            │        clock · dashboard · reader       │
                 │                      load switches   GPS · mics · voice button      │
                 │                            ▼                      │                 │
                 │        Raspberry Pi CM5 · Linux · Sway            │                 │
                 │        Wi-Fi/BT · speaker · NVMe ─────────┐       │                 │
                 │                                           ▼       ▼                 │
                 │                          bus switch ─► display controller (TBD) ─► 10.3″ Kaleido 4 + Wacom EMR
                 └─────────────────────────────────────────────────────────────────────┘
```

A bus switch hands the display to whichever brain is awake. V1 gets online over Wi-Fi or your phone's
hotspot and talks to an external Meshtastic radio over Bluetooth; cellular, on-board LoRa, NFC and a
camera arrive in V2, and the V1 board already reserves their footprints and pins
([`docs/PIN_BUDGET.md`](docs/PIN_BUDGET.md)). The full architecture is in
[`docs/MVP_ARCHITECTURE.md`](docs/MVP_ARCHITECTURE.md).

---

## Built to keep

- **Replaceable battery.** The cell lives in a smart pack — cell, protection and fuel gauge together —
  that unscrews and unplugs. No glue. A bigger pack of the same chemistry drops straight in, and the
  charger refuses a pack that doesn't match (ADR-048).
- **Socketed compute.** The CM5 plugs in, so memory and processor upgrades are a module swap; storage
  is a standard M.2 NVMe drive.
- **Safe by construction.** Charging stays off until the co-processor has set and read back the correct
  charge voltage; radios and microphones have physical switches; every pin's job and its protection
  against back-powering is checked automatically ([`AGENTS.md`](AGENTS.md) §4).
- **Open all the way down.** Hardware under CERN-OHL-S, software under MIT, and every design decision
  — including the ones we reversed — written up in the
  [decision log](docs/90-history/decisions.md).

---

## Product pillars

These are what the product is judged on. Each one is a **target** until its acceptance gate is
measured; live status is generated into [`docs/STATUS.md`](docs/STATUS.md), and the full
specification is in [`docs/STANDOUT_FEATURES.md`](docs/STANDOUT_FEATURES.md).

| # | Pillar | What it promises | Status |
| :-- | :--- | :--- | :--- |
| P1 | **Dual-brain handoff** | Ambient modes are instant on the co-processor; Linux is back in seconds | aspirational |
| P2 | **Typewriter-on-paper** | Instant haptic and audio feedback per keystroke; ink with no flashing while you type | aspirational |
| P3 | **Sunlight-readable, solar-topped** | Readable in direct sun; outdoors the bezel strip tops up the idle co-processor | aspirational |
| P4 | **Field-ready form** | Thin slate, desk easel, modular grips (`chassis_mm`, `mass_g`) | modelled |
| P5 | **Field hardening** | Hardware airgap switch, GPS, IP54 in V1 (IP67 in V2), rain-lock touch cutoff | aspirational |
| P6 | **Modular upgrade bridge** | Socketed compute module, RAM by module swap, M.2 NVMe | specified |
| P7 | **Voice-first control** | Hold-to-talk button, opt-in hands-free wake word, barge-in | aspirational |

<details>
<summary><b>Engineering bets behind the pillars</b></summary>

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

</details>

---

## V1 at a glance

Numbers live in [`docs/spec_values.json`](docs/spec_values.json); this table names parts and keys.

| Subsystem | V1 design |
| :--- | :--- |
| Compute | Raspberry Pi CM5 (CM5116064: 16 GB RAM, 64 GB eMMC, Wi-Fi/BT), socketed — ADR-031 (`cm5`) |
| Co-processor | RP2350B + 8 MB PSRAM + 16 MB flash |
| Display | 10.3″ E Ink Kaleido 4 colour, pending E Ink's datasheet — ADR-032 (`panel_sku`) |
| Pen / touch | EMR pen layer + capacitive touch, hardware palm blanking |
| Voice | Two MEMS mics owned by the co-processor, speaker, hold-to-talk button, mute switch — ADR-036, ADR-046 |
| Haptics | DRV2605L + frame-mounted LRA, plus typewriter sound — ADR-037 |
| Battery | 1S Li-ion in a user-replaceable smart pack (protection + gauge in the pack); capacity claimed only from a real datasheet — ADR-048 (`battery`, `battery_wh`) |
| Charging & power | BQ25798 charger, STUSB4500 USB-C PD sink, buck-boost always-on rail, power bank capped at 2 A — ADR-035, ADR-048 |
| Solar | Bezel strip with a hardware temperature gate; outdoor top-up only — ADR-041, ADR-048 (`solar_w`) |
| Radios | Wi-Fi/BT on the CM5, u-blox MAX-M10S GPS on the co-processor — ADR-038 (`gnss`) |
| Storage | eMMC + M.2 NVMe + microSD; native USB 3 — ADR-042 |
| Enclosure | PA12 prototypes, PC/ABS production, IP54 target — ADR-039 (`chassis_mm`, `ingress`) |
| **Coming in V2** | LTE with nano-SIM and SGP.22 eSIM (ADR-033), on-board LoRa, NFC, rear camera, snap-on Hotpacks — ADR-034, ADR-044 |

---

## Where things stand

| Area | State |
| :--- | :--- |
| Specs & decisions | Detailed, with one source of truth for numbers and a full [decision log](docs/90-history/decisions.md). |
| Pin budget | Every CM5 and RP2350 pin assigned for V1 and V2, checked against the datasheets ([`docs/PIN_BUDGET.md`](docs/PIN_BUDGET.md)). |
| Power board | Capture-ready design package for the first board, EVT-0 ([`docs/EVT0_POWER_BOARD.md`](docs/EVT0_POWER_BOARD.md)). |
| Schematic / PCB | Not started for real: the KiCad files are unwired placeholders, and there are no fabrication files. |
| Software | Frozen until there is hardware to run it on (ADR-046). |
| Measurements | None yet. Every performance figure is modelled or aspirational. |
| Certification | Not started ([`docs/REGULATORY.md`](docs/REGULATORY.md)). |

**What we're waiting on:**
1. **Kaleido 4 (E Ink).** Announced without public sizes, resolution or a sampling programme; a 10.3″
   version is not yet confirmed. A sales inquiry went to E Ink on 2026-10-21. Panel figures stay `null`
   until the datasheet exists (ADR-032), and the case outline waits on its drawing.
2. **The pen layer.** Wacom works with OEMs under NDA; Hanvon Ugee sells custom EMR modules to
   businesses. We'll ask for quotes once the panel size is confirmed.
3. **A certified Li-ion cell (ADR-048).** Chosen from a datasheet with UN38.3 and IEC 62133 reports;
   `battery_wh.li_ion` stays `null` until then.
4. **Bench numbers.** Linux wake time, wake-word power, heat and charging behaviour come from a dev-kit
   bench, bought once the panel and pen layer are available.

<details>
<summary><b>Kaleido 4 day-one list</b> (the day E Ink's datasheet and drawing arrive)</summary>

- Fill `ppi`, `display_active_mm`, `panel_module_outline_mm`, `display_stack_mm`, `epdc_spi_mhz`,
  `refresh_modes` and the reader geometry in `docs/spec_values.json`, tagged `datasheet`.
- Run `python3 scripts/verify_all.py`: the panel-fit, page-cache and enclosure checks stop skipping and
  report anything that no longer fits.
- Choose the display controller (ADR-032) and check its host interface against `docs/PIN_BUDGET.md`
  (the budget assumes SPI plus ready and reset).
- Freeze the case outline (ADR-039) and the battery bay, then capture the carrier schematic.

</details>

---

## Working in this repo

```sh
python3 scripts/verify_all.py         # 16 phases; green = internally consistent, NOT a design sign-off
git config core.hooksPath .githooks   # once per clone: the suite runs before every push (no hosted CI)
```

- Start with [`docs/README.md`](docs/README.md) (reading order and claim vocabulary), then
  [`docs/WORKFLOW.md`](docs/WORKFLOW.md) (how changes are made) and [`AGENTS.md`](AGENTS.md) (hard
  rules, including the battery, RF and waveform safety constraints).
- Every number belongs in [`docs/spec_values.json`](docs/spec_values.json) with a tag: `measured`,
  `datasheet`, `modelled`, `aspirational`, or `null`.
- Contributing: [`CONTRIBUTING.md`](CONTRIBUTING.md). Security model: [`SECURITY.md`](SECURITY.md).
  Outside review: [`docs/REVIEW_PACKET.md`](docs/REVIEW_PACKET.md).

| Path | Contents |
| :--- | :--- |
| `docs/` | Specs, audits, decisions, the single source of truth |
| `hardware/` | KiCad sources (placeholder), enclosure OpenSCAD; `production/` is NOT FOR FAB (ADR-046) |
| `firmware/rp2350/` | Co-processor firmware and host tests |
| `src/daemons/`, `src/dts/` | Linux daemons and the CM5 device-tree overlay (not yet ported to RP1) |
| `tools/provision/` | OS provisioning script |
| `scripts/` | The verification suite |

## License

Hardware CERN-OHL-S-2.0, software MIT, documentation CC-BY-SA. The per-path map is in
[`LICENSES/PATHS.md`](LICENSES/PATHS.md).
