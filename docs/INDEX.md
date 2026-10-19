# Master Documentation Index & Architectural Map — SolarDeck

Written 2026-10-18 18:28 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Documentation Structure & Reading Order

The SolarDeck repository contains comprehensive, mathematically verified specifications governing every aspect of the system. Documents should be reviewed in the following recommended order:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK DOCUMENTATION HIERARCHY                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. README.md                                                                │
│    • Executive overview, core personas, specs table, and elevator pitches.  │
│                                                                             │
│ 2. docs/STANDOUT_FEATURES.md                                                │
│    • The 5 non-negotiable engineering North Stars to hammer in on:          │
│      Dual-Brain Handoff, Typewriter Latency, Sunlight Sovereignty,         │
│      Universal Form-Morphology, and Sovereign Field Hardening.             │
│                                                                             │
│ 3. docs/MVP_ARCHITECTURE.md                                                 │
│    • High-level system architecture, user workflows, 4 operating postures,  │
│      subsystem block diagrams, and day-in-the-life operational timelines.   │
│                                                                             │
│ 4. docs/HARDWARE_SPEC.md                                                    │
│    • Carrier board schematics, bus topologies, power rails, IC pinouts,     │
│      RF design, mechanical tolerances, and Zero-Brick hardware safeguards.  │
│                                                                             │
│ 5. docs/SOFTWARE_SPEC.md                                                    │
│    • Linux kernel DRM/KMS drivers, custom daemons (eink-refreshd, inkd,     │
│      telemetryd), Wayland configurations, voice/vision AI pipelines, and   │
│      Zero-Brick A/B firmware update protocols.                             │
│                                                                             │
│ 6. docs/BOM_COST_ESTIMATE.md                                                │
│    • Complete, turnkey Bill of Materials: 60 core line items ($389–$414),   │
│      supplier part numbers, distributor links, and turnkey assembly costs.  │
│                                                                             │
│ 7. docs/HARDWARE_VERIFICATION_WORKFLOW.md                                   │
│    • 5-Stage Zero-Brick verification ladder: static netlist trap auditor,   │
│      SPICE power transient simulation, Renode/QEMU co-simulation, and DRC.  │
│                                                                             │
│ 8. docs/OFFGRID_TACTICAL_SENSORS.md                                         │
│    • Campervan BLE/CAN/RS485 integration, 9-DOF IMU celestial navigation,   │
│      RTK/Galileo HAS, doomsday radio/dosimeter/wild-power hardening, and    │
│      offline local RAG knowledgebase traversal.                             │
│                                                                             │
│ 9. docs/MECHANICAL_FIT_AND_ENCLOSURE_WORKFLOW.md                     │
│    • 4-Step mechanical fit pipeline: Good Display 3D STEP import,    │
│      KiCad 3D board export, tolerance budget (+0.4mm XY, 12.55mm Z), │
│      and Two-Tier Sanity Check (1:1 paper DXF + $15 3D-printed fit). │
│                                                                             │
│ 10. docs/HANDOFF_TO_FABLE.md                                                │
│    • Comprehensive engineering handover for Fable Wednesday audit: Seeed    │
│      quotation status, 7-phase verification pipeline, and review checklist. │
│                                                                             │
│ 11. AGENTS.md                                                               │
│    • Developer & AI agent instructions, coding discipline, and safety rules.│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Subsystem Cross-Reference Map

| Subsystem | Primary Specification | Hardware Controller | Key Interface |
| :--- | :--- | :--- | :--- |
| **Main Compute Brain** | `docs/HARDWARE_SPEC.md` §2.1 | Broadcom BCM2711 (CM4) | Hirose DF40 100-pin Dual Socket |
| **Co-Processor Nervous System** | `docs/HARDWARE_SPEC.md` §2.1 | Raspberry Pi RP2350B | Dedicated SPI, UART, & GPIO |
| **Display & Digitizer** | `docs/HARDWARE_SPEC.md` §2.2 | ITE IT8951 + Wacom EMR | 32 MHz SPI via TMUX1575 Switch |
| **Power Management & Solar** | `docs/HARDWARE_SPEC.md` §2.3 | TI BQ25895 + TI TPS62840 | I2C / Dynamic MPPT Tracking |
| **USB Host / Peripherals** | `docs/HARDWARE_SPEC.md` §2.4 | VIA VL805 / ASM1042A | PCIe Gen 2 x1 to Quad USB 2.0 |
| **Cellular, GNSS & Dual-SIM** | `docs/HARDWARE_SPEC.md` §2.5 | Quectel EG25-G (LTE Cat-4) | USB 2.0 + Dual SIM (MFF2 + Nano) |
| **Off-Grid Radio Mesh** | `docs/HARDWARE_SPEC.md` §2.5 | Semtech SX1262 (LoRa) | Dedicated SPI to RP2350 (Meshtastic) |
| **Local NFC & Security** | `docs/HARDWARE_SPEC.md` §2.5 | STMicroelectronics ST25R3916 | SPI / I2C (13.56 MHz NFC-A/B/V) |
| **Audio & Speech Input** | `docs/HARDWARE_SPEC.md` §2.7 | Knowles MEMS + MAX98357A | PDM Dual-Mic + I2S Class-D Amp |
| **Secondary Monitor Sink** | `docs/HARDWARE_SPEC.md` §2.4 | BCM2711 Native OTG PHY | USB-C Port 1 (`g_webcam` / `dummy_hcd`)|
| **Universal Mechanical Mount** | `docs/HARDWARE_SPEC.md` §3 | M2.5 Threaded + MagSafe | Mechanical Heat-Set & N52 Magnets |
| **EDC Phone & Cyberdeck Dock** | `docs/STANDOUT_FEATURES.md` §9 | Clicks Communicator / Jelly| Bluetooth PAN (`bnep0`) & Chin-Dock |
| **External 4K Video & Campervan Dock**| `docs/HARDWARE_SPEC.md` §2.18 | CM4 HDMI0 + TPD4E05U06 | Micro-HDMI 4K60 / Sway Multi-Head |
| **Blackout Supercap Emergency Beacon** | `docs/HARDWARE_SPEC.md` §2.19 | 1.0F Supercap + RP2350 | Bat-Free Solar Cold-Boot & LoRa SOS|
| **Sovereign Voice & Barge-In Pipeline**| `docs/HARDWARE_SPEC.md` §2.20 | Knowles MEMS + RP2350/NDP120 | microWakeWord + Resemblyzer + AEC |
| **Zero-Hardware Wacom Field Caliper** | `docs/HARDWARE_SPEC.md` §2.21 | Wacom EMR + Goodix Touch | 10mm Hover + Mutual Cap Centroid |
| **Thermal Night-Vision Hotpack** | `docs/OFFGRID_TACTICAL_SENSORS.md` §8.7| InfiRay Tiny1-C (256x192 LWIR) | USB-C Port 2 / GPU 16-shade Dither |
| **3GPP NTN Satellite Skylo Hotpack** | `docs/OFFGRID_TACTICAL_SENSORS.md` §8.8| Quectel CC660D-LS (IoT-NTN) | USB-C Port 2 / S-Band RHCP Patch |
| **Off-Grid & Tactical Sensors**| `docs/OFFGRID_TACTICAL_SENSORS.md` | Dual Brain (CM4 + RP2350) | BLE, SocketCAN, 9-DOF IMU, RTK, RAG |
| **Dual-Footprint & DNP Architecture** | `docs/HARDWARE_SPEC.md` §2.22 | 8 Strategic Fallback Footprints| NDP120, RV-3028, WSON-8, CH224K, PCIe|
| **Autonomous LLM Hardware BIST Engine**| `docs/SOFTWARE_SPEC.md` §21 | `solardeck-diag --json` | 8-Subsystem BIST & Power-Gated Heal|
| **30-Year Zero-Failure & Hi-Rel HW** | `docs/HARDWARE_SPEC.md` §7 | 5 Hi-Rel Rules + Escape Hatches | 50% Derate, Soft-Term MLCC, GDT, E-Fuse|
| **Cold Storage Vault** | `docs/HARDWARE_SPEC.md` §4.2 | 3x MicroSD Slots + SIM Tool | Spring-latch Retention Pockets |

---

## 3. Legacy Pruning & Historical Decision Record

For engineering posterity, the following major design iterations and descoping decisions were executed during the architectural refinement process:

1. **Descoped Standalone GPS Module (-$17.00 BOM):**
   * *Original Plan:* Dedicated u-blox MAX-M10S GNSS receiver.
   * *Decision:* The Quectel EG25-G LTE modem already integrates an automotive-grade Qualcomm multi-constellation GNSS engine (GPS, GLONASS, BeiDou, Galileo). Eliminating the standalone chip pruned $17.00 in BOM and eliminated RF board trace interference.
2. **Descoped Front Camera & Sliding Shutter (-$8.50 BOM):**
   * *Original Plan:* Front 5MP OmniVision OV5647 camera with mechanical ThinkShutter.
   * *Decision:* Video calls are poor on E-Ink due to refresh physics. Eliminating the front camera preserved IP67 water sealing, removed MIPI CSI-2 high-speed trace noise, and freed the top bezel for solar harvesting. Retained the flush rear 12MP Sony IMX708 PDAF camera for paper document and whiteboard capture.
3. **Descoped Dedicated Lux Sensor (-$1.10 BOM):**
   * *Original Plan:* Dedicated TI OPT3001 digital ambient light sensor.
   * *Decision:* The top-bezel monocrystalline solar strip functions natively as a large-area photodiode. Sampling solar open-circuit voltage via the RP2350's 12-bit ADC provides a continuous 0 to 100,000 lux ambient light meter with zero added components.
4. **Descoped Custom SnapDeck Scissor Keyboard (-$32.65 BOM, -$25k Tooling):**
   * *Original Plan:* Proprietary 5-pin magnetic pogo keyboard with custom Kailh X-switches and CNC aluminum chassis.
   * *Decision:* Descoping from V1 eliminated $25,000+ in custom injection molds and 6 months of mechanical/ZMK bring-up. The tablet provides Universal M2.5 Threaded Inserts and a MagSafe Magnetic Array, opening it to any standard Bluetooth/USB-C keyboard or an open-source 3D-printed $20 BlackBerry Q20 handheld thumb keyboard.
5. **Descoped Internal Metal Kickstand (-$8.00 BOM, -150g Weight):**
   * *Original Plan:* Internal folding friction-hinge metal kickstand.
   * *Decision:* Friction hinges fatigue and leak water under IP67 submersion. Replaced with the flush M.2 Service Hatch containing the Cold Storage Vault (3x MicroSD card slots + SIM ejector tool). Tablet props up on any MagSafe desk stand, camera tripod, or stylus kickstand wedge.
6. **Descoped Custom Flipper Zero Clone Module (-$24.00 BOM):**
   * *Original Plan:* Proprietary RF backpack integrating CC1101 Sub-GHz, 125 kHz RFID coil, and Vishay IR emitters.
   * *Decision:* Redundant over-engineering. An actual Flipper Zero already has its own battery, screen, and mature open-source firmware. Operators simply mount their physical Flipper Zero via rear M2.5 inserts or MagSafe and plug it into USB-C Port 2 or Bluetooth, controlling it via `qflipper-cli` on SolarDeck's 10.3" screen.
7. **Descoped Fragile Spring-Loaded Pogo Pin Expansion Bus:**
   * *Original Plan:* 8-pin hermetic magnetic pogo bus on rear chassis.
   * *Decision:* Pogo pins corrode, pit, and mechanically jam when exposed to beach sand, volcanic dust, or salt spray. Replaced with a recessed right-angle plug into IP68-sealed USB-C Port 2 (High-Speed Host) secured by the MagSafe ring and 4x M2.5 threaded brass inserts.
8. **Descoped Integrated Solar Smart Cover (Thermal Safety):**
   * *Original Plan:* Bi-folding solar cover attached directly to the tablet face.
   * *Decision:* In direct tropical sun (Hawaii/Arizona), dark unibody surfaces bake to >+70°C. E-Ink microcapsules permanently degrade above +60°C, and LiFePO4 charging must terminate above +45°C. Prescribed a detached 15W–28W folding USB-C panel placed in direct sun, connected via a 3-meter cable to SolarDeck resting safely in ambient shade.
9. **Solid-State Electronic E-Fuses & 3-Stage Surge Suppression Over Consumable Fuses:**
   * *Original Plan:* Sacrificial melting fuses and standalone single-stage TVS diodes.
   * *Decision:* Consumable fuses melt once and require factory desoldering. Lone TVS diodes burn up under sustained lightning or high-energy static discharges. Upgraded to **TI TPS259xx electronic e-fuses** (500ns trip & auto-retry) and a **3-stage cascaded transient filter (GDT + choke + TVS)**, eliminating diode burnout while providing zero-cost 0.2mm sacrificial trace notches and `SJ1`–`SJ8` solder-bridge bypasses as field escape hatches.

---

## 4. Hardware Safety & Power Discipline Check

* **LiFePO4 Chemistry Discipline:** Nominal cell voltage is **3.2V** (3.65V charging cutoff). Never apply 4.2V Li-ion charging profiles.
* **Always-On Rail Isolation:** The **TI TPS62840** buck-boost regulator maintains 3.3V power to the RP2350 and critical sensors when the CM4 5V system boost is disabled.
* **Galvanic Display Bus Isolation:** The **TI TMUX1575** 8-channel bus switch ensures zero parasitic back-powering from unpowered CM4 GPIO pins into the IT8951 display controller during Zen reading.
* **Airgap Series Disconnect:** The physical airgap slide switch disconnects power gate enable nets in series, preventing direct GPIO-to-ground short circuits.

---

## 5. Master Automated Verification Suite & CI Pipeline

To verify every hardware rule, firmware state transition, cadence timing, and 3D mechanical dimension in a single command before submitting fabrication orders:

* **Unified CLI Runner:**
  ```bash
  python3 scripts/verify_all.py
  ```
  Executes all 7 verification phases in ~1.0 second with colored pass/fail status and timing metrics.
* **Continuous Integration:** `.github/workflows/verify.yml` automatically triggers on every push and pull request to `main`.
* **Turnkey Box-Build Package:** `hardware/production/` houses the complete, validated manufacturing bundle for Seeed Studio Fusion (`solardeck_gerbers.zip`, `seeed_fusion_bom.csv`, `solardeck_cpl.csv`, `solardeck_chassis.stl`, and `SEEED_FUSION_BOX_BUILD_INSTRUCTIONS.md`).

---

*End of Index.*
