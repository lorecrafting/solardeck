/**
 * Written 2026-10-20 12:35 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017
 *
 * Wire-contract self-test. The _Static_asserts in solardeck_regs.h prove the layout at compile time;
 * this proves the parts a compiler cannot: CRC behaviour and frame validation.
 */
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "solardeck_regs.h"

static void fill_valid(solardeck_frame_t *f)
{
    memset(f, 0, sizeof *f);
    f->magic0 = SD_MAGIC0;
    f->magic1 = SD_MAGIC1;
    f->proto = SD_PROTO_VERSION;
    f->state = SD_STATE_S2IDLE;
    f->vbat_mv = 3300;
    f->crc16 = sd_crc16_ccitt((const uint8_t *)f, REG_CRC16);
}

int main(void)
{
    solardeck_frame_t f;

    /* Layout invariants that matter on the wire. */
    assert(sizeof(solardeck_frame_t) == 64);
    assert(offsetof(solardeck_frame_t, vbat_mv) == 0x08);
    assert(offsetof(solardeck_frame_t, last_wake_us) == 0x10);
    assert(offsetof(solardeck_frame_t, events) == 0x18);
    assert(offsetof(solardeck_frame_t, crc16) == 0x3E);

    /* CRC-16/CCITT-FALSE standard vector: "123456789" -> 0x29B1. */
    assert(sd_crc16_ccitt((const uint8_t *)"123456789", 9) == 0x29B1);

    /* A well-formed frame validates. */
    fill_valid(&f);
    assert(sd_frame_valid(&f));

    /* Any single-bit flip in the payload must be rejected. */
    for (size_t byte = 0; byte < REG_CRC16; byte++) {
        solardeck_frame_t g = f;
        ((uint8_t *)&g)[byte] ^= 0x01;
        assert(!sd_frame_valid(&g));
    }

    /* Wrong magic and wrong protocol are rejected even with a valid CRC. */
    solardeck_frame_t g = f;
    g.magic0 = 'X';
    g.crc16 = sd_crc16_ccitt((const uint8_t *)&g, REG_CRC16);
    assert(!sd_frame_valid(&g));

    g = f;
    g.proto = SD_PROTO_VERSION + 1;
    g.crc16 = sd_crc16_ccitt((const uint8_t *)&g, REG_CRC16);
    assert(!sd_frame_valid(&g));

    printf("test_regs: OK (64-byte frame, CRC-16/CCITT-FALSE, %d-byte payload guarded)\n",
           (int)REG_CRC16);
    return 0;
}
