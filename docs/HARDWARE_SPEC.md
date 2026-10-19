# SolarDeck Hardware Specification

Written 2026-10-18 17:38 UTC in the Pi harness by antigravity/gemini-3.8-flash

Detailed hardware architecture, component selection, bus topology, antenna engineering, and electrical requirements for the custom carrier board and mechanical enclosure.

---

## 1. System Block Diagram

```
                                  [ 10.3" E-INK PANEL (KALEIDO 3 / CARTA 1200) ]
                                  [ + CAPACITIVE TOUCH + WACOM EMR DIGITIZER    ]
                                                        ▲
                                                        │ (MIPI DSI / Parallel / SPI)
                                                        │
┌───────────────────────────┐                 ┌─────────┴─────────┐
│  TI BQ25895 BUCK CHARGER  │                 │    IT8951 EPDC    │
│  • WCH CH224K USB-PD Sink │                 └─────────▲─────────┘
│  • 1S LiPo/LiFePO4 Pack   │                           │
└─────────────┬─────────────┘                 ┌─────────┴─────────┐
              │ VBAT Rail                     │ TI TMUX1575 MUX   │ (8-Ch SPDT Bus Isolation)
              ▼                               └────▲─────────▲────┘
┌───────────────────────────┐                      │         │
│ TI TPS62840 LOW-IQ BUCK-  │                      │         │
│ BOOST (60nA IQ, 3.3V AON) │                      │         │
└─────────────┬─────────────┘                      │         │
              │ VDD_3V3_AON                        │         │
              ▼                                    │         │
┌───────────────────────────┐                      │         │
│   RP2350B CO-PROCESSOR    ├──────────────────────┤ (SPI)   │ (SPI / Parallel)
│  • Dual M33 / RISC-V Cores│  I2C / GPIO Wake     │         │
│  • 8MB QSPI PSRAM Buffer  │────────────────┐     │         │
│  • 10 µA Sleep / 4.5mW Zen│                │     │         │
│  • Seiko MS621FE RTC (100d│                │     │         │
└───────────────────────────┘                ▼     │         │
                                      ┌────────────┴─────────┴────┐
                                      │ UNIVERSAL COMPUTE SOCKET  │
                                      │ (Dual Hirose DF40 100-pin)│
                                      │ • CM4 (8GB LPDDR4 / A72)  │
                                      │ • CM5 (A76 3x Compile)    │
                                      │ • Radxa CM3 (RK3566 22nm) │
                                      └───┬───────────────────┬───┘
                                          │ Native USB OTG    │ PCIe Gen 2 x1
                                          ▼                   ▼
                            ┌─────────────────────┐   ┌───────────────────────────┐
                            │ USB-C PORT 1 (DRP)  │   │ DEDICATED USB HOST / HUB  │
                            │ • Driverless Display│   │ • VIA VL805 / ASM1042A or │
                            │ • rpiboot Recovery  │   │   Microchip USB2514B Hub  │
                            └─────────────────────┘   └─────────────┬─────────────┘
                                                                    │
                                      ┌─────────────────────────────┴─────────────┐
                                      │  PERIPHERALS & NETWORKING                 │
                                      │  • Quectel EG25-G 4G LTE Modem (M.2)      │
                                      │    (Includes Integrated Qualcomm GNSS)    │
                                      │  • Onboard MFF2 eSIM (ST4SIM-200M)        │
                                      │  • Semtech SX1262 LoRa 915MHz (RP2350 SPI)│
                                      │  • Knowles I2S MEMS Mic Array             │
                                      │  • Maxim/ADI MAX98357A 1W Speaker Amp     │
                                      │  • USB-C Port 2 (Host / TPS2051B Switch)  │
                                      └──────┬─────────────────────────────┬──────┘
                                             │                             │
              (M2.5 Mounts / MagSafe Array)  ▼                             ▼         (External USB-C Port 2)
        ┌────────────────────────────────────┐             ┌────────────────────────────────┐
        │ UNIVERSAL MOUNT & OPEN KEYBOARD    │             │ MODULAR TACTICAL RF MULTI-TOOL │
        │ • M2.5 Threaded Inserts + MagSafe  │             │ • Internal RP2040 MCU + USB Hub│
        │ • 3D-Printed $20 Q20 Thumb Grip    │             │ • RTL2832U Wideband SDR        │
        │ • Any Bluetooth / USB-C Keyboard   │             │ • TI CC1101 Sub-GHz (300-928M) │
        │ • Camera Tripod (1/4"-20) & Stands │             │ • NXP PN532 NFC (13.56 MHz)    │
        │ • Phase 2 SnapDeck Option ($32 BOM)│             │ • EM4095 125 kHz RFID Demod    │
        └────────────────────────────────────┘             │ • Dual High-Power IR TX/RX     │
                                                           └────────────────────────────────┘
```

---

## 2. Component Selection & Electrical Interfaces

### 2.1 Compute & Low-Power Co-Processing
* **Universal Modular Compute Socket (Dual Hirose DF40 100-Pin Footprint):**
  * Rather than locking the hardware to a single soldered SoC, the carrier board integrates standard dual Hirose DF40 100-pin board-to-board receptacles (55mm × 40mm mechanical envelope).
  * **Drop-in Interchangeability & Silicon-Agnostic Modularity:**
    * **Raspberry Pi CM4 (Baseline Specification):** Model `CM4108032` (Quad Cortex-A72 @ 1.8GHz, Wi-Fi 5, Bluetooth 5.0, **8GB LPDDR4 RAM**, 32GB eMMC). The 8GB configuration is the official engineering baseline: it provides zero-lag AST parsing in Claude Code CLI, parallel compilation (`cargo build -j4`), and runs local quantized 3B LLMs (`llama.cpp`) with zero swap thrashing, while keeping S2idle self-refresh current to ~18 mW.
    * **The Bridge to Pure 64-Bit RISC-V (Milk-V Mars CM):** Drop-in pin-compatible module featuring the **StarFive JH7110 Quad-Core 64-bit RISC-V CPU (RV64GC @ 1.5GHz)** with 4GB/8GB LPDDR4. As the RISC-V Linux ecosystem matures, users can literally unclip the ARM CM4 and snap in the Milk-V Mars CM module, transforming SolarDeck into a 100% pure RISC-V workstation with zero PCB or chassis redesign.
    * **Raspberry Pi CM5 (Drop-in Horsepower Upgrade):** Quad Cortex-A76 @ 2.4GHz with 3x faster compilation throughput for heavy local builds.
    * **Radxa CM3 / Pine64 SOQuartz (Rockchip RK3566 Alternative):** Quad Cortex-A55 @ 1.8GHz on 22nm node for 40% lower active power draw.
  * **RAM Upgradability:** Because high-frequency LPDDR4X memory signals (>4,000 MT/s) cannot travel across long traces without degradation, RAM is tightly coupled on the SOM. Upgrading RAM from 4GB to 8GB or next-gen 16GB is accomplished in under 30 seconds by unclipping the SOM and seating a higher-capacity module.
  * **Multi-Tiered Mass Storage Architecture (Up to 4TB+ Total Capacity):**
    * **Tier 1 (Base System OS):** 32GB high-speed eMMC soldered on the compute module for an immutable, tamper-resistant Linux root filesystem.
    * **Tier 2 (Hot-Swappable Edge MicroSDXC Slot):** Accessible on the outer chassis edge; supports up to **2TB UHS-I MicroSDXC cards** for instant off-grid distro hopping, encrypted backups, and airgapped dataset transport.
    * **Tier 3 (High-Speed M.2 2230/2242 PCIe NVMe SSD Socket):** An M.2 Key-M socket situated on the carrier board underside wired directly to the PCIe Gen 2 x1 lane. Accommodates standard ultra-compact **M.2 2230 and 2242 NVMe SSDs** (Steam Deck / Surface Pro form-factor) from **256GB to 2TB** with transfer speeds exceeding **400 MB/s**, enabling instant storage for full offline Kiwix Wikipedia/StackOverflow archives, git repositories, and multi-gigabyte local LLM weights.
* **Low-Power Co-Processor:** Raspberry Pi **RP2350B** (Dual ARM Cortex-M33 with FPU/DSP or Dual Hazard3 RISC-V cores @ 150MHz).
  * **Ultra-Low Dormant Sleep:** Drops from 180 µA (RP2040) down to **10 µA (~0.033 mW)**—an **18x reduction in sleep current**.
  * **Storage & Memory:**
    * **NOR Flash:** 16MB QSPI NOR Flash (**Winbond W25Q128JVS**).
    * **Dual-Bank A/B Firmware Partitioning & Hardware Watchdog Rollback:**
      * **Slot 0 (0x000000 – 0x00FFFF, 64 KB):** Permanent, immutable hardware-protected Bootloader.
      * **Bank A (0x010000 – 0x40FFFF, 4 MB):** Active golden firmware partition.
      * **Bank B (0x410000 – 0x80FFFF, 4 MB):** Staged OTA / developer test firmware partition.
      * **Data & Telemetry Pool (0x810000 – 0xFFFFFF, 8 MB):** Non-volatile shadow sensor barograph and telemetry logs.
      * **Hardware Watchdog Fallback:** The bootloader boots into the target bank with a **5-second hardware watchdog window**. Newly flashed firmware must execute a self-test and assert `WATCHDOG_KICK`. If the watchdog trips twice without a kick, the bootloader automatically reverts to the previous known-good golden bank, guaranteeing the power arbiter and S2idle wake logic cannot be bricked.
  * **External High-Speed Memory:** Paired with an **8MB QSPI PSRAM chip** (APMemory `APS6404L` / Winbond, $0.75).
  * **The 5 RP2350 Superpowers:**
    1. **Full-Screen Autonomous Framebuffering (30ms Zen Reader):** Holds two uncompressed 1872×1404 8-bit framebuffers (2.62MB each). Pre-caches eBook pages and executes sub-30ms paper-fast page turns without waking the CM4, dropping reading power to **4.5 mW (300+ days battery life)**.
    2. **Perpetual Standalone LoRa Meshtastic Mesh Repeater:** Dedicated Semtech SX1262 LoRa SPI lines connect directly to the RP2350, allowing the co-processor to route mesh packets autonomously at **12–15 mW**, transforming SolarDeck into an 80+ day off-grid emergency mesh node.
    3. **Hardware Power Master & Anti-Brownout Shield:** Continuously monitors the TI BQ27441 fuel gauge; blocks CM4 boot if battery voltage is $<3.0\text{V}$, preventing inrush brownouts and eMMC filesystem corruption.
    4. **Shadow Environmental Telemetry Logger:** Samples BMP390 barometric trends and TMP112 thermals every 60 seconds into a circular PSRAM buffer; dumps a 7-day weather barograph to Linux upon wake in 2ms.
    5. **Autonomous Bezel Touch Gestures:** Scans capacitive side-bezel touch traces at 10 Hz (15 µA) for instant page-flip navigation.
* **Dual-Master Display Bus Multiplexer:** Texas Instruments **TMUX1575** (8-channel SPDT bus switch).
  * High-speed **8-channel SPDT bidirectional bus switch** with Fail-Safe Power-Off Protection ($I_{\text{off}}$).
  * Completely isolates all 6 EPDC control and data lines: `SPI_MOSI`, `SPI_MISO`, `SPI_SCLK`, `SPI_CS`, `HRDY` (status flag), and `RESET`.
  * **Zero-Leakage Isolation Safety:** When CM4 is powered down to 0.000V, the TMUX1575 completely disconnects CM4 lines to eliminate parasitic back-powering and pin leakage ($I_{\text{leak}} < 10\text{ nA}$), allowing the RP2350 to update the display in deep sleep while drawing only **4.5 mW total system power**.
* **Real-Time Clock (RTC):** Maxim **DS3231** temperature-compensated crystal oscillator (TCXO).
  * Drift: < 2 minutes per year ($\pm 2$ ppm).
  * **Rechargeable Micro-Battery Power Reservoir:** Powered by a high-reliability SMT **Seiko MS621FE** rechargeable 3.0V 5.5 mAh Lithium Micro-Battery ($0.65) paired with a reverse-blocking Schottky diode and trickle charge circuit.
  * **Zero Maintenance & 100+ Day Lifespan:** Charges whenever the tablet is powered; maintains TCXO clock, alarms, and NVRAM registers for **over 100 days** when the main battery is completely removed or depleted, eliminating the 1970 UNIX epoch clock reset bug without coin-cell leakage.

### 2.2 Display & Digitizer Assembly
* **Display Panel:** 10.3-inch E-Ink **Kaleido 3** or **Kaleido 4** (Color) / **Carta 1200** (Monochrome).
  * Resolution: 1872 × 1404 pixels (**227 PPI** black/white, 114–150 PPI color).
  * Active Area: 209.66 mm × 157.25 mm; Contrast Ratio: 15:1.
  * **Kaleido 4 Ready (Drop-in Panel Compatibility):** Supports the newly released Kaleido 4 panel featuring an **Oxide TFT backplane** ($10\times$ higher electron mobility, >40,000 colors, +15% white reflectivity, +50% contrast) sharing the identical 10.32" mechanical envelope, 40/50-pin FPC interface, and rear-laminated Wacom digitizer.
* **V1 24 FPS Cinema Video & High-Speed Display Architecture:**
  * **Dual-Path Host Bus Architecture:**
    1. *High-Speed MIPI-DSI Video Path (CM4 Host - 24 to 30 FPS):* The CM4 routes its native 2-lane MIPI-DSI display bus (1 Gbps per lane = 2,000 Mbps aggregate bandwidth) to a high-speed video bridge / timing controller (TI SN65DSI83 DSI-to-FlatLink bridge / Lattice CrossLink-NX FPGA / IT8961). Transferring a full 1872×1404 frame takes **< 2.5 milliseconds** (eliminating the legacy 55ms SPI transfer bottleneck). This frees up **39 ms of the 41.67 ms frame budget** purely for electrophoretic particle motion, unlocking **24 FPS cinema video playback** and fluid Wayland desktop rendering.
    2. *Ultra-Low-Power SPI Fallback Path (RP2350 Co-Processor - 4.5 mW Zen Mode):* When the CM4 and MIPI-DSI rails are completely powered down (0.000W), the TI TMUX1575 bus switch routes the RP2350's SPI lines to the display controller, enabling autonomous 30ms book page flips and 1-second clock updates drawing only **4.5 mW total system power**.
  * **Thermal-Assisted Fluid Viscosity Coupling (Overdrive Viscosity Assist):**
    * Electrophoretic particle mobility ($\mu$) is inversely proportional to fluid viscosity ($\eta$): $\mu \propto 1/\eta(T)$.
    * In cold conditions (<20°C), microcapsule fluid is viscous and sluggish. At 30°C–33°C, dielectric fluid viscosity drops by **>40%**, enabling pigment particles to accelerate **$1.8\times$ faster** under identical electrical drive pulses.
    * The V1 PCBA integrates a balanced internal copper thermal dissipation plane that routes heat from the CM4 CPU shield directly beneath the display backplane.
    * During 24 FPS video playback, the thermal management daemon (`solardeck-thermal-boostd`) uses waste CPU heat to maintain the backplane at a controlled **30°C–33°C** (monitored by the panel TMP112 sensor), completely eliminating motion trails and holding fluid 24 FPS without dedicated heater elements.
* **EPDC (Electronic Paper Display Controller):** Dedicated High-Speed Controller (ITE **IT8951** / **IT8961** with MIPI bridge).
  * *SoC-Direct Drive Architectural Evaluation:* While driving E-Ink directly from an SoC's integrated controller (e.g. RK3566 `rockchip-ebc`) eliminates an $18 chip, it creates fatal system lock-in: the display cannot be driven when the main CPU is powered down to 0.000W. Retaining a dedicated EPDC with dual-bus inputs (MIPI-DSI from CM4 for 24 FPS video + SPI from RP2350 for Zen reading) is mandatory to enable both the **universal modular compute socket** and the **RP2350 dual-brain co-processor** (which commands the display over SPI to achieve 160+ day desk-clock and 300+ day reading lifespans).
* **reMarkable-Grade Stylus Digitizer & Tactile Paper-Feel:**
  * **Digitizer Sensor:** Genuine **Wacom EMR (Electro-Magnetic Resonance)** sensor board laminated behind the e-paper panel (240 Hz sampling rate, 4,096 levels of pressure and tilt, `wacom_w9013` driver).
  * **Magnetic Shielding & Flux Absorption:** Wacom EMR is inherently sensitive to external magnetic fields (~560 kHz resonant coil). To prevent coordinate warping or pen drift from the SnapDeck keyboard pogo magnets, backpack dock, or internal speaker:
    1. A **0.1mm high-permeability Mu-Metal / Ferrite shielding foil sheet** is laminated directly across the entire rear surface of the Wacom digitizer PCB, redirecting stray magnetic flux away from the sensor loop.
    2. All chassis docking neodymium magnets (N52) are positioned strictly outside the active writing perimeter with a minimum **14mm mechanical keep-out zone** into the outer bezel margin.
  * **Tactile Paper Friction:** The front cover lens uses **chemically etched anti-glare matte glass** (15% haze). When paired with soft elastomer or felt-composite nibs (Staedtler Noris Digital, Lamy AL-star with PC/EL nibs, or genuine reMarkable Marker felt nibs), the friction coefficient matches real 80gsm paper ($\mu = 0.18–0.22$), producing the authentic acoustic pencil "scritch-scratch" sound without slippery plastic glide.
  * **Predictive 3-Stage Wacom EMR Hover Proximity Power Gating:**
    1. *Stage 1 (Reading / Rest >15mm):* System rests in S2idle suspend (15 mW) or RP2350 Zen reader mode (4.5 mW). Display is static (0 mW).
    2. *Stage 2 (Hover Approach 10–15mm):* The Wacom resonant coil detects pen proximity and fires the hardware interrupt `PEN_PROX_INT`. In **< 2 milliseconds**, the system wakes to "Inking Standby": Core 0 runs throttled at 600 MHz (Cores 1–3 stay OFF) and the IT8951 primes its 1-bit Direct Update (DU) waveform buffer. Total standby power is ~350 mW—pre-armed before the pen even touches glass.
    3. *Stage 3 (Tip Contact & Active Drawing):* Tip switch closes (`BTN_TOUCH = 1`). Coordinates bypass the window compositor directly into the IT8951 partial line buffer (<18ms tip-to-ink latency, ~600 mW active power on Linux, or <15ms and ~220 mW when driven directly by the RP2350).
    4. *Stage 4 (Pen Lift & Retreat >500ms):* Stroke vector is committed to disk; system immediately drops back to 15 mW / 4.5 mW suspend.
* **Touch Panel & Hardware-Enforced Zero-Latency Palm Rejection:**
  * **Sensor:** Capacitive multi-touch glass overlay with chemically etched anti-glare matte finish.
  * **Direct Hardware Proximity Blanking Gate:** When the battery-free Wacom stylus approaches within **10–14 mm** of the glass, the Wacom digitizer asserts **`PEN_PROX_INT`** LOW. This signal is routed directly to a hardware logic gate on the Goodix GT911 touch interrupt line, **hardware-suppressing all capacitive touch coordinates** before they reach the CPU. The user can rest their entire hand and forearm on the glass while writing with 100% immunity to stray touch events, with zero software latency or CPU overhead.
* **Coordinate-Targeted Localized Piezoelectric Haptic Engine (Quad-Corner Acoustic Phase Array):**
  * **The Problem with Global LRAs:** Conventional smartphones and tablets use a single vibration motor (LRA or ERM) mounted to the chassis. Pressing a virtual key shakes the entire device, vibrating both palms and feeling muddy, artificial, and disconnected from the finger.
  * **Driver ICs:** Dual **Boréas Technologies BOS1901** (or BOS1211) ultra-low-power CapDrive piezoelectric haptic drivers ($1.45 each) with high-voltage differential outputs (up to 190Vpp from a single 3.3V/5V rail) and integrated energy recovery. CapDrive absorbs **>80% of electrical energy back into the storage capacitor** at the end of each mechanical pulse, slashing power draw to just **15 to 25 mW per click** (10× less power than conventional piezo drivers).
  * **Actuator Array:** 4× **TDK PowerHap 0904H014V060** (or 1204) miniature multi-layer piezoelectric actuators ($1.25 each) bonded rigidly directly between the chemically etched cover glass perimeter and the CNC aluminum/chassis mounting bracket at the four corners ($TL, TR, BL, BR$).
  * **Sub-1.0ms Mechanical Acceleration:** Unlike magnetic motors that take 12–20ms to overcome mechanical inertia, piezo ceramics accelerate instantaneously in **< 1.0 millisecond** with massive **>5G peak acceleration** and 15 µm displacement.
  * **Spatial $(X,Y)$ Coordinate-Targeted Tactile Driving:**
    * When the Goodix GT911 touch controller registers a keystroke at $(X, Y)$ (e.g. typing the 'A' or 'P' key on the bare-glass virtual terminal keyboard), the haptic daemon (`solardeck-hapticd`) maps the touch coordinate to distance weights across the four corner piezos:
      $$w_i = \frac{1 / d_i^\alpha}{\sum_j (1 / d_j^\alpha)}$$
    * The closest corner actuator fires a crisp 1.2ms square/sine displacement pulse into the glass substrate, while opposing corner actuators fire attenuated, microsecond phase-delayed damping waveforms to actively cancel acoustic reflection and chassis resonance.
    * **The Tactile Feel:** Kinetic displacement concentrates strictly under the touching fingertip. Instead of the whole tablet shaking, the user feels a **sharp, localized mechanical click directly under that individual thumb/finger**, replicating the tactile feedback of a physical microswitch on bare glass.
  * **Single LRA Fallback (DNP Option):** The PCBA retains an alternate footprint for a single TI **DRV2605L** + Vybronics 8mm Z-axis LRA as a budget build variant for cost-reduced educational runs.
* **Dual CCT Frontlight Subsystem (Pitch-Black Reading & Circadian Amber):**
  * **Driver IC:** Texas Instruments **TPS61163** dual-channel constant-current step-up LED driver ($0.65).
  * **Dual Interleaved Bezel LED Strings:** 12 cold-white LEDs (5000K) and 12 warm-amber LEDs (2700K) embedded along the bottom-edge lightguide.
  * **Autonomous Circadian Dimming:** Controlled by the RP2350 via 2048-step logarithmic PWM dimming; automatically transitions from crisp white in dim daylight to soft amber (zero blue light emission) after sunset based on RTC time and solar strip ambient lux readings.
  * **Zero Idle Drain:** Draws **0.000 µA** when turned off during sunlight reading.

### 2.3 Power Subsystem & Multi-Tier Voltage Regulation
* **Battery Chemistry & Secondary Hardware Protection:**
  * **Chemistry:** **1S Li-ion / LiPo** (3.7V nominal, 4.2V peak) or **1S2P LiFePO4** (3.2V nominal, 3.65V peak).
  * **Target Capacity:** 8,000 to 10,000 mAh (26–32 Wh LiFePO4 / 30–37 Wh Li-ion) pouch pack (airline-compliant <100Wh).
  * **Physical Battery Chemistry Strap (`CHEM_SEL` LiFePO4 vs. Li-ion Hardware Lock):**
    * A dedicated 3-pin solder-bridge / sub-miniature slide switch (**C&K JS102011SAQN**, $0.35) located on the PCBA under the battery cover rigidly straps the hardware charging ceiling:
      * **Position 1 (GND / LiFePO4 Mode):** Hardwires the BQ25895 resistor network / default register pin to clamp maximum charge voltage strictly to **3.60V / 3.65V**. Prevents destructive 4.2V overcharging even if Linux OS, config files, or I2C bus are corrupted.
      * **Position 2 (VDD / Li-ion Mode):** Unlocks standard **4.20V** charging for standard lithium polymer chemistry.
      * **Fuel Gauge Auto-Profile:** Connected directly to RP2350 `GPIO 15` on Power-On Reset (POR). The co-processor reads the physical strap state and automatically configures the BQ27441 fuel gauge with the appropriate chemical Open-Circuit Voltage (OCV) profile table.
  * **Hardware Battery PCM (Pure Silicon Secondary Protection):**
    * Texas Instruments **BQ2970** battery protection IC paired with dual low-$R_{\text{DS(on)}}$ (12 mΩ) N-channel power MOSFETs (**TI CSD87330Q3D**, $0.55 total).
    * Completely autonomous from software and I2C: physically cuts off the battery pack if cell voltage drops below **2.50V** (over-discharge protection) or exceeds **3.65V/4.25V** (over-charge protection).
    * Instantaneous hardware short-circuit trip: physically disconnects in **< 10 microseconds** if load current exceeds **8.0A peak**.
* **Battery Charger IC & Autonomous Hardware JEITA Thermal Protection:**
  * Texas Instruments **BQ25895** I2C-controlled Synchronous Buck Charger paired with a dedicated **WCH CH224K** (or STMicroelectronics STUSB4500) standalone USB-PD Sink Controller ($0.45).
  * **USB-PD 20W Power Negotiation:** The CH224K automatically advertises sink capabilities and negotiates a 9V/2.22A or 12V/1.67A (20W) power contract from any standard USB-PD charger, supplying high voltage to the BQ25895 buck input to recharge the pack in **1.5 to 2 hours**.
  * **Pure Silicon JEITA Cold-Weather Lockout Ladder (Zero Software Dependency):**
    * The BQ25895 `TS` pin is configured with a precision 0.1% resistor divider network (5.23 kΩ pull-up $R_1$, 30.1 kΩ pull-down $R_2$) paired with a **10 kΩ NTC thermistor (Murata NCP18XH103F03RB, $\beta = 3950\text{K}$)** glued directly to the battery pouch cell.
    * **$T < 0^\circ\text{C}$ (Freezing Lockout):** Charger automatically terminates charging completely ($I_{\text{CHG}} = 0.000\text{ A}$), preventing catastrophic metallic lithium plating and internal micro-shorts while still powering system loads from solar/USB.
    * **$0^\circ\text{C} \le T < 10^\circ\text{C}$ (Cold Taper):** Charge current automatically throttled to $0.2\text{C}$ ($400\text{ mA}$) to protect chemistry.
    * **$10^\circ\text{C} \le T \le 45^\circ\text{C}$ (Normal Band):** Full 20W fast charging ($3.0\text{A}$).
    * **$45^\circ\text{C} < T \le 60^\circ\text{C}$ (Heat Taper):** Charge voltage throttled from 3.65V down to 3.40V.
    * **$T > 60^\circ\text{C}$ (Overheat Lockout):** Complete charger shutdown.
* **Dual-Stage Solar Harvesting & Ambient Sensing Architecture:**
  1. *High-Power Field Solar (Fast Recharge via USB-C):* Standard USB-C Port 2 supports 5V–14V input from folding 15W–28W outdoor panels. The BQ25895's integrated dynamic input voltage management (**VINDPM / MPPT**) tracks optimal solar output to recharge the pack safely in field conditions.
  2. *Dedicated Nano-Power Bezel Harvester (Texas Instruments BQ25504):*
     * Resolves the primary charger's 3.9V Under-Voltage Lockout ($V_{\text{UVLO}}$) ceiling.
     * Dedicated ultra-low-quiescent boost converter ($1.80) wired directly to the top-bezel monocrystalline micro-solar strip (IXYS SM141K06L, $22\text{ mm} \times 35\text{ mm}$, ~0.15W peak, ~50–120 mW real-world).
     * Cold-starts from as low as **330 mV** and continuously harvests down to **100 mV**.
     * Executes autonomous 80% Fractional Open-Circuit Voltage (FOCV) MPPT sampling, boosting micro-solar energy directly into the battery rail with >90% efficiency, keeping the 4.5 mW RP2350 Zen reader topped off indefinitely even under indoor lighting.
  3. *Zero-BOM Ambient Lux Sensor (Solar Strip via RP2350 ADC):*
     * The open-circuit voltage ($V_{OC}$) of the top-bezel solar strip is tapped through a high-impedance 10:1 divider (1.0 MΩ / 110 kΩ, <3 µA draw) into RP2350 analog input pin `RP2350_ADC0`.
     * The co-processor maps cell photodiode voltage across a calibrated log curve from 10 lux (candlelit room) to 120,000 lux (blinding noon sunlight).
     * Automatically adjusts E-ink Look-Up Table (LUT) waveform contrast, boosts color saturation in sunlight, and signals the compositor to engage dark mode in dim environments without adding a dedicated ambient light sensor IC ($0.00 BOM cost).
* **Survival Powerbank Mode (15W Reverse Boost):**
  * The Texas Instruments **BQ25895** features a built-in bidirectional synchronous boost converter mode.
  * When an external phone or USB device is connected to USB-C Port 1 or Port 2, the RP2350 writes to the BQ25895 I2C register to enable **OTG Mode** (`OTG_CONFIG = 1`).
  * The charger steps up battery voltage to output **5.1V @ 3.1A (15.8W max)** with internal current limiting and short-circuit protection.
  * **Zero-Compute Autonomous Operation:** The entire reverse powerbank session runs under RP2350 supervision while the power-hungry CM4 Linux brain remains **100% powered off (0.000W)**.
  * The E-Ink screen displays a live, high-contrast charging gauge updated every 10 seconds:
    `"Powering External Device: 5.10V @ 2.40A (12.2W) | Battery: 74% (25.9 Wh) | Est: 2h 15m remaining"`.
  * Turns the 35 Wh LiFePO4 tablet into an ultra-durable, flame-safe emergency power bank for smartphones, GPS handhelds, and flashlights in off-grid emergencies.
* **Rigid Voltage Regulators (Anti-Brownout Engineering):**
  1. *Always-On 3.3V System Rail (`VDD_3V3_AON`):* Dedicated Texas Instruments **TPS62840** ultra-low quiescent current (**60 nA $I_Q$**) synchronous buck-boost converter. Powered directly from VBAT (2.5V–4.35V), it supplies a stable, ultra-clean 3.3V rail at up to 750 mA to the RP2350, 8MB PSRAM, DS3231 RTC, `I2C_ALWAYS_ON` sensors, and Semtech SX1262 LoRa module continuously, ensuring perpetual operation when the main CM4 5V boost converter is completely unpowered.
  2. *Main 5.0V System Boost:* Texas Instruments **TPS61088** synchronous boost converter steps up 3.0V–4.2V battery voltage to a rigid 5.0V @ 3.5A rail, delivering up to 17.5W peak power for CM4 turbo compilation, USB peripheral bus power, and display supply.
  3. *Cellular Modem 3.8V Buck-Boost:* Texas Instruments **TPS63020** 3.8V 2.5A synchronous buck-boost converter dedicated exclusively to the M.2 Quectel EG25-G modem, accompanied by a **1,000 µF low-ESR polymer capacitor array**. This completely buffers the modem's 2.0A transient GSM/LTE transmit bursts, preventing battery rail sag and system brownouts even when the battery is depleted to 3.0V.
* **Power Gating (Physical Cutoff Switches):**
  * Texas Instruments **TPS22918** ultra-low leakage load switches on peripheral power rails (LTE modem, Wi-Fi, audio amp, and external expansion bus). Zero leakage current during S2idle sleep.

### 2.4 USB Host Controller & Wireless Subsystem
* **Dedicated PCIe USB Host Controller & Port Architecture:**
  * To resolve the BCM2711's single native USB 2.0 PHY limitation and eliminate peripheral bus contention:
    1. **Host Peripherals (Dedicated PCIe USB Controller):** A dedicated **VIA VL805** or **ASMedia ASM1042A** USB host controller (or industrial Microchip **USB2514B** USB 2.0 Hub IC) interfaces to the CM4 via the PCIe Gen 2 x1 lane, providing isolated, simultaneous downstream USB channels to:
       * M.2 Key-B 3042 Quectel EG25-G Cellular Modem
       * USB-C Port 2 (Host peripheral port with TPS2051B current limiter)
       * SnapDeck 5-pin magnetic pogo keyboard dock
       * Rear 8-pin hermetic backpack expansion bus
       * RP2350 USB CDC serial console (`/dev/ttyACM0`)
    2. **Dedicated USB Gadget & Recovery Port (Native BCM2711 USB OTG):** The Broadcom BCM2711's native USB 2.0 OTG PHY connects directly to **USB-C Port 1**. This ensures that entering USB Gadget Secondary Display Mode or triggering `rpiboot` recovery never disconnects the internal cellular modem, keyboard, or modular backpack.
* **Cellular Modem & Dual-SIM Architecture:** **M.2 Key-B (3042)** socket connected to dedicated host USB lines.
  * Module: **Quectel EG25-G** (Worldwide Cat-4 LTE, 30+ bands, global carrier certifications).
  * **Dual-SIM Capability:**
    1. **Onboard Soldered MFF2 eSIM:** STMicroelectronics **ST4SIM-200M** (or Infineon **SLM97**) in industrial DFN-8 (5×6mm) package, directly soldered to carrier board. Managed natively under Linux via **`lpac`** and `ModemManager` over standard AT channels (`AT+CCHO`/`AT+CGLA`) for instant QR-code carrier activation.
    2. **External Physical Nano-SIM Tray:** IP67 weather-sealed push-push Nano-SIM tray on the chassis edge for local prepaid, international traveler, or burner SIM cards.
    3. **Software Slot Switching:** Instant toggle between physical SIM and eSIM via standard `mmcli -m 0 --set-primary-sim-slot=1/2`.
  * **RF Decoupling:** 470 µF low-ESR polymer capacitor placed adjacent to modem VCC to handle 2.0A transient TX bursts without voltage sag.
* **Near Field Communication (13.56 MHz NFC / Smartcard / Crypto):**
  * Controller: **NXP PN532** (or STMicroelectronics **ST25R3916**) connected via I2C (`0x24`) to Linux.
  * Antenna: Tuned flexible PCB loop antenna laminated in the top bezel (free of metal shielding).
  * Capabilities: ISO/IEC 14443 Type A/B, FeliCa, MIFARE, ePassport reading (ICAO 9303), hardware FIDO2 / WebAuthn authentication (tap physical YubiKey to top bezel), and airgapped NFC crypto wallet signing (Tangem, Satochip, Coldcard).
  * Physical Wallet Companion: Rear chassis MagSafe magnetic ring supports snapping standard physical MagSafe card wallets (Apple, Moft, Peak Design) for carrying 2–3 physical credit cards, IDs, and cash.
* **LoRa Mesh Radio:** **Semtech SX1262** 915/868 MHz transceiver (up to +22 dBm output).
  * Connects via dedicated SPI to the RP2350 co-processor, running autonomous 24/7 **Meshtastic** mesh repeating firmware at 12–15 mW, and exposing a virtual serial interface to Linux over the inter-processor UART/serial bus (`/dev/ttyAMA0`).
* **Global Satellite Navigation (Integrated Qualcomm GNSS):**
  * Integrated multi-constellation GNSS engine inside the Quectel EG25-G modem (Qualcomm Gen8C Lite).
  * Concurrent reception of GPS, BeiDou, Galileo, GLONASS, and QZSS.
  * Connects via an internal dedicated high-efficiency FPC antenna (Molex 1461860100).
  * Feeds standard NMEA sentences directly into Linux `gpsd` (`/dev/ttyUSB1`) for offline OsmAnd, QGIS, and FoxtrotGPS mapping without requiring a redundant standalone GPS chip, saving $17.00 in BOM and precious PCB space.

### 2.5 Antenna Engineering & RF Architecture
To prevent the device from becoming an unwieldy "hedgehog" with 5 external antennas, SolarDeck adopts a hybrid external/embedded antenna topology:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SOLARDECK TOP BEZEL RF TOPOLOGY                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [IP67 SMA JACK]                                     [IP67 SMA JACK]       │
│         │                                                   │               │
│         ▼                                                   ▼               │
│    LoRa 915MHz                                        Cellular MAIN         │
│  (Detachable Whip)                                  (Optional Field Whip)   │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│  INTERNAL CONCEALED ANTENNAS (Inside PA12 Frame / TPU Bumpers):             │
│                                                                             │
│  • Cellular DIVERSITY (RX):  Taoglas FXUB63 Ultra-Wideband Flexible PCB     │
│  • Wi-Fi 5 / BT (2.4/5GHz):  Molex 1461530100 Dual-Band Dipole FPC         │
│  • GNSS (GPS/BeiDou/Galileo): 15×15mm Ceramic Active Patch (Upward Facing)  │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **LoRa 915/868 MHz Antenna (Meshtastic):**
   * **Mount:** Top-edge IP67 Bulkhead SMA Female (Jack) with silicone O-ring gasket.
   * **Tactical Field Whip:** **Linx Technologies `ANT-916-CW-HWR-SMA`** (1/2-wave center-fed dipole, 3.2 dBi gain, operates independently of internal ground plane, hinged knuckle).
   * **Low-Profile Pocket Stub:** **Linx Technologies `ANT-916-CW-RH-SMA`** (50mm rubber ducky for compact transit).
2. **Cellular LTE 2×2 MIMO Antennas (Quectel EG25-G):**
   * **Main (TX/RX):** Vertical **Taoglas `FXUB63.07.0150C`** ultra-wideband (698–3000 MHz) flexible PCB antenna adhered along the right chassis bezel.
   * **Diversity (RX Only):** Horizontal **Taoglas `FXUB63.07.0150C`** flexible PCB antenna adhered along the bottom chassis bezel.
   * **Spatial & Polarization Isolation:** The two cellular antennas are separated by $>180\text{ mm}$ and cross-polarized (vertical vs. horizontal), achieving >20 dB isolation and enabling full 2×2 MIMO carrier aggregation, doubling weak-signal throughput in rural areas.
3. **Wi-Fi 5 & Bluetooth 5.0 (CM4):**
   * **Molex `1461530100`** balanced dual-band (2.4 GHz / 5.8 GHz) dipole FPC with micro-coax pigtail to CM4 U.FL connector. Balanced dipole design ensures human hand grip does not de-tune the wireless link.
4. **Enclosure RF Physics (Faraday Cage Mitigation):**
   * **PA12 SLS Nylon:** Inherently RF-transparent; all internal FPC antennas radiate freely.
   * **CNC 6061-T6 Aluminum:** Aluminum completely blocks RF signals. When the aluminum unibody is chosen, the top 25mm bezel is manufactured as a modular **PA12/Delrin "RF Window"** cap, allowing RF waves to escape while maintaining IP67 gasket sealing.

### 2.5.1 RF Coexistence & Multi-Radio Isolation Architecture
SolarDeck operates five concurrent radio channels (LoRa 915 MHz, Cellular LTE Cat-4, Wi-Fi 5 GHz, Bluetooth 5.0 2.4 GHz, and GNSS L1 1575.42 MHz) within a single 10.3" portable frame without mutual receiver desensitization (desense) or packet degradation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SOLARDECK 4-CORNER RF COEXISTENCE TOPOLOGY                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ [TOP-LEFT CORNER]                                       [TOP-RIGHT CORNER]  │
│ LoRa 915/868 MHz External Whip                          Cellular LTE Main   │
│ • Vertically Polarized                                  • Internal FPC / SMA│
│ • Bursty Duty Cycle (<0.1% TX)                          • Integrated SAW    │
│            │                                                    │           │
│            │ ◄─────────── 240mm Spatial Isolation ────────────► │           │
│            ▼              (25 to 35 dB Path Loss)               ▼           │
│ [BOTTOM-LEFT CORNER]                                    [BOTTOM-RIGHT]      │
│ Wi-Fi 5.0 GHz & BT 2.4 GHz                              Cellular Diversity  │
│ • Dual-Band Balanced Dipole                             • Taoglas FXUB63    │
│ • Hardware PTA Coexistence                              • Cross-Polarized   │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **Spatial Path-Loss Isolation (> 200mm Separation):**
   * Signal power drops with the square of distance ($1/r^2$). Unlike a smartphone crammed into a 70mm chassis, SolarDeck's 240mm width provides **25 to 35 dB of natural path-loss attenuation** between the high-power LoRa transmitter (+22 dBm) and the sensitive Cellular/Wi-Fi receivers.
2. **Polarization Orthogonality (Cross-Polarization):**
   * The external LoRa whip is vertically polarized (perpendicular to chassis).
   * The internal Cellular Diversity and Wi-Fi dipole antennas are oriented horizontally along the bottom/side frame.
   * Orthogonal polarization provides an additional **15 to 20 dB of cross-polarization isolation**, preventing front-end LNA saturation.
3. **Front-End SAW & BAW Filtering:**
   * Both the Quectel EG25-G modem and the Semtech SX1262 transceiver incorporate internal Surface Acoustic Wave (SAW) bandpass filters directly on their RF inputs, rejecting out-of-band harmonics by $>40\text{ dB}$.
4. **Bursty LoRa Duty Cycle (<0.1% Airtime):**
   * LoRa transmits short text and telemetry packets lasting 60–150 milliseconds once every few minutes, remaining in passive microamp listening mode for 99.9% of the operational cycle.
5. **5 GHz Wi-Fi Spectrum Steering:**
   * Linux network profiles default Wi-Fi connectivity to the **5.0 GHz band**, leaving the 2.4 GHz ISM band 100% clear for low-latency Bluetooth keyboard and audio pairing, arbitrated seamlessly by the BCM43455 combo chip's internal 3-wire Packet Traffic Arbitration (PTA).

### 2.5.2 RF Front-End Precision: Pi-Matching Networks & Coaxial Strain Relief
To guarantee peak radiation efficiency, prevent destructive transmitter reflection, and maintain impedance integrity across manufacturing tolerances:
* **0402 Discrete Pi-Matching Networks:** Every antenna trace on the carrier board features a dedicated 3-element Pi-matching footprint ($C_{\text{shunt1}}$ – $L_{\text{series}}$ – $C_{\text{shunt2}}$ in 0402 surface-mount packaging with high-Q Murata / TDK RF components) immediately adjacent to its U.FL / SMA launch point:
  * `RF_LORA`: Tuned specifically for 915 MHz (US) or 868 MHz (EU) to cancel chassis grounding reactance.
  * `RF_LTE_MAIN` & `RF_LTE_DIV`: Tuned across wideband LTE 700–2600 MHz to achieve $\text{VSWR} < 2.0:1$ across all carrier aggregation bands.
  * `RF_WIFI_BT`: Dual-band conjugate matching for 2.4 GHz and 5.8 GHz.
  * `RF_GNSS`: High-rejection ceramic matching with DC bias choke for active LNA injection.
* **Inner-Layer Ground Keepout:** A continuous **3.0 mm copper clearance void** is etched across all internal PCBA ground layers directly beneath each surface-mount U.FL pad, eliminating parasitic shunt capacitance that would otherwise detune high-frequency RF launches.
* **Molded Coaxial Cable Retention Channels:** Internal chassis ribs feature recessed silicone-gasketed micro-routing channels that lock IPEX MHF4 / U.FL micro-coaxial pigtails securely in place, completely preventing cable detachment or microphonics during heavy vehicle vibration and 4-foot drops.

### 2.6 Dual-Camera Subsystem (Multimodal AI & Video Conferencing)
SolarDeck leverages the Broadcom SoC's dual independent MIPI CSI-2 camera ports (`CAM0` and `CAM1`) and hardware Image Signal Processor (ISP) to deliver complete visual intelligence and teleconferencing with zero USB overhead:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SOLARDECK DUAL-CAMERA ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. REAR FLUSH CAMERA FOR AI VISUAL REASONING (Back Chassis):                 │
│    • Sensor: Sony IMX708 (12.0 Megapixels, 4608 × 2592, HDR, PDAF)          │
│    • 100% Flush Zero-Bump Integration: Sits recessed beneath an anti-reflec-│
│      tive sapphire crystal optical window flush with the rear aluminum plate │
│      (0.0mm camera bump / zero wobble when typing flat on a desk).          │
│    • Focus: Motorized Phase Detection Autofocus (PDAF) from 5cm to infinity │
│    • Bus: 2-Lane MIPI CSI-2 on `CAM1` (Direct Hardware ISP Pipeline)        │
│    • Shutter: Internal hardware load switch cut + firmware electronic gate  │
│    • Role: Claude Vision multimodal analysis, document & receipt digitizing,│
│            whiteboard capture, 5cm macro PCB inspection, TXQR ingestion     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. V1 FRONT BEZEL STREAMLINING (Ponytail Descoping Win):                   │
│    • Front camera and mechanical sliding ThinkShutter are descoped from V1. │
│    • Eliminates high-speed MIPI-CSI trace routing noise and IP67 water leak │
│      vulnerabilities, while freeing bezel space for solar energy harvesting.│
│    • Standard UVC USB-C webcams are 100% plug-and-play via USB-C Port 2.    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. POWER & AIRGAP INTEGRATION:                                              │
│    • Rear camera power-gated via TI TPS22918 load switch (0.000W standby).  │
│    • Hardware Airgap Switch physically shunts camera VDD to GND in STEALTH. │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Rear Camera Capabilities (Sony IMX708 12MP PDAF):**
  * **Multimodal Claude Code CLI:** Pass real-world photos directly to Claude (`claude "Inspect this breadboard wiring, verify pinout, and write the driver"`).
  * **5cm Macro PCB Inspection Loupe:** Uses the 10.3" 227 PPI E-Ink display as a real-time digital microscope to inspect 0402 SMD solder bridges, trace micro-fractures, and laser-etched IC part numbers.
  * **High-Speed Optical Airgap Data Ingestion (`txqr`):** Ingests multi-megabyte files, encrypted GPG archives, and tactical maps at 250+ kbps by reading 30 FPS animated QR fountain streams with zero RF emission.
  * **Night-Sky Celestial Navigation:** Captures night sky star patterns; local offline plate-solving (`astrometry.net`) computes astronomical heading and coordinates when GPS is jammed.

### 2.7 Audio & Standby Alert Subsystem
* **Dual-MEMS Noise-Cancelling Acoustic Array (Broadside Beamforming):**
  * **Sensors:** Dual matched Knowles **SPH0645LM4H-B** (or InvenSense ICS-43434) high-SNR I2S digital MEMS microphones.
  * **Acoustic Geometry:** Spaced **65 mm apart** along the top front bezel inside molded acoustic elastomer isolation boots with hydrophobic ePTFE dust/wind acoustic grilles.
  * **Bus Architecture:** Connected to the Broadcom I2S bus configured for stereo L/R time-division multiplexing over a single data line (`I2S_DIN`).
  * **Acoustic Beamforming & Wind Rejection:** Processed in Linux via PipeWire / WebRTC audio processing DSP (`solardeck-beamformd`). Computes differential phase delay between Left and Right microphones, forming an elliptical 60° directional voice pickup cone targeted at the operator's face while attenuating 18–24 dB of ambient wind gusts, road noise, and office chatter. Yields clean, near-studio 16 kHz voice streams for 99%+ accuracy in local Whisper and Claude Code voice prompts.
* **Physical Privacy Switch:** Hardware slide switch that physically breaks VDD to both microphones simultaneously (hardware-guaranteed un-hackable mute).
* **Primary Audio Output (Linux Master):** Maxim Integrated / Analog Devices **MAX98357A** I2S Class-D amplifier driving an internal 1W sealed acoustic chamber micro-box speaker.
* **High-Fidelity 3.5mm TRRS Audio Jack (Bottom Edge):**
  * **Connector:** IP67 water/dust sealed 3.5mm TRRS jack (**CUI Devices SJ2-35984A-SMT-TR** / Wurth Elektronik) mounted on the bottom chassis edge.
  * **Pinout Standard:** CTIA Standard (Tip = Left Audio, Ring 1 = Right Audio, Ring 2 = Ground, Sleeve = Microphone In).
  * **DAC / Headphone Amp:** High-performance, low-power 32-bit I2S Stereo DAC (**Texas Instruments PCM5102A**) with ground-centered charge-pump outputs (zero DC blocking capacitors required, 112 dB SNR).
  * **Hardware Auto-Mute Switch:** The 3.5mm jack features an isolated mechanical detection switch pin. When a headphone plug is inserted, it automatically asserts `SD_MODE` LOW on the internal MAX98357A Class-D amplifier, instantly silencing the internal speaker with zero software latency.
  * **Sovereign Private Listening:** Fully operational in Hardware Airgap Mode (where Bluetooth is powered to 0.000V), allowing developers to listen to audiobooks, podcasts, local AI speech synthesis, or decode radio AFSK audio packets with zero electromagnetic RF radiation.
* **Standby Alert Piezo (Co-Processor Master):** SMT **5.0mm micro-piezo acoustic buzzer** (75 dB @ 10cm, $0.25) directly connected to RP2350 PWM pin `RP2350_GPIO18`.
  * Sounds immediate chime tones for incoming 24/7 Meshtastic LoRa messages, RTC alarms, and barometric storm alerts without cold-booting Linux (draws < 2 mW during chirp).

### 2.7.1 Programmable Multi-Color RGB Notification Beacon ("Signal Halo")
Inspired by iconic ambient communicator status lights (Clicks, BlackBerry, Palm), SolarDeck features a flush, jewel-like RGB indicator on the upper-right front bezel:
* **Hardware:** High-efficiency Common-Anode RGB SMD LED (Kingbright `KPF-3224` / Cree `CLV1A-FKB`) coupled to a flush-mounted frosted optical light-pipe diffuser integrated into the matte glass bezel.
* **Control:** Driven directly by 3 hardware PWM channels on the RP2350 (`LED_R`, `LED_G`, `LED_B`) through 1.2kΩ / 2.2kΩ ballast resistors.
* **Zero Standby Leech:** Draws **0.000 µA** when turned off.
* **Breathing Engine:** Hardware PWM executes logarithmic gamma-corrected "breathing" and "heartbeat" pulsing curves at an average current of **< 0.18 mA**, providing glanceable ambient status without draining the battery.
* **Factory Color Mapping & Fully User-Programmable Profiles:**
  * **Breathing Amber (Solar / Charge Active):** Indicates battery is replenishing from folding panel or USB-C.
  * **Steady Dim Green (Charge Complete):** Battery is at 100%.
  * **Gentle Pulsing Emerald Green (LoRa Mesh Activity):** Unread Meshtastic text packet or tactical direct message received.
  * **Pulsing Sapphire Blue (Bluetooth / SnapDeck):** Keyboard pairing or active wireless connection.
  * **Pulsing Amethyst Purple (Comms Mention):** Discord ping, Slack huddle, or Matrix room notification.
  * **Urgent Strobe Ruby Red (Environmental Hazard / Critical Battery):** Rapid barometric drop (storm warning) or battery $<5\%$.
  * **Steady Dim Warm White (Ambient Locator / Nightstand):** Ultra-faint glow for finding the tablet in complete darkness.
  * **Physical Airgap Cutoff:** LED VDD rail is routed through the Hardware Airgap Switch; in `STEALTH` mode, LED power is physically cut to 0.000V.

### 2.7.2 Tactical Covert & Night Vision (NVG) Stealth Hardware Architecture
For field operations, astronomy observation, and night maneuvers requiring zero white/colored light bloom and acoustic silence:
* **Hardware Deep-Red Clamping (630 nm Monochromatic):** When switched to Covert Mode (`COVERT_MODE_EN` asserted), RP2350 hardware PWM permanently locks out Green and Blue LED drive channels. Red channel duty cycle is clamped to $<0.5\%$ ($<5\text{ µA}$ average drive current). The resulting ultra-dim $630\text{ nm}$ glow is fully readable with Gen 3+ Night Vision Goggles (NVG) and dark-adapted eyes, while undetectable to unaided eyes beyond 3 meters.
* **Dual CCT Frontlight Floor Clamping:** The TI TPS61163 frontlight driver hardware locks out the Cold-White string entirely, allowing only the Warm-Amber string to illuminate at Step 1 of 2048 ($<0.05\text{ lux}$), preserving rod cell night adaptation.
* **Acoustic Squelch:** Hardware gate pulls `MUTE` on the MAX98357A Class-D speaker amplifier and disables PWM oscillations to the SMT piezo buzzer, guaranteeing absolute zero sound emission.

### 2.8 Dual-Brain Display Isolation & Fail-Safe Bus Multiplexing (TI TMUX1575)
To allow the RP2350B co-processor to sip 4.5 mW of power while driving the E-Ink screen with the CM4 completely unpowered (0.000W), the high-speed SPI display bus passes through a Texas Instruments **TMUX1575** 8-channel SPDT bidirectional switch:

```
                      ┌──────────────────────┐
CM4 Display Bus ─────►│ S1A..S6A             │
(GPIO 8..11, 24, 25)  │                      │
                      │   TI TMUX1575        │─────► IT8951 EPDC Bus
RP2350B Display Bus ─►│ S1B..S6B     (D1..D6)│       (MOSI, MISO, SCK, CS, HRDY, RESET)
(GPIO 16..21)         │                      │
                      │  SEL       /EN       │
                      └───┬─────────┬────────┘
                          │         │
CM4_CLAIM_DISPLAY ────────┘         └── GND (Always Enabled)
(Pulled DOWN by 10kΩ to GND)
```

1. **Complete 6-Signal Galvanic Isolation (Power-Off Protection):**
   * Unlike 4-channel switches that leave status flags exposed, the **TMUX1575 (8-channel SPDT)** switches all 6 EPDC lines: `SPI_MOSI`, `SPI_MISO`, `SPI_SCLK`, `SPI_CS`, `HRDY` (Host Ready flag), and `RESET`.
   * The TMUX1575 features fail-safe inputs ($I_{\text{off}}$ circuitry): when CM4 `VDD_3V3` drops to 0.0V, the switch maintains giga-ohm impedance on the CM4 side, completely eliminating parasitic back-powering through internal ESD clamping diodes into unpowered rails ($I_{\text{leak}} < 10\text{ nA}$).
2. **Deterministic Hardware Arbitration:**
   * The `SEL` line is pulled down to GND via a 10 kΩ resistor, defaulting bus ownership to the RP2350B.
   * When Linux boots, the CM4 kernel driver negotiates with the RP2350B via GPIO interrupt handshake (`CM4_REQ_BUS` $\to$ `RP2350_ACK_READY`), then asserts `CM4_CLAIM_DISPLAY` HIGH to seize the display bus.
3. **DC Pigment Burn-In Protection:**
   * The RP2350B holds dedicated hardware control over `EPDC_PWR_EN` (TPS22918 load switch feeding the display rail).
   * Before cutting display power or transitioning states, firmware polls the IT8951 `HRDY` line to ensure the active waveform has completed, averaging net DC bias across all electrophoretic capsules to **0.0V** before sequencing down high-voltage rails (`VCOM` $\to$ `VGL` $\to$ `VGH` $\to$ `VDD`).

### 2.9 Dual Independent I2C Buses & Inter-Processor Telemetry Bridge
To completely eliminate bus arbitration lockups and the hardware address collision between the Goodix touch controller (`0x14`) and Bosch accelerometer (`0x14`), SolarDeck bifurcates I2C into two galvanically separated hardware domains:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SOLARDECK DUAL-BUS I2C ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. `I2C_ALWAYS_ON` BUS (RP2350 Master, 100 kHz, 3.3V Low-Power):           │
│    • 0x68: Maxim DS3231 TCXO Real-Time Clock (DNP Fallback Footprint)        │
│    • 0x55: TI BQ27441-G1 Impedance Track Battery Fuel Gauge                 │
│    • 0x40: TI INA3221 3-Channel System Power Ammeter                        │
│    • 0x48: TI TMP112 #1 (Battery Pouch Thermal Sensor)                      │
│    • 0x49: TI TMP112 #2 (E-Ink Backplane Thermal Sensor)                    │
│    • 0x15: Bosch BMA400 3-Axis Accelerometer (Hardwired SDO = VDDIO)        │
│    • 0x76: Bosch BMP390 Precision Barometer & Altimeter                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. `I2C_HOST` BUS (CM4 Master, 400 kHz Fast-Mode):                          │
│    • 0x09: Wacom EMR Stylus Digitizer Controller (`wacom_w9013`)            │
│    • 0x5D: Goodix GT911 Capacitive Multi-Touch Controller (Hardwired)       │
│    • 0x6A: TI BQ25895 Synchronous Buck Battery Charger                      │
│    • 0x42: RP2350 Virtual Telemetry Target (Exposes I2C_ALWAYS_ON to Linux) │
│    • External: USB-C Port 2 Host (Plug-and-play USB-to-I2C bridge dongles)   │
└─────────────────────────────────────────────────────────────────────────────┘
```
* **Collision Resolved:** Hardwiring BMA400 `SDO = VDDIO` locks the accelerometer to `0x15`, completely clear of Goodix touch `0x14/0x5D`.
* **Zero Bus Contention:** The RP2350 continuously samples sensors in deep sleep without ever colliding with Linux or waiting for bus arbitration.
* **Inter-Processor Telemetry Bridge:** Because `I2C_ALWAYS_ON` is physically isolated from the CM4 host to maintain low sleep power, the RP2350 acts as an intelligent hardware bridge:
  1. It samples battery thermals, ambient lux, and power rails in hardware.
  2. It exposes these metrics as an I2C Target device (`0x42`) on `I2C_HOST` and streams structured telemetry over the dedicated high-speed UART/USB CDC serial pipe (`/dev/ttyACM0`). Linux daemons (`solardeck-telemetryd`, `eink-refreshd`) read thermal and battery metrics directly from this bridge without requiring physical access to `I2C_ALWAYS_ON`.
* **External I2C Sensor Expansion via USB-C Port 2:**
  * To preserve the IP67 enclosure seal and avoid fragile external JST connectors, external sensor expansion (BME280, thermal imagers, Geiger counters) is routed through **USB-C Port 2** using standard USB-to-I2C/Qwiic bridge dongles (e.g. MCP2221A or RP2040 PIO).
  * Eliminates a dedicated chassis penetration and provides instant plug-and-play CLI access (`i2cdetect -y 1`) without exposing delicate 1.0mm pins to mud or rain.

### 2.10 Multi-Rail Power & Environmental Telemetry Sensors
* **Multi-Rail Digital Power Monitor (Texas Instruments INA3221 - KEPT FOR TELEMETRY):**
  * Replaces generic single ammeters with a 3-channel high-side current and bus voltage monitor over I2C.
  * Measures voltage and shunt current across three isolated domains simultaneously:
    * **Rail 1 (Compute):** CM4 core, LPDDR4, eMMC. Pinpoints CPU governor efficiency and memory leaks.
    * **Rail 2 (Display):** IT8951 EPDC and high-voltage rails. Pinpoints display power draw per waveform mode.
    * **Rail 3 (RF Radios):** Quectel modem, LoRa transceiver, Wi-Fi/BT. Catches hung cellular RRC sockets and rogue radio beacons.
  * Direct telemetry to Claude Code CLI and `solardeck-telemetryd` SQLite database for empirical algorithmic power profiling.
* **Coulomb Counter & Battery Fuel Gauge (Texas Instruments BQ27441-G1):**
  * Integrated Impedance Track™ fuel-gauge technology tracks exact milliamp-hours entering and leaving the pack (true Coulomb counting).
  * Measures battery cell internal impedance ($R_{\text{cell}}$ in mΩ) and computes true State-of-Health (SOH %) across 3,000+ charge cycles.
  * Enables charging optimization: signals the BQ25895 charger to reduce charge current when cell resistance rises or temperatures elevate, doubling battery operational lifespan to 10+ years.
* **Multi-Zone Precision Thermal Triad (Texas Instruments TMP112 + SoC Diode - KEPT FOR THERMAL LOGS):**
  * High-precision ($\pm 0.5^\circ\text{C}$), ultra-thin SOT-563 digital temperature sensors placed at strategic thermal points:
    * **Battery Zone:** Directly adhered to the pouch cell under the thermal protection sleeve for millidegree charging logs.
    * **Display Zone:** Adhered to the aluminum backplate behind the E-Ink panel. Directly feeds the IT8951 EPDC Look-Up Table (`TEMP_REG`) via the RP2350 bridge to dynamically adjust waveform voltage pulses as liquid microcapsule viscosity changes with temperature (eliminating ghosting in winter cold and bleeding in summer heat).
    * **Compute Zone:** Monitored via CM4 internal thermal diode and modem AT commands (`AT+QTEMP`).
* **Ambient Light & Solar Lux Sensing (Via Bezel Solar Strip & RP2350 ADC - Zero BOM):**
  * Rather than adding a dedicated photodiode IC, the RP2350's internal 12-bit ADC directly samples the open-circuit voltage ($V_{OC}$) of the top-bezel IXYS solar strip. Dynamic range spans from 0.01 lux up to 120,000 lux.
  * Enables dynamic E-Ink contrast optimization: disables front-lights completely in full sunlight ($>10,000\text{ lux}$), decreases anti-ghosting frequency, and calculates optimal solar panel angles when external folding panels are connected.
* **Motion & Kinematics Accelerometer (Bosch BMA400):**
  * Ultra-low-power 12-bit 3-axis accelerometer drawing **3.5 µA**.
  * Continuous autonomous motion detection: picks up physical desk wake interrupts, detects orientation (portrait vs. landscape), double-tap frame gestures, and free-fall conditions (firing an emergency interrupt to flush eMMC dirty buffers before ground impact).
* **GNSS Course-Over-Ground (Descoping Win for Compass):**
  * Compass heading is provided natively by the Quectel modem's integrated Qualcomm GNSS receiver calculating course-over-ground. Eliminates the separate MMC5603NJ magnetometer, avoiding complex magnetic hard/soft-iron distortion from chassis magnets.
* **Precision Barometer & Altimeter (Bosch BMP390):**
  * 0.1m relative altitude precision; samples ambient air pressure to plot barometric barographs on the ambient desk clock and alert the user to incoming weather fronts.
* **Benchtop Diagnostic Test Points & Hardware Probing Straps:**
  * Labeled 1.0mm gold SMD test pads (`TP_VCC_CORE`, `TP_VCC_MODEM`, `TP_SPI_SCK`, `TP_CHG_STAT`, `TP_AIRGAP_STAT`) exposed on the secondary PCB layer for oscilloscope and logic analyzer probing.

### 2.11 Dual USB-C Architecture, Driverless Monitor Mode & Host Protection
SolarDeck provides two rugged IP68 Type-C ports engineered with autonomous hardware protection against reverse currents and accidental cross-plugging:
* **Autonomous Ideal Diode Power OR-ing:**
  * Two Texas Instruments **LM66100** ultra-low $R_{\text{ON}}$ ideal diode ICs arbitrate VBUS inputs from Port 1 and Port 2.
  * Whichever port provides higher voltage (e.g. 12V folding solar panel vs 5V laptop) seamlessly feeds the BQ25895 charger.
  * Reverse leakage is **0.000 µA**, completely preventing circulating currents between two connected power sources.
* **USB-C Port 1 Dual-Role Port (DRP) & Secondary Monitor Mode:**
  * Managed by Texas Instruments **TUSB320** Configuration Channel (CC) controller paired with the Broadcom BCM2711's dedicated native USB 2.0 OTG PHY.
  * **Driverless USB Gadget Pipeline:** Connect a single USB-C cable to a laptop. The CM4 Linux kernel exposes a high-speed USB Gadget composite device (CDC-NCM / RNDIS network + UVC virtual display). SolarDeck receives the host screen stream (via Weylus, Deskreen, or Moonlight) and renders it using the 20ms 1-bit fast-typing waveform, while simultaneously drawing charging power from the host laptop.
* **Port 2 Current-Limited Host Switch (TI TPS2051B):**
  * When SolarDeck powers external USB devices (flash drives, keyboards) from Port 2, a **TI TPS2051B** power distribution switch limits output current to 1.5A with automatic short-circuit cutoff and thermal shutdown, protecting the tablet from rogue USB peripherals.

### 2.12 Physical Hardware Airgap Switch (Stealth / Zero-EMF Zen Reader Mode)
For true sovereign privacy, commercial flight compliance, sensitive compartmented facilities (SCIFs), and zero-distraction reading, SolarDeck incorporates a recessed, physical 2-position slide switch on the chassis side (`RADIO ACTIVE` vs. `AIRGAP STEALTH`):

```
                   ┌───────────────────────────────────────────┐
                   │        HARDWARE AIRGAP KILL SWITCH        │
                   └─────────────────────┬─────────────────────┘
                                         │
             ┌───────────────────────────┴───────────────────────────┐
             ▼                                                       ▼
   [NORMAL POSITION: 3.3V PASS]                          [AIRGAP POSITION: OPEN / 0V]
             │                                                       │
   GPIO Enable Lines Pass Freely                           Hardware Series Disconnect
   To TPS22918 Load Switch Gates                           Gates Pulled to GND via 100kΩ
             │                                                       │
             ▼                                                       ▼
   All Peripherals Under OS Control                        All Radio Load Switches Dead:
                                                           • Quectel EG25-G Modem & GNSS (0.000V)
                                                           • Semtech SX1262 LoRa (0.000V)
                                                           • BCM43455 Wi-Fi/BT (0.000V)
                                                           • Knowles MEMS Mic (0.000V)
                                                           • Rear Flush 12MP Camera (0.000V)
                                                           • Rear Backpack Pogo (0.000V)
```

1. **Hardware-Guaranteed Safe Series Disconnect (Zero GPIO Short-Circuit Risk):**
   * Unlike dangerous designs that short active microcontroller GPIOs directly to ground, the SolarDeck Airgap Switch acts as a **hardware series disconnect**:
     * In **NORMAL** mode, the switch passes the active-high gate enable signals from the CM4 and RP2350 to the `ON` pins of the respective TPS22918 load switches.
     * In **STEALTH** mode, the physical switch opens the gate drive nets and pulls each load switch `ON` pin to GND through dedicated 100 kΩ pull-down resistors. The microcontrollers' GPIO drivers are completely isolated and never shorted to ground, ensuring zero silicon stress while guaranteeing absolute 0.000V shutdown of all radio and sensor rails.
2. **Absolute Zero EMF & Radio Silence:**
   * **0.000 dBm RF output.** Completely undetectable by RF spectrum analyzers, direction-finding antennas, or cell-tower triangulators.
   * Eliminates all radio-frequency electromagnetic fields, leaving only the DC static magnetic field of the earth and low-frequency CPU clock traces shielded by internal PCB ground planes and the aluminum chassis.
3. **Pure Zen Reader / Scribe Operating Mode:**
   * When the switch is flipped, a sense line (`AIRGAP_STAT`) interrupts the Linux kernel.
   * Sway/Wayland renders a padlock badge: `[AIRGAP LOCKED: 0.000 dBm]`.
   * CPU governor immediately throttles to `powersave` (600 MHz single-core), and all radio daemons are frozen.
   * Active system power drops from 2.5W to **under 0.75W**!
   * **Battery Life:** Reading PDFs in Zathura, annotating with the battery-free Wacom stylus, and browsing offline Wikipedia in Kiwix lasts **35 to 42 continuous hours** on a single charge.
4. **Airgapped Cold-Storage Cryptographic Signer & Document Notary:**
   * When flipped to STEALTH, SolarDeck becomes an impenetrable, mathematically verifiable cold-storage signing station:
     * **Zero RF Transmission:** Hardware power switches disconnect the cellular modem, LoRa transceiver, and Wi-Fi/Bluetooth to 0.000V.
     * **Visual Optical Ingestion:** The operator scans an unsigned Bitcoin/Ethereum transaction QR code or document hash using the rear flush 12MP Sony IMX708 camera.
     * **High-Contrast On-Screen Verification:** The decoded recipient address, smart contract bytecode, and fee breakdown are rendered in high contrast on the 10.3" E-Ink paper screen.
     * **Hardware Authentication:** The operator authorizes the signature by tapping a physical YubiKey, Tangem, or Coldcard NFC hardware wallet against the top-bezel 13.56 MHz NFC antenna, or enters an airgapped passphrase.
     * **Optical Broadcast:** The signed transaction QR code is displayed on the 10.3" screen for an online smartphone or companion device to scan and broadcast to the public blockchain.
     * **Zero-Leakage Assurance:** Private keys never touch an internet-connected bus or memory space, backed by physical hardware power gates.

### 2.13 Anti-Phantom-Leakage Circuitry ($I_{\text{off}}$ & Cross-Domain I/O Isolation)
In low-power tiered architectures, cutting $V_{CC}$ to a subsystem is only half the battle. If digital I/O lines (UART, SPI, I2C, USB, GPIO) remain high (3.3V), current will leak backward through the unpowered chip's internal **ESD clamping diodes** into its unpowered $V_{CC}$ rail. This creates **parasitic back-powering (phantom leakage)**, which can silently bleed 20–80 mW of power, corrupt buses, and destroy the battery life.

To guarantee true 0.000V electrical isolation and zero phantom leakage across all power tiers, SolarDeck employs four strict hardware protections:

```
    POWERED DOMAIN (3.3V)                         UNPOWERED DOMAIN (0.000V)
┌───────────────────────────┐                 ┌───────────────────────────┐
│ Host Controller / Bus     │                 │ Target Radio / Peripheral │
│                           │                 │                           │
│   [TX / SCLK / MOSI] ─────┼────┐       ┌────┼─────► [Internal ESD Diode]│
│                           │    │       │    │                │          │
└───────────────────────────┘    │       │    │                ▼          │
                                 ▼       ▼    │          [VCC Rail: 0V]   │
                      ┌──────────────────────┐└───────────────────────────┘
                      │   TI TXU0104 / LVC   │   WITHOUT ISOLATION:
                      │ Fail-Safe I/O Buffer │   Current flows into 0V rail!
                      │  (I_off Support)     │   (20–80 mW Phantom Bleed)
                      ├──────────────────────┤
                      │  When Target VCC=0V: │   WITH SOLARDECK ISOLATION:
                      │  • Pins drop to Hi-Z │   • Leakage < 1 µA
                      │  • Current = 0.000 µA│   • Output Discharged to 0.0V
                      └──────────────────────┘
```

1. **Quick Output Discharge (QOD) on TPS22918 Switches:**
   * Each TPS22918 load switch includes an internal discharge transistor that connects the output rail (`VOUT`) to GND through a 470 Ω resistor whenever the switch is disabled.
   * Floating pins and residual capacitor charges are forcibly drained to true 0.000V within 50 microseconds.
2. **$I_{\text{off}}$ Partial-Power-Down Protection on All Inter-Domain Lines:**
   * All digital lines crossing between power tiers (UART to Quectel modem, UART to GPS, SPI to LoRa, and I2S to microphone) pass through Texas Instruments **TXU0104** or **SN74LVC1G125** buffers featuring **$I_{\text{off}}$ circuitry**.
   * When either $V_{CCA}$ or $V_{CCB}$ is 0V, the device automatically forces all I/O lines into a high-impedance (Hi-Z) state, guaranteeing leakage current **$I_{\text{leak}} < 1\text{ µA}$**.
3. **Display Bus Multiplexer Isolation (TMUX1575):**
   * The high-speed SPI bus to the IT8951 controller is isolated by the TI TMUX1575 8-channel switch. Its fail-safe inputs tolerate up to 5.5V independent of supply voltage, completely preventing display signals from back-powering the CM4 in deep sleep.
4. **Physical Line-Breaker for Microphone & Cameras:**
   * The physical airgap switch cuts `VDD_MIC`, shunts `I2S_CLK` and `I2S_DATA` to GND, and disables the camera load switches, cutting `VCC_CAM_FRONT` and `VCC_CAM_REAR` to 0.000V.

#### Summary of SolarDeck Tiered Power Domains

| Operating Tier | Active Brain | Display Driver | Powered Subsystems | Total Power Draw | Battery Runtime (35 Wh Pack) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 0: Dormant Standby** | RP2350 (10 µA sleep) | Display OFF (Static) | Internal 32kHz RTC, BQ27441 (CM4 0V, Radios 0V, Hi-Z)| **< 0.1 mW** | **10+ Years shelf life** |
| **Tier 1: Ambient Clock & Zen Reader**| RP2350 (12MHz Cortex-M33)| IT8951 (PSRAM Double-Buf)| 8MB PSRAM, BMA400, BMP390 (30ms Page Turns) | **~4.5 mW** | **300+ Days (10 Months)** |
| **Tier 2: Perpetual LoRa Mesh Node** | RP2350 (48MHz M33 / RISC-V)| IT8951 (Status Banner) | Semtech SX1262 LoRa Transceiver (Autonomous routing)| **12 to 15 mW** | **80+ Days (2.6 Months)** |
| **Tier 3: Paper-Feel Scribe Slate** | CM4 (1 core @ 600 MHz) | IT8951 (DU 1-bit Buffer) | Wacom EMR (240 Hz, Hover-gated), eMMC | **~0.60 W** | **58 Hours** active (460h study) |
| **Tier 4: Adaptive Mixed Workstation**| CM4 (Dynamic DVFS 0.6–1.5G)| IT8951 (Dynamic Waveforms)| Wi-Fi/LTE, Web, Twitter, Discord, Claude Code CLI | **~1.40 W** | **25 Hours** screen-on (3–6 days) |
| **Tier 5: Multimedia & Audio Station**| CM4 (Hardware Audio Pipeline)| IT8951 (A2 Motion / GC16)| Knowles Mic, MAX98357A Box Speaker, Wi-Fi/LTE | **~1.70 W** | **20 Hours** continuous audio/calls |
| **Tier 6: AI Compile Turbo** | CM4 (1.8GHz Quad A72) | IT8951 (Sway Wayland) | All Radios, SnapDeck Keyboard, Parallel Compiles | **2.8 W to 3.8 W** | **9 to 12 Hours** continuous |

---

### 2.14 Tool-Free Field Recovery & Factory Diagnostic Test Points
To ensure the sealed IP67 tablet is 100% field-recoverable without screwdrivers or factory teardowns:
* **Single Recessed IP67 Pinhole Recovery Button (Bottom Edge):**
  * Actuates a micro-tactile switch pulling CM4 `nRPIBOOT` to GND. When connected to a host computer via USB-C Port 1, the CM4 enumerates as a mass storage device via `rpiboot`, allowing instant reflashing of the Linux rootfs.
  * Co-processor (RP2350) firmware recovery and updates are handled directly by Linux over dedicated internal SWD lines (`solardeck-coproc-flash`) with automatic hardware watchdog rollback, eliminating the need for a second physical chassis button.
* **Bed-of-Nails Automated Factory Test Matrix (PCBA Bottom):**
  * Standardized 1.27mm gold pogo pads: `TP_5V0`, `TP_3V8`, `TP_3V3`, `TP_1V8`, `TP_VBAT`, `TP_SWD_CLK`, `TP_SWD_DIO`, `TP_UART_TX`, `TP_UART_RX` for automated SMT testing and initial silicon flashing.

### 2.15 Industrial ESD & Transient Voltage Suppression Matrix
To withstand field operations where exposed gold pogo pins and USB-C ports touch metallic surfaces, wet desks, or receive high-voltage human-body static shocks in dry environments, SolarDeck integrates an exhaustive, multi-tier ESD protection network complying with **IEC 61000-4-2 Level 4 (±15 kV air discharge, ±8 kV contact discharge)**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SOLARDECK ESD & TRANSIENT SUPPRESSION                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. HIGH-SPEED DATA LINES (USB-C Ports 1 & 2, SnapDeck & Backpack Pogo):    │
│    • TI TPD4E05U06 4-Channel Bidirectional Ultra-Low Capacitance TVS Array  │
│    • Capacitance: 0.5 pF (guarantees zero attenuation of 480 Mbps signals)  │
│    • Clamping Voltage: 8.5V @ 5A (instantaneous absorption < 1 ns)          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. EXPOSED POWER RAILS (VBUS 5V & Battery Input Rails):                     │
│    • Vishay SMAJ5.0A / SMF05C High-Surge Clamping TVS Diodes (400W peak)    │
│    • Absorbs inductive kickback when snapping magnetic keyboard on/off      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. CO-PROCESSOR & SENSOR I/O PINS (Buttons, Airgap Switch, Bezel Touch):    │
│    • Bourns CD0603-T05C Miniature Bidirectional TVS Diodes on all lines    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.16 PCBA Signal Integrity & 6-Layer Impedance-Controlled Stackup
To eliminate EMI radiation from dual 1 Gbps MIPI-CSI camera interfaces, guarantee 50Ω coplanar waveguide matching for LTE/LoRa RF traces, and prevent digital noise from leaking into sensitive GPS and audio LNAs, SolarDeck mandates a **6-layer impedance-controlled board stackup** (Standard JLC2313 / Isola FR408HR):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SOLARDECK 6-LAYER PCBA LAYER ASSIGNMENT                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 1 (Top Signal & RF):                                                  │
│ • 50Ω Coplanar Waveguides (LoRa SMA, Quectel LTE Main/Div, GPS L1 RF traces)│
│ • 90Ω Differential Pairs for USB 2.0 (Port 1, Port 2, Pogo Docks)           │
│ • SMT Component Pads & Local Decoupling                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 2 (Inner 1 - Continuous Ground Plane):                                │
│ • Solid 1oz unbroken copper plane across entire 10.3" footprint             │
│ • Provides ultra-low-impedance return path for all Top Layer signals        │
│ • Zero slots or breaks under RF or high-speed differential pairs            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 3 (Inner 2 - High-Speed Routing):                                     │
│ • 100Ω Differential Pairs for Dual MIPI-CSI (Sony IMX708 PDAF & IMX219)     │
│ • 24 MHz SPI Display Bus to IT8951 EPDC (MOSI, MISO, SCLK, CS)              │
│ • Sandwiched between Layer 2 and Layer 4 ground pours (Stripline Shielding) │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 4 (Inner 3 - Power Plane & Secondary Ground):                         │
│ • Power Distribution Islands: VDD_5V0 (Boost), VDD_3V8 (Modem), VDD_3V3, 1V8│
│ • Star-ground copper pours around analog audio and BQ25895 switching nodes  │
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 5 (Inner 4 - Solid Ground Plane):                                     │
│ • Continuous secondary reference plane isolating digital and power switching│
├─────────────────────────────────────────────────────────────────────────────┤
│ Layer 6 (Bottom Signal & Test Points):                                      │
│ • Low-Speed Busses (I2C_ALWAYS_ON, I2C_HOST, UART, GPIOs)                   │
│ • 1.27mm Gold Bed-of-Nails Automated Factory Test Pads                      │
│ • Heat-Spreading Copper Thermal Vias coupling CM4/Modem heat to chassis     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.17 Tactical Field Controls & All-Weather Torrential Rain Mode
To provide 100% mission reliability in severe sub-zero weather, dust storms, and driving tropical rains where gloves must be worn and touchscreens fail:
* **IP67 Sealed 5-Way Tactical Navigation Rocker (Left Bezel):**
  * Sub-miniature multi-directional tactical joystick (**ALPS SKRHABE010** / Panasonic EVQ-W, $0.85) integrated into the left chassis grip area.
  * Sealed behind an overmolded silicone rubber boot (IP67 certified).
  * Direct electrical connection to 5 dedicated RP2350 GPIO inputs (`NAV_UP`, `NAV_DOWN`, `NAV_LEFT`, `NAV_RIGHT`, `NAV_PRESS`) with hardware RC debounce filtering.
  * **Functions:**
    * **Single-Handed Gloved Navigation:** Operators wearing thick winter or Kevlar tactical gloves can flip pages, scroll terminal command history, cycle Sway Wayland workspaces, and select menu items without touching the glass.
    * **Direct Hardware Dimming:** Holding `NAV_PRESS` and rocking Up/Down adjusts frontlight circadian brightness smoothly.
* **Torrential Rain / Water-Lock Mode (Wacom-Only Operating Mode):**
  * **The Problem:** Water droplets falling on capacitive glass act as conductive finger touches, creating erratic cursor jumps and phantom clicks in heavy downpours.
  * **The Solution:** A dedicated hardware-assisted **Water-Lock Mode**, toggled by holding the 5-way rocker center-press for 2 seconds (or via the terminal command `solardeck-waterlock on`).
  * **Mechanism:** Shuts off power to the Goodix capacitive touch controller completely via its dedicated TPS22918 load switch.
  * **Why It Works:** The battery-free **Wacom EMR digitizer operates on electromagnetic resonance (~560 kHz)** and is completely unaffected by surface water or liquid sheets. With capacitive touch deactivated, the user can write, sketch, annotate maps, and navigate terminal apps with the stylus while water streams down the display.

### 2.18 Native Micro-HDMI 4K External Video Output & Campervan E-Ink Dual-Screen Dock
* **Native Silicon Path:** The Broadcom BCM2711 / CM4 exposes two hardware HDMI 2.0 transmitters. `HDMI0` is routed to a recessed, sealed **Micro-HDMI port** (Type-D) on the chassis flank, protected by a Texas Instruments **TPD4E05U06** 4-channel ultra-low capacitance ($C_{\text{IO}} = 0.5\text{ pF}$) ESD protection array complying with IEC 61000-4-2 Level 4 (±15 kV air discharge).
* **Max Workable Display:**
  * **Resolution:** Single display up to **4K UHD (3840 × 2160 @ 60 Hz)** or 1440p/1080p @ 60 Hz with Broadcom VideoCore VI hardware acceleration.
  * **Physical Size:** Infinite (13.3" to 85").
* **Giant External E-Ink Secondary Monitor (The Daylight Campervan Dock):**
  * Fully supports commercial large-format E-Ink monitors: **13.3-inch** (2200 × 1650, 4:3 — Dasung Paperlike HD / Boox Tab X) and **25.3-inch** (3200 × 1800, 16:9 — Boox Mira Pro / Dasung Paperlike 253).
  * **Why E-Ink Second Monitors Dominate Off-Grid Vans:**
    * **0.000W Static Power Sipping:** Unlike LED/OLED monitors that burn 8W–25W continuous backlight power on static text/code, E-Ink monitors consume power ONLY when flipping pixels. Static reading, schematics, and code inspection consume **0.000W** holding power.
    * **Typing Power:** A 13.3" E-Ink monitor averages ~1.5W during active typing vs. 12W–15W for a backlit LCD in ambient daylight.
    * **Zero Glare:** Under direct van sunlight through open slider doors or skylights, LCDs wash out; E-Ink gets crisper and higher contrast without increasing backlight wattage.
* **Campervan Dual-Head Wayland Integration:**
  * Driven natively by Sway/Wayland multi-head output.
  * Internal 10.3" E-Ink serves as dedicated live van telemetry palette (Victron battery SoC, water levels, LoRa chat, terminal scratchpad).
  * External 25.3" E-Ink / 4K monitor serves as primary high-density code and Kiwix browser workspace.

### 2.19 Blackout Supercapacitor Emergency SOS Beacon (Zero-Battery Survival Boot)
* **The Operational Ceiling:** In catastrophic backcountry scenarios where the main LiFePO4 battery pack is deeply discharged to 0.000V or physically damaged, standard mobile terminals cannot boot.
* **The Supercapacitor Circuit:**
  * A **1.0F 3.3V ultra-low-leakage EDLC supercapacitor** (AVX BestCap / Eaton / Cornell Dubilier, $0.95) is wired directly across the Always-On 3.3V rail fed by the IXYS SM141K06L front micro-solar strip via a low-drop Schottky diode (BAT54CW).
* **Zero-Battery Survival Sequence:**
  1. **Direct Sunlight Charging:** In direct sunlight (100,000 lux), the front solar strip generates ~35 mA, charging the 1.0F supercapacitor from 0.0V to 3.3V in **12 to 15 minutes** with no battery installed.
  2. **150ms Cold-Boot Burst:** The TI TPS62840 buck-boost asserts `POWER_GOOD`, releasing the RP2350 reset line.
  3. **Atomic Coordinate Capture & Broadcast:** The RP2350 cold-boots in **15ms**, wakes the Semtech SX1262 LoRa transceiver, reads last-known GPS coordinates from RTC NVRAM, and transmits a high-power (+22 dBm) encrypted emergency SOS distress burst on 915 MHz / 868 MHz Meshtastic emergency channels (drawing 110 mA for 45ms = 0.016 Joules).
  4. **Indelible E-Ink Distress Stamping:** While the remaining supercapacitor energy bleeds down, the RP2350 pulses the IT8951 EPDC to burn an indelible high-contrast distress placard onto the 10.3" E-Ink screen: `EMERGENCY SOS BROADCAST ACTIVE | COORD: 21.3069 N, 157.8583 W | TIME: 2026-10-19 14:00 UTC | BLOOD: O-POS | ZERO-BATTERY SOLAR BEACON`.
  5. **Bistable Permanence:** The distress text remains frozen on the screen with **0.000W power draw** indefinitely, visible to SAR teams even if the device is submerged or abandoned.

### 2.20 Cascaded Edge Audio ML Hardware & Acoustic Barge-In Pipeline
* **The Standby Power Problem:** Running full continuous speech recognition on the quad-core Cortex-A72 CM4 consumes 1.8W to 2.4W, killing a 32Wh battery in under 16 hours.
* **The Cascaded Wake Hierarchy:**
  1. **Tier 1 (Acoustic Activity Detect - VAD):** Knowles SPH0645 MEMS acoustic front-end comparator detects ambient sound energy $> 45\text{ dB SPL}$ (<0.05 mW power).
  2. **Tier 2 (microWakeWord on RP2350 Co-Processor):**
     * RP2350 Cortex-M33 ingests 16 kHz audio via PIO DMA.
     * Evaluates an INT8-quantized depthwise separable convolutional neural network (DS-CNN) wake model (`microWakeWord`).
     * Power: **14 mW active** (yielding **80+ days continuous hands-free listening** on battery).
     * Optional drop-in: Dedicated **Syntiant NDP120** Neural Decision Processor footprint (<140 µW active listening, 20+ year standby).
  3. **Tier 3 (CM4 Voice Biometrics & Whisper Engine):**
     * If "Hey Deck" matches, RP2350 fires `WAKE_CM4` GPIO interrupt.
     * CM4 resumes from S2idle in 250ms, ingests buffered audio, and computes 256-d voice embedding via **Resemblyzer** ($<35\text{ms}$).
     * If cosine similarity $\ge 0.78$ with owner's enrolled biometric voice print, command is processed via `whisper.cpp` (base.en); bystanders and background radio chatter are rejected.
* **Acoustic Echo Cancellation (AEC) & Hardware Loopback for Seamless Barge-In:**
  * To allow the operator to interrupt ("barge in") while SolarDeck is speaking or playing audio:
  * The digital audio stream driving the **MAX98357A I2S Class-D speaker amplifier** is looped back in hardware/software into the PipeWire/ALSA DSP mixer.
  * SpeexDSP / WebRTC AEC3 Acoustic Echo Cancellation subtracts the speaker's own output from the Knowles microphone inputs in real time ($<5\text{ms}$ latency), enabling the system to hear the user's voice interruption even at 100% speaker volume.

### 2.21 Zero-Hardware Wacom Precision Caliper & Hover CAD Mode
* **Wacom EMR Hover Tracking (Zero-Touch Stylus):**
  * The Wacom EMR digitizer senses the battery-free stylus tip up to **10.0 mm above the protective glass**.
  * Software tracks $(X, Y)$ coordinates with **0.1 mm precision** and 200 Hz update rates without the stylus physically touching the display.
  * Allows measuring fragile specimens (botanical leaves, wet paint, live insects) suspended above the glass.
* **Capacitive Multi-Touch Contact Centroid Ellipses (Conductive Parts):**
  * Placing conductive metal components (drill bits, bolts, washers, brass heat-set inserts) directly onto the hardened glass triggers localized mutual-capacitance sensor node depressions.
  * The Goodix touch controller computes contact centroid ellipses; software extracts the major axis length (bolt length) and minor axis width (bolt diameter) with sub-millimeter precision automatically with zero manual inputs.

---

## 3. Universal Mechanical Mount, Handheld Thumb Grips & Open Keyboard Architecture

To eliminate $25,000 in custom injection tooling risk and 6 months of bespoke ZMK keyboard firmware development, SolarDeck V1 descopes the proprietary keyboard in favor of an **Open Keyboard Ecosystem & Universal Mechanical Mount**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 UNIVERSAL MECHANICAL MOUNT & OPEN KEYBOARDS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. TOTAL INPUT FREEDOM:                                                     │
│    • Pair any existing Bluetooth LE 5.0 or USB-C keyboard                   │
│      (ThinkPad TrackPoint, Keychron, NuPhy Air60, Corne split, Apple Magic).│
│ 2. REAR UNIVERSAL MECHANICAL MOUNT:                                         │
│    • 4x M2.5 Brass Threaded Heat-Set Inserts (50mm & 75mm VESA spacing).    │
│    • Embedded MagSafe-Compatible Neodymium N52 Magnetic Anchor Array.       │
│ 3. HANDHELD BED/COUCH MODE (3D-Printed BlackBerry Q20 Thumb Grip):          │
│    • Open-source 3D-printed snap-on bracket mounts an off-the-shelf $20      │
│      Solder Party BlackBerry Q20 tactile clicky keyboard beneath display.   │
│ 4. SOLID UNIBODY BACKPLATE & OEM STAND COMPATIBILITY:                       │
│    • Descoped failure-prone friction hinges for 100% rigid unibody shell.   │
│    • Snaps effortlessly to any MagSafe desk stand or standard OEM easel.    │
│ 5. PHASE 2 SNAPDECK RESERVED FOOTPRINT:                                     │
│    • 5-pin hermetic magnetic pogo bus pads retained on PCBA bottom edge     │
│      for future turnkey SnapDeck clamshell accessory production.            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Total Input Freedom & Ergonomic Portability
* **The Philosophy:** Developers are fiercely loyal to their preferred keyboard switches, layouts, and keycaps. Forcing a proprietary scissor keyboard alienates mechanical keyboard purists and increases device failure rates.
* **Low-Latency Wireless & Wired Connectivity:**
  * **Bluetooth LE 5.0:** Linux `bluez` pairs instantly with any standard wireless keyboard. Latency is $<8\text{ ms}$.
  * **USB-C Port 2 (Host):** Plug in any high-end custom mechanical keyboard, split keyboard (Corne, Ergodox), or macro pad with full QMK/VIA programmability.

### 3.2 Rear Universal Mechanical Anchor & MagSafe Array
* **M2.5 Threaded Brass Inserts:** Four M2.5 heat-set brass inserts embedded into the rigid rear PA12/aluminum chassis on standard 50mm and 75mm square grid spacing. Provides a rock-solid, vibration-proof anchor for:
  * Camera tripod 1/4"-20 adapter plates.
  * RAM Mount ball joints for vehicle dash, sailboat bulkhead, or aircraft cockpit mounting.
  * Heavy-duty desk-arm articulation clamps.
* **MagSafe Magnetic Ring:** An embedded 36-magnet neodymium N52 array (standard 54mm outer diameter with vertical alignment magnet) allows instantaneous magnetic snap-on attachment to:
  * **MOFT Snap Origami Tablet Stands:** Folds flat to 3mm for transport; deploys instantly into 25° (stylus writing), 45° (lap typing), and 60° (reading) angles in Portrait and Landscape.
  * **Campervan Bulkhead & Refrigerator Pucks:** $5 magnetic wall discs securely mount SolarDeck to metal walls, vehicle galleys, or toolboxes.
  * **Pocket Communicator Docking:** The Clicks Communicator (Qi2/MagSafe) snaps flush to the rear backplate during transit with zero brackets.
* **Wacom EMR Magnetic Isolation:** A **0.1mm Mu-Metal / Ferrite shielding foil sheet** is laminated across the entire rear surface of the Wacom digitizer PCB (§1.2), isolating the 560 kHz resonant pen sensing loop and ensuring **zero coordinate warping, jitter, or offset** when using strong magnetic kickstands or phone mounts.

### 3.3 Handheld Bed/Couch Mode: 3D-Printed BlackBerry Q20 Grip & Clicks Communicator Chin-Dock
* **The Use Case:** Typing on a 10.3" tablet while lounging in a hammock, lying in bed, or walking in the field is impossible with a full-size desk keyboard.
* **Option A: Solder Party BlackBerry Q20 Grip:**
  * Weighs only 45 grams; costs ~$20.
  * Features 35 clicky tactile dome keys + BlackBerry optical trackpad.
  * Connects over internal Bluetooth LE or low-profile USB-C jumper.
  * Enables effortless two-thumb terminal coding, chat, and prompt generation while holding the tablet like a Game Boy.
* **Option B: Clicks Communicator Center-of-Gravity Chin-Dock:**
  * **The Problem Solved:** Cantilevering a phone below the bottom bezel creates a 227mm lever arm that exhausts wrists.
  * **The Overlap Solution:** A 3D-printed SLS PA12 snap cradle clips the Clicks Communicator **over the front face of the lower bezel/screen**, suspended 1.0mm above the E-Ink glass with 0.5mm Poron foam cushioning.
  * **Ergonomics:** Hands grip the rigid lower chassis of SolarDeck. The 510g tablet mass is cradled directly between your palms with **zero rotational wrist torque**, creating a balanced handheld terminal (like a Steam Deck or Nintendo DS).
  * **Dual-Screen Hybrid:** Top 10.3" E-Ink runs Wayland terminal/code (shifted via `solardeck-chin-dock`); bottom 4.03" AMOLED runs live color Google Maps, telemetry widgets, and tactile QWERTY thumb keys. Wired 3cm flat U-cable bridges into USB-C Port 2 for sub-1ms typing and 15W reverse charging.


### 3.4 Phase 2 SnapDeck Footprint Preservation
* To ensure the carrier motherboard never requires a revision if a custom magnetic pogo keyboard is manufactured in Phase 2, the bottom edge of the PCBA retains the SMD landing pads for the **5-pin hermetic magnetic pogo connector** (`VBUS`, `USB_D-`, `USB_D+`, `GND`, `ID_SENSE`) with dedicated TVS ESD diodes.

---

## 4. Mechanical Enclosure & Ingress Protection (IP67)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 3M 5952 VHB Waterproof Acrylic Foam Tape around Glass   │
├─────────────────────────────────────────────────────────────┤
│ 2. CNC 6061-T6 Aluminum Unibody / SLS PA12 Nylon Shell     │
├─────────────────────────────────────────────────────────────┤
│ 3. Continuous Tongue-and-Groove Hollow Silicone O-Ring     │
├─────────────────────────────────────────────────────────────┤
│ 4. GORE Protective ePTFE Pressure Equalization Vent        │
├─────────────────────────────────────────────────────────────┤
│ 5. Overmolded 85A TPU Shock-Absorbing Armor Corners        │
└─────────────────────────────────────────────────────────────┘
```

1. **Waterproofing Seams:** Continuous perimeter channel with 1.5 mm hollow-core silicone gasket, compressed 30% by 12 stainless steel M2.5 Torx screws.
2. **Glass Bonding:** Front glass is recessed 1 mm below an aluminum lip and bonded from behind with 3M 5952 VHB tape.
3. **Pressure Equalization:** A **Gore-Tex ePTFE vent plug** on the bottom plate allows internal air pressure to equalize during temperature swings (preventing vacuum moisture suction) while blocking 100% of liquid water and humidity.
4. **Drop Armor:** 85A durometer TPU rubber bumpers permanently molded around all four corners to absorb 4-foot drops onto concrete or rock.

---

## 4. Enclosure, Ingress Protection & Thermal Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SOLARDECK PHYSICAL ENCLOSURE & THERMALS                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ Dimensions: 248 mm (W) × 188 mm (H) × 9.8 mm (D) | Device Mass: ~510 grams  │
│                                                                             │
│ [FRONT & EDGE TOPOLOGY]                                                     │
│ • Chemically Etched Matte Glass Overlay (15% Haze, Paper-Texture Friction)  │
│ • 10.3" E-Ink Kaleido 3 / Carta 1200 Panel + Wacom EMR Digitizer           │
│ • 0.1mm Mu-Metal / Ferrite Magnetic Shielding Layer (Behind Digitizer)      │
│ • Top Bezel: IXYS Micro-Solar Strip + 13.56 MHz NFC Antenna Loop (YubiKey)  │
│ • Bottom Edge: IP67 3.5mm TRRS Audio Jack + Recessed Recovery + USB-C Port 1│
│ • Right Flank: Magnetic Precision Stylus Clamping (N52 Array + Align Groove)│
│ • Left Flank: 5-Way Tactical Navigation Rocker (ALPS SKRH) + Airgap Switch  │
│                                                                             │
│ [INTERNAL COPLANAR CHASSIS STACKUP (X-Y ARRANGEMENT)]                       │
│ • Front Glass + E-Ink Panel + Wacom EMR Layer: 2.8 mm uniform               │
│ • Side-by-Side Co-Planar Layout behind Display:                             │
│   - Left/Lower Cavity: Ultra-Thin 5.5 mm Prismatic 35 Wh Battery Pack       │
│   - Right/Upper Cavity: 6-Layer Mainboard PCBA + CM4 Module (6.0 mm)        │
│ • Total Internal Cavity Depth: 6.0 mm (Chassis Total Thickness: 9.8 mm)     │
│ • Thermal Isolation Barrier between Battery Cell and Compute Module         │
│                                                                             │
│ [REAR CHASSIS & THERMAL MANAGEMENT]                                         │
│ • CM4 SoC faces outward toward the rear chassis                             │
│ • 1.5mm Thermal Gap Pad (6.0 W/m·K) bridges SoC to Aluminum Backplate       │
│ • Zero Heat Migration into temperature-sensitive E-Ink microcapsules        │
│ • Universal Mechanical Mount: 4x M2.5 Threaded Inserts (50mm/75mm) + MagSafe│
│ • The "Cold Storage Vault" (Concealed inside gasketed M.2 service hatch):   │
│   - 3x Uniform Friction-Fit MicroSD Card Slots (Supports Nano-SIM via shell)│
│   - 1x Stainless Steel SIM Ejector Tool Retaining Clip                      │
│ • GORE ePTFE Pressure Vent (PMF100396): Equalizes altitude barometric delta │
│   while maintaining IP67 water/dust seal (tested safe to 1 meter immersion) │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Ingress Protection (IP67 Engineering)
* **Perimeter Gasket:** Continuous CNC silicone O-ring tongue-and-groove channel sealing front lens to rear housing.
* **Ports & Connectors:**
  * 2x IP68 waterproof Type-C receptacles with rear epoxy potting and silicone outer O-rings.
  * 1x Top-edge IP67 bulkhead SMA female connector with silicone sealing washer.
  * Front 5-pin and rear 8-pin pogo pin connectors feature solid gold-plated brass barrels hermetically potted in high-temperature liquid epoxy.
* **Acoustic Sealing:** Knowles MEMS microphone and 1W speaker sound chambers ported through waterproof acoustic ePTFE hydrophobic membranes.
* **Barometric Equalization:** GORE PMF100396 vent plug prevents internal vacuum or pressure buildup during air travel or mountain ascents.

### 4.2 Magnetic Precision Stylus Clamping & Field Transport
* Rather than boring a 140 mm hollow internal tube through the chassis (which steals 10 cm³ of internal battery volume and introduces complex internal seals), SolarDeck adopts **Magnetic Precision Side-Clamping (reMarkable 2 / iPad Pro style)**:
  * An array of high-grade **Neodymium N52 rare-earth magnets** is embedded directly into the right aluminum chassis flank, paired with a shallow tactile alignment channel.
  * Delivers a solid **1.2 kgf retention force**, securely locking standard 8.0mm–9.5mm EMR styluses (Staedtler Noris Digital, Lamy AL-star, or reMarkable Marker) to the side of the tablet.
  * For transit in rugged backpacks, the SnapDeck keyboard folio incorporates a secondary elastic retention loop for double drop-proof security.

### 4.3 Shock-Proof Compute Module Retention & Thermal Heat-Pipe Clamp
To prevent the CM4’s dual 100-pin Hirose DF40 micro-connectors from unseating during 4-foot drops or high-vibration off-road vehicle transport:
* **Mechanical Retention Standoffs:** Four M2 brass threaded standoffs soldered directly to the carrier board PCBA surrounding the CM4 perimeter.
* **CNC Anodized Aluminum Clamp Plate:** A precision CNC aluminum retention bracket clamps over the CM4 module, secured by 4 stainless steel Torx screws. This applies constant, uniform mechanical compression across both Hirose connectors, ensuring they can **never unseat or suffer intermittent contact during severe drops**.
* **Integrated Thermal Conduction Bridge:** A 1.5mm high-conductivity thermal interface pad ($6.0\text{ W/m}\cdot\text{K}$) directly couples the Broadcom BCM2711 SoC silicon die to the aluminum clamp, which in turn bonds to the outer chassis backplate via graphite heat-spreading sheets, exhausting compute heat outward with zero thermal migration into the E-Ink panel.

### 4.4 Hardware Anti-Tamper & Cryptographic Key Management
To protect sensitive private keys, encrypted credentials, and communications logs against physical capture or laboratory disassembly:
* **Chassis Intrusion Micro-Switch:** A hermetically sealed sub-miniature limit switch (C&K PTS645 / Panasonic EVQ) is mounted to the carrier PCBA and held depressed by the CNC aluminum backplate.
* **RP2350 TrustZone Zeroization Architecture:**
  * When the backplate is loosened or pried open while "Vault Security" is armed, the intrusion switch opens, asserting a Non-Maskable Interrupt (NMI) on the RP2350.
  * In $<100\text{ ns}$, the RP2350 secure core wipes the volatile session decryption tokens stored in retention SRAM, instantly unmounting encrypted F2FS partitions on the eMMC and dropping the SoC into permanent hardware lockdown.
  * **No Unintended Bricking on Battery Replacement:** Unlike naive designs where master keys exist only in volatile RAM, the master keys are derived from RP2350 hardware-locked OTP memory with Arm TrustZone access control paired with a user-defined passphrase. If the main battery is fully depleted or removed for routine servicing, the device does not brick: upon re-powering, the legitimate user enters their recovery passphrase / BIP-39 mnemonic seed to reconstitute the session tokens.
* **Manual Emergency Purge:** An operator can manually trigger immediate session zeroization and flash lockout by depressing the recessed `REC_MCU` pinhole switch continuously for 10 seconds.

### 4.5 Micro-Solar Bezel Thermal Decoupling & Expansion Barrier
* **Radiant Heat Problem:** In direct desert sunlight ($>900\text{ W/m}^2$), dark monocrystalline silicon solar cells reach surface temperatures of $65^\circ\text{C} \text{ to } 75^\circ\text{C}$. Direct contact with the E-Ink panel backplane causes microcapsule discoloration and localized pigment degradation.
* **Aerogel Thermal Decoupling Barrier:** A **0.5 mm die-cut Pyrogel aerogel insulation strip** (thermal conductivity $<0.015\text{ W/m}\cdot\text{K}$) is laminated between the top micro-solar bezel and the E-Ink panel frame, blocking 95% of conductive heat migration into the display.
* **PCBA Milled Thermal Relief Slot:** A 1.0 mm continuous routed slot in the carrier PCB isolates the BQ25504 nano-power boost harvester thermally from the low-noise analog sensor cluster and Wacom digitizer grounding plane.

### 4.6 The "Cold Storage Vault" (Concealed Inside Gasketed M.2 Service Hatch)
To make SolarDeck the ultimate sovereign, off-grid archive workstation without adding a single cent in electronics or compromising exterior unibody waterproofing:
* **Gasketed M.2 Service Hatch Cavity:** Molded directly into the inner face of the flush, IP67 silicone-gasketed M.2 SSD service hatch on the rear chassis unibody (secured by 2x stainless M2 captive screws).
* **Storage Capacity:**
  * **3x Uniform Friction-Fit MicroSD Card Pockets:** Accommodates three extra MicroSD cards (e.g., Card 1: 1TB offline Kiwix Wikipedia + Library of Genesis; Card 2: bootable Tails / Arch Linux rescue OS; Card 3: encrypted personal git vault).
  * **Nano-SIM Compatibility:** Standardizes on uniform MicroSD pocket dimensions (15.0mm × 11.0mm × 1.0mm). To carry a spare Nano-SIM, users insert the SIM into a standard $0.05 plastic MicroSD-shaped carrier shell. This eliminates asymmetric mold tooling and gives users complete freedom to carry 3x MicroSDs or any combination of SDs and SIMs.
  * **1x Stainless Steel SIM Ejector Pin Clip:** Snaps a standard metal SIM ejector tool (or safety pin) securely into place.
* **Mechanical Retention & Weather Protection:**
  * Each card pocket is lined with molded 85A TPU retention micro-ribs and a thumb-notch for quick extraction with a fingernail.
  * Zero rattle, zero vibration, and 100% immune to drops.
  * Completely protected inside the IP67 sealed internal envelope—invisible from the outside, tamper-resistant, and impervious to weather, dirt, and water.
* **Bill of Materials Cost:** **$0.00** (Zero electrical parts; pure CAD negative-cavity geometry).

---

## 5. Modular Tactical RF & SIGINT USB-C Multi-Tool (External Add-on)

In SolarDeck V1, the Tactical RF Multi-Tool is packaged as a rugged, low-profile snap-on pod that mates directly to external high-speed **USB-C Port 2**. This eliminates the complex rear 8-pin hermetic pogo bus from the V1 core chassis, saving $12.00 in BOM and tooling, eliminating PCB routing congestion, and preserving a completely solid, watertight unibody rear chassis.

To interface wideband SDR (USB), Sub-GHz (SPI), 125 kHz RFID (analog/pulse), NFC (I2C/SPI), and IR blaster (PWM) across a single high-speed USB-C port:
* **Core Bridge MCU & USB Hub Architecture:**
  * **USB 2.0 Hub Controller:** Genesys Logic **GL850G** (or FE1.1s, $0.35) 2-port USB 2.0 hub IC splits the USB pair between the RTL2832U SDR and the bridge MCU.
  * **Bridge Microcontroller:** Raspberry Pi **RP2040** (Dual Cortex-M0+, $0.70) interfaces to the host via USB CDC / HID, natively driving:
    * Texas Instruments **CC1101** over dedicated SPI.
    * **EM4095** 125 kHz RFID demodulator over analog/pulse-timing lines.
    * NXP **PN532** NFC over high-speed I2C/SPI.
    * Vishay **TSAL6200** IR LEDs via high-current MOSFET driven by RP2040 PIO/PWM.

### 5.1 Tactical RF Multi-Tool (Flipper Zero Suite)
* **Sub-GHz Radio:** Texas Instruments **CC1101** transceiver (300–348 MHz, 387–464 MHz, 779–928 MHz) driven via SPI by the backpack RP2040 with dedicated tuned spring whip antenna for 315/433 MHz remote replay and decoding.
* **NFC (13.56 MHz):** NXP **PN532** controller with dedicated PCB trace loop antenna for ISO14443A/MIFARE read/emulate.
* **RFID (125 kHz):** **EM4095** analog front-end demodulator with a ferrite-core resonant coil for low-frequency access cards, timed directly by RP2040 PIO state machines.
* **Infrared Transceiver:** Vishay **TSOP4838** 38 kHz demodulator receiver + dual high-power **TSAL6200** 940 nm LEDs driven by 2N7002 MOSFET for 15-meter IR blasting.

### 5.2 Tactical Sky-Scan & SIGINT Suite (Air & Satellite Radio Analysis)
While the core tablet natively receives positioning and orbital timing from 4 GNSS satellite constellations (GPS, Galileo, GLONASS, BeiDou via the Quectel EG25-G modem's integrated Qualcomm GNSS receiver), wideband RF scanning of airplanes and atmospheric satellites is offloaded to the backpack:
* **Wideband Software Defined Radio (SDR):** Integrated **RTL2832U + R860/R820T2** tuner (24 MHz to 1766 MHz).
* **Dedicated Top-Right SMA Port:** Tuned for wideband VHF/UHF tactical reception.
* **Capabilities Enabled:**
  1. **Airplane ADS-B Radar (1090 MHz & 978 MHz UAT):** Real-time flight tracking, altitude, squawk codes, and flight paths rendered on offline vector maps via `dump1090` / `readsb`.
  2. **Aircraft Voice & ACARS (118–137 MHz):** Decodes air-traffic control telemetry and aircraft maintenance datalinks.
  3. **Direct Weather Satellite Imagery (137 MHz):** Direct reception of orbiting **NOAA 15/18/19** (APT) and **Meteor-M2** (LRPT) satellites as they pass overhead, decoding live infrared cloud maps via `satdump` with zero internet.
  4. **Marine AIS Vessel Tracking (161.975 / 162.025 MHz):** Tracks commercial cargo ships, tankers, and coastal vessel positions via `rtl-ais`.
* **Thermal & Power Architecture:** An active SDR tuner draws **1.5W to 2.2W (300–450 mA @ 5V)** and runs warm. Housing it in the rear snap-on backpack keeps heat away from the battery and E-Ink display, while allowing the core tablet to maintain its 10+ hour workstation endurance when not scanning the skies.

### 5.3 Modular Backpack Hermetic 8-Pin Interface: Dedicated Pinout & Make-First-Break-Last Hot-Plug Architecture
To ensure high-speed USB 2.0 integrity, robust I2C enumeration, and absolute protection against hot-plug latch-up or arcing when snapping accessories on in the field:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             SOLARDECK REAR 8-PIN HERMETIC EXPANSION POGO BUS                │
├───────┬──────────────┬───────────────┬──────────────────────────────────────┤
│ Pin # │ Signal Name  │ Voltage / Spec│ Functional Description               │
├───────┼──────────────┼───────────────┼──────────────────────────────────────┤
│ Pin 1 │ `VBUS_5V`    │ +5.0V @ 1.5A  │ Main backpack power via TPS22918     │
│ Pin 2 │ `USB_D-`     │ 3.3V Diff     │ USB 2.0 High-Speed Negative          │
│ Pin 3 │ `USB_D+`     │ 3.3V Diff     │ USB 2.0 High-Speed Positive          │
│ Pin 4 │ `GND`        │ 0.0V Return   │ Heavy-copper system ground           │
│ Pin 5 │ `I2C_SDA`    │ 3.3V (HOST)   │ EEPROM backpack ID & register config │
│ Pin 6 │ `I2C_SCL`    │ 3.3V (HOST)   │ Fast-Mode 400 kHz clock              │
│ Pin 7 │ `GPIO_IRQ`   │ 3.3V CMOS In  │ Low-latency interrupt (CC1101/PN532) │
│ Pin 8 │ `BP_DETECT_L`│ 3.3V Pull-Up  │ Hardware Interlock Sense (Shorter Pin)│
└───────┴──────────────┴───────────────┴──────────────────────────────────────┘
```

* **Make-First-Break-Last (MFBL) Protection:** Pin 8 (`BP_DETECT_L`) is manufactured **0.5 mm shorter** than Pins 1–7.
  * **On Docking:** `GND`, `VBUS`, and data pins establish contact first; Pin 8 contacts last, pulling the line to ground. Only upon detecting `BP_DETECT_L == LOW` does the system assert the gate of the TPS22918 load switch to energize `VBUS_5V`.
  * **On Undocking:** Pin 8 breaks contact first. The RP2350/CM4 instantly trips an interrupt, disabling `VBUS_5V` power within $<10\text{ µs}$ before data pins physically separate, completely eliminating hot-plug sparks, inductive kickback, and digital I/O latch-up.
* **ESD & Signal Protection:** All 8 lines pass through an onboard Texas Instruments **TPD4E05U06** TVS array directly adjacent to the hermetic pogo barrel headers.

---

## 6. Zero-Brick Hardware & Electrical Safeguards

To enable fearless experimentation, on-the-fly firmware flashing, core architecture switching (ARM vs. RISC-V), and autonomous AI agent code execution without risk of bricking or physical hardware damage, SolarDeck implements an ironclad, multi-layer hardware defense matrix:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE 6-LAYER ZERO-BRICK DEFENSE MATRIX                    │
├───────┬───────────────────────────┬─────────────────────────────────────────┤
│ Layer │ Safeguard                 │ What It Prevents                        │
├───────┼───────────────────────────┼─────────────────────────────────────────┤
│ **1** │ Silicon Mask ROM (RP2350) │ Unbrickable hardware recovery bootloader│
│ **2** │ Dual-Bank A/B Flash & WDT │ Auto-rollback if new code hangs or faults│
│ **3** │ Current-Clamping Resistors│ Physical silicon pad burnout from shorts│
│ **4** │ Analog Battery Comparators│ Thermal runaway (cannot be bypassed)    │
│ **5** │ Immutable Linux OverlayFS │ OS corruption restored in 3 seconds     │
│ **6** │ Hardware Recessed Boot Pin│ 1-click factory restore from any laptop │
└───────┴───────────────────────────┴─────────────────────────────────────────┘
```

### 6.1 Silicon-Level Mask ROM Bootloader (RP2350)
* **Factory Etched Silicon:** The RP2350 micro-coprocessor contains a factory bootloader etched into **physical silicon Mask ROM** at TSMC during chip fabrication.
* **Permanence:** This code is physically part of the silicon die. It cannot be erased, overwritten, corrupted, or glitched by any software bug, root privilege escalation, or AI coding loop.
* **Guaranteed Recovery:** Even if an experimental binary completely overwrites the external 16MB QSPI flash with random zeroes or corrupted code, the RP2350 ROM bootloader will execute upon hardware reset, exposing the internal Serial Wire Debug (SWD) interface to the CM4 (`/dev/spidev0.1` or GPIO bit-bang) and USB Mass Storage / UF2 mode to external host PCs.

### 6.2 Dual-Bank A/B Flash Partitioning with Hardware Watchdog Rollback
The 16MB Winbond W25Q128JVS QSPI NOR flash memory is partitioned into two distinct physical segments:
1. **Bank A (0x000000 – 0x7FFFFF, 8MB): Factory "Golden Image" (Cryptographically Locked):**
   * Contains the baseline, production-verified power management, S2idle wake listener, battery charging loop, and emergency IT8951 recovery waveforms.
   * Marked read-only by the RP2350 internal memory protection unit (MPU).
2. **Bank B (0x800000 – 0xFFFFFF, 8MB): "Playground / Experimental" Bank:**
   * Receives live on-the-fly firmware flashes, custom RISC-V DSP routines, experimental PIO microcode, and alternative operating kernels (e.g., Zephyr / FreeRTOS).
* **Hardware Watchdog Ping Gate (8-Second Timeout):**
  * When booting Bank B, the hardware watchdog timer (RP2350 WDT) is configured for an 8-second window.
  * The newly flashed firmware must execute its boot sequence, run an internal self-test, verify sensor communications, and toggle the hardware watchdog clear pin.
  * If the experimental code hangs in an infinite loop, triggers a HardFault/Crash, or configures clocks incorrectly, the hardware watchdog trips. The boot ROM increments an internal boot-fail counter and **instantly rolls back execution to Bank A (Golden Image)** in $<2.5\text{ ms}$.

### 6.3 Electrical Current-Limiting & Logic Contention Clamping
* **The Contention Threat:** If buggy or AI-generated firmware inadvertently configures a GPIO connected to a shared bus (e.g., UART, SPI, or inter-processor interrupt lines) as a low-impedance output driving `3.3V` (HIGH) while the CM4 is simultaneously driving that same net to `0.0V` (LOW), a short circuit is created, causing excessive current draw and physical pad burnout.
* **Hardware Protection:**
  * All inter-processor digital signal lines passing between the BCM2711 (CM4) and RP2350 pass through **330 Ω to 1 kΩ series current-limiting resistors** or **TI TXU0104 unidirectional / TI TXS0108E auto-direction sensing level shifters** with integrated output clamping.
  * **Current Limit:** $I_{\text{max}} = \frac{3.3\text{V}}{1,000\,\Omega} = 3.3\text{ mA}$.
  * Even under continuous, indefinite pin-state contention, current is physically restricted to safe levels well below the 16 mA maximum pin rating of the Broadcom and RP2350 silicon pads.
  * Peripheral load switch enable lines (TI TPS22918) incorporate 100 kΩ pull-down resistors to ground, ensuring that floating or uninitialized GPIOs during boot/reflash default safely to **OFF**.

### 6.4 Autonomous Analog Battery & Thermal Protection
* **Hardware-Autonomous Silicon Safety:** Over-temperature and over-voltage charging cutoffs do not rely on running firmware or operating system software.
* **Dedicated NTC Analog Comparator:** The 10 kΩ NTC thermistor inside the LiFePO4 battery pouch connects directly to the `TS` (Temperature Sense) analog pin on the **Texas Instruments BQ25895** buck charger.
* **Instant Analog Trip:** If cell temperature exceeds 45°C during charging or 60°C during discharge, internal analog comparators within the BQ25895 silicon instantly terminate charging current and disconnect the load switch in nanoseconds. This hardware interlock operates independently of the Linux kernel, RP2350 firmware, or software state.

### 6.5 Physical Recessed Hardware Recovery Switch ("Dead-Man Recovery")
* A miniature recessed tactile switch is located adjacent to USB-C Port 1 on the lower chassis flank, accessible via a standard paperclip or SIM-eject tool.
* **Operation:**
  * **Holding the switch while inserting USB-C:**
    * Physically grounds the RP2350 `BOOTSEL` pin, forcing it into USB Mass Storage Mode (appears on any connected Mac, PC, or Linux machine as a USB flash drive for instant drag-and-drop `.uf2` image recovery).
    * Connects CM4 `nRPIBOOT` pin to GND, placing the BCM2711 into USB slave bootloader mode (`rpiboot`).
  * Allows a completely blank, wiped, or corrupted device to be completely re-provisioned and re-flashed in under 60 seconds from an external host using standard open-source tools.
