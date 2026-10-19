/**
 * Written 2026-10-19 08:30 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * SolarDeck eink-refreshd: Cadence-Aware Anti-Ghosting Engine Header
 */

#ifndef EINK_REFRESHD_H
#define EINK_REFRESHD_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#define TYPING_LOCKOUT_MS   800   // Suppress GC16 flash if typing gap < 800ms
#define IDLE_SCRUB_MS       1200  // Trigger full anti-ghosting scrub if idle > 1.2s
#define MAX_DIRTY_FRAMES    30    // Maximum fast updates before mandatory scrub

typedef enum {
    WAVEFORM_MODE_A2_FAST = 0,   // Fast 1-bit 20ms monochrome update
    WAVEFORM_MODE_GC16_CLEAR,    // High-fidelity 16-level grayscale anti-ghosting clear
    WAVEFORM_MODE_IDLE
} waveform_mode_t;

typedef struct {
    uint32_t last_keystroke_timestamp_ms;
    uint32_t dirty_frame_count;
    bool scrub_pending;
    bool lock_active;
    waveform_mode_t active_mode;
    uint32_t total_scrubs_executed;
    uint32_t total_fast_updates;
} refreshd_engine_t;

void refreshd_init(refreshd_engine_t *engine);
waveform_mode_t refreshd_on_keystroke(refreshd_engine_t *engine, uint32_t timestamp_ms);
waveform_mode_t refreshd_tick(refreshd_engine_t *engine, uint32_t current_timestamp_ms);

#ifdef __cplusplus
}
#endif

#endif // EINK_REFRESHD_H
