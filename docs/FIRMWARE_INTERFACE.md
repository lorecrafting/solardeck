# FIRMWARE_INTERFACE.md — CM5 ↔ RP2350 Contract

Written 2026-10-20 12:40 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Audit 3 found the two halves of the product had no interface definition, so neither could be built or
tested against the other. This is that definition.

**The contract is the header, not this page:** `firmware/rp2350/include/solardeck_regs.h`.
CI Phase 15 fails if a register in the header is missing here, or if this page names a register that
does not exist in the header. Prose cannot drift from code in either direction.

## 1. Transport

| Property | Value | Why |
| :--- | :--- | :--- |
| Bus | SPI, **CM5 is master**, RP2350 is slave | The CM5 sleeps; it must be the side that initiates |
| Frame | **64 bytes fixed**, little-endian, fixed offsets | No variable-length parsing on a device that wakes in 30 ms |
| Integrity | **CRC-16/CCITT-FALSE** over bytes `0x00..0x3D`, stored at `0x3E` | A single bit flip must not become a state change |
| Identity | `magic0='S'`, `magic1='D'`, `proto=1` | A driver that reads the wrong magic refuses to bind |
| Cadence | CM5 polls at 10 Hz awake, 1 Hz in S2idle | `heartbeat_ms` catches a wedged RP2350 |

`sd_frame_valid()` in the header is the only validator either side should call. It checks magic,
protocol version, and CRC, in that order.

## 2. Register map

| Offset | Name | Dir | Type | Meaning |
| :--- | :--- | :--- | :--- | :--- |
| `0x00` | `REG_ID_MAGIC0` | RO | u8 | `'S'` |
| `0x01` | `REG_ID_MAGIC1` | RO | u8 | `'D'` |
| `0x02` | `REG_ID_PROTO` | RO | u8 | protocol version, currently 1 |
| `0x03` | `REG_ID_FW_MAJOR` | RO | u8 | firmware major |
| `0x04` | `REG_ID_FW_MINOR` | RO | u8 | firmware minor |
| `0x05` | `REG_STATE` | RO | u8 | `SD_STATE_*` |
| `0x06` | `REG_FLAGS` | RO | u8 | `SD_FLAG_*` bitfield |
| `0x08` | `REG_VBAT_MV` | RO | u16 | battery voltage |
| `0x0A` | `REG_VSOLAR_MV` | RO | u16 | solar open-circuit voltage |
| `0x0C` | `REG_SOC_PCT` | RO | u8 | state of charge, from BQ27441 |
| `0x0D` | `REG_TEMP_C` | RO | i8 | battery thermistor |
| `0x0E` | `REG_WAKE_CAUSE` | RO | u8 | `SD_WAKE_*`, valid after a wake |
| `0x0F` | `REG_SEQ` | RO | u8 | increments on every accepted state change |
| `0x10` | `REG_LAST_WAKE_US` | RO | u32 | last measured wake latency — the `<400 ms` pillar's number |
| `0x14` | `REG_CMD` | WO | u8 | `SD_CMD_*` |
| `0x15` | `REG_CMD_ARG` | WO | u8 | command argument |
| `0x16` | `REG_CMD_ACK` | RO | u8 | `SD_ACK_IDLE/APPLIED/REJECTED` |
| `0x18` | `REG_EVENTS` | RO/W1C | u16 | `SD_EVENT_*`, write 1 to clear |
| `0x1A` | `REG_LORA_RX_LEN` | RO | u8 | bytes queued in the LoRa RX ring |
| `0x1B` | `REG_LORA_RX_HEAD` | RO | u8 | ring head index |
| `0x1C` | `REG_EPDC_OWNER` | RO | u8 | `SD_OWNER_CM5` or `SD_OWNER_RP2350` |
| `0x1E` | `REG_HEARTBEAT_MS` | RO | u16 | ms since the RP2350 last serviced the bus |
| `0x3E` | `REG_CRC16` | RO | u16 | frame checksum |

## 2b. Enumerations

| State | Value | Meaning |
| :--- | ---: | :--- |
| `SD_STATE_COLD_BOOT` | 0 | RP2350 up, CM5 not yet talking |
| `SD_STATE_CM5_ACTIVE` | 1 | CM5 owns the EPDC bus |
| `SD_STATE_ZEN_READER` | 2 | RP2350 drives the panel, CM5 off |
| `SD_STATE_S2IDLE` | 3 | CM5 suspended, RP2350 listening |
| `SD_STATE_LOW_BATT` | 4 | below cutoff, shedding loads |

| Command | Value | Meaning |
| :--- | ---: | :--- |
| `SD_CMD_NOP` | 0 | no operation |
| `SD_CMD_SLEEP_CM5` | 1 | RP2350 takes the EPDC bus, CM5 may power down |
| `SD_CMD_WAKE_CM5` | 2 | assert GPIO17, expect S2idle exit |
| `SD_CMD_RELEASE_EPDC` | 3 | hand the bus back to the CM5 |
| `SD_CMD_PWRFAIL_ACK` | 4 | CM5 finished its 150 ms flush |
| `SD_CMD_BLACKOUT` | 5 | cut mics + RF + camera (hardware already latched) |

| Ack | Value | Meaning |
| :--- | ---: | :--- |
| `SD_ACK_IDLE` | 0 | no command pending |
| `SD_ACK_APPLIED` | 1 | command accepted and applied |
| `SD_ACK_REJECTED` | 2 | illegal transition, `REG_SEQ` unchanged |

| Event | Bit | Meaning |
| :--- | ---: | :--- |
| `SD_EVENT_WAKE_REQ` | 0 | CM5 should resume |
| `SD_EVENT_PWRFAIL` | 1 | power failing, flush now |
| `SD_EVENT_BUTTON` | 2 | user button |
| `SD_EVENT_LORA_RX` | 3 | packet queued in the ring |
| `SD_EVENT_TAMPER` | 4 | enclosure opened |

| Flag | Bit | Meaning |
| :--- | ---: | :--- |
| `SD_FLAG_CM5_SELECTED` | 0 | TMUX is on the CM5 side |
| `SD_FLAG_5V_ENABLED` | 1 | TPS61088 boost on |
| `SD_FLAG_PWRFAIL` | 2 | powerfail pin asserted |
| `SD_FLAG_LIFEPO4` | 3 | chemistry strap reads LiFePO4 |
| `SD_FLAG_LOW_BATT` | 4 | below cutoff threshold |
| `SD_FLAG_CHARGING` | 5 | charger active |

| Wake cause | Value | Meaning |
| :--- | ---: | :--- |
| `SD_WAKE_NONE` | 0 | not a wake event |
| `SD_WAKE_BUTTON` | 1 | user button |
| `SD_WAKE_LORA` | 2 | mesh packet addressed to us |
| `SD_WAKE_RTC` | 3 | scheduled alarm |
| `SD_WAKE_PEN` | 4 | stylus pickup |
| `SD_WAKE_PWRFAIL` | 5 | power fail |

| Owner | Value | Meaning |
| :--- | ---: | :--- |
| `SD_OWNER_CM5` | 0 | CM5 drives the EPDC |
| `SD_OWNER_RP2350` | 1 | RP2350 drives the EPDC |

## 3. The three rules that prevent the classic bugs

1. **`REG_EPDC_OWNER` must agree with the TMUX select pin.** The pin is the authority; the register is
   the report. Firmware asserts the pin, then writes the register — never the reverse. If they disagree,
   the CM5 must stop driving the bus and re-read, because two drivers on one bus is how a panel dies.
2. **A command is applied only when `REG_CMD_ACK` becomes `SD_ACK_APPLIED`.** `SD_ACK_REJECTED` means
   an illegal transition (e.g. `SD_CMD_SLEEP_CM5` while `REG_EPDC_OWNER` is already `SD_OWNER_RP2350`);
   `REG_SEQ` is then unchanged, so the CM5 can detect "nothing happened" without a timeout.
3. **Events are write-1-to-clear and are latched.** `SD_EVENT_PWRFAIL` must survive a slow CM5 poll —
   the CM5 has 150 ms to flush, so a missed latch is data loss.

## 4. Sequence: waking from S2idle

```
RP2350 (event)                       CM5 (S2idle)
  button/lora/rtc interrupt
  latch SD_EVENT_WAKE_REQ
  assert PIN_GPIO17_WAKE ──────────►  GPIO interrupt, kernel resumes
                                      read frame, see WAKE_REQ
                                      write REG_EVENTS = WAKE_REQ (clear)
  deassert GPIO17   ◄──────────────── 
  REG_LAST_WAKE_US = measured  ─────►  daemon logs it; >400 ms is a regression
```

`REG_LAST_WAKE_US` is the measurement the dual-brain pillar is judged on. Without this register the
`<400 ms` claim had no mechanism to be true or false — which is exactly what audit 1 found.

## 5. What the CM5 side must not do

- Do not poll faster than 10 Hz while awake; the RP2350 services the EPDC bus from the same core.
- Do not read the frame while `REG_EPDC_OWNER == SD_OWNER_RP2350` **and** the TMUX pin says RP2350 —
  the SPI lines are isolated, so the read returns garbage rather than an error.
- Do not assume `REG_VBAT_MV` is fresh: it is sampled at 1 Hz in sleep. Treat it as a slow signal.

## 6. Deliberately not in the contract (yet)

No DFU/update path, no logging channel, no LoRa payload transfer beyond the ring head/length pair.
Each is a real need, none is needed to make the first bring-up testable, and every one of them adds a
protocol version bump. Add them behind `proto = 2` when a second firmware binary has to be flashed in
the field.

→ skipped: generating this table from the header. A generator would be one more thing to keep working;
Phase 15's bidirectional name check gets the same guarantee in 20 lines and leaves the prose readable.
