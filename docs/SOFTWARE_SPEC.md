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
```

### 2.1 The 20ms "Typing Waveform" (LUT Tuning)
* In the IT8951 kernel driver (`/drivers/gpu/drm/tinydrm/`), we load a custom Look-Up Table (LUT) that issues a single 25ms electrical voltage pulse to turn pixels black without the intermediate erasing clear cycle.
* This allows **typing in Claude Code at 30 to 45 FPS** with zero perceptible latency.

### 2.2 Intelligent Anti-Ghosting Daemon
* A lightweight background daemon (`eink-refreshd`) monitors typing cadence:
  * While the user is actively typing, the screen remains locked in Fast 1-bit Mode.
  * When keystrokes pause for **1.5 seconds**, the daemon quietly triggers an asynchronous anti-ghosting micro-clear. The user experiences LCD-like speed while typing, and paper-sharp clarity when reading.

### 2.3 Direct Zero-Compositor Pen Overlay Daemon (`solardeck-inkd`)
* To achieve true paper-like handwriting latency (**< 18ms tip-to-ink**), stylus strokes completely bypass Wayland, Sway, and windowing frameworks:
  1. `solardeck-inkd` reads raw coordinates directly from `/dev/input/event*` (Wacom EMR 240 Hz stream) in non-blocking mode.
  2. A fast Bresenham line algorithm calculates the micro-line bounding box between sequential coordinates (e.g., a tiny 12×18 pixel rectangle).
  3. Writes the damaged rectangle directly into the IT8951 EPDC memory over 24 MHz SPI using the **1-bit Direct Update (DU)** waveform register (`IT8951_CMD_WRITE_PIXEL_AREA`), applying a single 12ms pulse.
  4. When the pen lifts for $>500\text{ ms}$, the daemon asynchronously delivers the complete vector stroke (`x, y, pressure, tilt, timestamp`) to the active document application (Xournal++, Obsidian, or Zathura) to commit the layer to disk, followed by a regal anti-ghosting micro-clear.

### 2.4 Teleconference & Video Call Engine ("Conference Mode")
To support high-definition video calls on Discord, Google Meet, and Zoom without overwhelming the E-Ink display:
1. **Outgoing 1080p30 Stream:**
   * Captured by the front 5MP Sony IMX219 sensor via `libcamera` and Broadcom hardware ISP.
   * Encoded directly in silicon via hardware H.264/H.265 encoder at 30 FPS, transmitting crisp color video to remote participants.
2. **Inbound Presentation & Shared Screens:**
   * Incoming screen shares (slides, code, whiteboards) render in full 16-bit grayscale (GC16) at 300 PPI with exceptional readability.
3. **Inbound Participant Video Thumbnails:**
   * Displayed in a compact floating overlay rendered in **A2 Motion Mode (60–75ms refresh, 2-bit grayscale)**.
   * **Smart-Still Toggle:** Automatically freezes participant video into a crisp still portrait, refreshing only when the active speaker changes or every 3 seconds, cutting display power by 85% while keeping audio 100% real-time.

---

## 3. Power Management & Deep Sleep (Suspend-to-RAM)

### 3.1 Fast Sleep / Instant Wake Pipeline
* **Suspend-to-RAM (S2idle):**
  * When sleep is triggered, Linux freezes userspace tasks, flushes file caches, cuts peripheral power switches (TPS22918), and drops the LPDDR4 memory controller into Self-Refresh mode.
  * Power draw drops to **15 mW**.
* **Instant Wake (0.3 Seconds):**
  * Touching any key or tapping the touch bar sends a hardware interrupt from the RP2040 to GPIO 17 on the CM4.
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
│    • OPT3001 (Lux) • BMA400 (Motion) • Quectel/SX1262 (RF Link Metrics)     │
│                                  │                                          │
│                                  ▼ (10Hz / 1Hz / 0.1Hz Sampling)            │
│ 2. TELEMETRY DAEMON (`solardeck-telemetryd`):                               │
│    • Circular SQLite Database: `/var/log/solardeck/telemetry.db` (WAL mode) │
│    • Structured Tables: power_rails, battery_health, thermals, rf, motion   │
│                                  │                                          │
│         ┌────────────────────────┼────────────────────────┐                 │
│         ▼                        ▼                        ▼                 │
│ [TIER 1: IMMEDIATE LOCAL]  [TIER 2: RUNTIME AI TUNING] [TIER 3: HARDWARE REV 2]│
│ • Waveform LUT Temp Comp   • `solardeck-optimize`     • Long-term Inrush/Heat│
│ • 0% Frontlight in Sun     • Claude Code CLI Tuning   • Feature Usage (YAGNI)│
│ • Dead Cellular Power-Cycle• Custom power.conf & udev • Automated KiCad Gen │
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
   * **Ambient Lux Scaling:** When the OPT3001 reads $>10,000\text{ lux}$ (direct sunlight), the front-light is locked to 0% and E-ink contrast curves are maximized.
   * **Dead-Socket Power Cycle:** If the RF rail ammeter registers continuous active transmission power ($>1.2\text{W}$) for >45 seconds without network throughput, the daemon automatically pulses the modem's TPS22918 load switch to reset the baseband.
2. **Tier 2: Runtime System Profile Self-Tuning (`solardeck-optimize`):**
   * Running `solardeck-optimize` aggregates the past 24 hours of telemetry into a dense JSON payload and passes it to Claude Code:
     ```bash
     solardeck-cli telemetry export --last 24h --json | claude "Analyze power anomalies and generate tuned /etc/solardeck-power.conf"
     ```
   * The LLM identifies parasitic drains, optimizes core parking thresholds, and adjusts charging currents to preserve battery longevity.
3. **Tier 3: Long-Term Hardware Evolution Loop (Rev 1 $\to$ Rev 2 PCB Redesign):**
   * Once a hardware board is built, silicon is set in stone—**unless your design files are machine-readable**.
   * Because SolarDeck's schematics and layouts are maintained in plain-text KiCad format (`.kicad_sch` and `.kicad_pcb`), an LLM can analyze months of real-world operational logs and generate the engineering revisions for Rev 2:
     * **Capacitor & Regulator Right-Sizing:** If peak inrush logs show the Quectel LTE modem never pulls more than 1.6A, the oversized 470µF tantalum decoupling capacitor is safely downsized to two compact 100µF ceramic capacitors in Rev 2, saving board area and cost.
     * **Thermal Gradient Relief:** If thermal logs show a 12°C gradient between the CM4 CPU and the battery pouch during long Claude Code compile sessions, the LLM generates a KiCad PCB layout modification script (using KiCad's `pcbnew` Python API) to rotate the module and insert copper-pour thermal vias to vent heat out the chassis edge.
     * **Hardware YAGNI Pruning:** If peripheral telemetry logs show that an expansion rail or auxiliary port was utilized less than 0.1% over six months, the LLM flags it for deletion in Rev 2, reducing weight, BOM cost, and trace complexity.

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
  * **Ambient Nightstand Beacon:** When OPT3001 reads $< 0.5\text{ lux}$ (pitch black) and device is on kickstand, pulses an ultra-faint warm white locator glow (2% duty cycle, $< 15\text{ µA}$) so you can effortlessly find the tablet in the dark.

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
