#!/usr/bin/env python3
"""
Phase 15: the CM4 <-> RP2350 contract cannot drift.

Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

The header is the contract; docs/FIRMWARE_INTERFACE.md is the readable copy. This check is
bidirectional, so neither can silently gain a register the other does not know about:

  1. every `REG_*` in the header is documented, and every `REG_*` in the doc exists in the header
  2. every SD_CMD_/SD_EVENT_/SD_ACK_/SD_STATE_ constant used by the doc exists in the header
  3. the wire test compiles and passes natively (the layout asserts are compile-time; CRC is not)

A one-directional check would let a developer add a register to the header and ship firmware the CM4
driver never reads -- which is the exact class of bug this file exists to prevent.
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDR = os.path.join(ROOT, "firmware", "rp2350", "include", "solardeck_regs.h")
DOC = os.path.join(ROOT, "docs", "FIRMWARE_INTERFACE.md")
TEST = os.path.join(ROOT, "firmware", "rp2350", "test", "test_regs.c")

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
    print(f"  {len(hdr_names)} contract symbols agree; wire test compiles and passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
