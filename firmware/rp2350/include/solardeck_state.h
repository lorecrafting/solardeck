/**
 * Written 2026-10-19 08:25 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * SolarDeck RP2350 Co-Processor Power Management & Bus Control State Machine
 */

#ifndef SOLARDECK_STATE_H
#define SOLARDECK_STATE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// Hardware Pin Definitions
#define PIN_TMUX_SEL_CM4_NRP    13   // High: CM4 controls EPDC; Low: RP2350 controls EPDC
#define PIN_EN_5V_SYS           14   // TPS61088 5V System Boost Enable
#define PIN_GPIO17_WAKE         15   // CM4 S2idle Wake Trigger (<300ms)
#define PIN_GPIO16_PWRFAIL      16   // CM4 Emergency Powerfail Flush (<150ms)
#define PIN_CHEM_SEL            18   // Hardware Chem Sel (Low: LiFePO4 3.65V, High: Li-ion 4.2V)
#define PIN_SOLAR_ADC           26   // ADC Channel 0 for Solar Panel Voc/Vmpp

// System States
typedef enum {
    SOLAR_STATE_COLD_BOOT = 0,
    SOLAR_STATE_CM4_ACTIVE,
    SOLAR_STATE_ZEN_READER,
    SOLAR_STATE_S2IDLE_SLEEP,
    SOLAR_STATE_LOW_BATT_ALARM
} solardeck_state_t;

// State Machine Context
typedef struct {
    solardeck_state_t current_state;
    bool tmux_cm4_selected;    // true = CM4, false = RP2350
    bool sys_5v_enabled;       // true = TPS61088 active
    bool wake_pin_asserted;    // GPIO17 state
    bool pwrfail_pin_asserted; // GPIO16 state
    uint16_t vbat_mv;          // Battery voltage (mV)
    uint16_t solar_voc_mv;     // Solar panel open-circuit voltage (mV)
    uint16_t solar_vmpp_mv;    // Target MPP voltage (approx 78% Voc)
    bool is_lifepo4;           // Chem select (true = LiFePO4)
    uint32_t last_wake_elapsed_us; // Wake latency measurement
} solardeck_ctx_t;

// Core Functions
void solardeck_sm_init(solardeck_ctx_t *ctx, bool chem_sel_pin);
void solardeck_sm_transition(solardeck_ctx_t *ctx, solardeck_state_t next_state);
void solardeck_sample_solar_mppt(solardeck_ctx_t *ctx, uint16_t measured_voc_mv);
bool solardeck_trigger_s2idle_wake(solardeck_ctx_t *ctx);
bool solardeck_check_power_thresholds(solardeck_ctx_t *ctx, uint16_t vbat_mv);

#ifdef __cplusplus
}
#endif

#endif // SOLARDECK_STATE_H
