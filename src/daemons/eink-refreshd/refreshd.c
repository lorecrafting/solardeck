/**
 * Written 2026-10-19 08:31 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * Scheduler (§52): written 2026-10-20 in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
 * SolarDeck eink-refreshd: Cadence-Aware Anti-Ghosting Engine Implementation
 */

#include "refreshd.h"

void refreshd_init(refreshd_engine_t *engine) {
    if (!engine) return;
    engine->last_keystroke_timestamp_ms = 0;
    engine->dirty_frame_count = 0;
    engine->scrub_pending = false;
    engine->lock_active = false;
    engine->active_mode = WAVEFORM_MODE_IDLE;
    engine->total_scrubs_executed = 0;
    engine->total_fast_updates = 0;
}

waveform_mode_t refreshd_on_keystroke(refreshd_engine_t *engine, uint32_t timestamp_ms) {
    if (!engine) return WAVEFORM_MODE_IDLE;

    uint32_t delta = timestamp_ms - engine->last_keystroke_timestamp_ms;
    engine->last_keystroke_timestamp_ms = timestamp_ms;
    engine->dirty_frame_count++;
    engine->total_fast_updates++;
    engine->scrub_pending = true;

    // Fast typing stream lockout (<800ms)
    if (delta < TYPING_LOCKOUT_MS) {
        engine->lock_active = true;
    }

    // Mandatory clean threshold if typing continuous text for too long without pause
    if (engine->dirty_frame_count >= MAX_DIRTY_FRAMES) {
        engine->dirty_frame_count = 0;
        engine->scrub_pending = false;
        engine->lock_active = false;
        engine->total_scrubs_executed++;
        engine->active_mode = WAVEFORM_MODE_GC16_CLEAR;
        return WAVEFORM_MODE_GC16_CLEAR;
    }

    engine->active_mode = WAVEFORM_MODE_A2_FAST;
    return WAVEFORM_MODE_A2_FAST;
}

waveform_mode_t refreshd_tick(refreshd_engine_t *engine, uint32_t current_timestamp_ms) {
    if (!engine) return WAVEFORM_MODE_IDLE;

    uint32_t idle_gap = current_timestamp_ms - engine->last_keystroke_timestamp_ms;

    // Unlock typing lock if gap exceeds lockout window (>=800ms)
    if (idle_gap >= TYPING_LOCKOUT_MS) {
        engine->lock_active = false;
    }

    // Trigger full anti-ghosting scrub if idle pause > 1200ms (>1.2s) and dirty frames are pending
    if (engine->scrub_pending && idle_gap >= IDLE_SCRUB_MS) {
        engine->scrub_pending = false;
        engine->dirty_frame_count = 0;
        engine->total_scrubs_executed++;
        engine->active_mode = WAVEFORM_MODE_GC16_CLEAR;
        return WAVEFORM_MODE_GC16_CLEAR;
    }

    engine->active_mode = WAVEFORM_MODE_IDLE;
    return WAVEFORM_MODE_IDLE;
}

/* ------------------------------------------------------------------ */
/* §52 scheduler extension                                           */
/* ------------------------------------------------------------------ */

waveform_mode_t refreshd_pick_mode(refreshd_content_t cls) {
    /* Ladder must stay strictly increasing (Phase 4 asserts the enum order). */
    switch (cls) {
        case CONTENT_TEXT_1BIT:
            return WAVEFORM_MODE_DU;
        case CONTENT_GREY:
            return WAVEFORM_MODE_GLR16;
        case CONTENT_COLOUR:
            /* No colour fast path, ever: colour motion is unsupported (§52). */
            return WAVEFORM_MODE_GC16_CLEAR;
    }
    return WAVEFORM_MODE_IDLE; /* unreachable: exhaustive enum */
}

void refreshd_ledger_init(refreshd_ghost_ledger_t *lg) {
    if (!lg) return;
    for (int i = 0; i < GHOST_TILE_COUNT; i++) {
        lg->debt[i] = 0;
    }
}

int refreshd_ledger_charge(refreshd_ghost_ledger_t *lg, uint16_t panel_w, uint16_t panel_h,
                           refreshd_rect_t rect) {
    if (!lg) return -2;
    if (panel_w == 0 || panel_h == 0) return -2;
    if (rect.x >= panel_w || rect.y >= panel_h) return -2; /* outside panel */
    if (rect.w == 0 || rect.h == 0) return -2;               /* zero-area update: nothing to charge */

    /* Cover the dirty rect with the tile grid; clamp so the last row/col is inclusive. */
    uint32_t right = rect.x + rect.w;
    uint32_t bottom = rect.y + rect.h;
    if (right > panel_w) right = panel_w;
    if (bottom > panel_h) bottom = panel_h;
    uint8_t col0 = (uint8_t)(rect.x * GHOST_TILE_COLS / panel_w);
    uint8_t row0 = (uint8_t)(rect.y * GHOST_TILE_ROWS / panel_h);
    uint8_t col1 = (uint8_t)((right - 1) * GHOST_TILE_COLS / panel_w);
    uint8_t row1 = (uint8_t)((bottom - 1) * GHOST_TILE_ROWS / panel_h);

    /* Charge every tile the rect touches. */
    for (uint8_t r = row0; r <= row1; r++) {
        for (uint8_t c = col0; c <= col1; c++) {
            uint8_t t = (uint8_t)(r * GHOST_TILE_COLS + c);
            if (lg->debt[t] < UINT16_MAX) lg->debt[t]++; /* saturate, never wrap */
        }
    }

    /* Most-indebted tile that has crossed the threshold: that one owes a GC16. */
    int worst = -1;
    uint16_t worst_debt = 0;
    for (uint8_t t = 0; t < GHOST_TILE_COUNT; t++) {
        if (lg->debt[t] >= GHOST_DEBT_THRESHOLD && lg->debt[t] > worst_debt) {
            worst = t;
            worst_debt = lg->debt[t];
        }
    }
    return worst;
}

void refreshd_ledger_clear(refreshd_ghost_ledger_t *lg, uint8_t tile) {
    if (!lg || tile >= GHOST_TILE_COUNT) return;
    lg->debt[tile] = 0;
}

waveform_mode_t refreshd_schedule(refreshd_engine_t *engine, refreshd_ghost_ledger_t *lg,
                                  uint16_t panel_w, uint16_t panel_h, refreshd_rect_t rect,
                                  refreshd_content_t cls) {
    if (!engine || !lg) return WAVEFORM_MODE_IDLE;

    /* Colour is always the slow balanced path; refuse the fast path outright. */
    if (cls == CONTENT_COLOUR) {
        engine->active_mode = WAVEFORM_MODE_GC16_CLEAR;
        return WAVEFORM_MODE_GC16_CLEAR;
    }

    waveform_mode_t mode = refreshd_pick_mode(cls);
    int owed = refreshd_ledger_charge(lg, panel_w, panel_h, rect);
    if (owed >= 0) {
        /* A tile crossed its debt threshold: pay it off with one GC16 pass, cheapest first. */
        refreshd_ledger_clear(lg, (uint8_t)owed);
        engine->active_mode = WAVEFORM_MODE_GC16_CLEAR;
        engine->total_scrubs_executed++;
        return WAVEFORM_MODE_GC16_CLEAR;
    }

    engine->active_mode = mode;
    if (mode != WAVEFORM_MODE_GC16_CLEAR) {
        engine->total_fast_updates++;
    }
    return mode;
}
