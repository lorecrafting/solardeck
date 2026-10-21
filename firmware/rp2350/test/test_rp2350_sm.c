/**
 * Written 2026-10-19 08:28 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * Runnable Assert-based Self-Test for RP2350 State Machine & Power Rails
 */

#include <stdio.h>
#include <assert.h>
#include "solardeck_state.h"

int main(void) {
    printf("[Track B Check 1] Running RP2350 State Machine Self-Tests...\n");

    solardeck_ctx_t ctx;

    // 1. Initial state
    solardeck_sm_init(&ctx);
    assert(ctx.current_state == SOLAR_STATE_COLD_BOOT);
    assert(ctx.sys_5v_enabled == false);
    assert(ctx.tmux_cm5_selected == false);

    // 2. Transition to CM5 Active Mode
    solardeck_sm_transition(&ctx, SOLAR_STATE_CM5_ACTIVE);
    assert(ctx.current_state == SOLAR_STATE_CM5_ACTIVE);
    assert(ctx.sys_5v_enabled == true);
    assert(ctx.tmux_cm5_selected == true);

    // 3. Transition to Zen Reader Mode (4.5mW reading, CM5 off)
    solardeck_sm_transition(&ctx, SOLAR_STATE_ZEN_READER);
    assert(ctx.current_state == SOLAR_STATE_ZEN_READER);
    assert(ctx.sys_5v_enabled == false);
    assert(ctx.tmux_cm5_selected == false);

    // 4. Test S2idle Wake Trigger (<300ms spec)
    // Put into S2idle
    solardeck_sm_transition(&ctx, SOLAR_STATE_S2IDLE_SLEEP);
    assert(ctx.current_state == SOLAR_STATE_S2IDLE_SLEEP);

    bool woke = solardeck_trigger_s2idle_wake(&ctx);
    assert(woke == true);
    assert(ctx.current_state == SOLAR_STATE_CM5_ACTIVE);
    assert(ctx.sys_5v_enabled == true);
    assert(ctx.tmux_cm5_selected == true);
    printf("  ✓ Wake powers the CM5 and hands it the display\n");

    // 5. Test Solar MPPT Calculation
    solardeck_sample_solar_mppt(&ctx, 2500); // 2.5V Voc
    assert(ctx.solar_voc_mv == 2500);
    assert(ctx.solar_vmpp_mv == 1950); // 78% of 2500 = 1950 mV
    printf("  ✓ Solar MPPT sampling verified (Voc=%u mV -> Vmpp=%u mV)\n", ctx.solar_voc_mv, ctx.solar_vmpp_mv);

    // 6. Critical low-battery alarm
    bool alarm = solardeck_check_power_thresholds(&ctx, SD_LOW_BATT_ALARM_MV + 300); // healthy pack
    assert(alarm == false);

    alarm = solardeck_check_power_thresholds(&ctx, SD_LOW_BATT_ALARM_MV - 50);
    assert(alarm == true);
    assert(ctx.current_state == SOLAR_STATE_LOW_BATT_ALARM);
    assert(ctx.pwrfail_pin_asserted == true);
    assert(ctx.tmux_cm5_selected == false);
    printf("  ✓ Low-battery alarm raises power-fail\n");

    // 7. Charger hold-off (ADR-035/048): VREG at the limit, watchdog off, and a matching pack.
    solardeck_sm_init(&ctx);
    assert(solardeck_charge_enable_allowed(&ctx) == false);   // nothing written or read
    ctx.charger_vreg_mv = SD_CHARGE_LIMIT_MV;                   // a reset charger reads its POR VREG,
    ctx.pack_charge_mv = SD_CHARGE_LIMIT_MV;                    // which equals the Li-ion limit...
    assert(solardeck_charge_enable_allowed(&ctx) == false);   // ...but its watchdog is still on
    ctx.charger_wdt_off = true;
    assert(solardeck_charge_enable_allowed(&ctx) == true);
    ctx.pack_charge_mv = SD_CHARGE_LIMIT_MV + 150;              // a pack rated for another voltage
    assert(solardeck_charge_enable_allowed(&ctx) == false);
    ctx.pack_charge_mv = 0;                                     // pack gauge not read / no pack
    assert(solardeck_charge_enable_allowed(&ctx) == false);
    printf("  ✓ Charger stays off until VREG, watchdog and pack all check out at %u mV\n", SD_CHARGE_LIMIT_MV);

    // 8. No line is driven into an unpowered CM5 (PIN_BUDGET rule 1, defence in depth).
    solardeck_sm_init(&ctx);
    solardeck_sm_transition(&ctx, SOLAR_STATE_ZEN_READER);
    solardeck_check_power_thresholds(&ctx, SD_LOW_BATT_ALARM_MV - 50);
    assert(ctx.pwrfail_pin_asserted == false);
    printf("  ✓ Power-fail line stays low while the CM5 is unpowered\n");

    printf("✓ All RP2350 State Machine self-tests passed successfully!\n");
    return 0;
}
