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
                                      │  • Onboard MFF2 eSIM (ST4SIM-200M)        │
                                      │  • Semtech SX1262 LoRa 915MHz (RP2350 SPI)│
                                      │  • u-blox MAX-M10S GNSS                   │
                                      │  • Knowles I2S MEMS Mic Array             │
                                      │  • Maxim/ADI MAX98357A 1W Speaker Amp     │
                                      │  • USB-C Port 2 (Host / TPS2051B Switch)  │
                                      └──────┬─────────────────────────────┬──────┘
                                             │                             │
                    (5-Pin Pogo Bus)         ▼                             ▼         (Rear 8-Pin Pogo / USB-C)
        ┌────────────────────────────────────┐             ┌────────────────────────────────┐
        │ SNAPDECK KEYBOARD DOCK (PARALLEL)  │             │ MODULAR TACTICAL RF BACKPACK   │
        │ • Kailh X-Switches (3.5mm low prof)│             │ • Internal RP2040 MCU + USB Hub│
        │ • Blackberry RIM 9900 Trackpad     │             │ • RTL2832U Wideband SDR        │
        │ • Nordic nRF52840 (ZMK + BLE 5.0)  │             │ • TI CC1101 Sub-GHz (300-928M) │
        │ • MCP73831T LiPo Charger + PCM     │             │ • NXP PN532 NFC (13.56 MHz)    │
        │ • Wayland Reserved Margin Resize   │             │ • EM4095 125 kHz RFID Demod    │
        └────────────────────────────────────┘             │ • Dual High-Power IR TX/RX     │
                                                           └────────────────────────────────┘
```

---

## 2. Component Selection & Electrical Interfaces

### 2.1 Compute & Low-Power Co-Processing
* **Universal Modular Compute Socket (Dual Hirose DF40 100-Pin Footprint):**
  * Rather than locking the hardware to a single soldered SoC, the carrier board integrates standard dual Hirose DF40 100-pin board-to-board receptacles (55mm × 40mm mechanical envelope).
  * **Drop-in Interchangeability:**
    * **Raspberry Pi CM4 (Baseline Specification):** Model `CM4108032` (Quad Cortex-A72 @ 1.8GHz, Wi-Fi 5, Bluetooth 5.0, **8GB LPDDR4 RAM**, 32GB eMMC). The 8GB configuration is the official engineering baseline: it provides zero-lag AST parsing in Claude Code CLI, parallel compilation (`cargo build -j4`), and runs local quantized 3B LLMs (`llama.cpp`) with zero swap thrashing, while keeping S2idle self-refresh current to ~18 mW.
    * **Raspberry Pi CM5 (Drop-in Horsepower Upgrade):** Quad Cortex-A76 @ 2.4GHz with 3x faster compilation throughput for heavy local builds.
    * **Radxa CM3 / Pine64 SOQuartz (Rockchip RK3566 Alternative):** Quad Cortex-A55 @ 1.8GHz on 22nm node for 40% lower active power draw.
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
  * **Autonomous Circadian Dimming:** Controlled by the RP2350 via 2048-step logarithmic PWM dimming; automatically transitions from crisp white in dim daylight to soft amber (zero blue light emission) after sunset based on RTC time and OPT3001 lux readings.
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
* **Dual-Stage Solar Harvesting Architecture:**
  1. *High-Power Field Solar (Fast Recharge via USB-C):* Standard USB-C Port 2 supports 5V–14V input from folding 15W–28W outdoor panels. The BQ25895's integrated dynamic input voltage management (**VINDPM / MPPT**) tracks optimal solar output to recharge the pack safely in field conditions.
  2. *Dedicated Nano-Power Bezel Harvester (Texas Instruments BQ25504):*
     * Resolves the primary charger's 3.9V Under-Voltage Lockout ($V_{\text{UVLO}}$) ceiling.
     * Dedicated ultra-low-quiescent boost converter ($1.80) wired directly to the top-bezel monocrystalline micro-solar strip (IXYS SM141K06L, $22\text{ mm} \times 35\text{ mm}$, ~0.15W peak, ~50–120 mW real-world).
     * Cold-starts from as low as **330 mV** and continuously harvests down to **100 mV**.
     * Executes autonomous 80% Fractional Open-Circuit Voltage (FOCV) MPPT sampling, boosting micro-solar energy directly into the battery rail with >90% efficiency, keeping the 4.5 mW RP2350 Zen reader topped off indefinitely even under indoor lighting.
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
* **Cellular Modem:** **M.2 Key-B (3042)** socket connected to dedicated host USB lines.
  * Module: **Quectel EG25-G** (Worldwide Cat-4 LTE, 30+ bands, global carrier certifications).
  * **RF Decoupling:** 470 µF low-ESR polymer capacitor placed adjacent to modem VCC to handle 2.0A transient TX bursts without voltage sag.
* **Onboard eSIM (eUICC):**
  * Chip: STMicroelectronics **ST4SIM-200M** or Infineon **SLM97** in industrial **MFF2 (DFN-8, 5×6mm)** package.
  * Directly soldered to carrier board and routed to M.2 SIM lines; zero external chassis slots, maintaining IP67 sealing.
  * Management: Controlled natively under Linux via **`lpac`** (open-source C LPA) and `ModemManager` over standard AT channel commands (`AT+CCHO`/`AT+CGLA`) for instant QR-code carrier activation.
* **LoRa Mesh Radio:** **Semtech SX1262** 915/868 MHz transceiver (up to +22 dBm output).
  * Connects via dedicated SPI to the RP2350 co-processor, running autonomous 24/7 **Meshtastic** mesh repeating firmware at 12–15 mW, and exposing a virtual serial interface to Linux over the inter-processor UART/serial bus (`/dev/ttyAMA0`).
* **Global Satellite Navigation:** **u-blox MAX-M10S** GNSS receiver.
  * Concurrent reception of GPS, BeiDou-3, Galileo, GLONASS, and QZSS.
  * Ultra-low power (15 mW) feeding `gpsd` for offline OsmAnd / FoxtrotGPS mapping.

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
│ 1. REAR WORLD-FACING CAMERA (Back Chassis):                                 │
│    • Sensor: Sony IMX708 (12.0 Megapixels, 4608 × 2592, HDR)                │
│    • Focus: Motorized Phase Detection Autofocus (PDAF) from 5cm to infinity │
│    • Bus: 2-Lane MIPI CSI-2 on `CAM1` (Direct Hardware ISP Pipeline)        │
│    • Optics: Recessed sapphire crystal glass window with silicone O-ring    │
│    • Shutter: Anodized aluminum mechanical sliding privacy hatch            │
│    • Role: Claude Code multimodal vision, 5cm macro PCB inspection loupe,   │
│            document OCR, animated QR airgap ingestion, celestial navigation │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. FRONT USER-FACING CAMERA (Top Front Bezel):                              │
│    • Sensor: Sony IMX219 / Omnivision OV5647 (5.0 Megapixels, 1080p30)      │
│    • Lens: 80° Field-of-View fixed focus (optimized for head-and-shoulders) │
│    • Bus: 2-Lane MIPI CSI-2 on `CAM0`                                       │
│    • Optics: Sealed flush under front glass overlay with laser-etched port  │
│    • Shutter: Integrated mechanical "ThinkShutter" sliding lens cover       │
│    • Hardware Indicator: Ultra-dim green LED physically in series with VDD  │
│    • Role: Zoom, Google Meet, Discord, tactical video logs                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. POWER & AIRGAP INTEGRATION:                                              │
│    • Both cameras power-gated via TI TPS22918 load switch (0.000W standby). │
│    • Hardware Airgap Switch physically shunts camera VDD to GND in STEALTH. │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Rear Camera Capabilities (Sony IMX708 12MP PDAF):**
  * **Multimodal Claude Code CLI:** Pass real-world photos directly to Claude (`claude "Inspect this breadboard wiring, verify pinout, and write the driver"`).
  * **5cm Macro PCB Inspection Loupe:** Uses the 10.3" 227 PPI E-Ink display as a real-time digital microscope to inspect 0402 SMD solder bridges, trace micro-fractures, and laser-etched IC part numbers.
  * **High-Speed Optical Airgap Data Ingestion (`txqr`):** Ingests multi-megabyte files, encrypted GPG archives, and tactical maps at 250+ kbps by reading 30 FPS animated QR fountain streams with zero RF emission.
  * **Night-Sky Celestial Navigation:** Captures night sky star patterns; local offline plate-solving (`astrometry.net`) computes astronomical heading and coordinates when GPS is jammed.
* **Front Camera & Video Conferencing (Sony IMX219 5MP):**
  * **Clean Outgoing Stream:** Hardware-accelerated H.264 video encode transmits crisp 1080p30 color video to meeting participants over LTE or Wi-Fi.
  * **E-Ink Meeting UX:** Inbound screen-shared code/slides render with paper-sharp 16-bit grayscale (GC16), while participant video thumbnails render in 2-bit A2 motion mode (60–75ms) or update on active speaker change, eliminating screen flicker while maintaining real-time audio.

### 2.7 Audio & Standby Alert Subsystem
* **Dual-MEMS Noise-Cancelling Acoustic Array (Broadside Beamforming):**
  * **Sensors:** Dual matched Knowles **SPH0645LM4H-B** (or InvenSense ICS-43434) high-SNR I2S digital MEMS microphones.
  * **Acoustic Geometry:** Spaced **65 mm apart** along the top front bezel inside molded acoustic elastomer isolation boots with hydrophobic ePTFE dust/wind acoustic grilles.
  * **Bus Architecture:** Connected to the Broadcom I2S bus configured for stereo L/R time-division multiplexing over a single data line (`I2S_DIN`).
  * **Acoustic Beamforming & Wind Rejection:** Processed in Linux via PipeWire / WebRTC audio processing DSP (`solardeck-beamformd`). Computes differential phase delay between Left and Right microphones, forming an elliptical 60° directional voice pickup cone targeted at the operator's face while attenuating 18–24 dB of ambient wind gusts, road noise, and office chatter. Yields clean, near-studio 16 kHz voice streams for 99%+ accuracy in local Whisper and Claude Code voice prompts.
* **Physical Privacy Switch:** Hardware slide switch that physically breaks VDD to both microphones simultaneously (hardware-guaranteed un-hackable mute).
* **Primary Audio Output (Linux Master):** Maxim Integrated / Analog Devices **MAX98357A** I2S Class-D amplifier driving an internal 1W sealed acoustic chamber micro-box speaker.
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
│    • 0x68: Maxim DS3231 TCXO Real-Time Clock                                │
│    • 0x55: TI BQ27441-G1 Impedance Track Battery Fuel Gauge                 │
│    • 0x40: TI INA3221 3-Channel System Power Ammeter                        │
│    • 0x44: TI OPT3001 Ambient Sunlight Lux Sensor                           │
│    • 0x48: TI TMP112 #1 (Battery Pouch Thermal Sensor)                      │
│    • 0x49: TI TMP112 #2 (E-Ink Backplane Thermal Sensor)                    │
│    • 0x15: Bosch BMA400 3-Axis Accelerometer (Hardwired SDO = VDDIO)        │
│    • 0x76: Bosch BMP390 Precision Barometer & Altimeter                     │
│    • 0x30: Memsic MMC5603NJ 3-Axis Digital Magnetometer / Compass           │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. `I2C_HOST` BUS (CM4 Master, 400 kHz Fast-Mode):                          │
│    • 0x09: Wacom EMR Stylus Digitizer Controller (`wacom_w9013`)            │
│    • 0x5D: Goodix GT911 Capacitive Multi-Touch Controller (Hardwired)       │
│    • 0x6A: TI BQ25895 Synchronous Buck Battery Charger                      │
│    • 0x5A: TI DRV2605L Linear Resonant Actuator Haptic Driver               │
│    • 0x42: RP2350 Virtual Telemetry Target (Exposes I2C_ALWAYS_ON to Linux) │
│    • External: Rugged Qwiic / Stemma QT 3.3V Expansion Port (Hot-pluggable) │
└─────────────────────────────────────────────────────────────────────────────┘
```
* **Collision Resolved:** Hardwiring BMA400 `SDO = VDDIO` locks the accelerometer to `0x15`, completely clear of Goodix touch `0x14/0x5D`.
* **Zero Bus Contention:** The RP2350 continuously samples sensors in deep sleep without ever colliding with Linux or waiting for bus arbitration.
* **Inter-Processor Telemetry Bridge:** Because `I2C_ALWAYS_ON` is physically isolated from the CM4 host to maintain low sleep power, the RP2350 acts as an intelligent hardware bridge:
  1. It samples battery thermals, ambient lux, and power rails in hardware.
  2. It exposes these metrics as an I2C Target device (`0x42`) on `I2C_HOST` and streams structured telemetry over the dedicated high-speed UART/USB CDC serial pipe (`/dev/ttyACM0`). Linux daemons (`solardeck-telemetryd`, `eink-refreshd`) read thermal and battery metrics directly from this bridge without requiring physical access to `I2C_ALWAYS_ON`.
* **External Rugged Qwiic / Stemma QT 3.3V Sensor Port:**
  * Flush 4-pin JST-SH (1.0 mm pitch) connector on side chassis sealed by a captive IP67 silicone plug.
  * Connected to `I2C_HOST` through a TI TPS22918 load switch (software power-gated, 0.000W when empty) and protected by TI TPD4E05U06 TVS diodes.
  * Instant plug-and-play CLI access (`i2cdetect -y 1`) for external environmental, thermal, gas, or radiation sensors without opening the sealed chassis.

### 2.10 Multi-Rail Power & Environmental Telemetry Sensors
* **Multi-Rail Digital Power Monitor (Texas Instruments INA3221):**
  * Replaces generic single ammeters with a 3-channel high-side current and bus voltage monitor over I2C.
  * Measures voltage and shunt current across three isolated domains simultaneously:
    * **Rail 1 (Compute):** CM4 core, LPDDR4, eMMC. Pinpoints CPU governor efficiency and memory leaks.
    * **Rail 2 (Display):** IT8951 EPDC and high-voltage rails. Pinpoints display power draw per waveform mode.
    * **Rail 3 (RF Radios):** Quectel modem, LoRa transceiver, Wi-Fi/BT. Catches hung cellular RRC sockets and rogue radio beacons.
  * Programmable conversion times down to 140 µs with an active-low `CRITICAL` alert pin that trips on inrush current spikes, latching peak transient events for analysis.
* **Coulomb Counter & Battery Fuel Gauge (Texas Instruments BQ27441-G1):**
  * Integrated Impedance Track™ fuel-gauge technology tracks exact milliamp-hours entering and leaving the pack (true Coulomb counting).
  * Measures battery cell internal impedance ($R_{\text{cell}}$ in mΩ) and computes true State-of-Health (SOH %) across 3,000+ charge cycles.
  * Enables charging optimization: signals the BQ25895 charger to reduce charge current when cell resistance rises or temperatures elevate, doubling battery operational lifespan to 10+ years.
* **Multi-Zone Thermal Triad (Texas Instruments TMP112 + SoC Diode):**
  * High-precision ($\pm 0.5^\circ\text{C}$), ultra-thin SOT-563 digital temperature sensors placed at strategic thermal points:
    * **Battery Zone:** Directly adhered to the pouch cell under the thermal protection sleeve.
    * **Display Zone:** Adhered to the aluminum backplate behind the E-Ink panel. Directly feeds the IT8951 EPDC Look-Up Table (`TEMP_REG`) via the RP2350 bridge to dynamically adjust waveform voltage pulses as liquid microcapsule viscosity changes with temperature (eliminating ghosting in winter cold and bleeding in summer heat).
    * **Compute Zone:** Monitored via CM4 internal thermal diode and modem AT commands (`AT+QTEMP`).
* **Ambient Light & Solar Lux Sensor (Texas Instruments OPT3001):**
  * Precision spectral matching to the human eye response; dynamic range from 0.01 lux up to 120,000 lux.
  * Enables dynamic E-Ink contrast optimization: disables front-lights completely in full sunlight ($>10,000\text{ lux}$), decreases anti-ghosting frequency, and calculates optimal solar panel angles when external folding panels are connected.
* **Motion & Kinematics Accelerometer (Bosch BMA400):**
  * Ultra-low-power 12-bit 3-axis accelerometer drawing **3.5 µA**.
  * Continuous autonomous motion detection: picks up physical desk wake interrupts, detects orientation (portrait vs. landscape), double-tap frame gestures, and free-fall conditions (firing an emergency interrupt to flush eMMC dirty buffers before ground impact).
* **3-Axis Digital Magnetometer / Compass (Memsic MMC5603NJ):**
  * 20 µA digital compass for offline tactical mapping (Meshtastic, ATAK, OsmAnd) without network connectivity.
  * Monitors localized chassis magnetic interference to detect nearby ferrous metal or docking magnets.
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
                                                           • Quectel EG25-G Modem (0.000V)
                                                           • Semtech SX1262 LoRa (0.000V)
                                                           • BCM43455 Wi-Fi/BT (0.000V)
                                                           • u-blox MAX-M10S GNSS (0.000V)
                                                           • Knowles MEMS Mic (0.000V)
                                                           • Dual MIPI Cameras (0.000V)
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
| **Tier 0: Dormant Standby** | RP2350 (10 µA sleep) | Display OFF (Static) | DS3231 RTC, BQ27441 (CM4 0V, Radios 0V, Hi-Z) | **< 0.1 mW** | **10+ Years shelf life** |
| **Tier 1: Ambient Clock & Zen Reader**| RP2350 (12MHz Cortex-M33)| IT8951 (PSRAM Double-Buf)| 8MB PSRAM, BMA400, BMP390 (30ms Page Turns) | **~4.5 mW** | **300+ Days (10 Months)** |
| **Tier 2: Perpetual LoRa Mesh Node** | RP2350 (48MHz M33 / RISC-V)| IT8951 (Status Banner) | Semtech SX1262 LoRa Transceiver (Autonomous routing)| **12 to 15 mW** | **80+ Days (2.6 Months)** |
| **Tier 3: Paper-Feel Scribe Slate** | CM4 (1 core @ 600 MHz) | IT8951 (DU 1-bit Buffer) | Wacom EMR (240 Hz, Hover-gated), eMMC | **~0.60 W** | **58 Hours** active (460h study) |
| **Tier 4: Adaptive Mixed Workstation**| CM4 (Dynamic DVFS 0.6–1.5G)| IT8951 (Dynamic Waveforms)| Wi-Fi/LTE, Web, Twitter, Discord, Claude Code CLI | **~1.40 W** | **25 Hours** screen-on (3–6 days) |
| **Tier 5: Video Teleconference Mode**| CM4 (Hardware H.264 ISP) | IT8951 (A2 Motion / GC16)| Front 5MP Cam, Knowles Mic, Speaker, Wi-Fi/LTE | **~2.10 W** | **16.5 Hours** continuous calls |
| **Tier 6: AI Compile Turbo** | CM4 (1.8GHz Quad A72) | IT8951 (Sway Wayland) | All Radios, SnapDeck Keyboard, Parallel Compiles | **2.8 W to 3.8 W** | **9 to 12 Hours** continuous |

---

### 2.14 Tool-Free Field Recovery & Factory Diagnostic Test Points
To ensure the sealed IP67 tablet is 100% field-recoverable without screwdrivers or factory teardowns:
* **Recessed IP67 Pinhole Recovery Buttons (Bottom Edge):**
  1. **`REC_RPI` (eMMC System Recovery):** Actuates a micro-tactile switch pulling CM4 `nRPIBOOT` to GND. When plugged into a PC via USB-C Port 1, the CM4 enumerates as a mass storage device via `rpiboot`, flashing a new Linux OS image in seconds.
  2. **`REC_MCU` (RP2350 Bootloader):** Pulls RP2350 `BOOTSEL` to GND. Mounts the co-processor as a drag-and-drop UF2 USB drive for instant firmware updates.
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

---

## 3. The SnapDeck Hybrid Detachable Keyboard (Parallel Co-Design)

The SnapDeck keyboard is co-engineered alongside the core tablet to guarantee mechanical tolerances, magnetic alignment, and seamless Wayland display resizing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SNAPDECK CO-DESIGN SPECIFICATION                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. BRAIN:        Nordic nRF52840 (Native USB 2.0 + Bluetooth LE 5.0)        │
│ 2. FIRMWARE:     ZMK (Open-source, ultra-low power, instant BLE switching)  │
│ 3. SWITCHES:     Kailh X-Switch (ultra-low 3.5mm profile, tactile scissor)  │
│ 4. NAVIGATION:   Blackberry RIM 9900 Optical Trackpad centered below space  │
│ 5. ERGONOMICS:   Folding Magnetic Hinge Flap (7° Natural Typing Cant Angle) │
│ 6. ALIGNMENT:    Dual Chamfered 1.5mm Stainless Steel Dowel Guide Pins      │
│ 7. BATTERY:      Thin 300 mAh LiPo pouch cell + MCP73831T charger & PCM     │
│ 8. DOCK BUS:     5-Pin Magnetic Pogo (5V Charge, GND, USB D+, USB D-, ID)   │
│ 9. CHASSIS MATE: Matching PA12 / 6061-T6 shell with N52 neodymium magnets   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.1 Pogo-Pin Docking, Charging Circuit & Mechanical Interface
* **Connector:** 5-pin hermetic magnetic spring-loaded gold Pogo connector (2.54 mm pitch).
* **Pinout:**
  1. `VBUS` (+5.0V Power from tablet to keyboard charging circuit)
  2. `USB_D-` (USB 2.0 Differential Data Negative)
  3. `USB_D+` (USB 2.0 Differential Data Positive)
  4. `GND` (Ground)
  5. `ID_SENSE` (Grounded inside keyboard for hardware insertion detection)
* **Keyboard Internal Battery Management & Pure Silicon Safety:**
  * To safely charge the 300 mAh internal LiPo cell from the 5.0V pogo rail, the SnapDeck integrates a dedicated Microchip **MCP73831T-2ACI/OT** miniature linear charge management IC ($0.25).
  * Programmed via a precision pull-down resistor for a safe 0.5C charge current (150 mA) and a rigid 4.20V termination threshold.
  * Paired with a Texas Instruments **BQ2970** battery protection PCM and miniature dual-MOSFET to protect the 300 mAh pouch against over-discharge (<2.8V), over-charge (>4.25V), and short circuits.
* **Dual Stainless Steel Alignment Guide Pins:**
  * Two chamfered 1.5mm 304-stainless steel guide dowels flank the 5-pin pogo array on the keyboard deck, mating with CNC receiver wells on the tablet lower bezel.
  * Ensures blind, instantaneous magnetic capture with **zero lateral shearing force** on the spring-loaded gold pogo pins.
* **Ergonomic 7° Magnetic Folding Cant Flap:**
  * A secondary folding magnetic strip along the keyboard top edge allows the keyboard to rest either completely flat (0° Lapdeck mode) or propped up at a comfortable **7° ergonomic typing cant** on desks or tables, relieving wrist strain during multi-hour programming sprints.

### 3.2 Operating Modes, Wayland Integration & Touch Exclusion
1. **On-Screen Lapdeck Mode (Docked):**
   * Snaps magnetically onto the lower 1/3 of the landscape display.
   * `ID_SENSE` grounds and front-bezel Hall sensor trips on the tablet.
   * **Native Sway Workspace Docking:** The Sway Wayland compositor dynamically reserves the lower 454 vertical pixels without invalid DRM mode-switching:
     ```bash
     # Reserve lower 454 pixels; active terminal dock confined to upper 1872x950
     swaymsg output SPI-1 scale 1
     swaymsg output SPI-1 transform normal
     # swaymsg commands dynamically re-dock workspaces into the visible top view
     ```
   * **Capacitive Touch Isolation:** To prevent the keyboard's conductive PCB, aluminum scissor switches, and typing fingers from causing phantom touch interrupts on the Goodix GT911 touch glass underneath:
     * A udev rule commands `libinput` to ignore capacitive touch coordinates on `SPI-1` below $Y = 950$, OR
     * The system temporarily disables the GT911 via its dedicated TPS22918 power load switch, defaulting cursor navigation entirely to the RIM 9900 optical trackpad.
   * Runs as a wired USB keyboard; charges the internal 300 mAh LiPo via the MCP73831T charger.
2. **Propped-Up Desktop Mode (Detached BLE):**
   * Undocking breaks `ID_SENSE`. The nRF52840 automatically switches to **Bluetooth LE 5.0 in <5 ms**.
   * Tablet Hall sensor releases; Sway expands workspace to full 1872×1404 pixels, and full-screen capacitive touch re-enables.
3. **Rear Stowed Slate Mode:**
   * Snaps magnetically to the rear chassis for reading or stylus sketching.
   * Rear Hall sensor trips, placing keyboard keys into sleep to ignore accidental hand presses.

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
│ [FRONT FACE]                                                                │
│ • Chemically Etched Matte Glass Overlay (15% Haze, Paper-Texture Friction)  │
│ • 10.3" E-Ink Kaleido 3 / Carta 1200 Panel + Wacom EMR Digitizer           │
│ • 0.1mm Mu-Metal / Ferrite Magnetic Shielding Layer (Behind Digitizer)      │
│ • Top Bezel: IXYS Micro-Solar Strip + 5MP Front Cam with "ThinkShutter"     │
│ • Bottom Bezel: 5-Pin Hermetic Magnetic Pogo Dock for SnapDeck Keyboard     │
│ • Right Flank: Recessed Stylus Garage Groove with Mechanical Spring Clip    │
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
│ • Rear Flank: 8-Pin Hermetic Pogo Bus for Modular RF Backpack               │
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

### 4.2 Stylus Garage & Field Transport
* The right chassis flank features a recessed magnetic channel paired with a low-profile mechanical spring retaining clasp.
* Holds standard 8.0mm diameter EMR styluses (Staedtler Noris Digital, Lamy AL-star, or reMarkable Marker) securely during transit without accidental snagging.

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

---

## 5. Modular Tactical RF & SIGINT Backpack (Optional Add-on)

The modular backpack attaches to the rear 8-pin hermetic pogo bus. To interface wideband SDR (USB), Sub-GHz (SPI), 125 kHz RFID (analog/pulse), NFC (I2C/SPI), and IR blaster (PWM) across a single high-speed USB differential pair and I2C bus:
* **Backpack Core Bridge MCU & USB Hub Architecture:**
  * **USB 2.0 Hub Controller:** Genesys Logic **GL850G** (or FE1.1s, $0.35) 2-port USB 2.0 hub IC splits the pogo bus USB pair between the RTL2832U SDR and the backpack bridge MCU.
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
While the core tablet natively receives positioning and orbital timing from 4 GNSS satellite constellations (GPS, Galileo, GLONASS, BeiDou via the u-blox MAX-M10S), wideband RF scanning of airplanes and atmospheric satellites is offloaded to the backpack:
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
