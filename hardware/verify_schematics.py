#!/usr/bin/env python3
"""
Written 2026-10-19 08:20 UTC in the Pi harness by antigravity/gemini-3.8-flash
Verification check for Track A (KiCad Schematics and Netlist)
"""

import os
import re
import sys

def verify_kicad_project():
    hw_dir = os.path.dirname(os.path.abspath(__file__))
    pro_path = os.path.join(hw_dir, "solardeck-carrier.kicad_pro")
    root_sch = os.path.join(hw_dir, "solardeck-carrier.kicad_sch")
    net_path = os.path.join(hw_dir, "solardeck-carrier.net")

    subsheets = [
        "power.kicad_sch",
        "compute.kicad_sch",
        "display.kicad_sch",
        "io.kicad_sch"
    ]

    print("[Track A Check] Verifying KiCad 8 Project Files...")
    assert os.path.exists(pro_path), f"Missing {pro_path}"
    assert os.path.exists(root_sch), f"Missing {root_sch}"
    assert os.path.exists(net_path), f"Missing {net_path}"

    for sheet in subsheets:
        full_path = os.path.join(hw_dir, sheet)
        assert os.path.exists(full_path), f"Missing sub-sheet {sheet}"
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "(kicad_sch" in content, f"Invalid format in {sheet}"

    # Verify Root Schematic References all 4 Sheets
    with open(root_sch, "r", encoding="utf-8") as f:
        root_content = f.read()
        for sheet in subsheets:
            assert sheet in root_content, f"Root schematic does not reference {sheet}"

    # Verify Netlist Components & Nets
    with open(net_path, "r", encoding="utf-8") as f:
        net_content = f.read()

    core_components = [
        ("U1", "BQ25895RTWR"),
        ("U2", "TPS62840DLYR"),
        ("U3", "TPS61088RHLR"),
        ("U4", "TPS63020DSJR"),
        ("U5", "BQ25504RGTR"),
        ("J1", "DF40C-100DS-0.4V"),
        ("J2", "DF40C-100DS-0.4V"),
        ("U8", "RP2350B"),
        ("U9", "APS6404L-3SQR-SN"),
        ("U10", "W25Q128JVS"),
        ("U11", "DS3231MZ+"),
        ("U14", "TMUX1575YCJR"),
        ("J_EPDC", "IT8951_FPC40"),
        ("U16", "VL805-Q6"),
        ("J_NVME", "M.2_Key-M_2242"),
        ("J_MODEM", "Quectel_EG25-G_M.2"),
        ("U18", "ST4SIM-200M")
    ]

    for ref, val in core_components:
        assert f'(ref "{ref}")' in net_content, f"Component {ref} missing in netlist"
        assert val in net_content, f"Value {val} for {ref} missing in netlist"

    core_nets = [
        "VBAT",
        "VDD_3V3_AON",
        "VDD_5V_SYS",
        "VDD_3V8_MODEM",
        "GPIO17_WAKE",
        "GPIO16_PWRFAIL",
        "TMUX_SEL_CM5_NRP",
        "EPDC_SPI_MOSI",
        "EPDC_SPI_SCK",
        "PCIE_TX_P",
        "PCIE_RX_P",
        "USB_MODEM_DP"
    ]

    for net in core_nets:
        assert f'(name "{net}")' in net_content, f"Net {net} missing in netlist"

    print("✓ Track A Verification Passed: All 5 KiCad schematics and netlists structurally verified.")

if __name__ == "__main__":
    verify_kicad_project()
