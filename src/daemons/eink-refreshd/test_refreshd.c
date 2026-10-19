/**
 * Written 2026-10-19 08:32 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * Runnable Assert-based Verification Check for eink-refreshd
 */

#include <stdio.h>
#include <assert.h>
#include "refreshd.h"

int main(void) {
    printf("[Track B Check 2] Running eink-refreshd Cadence Engine Self-Tests...\n");

    refreshd_engine_t engine;
    refreshd_init(&engine);

    assert(engine.dirty_frame_count == 0);
    assert(engine.lock_active == false);
    assert(engine.scrub_pending == false);

    // 1. First Keystroke at t=1000ms
    waveform_mode_t mode = refreshd_on_keystroke(&engine, 1000);
    assert(mode == WAVEFORM_MODE_A2_FAST);
    assert(engine.dirty_frame_count == 1);
    assert(engine.scrub_pending == true);

    // 2. Fast Burst Keystrokes (<800ms gap, e.g. typing at 120 WPM)
    mode = refreshd_on_keystroke(&engine, 1150); // delta 150ms < 800ms
    assert(mode == WAVEFORM_MODE_A2_FAST);
    assert(engine.lock_active == true); // Locked out!

    mode = refreshd_on_keystroke(&engine, 1300); // delta 150ms < 800ms
    assert(mode == WAVEFORM_MODE_A2_FAST);
    assert(engine.lock_active == true);

    // 3. Periodic tick while still typing / short pause (gap 300ms < 1200ms)
    mode = refreshd_tick(&engine, 1600); // delta = 300ms
    assert(mode == WAVEFORM_MODE_IDLE);
    assert(engine.total_scrubs_executed == 0); // No scrub triggered!
    assert(engine.lock_active == true);       // Lock still held (<800ms)

    // 4. Tick after typing pauses for 900ms (>= 800ms lockout cleared, but < 1200ms scrub)
    mode = refreshd_tick(&engine, 2200); // delta = 900ms
    assert(mode == WAVEFORM_MODE_IDLE);
    assert(engine.lock_active == false);      // Lock released!
    assert(engine.scrub_pending == true);     // Scrub still waiting for >1.2s idle

    // 5. Tick after idle exceeds 1.2s (>1200ms scrub threshold)
    mode = refreshd_tick(&engine, 2550); // delta = 1250ms > 1200ms
    assert(mode == WAVEFORM_MODE_GC16_CLEAR); // Scrub triggered!
    assert(engine.total_scrubs_executed == 1);
    assert(engine.scrub_pending == false);
    assert(engine.dirty_frame_count == 0);
    printf("  ✓ Cadence lockout (<800ms lock, >1.2s scrub) verified cleanly.\n");

    // 6. Mandatory Scrub on Continuous Typing (>30 frames without pause)
    for (int i = 0; i < 29; i++) {
        mode = refreshd_on_keystroke(&engine, 3000 + (i * 100));
        assert(mode == WAVEFORM_MODE_A2_FAST);
    }
    // 30th keystroke triggers safety GC16 clear
    mode = refreshd_on_keystroke(&engine, 3000 + (29 * 100));
    assert(mode == WAVEFORM_MODE_GC16_CLEAR);
    assert(engine.total_scrubs_executed == 2);
    printf("  ✓ Max dirty frame limit (30 frames) mandatory clear verified.\n");

    printf("✓ All eink-refreshd self-tests passed successfully!\n");
    return 0;
}
