#!/usr/bin/env python3
"""
SolarDeck Master Verification Suite (verify_all.py)
Written 2026-10-20 UTC in the Pi harness by openrouter/deepseek/deepseek-v4.1-flash-1017

Executes the complete verification pipeline. Phase numbering is DERIVED from PHASES below --
never restated by hand in docs, CI, or README (that is how the old 7-vs-9 drift happened).
Every doc that mentions a phase count is checked against docs/spec_values.json by phase 10.

  Phase  1: KiCad schematics + netlist structure, and kicad-cli ERC/DRC when installed
  Phase  2: Netlist electrical trap audit (8 rules)
  Phase  3: RP2350 co-processor firmware contract tests
  Phase  4: Host daemon contract tests (eink-refreshd, solardeck-telemetryd)
  Phase  5: OpenSCAD mechanical envelope
  Phase  6: SMT PCBA & centroid package integrity
  Phase  7: Seeed Studio Fusion turnkey assets
  Phase  8: OS provisioning script (setup_solardeck_os.sh --test)
  Phase  9: Documentation presence and attribution (links are checked in Phase 10)
  Phase 10: Single source of truth (docs/spec_values.json) consistency
  Phase 11: BOM <-> netlist <-> CPL coverage
  Phase 12: Status catalogue (docs/STATUS.md generated and current)
  Phase 13: Longevity constraints (docs/LONGEVITY_30Y.md)
  Phase 14: Derived numbers (BOM total, energy budget) recomputed from artifacts
  Phase 15: Firmware interface contract (header <-> doc <-> wire test) and pin budget (ADR-045)
  Phase 16: Reliability model, obsolescence policy, design-for-test

NOTE: a green run means "the artifacts are internally consistent". It does NOT mean the design is
fabricable -- the schematic is still a partial capture and the production bundles are placeholders.
See docs/AUDIT_6_2026-10-21.md.
"""

import os
import re
import subprocess
import sys
import time
import zipfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def log_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 72}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 72}{Colors.END}")


def run_step(step_name, command):
    t0 = time.time()
    print(f"▶ {Colors.BOLD}{step_name}...{Colors.END} ", end="", flush=True)
    if isinstance(command, list):
        res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        res = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    elapsed = (time.time() - t0) * 1000
    if res.returncode == 0:
        print(f"{Colors.GREEN}[PASS]{Colors.END} ({elapsed:.1f}ms)")
        if res.stdout.strip():
            print(res.stdout.rstrip())
        return True
    print(f"{Colors.RED}[FAIL]{Colors.END} ({elapsed:.1f}ms)")
    print(f"{Colors.RED}STDOUT:\n{res.stdout}{Colors.END}")
    print(f"{Colors.RED}STDERR:\n{res.stderr}{Colors.END}")
    return False


def verify_kicad_cli():
    """ERC/DRC are the only checks that can see a real design error. Skipped without kicad-cli."""
    if not subprocess.run("command -v kicad-cli", shell=True, stdout=subprocess.DEVNULL).returncode == 0:
        strict = os.environ.get("CI") or os.environ.get("SOLARDECK_STRICT")
        msg = ("kicad-cli not installed -- ERC/DRC NOT RUN"
               " (CI installs it; install locally to check before pushing)")
        if strict:
            print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")
            return False
        print(f"{Colors.YELLOW}[SKIP]{Colors.END} {msg}")
        return True

    # kicad-cli subcommand sets differ across releases (e.g. apt kicad 8.0.x exposes
    # only 'sch export'; 'sch erc' appeared later). Probe what THIS install advertises
    # so ERC/DRC run when available and degrade to a loud SKIP otherwise -- never a
    # hard failure caused by a newer KiCad moving a subcommand.
    def advertised(tool):
        res = subprocess.run(["kicad-cli", tool, "--help"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        m = re.search(r"\{([^}]+)\}", res.stdout or "")
        return {s.strip() for s in m.group(1).split(",")} if m else set()

    ok = True
    sch_cmds, pcb_cmds = advertised("sch"), advertised("pcb")
    if "erc" in sch_cmds:
        ok &= run_step("Phase 1b: kicad-cli schematic ERC",
                       "kicad-cli sch erc --severity-error --exit-code-violations hardware/solardeck-carrier.kicad_sch")
    else:
        print(f"{Colors.YELLOW}[SKIP]{Colors.END} kicad-cli sch does not advertise 'erc' (has: {sorted(sch_cmds) or 'none'}); schematic ERC skipped")
    if "drc" in pcb_cmds:
        ok &= run_step("Phase 1c: kicad-cli PCB DRC",
                       "kicad-cli pcb drc --severity-error --exit-code-violations hardware/solardeck-carrier.kicad_pcb")
    else:
        print(f"{Colors.YELLOW}[SKIP]{Colors.END} kicad-cli pcb does not advertise 'drc' (has: {sorted(pcb_cmds) or 'none'}); PCB DRC skipped")
    return ok


def verify_docs_present():
    t0 = time.time()
    print(f"▶ {Colors.BOLD}Phase 9: Documentation presence & attribution (links: Phase 10)...{Colors.END} ", end="", flush=True)
    try:
        assert os.path.isfile("README.md"), "missing README.md"
        docs = []
        for base, _, files in os.walk("docs"):
            docs += [os.path.join(base, f) for f in files if f.endswith(".md")]
        assert len(docs) >= 11, f"expected >= 11 docs, found {len(docs)}"
        for path in docs:
            assert os.path.getsize(path) > 1000, f"{path} too small (<1KB)"
            text = open(path, encoding="utf-8", errors="ignore").read()
            assert re.search(r"Written \d{4}-\d{2}-\d{2}( \d{2}:\d{2})? UTC in .+ by \S+/", text), \
                f"{path} missing 'Written <date> [HH:MM] UTC in <harness> by <provider>/<model>' line"
    except AssertionError as e:
        print(f"{Colors.RED}[FAIL]{Colors.END} ({e})")
        return False
    print(f"{Colors.GREEN}[PASS]{Colors.END} ({(time.time() - t0) * 1000:.1f}ms)")
    return True


def verify_seeed_turnkey():
    t0 = time.time()
    print(f"▶ {Colors.BOLD}Phase 7: Seeed Studio Fusion turnkey assets...{Colors.END} ", end="", flush=True)
    prod = os.path.join(PROJECT_ROOT, "hardware", "production")
    for f in ("solardeck_gerbers.zip", "seeed_fusion_bom.csv", "solardeck_chassis.stl",
              "SEEED_FUSION_BOX_BUILD_INSTRUCTIONS.md"):
        assert os.path.isfile(os.path.join(prod, f)), f"missing {f}"
    with zipfile.ZipFile(os.path.join(prod, "solardeck_gerbers.zip")) as zf:
        names = zf.namelist()
        for r in ("solardeck-carrier-Edge.Cuts.gbr", "solardeck-carrier-F.Cu.gbr",
                  "solardeck-carrier-B.Cu.gbr", "solardeck-carrier.drl"):
            assert r in names, f"gerber zip missing {r}"
    assert os.path.getsize(os.path.join(prod, "solardeck_chassis.stl")) > 1000, "empty STL"
    print(f"{Colors.GREEN}[PASS]{Colors.END} ({(time.time() - t0) * 1000:.1f}ms)")
    return True


FIRMWARE_TEST = ("gcc -Wall -Wextra -I firmware/rp2350/include "
                 "firmware/rp2350/src/solardeck_sm.c firmware/rp2350/test/test_rp2350_sm.c "
                 "-o /tmp/solardeck_test_sm && /tmp/solardeck_test_sm")
REFRESHD_TEST = ("gcc -Wall -Wextra -I src/daemons/eink-refreshd "
                 "src/daemons/eink-refreshd/refreshd.c src/daemons/eink-refreshd/test_refreshd.c "
                 "-o /tmp/solardeck_test_rf && /tmp/solardeck_test_rf")
TELEMETRYD_TEST = ("gcc -Wall -Wextra -I src/daemons/solardeck-telemetryd "
                   "src/daemons/solardeck-telemetryd/telemetryd.c "
                   "src/daemons/solardeck-telemetryd/test_telemetryd.c "
                   "-o /tmp/solardeck_test_telemetryd && /tmp/solardeck_test_telemetryd")

# The pipeline. Order is the numbering.
PHASES = [
    ("KiCad schematics & netlist structure",
     lambda: run_step("Phase 1: KiCad schematics & netlist", [sys.executable, "hardware/verify_schematics.py"])
     and verify_kicad_cli()),
    ("Netlist electrical trap audit (8 rules)",
     lambda: run_step("Phase 2: Netlist electrical trap audit (8 rules)", [sys.executable, "hardware/audit_hardware_traps.py"])),
    ("RP2350 co-processor firmware contract tests",
     lambda: run_step("Phase 3: RP2350 firmware contract tests", FIRMWARE_TEST)),
    ("Host daemon contract tests",
     lambda: run_step("Phase 4a: eink-refreshd cadence + §52 scheduler contract", REFRESHD_TEST)
     and run_step("Phase 4b: solardeck-telemetryd bridge contract (CRC-8 & JSON)", TELEMETRYD_TEST)),
    ("OpenSCAD mechanical envelope",
     lambda: run_step("Phase 5: OpenSCAD mechanical envelope", [sys.executable, "hardware/enclosure/verify_enclosure.py"])),
    ("SMT PCBA & centroid package integrity",
     lambda: run_step("Phase 6: SMT PCBA & centroid package", [sys.executable, "hardware/production/verify_manufacturing_package.py"])),
    ("Seeed Studio Fusion turnkey assets", verify_seeed_turnkey),
    ("OS provisioning script",
     lambda: run_step("Phase 8: OS provisioning (setup_solardeck_os.sh --test)", ["bash", "tools/provision/setup_solardeck_os.sh", "--test"])),
    ("Documentation presence & attribution", verify_docs_present),
    ("Single source of truth consistency",
     lambda: run_step("Phase 10: single source of truth (spec_values.json)", [sys.executable, "scripts/check_docs_numbers.py"])),
    ("BOM <-> netlist <-> CPL coverage",
     lambda: run_step("Phase 11: BOM <-> netlist <-> CPL coverage", [sys.executable, "scripts/check_bom_coverage.py"])),
    ("Status catalogue generated and current",
     lambda: run_step("Phase 12: feature status catalogue (docs/STATUS.md)", [sys.executable, "scripts/gen_status.py", "--check"])),
    ("30-year longevity constraints enforced",
     lambda: run_step("Phase 13: longevity constraints (docs/LONGEVITY_30Y.md)", [sys.executable, "scripts/check_longevity.py"])),
    ("Derived numbers: BOM total and energy budget",
     lambda: run_step("Phase 14: derived numbers (BOM + power)", [sys.executable, "scripts/check_cost_and_power.py"])),
    ("CM5 <-> RP2350 interface contract",
     lambda: run_step("Phase 15: firmware interface contract", [sys.executable, "scripts/check_firmware_interface.py"])),
    ("Reliability model + obsolescence + DFT",
     lambda: run_step("Phase 16: reliability, obsolescence, design-for-test", [sys.executable, "scripts/check_reliability_and_supply.py"])),
]


def verify_pipeline_metadata():
    """AUDIT 5 fixes A/B: the docstring phase list and the CI workflow job name must not drift
    from the real PHASES list (that is how the old 7-vs-9 / 11-vs-16 drift happened twice)."""
    t0 = time.time()
    print(f"▶ {Colors.BOLD}Phase metadata consistency (docstring + CI name)...{Colors.END} ", end="", flush=True)
    try:
        expected = list(range(1, len(PHASES) + 1))
        nums = [int(x) for x in re.findall(r"Phase\s+(\d+):", __doc__ or "")]
        assert nums == expected, f"docstring phase list {nums} != {expected}"
        yml = open(os.path.join(PROJECT_ROOT, ".github/workflows/verify.yml"), encoding="utf-8").read()
        m = re.search(r"(\d+)-Phase System Verification", yml)
        assert m and int(m.group(1)) == len(PHASES), \
            f"workflow job name phase count != {len(PHASES)}"
    except AssertionError as e:
        print(f"{Colors.RED}[FAIL]{Colors.END} ({e})")
        return False
    print(f"{Colors.GREEN}[PASS]{Colors.END} ({(time.time() - t0) * 1000:.1f}ms)")
    return True


def main():
    log_header("SOLARDECK MASTER VERIFICATION PIPELINE")
    t_start = time.time()
    if not verify_pipeline_metadata():
        return 1
    failures = []
    for i, (label, fn) in enumerate(PHASES, 1):
        try:
            ok = fn()
        except Exception as e:
            print(f"{Colors.RED}[FAIL]{Colors.END} Phase {i} raised: {e}")
            ok = False
        if not ok:
            failures.append(f"Phase {i}: {label}")

    total_time = (time.time() - t_start) * 1000
    print(f"\n{Colors.BOLD}{'=' * 72}{Colors.END}")
    if not failures:
        print(f"{Colors.BOLD}{Colors.GREEN}  ✅ ALL {len(PHASES)} PHASES PASSED IN {total_time:.1f}ms{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}  Artifacts are internally consistent -- NOT a design sign-off.{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}  Schematic is a partial capture; production bundles are placeholders.{Colors.END}")
        print(f"{Colors.BOLD}{Colors.YELLOW}  See docs/AUDIT_6_2026-10-21.md before ordering anything.{Colors.END}")
        print(f"{Colors.BOLD}{'=' * 72}{Colors.END}\n")
        return 0
    print(f"{Colors.BOLD}{Colors.RED}  ❌ {len(failures)} OF {len(PHASES)} PHASE(S) FAILED!{Colors.END}")
    for f in failures:
        print(f"   • {f}")
    print(f"{Colors.BOLD}{'=' * 72}{Colors.END}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
