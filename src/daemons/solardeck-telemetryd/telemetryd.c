/* SPDX-License-Identifier: MIT
 * SolarDeck Telemetry Daemon Implementation (telemetryd.c)
 * Written 2026-10-19 UTC in the Pi harness by antigravity/gemini-3.8-flash
 */

#include "telemetryd.h"
#include <stdio.h>
#include <string.h>

/* Dallas/Maxim CRC-8 (polynomial 0x31: x^8 + x^5 + x^4 + 1) */
uint8_t telemetry_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

bool telemetry_parse_frame(const uint8_t *buf, size_t len, telemetry_frame_t *out_frame) {
    if (!buf || !out_frame || len < sizeof(telemetry_frame_t)) {
        return false;
    }

    const telemetry_frame_t *f = (const telemetry_frame_t *)buf;

    /* Verify Magic */
    if (f->magic != TELEMETRY_FRAME_MAGIC) {
        return false;
    }

    /* Verify CRC-8 over entire frame except the last byte (crc8 itself) */
    size_t payload_len = sizeof(telemetry_frame_t) - 1;
    uint8_t calc_crc = telemetry_crc8(buf, payload_len);
    if (calc_crc != f->crc8) {
        return false;
    }

    /* Plausibility check for LiFePO4 battery voltage (2.0V to 4.0V) */
    if (f->vbat_mv < 2000 || f->vbat_mv > 4200) {
        return false;
    }

    memcpy(out_frame, f, sizeof(telemetry_frame_t));
    return true;
}

int telemetry_format_json(const telemetry_frame_t *frame, char *out_json, size_t max_len) {
    if (!frame || !out_json || max_len == 0) {
        return -1;
    }

    float vbat_v = (float)frame->vbat_mv / 1000.0f;
    float temp_c = (float)frame->temp_c_x10 / 10.0f;
    uint16_t total_pwr_mw = frame->pwr_compute_mw + frame->pwr_display_mw + frame->pwr_rf_mw;

    return snprintf(out_json, max_len,
        "{\n"
        "  \"vbat_v\": %.3f,\n"
        "  \"ibat_ma\": %d,\n"
        "  \"soc_pct\": %u,\n"
        "  \"solar_lux\": %u,\n"
        "  \"temp_c\": %.1f,\n"
        "  \"power\": {\n"
        "    \"compute_mw\": %u,\n"
        "    \"display_mw\": %u,\n"
        "    \"rf_mw\": %u,\n"
        "    \"total_mw\": %u\n"
        "  },\n"
        "  \"airgap_active\": %s\n"
        "}\n",
        vbat_v,
        frame->ibat_ma,
        frame->soc_pct,
        frame->solar_lux,
        temp_c,
        frame->pwr_compute_mw,
        frame->pwr_display_mw,
        frame->pwr_rf_mw,
        total_pwr_mw,
        frame->airgap_active ? "true" : "false"
    );
}
