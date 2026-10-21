/* SPDX-License-Identifier: MIT
 * SolarDeck Telemetry Daemon Header (telemetryd.h)
 * Written 2026-10-19 UTC in the Pi harness by antigravity/gemini-3.8-flash
 */

#ifndef SOLARDECK_TELEMETRYD_H
#define SOLARDECK_TELEMETRYD_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define TELEMETRY_FRAME_MAGIC 0x5344 /* 'SD' in ASCII */
#define TELEMETRY_JSON_MAX_LEN 1024

/* Structured Telemetry Frame transmitted from RP2350 co-processor */
#pragma pack(push, 1)
typedef struct {
    uint16_t magic;         /* 0x5344 */
    uint16_t vbat_mv;       /* Battery voltage in millivolts (e.g. 3300 = 3.30V) */
    int16_t  ibat_ma;       /* Battery current in mA (+ charging, - discharging) */
    uint8_t  soc_pct;       /* State of charge (0-100%) */
    uint32_t solar_lux;     /* Ambient illuminance from top solar strip ADC (0-120000) */
    int16_t  temp_c_x10;    /* Temperature in 0.1°C (e.g. 265 = 26.5°C) */
    uint16_t pwr_compute_mw;/* Compute rail power in mW (INA3221 CH1) */
    uint16_t pwr_display_mw;/* Display rail power in mW (INA3221 CH2) */
    uint16_t pwr_rf_mw;     /* radio rail power in mW (INA3221 CH3; GNSS in V1) */
    uint8_t  airgap_active; /* 1 if Airgap Stealth Switch is engaged, 0 if normal */
    uint8_t  crc8;          /* CRC-8 over payload */
} telemetry_frame_t;
#pragma pack(pop)

/* Calculate Dallas/Maxim 1-Wire CRC-8 */
uint8_t telemetry_crc8(const uint8_t *data, size_t len);

/* Validate and parse frame */
bool telemetry_parse_frame(const uint8_t *buf, size_t len, telemetry_frame_t *out_frame);

/* Format telemetry frame into human-readable / Waybar-friendly JSON string */
int telemetry_format_json(const telemetry_frame_t *frame, char *out_json, size_t max_len);

#endif /* SOLARDECK_TELEMETRYD_H */
