/**
 * Written 2026-10-19 08:27 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * SolarDeck RP2350 Co-Processor Main Entry Point
 */

#include "solardeck_state.h"

#ifdef PICO_SDK_AVAILABLE
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include "hardware/timer.h"
#include "hardware/uart.h"
#else
#include <stdio.h>
#endif

int main(void) {
    solardeck_ctx_t ctx;

#ifdef PICO_SDK_AVAILABLE
    stdio_init_all();

    // Configure GPIOs
    gpio_init(PIN_TMUX_SEL_CM5_NRP);
    gpio_set_dir(PIN_TMUX_SEL_CM5_NRP, GPIO_OUT);
    gpio_put(PIN_TMUX_SEL_CM5_NRP, 0);

    gpio_init(PIN_EN_5V_SYS);
    gpio_set_dir(PIN_EN_5V_SYS, GPIO_OUT);
    gpio_put(PIN_EN_5V_SYS, 0);

    gpio_init(PIN_GPIO17_WAKE);
    gpio_set_dir(PIN_GPIO17_WAKE, GPIO_OUT);
    gpio_put(PIN_GPIO17_WAKE, 0);

    gpio_init(PIN_GPIO16_PWRFAIL);
    gpio_set_dir(PIN_GPIO16_PWRFAIL, GPIO_OUT);
    gpio_put(PIN_GPIO16_PWRFAIL, 0);

    // ADC setup for solar monitoring
    adc_init();
    adc_gpio_init(PIN_SOLAR_ADC);
    adc_select_input(0);

    solardeck_sm_init(&ctx);
#else
    solardeck_sm_init(&ctx);
#endif

    // Initial transition into CM5 active mode
    solardeck_sm_transition(&ctx, SOLAR_STATE_CM5_ACTIVE);

#ifdef PICO_SDK_AVAILABLE
    while (1) {
        // Read Solar ADC
        uint16_t raw_adc = adc_read();
        uint16_t solar_mv = (uint16_t)(((uint32_t)raw_adc * 3300) / 4096);
        solardeck_sample_solar_mppt(&ctx, solar_mv);

        sleep_ms(100);
    }
#endif

    return 0;
}
