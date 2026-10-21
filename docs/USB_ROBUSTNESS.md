# USB_ROBUSTNESS.md — Every Way USB-C Fails, and What the Hardware Does About It

Written 2026-10-20 13:05 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

The quoted failure is the most common one in the field: a USB-C device with **no 5.1 kΩ Rd pull-downs**
looks like nothing at all to a Mac's Thunderbolt port, so a C-to-C cable "doesn't work" and the user
concludes the device is dead. SolarDeck has two C ports (and, in V2, a Hotpack bus — ADR-034), so it can hit this six
different ways. This is the taxonomy and the rules that close each one.

Machine-readable constraints: `docs/spec_values.json` → `usb`.
Enforced by `scripts/check_longevity.py` (Phase 13).

---

## 1. The failure taxonomy

| # | Failure | Mechanism | Who hits it |
| :-- | :--- | :--- | :--- |
| 1 | **No Rd ⇒ C-to-C dead** | Sink must present 5.1 kΩ on **both** CC1 and CC2. No Rd = host sees an open, sends no VBUS, no data | Mac, any PD host, any C-to-C cable |
| 2 | **One Rd instead of two** | Works on a C-to-A cable (one CC), fails on C-to-C (host needs both) | Intermittent — worst kind |
| 3 | **Shared Rd** | One 5.1 kΩ tied to both CC pins reads as 2.55 kΩ ⇒ host interprets as an *audio accessory* or a source | Rare, and misdiagnosed as a bad cable |
| 4 | **Dead-battery no-Rd** | Rd is presented by an IC (TUSB320/TPS25750) that has no power at 0 V. Flat battery ⇒ no Rd ⇒ **cannot charge from a C-to-C charger**. The classic "my device won't wake up" | Every device whose CC logic is firmware-powered |
| 5 | **Charge-only cable** | No D+/D- inside. Power works, enumeration never happens | Unavoidable; must be **diagnosable** |
| 6 | **CC capacitance / stub** | A filter cap on CC breaks BMC PD signalling; a long stub corrupts it | Design-induced, silent |
| 7 | **Over-current negotiation** | Sinking 3 A from a 500 mA port ⇒ host cuts the port and blames the device | Cheap chargers, hubs |
| 8 | **Two sources fighting** | Laptop on Port 1, panel on Port 2 ⇒ circulating current without OR-ing | Already solved (LM66100) |
| 9 | **Back-powering the host** | Device sources 5 V onto a port that is being charged | Already solved (LM66100 + TPS2051B) |
| 10 | **Flashing depends on USB** | If the only recovery path is USB, failure 1 or 5 bricks the unit | Every board without a second door |

Failures 1–4 are one design decision; 5 is a *diagnostic* problem, not a hardware one; 10 is the one
that turns a cable problem into an RMA.

---

## 2. The rules (all in `spec_values.usb`)

**R1 — Passive Rd is the floor, always.** Each USB-C sink port carries **two independent 5.1 kΩ ±1 %
resistors, one per CC pin, to GND**, populated whether or not the CC controller is powered. The
controller may *override* them for DRP/source mode; it may never be the only path to them. This is what
makes C-to-C work with a Mac, a ThinkPad, a phone, and a $3 hub, and it is the difference between
failures 1–3 and a working port.

**R2 — Dead-battery Rd is non-negotiable.** At 0 V, before any rail is up, both CC pins must still
read 5.1 kΩ. Verified by measurement, not by datasheet claim: power the board from a bench supply at
0 V, probe CC1/CC2 to GND, expect 5.1 kΩ ±1 %. This is the single check that catches failure 4.

**R3 — No capacitance on CC.** No filter caps, no TVS on CC beyond what the controller integrates, no
test points with long stubs. CC is a current-mode signalling pair for PD; 100 pF of convenience breaks
it. (ESD on CC is handled inside the CC controller.)

**R4 — Advertise, then respect.** TPS25750 reads the host's advertised current and the firmware must
clamp charging to it. Never assume 3 A.

**R5 — Every Hotpack repeats R1 and R2 (Hotpacks are V2, ADR-034).** A Hotpack is a USB-C sink with its own CC pins; a missing Rd
pair in a $20 accessory reproduces failure 1 for the whole tablet. Hotpack spec includes the two
resistors and the dead-battery check.

**R6 — Charge-only cable must be *visible*, not mysterious.** If VBUS is present for >3 s with no
enumeration, `solardeck-diag` reports `USB_NO_DATA_LINES: cable has power but no data — use a data
cable` on the E-Ink panel. The user gets a sentence instead of a dead device. Costs ~0.

**R7 — Three independent recovery doors.** Flashing and recovery must not depend on USB enumeration:
1. **BOOTSEL pinhole** on the RP2350 (UF2 over USB *if* USB works).
2. **UART/SWD 4-pin header** under the M.2 service hatch (§4.6) — always works, needs no CC at all.
3. **microSD recovery image** — boot a signed image from the edge slot.
Losing USB is then an inconvenience, never a brick.

**R8 — Mechanical and ESD.** Recessed receptacle (already), strain relief on the shell (already),
TPD4E05U06 on D+/D- (already). Cable insertion force is taken by the chassis, not the solder joints.

---

## 3. The test matrix (gate G11)

Every row must pass before a build is called field-ready. Rows 1–3 are the ones that fail in the wild.

| # | Test | Pass criterion |
| :-- | :--- | :--- |
| 1 | Mac C-to-C, powered device | Enumerates as gadget; charges |
| 2 | Mac C-to-C, **flat battery (0 V)** | Enumerates; charges — proves R2 |
| 3 | USB-A→C through a hub | Enumerates; charges |
| 4 | Charge-only cable | `USB_NO_DATA_LINES` diagnostic within 3 s — proves R6 |
| 5 | PD charger only (no data) | Charges at advertised current, no enumeration needed |
| 6 | Laptop on P1 + panel on P2 | No circulating current; highest voltage wins |
| 7 | Device plugged into P2 as host | 1.5 A limit holds; short-circuit cutoff works |
| 8 | CC1/CC2 to GND at 0 V | 5.1 kΩ ±1 % on each pin — proves R1/R2 |
| 9 | 500 mA port, high load | Current clamped, port not shut down |
| 10 | Recovery with USB disabled | UART header and microSD image both boot |

---

## 4. Why this is cheap

Total cost of R1–R8: **four 5.1 kΩ 1 % resistors ($0.02), two pinholes, one 4-pin header, a diag
message.** The alternative is the support burden of every user who owns a C-to-C cable and a Mac —
which, in 2026, is most of them.

→ skipped: a USB-PD protocol conformance suite. TPS25750 is pre-certified for PD; re-testing its
protocol is paying twice. The rows above test *our* port, not TI's silicon.
