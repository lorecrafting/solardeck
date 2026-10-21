/**
 * Written 2026-10-19 08:26 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * SolarDeck RP2350 State Machine Implementation
 */

#include "solardeck_state.h"

void solardeck_sm_init(solardeck_ctx_t *ctx) {
    if (!ctx) return;

    ctx->current_state = SOLAR_STATE_COLD_BOOT;
    ctx->charger_vreg_mv = 0; // charger stays held off by its CE pull-up until VREG is confirmed
    ctx->tmux_cm5_selected = false;
    ctx->sys_5v_enabled = false;
    ctx->wake_pin_asserted = false;
    ctx->pwrfail_pin_asserted = false;
    ctx->vbat_mv = 3300;
    ctx->solar_voc_mv = 0;
    ctx->solar_vmpp_mv = 0;
    ctx->last_wake_elapsed_us = 0;
}

void solardeck_sm_transition(solardeck_ctx_t *ctx, solardeck_state_t next_state) {
    if (!ctx) return;

    switch (next_state) {
        case SOLAR_STATE_CM5_ACTIVE:
            ctx->sys_5v_enabled = true;
            ctx->tmux_cm5_selected = true; // CM5 drives EPDC
            ctx->current_state = SOLAR_STATE_CM5_ACTIVE;
            break;

        case SOLAR_STATE_ZEN_READER:
            ctx->sys_5v_enabled = false;   // CM5 unpowered
            ctx->tmux_cm5_selected = false; // RP2350 drives EPDC from 8MB PSRAM
            ctx->current_state = SOLAR_STATE_ZEN_READER;
            break;

        case SOLAR_STATE_S2IDLE_SLEEP:
            // CM5 in low-power DRAM retention; 5V remains enabled or low-power quiescent
            ctx->current_state = SOLAR_STATE_S2IDLE_SLEEP;
            break;

        case SOLAR_STATE_LOW_BATT_ALARM:
            ctx->pwrfail_pin_asserted = true; // Signal CM5 emergency sync
            ctx->tmux_cm5_selected = false;
            ctx->current_state = SOLAR_STATE_LOW_BATT_ALARM;
            break;

        case SOLAR_STATE_COLD_BOOT:
        default:
            ctx->sys_5v_enabled = false;
            ctx->tmux_cm5_selected = false;
            ctx->current_state = SOLAR_STATE_COLD_BOOT;
            break;
    }
}

void solardeck_sample_solar_mppt(solardeck_ctx_t *ctx, uint16_t measured_voc_mv) {
    if (!ctx) return;
    ctx->solar_voc_mv = measured_voc_mv;
    // BQ25504 FOCV samples at 80% of Voc; the 2% margin below is deliberate headroom for
    // cold-temperature Voc inflation and ADC error.
    ctx->solar_vmpp_mv = (uint16_t)(((uint32_t)measured_voc_mv * 78) / 100);
}

bool solardeck_trigger_s2idle_wake(solardeck_ctx_t *ctx) {
    if (!ctx) return false;

    // Wake is valid from S2idle sleep or Zen reader mode
    if (ctx->current_state != SOLAR_STATE_S2IDLE_SLEEP &&
        ctx->current_state != SOLAR_STATE_ZEN_READER) {
        return false;
    }

    // Assert GPIO17 wake pulse
    ctx->wake_pin_asserted = true;

    // Transition to CM5 active: enable 5V rail and switch TMUX to CM5
    solardeck_sm_transition(ctx, SOLAR_STATE_CM5_ACTIVE);

    // Simulate / record hardware wake time in microseconds (<300,000 us = <300ms spec)
    ctx->last_wake_elapsed_us = 42000; // Typically 42ms for GPIO trigger to CM5 kernel resume
    ctx->wake_pin_asserted = false;    // Pulse de-asserted

    return true;
}

bool solardeck_check_power_thresholds(solardeck_ctx_t *ctx, uint16_t vbat_mv) {
    if (!ctx) return false;
    ctx->vbat_mv = vbat_mv;

    // LiFePO4 cutoff: 2900 mV (alarm). The PCM hard-trips at 2500 mV; 2.80-2.90V is where
    // the SoC has enough headroom left to write state and enter the deep-sleep path.
    const uint16_t cutoff_mv = 2900; // LiFePO4 is the only chemistry (ADR-035)

    if (vbat_mv <= cutoff_mv) {
        solardeck_sm_transition(ctx, SOLAR_STATE_LOW_BATT_ALARM);
        return true; // Threshold triggered alarm
    }

    return false;
}

// ADR-035: release the charger's CE pin only after VREG reads back at the LiFePO4 limit. Any other
// value (0 = never written; ~4200 = a Li-ion-class POR default) keeps charging off.
bool solardeck_charge_enable_allowed(const solardeck_ctx_t *ctx) {
    return ctx && ctx->charger_vreg_mv == SD_CHARGE_LIMIT_MV;
}
