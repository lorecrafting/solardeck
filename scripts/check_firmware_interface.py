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
          15: {"uart0_rx"}, 18: {"i2s1_sclk"}, 19: {"i2s1_ws"}, 20: {"i2s1_sdi"}, 21: {"i2s1_sdo"}}
# RP1 I2S0 is clock master only, I2S1 is the clock target (CM5 datasheet, peripheral list).
# Ways a net from the always-on RP2350 into the CM5 domain avoids back-powering it. Every driven line
# needs hardware (TMUX or an I_off buffer); firmware tri-stating alone does not survive a hang.
ISOLATION = {"tmux", "buffer", "gate", "rp_input", "od"}


def rp2350_fn_ok(pin, fn):
    """RP2350B GPIO function select (datasheet Table 3), as arithmetic on the pin number."""
    if fn in ("sio", "pio", "pwm"):
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


def pwm_slice(pin):
    """RP2350B PWM slice: GPIO 0-31 wrap slices 0-7, GPIO 32-47 wrap slices 8-11 (datasheet Table 3)."""
    return (pin % 16) // 2 if pin < 32 else 8 + ((pin - 32) // 2) % 4


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
    for side, table in (("RP2350/expander", {**{f"r{k}": v for k, v in rp.items()},
                                             **{f"e{k}": v for k, v in ex.items()}}), ("CM5", cm)):
        nets = [e["net"] for e in table.values()]
        for n in sorted({n for n in nets if nets.count(n) > 1}):
            errors.append(f"{side}: net {n} is assigned to more than one pin")
    for side, table, ok, top in (("RP2350", rp, rp2350_fn_ok, 47),
                                 ("EXP", ex, lambda p, f: f == "gpio", pins["aon_expander_pins"] - 1),
                                 ("CM5", cm, lambda p, f: f == "gpio" or f in CM5_FN.get(p, ()), 27)):
        for pin, e in table.items():
            if not 0 <= int(pin) <= top or not ok(int(pin), e["fn"]):
                errors.append(f"{side} GPIO{pin}: function '{e['fn']}' is not available on that pin "
                              f"(or unverified)")
            if e.get("iso") and e["iso"] not in ISOLATION:
                errors.append(f"{side} GPIO{pin}: unknown isolation '{e['iso']}'")
    # One slice has one counter and divider: two PWM outputs on it cannot run independent waveforms.
    slices = [pwm_slice(int(p)) for p, e in rp.items() if e["fn"] == "pwm"]
    for sl in sorted({x for x in slices if slices.count(x) > 1}):
        errors.append(f"RP2350: two PWM outputs share PWM slice {sl}")
    cm5_nets = {e["net"] for e in cm.values()} | {e["net"] for e in pins["cm5_ctrl"].values()}
    for pin, e in list(rp.items()) + list(ex.items()):
        if e["net"] in cm5_nets and e.get("iso") in (None, "tmux"):
            errors.append(f"RP2350 GPIO{pin} {e['net']} enters the CM5 domain without an isolation rule")
    buffered = sum(e.get("iso") == "buffer" for e in rp.values())
    if buffered > pins["buffer_channels"]:
        errors.append(f"{buffered} buffered lines exceed {pins['buffer_channels']} I_off buffer channels")
    # ADR-055: a TXU0104 has one B-side supply, the CM5 rail; a line into another switched rail needs its own gate.
    for pin, e in list(rp.items()) + list(ex.items()):
        if e.get("iso") == "buffer" and e["net"] not in cm5_nets:
            errors.append(f"GPIO{pin} {e['net']} uses a CM5-rail TXU0104 but does not enter the CM5 domain")
    gates = sum(e.get("iso") == "gate" for e in list(rp.values()) + list(ex.values()))
    if gates != pins["gate_buffers"]:
        errors.append(f"{gates} gated lines, but pins.gate_buffers is {pins['gate_buffers']}")
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
    # Every table column the spec holds must match: net, function, scope, isolation.
    doc_rows = set(re.findall(r"^\| (RP2350|EXP|CM5) (\d+) \| `([A-Z0-9_]+)` \| (\w+) \| (\w+) \| (\w*) \|",
                              pin_doc, re.M))
    spec_rows = {(side, p, e["net"], e["fn"], e["use"].upper(), e.get("iso", ""))
                 for side, t in (("RP2350", rp), ("EXP", ex), ("CM5", cm)) for p, e in t.items()}
    for row in sorted(spec_rows ^ doc_rows):
        where = "PIN_BUDGET.md" if row in spec_rows else "spec_values.pins"
        errors.append(f"{row[0]} GPIO{row[1]} {' / '.join(row[2:])} is missing from {where}")
    return errors

FAMILIES = ("REG_", "SD_CMD_", "SD_EVENT_", "SD_ACK_", "SD_STATE_", "SD_OWNER_",
            "SD_FLAG_", "SD_WAKE_")


def names(text, prefixes=FAMILIES):
    found = set()
    for p in prefixes:
        found |= set(re.findall(rf"\b({p}[A-Z0-9_]+)\b", text))
    return found


def selftest(spec_text, state_hdr, pin_doc):
    """Red controls: each mutation of the real budget must be caught (expected values from the datasheet)."""
    ok = rp2350_fn_ok
    assert ok(40, "adc") and not ok(26, "adc")
    assert ok(20, "uart1_tx") and not ok(20, "uart0_tx") and not ok(22, "uart1_tx") and ok(44, "uart0_tx")
    assert ok(24, "i2c0_sda") and not ok(24, "i2c1_sda") and ok(8, "spi1_rx") and not ok(8, "spi0_rx")
    assert ok(19, "qmi_cs1") and not ok(1, "qmi_cs1")
    assert [pwm_slice(p) for p in (0, 16, 31, 32, 39, 41, 44, 45, 46)] == [0, 0, 7, 8, 11, 8, 10, 10, 11]
    assert pin_errors(spec_text, state_hdr, pin_doc) == []
    for broken in (spec_text.replace('"fn": "spi0_sck"', '"fn": "spi0_tx"', 1),      # wrong SPI role
                   spec_text.replace('"iso": "buffer"', '"iso": "tmux"', 1),          # unisolated line
                   spec_text.replace('"net": "GNSS_PPS"', '"net": "GNSS_EN"'),        # net on two pins
                   spec_text.replace('"46": {\n        "net": "PIEZO"', '"45": {\n        "net": "PIEZO"'),  # pin twice
                   spec_text.replace('"uart1_tx",\n        "use": "v1",\n        "iso": "gate"',
                                     '"uart1_tx",\n        "use": "v1",\n        "iso": "buffer"'),  # GNSS on a CM5-rail TXU0104
                   spec_text.replace('"RADIO_NRESET",\n        "fn": "gpio",\n        "use": "v1",\n        "iso": "gate"',
                                     '"RADIO_NRESET",\n        "fn": "gpio",\n        "use": "v1"')):  # reset back-powers the radio
        assert broken != spec_text and pin_errors(broken, state_hdr, pin_doc)
    assert pin_errors(spec_text, state_hdr.replace("PIN_SOLAR_ADC           40", "PIN_SOLAR_ADC           26"),
                      pin_doc)


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

    pin_inputs = (open(SPEC, encoding="utf-8").read(), open(STATE_HDR, encoding="utf-8").read(),
                  open(PIN_DOC, encoding="utf-8").read() if os.path.exists(PIN_DOC) else "")
    errors += pin_errors(*pin_inputs)
    if not errors:
        selftest(*pin_inputs)

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
