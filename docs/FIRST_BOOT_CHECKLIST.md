# SolarDeck V1 — Field Bring-Up & First Boot Checklist

*Written 2026-10-19 16:45 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Revised 2026-10-21 16:01 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

Revised 2026-10-21 16:45 UTC in Claude Code by anthropic/claude-opus-5-5 (V1 scope, ADR-034–043).

Revised 2026-10-21 17:22 UTC in Claude Code by anthropic/claude-opus-5-5 (LoRa to V2, ADR-044/045).

Revised 2026-10-21 17:53 UTC in Claude Code by anthropic/claude-opus-5-5 (RTC chip, jack removed, ADR-046).

Revised 2026-10-21 19:45 UTC in Claude Code by anthropic/claude-opus-5-5 (Li-ion smart pack, ADR-048).

This step-by-step technical punch list guides the hardware engineer or field operator from unboxing the DHL Express package from Seeed Studio Fusion in Honolulu to running an authorized terminal session in pure sunlight.

---

## 1. Unboxing & Physical Inspection (Cold State)

**Equipment Needed:**
* Anti-static ESD mat and grounded wrist strap.
* Digital Multimeter (DMM) with fine-point needle probes.
* Illuminated inspection loupe / digital microscope.
* #0 Phillips and T5/T6 Torx precision screwdrivers.

### Visual Inspection Steps
1. **Packaging Verification:** Inspect the anti-static shielded bubble bag for transit punctures or crushed corners. Confirm Seeed QC pass sticker.
2. **Hirose 100-Pin Sockets (`J1`, `J2`):** Inspect the dual 0.4mm pitch DF40 connectors under 10x magnification. Ensure zero bent pins, solder bridges, or flux residue.
3. **EPDC FPC Connector (`J_EPDC`):** Verify the flip-lock actuator (pin count and pitch TBD with the Kaleido 4 panel, ADR-032) is undamaged and moves freely.
4. **Solder Joint Inspection:** Inspect the QFN-80 package of the RP2350B, the TI BQ25798 charger, and the TI TMUX1575 bus switch for solder bridging or tombstoned 0402 passives.
5. **Cold-Storage Vault:** Verify the gasketed hatch fits flush and the 3x friction-fit MicroSD slots retain cards securely.

---

## 2. Cold Resistance Sanity Checks (Zero Power Applied)

**Rule:** NEVER connect a battery or USB-C power cable until every major power rail passes the cold resistance check. Solder whiskers across low-impedance rails can instantly destroy the CM5 or RP2350.

Connect the DMM negative lead to a chassis ground pad (`TP_GND`) and measure resistance in Ohms ($\Omega$):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 COLD RESISTANCE POWER RAIL SANITY MATRIX                    │
├─────────────────┬──────────────┬──────────────────┬─────────────────────────┤
│ TEST POINT      │ RAIL NAME    │ MIN RESISTANCE   │ EXPECTED NOMINAL        │
├─────────────────┼──────────────┼──────────────────┼─────────────────────────┤
│ `TP_VBAT`       │ Battery Rail │ > 50 kΩ          │ > 100 kΩ (Cap charging) │
│ `TP_SYS_3V3`    │ Main 3.3V    │ > 5 kΩ           │ 12 kΩ – 25 kΩ           │
│ `TP_ALWAYS_3V3` │ AON 3.3V     │ > 20 kΩ          │ 40 kΩ – 80 kΩ           │
│ `TP_VBUS_5V`    │ USB-C 5V     │ > 50 kΩ          │ > 200 kΩ                │
│ `TP_VCORE_1V1`  │ CM5 Core     │ > 400 Ω          │ 600 Ω – 1.2 kΩ          │
│ `TP_SOLAR_IN`   │ Solar Anode  │ > 100 kΩ         │ > 500 kΩ (Reverse diode)│
└─────────────────┴──────────────┴──────────────────┴─────────────────────────┘
```

* **Action on Failure:** If any rail reads $<10\ \Omega$, do NOT power on. Inspect with microscope for solder balls near QFN thermal pads or decoupling capacitors.

---

## 3. Co-Processor Bring-Up & Firmware Flashing

Before inserting the CM5, initialize the RP2350B co-processor to confirm power sequencing:

1. **Bench Power Configuration:** Set an adjustable bench power supply to **3.30V with current limit clamped to 50 mA**. Connect to battery terminal `J_BAT`.
2. **Current Draw Verification:**
   * Observe current draw on bench supply.
   * Expected: **$<1\text{ mA}$** (typically 60 nA to 12 µA baseline sleep).
   * If current hits 50 mA clamp, immediately disconnect and inspect the always-on buck-boost regulator (TPS63900 class, ADR-048).
3. **Flashing the RP2350 Firmware:**
   * Hold the physical `BOOTSEL` button on the carrier board.
   * Connect your host computer to the RP2350 USB pins on the **recovery header** (`uart_swd_header`; USB-C Port 1 is the CM5's OTG / `nRPI_BOOT` port — docs/PIN_BUDGET.md §2).
   * Release `BOOTSEL`. The host PC will mount a mass storage volume named `RPI-RP2`.
   * Drag and drop `firmware/rp2350/build/solardeck_rp2350.uf2` into the volume.
   * The volume will automatically unmount, and the onboard green status LED (`D1`) will begin a 1 Hz heartbeat blink.
4. **Co-Processor Serial Console:**
   * Open serial terminal at 115,200 baud on the virtual COM port:
     ```bash
     picocom -b 115200 /dev/ttyACM0
     ```
   * Confirm the banner appears:
     ```
     [SOLARDECK-RP2350] Co-Processor Initialized.
     [RTC] RV-3028-C7 detected: VALID.
     [PSRAM] APS6404L 8MB QSPI test: PASSED (0 errors).
     [INA3221] Voltage Monitor: VBAT=3302mV, ISYS=4.2mA.
     ```

---

## 4. Compute Module & E-Ink Display Integration

1. **Mount Compute Module 5 (CM5116064, ADR-031):**
   * Disconnect all power.
   * Align the Raspberry Pi CM5 over Hirose DF40 sockets `J1` and `J2`.
   * Press down evenly on both ends until both connectors click firmly into place.
   * Install the anodized aluminum CM5 retention bracket with 4x M2.0 screws.
2. **Connect E-Ink Panel & Wacom Digitizer:**
   * Insert the FPC ribbon cable from the 10.3" Kaleido 4 panel into `J_EPDC`. Lock the flip actuator.
   * Connect the 8-pin Wacom EMR digitizer ribbon into `J_WACOM`.
3. **Flash the CM5 eMMC:**
   * Flash Raspberry Pi OS Lite (64-bit) to the CM5's on-module eMMC over USB with `rpiboot`/usbboot (TBD — verify CM5 procedure).
   * Run the provisioning engine:
     ```bash
     sudo ./tools/provision/setup_solardeck_os.sh
     ```

---

## 5. First Boot & Verification Run

1. **Power Application:**
   * Connect the Li-ion smart pack (capacity TBD until the cell is chosen, ADR-040) to `J_BAT` through its keyed connector (ADR-048).
   * Confirm the RP2350 reads the pack gauge's design charge voltage over the pack connector's SDA/SCL before any charge is enabled, and that a pack (or gauge-programmed test pack) reporting a different design voltage is refused: charging stays off (ADR-048).
   * Connect a USB-PD 20W charger to USB-C Port 1. Confirm charging stays **off** until the RP2350 has written the BQ25798 VREG to `battery.charge_limit_v` (charger enable pin held off, ADR-035); only then does the amber charge LED illuminate. Read VREG back over I²C before leaving the pack on charge.
   * Verify the solar harvester's hardware temperature gate: with the pack NTC driven outside the charge-temperature window (heat or cool the NTC, or substitute a resistor), the harvester's output must switch off with no firmware involved (`harvester.temperature_gate`, AGENTS §4.1).
2. **Cold Boot Execution:**
   * Press the physical Power button on the top edge for 1.5 seconds.
   * The RP2350 co-processor will enable the CM5 (enable net TBD — verify on CM5) and cycle the reset net of the Kaleido 4 display controller (TBD, ADR-032).
   * The 10.3" E-Ink panel will execute an initial global white clearing flash.
   * Linux boots to the console login on the paper screen in seconds (ADR-036; no sub-second claim).
3. **Execute Automated Built-In Self-Test (BIST):**
   * Log in to the terminal and execute:
     ```bash
     solardeck-diag --json | jq .
     ```
   * **Acceptance Gate:** All 8 domains must report `"status": "PASS"`:
     - `power`: Battery voltage, cell impedance, solar harvesting ADC.
     - `coprocessor`: Firmware version, PSRAM integrity, RTC sync.
     - `display`: Kaleido 4 display controller (TBD, ADR-032) communication, temperature LUT matching.
     - `i2c_bus`: All 7 core sensors responding (`0x60`, `0x44`, `0x12`, `0x68`, `0x5D`, `0x40`, `0x6B`).
     - `environmental`: SHT40 internal humidity $<30\%$ (desiccant active).
     - `audio`: Dual MEMS mics, speaker echo-cancel reference and hardware mute switch functional.
     - `rf`: MAX-M10S GNSS UART response (ADR-038). No on-board LoRa in V1 (ADR-044).
     - `storage`: NVMe/eMMC write speed $>250\text{ MB/s}$.

---

### 5b. Sleep Gate (ADR-036)

The CM5 (BCM2712) has no RAM-retaining low-power state (ADR-031, AUDIT 6 X4), so `sleep_ladder` R2
is `null`: ambient modes (clock, reader) run on the RP2350 with the CM5 off, and Linux resumes
from off/hibernate in seconds. Nothing in CI measures either. Run this gate before accepting any
power claim:

* **Ambient floor:** with the CM5 off and every TPS22918 load hard off, the measured draw (USB-C PD
  meter or INA3221 telemetry) is **< 25 mW**.
* **Linux resume:** time power-button press to console login from hibernate and from cold off;
  record both as `measured <date>` against `sleep_ladder.r3_resume_s`.
* **If it fails:** record the kernel version and the firmware commit in this checklist, downgrade
  the claim to `modelled` in `README.md`, and re-scope the runtime arithmetic in
  `MVP_ARCHITECTURE.md`. Do not ship a number the board does not reach.
* **Replace the constant:** `firmware/rp2350/src/solardeck_sm.c` still records a hardcoded sub-second
  wake time from the withdrawn S2idle design. Replace it with the measured resume time from
  `docs/spec_values.json` and assert against that.

---

## 6. Wacom Stylus & Touch Calibration

1. **Stylus Hover & Pressure:**
   * Touch the battery-free Wacom stylus to the glass.
   * Verify cursor tracks hover up to 10mm above the surface.
   * In Xournalpp or Neovim inking mode, confirm 4096 pressure levels render with $<18\text{ms}$ visual latency.
2. **Torrential Rain Water-Lock Test:**
   * Spray water mist onto the glass.
   * Slide the tactical rocker switch to **WATER-LOCK**.
   * Confirm capacitive touch is disabled while the Wacom stylus continues writing flawlessly through water droplets.

---

## 7. Field Sign-Off Gate

Once all steps pass:
* [x] Cold resistance verified on all 6 power rails.
* [x] RP2350 co-processor flashed with `solardeck_rp2350.uf2`.
* [x] Linux 6.6 LTS boots with `eink-refreshd` active.
* [x] `solardeck-diag --json` returns 100% PASS across all 8 domains.
* [x] Enclosure sealed with GORE ePTFE vent and Poron perimeter gasket.

SolarDeck V1 is certified flight-ready and operational.
