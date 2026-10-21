# Pin Budget — CM5 and RP2350B, V1 with V2 reservations

Written 2026-10-21 17:20 UTC in Claude Code by anthropic/claude-opus-5-5 (ADR-044, ADR-045).
Revised 2026-10-21 17:26 UTC in Claude Code by anthropic/claude-opus-5-5 (checked against the V1 BOM; always-on GPIO expander).
Revised 2026-10-21 17:52 UTC in Claude Code by anthropic/claude-opus-5-5 (owner decisions, ADR-046).

Every signal on both processors is assigned before schematic capture, so V1 can be drawn once and V2
fits without a re-spin of the pinout (ADR-045). **The data is `spec_values.pins`; this page is the
readable copy.** Phase 15 (`scripts/check_firmware_interface.py`) fails if:

- a table row here differs from the spec in net, function, scope or isolation;
- two PWM outputs share an RP2350 PWM slice (one counter and divider per slice);

- a pin uses a function its datasheet mux does not offer there (RP2350 datasheet Table 3; CM5
  datasheet GPIO table). A CM5 function outside the table already verified counts as a failure;
- a net is assigned to two pins, or a pin appears twice (the RP2350 and its expander share one net list);
- a net from the always-on RP2350 into the CM5 domain has no hardware isolation rule (below), or the
  buffered lines exceed `pins.buffer_channels`;
- the TMUX lines on the two sides do not pair within `pins.tmux_channels`;
- a `PIN_*` define in `firmware/rp2350/include/solardeck_state.h` disagrees with the budget;

Green means the budget is internally consistent. It does not mean the schematic matches it; there is
no wired schematic yet (AUDIT 6 X8).

## 1. Rules

1. **No back-powering, in hardware.** The RP2350 is always on; the CM5 is often unpowered. A net that
   crosses into the CM5 domain needs one of these isolation rules:
   - `tmux`: the line goes through the TMUX1575 pair (I_off protected).
   - `buffer`: the RP2350 drives it through one of the two TXU0104 I_off buffers (BOM "I/O Isolators",
     `pins.buffer_channels`), which go high-impedance when the CM5 rail is at 0 V (HARDWARE_SPEC §2.13). The same buffers protect the UART into the switched-off GNSS.
   - `rp_input`: the RP2350 only receives on it.
   - `od`: open-drain, with the pull-up on the CM5 rail.

   Firmware tri-stating is not an isolation rule: a hang, a debugger halt or a brown-out restart leaves
   pins driven. Firmware still keeps these lines idle while the CM5 is off (defence in depth); for
   `LINK_MISO` an unpowered CM5 leaves `LINK_CS` at 0 V, which selects an active-low SPI target.
2. **V2 parts are DNP, never absent.** Every V2 row gets its footprint, pull resistors and test pad on
   the V1 board, unpopulated. High-speed V2 lanes run to their footprint and stop: no stubs, no branches.
3. **Shared buses are one net with several users.** The RP-side SPI0 bus (GPIO 4, 6, 7) serves the
   display through the TMUX and, in V2, the SX1262 with its own chip select. It is listed once.
4. **CM5 GPIO_VREF is tied to 3.3 V.** Every CM5 GPIO peripheral here is 3.3 V. Total GPIO current
   stays within the CM5 datasheet's bank limit.

## 2. CM5 high-speed interfaces and control pins

| Interface | V1 | V2 reservation |
| :--- | :--- | :--- |
| USB 3.0 port 0 | USB-C port 2 (host, `usb.port2_role`), SuperSpeed lanes plus their USB 2.0 pair | — |
| USB 3.0 port 1 | not routed in V1 | M.2 Key-B LTE modem (DNP socket), plus nano-SIM and MFF2 eSIM footprints |
| USB 2.0 port (OTG) | USB-C port 1 (DRP, `usb.port1_role`). This port also carries `nRPI_BOOT` USB boot, so the CM5 can be re-flashed from port 1 | — |
| PCIe Gen 2 x1 | M.2 NVMe socket (ADR-042) | — |
| MIPI 0 | not used (the panel is SPI) | — |
| MIPI 1 | not routed in V1 | CSI camera connector (DNP) and lens boss |
| `PWR_BUT` | from RP2350 GPIO 12 (`CM5_PWR_BUT`, open-drain) and the power button path | — |
| `nRPI_BOOT` | recovery pinhole (`usb.recovery_doors`) | — |
| `WL_nDisable`, `BT_nDisable` | pulled low by the airgap switch (they can only be driven low) | — |
| `USB_OTG_ID` | driven by the port 1 CC controller's data role | — |
| `GPIO_VREF` | 3.3 V | — |

The RP2350's own USB pins go to the recovery header (`uart_swd_header`) with SWD. The RP2350 has no
field update path yet (FIRMWARE_INTERFACE §6).

## 3. RP2350B (48 GPIO)

| GPIO | Net | Function | Scope | Isolation | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| RP2350 0 | `PSRAM_CS` | qmi_cs1 | V1 |  | 8 MB PSRAM chip select (QMI CS1n exists only on GPIO 0/8/19/47); the flash uses the dedicated QSPI pins |
| RP2350 1 | `LORA_NSS` | sio | V2 |  | SX1262 chip select on the shared RP-side SPI0 bus |
| RP2350 2 | `EPDC_HRDY_RP` | sio | V1 | tmux | display controller ready, RP2350 side of the TMUX |
| RP2350 3 | `EPDC_RST_RP` | sio | V1 | tmux | display controller reset, RP2350 side |
| RP2350 4 | `RP_SPI0_RX` | spi0_rx | V1 | tmux | SPI0 bus, RP2350 side: display (via TMUX) and V2 LoRa |
| RP2350 5 | `EPDC_CS_RP` | spi0_csn | V1 | tmux | display chip select, RP2350 side |
| RP2350 6 | `RP_SPI0_SCK` | spi0_sck | V1 | tmux | SPI0 bus clock (shared, as GPIO 4) |
| RP2350 7 | `RP_SPI0_TX` | spi0_tx | V1 | tmux | SPI0 bus data out (shared, as GPIO 4) |
| RP2350 8 | `LINK_MOSI` | spi1_rx | V1 | rp_input | CM5↔RP2350 link, RP2350 is SPI target (FIRMWARE_INTERFACE §1) |
| RP2350 9 | `LINK_CS` | spi1_csn | V1 | rp_input | link chip select from the CM5 |
| RP2350 10 | `LINK_SCK` | spi1_sck | V1 | rp_input | link clock from the CM5 |
| RP2350 11 | `LINK_MISO` | spi1_tx | V1 | buffer | link data to the CM5, through a TXU0104 |
| RP2350 12 | `CM5_PWR_BUT` | sio | V1 | od | open-drain into CM5 PWR_BUT: request a clean shutdown |
| RP2350 13 | `TMUX_SEL` | sio | V1 |  | TMUX select: high = CM5 drives the display |
| RP2350 14 | `EN_5V_SYS` | sio | V1 |  | enables the CM5 5 V supply |
| RP2350 15 | `WAKE_GPIO17` | sio | V1 | buffer | interrupt to CM5 GPIO17, through a TXU0104 |
| RP2350 16 | `PWRFAIL_GPIO16` | sio | V1 | buffer | power-fail warning to CM5 GPIO16, through a TXU0104 |
| RP2350 17 | `CHG_CE_N` | sio | V1 |  | BQ25798 CE, active-low, hardware pull-up keeps charging off (ADR-035); direct, never via the expander |
| RP2350 18 | `EXP_INT_N` | sio | V1 |  | always-on GPIO expander interrupt; wakes the RP2350 |
| RP2350 19 | `FRONTLIGHT_CTRL` | sio | V1 |  | TPS61163 frontlight EasyScale/enable (timed one-wire, so direct) |
| RP2350 20 | `GNSS_UART_TX` | uart1_tx | V1 | buffer | to MAX-M10S RXD (UART1), through a TXU0104 (GNSS rail may be off) |
| RP2350 21 | `GNSS_UART_RX` | uart1_rx | V1 |  | from MAX-M10S TXD (UART1) |
| RP2350 22 | `LORA_BUSY` | sio | V2 |  | SX1262 busy |
| RP2350 23 | `GNSS_PPS` | sio | V1 |  | GNSS time pulse, disciplines the RTC |
| RP2350 24 | `I2C_AON_SDA` | i2c0_sda | V1 |  | always-on I²C: charger, gauge, expander, RTC, sensors, CC controller |
| RP2350 25 | `I2C_AON_SCL` | i2c0_scl | V1 |  | always-on I²C clock |
| RP2350 26 | `MIC_BCLK` | pio | V1 |  | PIO I²S clock to both SPH0645 mics |
| RP2350 27 | `MIC_WS` | pio | V1 |  | PIO I²S word select (L/R mic) |
| RP2350 28 | `MIC_SD` | pio | V1 |  | PIO I²S data from both mics |
| RP2350 29 | `AUD_LINK_BCLK` | pio | V1 | buffer | PIO I²S clock to the CM5 (audio link; RP2350 is clock master), through a TXU0104 |
| RP2350 30 | `AUD_LINK_WS` | pio | V1 | buffer | audio link word select |
| RP2350 31 | `AUD_LINK_SD` | pio | V1 | buffer | audio link mic data to the CM5 |
| RP2350 32 | `VOICE_BTN` | sio | V1 |  | hold-to-talk voice button (ADR-036) |
| RP2350 33 | `PWR_BTN` | sio | V1 |  | power button |
| RP2350 34 | `ROCKER_UP` | sio | V1 |  | 5-way rocker: reader page turns with Linux off |
| RP2350 35 | `ROCKER_DOWN` | sio | V1 |  | 5-way rocker |
| RP2350 36 | `ROCKER_LEFT` | sio | V1 |  | 5-way rocker |
| RP2350 37 | `ROCKER_RIGHT` | sio | V1 |  | 5-way rocker |
| RP2350 38 | `ROCKER_PRESS` | sio | V1 |  | 5-way rocker centre press |
| RP2350 39 | `LORA_DIO1` | sio | V2 |  | SX1262 IRQ (DIO1); wakes the RP2350 |
| RP2350 40 | `SOLAR_ADC` | adc | V1 |  | solar strip voltage (ADC0) |
| RP2350 41 | `LED_R` | pwm | V1 |  | notification LED, PWM (slice 8) |
| RP2350 42 | `LED_G` | pwm | V1 |  | notification LED, PWM (slice 9) |
| RP2350 43 | `LUX_ADC` | adc | V1 |  | ambient light (ADC3, the BOM's "ADC Channel 3" lux row) |
| RP2350 44 | `LED_B` | pwm | V1 |  | notification LED, PWM (slice 10) |
| RP2350 45 | `LORA_RXEN` | sio | V2 |  | module RF switch, receive (E22 class) |
| RP2350 46 | `PIEZO` | pwm | V1 |  | standby alert piezo, PWM (slice 11, alone) |
| RP2350 47 | `LORA_TXEN` | sio | V2 |  | module RF switch, transmit |

## 4. Always-on GPIO expander (I²C, on the RP2350's bus)

Slow, interrupt-only and enable lines live here so the RP2350's own pins stay free for buses, PWM,
ADC and anything that must wake it directly. Part TBD (a 16-bit, low-quiescent I²C expander with an
interrupt output); it is a TBD row in the BOM. Its outputs come up as inputs, so every enable line has a
pull resistor that holds the load off until firmware drives it.

| GPIO | Net | Function | Scope | Isolation | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EXP 0 | `GNSS_EN` | gpio | V1 |  | GNSS load switch |
| EXP 1 | `PORT2_VBUS_EN` | gpio | V1 |  | USB-C port 2 VBUS load switch |
| EXP 2 | `AIRGAP_SENSE` | gpio | V1 |  | airgap switch position (the cut itself is hardware) |
| EXP 3 | `CHG_INT_N` | gpio | V1 |  | charger interrupt |
| EXP 4 | `GAUGE_INT` | gpio | V1 |  | BQ27Z561-R2 alert |
| EXP 5 | `IMU_INT` | gpio | V1 |  | BMA400 motion interrupt (wake on pick-up) |
| EXP 6 | `CC_INT_N` | gpio | V1 |  | TUSB320 port 1 CC interrupt |
| EXP 8 | `SENSOR_ALERT_N` | gpio | V1 |  | wired-OR TMP112 / INA3221 alerts |
| EXP 9 | `LORA_NRESET` | gpio | V2 |  | SX1262 reset |
| EXP 10 | `LORA_PWR_EN` | gpio | V2 |  | LoRa load switch |
| EXP 11 | `LTE_PWR_EN` | gpio | V2 |  | modem load switch |
| EXP 12 | `LTE_RESET_N` | gpio | V2 |  | M.2 RESET# |
| EXP 13 | `LTE_W_DISABLE_N` | gpio | V2 |  | M.2 W_DISABLE1#; airgap also forces it in hardware |

## 5. CM5 (28 GPIO)

| GPIO | Net | Function | Scope | Isolation | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| CM5 0 | `ID_SD` | id_sd | RESERVED |  | HAT EEPROM ID pins; free with force_eeprom_read=0, kept as spares |
| CM5 1 | `ID_SC` | id_sc | RESERVED |  |  |
| CM5 2 | `I2C_HOST_SDA` | i2c1_sda | V1 |  | host I²C: touch, Wacom, DRV2605L, V2 NFC (1.8 kΩ pull-ups on module) |
| CM5 3 | `I2C_HOST_SCL` | i2c1_scl | V1 |  |  |
| CM5 4 | `LINK_CS` | spi3_csn0 | V1 |  | CM5↔RP2350 link (SPI3 master) |
| CM5 5 | `LINK_MISO` | spi3_miso | V1 |  |  |
| CM5 6 | `LINK_MOSI` | spi3_mosi | V1 |  |  |
| CM5 7 | `LINK_SCK` | spi3_sclk | V1 |  |  |
| CM5 8 | `EPDC_CS_CM5` | spi0_ce0 | V1 | tmux | display SPI0, CM5 side of the TMUX |
| CM5 9 | `EPDC_MISO_CM5` | spi0_miso | V1 | tmux |  |
| CM5 10 | `EPDC_MOSI_CM5` | spi0_mosi | V1 | tmux |  |
| CM5 11 | `EPDC_SCK_CM5` | spi0_sclk | V1 | tmux |  |
| CM5 12 | `EPDC_HRDY_CM5` | gpio | V1 | tmux | display ready, CM5 side |
| CM5 13 | `EPDC_RST_CM5` | gpio | V1 | tmux | display reset, CM5 side |
| CM5 14 | `DEBUG_UART_TX` | uart0_tx | V1 |  | debug console header |
| CM5 15 | `DEBUG_UART_RX` | uart0_rx | V1 |  |  |
| CM5 16 | `PWRFAIL_GPIO16` | gpio | V1 |  | power-fail warning from the RP2350 |
| CM5 17 | `WAKE_GPIO17` | gpio | V1 |  | interrupt from the RP2350 |
| CM5 18 | `AUD_LINK_BCLK` | i2s1_sclk | V1 |  | I2S1, the CM5's clock-target I²S, clocked by the RP2350 (I2S0 is master-only) |
| CM5 19 | `AUD_LINK_WS` | i2s1_ws | V1 |  |  |
| CM5 20 | `AUD_LINK_SD` | i2s1_sdi | V1 |  | mic audio from the RP2350 |
| CM5 21 | `SPK_SDO` | i2s1_sdo | V1 |  | audio out to the MAX98357A speaker amp, on the link clocks |
| CM5 22 | `TOUCH_INT` | gpio | V1 |  | capacitive touch interrupt |
| CM5 23 | `TOUCH_RST` | gpio | V1 |  | touch reset |
| CM5 24 | `PEN_INT` | gpio | V1 |  | Wacom EMR interrupt |
| CM5 25 | `PEN_RST` | gpio | V1 |  | Wacom reset |
| CM5 26 | `HAPTIC_TRIG` | gpio | V1 |  | DRV2605L IN/TRIG: key-down haptic without an I²C round trip |
| CM5 27 | `NFC_IRQ` | gpio | V2 |  | NFC controller interrupt |

## 6. What the budget shows

- **V1 does not fit on the RP2350 without the expander.** Checked against every signal-bearing part in
  the V1 BOM (5-way rocker, lux ADC, motion sensor, CC controller, frontlight) and
  the HARDWARE_SPEC notification LED and piezo, V1 needs more lines than the RP2350B has. With the
  expander V1 fits, and V2 LoRa and the LTE modem's control take the rest: the RP2350's own pins are
  then full and the expander has a few lines spare (the Scope column is the count).
- **The CM5 is full in V1.** All 28 GPIO are assigned; GPIO 0/1 are the only spares. The audio link is
  what makes this fit: the RP2350 owns the microphones and is the audio clock master, so the speaker
  amp and the mic stream share the CM5's I2S1, its clock-target I²S (I2S0 is master-only).
- **The TMUX carries the display lines only:** SPI clock, data in, data out, chip select, ready and
  reset, within `pins.tmux_channels`.
- **USB decides the V2 modem's port.** The modem needs a USB 2.0 pair; USB 3.0 port 1 is the only one
  left once port 1 (OTG, re-flash) and port 2 (host) are assigned. This is why the mic stream uses I²S
  rather than USB audio (owner decision, ADR-046).

## 7. Assumptions to check at capture

- The Kaleido 4 controller interface is assumed SPI plus ready and reset, like the IT8951. The real
  controller reference (ADR-032, under NDA) may need different lines.
- The SX1262 module's `RXEN`/`TXEN` assume an Ebyte E22-class module. A bare SX1262 uses DIO2 for the
  RF switch and frees GPIO 45 and 47.
- SPI3 on CM5 GPIO 4–7 needs its device-tree overlay confirmed on the CM5 at bring-up.
- GNSS PPS on GPIO 23 assumes the MAX-M10S `TIMEPULSE` output is used.

Resolved by ADR-046: timekeeping is an I²C RTC chip on the always-on bus (no clock-input pin needed);
the headphone jack and DAC are out of V1; the quad piezo array stays off the board; the RP2350B's
firmware flash sits on its dedicated QSPI pins.
