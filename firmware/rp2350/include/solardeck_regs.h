/**
 * Written 2026-10-20 12:30 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
 *
 * SolarDeck CM5 <-> RP2350 interface register map. THIS FILE IS THE CONTRACT.
 *
 * Audit 3 found that firmware/ and the Linux daemons had no interface definition, so neither side
 * could be built or tested against the other. This header is the single source of truth: the offsets
 * below are the wire format, and `scripts/check_firmware_interface.py` (CI Phase 15) fails if
 * docs/FIRMWARE_INTERFACE.md drifts from these names.
 *
 * Transport: CM5 is SPI master, RP2350 is SPI slave. One transfer = one 64-byte frame, little-endian,
 * fixed offsets, no variable-length fields. The frame is idempotent to read; writes are commands only.
 *
 * The struct at the bottom is the same bytes as the register map, so firmware can memcpy it and the
 * _Static_asserts below make an accidental reorder a compile error rather than a silent protocol break.
 */

#ifndef SOLARDECK_REGS_H
#define SOLARDECK_REGS_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---- Protocol identity ---------------------------------------------------------------- */
#define SD_PROTO_VERSION      1
#define SD_FRAME_BYTES        64
#define SD_MAGIC0             'S'
#define SD_MAGIC1             'D'

/* ---- Register offsets (bytes from frame start) --------------------------------------- */
/* Identity, read-only. A CM5 driver that reads the wrong magic must refuse to bind. */
#define REG_ID_MAGIC0         0x00  /* 'S' */
#define REG_ID_MAGIC1         0x01  /* 'D' */
#define REG_ID_PROTO          0x02  /* SD_PROTO_VERSION */
#define REG_ID_FW_MAJOR       0x03
#define REG_ID_FW_MINOR       0x04

/* Live state, read-only from the CM5 side. */
#define REG_STATE             0x05  /* solardeck_state_t */
#define REG_FLAGS             0x06  /* SD_FLAG_* bitfield */
#define REG_VBAT_MV           0x08  /* uint16, battery voltage */
#define REG_VSOLAR_MV         0x0A  /* uint16, solar open-circuit voltage */
#define REG_SOC_PCT           0x0C  /* uint8, 0-100, from BQ27441 */
#define REG_TEMP_C            0x0D  /* int8, battery thermistor */
#define REG_WAKE_CAUSE        0x0E  /* SD_WAKE_* */
#define REG_SEQ               0x0F  /* uint8, increments every state change */

/* Latency measurement: the number the <400 ms glass-to-glass pillar is judged on. */
#define REG_LAST_WAKE_US      0x10  /* uint32 */

/* Command window, write-only from the CM5 side, read back as the last accepted command. */
#define REG_CMD               0x14  /* SD_CMD_* */
#define REG_CMD_ARG           0x15  /* uint8, command-specific */
#define REG_CMD_ACK           0x16  /* SD_ACK_*, RP2350 sets after applying */

/* Events raised by the RP2350, write-1-to-clear by the CM5. */
#define REG_EVENTS            0x18  /* SD_EVENT_* bitfield */
#define REG_LORA_RX_LEN       0x1A  /* reserved for V2 LoRa (ADR-044); reads 0 in V1 */
#define REG_LORA_RX_HEAD      0x1B  /* reserved for V2 LoRa (ADR-044); reads 0 in V1 */

/* Ownership of the EPDC bus. Must agree with the TMUX select pin, never instead of it. */
#define REG_EPDC_OWNER        0x1C  /* SD_OWNER_* */
#define REG_HEARTBEAT_MS      0x1E  /* uint16, ms since RP2350 last serviced the bus */

/* Frame integrity. CRC-16/CCITT-FALSE over bytes 0x00..0x3E. */
#define REG_CRC16             0x3E

/* ---- Enumerations -------------------------------------------------------------------- */
#define SD_STATE_COLD_BOOT    0
#define SD_STATE_CM5_ACTIVE   1
#define SD_STATE_ZEN_READER   2
#define SD_STATE_S2IDLE       3
#define SD_STATE_LOW_BATT     4

#define SD_FLAG_CM5_SELECTED  (1u << 0)
#define SD_FLAG_5V_ENABLED    (1u << 1)
#define SD_FLAG_PWRFAIL       (1u << 2)
#define SD_FLAG_LIFEPO4       (1u << 3)
#define SD_FLAG_LOW_BATT      (1u << 4)
#define SD_FLAG_CHARGING      (1u << 5)

#define SD_WAKE_NONE          0
#define SD_WAKE_BUTTON        1
#define SD_WAKE_LORA          2   /* reserved for V2 LoRa (ADR-044) */
#define SD_WAKE_RTC           3
#define SD_WAKE_PEN           4
#define SD_WAKE_PWRFAIL       5

#define SD_CMD_NOP            0
#define SD_CMD_SLEEP_CM5      1   /* RP2350 takes the EPDC bus, CM5 may power down */
#define SD_CMD_WAKE_CM5       2   /* assert GPIO17, expect S2idle exit */
#define SD_CMD_RELEASE_EPDC   3   /* hand the bus back to the CM5 */
#define SD_CMD_PWRFAIL_ACK    4   /* CM5 finished its <150 ms flush */
#define SD_CMD_BLACKOUT       5   /* cut mics + RF + camera, hardware already latched */

#define SD_ACK_IDLE           0
#define SD_ACK_APPLIED        1
#define SD_ACK_REJECTED       2   /* illegal transition; REG_SEQ unchanged */

#define SD_EVENT_WAKE_REQ     (1u << 0)
#define SD_EVENT_PWRFAIL      (1u << 1)
#define SD_EVENT_BUTTON       (1u << 2)
#define SD_EVENT_LORA_RX      (1u << 3)  /* reserved for V2 LoRa (ADR-044) */
#define SD_EVENT_TAMPER       (1u << 4)

#define SD_OWNER_CM5          0
#define SD_OWNER_RP2350       1

/* ---- Wire layout --------------------------------------------------------------------- */
/* Packed so the offsets above are the ABI. Never insert a field; append and bump SD_PROTO_VERSION. */
typedef struct __attribute__((packed)) {
    uint8_t  magic0;        /* 0x00 */
    uint8_t  magic1;        /* 0x01 */
    uint8_t  proto;         /* 0x02 */
    uint8_t  fw_major;      /* 0x03 */
    uint8_t  fw_minor;      /* 0x04 */
    uint8_t  state;         /* 0x05 */
    uint8_t  flags;         /* 0x06 */
    uint8_t  _reserved07;   /* 0x07 */
    uint16_t vbat_mv;       /* 0x08 */
    uint16_t vsolar_mv;     /* 0x0A */
    uint8_t  soc_pct;       /* 0x0C */
    int8_t   temp_c;        /* 0x0D */
    uint8_t  wake_cause;    /* 0x0E */
    uint8_t  seq;           /* 0x0F */
    uint32_t last_wake_us;  /* 0x10 */
    uint8_t  cmd;           /* 0x14 */
    uint8_t  cmd_arg;       /* 0x15 */
    uint8_t  cmd_ack;       /* 0x16 */
    uint8_t  _reserved17;   /* 0x17 */
    uint16_t events;        /* 0x18 */
    uint8_t  lora_rx_len;   /* 0x1A */
    uint8_t  lora_rx_head;  /* 0x1B */
    uint8_t  epdc_owner;    /* 0x1C */
    uint8_t  _reserved1d;   /* 0x1D */
    uint16_t heartbeat_ms;  /* 0x1E */
    uint8_t  _reserved[0x3E - 0x20]; /* 0x20..0x3D, zero-filled */
    uint16_t crc16;         /* 0x3E */
} solardeck_frame_t;

_Static_assert(sizeof(solardeck_frame_t) == SD_FRAME_BYTES, "frame must be exactly 64 bytes");
_Static_assert(offsetof(solardeck_frame_t, magic0)       == REG_ID_MAGIC0,    "magic0 offset");
_Static_assert(offsetof(solardeck_frame_t, proto)        == REG_ID_PROTO,     "proto offset");
_Static_assert(offsetof(solardeck_frame_t, state)        == REG_STATE,        "state offset");
_Static_assert(offsetof(solardeck_frame_t, flags)        == REG_FLAGS,        "flags offset");
_Static_assert(offsetof(solardeck_frame_t, vbat_mv)      == REG_VBAT_MV,      "vbat offset");
_Static_assert(offsetof(solardeck_frame_t, soc_pct)      == REG_SOC_PCT,      "soc offset");
_Static_assert(offsetof(solardeck_frame_t, temp_c)       == REG_TEMP_C,       "temp offset");
_Static_assert(offsetof(solardeck_frame_t, last_wake_us) == REG_LAST_WAKE_US, "wake latency offset");
_Static_assert(offsetof(solardeck_frame_t, cmd)          == REG_CMD,          "cmd offset");
_Static_assert(offsetof(solardeck_frame_t, cmd_ack)      == REG_CMD_ACK,      "ack offset");
_Static_assert(offsetof(solardeck_frame_t, events)       == REG_EVENTS,       "events offset");
_Static_assert(offsetof(solardeck_frame_t, epdc_owner)   == REG_EPDC_OWNER,   "owner offset");
_Static_assert(offsetof(solardeck_frame_t, crc16)        == REG_CRC16,        "crc offset");

/* ---- Helpers ------------------------------------------------------------------------- */
static inline uint16_t sd_crc16_ccitt(const uint8_t *buf, size_t len)
{
    uint16_t crc = 0xFFFFu;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)buf[i] << 8;
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x8000u) ? (uint16_t)((crc << 1) ^ 0x1021u) : (uint16_t)(crc << 1);
    }
    return crc;
}

/* True when the frame is from a compatible peer and not corrupted. */
static inline int sd_frame_valid(const solardeck_frame_t *f)
{
    if (f->magic0 != SD_MAGIC0 || f->magic1 != SD_MAGIC1) return 0;
    if (f->proto != SD_PROTO_VERSION) return 0;
    return sd_crc16_ccitt((const uint8_t *)f, REG_CRC16) == f->crc16;
}

#ifdef __cplusplus
}
#endif

#endif /* SOLARDECK_REGS_H */
