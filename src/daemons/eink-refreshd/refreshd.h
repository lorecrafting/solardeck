/**
 * Written 2026-10-19 08:30 UTC in the Pi harness by antigravity/gemini-3.8-flash
 * Scheduler (§52): written 2026-10-20 in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
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

/* IT8951 waveform ladder, fastest -> slowest (SOFTWARE_SPEC §52). The enum order is
 * itself a contract: Phase 4 asserts DU < A2 < GL16 < GLR16 < GLD16 < GC16. */
typedef enum {
    WAVEFORM_MODE_DU = 0,        // 1-bit direct update (~12ms; pen path)
    WAVEFORM_MODE_A2_FAST,       // 1-bit fast (~20ms; keystrokes)
    WAVEFORM_MODE_GL16,          // grey, non-Regal
    WAVEFORM_MODE_GLR16,         // Regal incremental grey
    WAVEFORM_MODE_GLD16,         // Regal direct grey
    WAVEFORM_MODE_GC16_CLEAR,    // High-fidelity 16-level grayscale anti-ghosting clear
    WAVEFORM_MODE_INIT,          // power-on init
    WAVEFORM_MODE_IDLE
} waveform_mode_t;

/* §52 content classes driving the mode picker. */
typedef enum {
    CONTENT_TEXT_1BIT,   // text / cursor -> DU or A2
    CONTENT_GREY,        // antialiased grey -> GLR16
    CONTENT_COLOUR       // images / colour -> GC16 only (no colour motion ever)
} refreshd_content_t;

typedef struct {
    uint16_t x, y, w, h;   // dirty rectangle in panel pixels
} refreshd_rect_t;

typedef struct {
    uint32_t last_keystroke_timestamp_ms;
    uint32_t dirty_frame_count;
    bool scrub_pending;
    bool lock_active;
    waveform_mode_t active_mode;
    uint32_t total_scrubs_executed;
    uint32_t total_fast_updates;
} refreshd_engine_t;

/* §52 Regal-class ghost ledger: one bounded debt counter per tile. */
#define GHOST_TILE_COLS 4
#define GHOST_TILE_ROWS 4
#define GHOST_TILE_COUNT (GHOST_TILE_COLS * GHOST_TILE_ROWS)
#define GHOST_DEBT_THRESHOLD 8   // fast update debt per tile before it owes a GC16

typedef struct {
    uint16_t debt[GHOST_TILE_COUNT];
} refreshd_ghost_ledger_t;

void refreshd_init(refreshd_engine_t *engine);
waveform_mode_t refreshd_on_keystroke(refreshd_engine_t *engine, uint32_t timestamp_ms);
waveform_mode_t refreshd_tick(refreshd_engine_t *engine, uint32_t current_timestamp_ms);

/* §52 scheduler extension. */
waveform_mode_t refreshd_pick_mode(refreshd_content_t cls);
void refreshd_ledger_init(refreshd_ghost_ledger_t *lg);
/* Charge one fast update to the tile covering rect. Returns the most-indebted tile that
 * has crossed GHOST_DEBT_THRESHOLD (index, or -1 when nobody owes a clear yet),
 * or -2 when the rect is outside the panel. Panel size is passed in so no physical
 * dimension is hard-coded here (rule 3.1). */
int refreshd_ledger_charge(refreshd_ghost_ledger_t *lg, uint16_t panel_w, uint16_t panel_h,
                           refreshd_rect_t rect);
void refreshd_ledger_clear(refreshd_ghost_ledger_t *lg, uint8_t tile);
/* Drive one dirty rect. Colour is always GC16 (fast path refused); fast content charges
 * the ghost ledger and is promoted to GC16 when a tile crosses its threshold. */
waveform_mode_t refreshd_schedule(refreshd_engine_t *engine, refreshd_ghost_ledger_t *lg,
                                  uint16_t panel_w, uint16_t panel_h, refreshd_rect_t rect,
                                  refreshd_content_t cls);

#ifdef __cplusplus
}
#endif

#endif // EINK_REFRESHD_H