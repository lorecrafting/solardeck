#!/usr/bin/env python3
"""
Phase 15: the CM5 <-> RP2350 contract cannot drift.

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

The header is the contract; docs/FIRMWARE_INTERFACE.md is the readable copy. This check is
bidirectional, so neither can silently gain a register the other does not know about:

  1. every `REG_*` in the header is documented, and every `REG_*` in the doc exists in the header
  2. every SD_CMD_/SD_EVENT_/SD_ACK_/SD_STATE_ constant used by the doc exists in the header
  3. the wire test compiles and passes natively (the layout asserts are compile-time; CRC is not)
  4. the pin budget (spec_values.pins, ADR-045): every pin's function exists on that pin per the
     datasheet mux, no net is assigned twice, every net crossing into the CM5 domain says how it is
     kept from back-powering an unpowered CM5, the TMUX has the channels, and the firmware PIN_*
     defines and docs/PIN_BUDGET.md agree with the spec

A one-directional check would let a developer add a register to the header and ship firmware the CM5
driver never reads -- which is the exact class of bug this file exists to prevent.
"""
import os
import re
import subprocess
import sys
import json
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = os.path.join(ROOT, "firmware", "rp2350", "include", "solardeck_regs.h")
DOC = os.path.join(ROOT, "docs", "FIRMWARE_INTERFACE.md")
TEST = os.path.join(ROOT, "firmware", "rp2350", "test", "test_regs.c")
SPEC = os.path.join(ROOT, "docs", "spec_values.json")
STATE_HDR = os.path.join(ROOT, "firmware", "rp2350", "include", "solardeck_state.h")
PIN_DOC = os.path.join(ROOT, "docs", "PIN_BUDGET.md")

# CM5 datasheet GPIO function table (RP1), only the alternates this design uses; any other function
# fails as unverified rather than being guessed. "gpio" is valid on every pin.
CM5_FN = {0: {"id_sd"}, 1: {"id_sc"}, 2: {"i2c1_sda"}, 3: {"i2c1_scl"}, 4: {"spi3_csn0"},
          5: {"spi3_miso"}, 6: {"spi3_mosi"}, 7: {"spi3_sclk", "spi0_ce1"}, 8: {"spi0_ce0"},
          9: {"spi0_miso"}, 10: {"spi0_mosi"}, 11: {"spi0_sclk"}, 14: {"uart0_tx"},
          15: {"uart0_rx"}, 18: {"i2s0_sclk"}, 19: {"i2s0_ws"}, 20: {"i2s0_sdi"}, 21: {"i2s0_sdo"}}
# Ways a net driven from the always-on RP2350 into the CM5 domain avoids back-powering it.
ISOLATION = {"tmux", "rp_input", "fw_hiz", "od", "low_when_off"}


def rp2350_fn_ok(pin, fn):
    """RP2350B GPIO function select (datasheet Table 3), as arithmetic on the pin number."""
    if fn in ("sio", "pio"):
        return 0 <= pin <= 47
    if fn == "adc":
        return 40 <= pin <= 47
    if fn == "qmi_cs1":
        return pin in (0, 8, 19, 47)
    m = re.fullmatch(r"spi([01])_(rx|csn|sck|tx)", fn)
    if m:
        return int(m[1]) == (pin // 8) % 2 and m[2] == ("rx", "csn", "sck", "tx")[pin % 4]
    m = re.fullmatch(r"i2c([01])_(sda|scl)", fn)
    if m:
        return int(m[1]) == (pin % 4) // 2 and m[2] == ("sda", "scl")[pin % 2]
    m = re.fullmatch(r"uart([01])_(tx|rx)", fn)
    if m:
        return pin % 4 < 2 and int(m[1]) == ((pin + 4) // 8) % 2 and m[2] == ("tx", "rx")[pin % 4]
    return False


def no_dup_keys(pairs):
    keys = [k for k, _ in pairs]
    dups = sorted({k for k in keys if keys.count(k) > 1})
    if dups:
        raise ValueError(f"duplicate key(s) {dups} in spec_values.json")
    return dict(pairs)


def pin_errors(spec_text, state_hdr, pin_doc):
    try:
        pins = json.loads(spec_text, object_pairs_hook=no_dup_keys)["pins"]
    except ValueError as e:
        return [f"pin budget: {e}"]
    rp, ex, cm = pins["rp2350b"], pins["aon_expander"], pins["cm5_gpio"]
    errors = []
    # The always-on GPIO expander is the RP2350's overflow: one net namespace with the RP2350.
    rp_nets = [e["net"] for e in list(rp.values()) + list(ex.values())]
    for n in sorted({n for n in rp_nets if rp_nets.count(n) > 1}):
        errors.append(f"RP2350/expander: net {n} is assigned to more than one pin")
    for side, table, ok, top in (("RP2350", rp, rp2350_fn_ok, 47),
                                 ("EXP", ex, lambda p, f: f == "gpio", pins["aon_expander_pins"] - 1),
                                 ("CM5", cm, lambda p, f: f == "gpio" or f in CM5_FN.get(p, ()), 27)):
        nets = [e["net"] for e in table.values()]
        for n in sorted({n for n in nets if nets.count(n) > 1}):
            errors.append(f"{side}: net {n} is assigned to more than one pin")
        for pin, e in table.items():
            if not 0 <= int(pin) <= top or not ok(int(pin), e["fn"]):
                errors.append(f"{side} GPIO{pin}: function '{e['fn']}' is not available on that pin "
                              f"(or unverified)")
            if e.get("iso") and e["iso"] not in ISOLATION:
                errors.append(f"{side} GPIO{pin}: unknown isolation '{e['iso']}'")
    cm5_nets = {e["net"] for e in cm.values()} | {e["net"] for e in pins["cm5_ctrl"].values()}
    for pin, e in list(rp.items()) + list(ex.items()):
        if e["net"] in cm5_nets and e.get("iso") in (None, "tmux"):
            errors.append(f"RP2350 GPIO{pin} {e['net']} enters the CM5 domain without an isolation rule")
    tmux = [sum(e.get("iso") == "tmux" for e in t.values()) for t in (rp, cm)]
    if tmux[0] != tmux[1] or tmux[0] > pins["tmux_channels"]:
        errors.append(f"TMUX lines RP2350={tmux[0]} CM5={tmux[1]} must pair within "
                      f"{pins['tmux_channels']} channels")
    defines = {n: int(v) for n, v in re.findall(r"#define\s+(PIN_[A-Z0-9_]+)\s+(\d+)", state_hdr)}
    spec_fw = {e["fw"]: int(p) for p, e in rp.items() if "fw" in e}
    for n in sorted(set(defines) | set(spec_fw)):
        if defines.get(n) != spec_fw.get(n):
            errors.append(f"{n}: solardeck_state.h says GPIO{defines.get(n)}, pin budget says "
                          f"GPIO{spec_fw.get(n)}")
    doc_rows = set(re.findall(r"^\| (RP2350|EXP|CM5) (\d+) \| `([A-Z0-9_]+)` \|", pin_doc, re.M))
    spec_rows = {(side, p, e["net"]) for side, t in (("RP2350", rp), ("EXP", ex), ("CM5", cm))
                 for p, e in t.items()}
    for side, p, n in sorted(spec_rows ^ doc_rows):
        where = "PIN_BUDGET.md" if (side, p, n) in spec_rows else "spec_values.pins"
        errors.append(f"{side} GPIO{p} {n} is missing from {where}")
    return errors

FAMILIES = ("REG_", "SD_CMD_", "SD_EVENT_", "SD_ACK_", "SD_STATE_", "SD_OWNER_",
            "SD_FLAG_", "SD_WAKE_")


def names(text, prefixes=FAMILIES):
    found = set()
    for p in prefixes:
        found |= set(re.findall(rf"\b({p}[A-Z0-9_]+)\b", text))
    return found


def main():
    hdr = open(HDR, encoding="utf-8").read()
    doc = open(DOC, encoding="utf-8").read()
    errors = []

    hdr_names = names(hdr)
    doc_names = names(doc)

    for n in sorted(hdr_names - doc_names):
        errors.append(f"{n} defined in solardeck_regs.h but not documented in FIRMWARE_INTERFACE.md")
    for n in sorted(doc_names - hdr_names):
        errors.append(f"{n} documented in FIRMWARE_INTERFACE.md but not defined in solardeck_regs.h")

    # The offsets the doc prints must match the header, or the table is worse than absent.
    hdr_offsets = dict(re.findall(r"#define\s+(REG_[A-Z0-9_]+)\s+0x([0-9A-Fa-f]{2})", hdr))
    for name, off in re.findall(r"\| `0x([0-9A-Fa-f]{2})` \| `(REG_[A-Z0-9_]+)` \|", doc):
        pass  # column order is offset-then-name; handled below
    for off, name in re.findall(r"\| `0x([0-9A-Fa-f]{2})` \| `(REG_[A-Z0-9_]+)` \|", doc):
        if name not in hdr_offsets:
            continue
        if hdr_offsets[name].upper() != off.upper():
            errors.append(f"{name} documented at 0x{off} but defined at 0x{hdr_offsets[name]}")

    errors += pin_errors(open(SPEC, encoding="utf-8").read(), open(STATE_HDR, encoding="utf-8").read(),
                         open(PIN_DOC, encoding="utf-8").read() if os.path.exists(PIN_DOC) else "")

    # Native compile + run of the wire test. Skip loudly if there is no host compiler.
    cc = os.environ.get("CC", "cc")
    with tempfile.TemporaryDirectory() as td:
        exe = os.path.join(td, "test_regs")
        build = subprocess.run(
            [cc, "-std=c11", "-I", os.path.dirname(HDR), "-o", exe, TEST],
            capture_output=True, text=True)
        if build.returncode != 0:
            errors.append(f"test_regs.c does not compile: {build.stderr.strip().splitlines()[:3]}")
        else:
            run = subprocess.run([exe], capture_output=True, text=True)
            if run.returncode != 0:
                errors.append(f"test_regs failed: {run.stdout.strip()} {run.stderr.strip()}")

    if errors:
        for e in errors:
            print(f"   • {e}")
        print(f"   {len(errors)} interface contract failure(s)")
        return 1
    print(f"  {len(hdr_names)} contract symbols agree; pin budget valid; wire test compiles and passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
