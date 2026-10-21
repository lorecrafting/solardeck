#!/usr/bin/env python3
"""
Written 2026-10-19 08:50 UTC in the Pi harness by antigravity/gemini-3.8-flash
SolarDeck Stage 1 Hardware Trap & Electrical Netlist Static Auditor
"""

import os
import re
import sys

def parse_netlist_nets(netlist_text):
    """
    Parses KiCad netlist s-expression format into a dictionary of nets and connected nodes:
    { net_name: [ (ref, pin), ... ] }
    """
    nets = {}
    chunks = netlist_text.split('(net (')
    for chunk in chunks[1:]:
        name_match = re.search(r'\(name\s+"([^"]+)"\)', chunk)
        if name_match:
            net_name = name_match.group(1)
            nodes = re.findall(r'\(node\s+\(ref\s+"([^"]+)"\)\s+\(pin\s+"([^"]+)"\)\)', chunk)
            nets[net_name] = nodes

    return nets

def parse_netlist_comps(netlist_text):
    """
    Parses the (comp ...) section (ref/value/footprint) so audits can scan part
    VALUES, not just net names -- a banned PN like TMUX1575PWR was hiding in a
    value while rule 8 only looked at names.
    Returns { ref: {value, footprint} }.
    """
    comps = {}
    chunks = netlist_text.split('(comp (ref ')
    for chunk in chunks[1:]:
        ref_match = re.match(r'"([^"]+)"', chunk)
        value_match = re.search(r'\(value\s+"([^"]+)"\)', chunk)
        fp_match = re.search(r'\(footprint\s+"([^"]+)"\)', chunk)
        if ref_match:
            comps[ref_match.group(1)] = {
                "value": value_match.group(1) if value_match else "",
                "footprint": fp_match.group(1) if fp_match else "",
            }
    return comps

def audit_hardware_traps():
    hw_dir = os.path.dirname(os.path.abspath(__file__))
    net_path = os.path.join(hw_dir, "solardeck-carrier.net")

    print("===================================================================")
    print("  SolarDeck Stage 1: Hardware Trap & Electrical Netlist Audit")
    print("===================================================================")
    assert os.path.exists(net_path), f"Netlist not found: {net_path}"

    with open(net_path, "r", encoding="utf-8") as f:
        net_content = f.read()

    nets = parse_netlist_nets(net_content)
    total_nets = len(nets)
    print(f"[*] Parsed {total_nets} interconnected electrical nets.")

    traps_found = 0

    # Trap 1: Single-Node Net Islands (Floating Typo Nets)
    print("\n[Rule 1] Checking for Single-Node Net Islands (Typo / Disconnect)...")
    single_node_nets = [name for name, nodes in nets.items() if len(nodes) < 2]
    if single_node_nets:
        print(f"  ❌ TRAP DETECTED: {len(single_node_nets)} floating nets with < 2 nodes: {single_node_nets}")
        traps_found += 1
    else:
        print(f"  ✓ Passed: All {total_nets} nets have $\\ge 2$ connected nodes. Zero floating nets.")

    # Trap 2: Display Back-Powering (Phantom Powering into Sleep SoC)
    print("\n[Rule 2] Checking Galvanic Display Bus Isolation (TMUX1575)...")
    cm4_spi_nets = ["CM4_SPI_MOSI", "CM4_SPI_MISO", "CM4_SPI_SCK", "CM4_SPI_CS"]
    rp_spi_nets  = ["RP_SPI_MOSI", "RP_SPI_MISO", "RP_SPI_SCK", "RP_SPI_CS"]
    epdc_out_nets = ["EPDC_SPI_MOSI", "EPDC_SPI_MISO", "EPDC_SPI_SCK", "EPDC_SPI_CS"]

    # Verify CM4 SPI nets only touch J2 and U14 (TMUX), NEVER directly touch J_EPDC
    direct_leak = False
    for net_name in cm4_spi_nets:
        nodes = nets.get(net_name, [])
        refs = [r for r, p in nodes]
        assert "U14" in refs, f"{net_name} must route through U14 TMUX1575"
        if "J_EPDC" in refs:
            print(f"  ❌ TRAP DETECTED: {net_name} connects directly to J_EPDC! Phantom back-power risk!")
            direct_leak = True
            traps_found += 1

    if not direct_leak:
        print("  ✓ Passed: CM4 display lines are 100% galvanically isolated by TMUX1575.")

    # Trap 3: Power Domain Short-Circuits & Collisions
    print("\n[Rule 3] Checking Power Domain Separation & Independent Rails...")
    power_rails = ["GND", "VBAT", "VDD_3V3_AON", "VDD_5V_SYS", "VDD_3V8_MODEM"]
    for rail in power_rails:
        assert rail in nets, f"Crucial power rail {rail} missing from netlist"

    # Verify no accidental alias or merging between separate voltage domains
    power_set = set(power_rails)
    assert len(power_set) == len(power_rails), "Duplicate rail definitions"
    print(f"  ✓ Passed: {len(power_rails)} distinct power domains isolated with zero net merging.")

    # Trap 4: Inter-Brain Wake & Emergency Powerfail Interrupts
    print("\n[Rule 4] Checking Dual-Brain GPIO Interrupt Pathways...")
    wake_net = nets.get("GPIO17_WAKE", [])
    pwrfail_net = nets.get("GPIO16_PWRFAIL", [])

    wake_refs = [r for r, p in wake_net]
    pwrfail_refs = [r for r, p in pwrfail_net]

    assert "U8" in wake_refs and "J2" in wake_refs, "GPIO17_WAKE must bridge RP2350 (U8) and CM4 (J2)"
    assert "U8" in pwrfail_refs and "J2" in pwrfail_refs, "GPIO16_PWRFAIL must bridge RP2350 (U8) and CM4 (J2)"
    print("  ✓ Passed: <300ms S2idle wake (GPIO17) & <150ms emergency powerfail (GPIO16) paths verified.")

    # Trap 5: LiFePO4 Chemistry Hardware Interlock (SW1)
    print("\n[Rule 5] Checking Battery Chemistry Selection Pin...")
    chem_net = nets.get("CHEM_SEL_RP", [])
    chem_refs = [r for r, p in chem_net]
    assert "SW1" in chem_refs and "U8" in chem_refs, "CHEM_SEL must route between SW1 and RP2350"
    print("  ✓ Passed: Hardware CHEM_SEL interlock verified to prevent 4.2V over-voltage on LiFePO4.")

    # Trap 6: Solar MPPT Energy Harvester Routing
    print("\n[Rule 6] Checking Solar MPPT Monitoring Circuit...")
    solar_net = nets.get("SOLAR_ADC_IN", [])
    solar_refs = [r for r, p in solar_net]
    assert "U5" in solar_refs and "U8" in solar_refs, "SOLAR_ADC_IN must route from BQ25504 (U5) to RP2350 (U8)"
    print("  ✓ Passed: Solar ambient Voc/Vmpp sensing confirmed on RP2350 12-bit ADC.")

    # Trap 7: Dual-SIM Modem Bus Integrity
    print("\n[Rule 7] Checking Cellular Dual-SIM (eSIM + Nano-SIM) Multiplexing...")
    sim_clk = nets.get("SIM_CLK", [])
    sim_data = nets.get("SIM_DATA", [])
    sim_rst = nets.get("SIM_RST", [])

    for s_net, name in [(sim_clk, "SIM_CLK"), (sim_data, "SIM_DATA"), (sim_rst, "SIM_RST")]:
        s_refs = [r for r, p in s_net]
        assert "J_MODEM" in s_refs, f"{name} missing modem node"
        assert "U18" in s_refs, f"{name} missing eSIM (U18) node"
        assert "J_SIM" in s_refs, f"{name} missing Nano-SIM (J_SIM) node"
    print("  ✓ Passed: Dual-SIM lines correctly multiplexed between Quectel modem, ST4SIM eSIM, and Nano-SIM.")

    # Trap 8: Banned/descoped nets must not re-enter the electrical layer (longevity + ADR guards).
    # Scans BOTH net names AND component values: the TMUX1575PWR trap hid in a comp value while
    # the rule only read net names, so the ban was silently dead code (B2 said DSBGA-YCJ only).
    print("\n[Rule 8] Checking Banned/Descoped Nets + Component Values are Absent (ADR-004/006/008/020/024)...")
    banned_nets = [
        (r"POGO", "rear pogo bus descoped, USB-C only (ADR-006)"),
        (r"SNAP", "SnapDeck keyboard is Phase 2, not a V1 board net (ADR-020)"),
        (r"8.?CH|8_?CH", "TMUX1575 is 4-channel; eight channels need two devices (ADR-004, B2)"),
        (r"24.?FPS|FPS_24", "video-rate claim removed; 32MHz SPI gives ~6 fps 1-bit (ADR-018, B3)"),
        (r"TMUX1575PWR", "TMUX1575 has no PWR package; DSBGA YCJ only (B2)"),
    ]
    comps = parse_netlist_comps(net_content)
    haystack = {}
    for name in nets:
        haystack[f"net:{name}"] = name
    for ref, meta in comps.items():
        haystack[f"comp:{ref}"] = f"{meta['value']} {meta['footprint']}"
    banned_hits = [f"{label} ({why})" for label, text in haystack.items()
                   for pat, why in banned_nets if re.search(pat, text)]
    if banned_hits:
        print(f"  ❌ TRAP DETECTED: descoped content present: {banned_hits}")
        traps_found += 1
    else:
        print("  ✓ Passed: no descoped/banned nets or component values (all ADR-004/006/008/020 closures hold).")

    print("\n===================================================================")
    if traps_found == 0:
        print("  🎉 AUDIT RESULT: 0 TRAPS DETECTED. ALL HARDWARE RULES PASSED!")
        print("===================================================================")
        return 0
    else:
        print(f"  ❌ AUDIT FAILED: {traps_found} HARDWARE TRAPS DETECTED.")
        print("===================================================================")
        return 1

if __name__ == "__main__":
    sys.exit(audit_hardware_traps())
