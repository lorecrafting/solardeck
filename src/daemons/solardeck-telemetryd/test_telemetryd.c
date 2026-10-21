/* SPDX-License-Identifier: MIT
 * SolarDeck Telemetry Daemon Assert Self-Test (test_telemetryd.c)
 * Written 2026-10-19 UTC in the Pi harness by antigravity/gemini-3.8-flash
 */

#include "telemetryd.h"
#include <stdio.h>
#include <string.h>
#include <assert.h>

int main(void) {
    printf("[test_telemetryd] Running SolarDeck Telemetry Daemon unit tests...\n");

    /* 1. Construct simulated valid frame from RP2350 */
    telemetry_frame_t tx_frame;
    memset(&tx_frame, 0, sizeof(tx_frame));
    tx_frame.magic = TELEMETRY_FRAME_MAGIC;
    tx_frame.vbat_mv = 3320;        /* mid-discharge sample */
    tx_frame.ibat_ma = 125;         /* +125mA charging from solar */
    tx_frame.soc_pct = 85;          /* 85% battery remaining */
    tx_frame.solar_lux = 78000;     /* 78,000 lux (bright Hawaiian sun) */
    tx_frame.temp_c_x10 = 265;      /* 26.5°C */
    tx_frame.pwr_compute_mw = 1200; /* 1.2W CM5 CPU */
    tx_frame.pwr_display_mw = 45;   /* 45mW E-Ink idle */
    tx_frame.pwr_rf_mw = 15;        /* sample radio-rail reading */
    tx_frame.airgap_active = 0;     /* Normal mode */

    /* Compute CRC */
    tx_frame.crc8 = telemetry_crc8((const uint8_t *)&tx_frame, sizeof(tx_frame) - 1);
    assert(tx_frame.crc8 != 0);

    /* 2. Test successful parsing */
    telemetry_frame_t rx_frame;
    bool ok = telemetry_parse_frame((const uint8_t *)&tx_frame, sizeof(tx_frame), &rx_frame);
    assert(ok == true);
    assert(rx_frame.vbat_mv == 3320);
    assert(rx_frame.ibat_ma == 125);
    assert(rx_frame.soc_pct == 85);
    assert(rx_frame.solar_lux == 78000);
    assert(rx_frame.temp_c_x10 == 265);
    assert(rx_frame.pwr_compute_mw == 1200);
    assert(rx_frame.crc8 == tx_frame.crc8);
    printf("  ✓ Valid frame parsing & CRC-8 verification: PASS\n");

    /* 3. Test corrupted CRC rejection */
    tx_frame.crc8 ^= 0xFF; /* flip bits */
    ok = telemetry_parse_frame((const uint8_t *)&tx_frame, sizeof(tx_frame), &rx_frame);
    assert(ok == false);
    printf("  ✓ Corrupt CRC-8 bitflip rejection: PASS\n");

    /* 4. Test invalid Magic rejection */
    tx_frame.crc8 ^= 0xFF; /* restore CRC */
    tx_frame.magic = 0xDEAD;
    ok = telemetry_parse_frame((const uint8_t *)&tx_frame, sizeof(tx_frame), &rx_frame);
    assert(ok == false);
    printf("  ✓ Bad frame magic rejection: PASS\n");

    /* 5. Test JSON formatting */
    tx_frame.magic = TELEMETRY_FRAME_MAGIC;
    tx_frame.crc8 = telemetry_crc8((const uint8_t *)&tx_frame, sizeof(tx_frame) - 1);
    char json_buf[TELEMETRY_JSON_MAX_LEN];
    int written = telemetry_format_json(&tx_frame, json_buf, sizeof(json_buf));
    assert(written > 0);
    assert(strstr(json_buf, "\"vbat_v\": 3.320") != NULL);
    assert(strstr(json_buf, "\"solar_lux\": 78000") != NULL);
    assert(strstr(json_buf, "\"temp_c\": 26.5") != NULL);
    assert(strstr(json_buf, "\"total_mw\": 1260") != NULL);
    assert(strstr(json_buf, "\"airgap_active\": false") != NULL);
    printf("  ✓ JSON formatting & Waybar output: PASS\n");

    printf("[test_telemetryd] All assertions passed successfully!\n");
    return 0;
}
