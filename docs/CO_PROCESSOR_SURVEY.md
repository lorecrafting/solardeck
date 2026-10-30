# Co-Processor Options Survey & PSRAM Read-Mode Dig

Written 2026-10-21 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-0731
Revised 2026-10-21 15:59 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).
Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).
Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).
Revised 2026-10-29 07:20 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa and BLE in V1 on a radio MCU, ADR-055).

Status: **investigation record** — no design change committed by this document alone. Open question:
does the max-tier (ESP32-P4) or a bigger PSRAM on the RP2350 enter V1? See `docs/90-history/decisions.md`
for the ADR that will lock it. Companion: `docs/SOFTWARE_SPEC.md` §55 (reader tier) and
`docs/MVP_ARCHITECTURE.md` (power tiers).

---

## 1. The survey question

SolarDeck's sleep story is a one-chip ladder today: the RP2350 co-processor owns RTC, ADC sampling,
PSRAM frame cache, Linux wake, and the reader tier. This survey asks three things:

1. Who else does the "dual ARM/RISC-V" trick, and at what power?
2. What would a *3-tier* co-processor ladder (ultra-low / mid / max) actually buy?
3. Does the reader tier hit a PSRAM ceiling worth removing?

## 2. The candidates

| Chip | Architecture | Clocks | Sleep / deep-sleep | Why it rates for us |
| :--- | :--- | :--- | :--- | :--- |
| **RP2350** (incumbent) | Dual Cortex-M33 *or* dual Hazard3 RISC-V, pick at boot | 150 MHz | **10 µA** POWMAN (~0.033 mW @ 3.3 V) | Already specced; native QSPI PSRAM up to 16 MB per chip-select via the QMI |
| **RP2040** | Dual Cortex-M0+ | 133 MHz | ~180 µA (~0.59 mW) | Already in the BOM as the $0.70 USB bridge MCU (`BOM_COST_ESTIMATE.md`) |
| **ESP32-C6** | **Dual RISC-V**: 160 MHz HP core + LP co-core that keeps running in deep sleep | 160 MHz + LP | **7 µA** chip-level (~0.023 mW); boards ~15–70 µA | Wi-Fi 6 / BLE / Zigbee / Thread — the Matter radio switchboard |
| **ESP32-P4** | **Dual RISC-V**: 400 MHz dual-core HP + 40 MHz LP co-processor | 400 MHz | **12 µA** deep sleep (~0.040 mW); 0.075–0.8 mA light sleep | In-package 16/32 MB PSRAM; MIPI-DSI; H.264; 1080p ISP; vector AI exts — the *max* tier |
| **Ambiq Apollo 5** | Cortex-M55 + Helium vector (no dual-ISA trick) | 192 MHz | sub-µA standby | 30× better AI energy efficiency; always-on-voice benchmark — the *power* king |
| **TI AM62x** | Cortex-A53 app cores + Cortex-M4F MCU domain | GHz + M4F | mA-range standby | Linux-capable; M4F real-time — but standby is mA, disqualifying for coin-cell fan |

Key structural point: the ESP32-C6/P4 and RP2350 independently converged on the *same* trick — a
low-power co-rear that stays awake while the high-performance cores sleep. The niche is real but not
crowded; no vendor does ARM **and** RISC-V simultaneously (RP2350/C6/P4 are *one ISA, two tiers*; the
dual-ISA line in the table is "which ISA you boot into").

## 3. Power envelope vs. battery (capacity TBD, ADR-040)

`native-read` tier today sits at 4.5 mW; the floor is the cell's own shelf life, not the silicon. Days on
one charge are TBD until each tier is measured; derive the column from `battery_wh.li_ion` (ADR-049).

| Mode | Power | Days on one charge | Sobered note |
| :--- | :---: | :---: | :--- |
| **RP2350 reader tier** (incumbent) | 4.5 mW | TBD (ADR-040) | The real number, once the tier is measured. |
| RP2350 POWMAN deep sleep | ~0.033 mW | TBD (ADR-040) | Meaningless — beyond the pack's self-discharge and first wear-out (`reliability.first_wearout_years`) |
| ESP32-C6 deep sleep | ~0.023 mW | TBD (ADR-040) | Same caveat |
| ESP32-P4 deep sleep | ~0.040 mW | TBD (ADR-040) | Same caveat |
| ESP32-P4 light sleep | 1.3 mW | TBD (ADR-040) | The *honest* P4 advantage: it stays interactive longer |
| ESP32-C6 active, no RF | ~6 mW | TBD (ADR-040) | The floor you'd actually live in if the C6 ran the mesh |
| Opt-in wake-word tier (§17.2, ADR-036) | TBD (bench) | TBD (ADR-040) | The rung that matters — where a *snappier* max tier would slot in |
| Meshtastic-peer mode (opt-in, ADR-055) | `radio.meshtastic_mode_idle_mw` (null until measured) | TBD (ADR-040) | Receiver always on; outside the solar-strip claim. Station check-in, the default, is `radio.station_mode_idle_mw` |
| R4 keepalive + LoRa beacon | 0.2 mW | TBD (ADR-040) | The deep-off floor; battery-bound, not power-bound. Radio power is not counted here (ADR-055) |

**The sobering edit:** every sub-mW cell turns into "years" — but the Li-ion pack wears out first
(`spec_values.reliability.first_wearout_years`) and self-discharges long before "years" matter. **No
co-processor choice extends battery life; only the power modes around it do.** The reader tier is not
power-bound. This kills candidate #1 (a lower tier) with a clean YAGNI.

## 4. Would a 3-coprocessor ladder help?

| Tier | Chip | Would it buy? | Verdict |
| :--- | :--- | :--- | :--- |
| **Ultra-low** (R4 keepalive, 0.2 mW today) | ESP32-C6 7 µA | Goes 0.2 mW → 0.023 mW | **YAGNI — already bound by the cell's shelf life, not the silicon.** Extra chip, extra SPI bus, extra security surface, zero user-visible gain. |
| **Mid** (reader + wake-word, incumbent) | RP2350 | Reader and wake-word runtimes TBD (ADR-040) | **Keep.** POWMAN 10 µA deep sleep + native PSRAM is the right center. |
| **Max** (snappier reader, richer zero-kernel tier) | ESP32-P4 (400 MHz, 16–32 MB in-package PSRAM, MIPI, H.264) | 4× clocks; 2–4× PSRAM; hardware display IFs | **Tempting, but unproven against our panel.** P4's display muscle is for DSI/CSI panels; the host interface of the Kaleido 4 display controller (TBD, ADR-032) is unknown. Paying for a MIPI pipeline before that is known is the classic over-build. |

**Honest verdict: do not add a third co-processor.** The real ceiling in the reader tier is PSRAM
*size and frame format*, and both are solvable on the incumbent RP2350 — see §5. If a "snappier
reader" is ever needed beyond that, re-open the P4 once the Kaleido 4 controller's host interface is known (ADR-032), not before.

## 5. PSRAM read-mode dig: the actual lever is 16 MB → better, and 1-bit frames → *free*

The reader holds 8-bit frames (`page_width_px` × `page_height_px` × 1 B each) in 8 MB of PSRAM. Page
geometry is TBD (ADR-032): it comes from the Kaleido 4 resolution. Two findings reset the calculus:

1. **The RP2350 QMI (QSPI Memory Interface) addresses up to 16 MB per chip-select, 32 MB total** across
   its two CS lines. The 8 MB `APS6404L` is not the chip's ceiling — it's the *part*'s ceiling:
   SOIC-8 QSPI PSRAM tops out at 8 MB (64 Mbit) today; 16/32 MB PSRAM parts exist only as Octal-SPI
   (APS6408H-class) in 24-ball BGA, which the RP2350 QMI does not speak. **A 16 MB QSPI SOIC-8 part
   does not exist on the market yet.**
2. **Frame format is the free lever.** `page_bytes_8bit` = width × height B; a 1-bit dithered frame is
   exactly ÷8 of that. The same 8 MB therefore holds 8× as many 1-bit pages as 8-bit pages, with zero
   BOM change. The page counts (`single_buffer_pages_1bit` = ⌊8 MB ÷ `page_bytes_1bit`⌋,
   `double_buffer_pages_1bit` = half that) are TBD (ADR-032) until the Kaleido 4 resolution is published. For a book (mono
   text on E-Ink), 1-bit + dithering is the correct visual encoding anyway — Kaleido colour pages stay
   8-bit.

Consequences (all `spec_values.reader` keys):
* `page_bytes_1bit`, `double_buffer_pages_1bit`, `single_buffer_pages_1bit` exist and stay `null` until the
  Kaleido 4 resolution is published (ADR-032); derive them with the method above.
* `page_cache_psram_mb` stays 8 MB — the *size* is right; the *usage* was 8× wasteful.
* The `aspirational` text-reflow path (§55.2) becomes free-er: 8× as many pages of a reflowed bitmap
  layout can live in cache.
* Future 16 MB path (only if a QSPI 16 MB part appears): re-derive the table, no architecture change —
  the RP2350 already addresses it.

## 6. What this means for V1 (draft for ADR)

1. Keep the single RP2350 co-processor. No lower tier (YAGNI), no P4 max tier (MIPI-mismatch).
2. Reader tier switches pre-rendered frames to 1-bit dithered for mono books (8× the 8-bit page count
   in the same 8 MB; counts TBD, ADR-032); 8-bit reserved for colour/photo pages.
3. Fill `page_bytes_1bit` and the page counts in `spec_values.json` once the Kaleido 4 resolution is
   published (ADR-032), so the checker locks the numbers to the doc.
4. Re-open the P4 question only when the panel changes, the QSPI 16 MB part appears, or a zero-kernel
   audio/video tier is wanted.

## 7. Sources

- RP2350 datasheet (Raspberry Pi): QMI, XIP memory map `0x10000000–0x15FFFFFF`, POWMAN, dual ARM/RISC-V.
- ESP32-C6 datasheet (Espressif): 7 µA deep sleep, dual RISC-V HP/LP cores, 512 KB SRAM.
- ESP32-P4 product brief (Espressif): 400 MHz dual-core RISC-V + 40 MHz LP, 12 µA deep sleep,
  16/32 MB in-package PSRAM variants (`P4NRW16X/32X`), MIPI-DSI/CSI, H.264.
- Ambiq Apollo 4/5: SPOT sub-threshold, 4–5 µA/MHz active, sub-µA standby, Cortex-M55 + Helium.
- APMemory APS6404L/APS3204L: SOIC-8 3.3 V QSPI PSRAM, 8 MB / 4 MB. Current BOM part.
- Raspberry Pi Pico 2 teardown / SparkFun RP2350 boards: 8 MB PSRAM (APS6404-class) as the shipped norm.