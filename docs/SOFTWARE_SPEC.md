# SolarDeck Software Specification

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

### 2.3 Direct Framebuffer Pen Overlay
* To achieve reMarkable-class stylus latency (< 20ms), stylus coordinates bypass the Wayland window manager and write directly to the hardware EPDC partial-refresh line buffer, creating instantaneous ink under the pen tip.

---

## 3. Power Management & Deep Sleep (Suspend-to-RAM)

### 3.1 Fast Sleep / Instant Wake Pipeline
* **Suspend-to-RAM (S2idle):**
  * When sleep is triggered, Linux freezes userspace tasks, flushes file caches, cuts peripheral power switches (TPS22918), and drops the LPDDR4 memory controller into Self-Refresh mode.
  * Power draw drops to **15 mW**.
* **Instant Wake (0.3 Seconds):**
  * Touching any key or tapping the touch bar sends a hardware interrupt from the RP2040 to GPIO 17 on the CM4.
  * The CM4 restores CPU clock lines and resumes execution directly from RAM in **under 300 milliseconds**. All open terminal windows and Claude sessions remain intact.

### 3.2 The Ambient LifeOps Mode (RP2040 Firmware)
While the main CM4 is asleep, the RP2040 runs bare-metal C firmware:
1. **1-Second Clock Tick:**
   * Reads seconds from the DS3231 RTC.
   * Sends a SPI bounding-box command (`40×60` pixels) to the IT8951 controller to update only the second digits.
2. **15-Minute Wi-Fi Background Burst:**
   * Every 15 minutes, pulses a power gate to wake the Wi-Fi chip for 1.8 seconds.
   * Performs an HTTP GET request to fetch OpenWeatherMap Honolulu data and Sunrun/HECO rate schedules.
   * Writes the updated weather icons to the e-paper, then cuts Wi-Fi power.
3. **Shadow-Wave Gesture Engine:**
   * Reads the analog voltage from the front solar strip via ADC pin `GPIO26`.
   * A sudden voltage dip followed by immediate recovery (`1.8V → 0.3V → 1.8V` over 250ms) is recognized as a hand wave.
   * Triggers a page-turn event or wakes the screen touchlessly.

---

## 4. Claude Code & AI Integration

* **Terminal Coding:** Runs `claude` CLI natively in Alacritty / Foot terminal with tmux session persistence.
* **Voice Speech-to-Text (STT):**
  * **Offline Mode:** Uses `whisper.cpp` (Quantized `tiny.en` or `base.en` model) running locally on the Cortex-A72 cores using NEON SIMD instructions (transcription latency < 1.2 seconds).
  * **Cloud Mode:** Streams 16kHz audio from the I2S MEMS microphones directly to the Anthropic voice/audio API over 4G LTE.
* **Local Medical & Diagnostics Copilot:**
  * Integrates with locally installed small language models (via `llama.cpp` using 4-bit quantization) for completely air-gapped medical knowledge querying.

---

## 5. Offline Knowledge & Clinical Stack

* **Kiwix Offline Engine:**
  * Runs a local headless HTTP server indexing 100GB+ `.zim` archive files:
    * Complete English Wikipedia with full images (~95GB).
    * Classical Chinese Medicine Canon: *Huangdi Neijing*, *Shanghan Lun*, *Shennong Bencao Jing*, *Zhenjiu Dacheng*.
    * Western Medical Library: Merck Manual, PubMed clinical summaries, ICD-10 diagnostic codes.
* **Zi Wu Liu Zhu (Acupuncture Horary Chronometer):**
  * A custom Python daemon calculates **Honolulu True Solar Time (Zhen Tai Yang Shi)** based on longitude (157.8583° W):
    * Displays current BaZi Heavenly Stems & Earthly Branches (Year, Month, Day, Hour).
    * Calculates active 24 Solar Terms (*Jie Qi*).
    * Highlights active open acupuncture channels and *Ling Gui Ba Fa* (Mysterious Turtle Eight Points) in real-time.

---

## 6. Flipper Zero RF Toolchain

* **Sub-GHz Radio:** Controlled via `rfcat` or `Universal Radio Hacker (URH)` for analyzing 315/433 MHz signals.
* **Infrared:** Controlled via `LIRC` (Linux Infrared Remote Control) with preloaded profiles for home A/C units, TVs, and projectors.
* **NFC / RFID:** Controlled via `libnfc` and `proxmark3` CLI tools for cloning and emulating Mifare Classic, NTAG, and 125 kHz HID fobs.
* **BadUSB:** Configured via Linux USB Gadget API (`/sys/kernel/config/usb_gadget/`) allowing the device to emulate a USB HID keyboard/mouse for automated script injection.
