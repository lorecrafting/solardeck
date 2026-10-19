#!/usr/bin/env python3
"""
SolarDeck Master Verification Suite (verify_all.py)
Written 2026-10-19 UTC in the Pi harness by antigravity/gemini-3.8-flash

Executes the complete 7-Phase Verification Pipeline covering:
  Phase 1: Track A KiCad Schematics & Netlist Structure
  Phase 2: Hardware Trap & Electrical Integrity Audit (7 Rules)
  Phase 3: Track B RP2350 C Firmware Host Assert Tests (<300ms S2idle)
  Phase 4: Track B eink-refreshd Cadence Daemon Host Assert Tests (<800ms Lock)
  Phase 5: Track C Mechanical Enclosure Envelope (227x165x9.8mm IP67)
  Phase 6: SMT PCBA & Centroid Package Integrity (BOM / CPL / 6-Layer Layout)
  Phase 7: Seeed Studio Fusion Turnkey Fabrication Package & Box-Build Assets
"""

import os
import sys
import subprocess
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
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def log_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*72}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*72}{Colors.END}")

def run_step(step_name, command, cwd=PROJECT_ROOT):
    t0 = time.time()
    print(f"▶ {Colors.BOLD}{step_name}...{Colors.END} ", end="", flush=True)
    if isinstance(command, list):
        res = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    else:
        res = subprocess.run(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    elapsed = (time.time() - t0) * 1000
    if res.returncode == 0:
        print(f"{Colors.GREEN}[PASS]{Colors.END} ({elapsed:.1f}ms)")
        return True, res.stdout
    else:
        print(f"{Colors.RED}[FAIL]{Colors.END} ({elapsed:.1f}ms)")
        print(f"{Colors.RED}STDOUT:\n{res.stdout}{Colors.END}")
        print(f"{Colors.RED}STDERR:\n{res.stderr}{Colors.END}")
        return False, res.stderr

def verify_seeed_turnkey():
    t0 = time.time()
    print(f"▶ {Colors.BOLD}Verifying Seeed Studio Fusion Turnkey Assets...{Colors.END} ", end="", flush=True)
    
    gerber_zip = os.path.join(PROJECT_ROOT, "hardware", "production", "solardeck_gerbers.zip")
    seeed_bom = os.path.join(PROJECT_ROOT, "hardware", "production", "seeed_fusion_bom.csv")
    seeed_stl = os.path.join(PROJECT_ROOT, "hardware", "production", "solardeck_chassis.stl")
    seeed_doc = os.path.join(PROJECT_ROOT, "hardware", "production", "SEEED_FUSION_BOX_BUILD_INSTRUCTIONS.md")
    
    assert os.path.isfile(gerber_zip), f"Missing {gerber_zip}"
    with zipfile.ZipFile(gerber_zip, 'r') as zf:
        names = zf.namelist()
        required = ["solardeck-carrier-Edge_Cuts.gbr", "solardeck-carrier-F_Cu.gbr", "solardeck-carrier-B_Cu.gbr", "solardeck-carrier-PTH.drl"]
        for r in required:
            assert r in names, f"Gerber zip missing {r}"
            
    assert os.path.isfile(seeed_bom), f"Missing {seeed_bom}"
    with open(seeed_bom, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
        assert len(lines) >= 24, f"BOM expected >= 24 lines, found {len(lines)}"
        
    assert os.path.isfile(seeed_stl) and os.path.getsize(seeed_stl) > 1000, "Missing or empty STL"
    assert os.path.isfile(seeed_doc), f"Missing {seeed_doc}"
    
    elapsed = (time.time() - t0) * 1000
    print(f"{Colors.GREEN}[PASS]{Colors.END} ({elapsed:.1f}ms)")
    return True

def main():
    log_header("SOLARDECK V1 MASTER SYSTEM VERIFICATION WORKFLOW")
    t_start = time.time()
    failures = []

    # Phase 1: Track A KiCad Schematics
    ok, _ = run_step(
        "Phase 1: KiCad 8 Schematics & Netlist Structure",
        [sys.executable, "hardware/verify_schematics.py"]
    )
    if not ok: failures.append("Phase 1: KiCad Schematics")

    # Phase 2: Hardware Trap Audit
    ok, _ = run_step(
        "Phase 2: Netlist Electrical Trap Audit (7 Rules)",
        [sys.executable, "hardware/audit_hardware_traps.py"]
    )
    if not ok: failures.append("Phase 2: Hardware Trap Audit")

    # Phase 3: Track B RP2350 Firmware Assert Tests
    cmd_test_firmware = (
        "gcc -Wall -Wextra -I firmware/rp2350/include "
        "firmware/rp2350/src/solardeck_sm.c firmware/rp2350/test/test_rp2350_sm.c "
        "-o /tmp/solardeck_test_sm && /tmp/solardeck_test_sm"
    )
    ok, _ = run_step(
        "Phase 3: RP2350 Co-Processor Firmware Assert Test (<300ms S2idle)",
        cmd_test_firmware
    )
    if not ok: failures.append("Phase 3: RP2350 Firmware")

    # Phase 4: Track B Daemons (eink-refreshd & solardeck-telemetryd)
    cmd_test_daemon = (
        "gcc -Wall -Wextra -I src/daemons/eink-refreshd "
        "src/daemons/eink-refreshd/refreshd.c src/daemons/eink-refreshd/test_refreshd.c "
        "-o /tmp/solardeck_test_rf && /tmp/solardeck_test_rf"
    )
    ok, _ = run_step(
        "Phase 4a: eink-refreshd Cadence Daemon Assert Test (<800ms Lockout)",
        cmd_test_daemon
    )
    if not ok: failures.append("Phase 4a: eink-refreshd Daemon")

    cmd_test_telemetryd = (
        "gcc -Wall -Wextra -I src/daemons/solardeck-telemetryd "
        "src/daemons/solardeck-telemetryd/telemetryd.c src/daemons/solardeck-telemetryd/test_telemetryd.c "
        "-o /tmp/solardeck_test_telemetryd && /tmp/solardeck_test_telemetryd"
    )
    ok, _ = run_step(
        "Phase 4b: solardeck-telemetryd Co-Processor Bridge Assert Test (CRC-8 & JSON)",
        cmd_test_telemetryd
    )
    if not ok: failures.append("Phase 4b: solardeck-telemetryd Daemon")

    # Phase 5: Track C Mechanical Enclosure
    ok, _ = run_step(
        "Phase 5: OpenSCAD Mechanical Envelope (227x165x9.8mm IP67)",
        [sys.executable, "hardware/enclosure/verify_enclosure.py"]
    )
    if not ok: failures.append("Phase 5: Mechanical Enclosure")

    # Phase 6: SMT PCBA & Centroid Package
    ok, _ = run_step(
        "Phase 6: SMT PCBA & Centroid Package Integrity",
        [sys.executable, "hardware/production/verify_manufacturing_package.py"]
    )
    if not ok: failures.append("Phase 6: SMT Manufacturing Package")

    # Phase 7: Seeed Fusion Turnkey Package
    try:
        if not verify_seeed_turnkey():
            failures.append("Phase 7: Seeed Studio Turnkey Package")
    except Exception as e:
        print(f"{Colors.RED}[FAIL]{Colors.END} ({e})")
        failures.append(f"Phase 7: Seeed Studio Turnkey Package ({e})")

    total_time = (time.time() - t_start) * 1000
    print(f"\n{Colors.BOLD}{'='*72}{Colors.END}")
    if not failures:
        print(f"{Colors.BOLD}{Colors.GREEN}  🎉 ALL 7 VERIFICATION PHASES PASSED IN {total_time:.1f}ms!{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}  SolarDeck V1 is mathematically & structurally ready for fabrication.{Colors.END}")
        print(f"{Colors.BOLD}{'='*72}{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.BOLD}{Colors.RED}  ❌ {len(failures)} VERIFICATION PHASE(S) FAILED!{Colors.END}")
        for f in failures:
            print(f"   • {f}")
        print(f"{Colors.BOLD}{'='*72}{Colors.END}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
