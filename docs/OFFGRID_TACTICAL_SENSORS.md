# SolarDeck Off-Grid, Campervan & Tactical Sensor Expansion Specification

Written 2026-10-19 12:12 UTC in the Pi harness by antigravity/gemini-3.8-flash

Detailed architectural specification for campervan energy bus integration, enhanced sensor navigation (RTK, celestial plate-solving, 9-DOF IMU), grid-down doomsday survival hardware, frontlight optical engineering, and offline AI knowledgebase traversal.

---

## 1. Campervan & Mobile Living Energy Integration

SolarDeck's dual-brain architecture (CM4 Linux + RP2350 microcontroller) and connectivity options (BLE 5.0, USB-C Host, RS-485, CAN Bus) allow it to serve as a sovereign, zero-power campervan monitoring console and electrical diagnostics hub:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMPERVAN POWER BUS INTEGRATION                       │
├────────────────────┬─────────────────────────┬──────────────────────────────┤
│ SUBSYSTEM          │ PHYSICAL INTERFACE      │ PROTOCOL / DRIVER            │
├────────────────────┼─────────────────────────┼──────────────────────────────┤
│ Victron SmartSolar │ Bluetooth Low Energy    │ Passive Victron BLE Protocol │
│   & SmartShunts    │   (Non-pairing beacon)  │   (Instant Volts, Amps, SOC) │
│ Victron VE.Direct  │ USB-C Port 2 / UART     │ 19200-baud 3.3V ASCII Stream │
│ DIY LiFePO4 BMS    │ Bluetooth 5.0 (BlueZ)   │ `jbd-bms-cli`, `dalybms`     │
│   (JBD, Daly, ANT) │                         │   (Cell delta mV, thermals)  │
│ RV-C / Marine CAN  │ USB-to-CAN / SPI MCP2515│ Linux SocketCAN / J1939      │
│   (Inverters, Tank)│                         │   (RV-C standard PGNs)       │
│ Renogy / EPEVER    │ USB-to-RS485 Dongle     │ Modbus RTU / `libmodbus`     │
└────────────────────┴─────────────────────────┴──────────────────────────────┘
```

### 1.1 Victron Energy Passive BLE Sniffing
* **Mechanism:** Victron SmartSolar MPPTs, Orion-Tr Smart DC-DC chargers, and SmartShunts continuously transmit non-connectable BLE advertising beacons containing real-time telemetry (Battery Voltage, Amps, Watts, State of Charge, Yield).
* **Zero-Pairing Integration:** SolarDeck's CM4 captures these packets passively using `bleak` or a native C/Rust daemon (`solardeck-victron-ble`). No Bluetooth pairing, PIN codes, or handshakes are required. Telemetry is committed to `/var/log/solardeck/telemetry.db` every 1 to 5 seconds.
* **Wired Fallback (VE.Direct):** For metal campervan enclosures where 2.4 GHz RF is blocked, USB-C Port 2 accepts an isolated FTDI cable to read the native VE.Direct 19200-baud ASCII telemetry stream.

### 1.2 DIY LiFePO4 Battery Pack Management (JBD / Daly BMS)
* Connects over Linux BlueZ to over 90% of consumer and DIY campervan battery management systems.
* Tracks individual cell balancing voltages down to $\pm 1\text{ mV}$, high/low voltage cutoff thresholds, short-circuit faults, and MOS temperature limits.

### 1.3 RV-C CAN Bus Vehicle Gateway
* Modern expedition vehicles and campervans (Lithionics, BattleBorn, Mastervolt, Dometic, Victron Cerbo GX) use the open **RV-C protocol** (built on CAN Bus 2.0B / J1939 at 250 kbps).
* Mating a low-cost USB-CAN adapter (CANable / Candlelight firmware) to USB-C Port 2 or an onboard SPI CAN controller (MCP2515) exposes a native Linux `can0` interface via SocketCAN.
* SolarDeck monitors:
  1. High-voltage inverter status (AC output watts, shore power presence).
  2. Ultrasonic and resistive fresh/grey water tank level sensors.
  3. Hydronic and diesel cabin heater states (Webasto / Espar / Autoterm).

### 1.4 Perpetual E-Ink Van Wall Console
* **MagSafe Mount Integration:** SolarDeck mounts flush to an interior campervan bulkhead via its rear MagSafe magnetic array and M2.5 threaded brass inserts.
* **Circadian Advantage:** Unlike bright iPad or LCD camper monitors that illuminate the sleeping cabin with sleep-disrupting blue light, SolarDeck's frontlight locks to 0% at night. The screen displays battery health, solar yield, and water levels completely unlit, readable under natural moonlight, and drawing **0.000W** when static.

---

## 2. Advanced Sensors & Positioning (Beyond Standard GPS)

While standard single-band GPS provides 3 to 5 meter accuracy, SolarDeck's sensor architecture supports sub-meter satellite positioning, centimeter RTK, and zero-satellite celestial navigation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ENHANCED NAVIGATION & POSITIONING PIPELINE                  │
├───────────────────────┬─────────────────┬───────────────────────────────────┤
│ NAVIGATION TIER       │ TYPICAL ACCURACY│ HARDWARE / SENSOR MECHANISM       │
├───────────────────────┼─────────────────┼───────────────────────────────────┤
│ Standard GNSS (L1)    │ 3 – 5 Meters    │ Quectel EG25-G Qualcomm GNSS      │
│ Galileo HAS (E6)      │ < 20 cm         │ Satellite Precise Point Pos (PPP) │
│ Dual-Frequency RTK    │ 1.4 cm (0.5 in) │ u-blox ZED-F9P (L1/L2/L5 Carrier) │
│ Barometric Altitude   │ ± 10 cm         │ Bosch BMP390 (0.01 hPa I2C)       │
│ Optical Celestial Nav │ 0.5 – 1.0 Mile  │ 12MP Camera + DS3231 RTC (Zero RF)│
│ Inertial 9-DOF Vector │ Continuous $\Delta$│ Bosch BMI270 (6-DOF) + BMM350 Mag │
└───────────────────────┴─────────────────┴───────────────────────────────────┘
```

### 2.1 Centimeter-Level RTK & Galileo HAS (Multi-Band GNSS)
* **The RTK Upgrade Option:** The carrier board expansion header accommodates high-precision dual-frequency GNSS modules (**u-blox ZED-F9P** or **Quectel LC29H**). By tracking carrier phase cycles across L1, L2, and L5 bands alongside local RTCM differential corrections (via LoRa or cellular NTRIP), horizontal position accuracy drops to **1.4 centimeters**.
* **Galileo HAS (High Accuracy Service):** The European Galileo constellation transmits free, open-access correction parameters directly from orbit on the **E6 carrier (1278.75 MHz)**. This provides **sub-20 cm accuracy worldwide** without requiring ground base stations, internet access, or local radios.

### 2.2 9-DOF Celestial & Orientation IMU (Sensor-Driven Stargazing)
* **The Sensor Addition:** Complementing the onboard Bosch BMA400 accelerometer, the system integrates a 3-axis gyroscope and a 3-axis geomagnetic sensor (electronic compass) via a **Bosch BMI270 (6-DOF) + BMM350 (Magnetometer)** or an integrated **BNO085** orientation sensor.
* **Stellarium & Planetarium Night Mode:**
  * Running **Stellarium** or CLI tools (`skyfield`, `pyephem`) natively under Wayland.
  * Holding SolarDeck toward the night sky renders constellations, planets, and satellite pass tracks corresponding to the exact 3D vector of the device.
  * Inverted red-on-black or amber-on-black e-paper display modes preserve human rhodopsin (scotopic rod vision) with zero photon glare.

### 2.3 Optical Celestial Navigation & Plate-Solving (Zero-Satellite Doomsday Nav)
* **The Scenario:** In the event of satellite jamming, spoofing, orbital kinetic collisions (Kessler syndrome), or electromagnetic warfare, space-based GNSS becomes unavailable.
* **Optical Plate-Solving Pipeline:**
  1. The rear **12MP Sony IMX708 PDAF autofocus camera** captures a 1-second exposure of the night sky.
  2. A local, completely offline plate-solving engine (`astrometry.net` or `stellar-solver` with a compact 500MB Tycho-2/Hipparcos star catalog on NVMe) identifies geometric star triangles.
  3. The software computes the exact optical boresight coordinates (Right Ascension $\alpha$, Declination $\delta$) to sub-arcminute optical precision, immune to magnetic interference.
  4. Combining celestial sight reduction with the microsecond-precise UTC time from the **DS3231 TCXO RTC**, SolarDeck computes geographic latitude and longitude **without a single radio wave**.

---

## 3. Doomsday & Tactical Grid-Down Hardening

To guarantee survival and utility during severe natural disasters, infrastructure blackouts, or electromagnetic disturbances:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GRID-DOWN HARDENING ARCHITECTURE                         │
├────────────────────┬────────────────────────────────────────────────────────┤
│ SUBSYSTEM          │ IMPLEMENTATION SPECIFICATION                           │
├────────────────────┼────────────────────────────────────────────────────────┤
│ All-Band HF Radio  │ Si4732 / Si4735 DSP Receiver (LW, MW, SW 3–30M, SSB)   │
│ Radiation Monitor  │ Pocket Geiger Type 5 / BG51 Tube (RP2350 Interrupt)    │
│ Wild Power DC Port │ 3.9V–14V Raw DC Input to TI BQ25895 (Direct Solar/Auto)│
│ EMP Hardening      │ Sub-ns Bidirectional TVS Arrays + Faraday Storage      │
│ Physical Hardcopy  │ Mini 58mm Thermal Receipt Printer (ESC/POS Paper Map)  │
└────────────────────┴────────────────────────────────────────────────────────┘
```

### 3.1 All-Band HF / Shortwave / AM Radio Receiver (Si4732 / Si4735)
* **The Need:** While the RTL-SDR module covers VHF/UHF (24–1700 MHz), regional VHF repeaters die when emergency generator fuel runs out. Continental and trans-oceanic emergency intelligence broadcasts rely on **High-Frequency (HF) Shortwave (3–30 MHz)** and AM medium-wave radio.
* **The Silicon:** An ultra-low-power **Silicon Labs Si4732 / Si4735** all-band broadcast receiver IC connected over I2C/SPI:
  * Full coverage: AM (520–1710 kHz), Shortwave (2.3–30.0 MHz), Longwave (153–279 kHz), and FM (64–108 MHz).
  * Direct SSB (Single Sideband - USB/LSB) decoding for amateur ham radio emergency nets.
  * Operates on less than 15 mA total current.

### 3.2 Continuous Ionizing Radiation & Fallout Dosimeter
* **Sensor Selection:** Integrates a miniature solid-state radiation sensor (e.g., **Radiation Watch Pocket Geiger Type 5** or a miniature BG51 PIN diode sensor).
* **Autonomous Micro-Power Logging:** The pulse output is wired directly to an interrupt-enabled GPIO on the **RP2350 co-processor**.
  * RP2350 continuously accumulates Counts Per Minute (CPM) in background sleep ($I_Q < 15\text{ µA}$).
  * If radiation levels exceed normal ambient background threshold ($>0.25\text{ }\mu\text{Sv/hr}$), the RP2350 sounds the piezo buzzer, illuminates the ruby beacon, and fires `GPIO 17` to wake Linux with a radiological fallout contour map.

### 3.3 "Wild Power" Raw DC Input (Salvaged Power Harvesting)
* **The Problem:** In a disaster, regulated 5V USB-PD wall supplies do not exist. Power must be drawn from salvaged 12V car batteries, fluctuating 18V folding solar blankets, or improvised bicycle/water dynamos.
* **Implementation:** The carrier board routes an auxiliary rugged 2-pin screw terminal directly to the **TI BQ25895** buck charger:
  * Accepts raw DC voltages from **3.9V to 14.0V**.
  * Integrated Dynamic Power Management (VINDPM) prevents input voltage collapse when connected to weak or shaded solar panels.

### 3.4 Micro Thermal Hardcopy Receipt Printer (ESC/POS)
* **The Role:** Digital communication is ineffective if a companion's device is dead.
* **Operation:** Connects via USB-C or BLE to standard 58mm micro thermal receipt printers using standard ESC/POS commands. SolarDeck prints physical paper topographic snippets, medical step-by-step triage checklists, radio frequency rosters, and cryptographic public keys onto waterproof, inkless thermal paper.

---

## 4. Frontlight Optical Engineering & Spectrum Control

E-Ink panels are physically opaque (electrophoretic pigment microcapsules mounted on a steel or plastic backplane). They cannot be backlit.

```
                                [ AMBIENT SUNLIGHT / ROOM LIGHT ]
                                               │
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. PROTECTIVE MATTE COVER GLASS (Anti-Glare Etched Surface, 0% Glare)      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. ULTRA-THIN OPTICAL LIGHTGUIDE (Micro-Etched Extraction Prisms)           │
│    ◄── SIDE-FIRING BEZEL LED STRINGS: White (5000K) + Amber (2700K) + Red  │
│    (Light is directed downward onto the pigment capsules, then reflected up)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. 10.3" E-INK CAPSULE MATRIX (Black, White, Color Micro-Particles)         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. WACOM EMR DIGITIZER SHIELD (Behind Display Backplane, ~560 kHz RF)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Downward-Reflecting Lightguide Architecture
* **Physical Principle:** Bezel-mounted surface-mount LEDs inject light horizontally into the edge of a specialized micro-grooved optical lightguide film. The micro-prisms redirect light **strictly downward** onto the e-paper surface, which reflects back into the user's eyes.
* **Zero Eyestrain:** Photons reflect off paper naturally rather than shining directly out of a liquid crystal matrix into the user's retinas, completely eliminating optical fatigue.

### 4.2 2048-Step Logarithmic Dimming Curve
* **Driver:** Texas Instruments **TPS61163** dual-channel constant-current step-up driver.
* **Human Eye Perception:** Human luminous response is logarithmic. The RP2350 co-processor applies a 2048-step logarithmic PWM curve:
  * High-end: Smooth daylight fill illumination.
  * Low-end: Micro-adjustments below 0.1 lux, achieving a true **candlelight/moonlight floor (< 0.05 lux)** without flickering or jumping steps.

### 4.3 Spectrum Options: Dual CCT + Tactical Tri-Color Roadmap
1. **Cold-White (5000K):** High-contrast daytime reading in dimly lit rooms.
2. **Warm-Amber (2700K):** Circadian-safe night reading with zero blue light emission.
3. **Hardware Tri-Color Roadmap (630nm / 660nm Deep-Red):**
   * The frontlight FPC can populate interleaved **630nm/660nm monochromatic deep-red micro-LEDs**.
   * Provides full-screen, uniform red illumination across the 10.3" display.
   * Maintains 100% human night adaptation for dark-sky astronomy, tactical night navigation, and military flight decks.

---

## 5. Local Offline RAG (AI Knowledgebase Traversal)

SolarDeck runs a local, airgapped **Retrieval-Augmented Generation (RAG)** pipeline allowing users to query over 100GB of compressed human knowledge without external network access:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OFFLINE LOCAL RAG INFERENCE ENGINE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. USER PROMPT: Natural language query entered in terminal or voice         │
│                         │                                                   │
│                         ▼ (< 50ms over PCIe NVMe Gen 2 x1)                  │
│ 2. INDEX RETRIEVAL:                                                         │
│    • Queries pre-indexed Xapian / SQLite FTS5 index in Kiwix .zim archives  │
│    • Extracts top 3–5 candidate text chunks (~1,500 tokens)                 │
│                         │                                                   │
│                         ▼                                                   │
│ 3. CONTEXT ASSEMBLY:                                                        │
│    • Combines user query + extracted reference passages + strict grounding │
│                         │                                                   │
│                         ▼ (4.5 – 6.0 tokens/sec via ARM NEON SIMD)          │
│ 4. LOCAL SYNTHESIS (llama.cpp on CM4 Quad Cortex-A72):                      │
│    • Model: Qwen 2.5 3B Instruct or Llama 3.2 3B (Q4_K_M Quantization)     │
│    • Memory: 2.2 GB RAM footprint (leaves >5GB free on 8GB CM4)             │
│    • Synthesizes concise, actionable, numbered field steps                  │
│                         │                                                   │
│                         ▼                                                   │
│ 5. ZERO-POWER STATIC DISPLAY:                                               │
│    • Flushes answer to E-Ink display; consumes 0.000W while being read      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.1 Storage & Retrieval Performance
* **Index Storage:** The 100GB+ Kiwix `.zim` files reside on the **M.2 2230/2242 PCIe NVMe SSD** (wired to the CM4's PCIe Gen 2 x1 bus at 400+ MB/s).
* **Search Speed:** Pre-computed Xapian / SQLite full-text indices resolve multi-keyword queries in **under 45 milliseconds**.

### 5.2 Local LLM Resource Footprint (CM4 8GB LPDDR4)
* **Engine:** `llama.cpp` compiled with native ARMv8 NEON SIMD optimizations.
* **Model Selection:** **Qwen 2.5 3B Instruct** or **Llama 3.2 3B** (Q4_K_M quantization).
  * Model Weight Size: ~2.0 GB.
  * Active Inference RAM: ~2.4 GB (including 4K KV cache).
  * System Free Memory: > 5.0 GB remaining for Linux, Wayland, and user tasks.
  * Inference Throughput: **4.5 to 6.0 tokens per second**.
  * Battery Consumption: ~3.2W during 20 seconds of generation = **~0.018 Wh per query** (< 0.06% of the 32 Wh pack).
* **Zero-Hallucination Grounding:** The prompt template strictly constrains the model to cite only the retrieved excerpts. If an answer is not present in the local manuals, the model explicitly acknowledges the absence rather than guessing.

---

## 6. GPU Architecture & Silicon Capabilities (Broadcom VideoCore VI)

*Appended 2026-10-19 12:20 UTC in the Pi harness by antigravity/gemini-3.8-flash*

The Raspberry Pi CM4 integrates a dedicated **Broadcom VideoCore VI (V3D 4.2 @ 500 MHz)** 3D graphics and compute engine with open-source Linux kernel and userspace driver stacks:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 BROADCOM VIDEOCORE VI GPU SILICON PIPELINE                  │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ Graphics Standards    │ • OpenGL ES 3.1 & Vulkan 1.2 (Mesa v3d / v3dv)      │
│                       │ • Hardware direct DRM/KMS scanout with zero tearing │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ Dedicated Video ASIC  │ • 4Kp60 H.265 (HEVC) hardware video decoder         │
│                       │ • 1080p60 H.264 hardware video decoder              │
│                       │ • 1080p30 H.264 hardware video encoder (<2% CPU)    │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ SolarDeck Workloads   │ • Real-time GLSL Blue-Noise Dithering (<2.0ms frame)│
│                       │ • Vulkan compute acceleration for local AI / STT    │
│                       │ • Wayland Sway compositor GPU hardware page flip    │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

1. **Hardware-Accelerated Temporal Blue-Noise Dithering (`dither.glsl`):**
   * Electrophoretic displays physically cannot switch 24-bit RGB or 256-level grayscale at 30–60 FPS.
   * A custom GLSL fragment shader running on the VideoCore VI GPU dynamically maps 24-bit frames into 1-bit binary or 2-bit (4-level) dithered bitmaps in **under 2.0 milliseconds**, creating smooth optical gradients with near-zero CPU load.
2. **Vulkan Matrix Compute Acceleration (`llama.cpp` & `whisper.cpp`):**
   * Leveraging Mesa's native `v3dv` Vulkan driver, matrix multiplications and token embedding lookups can be partially offloaded from the Cortex-A72 cores to the GPU shaders, improving local STT transcription latency and conserving battery.
3. **Hardware Camera ISP & Outgoing Video Encoding:**
   * Incoming raw Bayer frames from the 12MP Sony IMX708 sensor pass through the Broadcom hardware Image Signal Processor (ISP) for lens shading correction, auto-white-balance, and hardware demosaicing.
   * Outgoing video feeds are encoded into H.264 1080p30 directly in silicon, enabling tactical streaming or reconnaissance recording without taxing the CPU cores.

---

## 8. Tactical Module Rejiggering: Core Tablet vs. USB-C "Hotpacks"

*Appended 2026-10-19 13:00 UTC in the Pi harness by antigravity/gemini-3.8-flash*

To achieve true physical reliability, zero-leakage battery efficiency, and foolproof field survivability, the system architecture rigorously divides hardware into **Core Onboard Subsystems** and **Modular USB-C Hotpacks**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 CORE TABLET vs. MODULAR USB-C HOTPACK ARCHITECTURE          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. THE CORE TABLET (Self-Contained Daily Driver & Survival Terminal)        │
│    • Brains: Broadcom CM4 (Linux) + RP2350B Co-Processor (12mW Supervisor)  │
│    • Display: 10.3" Kaleido 4 / Carta 1200 + Laminated Wacom EMR Digitizer  │
│    • Primary Mesh: Semtech SX1262 LoRa (Meshtastic 24/7 on RP2350 SPI)      │
│    • Security & Auth: 13.56 MHz NFC (ST25R3916 for YubiKey FIDO2 & Tap-Pair)│
│    • Inertial & Weather: 9-DOF IMU (BMI270/BMM350) + Bosch BMP390 Barometer │
│    • Acoustic Array: Dual Knowles MEMS Microphones (Whisper Voice-to-Text)  │
│    • Cellular & GNSS: Quectel EG25-G LTE + Qualcomm GNSS + eSIM / Nano-SIM  │
│    • Power: 8,000–10,000 mAh LiFePO4 (3.2V) + TI BQ25895 + Bezel Solar Strip│
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. THE EXPANSION INTERFACE: PURE USB-C PORT 2 (No Fragile Pogo Pins!)       │
│    • Mechanical Anchor: Rear MagSafe Magnetic Ring + 4x M2.5 Threaded Inserts│
│    • Electrical Connection: Recessed, low-profile right-angle USB-C male    │
│      mating to IP68-sealed USB-C Port 2 (High-Speed Host).                  │
│    • Advantage: Eliminates spring-loaded pogo pins that jam or corrode from │
│      beach sand, volcanic dust, or salt spray in tropical environments.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. THE 4 SPECIALIZED MODULAR USB-C HOTPACKS                                 │
│    • HOTPACK 1: DOOMSDAY SKY-SCAN & SIGINT (Passive Stealth Scanner)        │
│    • HOTPACK 2: TACTICAL DUAL-MESH & HF SHORTWAVE TRANSCEIVER (Active Comms)│
│    • HOTPACK 3: CBRN & SEARCH-AND-RESCUE ENVIRONMENTAL (Hazmat & Fire)     │
│    • HOTPACK 4: PRECISION RTK CENTIMETER SURVEY (1.4cm Land Surveying)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 8.1 Why We Descope the Flipper Zero Clone (Use the Real Flipper Zero)
* **The Trap:** Designing a custom backpack with a CC1101 Sub-GHz chip, 125 kHz RFID coil, and IR remote replicates hardware that already exists.
* **The Ponytail Reality:** The **Flipper Zero** is already a mature, battery-powered $169 multi-tool with extensive community firmware (Unleashed, Momentum).
* **The Integration:** Users mount their existing Flipper Zero directly to SolarDeck’s rear M2.5 inserts or MagSafe ring, connecting via a 10cm right-angle USB-C cable or Bluetooth 5.0. SolarDeck’s CM4 Linux runs `qflipper-cli` and `flipperzero-protobuf`, exposing full control on the 10.3" sunlight-readable screen without adding custom silicon.

---

### 8.2 Hotpack 1: Doomsday Sky-Scan & SIGINT (Passive All-Band Receiver)
* **Operational Doctrine:** 100% passive, zero-emission radio reconnaissance. Allows an operator to gather air, marine, weather, and satellite intelligence in a blackout without broadcasting a single milliwatt.
* **Silicon Architecture:**
  1. **RTL-SDR v4 Wideband Tuner (24 MHz – 1.766 GHz):** Built-in 0.5 PPM TCXO (temperature-compensated crystal oscillator) with upconverter direct sampling for High-Frequency (HF) coverage (500 kHz – 28 MHz).
  2. **Switched SAW Filter Bank & LNAs:**
     * 137 MHz SAW bandpass filter for crisp polar weather satellite reception.
     * 1090 MHz SAW bandpass filter for commercial/military ADS-B aircraft radar.
  3. **Dual Top RF Ports:**
     * `SMA Port 1 (HF 0.5–30 MHz)`: Connects to a long-wire antenna thrown over a tree or an active magnetic loop for international shortwave and AM emergency broadcasts.
     * `SMA Port 2 (VHF/UHF 30–1700 MHz)`: Connects to a wideband telescopic whip for aircraft, marine, and satellite scanning.
* **Field Intelligence Decoded on E-Ink:**
  * **Direct Weather Satellite Imagery:** Decodes live overhead infrared cloud/storm pictures from **NOAA 15/18/19 (APT)** and **Meteor-M2 (LRPT)** satellites via `satdump` with zero internet.
  * **Air Radar (`readsb` / `dump1090`):** Plots all commercial and military aircraft positions, altitudes, and squawk codes within 150 miles on offline vector maps.
  * **Marine AIS (`rtl-ais`):** Tracks commercial cargo ships, tankers, and coast guard cutters.
  * **Civil Emergency Audio:** Monitors continuous NOAA Weather Radio automated SAME emergency alerts (tornado, tsunami, wildfire).

---

### 8.3 Hotpack 2: Tactical Dual-Mesh & HF Transceiver (Active Off-Grid Comms)
* **Operational Doctrine:** Two-way encrypted long-distance communication when cellular networks and the global internet are completely destroyed.
* **Silicon Architecture:**
  1. **Second Semtech SX1262 LoRa Radio (with dedicated top SMA port):**
     * Dedicated to **MeshCore** or **Reticulum Network Stack (`rns`)**.
     * **Concurrent Dual-Mesh Operation:** Because this second transceiver has its own dedicated RF path and antenna, it eliminates the 3 dB signal loss and LNA burnout risk of passive splitters. SolarDeck listens and transmits on **both Meshtastic and MeshCore concurrently**, functioning as an autonomous cross-mesh bridge!
  2. **QRP 5W HF Shortwave Digital Transceiver (40m / 20m bands):**
     * Encodes and decodes **JS8Call** and **FT8** digital text messages over High Frequency.
     * Bounces RF energy off the ionosphere to send text messages **500 to 2,000 miles** across oceans or mountain ranges without satellites.
     * Terminated in a heavy-duty **BNC jack** for rapid connection to an end-fed random wire or dipole.
  3. **Hardware APRS / AX.25 TNC Audio Interface (3.5mm TRRS Smart Jack):**
     * A 3.5mm TRRS audio/PTT jack interfaces with any $30 analog handheld radio (Baofeng UV-5R, Yaesu, Kenwood).
     * Connects via an internal C-Media USB audio codec and optocoupled PTT transistor line.
     * Functions as a hardware AX.25 packet TNC (`direwolf`), APRS digital tracker, SSTV color image transceiver, and global Winlink emergency email portal without piercing the tablet unibody.
  4. **High-Power 940nm Infrared (IR) Blaster & Receiver Array:**
     * Features 4x high-output 940nm IR LEDs (120° flood cone) driven at 500mA pulses plus a Vishay TSOP75238 IR demodulator.
     * Operates with an offline LIRC library of 3,000+ appliance remotes (campervan MaxxFans, Dometic A/C units, Espar/Webasto heaters, TVs, cameras).
     * Enables **RF-silent optical line-of-sight data transfer** (115,200 baud serial) between two SolarDecks over a 50-meter clearing with **0.000 dBm radio signature**.

---

### 8.4 Hotpack 3: CBRN & Search-and-Rescue (SAR) Environmental Pack
* **Operational Doctrine:** Threat detection during radiological accidents, chemical leaks, wildfire evacuations, or post-disaster search-and-rescue.
* **Silicon Architecture:**
  1. **Solid-State Radiation Dosimeter (PocketGeiger Type 5 / BG51):**
     * Continuously logs gamma and beta radiation dose rates ($\mu\text{Sv/h}$).
     * Automatically plots real-time fallout decay curves on the E-Ink display and triggers audible piezo alarms on dangerous spikes.
  2. **Radiometric Thermal Camera (FLIR Lepton 3.5 or InfiRay P2):**
     * Long-wave infrared (8–14 µm) thermal sensor.
     * Sees through pitch-black darkness, dense fog, and thick wildfire smoke.
     * Locates lost human beings, hidden campfire embers, electrical panel hot spots, or building insulation leaks.
  3. **Photoacoustic Gas Sensor (Sensirion SCD41 + SGP40):**
     * Measures true CO2 concentration (400–5,000 ppm), volatile organic compounds (VOC index), and noxious gases.
     * Prevents asphyxiation in enclosed storm shelters, vans, or contaminated ruins.

---

### 8.5 Hotpack 4: Precision RTK Centimeter Survey Pack
* **Operational Doctrine:** Millimeter-to-centimeter precision surveying, property boundary verification, search-and-rescue grid tracking, and drone landing pad mapping.
* **Silicon Architecture:**
  1. **u-blox ZED-F9P Multi-Band RTK GNSS Engine:** Tracks carrier phases across L1, L2, and L5 frequencies concurrently across GPS, GLONASS, Galileo, and BeiDou.
  2. **Precision High-Gain Top TNC/SMA Port:** Mates to a multi-band helical antenna or carbon-fiber survey pole.
  3. **Real-World Precision:**
     * **1.4 cm Horizontal Accuracy:** When receiving RTCM differential corrections via NTRIP (cellular) or local LoRa base station.
     * **Sub-20 cm Worldwide Precision (Zero Internet):** Directly decodes **Galileo HAS (High Accuracy Service)** corrections broadcast from European satellites on the E6 band—delivering sub-foot precision anywhere on Earth with zero cellular connection.

---

### 8.6 The Hawaii Sun Problem: Why Solar Covers Are Descoped
* **The Thermal Ceiling:** In direct tropical midday sun (Hawaii, Arizona, Mexico), ambient temperatures hit +35°C to +42°C, and dark unibody surfaces bake to **over +70°C (+158°F)**.
* **Display Physics:** Electrophoretic microcapsules (E-Ink) undergo permanent fluid degradation and pigment sticking if operated above **+60°C**.
* **Battery Safety:** LiFePO4 cells must terminate charging at **+45°C to +50°C** to prevent internal gas generation and electrolyte breakdown.
* **The Detached Solar Workflow:**
  * Descope the integrated solar smart cover.
  * Pack a standard, lightweight folding 15W–28W USB-C solar panel (e.g. BigBlue / Anker with SunPower Maxeon cells).
  * Place the solar panel out in the scorching sun on a hot volcanic rock or vehicle roof.
  * Run a **3-meter high-visibility USB-C cable** into the shade of a tree, awning, or tent where SolarDeck and its LiFePO4 battery operate safely at ambient temperature.

---

### 8.7 Hotpack 5: 15g Thermal Night-Vision & Electrical Inspection Pack
* **Operational Doctrine:** Van electrical fire prevention (auditing fuse blocks, wire crimps, cracked solar panel bypass diodes), camp perimeter security in pitch darkness (150m human/wildlife heat detection), and building insulation heat leak mapping.
* **Silicon Architecture:**
  1. **Long-Wave Infrared (LWIR) Thermal Core:** Miniature **InfiRay Tiny1-C / P2 Pro** uncooled vanadium oxide (VOx) microbolometer (256 × 192 resolution, 12 µm pixel pitch, 25 Hz frame rate, spectral band 8–14 µm, NETD $<40\text{ mK}$).
  2. **Mounting & Interface:** Snaps to upper chassis MagSafe magnetic ring; connects via 5cm right-angle jumper to USB-C Port 2. Total weight: **15 grams**.
  3. **Display & GPU Acceleration:** Broadcom VideoCore VI hardware-accelerates 25 FPS thermal matrix interpolation and applies custom 16-shade e-ink blue-noise dithering (`dither.glsl`) or false-color palettes in $<2\text{ms}$.
  4. **Tactical Covertness:** Emits **0.000 lux** of visible light; allows passive thermal reconnaissance in complete darkness with the e-ink frontlight turned off.

---

### 8.8 Hotpack 6: 3GPP NTN Satellite Skylo Transceiver & Global SAR Protocol
* **Operational Doctrine:** Worldwide emergency SOS messaging, telemetry transmission, and life-saving rescue dispatch from anywhere on Earth (high oceans, polar caps, remote slot canyons) with zero cellular infrastructure or local mesh nodes.
* **Why Satellite Belongs in a Hotpack (Not Carrier Board):**
  1. **Antenna Geometry:** Satellite uplinks to 36,000 km geostationary orbit require an unobstructed upward-facing **Right-Hand Circularly Polarized (RHCP) ceramic patch antenna** tuned to S-band (~2.0 GHz) or L-band (~1.6 GHz). Internal chassis placement causes severe chassis absorption and detuning.
  2. **Certification Risk:** Direct-to-satellite modems require rigorous carrier lab certifications ($40,000+ FCC/CE/Skylo testing). Isolating this into a hotpack keeps the main carrier board agile and turnkey.
* **Silicon Architecture:**
  1. **Satellite Modem Engine:** **Quectel CC660D-LS** (or Sony Altair ALT1350 / MediaTek MT6825) supporting 3GPP Release 17 Non-Terrestrial Networks (IoT-NTN).
  2. **Top-Mounted RHCP Ceramic Patch:** 25×25×4mm high-gain circularly polarized antenna aimed directly at the sky.
  3. **Global SAR Routing:** Two-way encrypted 60-byte packets route directly through the **International Emergency Response Coordination Center (IERCC / Garmin Response)**, which immediately verifies the distress coordinates and dispatches local 911, Coast Guard, or regional air rescue.
* **Complementary 406 MHz Cospas-Sarsat Companion Protocol:**
  * For military-grade search-and-rescue, SolarDeck integrates with certified commercial PLBs (e.g. Ocean Signal rescueME PLB1, 116g, 7-year battery). SolarDeck reads the PLB diagnostic status over NFC and triggers automated digital coordinates via USB-C Hotpack 6 while the certified 5W transmitter pulses the international 406.037 MHz satellite payload.

---

### 8.9 Hotpack 7: Sub-Surface Acoustic & Perimeter Geophone Module (`solardeck-geophoned`)
* **Operational Doctrine:** 360-degree covert ground surveillance in zero-visibility conditions (dense fog, smoke, pitch black) with **zero RF emissions and zero optical signature**. Detects and classifies approaching vehicles, human footsteps, and wildlife by tracking Rayleigh seismic ground waves and acoustic transients.
* **Silicon & Transducer Architecture:**
  1. **Moving-Coil Electrodynamic Geophone:** Miniature **SM-24 / GS-11D** moving-coil geophone (4.5 Hz / 10 Hz natural resonance frequency, $28.8\text{ V/m/s}$ sensitivity, high-permeability neodymium magnet).
  2. **Direct Ground Coupling:** Includes a detachable 100mm threaded stainless-steel spike that screws into the Hotpack chassis and inserts into sub-surface soil, bypassing surface acoustic damping.
  3. **Ultra-Low-Noise Seismic Signal Chain:**
     * TI INA188 / AD8429 instrumentation amplifier ($1\text{ nV}/\sqrt{\text{Hz}}$ voltage noise).
     * TI ADS1282 / ADS1256 24-bit Delta-Sigma seismic ADC delivering **130 dB dynamic range**.
* **Seismic-Acoustic Multi-Modal Fusion:**
  * **Exact Radial Distance:** Compares the millisecond arrival delta ($\Delta t = t_{\text{air}} - t_{\text{ground}}$) between slow ground Rayleigh waves (250–500 m/s) and airborne sound (343 m/s) detected by the Knowles MEMS array.
  * **360° Azimuth Angle (Hodogram):** Orthogonal X/Y horizontal shear geophone coils compute the wave polarization ellipse to calculate exact cardinal bearing (0° to 360°).
* **TinyML Edge Wavelet Classifier:**
  * **Human Footstep:** 1.6–2.1 Hz cadence with 15–35 Hz heel-strike transients.
  * **Large Animals (Bear/Boar/Deer):** 3.2–5.0 Hz 4-beat trot/gallop cadence.
  * **Vehicles:** Continuous narrow-band engine shaft vibrations (20–40 Hz) and tire hum (60–120 Hz).
* **Tactical E-Ink Polar HUD:** Renders a 360-degree circular radar ring showing bearing, estimated distance, and target classification icons with 0.000W bi-stable persistence.

---

*Appended 2026-10-19 14:10 UTC in the Pi harness by antigravity/gemini-3.8-flash*

The following custom software utilities and daemons leverage SolarDeck's bi-stable E-Ink display, dual-brain architecture, tactical radios, and sensor array:

### 7.1 Tactical RF, Air Radar & Signals
1. **`solardeck-waterfall` (High-Contrast E-Ink RF Spectrum & Air Radar):**
   * Captures raw I/Q samples from the onboard RTL-SDR and CC1101 radios.
   * Renders a real-time RF waterfall using custom 1-bit Atkinson dithering optimized for high sunlight visibility.
   * Integrates with `dump1090-fa` to plot commercial and private aircraft ADS-B transponder positions, altitudes, and headings directly over an offline vector topographic map.
2. **`solardeck-recon` (Zero-Glow Wi-Fi & BLE Tactical RF Audit):**
   * Integrates with `kismet` or `bettercap` to passively map nearby Wi-Fi APs, client MAC addresses, and Bluetooth beacons along with Qualcomm GNSS coordinates.
   * **Zero-Glow Stealth Advantage:** Operates with the frontlight turned off (0.000 lux), remaining completely undetectable to outside observers at night while scanning.
3. **`solardeck-ham` (Off-Grid Global HF Text Messenger - JS8Call / FT8 / APRS):**
   * Interfaces with external QRP ham transceivers via USB audio or CAT control.
   * Encodes and decodes weak-signal digital text messages bounced off the ionosphere across continental distances using less than 5W of RF power.
   * Decodes 144.390 MHz VHF APRS packets, tracking local search-and-rescue teams, weather stations, and repeaters on the e-ink screen.

### 7.2 Acoustic, Solar & Inertial Field Navigation
4. **`solardeck-acoustic-compass` (Dual-Mic Acoustic Angle-of-Arrival Tracker):**
   * Utilizes the 65 mm Knowles dual-MEMS microphone array to compute the Time Difference of Arrival (TDoA) of sudden sharp transients (gunshots, distant engine revs, whistles, shouting).
   * Renders a 360-degree tactical compass HUD with an arrow pointing toward the bearing of the sound source.
5. **`solardeck-sundial` (Optical Solar Heading & Astronomical Compass):**
   * Samples micro-solar strip voltage via the RP2350 12-bit ADC alongside Qualcomm GNSS coordinates and DS3231 TCXO time.
   * Rotating the tablet until the micro-solar strip reaches peak voltage calculates **True Geographic North** geometrically from the sun's position, completely immune to magnetic vehicle distortion.
6. **`solardeck-survey` (BLE Laser Distance Room Sketcher & Clinometer):**
   * Connects via BLE to laser distance measurers (Bosch GLM, Leica DISTO) to automatically sketch real-time floor plans with Wacom EMR in CAD/SVG.
   * Uses the Bosch IMU as a high-precision digital clinometer for surveying slope grades, vehicle roll/pitch, and solar panel tilt optimization.

### 7.3 Maritime, UAV & Hardware Engineering
7. **`solardeck-marine` (Waterproof Salt-Spray E-Ink Marine Chartplotter):**
   * Runs **OpenCPN** and **Signal K** connected to NMEA 2000 / NMEA 0183 boat instrument buses and AIS ship receivers.
   * Delivers 0% glare under blinding open-ocean sunlight.
   * Hardware water-lock isolates capacitive touch against splashing waves while allowing the Wacom EMR stylus to plot course bearings; draws only 1.2W vs 25W for standard marine MFDs.
8. **`solardeck-gcs` (Sunlight UAV & Weather Balloon Ground Control Station):**
   * Runs **QGroundControl** over 915 MHz LoRa or telemetry radios using MAVLink.
   * Serves as an outdoor daylight ground station for tracking autonomous drones, search-and-rescue quadcopters, and high-altitude meteorological balloons.
9. **`solardeck-bench` (Outdoor Logic Analyzer, Oscilloscope & Bus Pirate):**
   * Pairs with open-source USB logic analyzers via `sigrok` and `PulseView` on USB-C Port 2.
   * Turns SolarDeck into an outdoor 24 MHz 8-channel logic analyzer and oscilloscope for probing SPI/I2C/UART lines on field hardware in direct sun.

### 7.4 Sovereign Writing, Focus & Cryptography
10. **`solardeck-zen` (Sovereign Prose Typewriter & S2idle Power Gating):**
    * A distraction-free markdown environment running on the 20ms 1-bit typing waveform.
    * Automatically drops into S2idle (15 mW) between keystroke pauses and wakes in <300ms, providing **35 to 45 hours of continuous active writing** outdoors.
11. **`solardeck-slate` (Low-Latency Wacom Vector Field Notebook):**
    * Direct-to-DRM canvas hooking into Wacom EMR (<18ms latency) for sketching circuit schematics, physics math, or tactical maps, with 1-click export to vector SVG or Obsidian.
12. **`solardeck-courier` (Autonomous Bi-Stable LoRa Pager & Bulletin Board):**
    * While Linux is unpowered, the RP2350 receives Meshtastic messages over LoRa at 12 mW and prints them to the E-Ink screen. Because E-Ink is bi-stable, messages remain legibly stamped on the display forever without consuming battery.
13. **`solardeck-airgap-tx` (Optical QR Fountain Code Bridge):**
    * Airgapped data exfiltration/ingestion using animated QR codes (`txqr`) at 50–100 KB/s through the rear 12MP camera and 10.3" screen with zero radio waves.
14. **`solardeck-vault-totp` (Bi-Stable Airgapped 2FA & Password Vault):**
    * Generates TOTP two-factor codes and unlocks KeePassXC vaults securely on an airgapped device.
    * Displays the 6-digit code on the zero-power e-ink screen where it can be read without casting a glow in dark rooms.
15. **`solardeck-drone` (Microclimate Generative Ambient Sound Synthesizer):**
    * Runs a lightweight Pure Data (Pd) or SuperCollider sound engine.
    * Maps barometric pressure drops and solar cloud shadow variations into soothing, real-time generative ambient soundscapes through the micro-speaker or 3.5mm jack.
16. **`solardeck-bioacoustics` (Ultrasonic Bat & Pest Spectrogram Detector):**
    * Samples high-frequency acoustic data from the Knowles MEMS array up to 48–96 kHz to heterodyne and visualize bat echolocation and pest activity on an e-paper spectrogram.
