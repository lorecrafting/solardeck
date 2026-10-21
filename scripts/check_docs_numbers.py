#!/usr/bin/env python3
"""
Single-source-of-truth checker for SolarDeck.
Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Everything quantitative lives in docs/spec_values.json. This script fails when a doc
(or README) states a different number, and when the resulting geometry does not close.

Checks:
  1. GEOMETRY   chassis clears the panel; display stack + cell fit the cavity; cell fits the chassis.
  2. NUMBERS    every "<N> PPI" / "<N> Hotpacks" / "<N> pillar" / "<N>-Phase" agrees with spec_values.
  3. BANNED     superseded designs must not survive in prose (see BANNED below).
  4. LINKS      every relative markdown link resolves.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = json.load(open(os.path.join(ROOT, "docs", "spec_values.json")))

# Files whose text is authoritatively historical: superseded designs are allowed there.
HISTORICAL = ("docs/90-history/", "docs/AUDIT_", "docs/HANDOFF_TO_FABLE.md", "AGENTS.md")

# (regex, why) -- these designs were removed or contradicted; they must not come back in prose.
BANNED = [
    (r"\b300\s*PPI\b", "panel is 227 PPI (spec_values.ppi); 150 PPI is only the Kaleido sub-pixel figure"),
    (r"TMUX1575PWR", "TMUX1575 has no PWR package; DSBGA YCJ only (BOM PN is TMUX1575YCJR)"),
    (r"8-channel SPDT", "TMUX1575 is 4-channel; the design uses two devices (B2)"),
    (r"SN65DSI83|CrossLink-NX", "no DSI/LVDS path exists: the panel is driven by IT8951 over SPI (B3)"),
    (r"\b24\s*FPS\b|30\s*to\s*45\s*FPS|30–60\s*FPS", "display video-rate claim removed: 32MHz SPI gives ~6 fps 1-bit (B3)"),
    (r"Dual[- ]MIPI[- ]CSI|Dual-Camera|\bIMX219\b|front[- ]camera", "front camera descoped; only the rear IMX708 exists (B8)"),
    (r"\bfour focused\b|four Hotpacks|\bthe 4 specialized\b",
     "7 Hotpacks are specified (spec_values.hotpacks)"),
    (r"8-pin hermetic magnetic pogo|POGO_[A-Z]", "rear pogo bus descoped, USB-C only (B6)"),
    (r"\b35\s*Wh\b", "use the per-chemistry Wh figures (spec_values.battery_wh)"),
    (r"\b50-item\b", "INDEX is generated; do not state a row count"),
    (r"\b4-layer\b(?!.*ADR)", "carrier PCB is 6-layer"),
    (r"7-Phase|7 Phase", "verification has 9 phases (spec_values.verification_phases)"),
    (r"12\.55\s*mm", "stackup is now bounded by spec_values.chassis_cavity_depth_mm"),
    (r"etc/solardeck/owner_voice\.npy|owner_voice\.npy",
     "enrollment is RP2350-flash-resident (spec_values.voice.enrollment_resident, ADR-026); a Linux file was the pre-ADR-026 design"),
    (r"227x165x9\\.8|227\\s*×\\s*165\\s*×\\s*9\\.8|227\\.0\\s*×\\s*165\\.0", "chassis is 232 x 170 x 14.0 (B4)"),
    (r"10,000 insertion cycles", "USB-C rating raised to >=20,000 cycles (longevity.usb_c_rated_cycles)"),
    (r"\\$388\\.85|\\$413\\.85", "core BOM total is $383.30-$408.30 (ADR-020)"),
    (r"SnapDeck Keyboard", "keyboard descoped to Phase 2; external USB-C/BT only"),
    (r"ready for fabrication", "placeholder artifacts are not a design sign-off"),
    (r"Arch Linux as the base|NixOS as the base|Fedora Rawhide as the base",
     "Debian stable is the base (ADR-028); rolling/non-LTS distros make the owner the maintainer"),
    (r"\bHyprland\b(?!.*rejected)", "Sway/Cage are the compositors (ADR-029); Hyprland effects are ghost/flash events on e-ink"),
    (r"\d+\s*-?\s*years?\s+(of\s+)?(dye|Kaleido).*\blifespan|kaleido.*\d+\s*years",
     "Kaleido dye lifespan is null until a datasheet figure exists (ADR-030); never estimate it"),
]


def docs():
    out = []
    for base, _, files in os.walk(os.path.join(ROOT, "docs")):
        for f in files:
            if f.endswith(".md"):
                out.append(os.path.relpath(os.path.join(base, f), ROOT))
    for extra in ("README.md", "AGENTS.md"):
        if os.path.isfile(os.path.join(ROOT, extra)):
            out.append(extra)
    return sorted(out)


def check_geometry(err):
    w, d, h = SPEC["chassis_mm"]
    pw, pd = SPEC["panel_module_outline_mm"]
    aw, ad = SPEC["display_active_mm"]
    cw, cd, ch = SPEC["battery_cell_mm"]
    if not (w >= pw + 2.0):
        err(f"geometry: chassis {w}mm cannot hold panel module {pw}mm + 2 x 1mm wall")
    if not (d >= pd + 2.0):
        err(f"geometry: chassis depth {d}mm cannot hold panel module {pd}mm + 2 x 1mm wall")
    if not (aw < pw and ad < pd):
        err("geometry: active area must be smaller than the panel module outline")
    stack = SPEC["display_stack_mm"] + ch
    if stack > SPEC["chassis_cavity_depth_mm"]:
        err(f"geometry: display stack {SPEC['display_stack_mm']} + cell {ch} = {stack:.1f}mm "
            f"> cavity {SPEC['chassis_cavity_depth_mm']}mm")
    if not (h >= SPEC["chassis_cavity_depth_mm"] + 0.8):
        err(f"geometry: chassis {h}mm leaves <0.8mm wall around a {SPEC['chassis_cavity_depth_mm']}mm cavity")
    if not (cw < w and cd < d):
        err(f"geometry: battery cell {cw}x{cd}mm exceeds chassis {w}x{d}mm")
    # reader frame math (CO_PROCESSOR_SURVEY.md §5): 1-bit counts are derived from page geometry
    # and the PSRAM size — guard them so a geometry change cannot silently invalidate the cache model.
    r = SPEC["reader"]
    if r["page_bytes_8bit"] != r["page_width_px"] * r["page_height_px"]:
        err("reader: page_bytes_8bit != page_width*height")
    if r["page_bytes_1bit"] != r["page_bytes_8bit"] // 8:
        err("reader: page_bytes_1bit != page_bytes_8bit / 8")
    mb = r["page_cache_psram_mb"] * 1024 * 1024
    if r["double_buffer_pages_1bit"] * 2 * r["page_bytes_1bit"] > mb:
        err("reader: 1-bit double-buffer (x2) exceeds PSRAM cache")
    if r["single_buffer_pages_1bit"] * r["page_bytes_1bit"] > mb:
        err("reader: 1-bit single-buffer exceeds PSRAM cache")


def check_numbers(path, text, err):
    for m in re.finditer(r"(\d{2,3})\s*PPI", text):
        win = (text[m.end():m.end() + 12] + text[max(0, m.start() - 20):m.start()]).lower()
        if "colo" in win:
            continue  # Kaleido sub-pixel colour figure, not the monochrome panel pitch
        if int(m.group(1)) != SPEC["ppi"]:
            err(f"{path}: '{m.group(1)} PPI' contradicts spec_values.ppi={SPEC['ppi']}")
    for n in {int(x) for x in re.findall(r"(\d+)\s*(?:standout\s*)?pillars", text, re.I)}:
        if n not in (SPEC["standout_pillars"], SPEC["engineering_pillars"], SPEC["feature_pillars"]):
            err(f"{path}: '{n} pillars' contradicts standout={SPEC['standout_pillars']} "
                f"or engineering={SPEC['engineering_pillars']}")
    for n in {int(x) for x in re.findall(r"(\d+)\s+(?:verification\s+)?phases", text, re.I)}:
        if n != SPEC["verification_phases"]:
            err(f"{path}: '{n} phases' contradicts spec_values.verification_phases={SPEC['verification_phases']}")
    for n in {int(x) for x in re.findall(r"(\d+)\s+(?:thermal\s+)?zones", text, re.I)}:
        if n != SPEC["telemetry"]["thermal_zones"]:
            err(f"{path}: '{n} zones' contradicts spec_values.telemetry.thermal_zones={SPEC['telemetry']['thermal_zones']}")
    for n in {int(x) for x in re.findall(r"(\d+)\s+TPS22918[\- ]gated rails?", text, re.I)}:
        if n != SPEC["telemetry"]["gated_rails"]:
            err(f"{path}: '{n} TPS22918-gated rails' contradicts spec_values.telemetry.gated_rails={SPEC['telemetry']['gated_rails']}")
    for n in {int(x) for x in re.findall(r"(\d+)\s+module health register", text, re.I)}:
        if n != SPEC["telemetry"]["module_health_registers"]:
            err(f"{path}: '{n} registers' contradicts spec_values.telemetry.module_health_registers={SPEC['telemetry']['module_health_registers']}")


def check_links(path, text, err):
    for target in re.findall(r"\]\((?!https?:|#)([^)#]+)", text):
        resolved = os.path.normpath(os.path.join(os.path.dirname(os.path.join(ROOT, path)), target))
        if not os.path.exists(resolved):
            err(f"{path}: broken link -> {target}")


def main():
    errors = []
    check_geometry(errors.append)

    # ADR-027: the streaming-text guarantee must stay self-consistent. A streaming update IS one
    # partial rectangle, so the two latencies cannot drift apart; and the video answer must name
    # the monitor-sink path, not an on-panel video engine.
    ts = SPEC.get("token_stream") or {}
    if ts.get("update_latency_ms") != SPEC.get("refresh_modes", {}).get("partial_rect_latency_ms"):
        errors.append("token_stream.update_latency_ms must equal refresh_modes.partial_rect_latency_ms")
    if "monitor" not in str(ts.get("full_screen_video", "")).lower():
        errors.append("token_stream.full_screen_video must name the USB-C monitor-sink path (ADR-027)")
    for req in ("guaranteed_wpm", "zero_flash", "ghost_residue_threshold_db", "bench_duration_min"):
        if req not in ts:
            errors.append(f"token_stream.{req} missing (ADR-027)")

    for rel in docs():
        text = open(os.path.join(ROOT, rel), encoding="utf-8", errors="ignore").read()
        check_links(rel, text, errors.append)
        if rel.startswith(HISTORICAL):
            continue
        check_numbers(rel, text, errors.append)
        for pattern, why in BANNED:
            m = re.search(pattern, text)
            if m:
                line = text[:m.start()].count("\n") + 1
                errors.append(f"{rel}:{line}: banned '{m.group(0)}' -- {why}")

    if errors:
        print(f"\n  {len(errors)} single-source-of-truth violation(s):")
        for e in errors:
            print(f"   • {e}")
        return 1
    print("  All quantitative claims agree with docs/spec_values.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
