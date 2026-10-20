# Master Documentation Index & Architectural Map — SolarDeck

Written 2026-10-18 18:28 UTC in the Pi harness by antigravity/gemini-3.8-flash

---

## 1. Documentation Structure & Reading Order

The SolarDeck repository contains comprehensive architectural specifications. Every number in
these docs resolves to `docs/spec_values.json` (checked by `scripts/check_docs_numbers.py`);
treat `docs/AUDIT_2026-10-20.md` as the current statement of what is measured, modelled or aspirational. governing every aspect of the system. Documents should be reviewed in the following recommended order:

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
│      KiCad 3D board export, tolerance budget (+0.4mm XY, 13.85mm Z), │
│      and Two-Tier Sanity Check (1:1 paper DXF + $15 3D-printed fit). │
│                                                                             │
│ 10. docs/HANDOFF_TO_FABLE.md                                                │
│    • Comprehensive engineering handover for Fable Wednesday audit: Seeed    │
│      quotation status, 16-phase verification pipeline, and review checklist. │
│                                                                             │
│ 11. docs/FIRST_BOOT_CHECKLIST.md                                            │
│    • Complete unboxing-to-first-prompt bring-up manual: cold DMM resistance  │
│      checks, RP2350 .uf2 flashing, OS provisioning, and BIST pass gate.     │
│                                                                             │
│ 12. AGENTS.md                                                               │
│ 12b. docs/WORKFLOW.md                                                       │
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
| **Cellular, GNSS & Dual-SIM** | `docs/HARDWARE_SPEC.md` §2.4 | Quectel EG25-G (LTE Cat-4) | USB 2.0 + Dual SIM (MFF2 + Nano) |
| **Off-Grid Radio Mesh** | `docs/HARDWARE_SPEC.md` §2.4 | Semtech SX1262 (LoRa) | Dedicated SPI to RP2350 (Meshtastic) |
| **Local NFC & Security** | `docs/HARDWARE_SPEC.md` §2.4 | STMicroelectronics ST25R3916 | SPI / I2C (13.56 MHz NFC-A/B/V) |
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
| **Process Layer: Joints, Seals, Retention** | `docs/HARDWARE_SPEC.md` §7.6 | 6 process constraints, no new silicon | Corner bond, VMQ gasket, clamped cell, 0.45 N.m, 20k USB-C|
| **30-Year Failure Budget & Service Plan** | `docs/LONGEVITY_30Y.md` | 12 failure mechanisms, service kit, 5-interval schedule | G7 drop, G8 thermal cycle, G9 UV, G10 unpowered |
| **Feature Status Catalogue** | `docs/STATUS.md` (generated) | 80 features x measured/modelled/specified/aspirational | Phase 12 fails on stale or uncatalogued|
| **Decadal Mechanical Durability** | `docs/HARDWARE_SPEC.md` §7.4 | Knurled Inserts + Poron Relief | 500+ Cycles, 4-Point USB-C, Hard Gold |
| **30-Year Chemistry & Solid-State** | `docs/HARDWARE_SPEC.md` §7.5 | 3.45V Float, Tantalum, UV LOCA | 10,000+ Cycles, Gold Switches, Ti Nib |
| **Instant-Ink 4.5mW Legal Pad** | `docs/HARDWARE_SPEC.md` §2.23 | RP2350 + Wacom Direct Blit | Sub-15ms S2idle Legal Pad & solardeck-inkd|
| **Multi-Source Emergency Battery** | `docs/HARDWARE_SPEC.md` §2.24 | JST-PH 3.9V–14V DC Terminal | Boots from 18650, AA, or 12V Car Battery|
| **3-Position Hardware Privacy Switch**| `docs/HARDWARE_SPEC.md` §2.25 | Physical Slide Switch | NORMAL, MIC_MUTE, FULL_BLACKOUT |
| **Blackout Indexing Pips & Chamfer**| `docs/HARDWARE_SPEC.md` §3.5 | Tactile Pips + 45° Corner | Blind Night-Vision / Blackout Operation|
| **Secret Knock & Anti-Theft Tripwire**| `docs/SOFTWARE_SPEC.md` §23 | `solardeck-tripwired` | 4µA BMA400 Knock Wake & LoRa Camp Alarm|
| **Autonomous Solar Tracking HUD**| `docs/SOFTWARE_SPEC.md` §24 | `solardeck-sunaim` | Sun Azimuth Fusion HUD & Peak Watt Reticle|
| **Bistable "Black Box" Crash QR** | `docs/SOFTWARE_SPEC.md` §25 | `solardeck-blackboxd` | 0.000W Permanent Panic QR & Phone Triage|
| **Offline Ghost-Nav Geolocation**| `docs/SOFTWARE_SPEC.md` §26 | `solardeck-ghostnavd` | Zero-Satellite Indoor BSSID & Cell Fix |
| **Passive RF Sweeper & Drone Alert**| `docs/SOFTWARE_SPEC.md` §27 | `solardeck-sweeperd` | Multi-Band Near-Field Radar & AirTag Sniff|
| **Airgapped Ultrasonic Sound-Bridge**| `docs/SOFTWARE_SPEC.md` §28 | `solardeck-soundbridged` | 19kHz Acoustic FSK Modem for RF-Silent Airgap|
| **Barometric Storm & Flood Radar**| `docs/SOFTWARE_SPEC.md` §29 | `solardeck-stormd` | 10cm BMP390 Pressure Drop Warning & Elevation |
| **GPU Display Steganography** | `docs/SOFTWARE_SPEC.md` §30 | `solardeck-stegod` | Blue-Noise LSB Photographic Leak Attribution |
| **Cold Storage Vault & Desiccant Pocket**| `docs/HARDWARE_SPEC.md` §4.6 | 3x MicroSD + 1g/2g Desiccant | IP67 Hatch Cavity / 100+ Regen Cycles |
| **Sub-Surface Geophone & Radar Hotpack**| `docs/OFFGRID_TACTICAL_SENSORS.md` §8.9| Hotpack 7 (`solardeck-geophoned`)| SM-24 Geophone + 100mm Spike + 24-bit ADC|
| **Direct-Satellite Weather Fax Decoder**| `docs/SOFTWARE_SPEC.md` §31 | `solardeck-satweathd` | NOAA-15/18/19 & Meteor-M2 137MHz APT Storm|
| **Hands-Free Trauma Medic AI** | `docs/SOFTWARE_SPEC.md` §32 | `solardeck-traumad` | Touch-Free Whisper + 3B LLM + Medical ZIM |
| **Campervan Alternator & Battery Profiler**| `docs/SOFTWARE_SPEC.md` §33 | `solardeck-alternatord` | 50kHz ADC 12V Diode Ripple & Cranking Sag|
| **8-Channel Logic Analyzer & CAN Sniffer**| `docs/SOFTWARE_SPEC.md` §34 | `solardeck-logicanalyzerd` | RP2350 PIO 100MSPS DMA & Sigrok/PulseView |
| **Radio Direction-Finding Foxhunt Pointer**| `docs/SOFTWARE_SPEC.md` §35 | `solardeck-foxhuntd` | Hotpack 1 SDR Directional Bearing Needle |
| **Stargazing Monochromatic 660nm Red Mode**| `docs/SOFTWARE_SPEC.md` §36 | `solardeck-nvgd` | Zero Photopic Glare Dark-Adaptation & NVG |
| **Autonomous Trailhead Community Mailbox**| `docs/SOFTWARE_SPEC.md` §37 | `solardeck-trailboxd` | 12mW Meshtastic ?WEATHER/?TRAIL/?SOS Resp |
| **Detached LUKS & Dual-PIN Decoy Boot**| `docs/SOFTWARE_SPEC.md` §38 | `solardeck-stealthluks` | Plausible Deniability & Zero Metadata |
| **Rogue Cellular Tower & Stingray Watchdog**| `docs/SOFTWARE_SPEC.md` §39 | `solardeck-stingrayd` | Anti-Stingray 2G Downgrade Kill Switch|
| **Airgapped e-Passport NFC Inspector** | `docs/SOFTWARE_SPEC.md` §40 | `solardeck-epassport` | ICAO 9303 RFID & Sovereign Clone Backup|
| **Camera Sign OCR & Currency Arbitrage** | `docs/SOFTWARE_SPEC.md` §41 | `solardeck-lensworld` | Offline Neural Translation & PPP Forex |
| **Consular Emergency Evacuation Navigator**| `docs/SOFTWARE_SPEC.md` §42 | `solardeck-evacd` | 195-Nation Embassy & Airstrip Vectors |
| **Parasite & Tick Morphology Triage AI** | `docs/SOFTWARE_SPEC.md` §43 | `solardeck-parasited` | 12MP Macro Cam Lyme & Venom Triage |
| **Soil pH & Agronomy Chemistry Profiler**| `docs/SOFTWARE_SPEC.md` §44 | `solardeck-soild` | Galvanic Dual-Probe 3.5–9.0 pH & Moisture|
| **Timber Energy & Bow-Drill Firecraft** | `docs/SOFTWARE_SPEC.md` §45 | `solardeck-timberd` | Wood BTU Density & Friction Fire Pairs |
| **Microscopic Water Pathogen Lens Guide**| `docs/SOFTWARE_SPEC.md` §46 | `solardeck-microbed` | 100x Smartphone Lens Giardia & Algae Guide|
| **Perpetual Solar Living Wall Clock** | `docs/SOFTWARE_SPEC.md` §47 | `solardeck-zen-clock` | 4.5mW Astronomical Calendar & Baro HUD |
| **Perpetual Solar Entertainment & Games**| `docs/SOFTWARE_SPEC.md` §48 | `solardeck-zen-games` | E-Ink Chess, Puzzles & Infocom Z-Machine|
| **Zen Stoic & Tao Te Ching Daily Oracle**| `docs/SOFTWARE_SPEC.md` §49 | `solardeck-zen-oracle` | 10,000 Text Dawn Typographic Inking |
| **Hardware USB Shield & Port Isolation** | `docs/HARDWARE_SPEC.md` §2.26 | TS3USB221A Analog SPST | D+/D- Mechanical Break Juice-Jacking Cut|
| **Chassis Intrusion & Zeroization Sensor**| `docs/HARDWARE_SPEC.md` §2.27 | TEMT6200 Phototransistor| NMI RAM Key Wiping (<3ms Case Breach) |
| **Dual-Bezel IBC Solar Array & Zombie Mode**| `docs/HARDWARE_SPEC.md` §2.28 | 1.24W IBC Cells + 1.0F Supercap| Direct Solar Cold-Boot (Zero Battery) |
| **Snap-On 7.1W Solar Armor & Remote Tether**| `docs/HARDWARE_SPEC.md` §2.29 | `SOLAR-ARMOR-V1` | 7.13W IBC Panel + 2.5m Flat Ribbon Spool|
| **Handlebar Cockpit & Convection Cooling** | `docs/HARDWARE_SPEC.md` §2.30 | RAM-B-238U Ball Mount | Forced Airflow $h=25\text{–}60\text{ W/m}^2\text{K}$ & Aerogel|
| **Overland Bike Computer & Varia Radar HUD**| `docs/SOFTWARE_SPEC.md` §50 | `solardeck-biked` | BLE Power/Cadence, Varia 140m Radar & VAM|

---

## 3. Historical Decision Record

Every descoping and re-derivation decision now lives in **`docs/90-history/decisions.md`** as a
numbered ADR (ADR-001 through ADR-016), each with the original plan, the trigger, the decision, and
the cost delta. Docs cite them as `ADR-nnn`.

This index deliberately carries no decision prose: keeping a second copy here is how the repository
ended up asserting both a descoped pogo bus and its full pinout at the same time.

## 4. Hardware Safety & Power Discipline Check

* **LiFePO4 Chemistry Discipline:** Nominal cell voltage is **3.2V** (3.65V charging cutoff). Never apply 4.2V Li-ion charging profiles.
* **Always-On Rail Isolation:** The **TI TPS62840** buck-boost regulator maintains 3.3V power to the RP2350 and critical sensors when the CM4 5V system boost is disabled.
* **Galvanic Display Bus Isolation:** **2× TI TMUX1575** (4-channel each, 8 channels total) ensure zero parasitic back-powering from unpowered CM4 GPIO pins into the IT8951 display controller during Zen reading.
* **Airgap Series Disconnect:** The physical airgap slide switch disconnects power gate enable nets in series, preventing direct GPIO-to-ground short circuits.

---

## 5. Master Automated Verification Suite & CI Pipeline

To verify every hardware rule, firmware state transition, cadence timing, and 3D mechanical dimension in a single command before submitting fabrication orders:

* **Unified CLI Runner:**
  ```bash
  python3 scripts/verify_all.py
  ```
  Executes all 16 verification phases in ~1.6 seconds with colored pass/fail status and timing metrics.
* **Continuous Integration:** `.github/workflows/verify.yml` automatically triggers on every push and pull request to `main`.
* **Turnkey Box-Build Package:** `hardware/export_production_zip.py` generates the manufacturing bundle for Seeed Studio Fusion from the KiCad/OpenSCAD sources (bundles are CI artifacts, not committed): (`solardeck_gerbers.zip`, `seeed_fusion_bom.csv`, `solardeck_cpl.csv`, `solardeck_chassis.stl`, and `SEEED_FUSION_BOX_BUILD_INSTRUCTIONS.md`).

---

*End of Index.*

## Audit and durability register

| Document | Covers | Status |
| :--- | :--- | :--- |
| `docs/AUDIT_2026-10-20.md` | Audit 1 — documentation truth | delivered |
| `docs/LONGEVITY_30Y.md` | Audit 2 — 30-year failure budget | delivered |
| `docs/AUDIT_2026-10-20_3.md` | Audit 3 — cost, energy, regulatory, DFM, integration | delivered |
| `docs/ARCHIVAL_BUILD.md` | Toolchain survival to 2056, key custody | specified |

Open blockers from audit 3: B1 BOM total (stated $383.30, rows sum $400.72, delta $19.02), B2 solar
energy (45 Wh/day real vs 150 assumed; 3-4 day claim holds only at idle), D3 no regulatory matrix.
