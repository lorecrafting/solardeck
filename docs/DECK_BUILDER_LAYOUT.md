# SolarDeck Deck-Builder Assembly Guide — Snap-in vs Soldered, and the Self-Diagnosis Contract

Written 2026-10-20 22:10 UTC in the Pi harness by openrouter/deepseek/deepseek-v4-flash-0731

Purpose: classify every `BOM_COST_ESTIMATE.md` line as **snap-in (user-serviceable)** or
**soldered (factory-welded)** so the SolarDeck quote (`HANDOFF_TO_FABLE.md`) is structured around a
user-assemblable "Deck-Builder" top layer — and to make that modularity serve the project's
AI-self-diagnosis ambition: an on-device LLM that reads telemetry and explains *which part is
failing or degrading, and where power is going*. Companion to
`MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md` and `SOFTWARE_SPEC.md` §3.3.1 (telemetry DB).

---

## 1. The principle: weld the substrate, snap the modules

| Layer | Technology | What it carries |
| :--- | :--- | :--- |
| **Substrate (carrier PCB)** | Factory-soldered SMT: power rails, bus mux, charge tree, air-gap gates | The safety-critical, density-crazy, thin-slab part — cannot be Lego |
| **Sockets/studs** | M.2, MFF2, SMA, standoff posts, FPC latches | The *user-assemblable* interface — Lego studs |
| **Modules** | CM4, LTE, eSIM, antennas, panel, RP2350 dev brick | The expensive, swappable, diagnosable top layer |

Rule: if it is dense (<0.5 mm pin pitch), carries the always-on rail, or is a safety gate → welded.
If it has a human-scale interface (screw, latch, twist-on) → snap.

---

## 2. Parts tree — every BOM line, one verdict

### Snap-in (user, no solder, with a screwdriver)

| Part | Interface | Diagnosable? (see §4) |
| :--- | :--- | :--- |
| CM4 (8 GB) | 2× standoff screws + board-to-board connector | ✅ identity + current sense on its rail |
| EG25-G LTE + MIMO antennas | M.2 Key-B slot + 2× SMA | ✅ AT diagnostics + GNSS fix telemetry |
| ST4SIM eSIM | MFF2 socket | ✅ managed via `lpac` (AT+CCHO/CGLA) |
| SX1262 LoRa + whip | Castellated pad *or* socket + SMA | ✅ RSSI/SNR telemetry |
| Panel (K3/Carta) + EMR | FPC latch (40/50-pin) | 🟨 physical latch, delicate; health via refresh-ACK latency |
| Speaker / dual MEMS / piezo | Fly-wires + micro connectors | ✅ audio-loop self-test |
| Battery pack | Screw-down terminals + strap | ✅ charge/discharge curve fit (see §4) |
| Solar strip | Adhesive + JST | ✅ mA from strip telemetry |

### Either-layer (both possible — quote decides)

| Part | Snap version | Soldered version | Note |
| :--- | :--- | :--- | :--- |
| RP2350 co-processor | **PGA2350 dev brick (pin grid, $12)** — fully user-insertable | Bare RP2350B soldered | The dev-brick route makes the co-proc a user-swappable brain — and lets users flash their own firmware |
| PSRAM (8 MB) | On the PGA brick | Soldered next to bare chip | Same job, two form factors |

### Soldered (factory; the welded spine)

| Part | Why it cannot be Lego |
| :--- | :--- |
| BQ25895 charger, TPS62840/TPS61088/TPS63020 rails | Power-delivery ICs: always-on rail, brownout-critical, sub-millimetre pitch |
| TPS22918 load-switch gates | **Safety + sleep-floor hard requirements** (air-gap cut, <25 mW floor, G6/G12) — a connector here is a failure point in the one rail that must never fail |
| TMUX1575 bus mux pair | Display-bus isolation; a loose contact = glitch mid-refresh |
| VL805 / ASM1042A / USB2514B hub | BGA-class package — not hand-solderable, not snap-pable |
| ST4SIM is snap; but **battery terminals + cells** | The cells' welded tabs are a fire-safety joint — never a snap |
| Camera (IMX708) | Flush optical alignment — factory |

---

## 3. Shopping list for the quote — "Deck-Builder sockets" request

When structuring the Seeed/JLCPCB request, ask for the carrier to be *born with these studs*:

1. **M.2 Key-B slot** (LTE) + **SMA stub mounts ×3** (LTE main/div + LoRa) + **U.FL** (Wi-Fi/GNSS)
2. **MFF2 eSIM socket** (click-in, `lpac`-manageable)
3. **40-pin FPC latch** for the panel (already specced)
4. **Standoff post inserts ×2** for CM4; **CG-adjacent posts** for the RP2350 PGA brick (PGA2350 is 64-pin 25.4 mm — a pinned socket for it is feasible if the quote allows a 2.54 mm-pitch castellation)
5. **Per-rail current-sense nodes** — the *diagnosis* requirement, not just assembly: a µA-grade sense point (sense resistor + ADC feed to RP2350) on each TPS22918-gated load rail (LTE, Wi-Fi, audio) and on the CM4 rail. See §4.
6. **JTAG/UART breakout** (TP_SWD_CLK/TP_SWD_DIO/TP_UART_* already exist in `HARDWARE_SPEC.md:635` — keep them in the quote as the diagnosis ports)

---

## 4. The self-diagnosis contract (this is the win modularity buys)

An on-device LLM (the repo's stated local-AI ambition, `SOFTWARE_SPEC.md` §4) cannot *look* at the
board — it can only read what instrumentation reports. So the design contract is: **every module
boundary emits a health row, every rail emits a current number, and the LLM compares them against
`spec_values.json` budgets.** That is exactly the "explains what part is failing or degrading and
power constrictions" you described. The modular top layer makes each reading *isolable*.

| Diagnostic | Sensor | LLM conclusion (example) |
| :--- | :--- | :--- |
| **Power constriction / overdraw** | µA sense per rail (§3.5) vs `spec_values.power.*` / `sleep_ladder.*` | "LTE rail draws 2.1× budget at idle → EG25-G module degrading or modem stuck in high-power; swap-test the M.2 module" |
| **Battery degradation** | Charge/discharge curve fit from telemetry DB | "Battery has 82% of 30 Wh → 18% capacity fade, near mid-life threshold (`longevity.*`)" |
| **E-ink panel wear** | Partial-refresh ACK latency creep + ghosting rate | "Refresh latency +38 ms over 90 days → panel pigment wear or waveform drift; re-run DC-balance calibration" |
| **RF degradation** | SX1262 RSSI/SNR, EG25-G signal stats | "LoRa RSSI floor −15 dB vs mesh baseline → antenna SMA loose or cable fatigue; check the twist-on joint first" |
| **Thermal / airflow** | On-board NTC per zone | "Charger zone runs 8 °C over profile → BQ heat-spread degradation, recommend service" |
| **Register-level** | CM4 SMART, eMMC wear counters (already in telemetry) | "eMMC at 61% endurance → plan recapture within the 30-year budget (`longevity`) precedence" |

**Swap-test isolation** is the modular dividend: when the LLM names a suspect module, the
remediation is *user-safe* — pop the M.2/SMA/PGA unit, bench-test it, replace. In a fully-welded
world the LLM can still isolate by rail signature but the repair isn't user-doable. So modularity
turns "diagnosis" into "diagnosis **and** self-service."

**Honest ceiling:** the LLM diagnoses what instrumentation senses. A cracked BGA pad under VL805 is
invisible without per-module register health and thermal zones — which is why §3.5 and NTC zones
are quote-line items, not afterthoughts.

---

## 5. Minimal diagnostic interface per module (the actual contract)

Keep it boring — one small recurring pattern per module:

```
Module ↔ RP2350/CM4      Module emits:
  UART/SPI health line   status register (ok/waning/fault) + one numeric
  rail sense (µA)        actual vs spec_values budget
  self-test hook         ("squawk now", returns ok/latency)
```

- CM4: SMART + eMMC wear + rail sense
- LTE: AT+CSQ, GNSS fix, rail sense
- LoRa: RSSI/SNR, rail sense
- Panel: per-refresh ACK latency (already needed for G1), ghosting counter
- Battery: coulomb-counted charge/discharge curve
- Audio: loopback self-test (padded output, measured mic RMS)

The LLM tier then sits on `telemetry.db`, joins with `spec_values.json`, and emits
"module X is the problem, here is the evidence, here is the swap procedure" — the exact
self-diagnosis loop requested.

---

## 6. What does NOT change

- The power/charge/safety spine stays factory-soldered (Section 2, Soldered) — never user-welded.
- Bench order is unchanged: `DEV_KIT_BENCH.md` Tranche 1 first; module-instrumentation findings
  from the bench feed the §3 socket list *before* the PCB quote, so the quote already includes the
  M.2/MFF2/SMA/pin-grid studs and the rail-sense nodes. Do not quote sockets before the bench.
- `docs/verify_all.py` enforces doc↔`spec_values.json` consistency; new keys only after bench
  data earns them (`measured <date>` per `WORKFLOW.md`).