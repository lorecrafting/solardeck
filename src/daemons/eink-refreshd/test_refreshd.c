/**
 * Written 2026-10-19 08:32 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * §52 scheduler checks: written 2026-10-20 in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
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

    /* ------------------------------------------------------------------ */
    /* §52 scheduler: monotonic ladder, mode picker, ghost ledger         */
    /* Panel is a normalized 4x4 unit grid (one unit per tile) so no      */
    /* physical dimension is hard-coded (rule 3.1).                       */
    /* ------------------------------------------------------------------ */
    const uint16_t PW = 4, PH = 4;

    /* 7. Ladder monotonic: faster modes sort below slower ones (Phase 4 contract). */
    assert(WAVEFORM_MODE_DU < WAVEFORM_MODE_A2_FAST);
    assert(WAVEFORM_MODE_A2_FAST < WAVEFORM_MODE_GL16);
    assert(WAVEFORM_MODE_GL16 < WAVEFORM_MODE_GLR16);
    assert(WAVEFORM_MODE_GLR16 < WAVEFORM_MODE_GLD16);
    assert(WAVEFORM_MODE_GLD16 < WAVEFORM_MODE_GC16_CLEAR);

    /* 8. Mode picker: text -> DU, grey -> GLR16, colour -> GC16 (refused fast path). */
    assert(refreshd_pick_mode(CONTENT_TEXT_1BIT) == WAVEFORM_MODE_DU);
    assert(refreshd_pick_mode(CONTENT_GREY) == WAVEFORM_MODE_GLR16);
    assert(refreshd_pick_mode(CONTENT_COLOUR) == WAVEFORM_MODE_GC16_CLEAR);
    printf("  ✓ Mode picker + monotonic ladder (DU<A2<GL16<GLR16<GLD16<GC16) verified.\n");

    /* 9. Ghost ledger drains to zero after a bounded workload (Phase 4 hook). */
    refreshd_ghost_ledger_t ledger;
    refreshd_ledger_init(&ledger);
    uint32_t total_debt = 0;
    for (int i = 0; i < GHOST_TILE_COUNT; i++) total_debt += ledger.debt[i];
    assert(total_debt == 0); /* fresh ledger is empty */

    /* Single-tile workload: (threshold - 1) fast updates owe nothing, the k-th crosses
     * the threshold, paying it returns the tile's debt to zero while debt stays low. */
    refreshd_rect_t tl = {0, 0, 1, 1}; /* top-left tile only */
    int owed = -1;
    for (int i = 0; i < GHOST_DEBT_THRESHOLD - 1; i++) {
        assert(refreshd_ledger_charge(&ledger, PW, PH, tl) == -1); /* not yet owing */
    }
    owed = refreshd_ledger_charge(&ledger, PW, PH, tl);
    assert(owed == 0); /* exactly the tile we dirtied, and it owes a GC16 */
    refreshd_ledger_clear(&ledger, (uint8_t)owed);
    total_debt = 0;
    for (int i = 0; i < GHOST_TILE_COUNT; i++) total_debt += ledger.debt[i];
    assert(total_debt == 0); /* paid tile is back to zero */
    printf("  ✓ Single-tile ghost debt crosses threshold and drains to zero (Regal-class).\n");

    /* Full-panel workload: a full-panel 1-bit rect charges all 16 tiles. A bounded
     * full clear pass (INIT/GC16 covers the panel) must return the ledger to zero. */
    refreshd_rect_t full = {0, 0, PW, PH};
    for (int i = 0; i < GHOST_DEBT_THRESHOLD; i++) {
        (void)refreshd_ledger_charge(&ledger, PW, PH, full);
    }
    total_debt = 0;
    for (int i = 0; i < GHOST_TILE_COUNT; i++) {
        assert(ledger.debt[i] >= GHOST_DEBT_THRESHOLD);
        refreshd_ledger_clear(&ledger, (uint8_t)i); /* one full clear pass */
    }
    total_debt = 0;
    for (int i = 0; i < GHOST_TILE_COUNT; i++) total_debt += ledger.debt[i];
    assert(total_debt == 0); /* full GC16 pass drains everything */
    printf("  ✓ Full-panel workload drains to zero after one full clear pass.\n");

    /* 10. Scheduler: text rect stays fast while debt is low... */
    refreshd_ghost_ledger_t l2;
    refreshd_ledger_init(&l2);
    refreshd_engine_t eng2;
    refreshd_init(&eng2);
    waveform_mode_t m = refreshd_schedule(&eng2, &l2, PW, PH, tl, CONTENT_TEXT_1BIT);
    assert(m == WAVEFORM_MODE_DU);
    assert(eng2.total_fast_updates == 1);
    assert(eng2.total_scrubs_executed == 0);

    /* ... but a colour rect is GC16 regardless of debt, and costs no fast-update credit. */
    refreshd_rect_t anywhere = {2, 2, 1, 1};
    m = refreshd_schedule(&eng2, &l2, PW, PH, anywhere, CONTENT_COLOUR);
    assert(m == WAVEFORM_MODE_GC16_CLEAR);
    assert(eng2.total_fast_updates == 1); /* unchanged by the colour pass */
    printf("  ✓ Scheduler: fast text stays DU, colour always GC16 (no colour-motion claim).\n");

    /* 11. Out-of-panel rect is rejected, not charged. */
    refreshd_rect_t off = {PW, 0, 1, 1};
    assert(refreshd_ledger_charge(&l2, PW, PH, off) == -2);
    assert(refreshd_ledger_charge(&l2, 0, PH, tl) == -2);
    refreshd_rect_t empty = {0, 0, 0, 0};
    assert(refreshd_ledger_charge(&l2, PW, PH, empty) == -2); /* zero-area */
    printf("  ✓ Out-of-panel dirt rejected.\n");

    printf("✓ All eink-refreshd self-tests passed successfully!\n");
    return 0;
}
