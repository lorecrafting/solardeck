/**
 * Written 2026-10-19 08:31 UTC in the Pi harness by antigravity/gemini-3.8-flash
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
