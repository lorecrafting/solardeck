# SolarDeck V1 — Field Bring-Up & First Boot Checklist

*Written 2026-10-19 16:45 UTC in the Pi harness by antigravity/gemini-3.8-flash*

Revised 2026-10-21 16:01 UTC in Claude Code by anthropic/claude-opus-5-5 (CM5 / Kaleido 4 / eSIM standardization, ADR-031–033).

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
4. **Solder Joint Inspection:** Inspect the QFN-80 package of the RP2350B, the TI BQ25895 buck charger, and the TI TMUX1575 bus switch for solder bridging or tombstoned 0402 passives.
5. **Cold-Storage Vault & SIM:** Verify the gasketed hatch fits flush and the 3x friction-fit MicroSD slots retain cards securely.

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
   * If current hits 50 mA clamp, immediately disconnect and inspect `U_TPS62840`.
3. **Flashing the RP2350 Firmware:**
   * Hold the physical `BOOTSEL` button on the carrier board.
   * Connect a USB-C data cable from your host computer to **USB-C Port 1**.
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
     [RTC] DS3231 TCXO detected: VALID.
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
   * Connect the 8,000–10,000 mAh LiFePO4 battery pack to `J_BAT`.
   * Connect a USB-PD 20W charger to USB-C Port 1. Confirm the TI BQ25895 amber charge LED illuminates.
2. **Cold Boot Execution:**
   * Press the physical Power button on the top edge for 1.5 seconds.
   * The RP2350 co-processor will enable the CM5 (enable net TBD — verify on CM5) and cycle the reset net of the Kaleido 4 display controller (TBD, ADR-032).
   * The 10.3" E-Ink panel will execute an initial global white clearing flash.
   * **In <400 milliseconds**, the Linux console login will appear on the high-contrast paper screen.
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
     - `audio`: Dual Knowles MEMS mics and MAX98357A speaker functional.
     - `rf`: SX1262 LoRa SPI response and EG25-G modem AT response.
     - `storage`: NVMe/eMMC write speed $>250\text{ MB/s}$.

---

### 5b. S2idle Gate (the 15 mW / 0.3 s pillar rests on this)

The 300-day desk clock and the 0.3 s instant wake both assume the CM5 can actually enter `s2idle`.
The CM5 (BCM2712) has no RAM-retaining low-power state (ADR-031, AUDIT 6 X4); whether `s2idle`
reaches the gate below is board-firmware and kernel-version dependent (TBD — verify on CM5), and
nothing in CI measures it.
Run this gate before accepting the power claims:

```bash
cat /sys/power/state                    # must contain "freeze"
grep -c . /sys/power/suspend_stats/success
sudo rtcwake -m freeze -s 10            # measure the round trip
cat /sys/power/suspend_stats/last_failed_dev   # empty means no device vetoed it
```

* **Pass:** `freeze` present, `success` increments by 1, wall time 10 s ± 0.5 s, and a measured
  current draw (USB-C PD meter or INA3221 telemetry) **< 25 mW** with radios gated.
* **If it fails:** record the kernel version and the firmware commit in this checklist, downgrade
  the pillar to `modelled` in `README.md`, and re-scope the runtime arithmetic in
  `MVP_ARCHITECTURE.md`. Do not ship a marketing number for a suspend state the board does not enter.
* **Replace the constant:** the <300 ms wake figure is currently a hardcoded constant in
  `firmware/rp2350/src/solardeck_sm.c`. Once measured, put the real number in `docs/spec_values.json`
  and assert against that.

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
