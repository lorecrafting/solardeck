# SolarDeck Software Specification

Written 2026-10-18 06:45 UTC in the Pi harness by antigravity/gemini-3.8-flash

Software architecture, operating system configuration, custom E-ink waveform drivers, power management daemons, and application workflows.

---

## 1. Operating System Architecture

SolarDeck avoids the high-latency abstraction layers of commercial Android tablets by running a streamlined, security-hardened Linux distribution with direct kernel DRM access:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ APPLICATIONS:  Claude Code • Neovim • Obsidian • Zathura • Kiwix • URH      │
├─────────────────────────────────────────────────────────────────────────────┤
│ USER INTERFACE: Sway (Wayland Tiling WM) / Cage (Single-App Kiosk Mode)     │
├─────────────────────────────────────────────────────────────────────────────┤
│ HARDWARE DRIVERS: Linux Direct Rendering Manager (DRM / KMS) + Wacom HID   │
├─────────────────────────────────────────────────────────────────────────────┤
│ KERNEL: Custom 64-bit Linux 6.6 LTS Kernel (Optimized for ARM64 Broadcom)   │
└─────────────────────────────────────────────────────────────────────────────┘
```

* **Base Distribution:** Minimal Debian Bookworm (Raspberry Pi OS Lite) or Alpine Linux for sub-3-second boot times.
* **Wayland Compositor:** **Sway** or **Cage** running natively without an X11 server overhead. 
* **Color Palette:** Custom high-contrast monochrome and 16-color E-ink CSS stylesheets (`solarized-eink`, `paper-dark`).

---

## 2. High-Speed E-Ink Driver & Waveform Tuning

Standard vendor e-ink drivers flash the screen for 400ms to eliminate ghosting. SolarDeck implements **Dynamic Adaptive Waveform Switching**:

```
MODE             UPDATE TIME   BIT DEPTH   USE CASE
─────────────────────────────────────────────────────────────────────────────
1. Fast Typing   20 – 35 ms    1-bit B/W   Terminal typing, Claude Code CLI
2. UI Motion     60 – 80 ms    2-bit Gray  Cursor movement, trackpad scroll
3. Scribe Pen    < 20 ms       Direct FB   Wacom stylus handwriting overlay
4. Regality Clear 300 ms       16-bit Gray Reading PDFs, medical diagrams
5. Cinema Video  41.67 ms(24F) 1-bit/2-bit Fluid video playback, MPV, YouTube
```

### 2.1 The 20ms "Typing Waveform" (LUT Tuning)
* In the IT8951 kernel driver (`/drivers/gpu/drm/tinydrm/`), we load a custom Look-Up Table (LUT) that issues a single 25ms electrical voltage pulse to turn pixels black without the intermediate erasing clear cycle.
* This allows **typing in Claude Code at 30 to 45 FPS** with zero perceptible latency.

### 2.2 Intelligent Anti-Ghosting Daemon
* A lightweight background daemon (`eink-refreshd`) monitors typing cadence:
  * While the user is actively typing, the screen remains locked in Fast 1-bit Mode.
  * When keystrokes pause for **1.5 seconds**, the daemon quietly triggers an asynchronous anti-ghosting micro-clear. The user experiences LCD-like speed while typing, and paper-sharp clarity when reading.

### 2.3 Low-Latency Pen Overlay Daemon (`solardeck-inkd`) & DRM Serialization
* To achieve true paper-like handwriting latency (**< 18ms tip-to-ink**) without corrupting concurrent display flushes from Sway or terminal windows:
  1. `solardeck-inkd` reads raw coordinates directly from `/dev/input/event*` (Wacom EMR 240 Hz stream) in non-blocking mode.
  2. A fast Bresenham line algorithm calculates the micro-line bounding box between sequential coordinates (e.g., a tiny 12×18 pixel rectangle).
  3. **Kernel SPI Bus Synchronization (Race Condition Elimination):**
     * Direct userspace writes to `/dev/spidev0.0` while the kernel DRM driver (`tinydrm/it8951.c`) is actively flushing frames will interleave SPI transactions and crash the EPDC controller.
     * To prevent bus collisions, `solardeck-inkd` submits damaged rectangles via a dedicated in-kernel character interface (`/dev/it8951_ink`) with an internal kernel mutex lock, OR commits partial damage updates through standard KMS atomic commits (`DRM_IOCTL_MODE_ATOMIC_COMMIT`).
     * The kernel driver applies the single 12ms pulse using the IT8951's **1-bit Direct Update (DU)** waveform register (`IT8951_CMD_WRITE_PIXEL_AREA`).
  4. When the pen lifts for $>500\text{ ms}$, the daemon asynchronously delivers the complete vector stroke (`x, y, pressure, tilt, timestamp`) to the active document application (Xournal++, Obsidian, or Zathura) to commit the layer to disk, followed by a quiet anti-ghosting micro-clear.

### 2.4 Teleconference & Video Call Engine ("Conference Mode")
To support high-definition video calls on Discord, Google Meet, and Zoom without overwhelming the E-Ink display:
1. **Outgoing 1080p30 Stream:**
   * Captured by the front 5MP Sony IMX219 sensor via `libcamera` and Broadcom hardware ISP.
   * Encoded directly in silicon via hardware H.264/H.265 encoder at 30 FPS, transmitting crisp color video to remote participants.
2. **Inbound Presentation & Shared Screens:**
   * Incoming screen shares (slides, code, whiteboards) render in full 16-bit grayscale (GC16) at 227 PPI with exceptional readability.
3. **Inbound Participant Video Thumbnails:**
   * Displayed in a compact floating overlay rendered in **A2 Motion Mode (60–75ms refresh, 2-bit grayscale)**.
   * **Smart-Still Toggle:** Automatically freezes participant video into a crisp still portrait, refreshing only when the active speaker changes or every 3 seconds, cutting display power by 85% while keeping audio 100% real-time.

### 2.5 V1 24 FPS Cinema Video Engine & Thermal Viscosity Management
To enable natural, "movie-like" 24 FPS video playback without choppy frame drops or severe pigment ghosting, SolarDeck integrates a dedicated hardware-accelerated video pipeline in V1:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SOLARDECK V1 24 FPS CINEMA VIDEO PIPELINE                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. VIDEO SOURCE: 24 FPS 1080p Stream (mpv / Chromium / YouTube)            │
│                          │                                                  │
│                          ▼ (<2.0 ms on Broadcom VideoCore VI GPU)           │
│ 2. GPU TEMPORAL BLUE-NOISE DITHERING:                                       │
│    • GLSL Compute/Fragment Shader: `/usr/lib/solardeck/shaders/dither.glsl` │
│    • Converts 24-bit RGB video into 1-bit B/W or 2-bit (4-color) bitmaps   │
│    • Human eye spatio-temporally fuses fine dots into continuous gradients  │
│                          │                                                  │
│                          ▼ (<1.5 ms via ARM NEON SIMD)                      │
│ 3. ARM NEON SIMD FRAME-DIFFERENCING (DIRTY DELTA PASS):                     │
│    • Delta = Frame[N] ^ Frame[N-1]                                          │
│    • Static backgrounds (65–80% of video frame) are bypassed (0 mW)         │
│    • Isolates active motion bounding boxes for partial update               │
│                          │                                                  │
│                          ▼ (<2.5 ms over MIPI-DSI 2 Gbps bus)               │
│ 4. HIGH-SPEED MIPI-DSI DMA PUSH:                                            │
│    • DMA pushes damaged rectangles to EPDC in <2.5 ms (vs. 55ms on SPI)     │
│    • Leaves 39 ms of 41.67 ms frame budget for physical particle motion     │
│                          │                                                  │
│                          ▼                                                  │
│ 5. TRUNCATED OVERDRIVE WAVEFORM & THERMAL VISCOSITY ASSIST:                 │
│    • Clamps voltage driving pulse to 22–26 ms (modulates surface pigment)   │
│    • Rolling 4-frame DC neutralization keeps net bias at 0.00V              │
│    • `solardeck-thermal-boostd` couples CPU heat to backplane (30°C–33°C),  │
│      reducing fluid viscosity >40% so particles accelerate 1.8x faster      │
└─────────────────────────────────────────────────────────────────────────────┘
```

1. **GPU Temporal Blue-Noise Dithering (`dither.glsl`):**
   * Physical electrophoretic particles cannot execute 16-level grayscale transitions in 41.67 ms.
   * A custom GLSL fragment shader running on the Broadcom VideoCore VI GPU converts video frames into 1-bit binary or 2-bit blue-noise dithered bitmaps in < 2 ms.
   * Spatial and temporal error-diffusion creates the visual illusion of smooth photographic color and grayscale gradients, while demanding only fast binary voltage pulses from the display.
2. **ARM NEON SIMD Delta Differencing:**
   * An optimized ARM NEON SIMD loop calculates XOR differences between consecutive frames in < 1.5 ms.
   * Unchanged scene backgrounds are bypassed entirely; only active motion bounding boxes are pulsed.
3. **High-Speed MIPI-DSI Transmission:**
   * Utilizing the CM4's native 2-lane MIPI-DSI bus (2 Gbps bandwidth), the video daemon transfers delta frames to the display controller in **< 2.5 ms** (compared to ~55 ms over SPI), eliminating bus latency as a bottleneck.
4. **Truncated Overdrive Waveforms & Rolling DC Neutralization:**
   * Driving pulses are truncated to **22–26 ms**. Particles oscillate within the upper optical zone rather than traveling the full capsule depth.
   * A rolling 4-frame mathematical compensation algorithm balances positive and negative voltage pulses to average **0.00V net DC bias**, completely preventing pigment burn-in.
5. **Thermal Viscosity Optimization (`solardeck-thermal-boostd`):**
   * Dielectric fluid viscosity is inversely proportional to temperature. At 15°C, fluid drag causes heavy motion smearing; at 30°C–33°C, fluid viscosity drops by **>40%**, accelerating particle velocity by **$1.8\times$**.
   * During active 24 FPS video playback, `solardeck-thermal-boostd` dynamically routes thermal dissipation from the CM4 CPU shield into the internal PCBA copper heat plane behind the display, maintaining the backplane at a safe 30°C–33°C without dedicated resistive heating elements.
6. **Battery Lifespan & Power Profile (Video vs. Non-Video):**
   * **During 24 FPS Video Playback:** Continuous GPU dithering, NEON differencing, high-speed DSI DMA, and high-frequency charge pump pulsing consume **~2.8W to 3.4W total system power**, delivering **10 to 12 hours** of continuous video playback on a single charge.
   * **When NOT Playing Video (Writing, Coding, Reading, Ambient Clock):**
     * **0.000W Bi-Stable Display:** The instant video stops, E-Ink pigments remain physically locked in place by fluid viscosity and van der Waals forces. The display consumes **0.000 Watts** to hold a static page.
     * **Active Terminal / Coding (Claude Code CLI, Neovim):** Drawing only ~1.1W to 1.4W, the battery provides **24 to 32 hours** of continuous active typing.
     * **Zen Reading Mode (Tier 1):** With CM4 powered down to 0.000W and the RP2350 flipping pages in <30ms at 4.5 mW average, battery life extends to **300+ days**.
     * **Perpetual Ambient Clock & Weather Station (Tier 0/1):** The 0.15W micro-solar bezel strip harvests more power than the 4.5 mW idle load, granting **infinite off-grid battery life** without wall recharging.
     * **Battery Chemical Longevity:** Because LiFePO4 cells are rated for **3,000 to 5,000+ full charge cycles** (vs. 500 cycles for standard consumer Li-ion), and typical non-video usage requires charging only once every few days or weeks, the physical battery pack lasts **10 to 15+ years** before degrading.

---

## 3. Power Management & Deep Sleep (Suspend-to-RAM)

### 3.1 Fast Sleep / Instant Wake Pipeline
* **Suspend-to-RAM (S2idle):**
  * When sleep is triggered, Linux freezes userspace tasks, flushes file caches, cuts peripheral power switches (TPS22918), and drops the LPDDR4 memory controller into Self-Refresh mode.
  * Power draw drops to **15 mW**.
* **Instant Wake (0.3 Seconds):**
  * Touching any key or tapping the touch bar sends a hardware interrupt from the RP2350 to GPIO 17 on the CM4.
  * The CM4 restores CPU clock lines and resumes execution directly from RAM in **under 300 milliseconds**. All open terminal windows and Claude sessions remain intact.

### 3.2 The Ambient LifeOps Mode (RP2350 Firmware)
While the main CM4 is powered completely off (0.000W), the **RP2350 co-processor** runs bare-metal C / Pico-SDK firmware:
1. **Sub-30ms Zen Reader & Framebuffer Pre-Caching:**
   * Utilizes the onboard **8MB QSPI PSRAM** to double-buffer full 1872×1404 8-bit page images.
   * When reading books, the CM4 pre-renders pages into PSRAM and sleeps. The RP2350 handles page-turn taps and side-bezel touch gestures autonomously, updating the IT8951 in <30ms while the CM4 remains dead (**~4.5 mW total power; 300+ days battery life**).
2. **Standalone 24/7 Meshtastic LoRa Mesh Repeater:**
   * The RP2350 communicates directly with the Semtech SX1262 LoRa transceiver over SPI.
   * Listens for encrypted mesh packets, inspects routing headers, and hops packets across off-grid networks autonomously at **12–15 mW**, transforming SolarDeck into an 80+ day continuous tactical repeater. If a direct message addresses the tablet, the RP2350 asserts `GPIO 17` to wake the CM4 and sound an alert.
3. **1-Second TCXO Clock Tick & Weather Barograph:**
   * Receives a 1Hz square-wave hardware interrupt (`INT/SQW`) from the high-precision DS3231 TCXO RTC.
   * Updates time digits and samples the Bosch BMP390 barometer and TMP112 thermals every 60 seconds into a rolling 7-day circular buffer in PSRAM.
4. **Motion & Pick-Up-To-Wake Interrupt:**
   * Configures the Bosch BMA400 accelerometer in 3.5 µA autonomous motion-detect mode, waking Linux in 0.3 seconds upon pick-up or frame tap.

### 3.3 Telemetry-Driven Adaptive Power Engine & Multi-Tier AI Closed-Loop
Rather than relying on static, hardcoded power profiles, SolarDeck continuously learns, monitors, and optimizes its physical behavior through a structured, multi-tier telemetry and AI feedback loop:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SOLARDECK MULTI-TIER AI FEEDBACK ARCHITECTURE             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. REAL-TIME SENSING (Hardware Layer):                                      │
│    • TI INA3221 (3-Rail mW) • BQ27441 (Coulombs/ESR) • TMP112 (Thermal)     │
│    • Solar Lux (RP2350 ADC) • BMA400 (Motion) • Quectel/SX1262 (RF Metrics) │
│                                  │                                          │
│                                  ▼ (10Hz / 1Hz / 0.1Hz Sampling)            │
│ 2. TELEMETRY DAEMON (`solardeck-telemetryd`):                               │
│    • Circular SQLite Database: `/var/log/solardeck/telemetry.db` (WAL mode) │
│    • Structured Tables: power_rails, battery_health, thermals, rf, motion   │
│                                  │                                          │
│         ┌────────────────────────┼────────────────────────┐                 │
│         ▼                        ▼                        ▼                 │
│ [TIER 1: IMMEDIATE LOCAL]  [TIER 2: RUNTIME AI TUNING] [TIER 3: HARDWARE EVOLUTION]│
│ • Waveform LUT Temp Comp   • `solardeck-optimize`     • Long-term Inrush/Heat│
│ • 0% Frontlight in Sun     • Claude Code CLI Tuning   • Feature Usage (YAGNI)│
│ • Dead Cellular Power-Cycle• Custom power.conf & udev • PCB Rev 2 Sizing Recs│
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 3.3.1 Structured Database Schema (`/var/log/solardeck/telemetry.db`)
The background daemon `solardeck-telemetryd` logs all physical metrics into a compact, rolling SQLite database (pruned automatically to maintain a 7-day / 50MB ceiling):

1. **`power_rails` Table:**
   `timestamp`, `vbus_v`, `core_mw`, `display_mw`, `rf_mw`, `total_mw`, `peak_inrush_ma`
2. **`battery_health` Table:**
   `timestamp`, `soc_pct`, `mah_remaining`, `cell_esr_mohm`, `soh_pct`, `charge_cycles`, `temp_c`
3. **`thermal_zones` Table:**
   `timestamp`, `battery_c`, `display_backplane_c`, `soc_die_c`, `modem_c`
4. **`rf_metrics` Table:**
   `timestamp`, `lte_rsrp`, `lte_sinr`, `lte_rrc_state`, `lora_rssi`, `lora_snr`, `lora_airtime_pct`, `wifi_rssi`, `gnss_cn0`, `gnss_ttff`
5. **`environment_motion` Table:**
   `timestamp`, `ambient_lux`, `baro_hpa`, `relative_altitude_m`, `motion_state`, `tilt_angle`
6. **`system_workload` Table:**
   `timestamp`, `active_window`, `cpu_governor`, `core_freqs_mhz`, `emmc_wear_pct`, `epdc_refresh_count`

#### 3.3.2 The Three AI Feedback Tiers
1. **Tier 1: Immediate Autonomous Hardware Adaptation (< 100ms response):**
   * **Waveform Temperature Tuning:** Reads the display backplane TMP112 sensor and writes directly to the IT8951 `TEMP_REG`. The EPDC switches waveform LUTs in real time, preventing slow ghosting in cold weather and bleeding in hot sunlight.
   * **Ambient Lux Scaling:** When the solar strip ambient lux reads $>10,000\text{ lux}$ (direct sunlight), the front-light is locked to 0% and E-ink contrast curves are maximized.
   * **Dead-Socket Power Cycle:** If the RF rail ammeter registers continuous active transmission power ($>1.2\text{W}$) for >45 seconds without network throughput, the daemon automatically pulses the modem's TPS22918 load switch to reset the baseband.
2. **Tier 2: Runtime System Profile Self-Tuning (`solardeck-optimize`):**
   * Running `solardeck-optimize` aggregates the past 24 hours of telemetry into a dense JSON payload and passes it to Claude Code:
     ```bash
     solardeck-cli telemetry export --last 24h --json | claude "Analyze power anomalies and generate tuned /etc/solardeck-power.conf"
     ```
   * The LLM identifies parasitic drains, optimizes core parking thresholds, and adjusts charging currents to preserve battery longevity.
3. **Tier 3: Long-Term Hardware Evolution Analysis (Rev 1 $\to$ Rev 2 Redesign Recommendations):**
   * Rather than attempting speculative, error-prone automated PCB trace rerouting via scripts, SolarDeck leverages machine-readable SQLite telemetry to generate rigorous, human-reviewed engineering recommendations for Rev 2:
     * **Capacitor & Regulator Right-Sizing:** If 6 months of peak inrush logs demonstrate the Quectel LTE modem never pulls more than 1.6A in the field, the oversized 470µF tantalum capacitor is flagged for replacement with compact ceramic capacitors in Rev 2, saving board area and BOM cost.
     * **Thermal Gradient Analysis:** If thermal logs record sustained gradients between the CM4 CPU and battery pouch during long Claude Code compile sessions, the toolchain generates specific mechanical and layout guidance (e.g., thermal pad thickness adjustments, copper pour relief) for the hardware team.
     * **Hardware YAGNI Pruning:** If telemetry reveals an auxiliary expansion rail or sensor was active $<0.01\%$ of the time over hundreds of field hours, it is flagged for deletion in Rev 2, shedding weight, cost, and complexity.

---

## 4. Claude Code & AI Integration

* **Terminal Coding:** Runs `claude` CLI natively in Alacritty / Foot terminal with tmux session persistence.
* **Voice Speech-to-Text (STT):**
  * **Offline Mode:** Uses `whisper.cpp` (Quantized `tiny.en` or `base.en` model) running locally on the Cortex-A72 cores using NEON SIMD instructions (transcription latency < 1.2 seconds).
  * **Cloud Mode:** Streams 16kHz audio from the I2S MEMS microphones directly to the Anthropic voice/audio API over 4G LTE.
* **Local Offline AI Copilot:**
  * Integrates with locally installed small language models (via `llama.cpp` using 4-bit quantization) for completely air-gapped technical and code querying.

---

## 5. Offline Knowledge & Engineering Stack

* **Kiwix Offline Engine:**
  * Runs a local headless HTTP server indexing 100GB+ `.zim` archive files:
    * Complete English Wikipedia with full images (~95GB).
    * Open-Source Software & Engineering Archives: Stack Overflow, ArchWiki, Linux man-pages.
    * Scientific & Reference Library: ArXiv digests, emergency field manuals, standard dictionaries.
* **Ambient LifeOps & Astronomical Telemetry:**
  * A lightweight background daemon calculates local solar ephemeris and ambient system telemetry:
    * Displays solar noon, day length, and twilight transitions based on live GNSS coordinates.
    * Monitors ambient room lux, weather forecasts, and battery state-of-charge.

---

## 6. Tactical RF & Sky-Scan Toolchain (Backpack Modules)

* **Sub-GHz Radio (CC1101):** Controlled via `rfcat` or `Universal Radio Hacker (URH)` for analyzing, recording, and replaying 315/433 MHz signals.
* **Infrared:** Controlled via `LIRC` (Linux Infrared Remote Control) with preloaded profiles for home A/C units, TVs, and projectors.
* **NFC / RFID:** Controlled via `libnfc` and `proxmark3` CLI tools for cloning and emulating Mifare Classic, NTAG, and 125 kHz HID fobs.
* **Airplane Tracking (ADS-B 1090 MHz):** Runs `dump1090-fa` or `readsb` in the background, feeding a vector radar map showing nearby commercial and private aircraft, altitudes, speeds, and flight numbers.
* **Weather Satellite Image Downlink (137 MHz):** Uses `satdump` CLI to automatically track satellite pass schedules and decode live visual and infrared cloud imagery directly from NOAA and Russian Meteor-M2 polar-orbiting satellites.
* **Marine AIS Vessel Tracking (162 MHz):** Runs `rtl-ais` to decode vessel identification, GPS position, course, and cargo data from coastal ships.

---

## 7. USB-C Secondary Monitor & Display Sink Software

When connected via USB-C to a host laptop (Mac, Windows, or Linux), SolarDeck acts as an external E-Ink monitor optimized for coding, diff reviews, and reading documentation:

```
┌────────────────────────────────────────────────────────┐
│ Host Laptop (Mac/Win/Linux)                            │
│   │                                                    │
│   ▼ High-Speed USB-C Cable (Composite USB Gadget)      │
├────────────────────────────────────────────────────────┤
│ SolarDeck Carrier Board                                │
│   │                                                    │
│   ├─► CDC-NCM Virtual Network Interface (Zero Config) │
│   │                                                    │
│   ├─► Low-Latency Frame Capture (Weylus / Deskreen)   │
│   │                                                    │
│   └─► `eink-refreshd` Bounding-Box Waveform Renderer   │
│         • Detects damaged text rects                   │
│         • Converts to 20ms 1-bit fast-typing LUT       │
│         • Flushes to IT8951 without 60Hz flicker       │
└────────────────────────────────────────────────────────┘
```

* **Zero-Driver Plug & Play:** The host OS recognizes SolarDeck as a native high-speed network device over CDC-NCM / RNDIS.
* **Damage-Rectangle Bounding Box Refresh:** Unlike standard 60 FPS video monitors that stream constant frames, the SolarDeck display sink captures only updated screen bounding boxes (damaged rects), preventing full-panel flashing and rendering smooth, tear-free text.
* **Simultaneous Host Charging:** Operates continuously without draining the internal battery by drawing USB-PD power from the host machine.

---

## 8. Ambient Notification & Beacon Daemon (`solardeck-beacond`)

SolarDeck's programmable RGB Notification Beacon ("Signal Halo") and Standby Piezo Buzzer are managed by a unified notification daemon running under both Linux and the RP2350 co-processor:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   SOLARDECK BEACON & ALERT ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Applications & Daemons:                                                     │
│ • `meshtasticd` (Incoming LoRa Packets) ──────────────────┐                 │
│ • `solardeck-telemetryd` (Battery / Solar / Thermals) ────┼─► `/run/beacon` │
│ • `desktop-notifications` (Discord / Matrix / Slack) ─────┤   (UNIX Socket) │
│ • `weather-barograph` (Barometric Storm Warnings) ────────┘        │        │
│                                                                    ▼        │
│                                                          `solardeck-beacond`│
│                                                                    │        │
│              ┌─────────────────────────────────────────────────────┴─┐      │
│              ▼ (When Linux CM4 is Active)                            ▼      │
│     Direct IPC to RP2350 via UART/SPI               (When Linux CM4 Suspends)
│     • Custom color profiles & patterns              Autonomous RP2350 Engine
│     • Gamma-corrected PWM curves (<0.2 mA)          • LoRa Mesh: Pulse Green
│     • SMT Piezo Chime Tones (75 dB)                 • Solar: Breathing Amber
│                                                     • Storm: Strobe Red Alert
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.1 Unified Control Interface
* **CLI Tool (`solardeck-beacon`):**
  * Trigger manual colors and patterns from bash scripts, cron jobs, or Claude Code:
    ```bash
    solardeck-beacon set --color purple --pattern breathe --duration 5s
    solardeck-beacon alert --tone mesh-chime --color emerald
    ```
* **D-Bus & Desktop Notification Bridge:**
  * Subscribes to `org.freedesktop.Notifications` (Sway / Mako).
  * Automatically maps urgent mentions to custom LED breathing pulses (e.g., Slack $\to$ Ruby, Discord $\to$ Amethyst Purple, GitHub $\to$ Cyan).

### 8.2 Deep-Sleep Autonomous Co-Processor Operation
* When the CM4 enters S2idle or full power-down (0.000W), the RP2350 firmware autonomously manages the beacon:
  * **Incoming LoRa Mesh Packets:** RP2350 detects packet on SX1262 SPI $\to$ plays a subtle 2-tone chime on the SMT micro-piezo buzzer $\to$ pulses the emerald green LED at 0.5 Hz for 15 seconds.
  * **Rapid Barometric Drops (Storm Alert):** BMP390 detects pressure drop $> 3\text{ hPa / 3 hr}$ $\to$ strobes ruby red warning and sounds a weather alert tone.
  * **Ambient Nightstand Beacon:** When ambient solar lux reads $< 0.5\text{ lux}$ (pitch black) and device is resting on a nightstand or desk, pulses an ultra-faint warm white locator glow (2% duty cycle, $< 15\text{ µA}$) so you can effortlessly find the tablet in the dark.

---

## 9. Flash Reliability, Storage Architecture & Power-Fail Emergency Sync

To prevent filesystem corruption from unexpected battery depletion, field disconnects, or sudden hardware airgap switches, SolarDeck implements a robust, tamper-proof storage stack:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 SOLARDECK POWER-FAIL SAFE STORAGE ARCHITECTURE               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. IMMUTABLE ROOT FILESYSTEM (`/`):                                         │
│    • Read-Only SquashFS / ext4 base image with `overlayfs` in RAM (tmpfs)   │
│    • System updates applied transactionally via A/B partition atomic swaps  │
│    • Impossible to corrupt OS binaries during sudden power loss             │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. PERSISTENT TRANSACTIONAL USER DATA (`/home`, `/var`):                    │
│    • F2FS (Flash-Friendly File System) with transactional write journaling  │
│    • Mount flags: `rw,noatime,nodiratime,barrier=1,alloc_mode=reuse,fsync_mode=strict`│
│    • Eliminates eMMC write amplification and prevents dirty inode orphans   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. 150ms EMERGENCY HARDWARE FLUSH HOOK (`GPIO_PWR_FAIL`):                   │
│    • RP2350 continuously samples battery voltage via BQ27441 fuel gauge     │
│    • When VBAT sags to 3.10V, RP2350 fires hardware interrupt `GPIO 16`    │
│    • Kernel traps interrupt ──► issues emergency `sync` ──► unmounts queues │
│    • Completed in < 150 ms, cleanly parking flash controller before cutoff  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.1 Emergency Sync Hook (`solardeck-powerfaild`)
* Runs as a high-priority real-time daemon listening on `/dev/input/event*` for `KEY_POWERFAIL` (generated by GPIO 16 from RP2350).
* When battery terminal voltage drops below 3.10V, the daemon:
  1. Issues an immediate `sync -f /home /var` kernel system call.
  2. Freezes write queues via `fsfreeze -f /home`.
  3. Sends `SIGTERM` to active Claude Code and tmux sessions, saving buffer state to disk.
  4. Signals the RP2350 that eMMC is parked; RP2350 then issues a graceful power-down.

---

## 10. Tactical Field Daemons, Acoustic Beamforming & All-Weather Rain Handling

### 10.1 Dual-Microphone Acoustic Beamforming Daemon (`solardeck-beamformd`)
* Integrates directly into PipeWire via the `libpipewire-module-echo-cancel` and WebRTC Audio Processing (AEC/NS/AGC) engine.
* **Broadside Spatial Filtering:**
  * Uses the 65 mm physical separation between the dual Knowles SPH0645 MEMS microphones.
  * Measures inter-aural time difference (ITD) to synthesize an elliptical 60° forward-facing acoustic pickup beam centered on the operator’s mouth.
  * Attenuates off-axis sounds by 18–24 dB, eliminating outdoor wind buffeting, rain splatter, and background conversations.
  * Direct pipe into local Whisper (`whisper.cpp`) and Claude Code CLI for 99%+ speech-to-text accuracy in harsh outdoor environments.

### 10.2 Torrential Rain / Water-Lock Daemon (`solardeck-waterlock`)
* Manages capacitive touch rejection when operating in heavy precipitation or marine environments:
  * **Triggering:** Activated by holding the 5-way tactical rocker center-press for 2 seconds, or via CLI:
    ```bash
    solardeck-waterlock on   # Cuts power to Goodix touch controller
    solardeck-waterlock off  # Restores capacitive multi-touch
    ```
  * **Hardware Action:** Controls the TPS22918 load switch supplying `VDD_TOUCH`. Disabling this rail drops capacitive sensor power to 0.000V.
  * **Digitizer Continuity:** The Wacom EMR digitizer (`wacom_w9013`) remains powered and 100% active. Stylus hover, pressure, tilt, and button clicks operate flawlessly under direct sheeting water with zero phantom taps.

### 10.3 Tactical 5-Way Navigation Rocker Daemon (`solardeck-navd`)
* Captures raw input events from the left-bezel ALPS 5-way rocker connected to RP2350 GPIOs.
* Injects standard Linux input events into `uinput`:
  * `NAV_UP` $\to$ `KEY_UP` (or Page Up / Terminal scrollback)
  * `NAV_DOWN` $\to$ `KEY_DOWN` (or Page Down)
  * `NAV_LEFT` $\to$ `KEY_LEFT` (Previous Workspace / PDF Chapter)
  * `NAV_RIGHT` $\to$ `KEY_RIGHT` (Next Workspace / PDF Chapter)
  * `NAV_PRESS` $\to$ `KEY_ENTER` (Select / Open)
* **Gloved Mode:** Enables seamless 1-handed terminal browsing, document reading, and system controls with heavy winter or tactical gloves on.

### 10.4 Co-Processor A/B Firmware Slotting & Hardware Watchdog Verification
* The RP2350 co-processor firmware incorporates a fail-safe A/B update daemon:
  * New firmware is flashed over SPI/UART to the inactive partition (Bank B).
  * Co-processor resets into Bank B with a 5-second hardware watchdog armed.
  * Bank B firmware must initialize all power rails, test the BQ27441 fuel gauge, and assert `WATCHDOG_KICK`.
  * If the firmware hangs or locks up, the hardware watchdog reboots the RP2350 into Bank A (golden image), eliminating any risk of bricking the hardware power controller during field updates.

### 10.5 Spatial Acoustic Piezo Haptic Daemon (`solardeck-hapticd`)
* **Purpose:** Drives the quad-corner TDK PowerHap piezoelectric actuator array via dual Boréas BOS1901 CapDrive controllers to deliver coordinate-targeted, localized tactile clicks during bare-glass on-screen typing.
* **Low-Latency Event Pipeline:**
  1. Hooks into `/dev/input/event*` (Goodix GT911 touch device) at high thread priority (`SCHED_FIFO`, priority 85).
  2. Upon receiving `EV_KEY` or `BTN_TOUCH` with absolute coordinates $(X, Y)$, maps the touch location relative to the four corner actuators:
     * $A_1 = \text{Top-Left } (0, 0)$
     * $A_2 = \text{Top-Right } (1872, 0)$
     * $A_3 = \text{Bottom-Left } (0, 1404)$
     * $A_4 = \text{Bottom-Right } (1872, 1404)$
  3. Calculates localized acoustic phase and amplitude weighting ($w_i \propto 1 / d_i^\alpha$).
  4. Dispatches differential SPI write transactions to the dual BOS1901 drivers in **< 0.4 milliseconds**:
     * Primary drive pulse: 1.2ms 140Vpp square-ramp waveform to the nearest corner actuator.
     * Inverse cancellation pulse: 180° phase-inverted damping pulse to distant actuators to suppress chassis shell vibration.
* **Autonomous Power Gating & Energy Recovery:**
  * Uses Boréas CapDrive bidirectional charge recycling, recovering **>80% of pulse energy** back into the power bus (net consumption **~18 mW per key click**).
  * **SnapDeck Docking Bypass:** When `ID_SENSE` indicates that the physical SnapDeck keyboard is docked, `solardeck-hapticd` immediately places the BOS1901 drivers into deep sleep ($I_Q < 0.1\text{ }\mu\text{A}$), completely eliminating phantom power consumption.

---

## 11. Temperature-Compensated Waveform LUT Matrix (`eink-refreshd`)

Electrophoretic fluid viscosity varies significantly with temperature. Running fixed-duration waveforms across seasons results in severe ghosting in the cold and pigment bleeding in the heat. SolarDeck implements dynamic temperature-steered waveform switching in `eink-refreshd`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              DYNAMIC QUAD-ZONE TEMPERATURE WAVEFORM MATRIX                  │
├────────────────────┬──────────────┬──────────────┬──────────────────────────┤
│ Temperature Band   │ Backplane °C │ Active LUT   │ Waveform Strategy        │
├────────────────────┼──────────────┼──────────────┼──────────────────────────┤
│ 1. Cold Sub-Zero   │ T < 5°C      │ `LUT_COLD`   │ • 45ms DU pulse duration │
│                    │              │              │ • Pulse width × 1.35     │
│                    │              │              │ • Full GC16 every 15 keys│
├────────────────────┼──────────────┼──────────────┼──────────────────────────┤
│ 2. Normal Ambience │ 5°C ≤ T ≤ 35°C│ `LUT_NORMAL` │ • 20ms fast-typing DU    │
│                    │              │              │ • 60ms A2 smooth motion  │
│                    │              │              │ • 200ms GC16 crisp color │
├────────────────────┼──────────────┼──────────────┼──────────────────────────┤
│ 3. High Desert Heat│ 35°C < T ≤ 50°C│ `LUT_HOT`   │ • Drive voltage −10%     │
│                    │              │              │ • Shortened settle time  │
│                    │              │              │ • Zero pigment overshoot │
├────────────────────┼──────────────┼──────────────┼──────────────────────────┤
│ 4. Thermal Cutoff  │ T > 50°C     │ `LUT_PROTECT`│ • High-temp alert banner │
│                    │              │              │ • Pauses high-rate A2    │
└────────────────────┴──────────────┴──────────────┴──────────────────────────┘
```

* **Thermal Sensing Hook:** `eink-refreshd` polls the display backplane TMP112 sensor via the RP2350 inter-processor telemetry bridge (`I2C_HOST` target address `0x42` or `/run/solardeck/telemetry.sock`) every 10 seconds.
* **Seamless In-Flight Transition:** Waveform switching occurs between frame updates without dropped keystrokes or UI tearing.

---

## 12. Tactical Covert & NVG Mode Daemon (`solardeck-covert`)

Provides one-touch blackout and night-vision optical configuration for covert field deployments and dark-sky astronomy:

* **CLI & Rocker Control:**
  ```bash
  solardeck-covert on     # Engages NVG stealth profile
  solardeck-covert status # Displays current luminance and squelch states
  solardeck-covert off    # Restores standard daylight profile
  ```
* **Daemon Orchestration:**
  1. **Optical Beacon Blackout:** Directs RP2350 via IPC to disable green and blue PWM channels on the Kingbright RGB LED, clamping the red channel to $630\text{ nm}$ monochromatic at $<0.5\%$ duty cycle.
  2. **Frontlight Clamp:** Commands TPS61163 to power down cold-white LEDs and lock warm-amber LEDs to ultra-dim Step 1 of 2048 ($<0.05\text{ lux}$).
  3. **Acoustic Mute:** Asserts hardware mute register on MAX98357A speaker amp and silences RP2350 micro-piezo tone generator.
  4. **Display Palette Shift:** Inverts Sway terminal themes to high-contrast red-on-black or amber-on-black colorways to maintain natural human scotopic (rod cell) night adaptation.

---

## 13. Hardware Anti-Tamper & Cryptographic Zeroization Hook (`solardeck-vault`)

Secures device data against physical chassis compromise, laboratory probing, or forensic acquisition without risking permanent bricking during routine battery maintenance:

* **Intrusion Interrupt Processing:**
  * The sealed chassis intrusion limit switch connects directly to a dedicated Non-Maskable Interrupt (NMI) on the RP2350 co-processor.
  * When `solardeck-vault --arm` is engaged, opening the CNC backplate trips the switch.
  * In $<100\text{ ns}$, RP2350 hardware TrustZone routine executes atomic memory zeroization:
    * Volatile session decryption tokens in retention SRAM are erased to all-zeros.
    * Pulls CM4 reset line low and halts all bus communication.
* **Routine Battery Maintenance & Tamper Recovery:**
  * Master partition encryption keys are derived from RP2350 hardware-locked OTP with TrustZone protection combined with a user passphrase.
  * If the device powers down completely or the battery is removed for servicing, volatile session tokens are cleared, but the device is **not bricked**. Upon re-powering, entering the correct passphrase or BIP-39 mnemonic restores the session tokens.
* **Emergency Zeroization Button:** Depressing the recessed `REC_MCU` pinhole switch continuously for 10 seconds triggers the same session zeroization cascade with audible confirmation (3 micro-piezo clicks before wipe).
* **Cryptographic Invalidation:** Because the transactional F2FS root and home partitions are encrypted via `fscrypt` with hardware-derived keys, wiping the session tokens permanently locks the eMMC partitions against forensic recovery.
* **Airgapped Transaction Signing & Document Notary Pipeline:**
  * When the physical Hardware Airgap Switch is in STEALTH mode, `solardeck-vault --sign-tx` or `solardeck-vault --notarize <file>` executes in absolute radio isolation:
    1. **Visual Ingestion:** Rear flush 12MP camera captures unsigned transaction QR codes (Bitcoin PSBT, Ethereum EIP-712, Solana) or document fingerprints via `zbarcam` / OpenCV.
    2. **High-Contrast Verification:** Full transaction details (recipient address, smart contract parameters, transfer amounts, and network gas fees) are displayed in razor-sharp typography on the 10.3" E-Ink screen.
    3. **Hardware Authorization:** The operator signs using an encrypted local GPG/Ed25519 key, or taps a physical **YubiKey, Tangem, or Coldcard** against the top-bezel 13.56 MHz NFC coil (`pcscd` / `nfc-tools`).
    4. **Optical Broadcast:** The signed transaction is converted into an animated QR fountain code (`txqr`) displayed full-screen on the E-Ink display for the operator's smartphone or companion device to scan and broadcast to the blockchain.
    5. **Zero-Leakage Assurance:** Private keys never touch an internet-connected bus or memory space, backed by physical hardware power gates.

---

## 14. Zero-Brick Architecture: Dual-Bank A/B Flash, Watchdog Rollback & Immutable OverlayFS

To guarantee that autonomous AI agents, experimental RISC-V assembly routines, kernel upgrades, or user modifications can **never soft-brick or permanently compromise the device**, SolarDeck implements a multi-tiered software and firmware safety net:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ZERO-BRICK SOFTWARE & FIRMWARE ARCHITECTURE                 │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Co-Processor Firmware │ • Dual-Bank A/B Partitioning (16MB QSPI Flash)      │
│                       │ • 8-Second Hardware Watchdog Auto-Rollback          │
│                       │ • `solardeck-coproc-flash` Safe Flashing CLI        │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Linux Host System     │ • Cryptographically Verified Read-Only Rootfs       │
│                       │   (`dm-verity` + SquashFS)                          │
│                       │ • Read-Write User Layer via OverlayFS               │
│                       │ • `solardeck-reset --safe` (3-Second Factory Clean) │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Recovery & Emergency  │ • Dual-Kernel A/B Bootloader (`u-boot` fallback)    │
│                       │ • Hardware Recessed Button USB Mass Storage / UF2   │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

### 14.1 Co-Processor Dual-Bank A/B Management (`solardeck-coproc-flash`)
The co-processor flashing utility manages dynamic firmware upgrades and experimental RISC-V code loading directly from the Linux terminal or Claude Code agent:

```bash
# Safe flash to Bank B with automated watchdog verification:
solardeck-coproc-flash --slot b --timeout 8 custom_riscv_dsp.elf

# Force rollback to factory Bank A (Golden Image):
solardeck-coproc-flash --rollback

# Query co-processor health and active bank status:
solardeck-coproc-flash --status
```

* **Flashing Flow:**
  1. Linux tool writes the new binary into **Bank B (0x800000)** of the QSPI flash over high-speed SWD (`/dev/spidev0.1` or GPIO bitbang).
  2. The utility sets the boot pointer to Bank B and configures the RP2350 hardware watchdog to an **8-second countdown**.
  3. The utility asserts the `RUN` (reset) pin on the RP2350.
  4. The newly loaded firmware executes its initial sanity test: verifies internal clocks, checks I2C sensor bus responses, and sends an atomic `ACK_BOOT_OK` token back across the UART link to Linux.
  5. Upon receiving `ACK_BOOT_OK`, the Linux daemon clears the watchdog and marks Bank B as the active valid slot.
  6. **Automatic Rollback:** If the new firmware faults, freezes, or fails to emit `ACK_BOOT_OK` within 8 seconds, the RP2350 hardware watchdog expires, forcing an immediate hardware reset into **Bank A (Factory Golden Image)**. The entire rollback completes in $<2.5\text{ ms}$ with zero user intervention.

### 14.2 Immutable Linux Root Filesystem with OverlayFS
To prevent broken package installs, rogue scripts, or corrupted libraries from breaking the desktop OS:
* **The Base OS is Read-Only:** The base operating system (`/usr`, `/bin`, `/lib`, `/opt`) is mounted as a read-only, compressed SquashFS image protected by Linux kernel `dm-verity`. Any attempt to tamper with base system binaries is rejected at the block layer.
* **The Writable Layer (OverlayFS):** All user configuration files, custom installed applications, home directory files (`/home/deck`), and Claude Code project workspaces write to a transactional F2FS read-write layer layered on top of the read-only base via `OverlayFS`.
* **Instant 3-Second Factory Reset:**
  If an experiment, dependency conflict, or corrupted library breaks the user environment:
  ```bash
  solardeck-reset --safe
  ```
  This command flushes the writable upperdir overlay, leaving the underlying base operating system completely intact. The system boots in **3 seconds** into a fresh, pristine factory state with all default window configurations, audio drivers, and telemetry daemons restored.
* **Dual-Kernel Boot Fallback:** The U-Boot bootloader maintains primary (`kernel_A`) and fallback (`kernel_B`) images on eMMC. If a kernel update causes a kernel panic, the hardware watchdog trips the system into the fallback kernel automatically on the next reboot.

---

## 15. USB-C Secondary Display Sink Daemon (`solardeck-sinkd`)

Enables SolarDeck to act as an instantaneous, driverless 10.3" sunlight-readable secondary display for MacBooks, ThinkPads, and iPads over USB-C Port 1:

* **USB Composite Gadget Pipeline:** Leverages Linux kernel `libcomposite` configfs to expose a high-speed USB Video Class (UVC) capture endpoint or CDC-NCM Ethernet gadget.
* **Low-Latency Rendering:**
  * When plugged into a laptop, `solardeck-sinkd` accepts video frames via Weylus, Deskreen, or Moonlight.
  * Extracted bounding boxes are converted to 1-bit or 2-bit blue-noise dithered bitmaps on the VideoCore VI GPU and pushed directly to the IT8951 EPDC via 24 FPS MIPI-DSI.
* **Host Power Ingestion:** Simultaneously draws charging power from the host laptop via the CH224K USB-PD sink controller, keeping SolarDeck charged indefinitely during long outdoor work sessions.

---

## 16. EDC Phone Symbiosis & Dual-Screen Hybrid Cyberdeck Toolchain

Enables seamless software integration between SolarDeck and a compact pocket communicator (Clicks Communicator, Unihertz Jelly Star, Sony Xperia 10 VI), transforming the pair into a balanced, power-sipping mobile workstation:

### 16.1 Bluetooth PAN Low-Power Internet Tethering Daemon (`solardeck-pan-connect`)
Provides instant, zero-touch internet over Bluetooth without touching the pocket phone:

```bash
#!/usr/bin/env bash
# /usr/local/bin/solardeck-pan-connect
# Auto-connects to paired phone's Bluetooth NAP (Network Access Point) upon S2idle wake
set -euo pipefail

PHONE_MAC=$(cat /etc/solardeck/phone_mac.conf 2>/dev/null || true)
[[ -z "$PHONE_MAC" ]] && exit 0

# Check if phone is within BLE/BR-EDR range (3-second timeout)
if hcitool name "$PHONE_MAC" >/dev/null 2>&1; then
    # Establish BNEP network link (sips ~0.05W on phone and tablet)
    bt-network -c "$PHONE_MAC" nap >/dev/null 2>&1 || true
    # Request DHCP lease from phone's Personal Hotspot gateway (172.20.10.x / 192.168.44.x)
    dhclient -q bnep0 2>/dev/null || true
fi
```

* **Power Profile:** Consumes **~0.10W total system power** across both devices (compared to 1.8W–2.3W for a Wi-Fi hotspot), keeping the phone ice-cold in your pocket with 2–3 days of battery life.
* **Auto-Wake Integration:** Triggered via systemd sleep hook (`/lib/systemd/system-sleep/solardeck-pan`) within **2.0 seconds** of co-processor S2idle wake.

### 16.2 Dynamic Wayland/Sway Viewport Resizing (`solardeck-chin-dock`)
When clipping a pocket phone (Clicks Communicator) over the lower portion of the 10.3" screen to create a handheld dual-screen cyberdeck:

```bash
#!/usr/bin/env bash
# /usr/local/bin/solardeck-chin-dock [--dock | --undock]
# Shifts active Wayland workspace upwards to clear the occluded bottom display region

ACTION="${1:---toggle}"

if [[ "$ACTION" == "--dock" ]]; then
    # Occlude bottom 400 pixels (1872x1404 -> 1872x1004 active viewport)
    swaymsg "gaps bottom 400"
    # Set occluded lower region to pure static black/white (0.000W holding power)
    notify-send -t 1500 "SolarDeck" "Cyberdeck Chin-Dock Engaged: 1872x1004 Viewport"
elif [[ "$ACTION" == "--undock" ]]; then
    # Restore full 10.3" 1872x1404 canvas
    swaymsg "gaps bottom 0"
    notify-send -t 1500 "SolarDeck" "Full 10.3\" Canvas Restored: 1872x1404"
fi
```

* **Center of Gravity:** Eliminates wrist torque by placing the phone directly over the lower bezel, allowing both hands to grip the rigid bottom chassis of SolarDeck.
* **Dual-Screen Symbiosis:** The 10.3" E-Ink top canvas runs Neovim, terminal, and Claude Code CLI; the phone's 4.03" AMOLED screen underneath displays live color Google Maps, audio controls, or Signal chat alongside physical tactile QWERTY thumb keys.

### 16.3 Hybrid Remote-Builder Toolchain (`bld --remote`)
Eliminates thermal throttling and battery drain during heavy compilation (Linux kernels, DRM tree, large Rust/C++ projects):

```bash
# Local compile (<15s small tools, Python, Go, C daemons, Pico-SDK RP2350 .uf2):
bld

# Remote offload (cross-compiles on home Apple Silicon / Ryzen workstation over Tailscale):
bld --remote
```

* **The Remote Pipeline:**
  1. SolarDeck computes a local `git diff` or working-tree sync (~5KB upload).
  2. Pushes diff over encrypted **Tailscale (WireGuard)** mesh VPN to home workstation.
  3. Workstation cross-compiles for `aarch64-linux-gnu` inside an ephemeral Docker container in **5 to 15 seconds** (using Apple M3/M4 or Ryzen multi-core power).
  4. Workstation SCPs the stripped ARM64 binary back to `/usr/local/bin` and hot-reloads the service.
* **Energy Impact:** Consumes **~180 Joules** on SolarDeck vs **18,000 Joules** for a local kernel compile—a **100× power reduction** that keeps the fanless aluminum chassis completely cool in direct sunlight.
* **Resilient Mosh Transport:** Paired with **Mosh (Mobile Shell)** and Tmux, cell tower handoffs or tunnel disconnects never drop the terminal session.

### 16.4 Smartphone Thumbboard HID Forwarding
Enables typing on the Clicks Communicator's physical tactile QWERTY keyboard to input directly into SolarDeck:
* **Bluetooth HID Mode:** Android runs an open-source Bluetooth HID peripheral service; SolarDeck recognizes it as a standard wireless keyboard (`/dev/input/eventX`).
* **Wired USB Link:** A 3cm flat ribbon U-cable bridges USB-C Port 2 directly into the phone, dropping keystroke latency to **<1 millisecond** while providing 15W reverse charging.
* **1-Button Hardware Focus Flip:** Tapping the Clicks Communicator's programmable side key flips typing focus between SolarDeck's terminal and local phone SMS/Google Maps in **0 milliseconds**.
* **Capacitive Touch Scrolling:** Swiping thumbs vertically across the physical keycaps sends Page Up / Page Down or scroll-wheel events to Wayland, enabling smooth document reading without lifting hands.

---

## 17. Sovereign Voice Assistant & Local Agent Daemon (`solardeck-voiced`)

*Written 2026-10-19 14:15 UTC in the Pi harness by antigravity/gemini-3.8-flash*

The `solardeck-voiced` daemon orchestrates hands-free and push-to-talk voice intelligence using a 3-tier cascade that preserves battery life while providing speaker verification and interruption (barge-in):

```
                                      VOICE PIPELINE
┌──────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
│   Knowles MEMS Array     │ PDM  │    RP2350 Co-Processor   │ GPIO │   Raspberry Pi CM4       │
│  (Hardware VAD <0.05mW)  ├─────►│  (microWakeWord ~14mW)   ├─────►│  (S2idle Wake: 250ms)    │
└──────────────────────────┘      └──────────────────────────┘      └────────────┬─────────────┘
                                                                                 │
             ┌───────────────────────────────────────────────────────────────────┘
             ▼
┌──────────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────────┐
│ Resemblyzer Biometrics   │ OK   │ whisper.cpp (base.en)    │ Text │ Local 3B LLM / Claude CLI│
│ (Speaker ID Cosine >=.78)├─────►│ Speech-to-Text (<450ms)  ├─────►│ Tool & Script Execution  │
└──────────────────────────┘      └──────────────────────────┘      └────────────┬─────────────┘
                                                                                 │
             ┌───────────────────────────────────────────────────────────────────┘
             ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│   Piper Fast TTS         │ PCM  │ MAX98357A Speaker Amp    │
│  (<120ms Synthesis)      ├─────►│ + Loopback AEC (Barge-In)│
└──────────────────────────┘      └──────────────────────────┘
```

### 17.1 Acoustic Echo Cancellation (AEC) & Seamless Interruption
* **The Barge-In Mechanism:** When SolarDeck speaks or generates audio, the audio frame buffer feeding the MAX98357A I2S amplifier is mirrored into a PipeWire loopback sink (`module-loopback`).
* **SpeexDSP / WebRTC AEC3:** The acoustic canceller subtracts the known output waveform from the live Knowles MEMS microphone input.
* **The Result:** Even when the speaker is playing at full volume, the operator can speak *"Stop"* or *"Never mind, check battery instead"*, instantly halting speech output and executing the new directive.

### 17.2 Voice Biometrics Enrollment & Rejection
* **Enrollment:** The operator runs `solardeck-voice-enroll`, speaking 3 sample sentences. A 256-d d-vector embedding is extracted via Resemblyzer and saved to `/etc/solardeck/owner_voice.npy`.
* **Cosine Verification:**
  ```python
  # /usr/local/bin/verify_speaker.py
  import numpy as np

  def is_owner(sample_emb, owner_emb, threshold=0.78):
      cos_sim = np.dot(sample_emb, owner_emb) / (np.linalg.norm(sample_emb) * np.linalg.norm(owner_emb))
      return cos_sim >= threshold
  ```
* **Bystander Immunity:** Radio chatter, bystanders, or synthetic speech with similarity $<0.78$ are discarded; CM4 returns to S2idle without executing commands.

### 17.3 Self-Improvement & System Modification by Voice
* Voice commands can invoke the local LLM or Claude Code CLI with tool permissions:
  * *"Increase screen refresh cadence to 500 milliseconds."* $\to$ Modifies `/etc/eink-refreshd.conf` and reloads daemon.
  * *"Search offline Kiwix for treatment of venomous scorpion stings."* $\to$ Queries ZIM database and renders formatted Markdown.
  * *"Recompile RP2350 firmware with 150ms wake timer."* $\to$ Compiles `.uf2` and flashes co-processor Bank B with watchdog verification.

---

## 18. Campervan Dual-Head Wayland Orchestrator (`solardeck-dockd`)

Automates dynamic multi-head display configuration when docking SolarDeck to external monitors:

```bash
#!/usr/bin/env bash
# /usr/local/bin/solardeck-dockd: Listens for HDMI udev hotplug events
set -euo pipefail

EVENT="${1:-}"
HDMI_PORT="HDMI-A-1"
INTERNAL_PANEL="DSI-1"

if [[ "$EVENT" == "plug" ]]; then
    # Detect external resolution and refresh rate
    EXT_RES=$(wlr-randr | awk "/^$HDMI_PORT/,/^[A-Z]/" | grep -E "^\s+[0-9]+x[0-9]+" | head -1 | awk '{print $1}')
    
    # Enable external output above or right of 10.3" E-Ink
    swaymsg output "$HDMI_PORT" enable mode "$EXT_RES" pos 0 0
    swaymsg output "$INTERNAL_PANEL" pos 0 1800
    
    # Bind Workspaces 1-8 to external screen (Intense coding/browser/Kiwix)
    for ws in {1..8}; do
        swaymsg workspace "$ws" output "$HDMI_PORT"
    done
    
    # Bind Workspaces 9-10 to internal 10.3" screen (Van telemetry, notes, LoRa chat)
    swaymsg workspace 9 output "$INTERNAL_PANEL"
    swaymsg workspace 10 output "$INTERNAL_PANEL"
    
    # Restrict Wacom EMR Stylus input strictly to internal 10.3" display
    swaymsg input "type:tablet_tool" map_to_output "$INTERNAL_PANEL"
    
    notify-send -t 2000 "SolarDeck Dock" "External Display Connected: $EXT_RES (Workspaces 1-8 mapped)"
elif [[ "$EVENT" == "unplug" ]]; then
    swaymsg output "$HDMI_PORT" disable
    swaymsg output "$INTERNAL_PANEL" pos 0 0
    for ws in {1..10}; do
        swaymsg workspace "$ws" output "$INTERNAL_PANEL"
    done
    notify-send -t 2000 "SolarDeck Dock" "Mobile Mode Restored: Full 10.3\" Canvas"
fi
```

### 18.1 Giant External E-Ink Secondary Monitor Power Economics
* **Dasung Paperlike 253 / Boox Mira Pro 25.3" (3200 × 1800):** Connects via standard HDMI.
* **0.000W Static Power Sipping:** When reading code, schematics, or documentation, the external E-Ink monitor draws **0.000W** holding power.
* **Sunlight Immunity:** Operates inside sun-drenched campervans with doors wide open; contrast improves under direct sunlight while drawing $10\times$ less power than a 27" 4K LED backlight.

---

## 19. Blackout Emergency SOS Beacon Engine (`solardeck-sosd`)

Governs the zero-battery supercapacitor cold-boot survival sequence:
1. When supercapacitor reaches 3.3V, RP2350 executes emergency bootstrap from ROM.
2. Ingests last-valid Qualcomm GNSS fix and DS3231 timestamp from battery-backed NVRAM.
3. Transmits 915 MHz / 868 MHz LoRa distress burst: `!SOS <LAT> <LON> <ALT> <TIME> <BLOOD_TYPE>`.
4. Renders indelible high-contrast distress placard onto the 10.3" bi-stable screen before voltage drops below 2.0V.
5. Once drawn, the distress message remains visible on the E-Ink display indefinitely with **0.000W battery consumption**.

---

## 20. Wacom Precision Field Caliper & CAD Digitizer (`solardeck-caliper`)

A hardware-assisted software measurement tool leveraging the Wacom EMR 10.0mm hover sensing and Goodix mutual capacitance:

```bash
# Launch precision field caliper overlay in Wayland:
solardeck-caliper --hover
```

* **Hover Mode (0.1 mm Resolution):** Tracks the stylus tip suspended up to 10 mm above delicate physical objects (leaves, biological specimens, wet electronics). Tapping twice calculates $(X_2 - X_1, Y_2 - Y_1)$ distance, angle, and radius.
* **Conductive Component Auto-Centroid:** Detects metallic bolts, washers, or drill bits placed on the glass. Reads the mutual capacitance contact matrix and computes the major and minor axes, displaying:
  `Bolt Length: 25.4 mm | Thread Diameter: 3.0 mm (M3) | Pitch: 0.5 mm`.
* **1-Click CAD Export:** Exports traced dimensions directly to standard 1:1 DXF or SVG files for immediate 3D printing on field fabricators.

---

## 21. Autonomous LLM Hardware Self-Diagnosis & Built-In Self-Test (BIST) Engine (`solardeck-diag`)

*Written 2026-10-19 14:35 UTC in the Pi harness by antigravity/gemini-3.8-flash*

The `solardeck-diag` diagnostic specification defines an integrated Built-In Self-Test (BIST) architecture that allows local sovereign LLMs (Qwen 2.5 3B, Llama 3.2 3B) and Claude Code CLI to programmatically inspect every power rail, communication bus, peripheral IC, and radio module in under 400 milliseconds, diagnosing hardware anomalies and executing active self-healing.

### 21.1 8-Subsystem BIST Telemetry & Register Map
When invoked via CLI or local agent tool call (`solardeck-diag --json`), the engine performs an atomic sweep across eight hardware inspection domains:

1. **Power Domain & Rail Current Telemetry (TI INA3221 & BQ25895):**
   * Reads high-side voltage and current across Rail 1 (CM4 Core), Rail 2 (EPDC Display), and Rail 3 (Modem/Radios).
   * Flags current anomalies: Rail 3 idle draw $>1\text{ mA}$ in sleep (phantom leakage), or Rail 1 current $>2.8\text{ A}$ (thermal/power saturation).
   * Reads BQ27441 battery health: pack voltage (3.2V nominal LiFePO4), state of charge (SoC %), internal cell impedance ($R_{\text{cell}} \le 45\text{ m}\Omega$), and cycle count.
   * Reads BQ25895 charge registers: fault flags (thermal shutdown, watchdog timer expiration, input overvoltage).
2. **Co-Processor & Low-Power Bus Domain (RP2350B):**
   * Pings the RP2350 over SPI/UART with a 64-byte random challenge; verifies CRC-8 return checksum in $<10\text{ms}$.
   * Queries 8MB PSRAM memory test pattern registers and checks DS3231/RV-3028 RTC synchronization drift ($|\Delta t| < 500\text{ms}$).
   * Reads 12-bit ADC raw voltages from the top-bezel IXYS micro-solar strip and supercapacitor rail.
3. **Display & Waveform Controller Domain (ITE IT8951 EPDC):**
   * Reads Device Info Register: validates panel geometry ($1872 \times 1404$), engine firmware version, and Look-Up Table (LUT) integrity.
   * Polls `HRDY` (Host Ready) pin state; checks for stuck busy flags indicating unseated FPC ribbon cables or frozen pigment microcapsules.
   * Reads panel temperature from backplane TMP112 sensor ($0^\circ\text{C}$ to $+50^\circ\text{C}$ safe operating window).
4. **I2C Sensor Fabric Domain (Bus 1 & Bus 2):**
   * Sweeps I2C addresses `0x00` through `0x7F` at 400 kHz:
     * `0x60`: Bosch BMP390 Barometer (verifies chip ID `0x60`, pressure sanity $300\text{–}1100\text{ hPa}$).
     * `0x12`: Bosch BMA400 Accelerometer (executes internal electrostatic self-test deflection).
     * `0x68`: Maxim DS3231 RTC (reads oscillator stop flag `OSF`; checks battery backup coin-cell voltage).
     * `0x5D` / `0x14`: Goodix Touch Controller (reads mutual-capacitance baseline calibration frame).
     * `0x34`: Syntiant NDP120 Neural Decision Processor (probes `WHO_AM_I` register; if NACK, triggers RP2350 software fallback).
5. **RF & Wireless Mesh Domain (Quectel EG25-G & Semtech SX1262):**
   * **Cellular Modem:** Sends AT command handshake via `/dev/ttyUSB2`: `AT+CPIN?` (SIM card presence), `AT+CSQ` (signal quality), `AT+QENG="servingcell"` (tower info).
   * **LoRa Transceiver:** Sends SPI opcode `0xC0` (`GetStatus`): verifies PLL lock, PA over-current protection flag, and antenna impedance match.
   * **Qualcomm GNSS:** Verifies NMEA sentence stream on `/dev/ttyUSB1`; counts tracked SVs (Satellites in View) and checks Fix status (2D/3D).
6. **Optical & Multimodal Sensor Domain (Sony IMX708 Camera):**
   * Probes V4L2 device `/dev/video0` via MIPI CSI-2.
   * Reads sensor ID (`0x0708`) over camera I2C control bus; runs a 5-step voice coil motor (VCM) autofocus calibration sweep.
7. **Acoustic & Voice Front-End Domain (Knowles MEMS & MAX98357A):**
   * Samples 20ms ambient audio frame from ALSA capture device; verifies noise floor SNR $> 35\text{ dB}$ (detects blocked acoustic vents or cracked solder joints).
   * Verifies MAX98357A I2S Class-D speaker loopback AEC channel integrity.
8. **Storage, External Ports & Hardware Safety Domain:**
   * Reads eMMC life-time wear estimation registers via `mmc extcsd read` (Type A & Type B device health).
   * Reads M.2 NVMe SSD SMART health telemetry (`smartctl --json`) for bad sectors and temperature.
   * Checks Micro-HDMI Hot-Plug Detect (`HPD`) GPIO pin state.
   * Checks USB-C Port 1 and Port 2 CC controller registers (TUSB320) for VBUS voltage, orientation, and short-circuit faults.
   * Reads physical Hardware Airgap Switch state pin (`AIRGAP_STAT`): 0V (Stealth Airgap Active) vs 3.3V (Normal Radio Operation).

### 21.2 Structured Diagnostic JSON Output Schema
```json
{
  "timestamp": "2026-10-19T14:35:00Z",
  "bist_duration_ms": 342,
  "overall_status": "WARNING",
  "domains": {
    "power": {
      "status": "PASS",
      "vbat_mv": 3280,
      "soc_pct": 88,
      "cell_impedance_mohm": 34,
      "rail_1_core_ma": 420,
      "rail_2_display_ma": 12,
      "rail_3_radios_ma": 385,
      "solar_voltage_mv": 1820
    },
    "coprocessor": {
      "status": "PASS",
      "firmware_version": "v1.4.2-rp2350",
      "psram_test": "OK",
      "rtc_drift_ms": 12
    },
    "display": {
      "status": "PASS",
      "epdc_model": "IT8951",
      "temp_c": 32.4,
      "panel_ready": true
    },
    "i2c_bus": {
      "status": "PASS",
      "devices_detected": ["0x60", "0x12", "0x68", "0x5D", "0x40", "0x6B"],
      "syntiant_ndp120_present": false,
      "wake_engine_active": "rp2350_microwakeword"
    },
    "wireless": {
      "status": "WARNING",
      "lora_sx1262": {"status": "PASS", "pll_locked": true, "vswr_fault": false},
      "lte_modem": {"status": "FAIL", "at_handshake": false, "current_draw": "STALL_420mA"},
      "gnss": {"status": "PASS", "satellites_tracked": 9, "fix": "3D"}
    },
    "cameras_audio": {
      "status": "PASS",
      "imx708_autofocus": "OK",
      "knowles_mics_snr_db": 42.1
    },
    "storage": {
      "status": "PASS",
      "emmc_wear_est": "0x01_NORMAL",
      "nvme_temp_c": 38.0
    },
    "safety_airgap": {
      "switch_position": "NORMAL_3.3V",
      "rf_enabled": true
    }
  }
}
```

### 21.3 LLM Reasoning & Plain-English Interpretation Rules
When the user queries system health ("Is anything broken?"), the LLM follows four strict diagnostic rules:
1. **Symptom-to-Hardware Correlation:** Never state raw register values alone; explain the physical meaning (e.g. *"LTE Modem AT handshake failed and Rail 3 is drawing 420mA, which means the modem firmware is hung in a network registration loop"*).
2. **False-Positive Filtering:** Cross-check the Hardware Airgap Switch (`AIRGAP_STAT`). If the airgap switch is in STEALTH mode, radio NACKs are expected and reported as *"Radios safely unpowered by physical airgap switch (0.000W)"* rather than hardware failures.
3. **Safety Clamping:** If battery cell impedance exceeds $85\text{ m}\Omega$ or display temperature exceeds $+55^\circ\text{C}$, the LLM flags an immediate safety alert and instructs the operator to disconnect solar charging.

### 21.4 Active Hardware Self-Healing & Power-Gated Mitigation
Beyond passive diagnosis, the LLM is authorized to invoke targeted mitigation commands using the TPS22918 load switches and system daemons:
* **`solardeck-heal --powercycle modem`:** Asserts the modem's dedicated load switch gate to 0.000V for 500ms, performing a cold electrical power-cycle of the Quectel EG25-G to recover from cellular network lockups.
* **`solardeck-heal --clear-epdc`:** Commands `eink-refreshd` to execute an atomic 3-phase high-voltage global inversion to rebalance DC pigment bias and eliminate persistent electrophoretic ghosting.
* **`solardeck-heal --coproc-ping`:** Flushes the RP2350 UART buffer and strobes the hardware `COPROC_RESET` pin if co-processor heartbeat packets are dropped.
* **`solardeck-heal --port2-trip-reset`:** Re-enables the TI TPS2051B USB-C Port 2 power switch after an overcurrent or short-circuit event has cleared.

