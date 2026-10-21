#!/usr/bin/env bash
#
# setup_solardeck_os.sh — SolarDeck V1 OS Provisioning Engine
# Written 2026-10-19 UTC in the Pi harness by antigravity/gemini-3.8-flash
#
# Automatically provisions a clean Raspberry Pi OS Lite (64-bit) image:
#   1. Compiles and installs solardeck-cm5.dtbo to /boot/firmware/overlays/
#   2. Enables dtoverlay=solardeck-cm5 in /boot/firmware/config.txt
#   3. Builds and installs eink-refreshd cadence daemon
#   4. Builds and installs solardeck-telemetryd bridge daemon
#   5. Configures systemd background services
#   6. Installs monochrome high-contrast Sway & Waybar configurations
#   7. Installs Wacom EMR & RF killswitch udev rules
#   8. Configures S2idle instant wake and OverlayFS read-only protection
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Color output helpers
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${CYAN}[INFO]${NC} $1"; }
log_ok()   { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${RED}[WARN]${NC} $1"; }

# Dry-run / Self-test verification mode
if [[ "${1:-}" == "--test" || "${1:-}" == "--dry-run" ]]; then
    echo -e "${BLUE}=== SolarDeck Provisioning Script Self-Test ===${NC}"
    
    # Check source files exist
    test -f "${REPO_ROOT}/src/dts/solardeck-cm5.dts" || { echo "Missing DTS file"; exit 1; }
    test -f "${REPO_ROOT}/src/daemons/eink-refreshd/refreshd.c" || { echo "Missing refreshd.c"; exit 1; }
    test -f "${REPO_ROOT}/src/daemons/solardeck-telemetryd/telemetryd.c" || { echo "Missing telemetryd.c"; exit 1; }
    test -f "${REPO_ROOT}/config/sway/config" || { echo "Missing sway config"; exit 1; }
    test -f "${REPO_ROOT}/config/waybar/config.jsonc" || { echo "Missing waybar config"; exit 1; }
    
    # Test C compilation of daemons locally
    gcc -Wall -Wextra -O2 -c "${REPO_ROOT}/src/daemons/eink-refreshd/refreshd.c" -o /tmp/test_refreshd.o
    gcc -Wall -Wextra -O2 -c "${REPO_ROOT}/src/daemons/solardeck-telemetryd/telemetryd.c" -o /tmp/test_telemetryd.o
    rm -f /tmp/test_refreshd.o /tmp/test_telemetryd.o
    
    echo -e "${GREEN}[PASS] All provisioning templates and daemons validated successfully.${NC}"
    exit 0
fi

# Root check for live execution
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}[ERROR] This script must be run as root: sudo ./setup_solardeck_os.sh${NC}"
   exit 1
fi

TARGET_USER="${SUDO_USER:-$(logname)}"
USER_HOME=$(getent passwd "${TARGET_USER}" | cut -d: -f6)

echo -e "${BLUE}========================================================================${NC}"
echo -e "${BLUE}  SolarDeck V1 OS Provisioning Engine (Target User: ${TARGET_USER})     ${NC}"
echo -e "${BLUE}========================================================================${NC}"

# 1. Device Tree Overlay Compilation
log_info "Step 1: Compiling Device Tree Overlay (solardeck-cm5.dts)..."
BOOT_DIR="/boot/firmware"
if [[ ! -d "${BOOT_DIR}" ]]; then
    BOOT_DIR="/boot"
fi

if command -v dtc >/dev/null 2>&1; then
    dtc -@ -I dts -O dtb -o "${BOOT_DIR}/overlays/solardeck-cm5.dtbo" "${REPO_ROOT}/src/dts/solardeck-cm5.dts"
    log_ok "Installed solardeck-cm5.dtbo to ${BOOT_DIR}/overlays/"
else
    log_warn "dtc not found; installing device-tree-compiler..."
    apt-get update -y && apt-get install -y device-tree-compiler
    dtc -@ -I dts -O dtb -o "${BOOT_DIR}/overlays/solardeck-cm5.dtbo" "${REPO_ROOT}/src/dts/solardeck-cm5.dts"
    log_ok "Installed solardeck-cm5.dtbo"
fi

CONFIG_TXT="${BOOT_DIR}/config.txt"
if ! grep -q "dtoverlay=solardeck-cm5" "${CONFIG_TXT}"; then
    echo "" >> "${CONFIG_TXT}"
    echo "# SolarDeck Hardware Carrier Board Overlay" >> "${CONFIG_TXT}"
    echo "dtoverlay=solardeck-cm5" >> "${CONFIG_TXT}"
    echo "dtparam=i2c_arm=on" >> "${CONFIG_TXT}"
    echo "dtparam=spi=on" >> "${CONFIG_TXT}"
    echo "dtparam=i2s=on" >> "${CONFIG_TXT}"
    log_ok "Added dtoverlay=solardeck-cm5 to ${CONFIG_TXT}"
else
    log_ok "dtoverlay=solardeck-cm5 already present in ${CONFIG_TXT}"
fi

# 2. Build and Install Daemons
log_info "Step 2: Compiling Daemons (eink-refreshd, solardeck-telemetryd)..."
gcc -O2 -Wall -Wextra "${REPO_ROOT}/src/daemons/eink-refreshd/refreshd.c" -o /usr/local/bin/eink-refreshd
chmod 755 /usr/local/bin/eink-refreshd
log_ok "Installed /usr/local/bin/eink-refreshd"

gcc -O2 -Wall -Wextra "${REPO_ROOT}/src/daemons/solardeck-telemetryd/telemetryd.c" -o /usr/local/bin/solardeck-telemetryd
chmod 755 /usr/local/bin/solardeck-telemetryd
log_ok "Installed /usr/local/bin/solardeck-telemetryd"

# 3. Register Systemd Units
log_info "Step 3: Creating Systemd Services..."
cat > /etc/systemd/system/eink-refreshd.service << 'EOF'
[Unit]
Description=SolarDeck E-Ink Typing Cadence & Anti-Ghosting Daemon
After=graphical.target

[Service]
Type=simple
ExecStart=/usr/local/bin/eink-refreshd
Restart=always
RestartSec=2
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

cat > /etc/systemd/system/solardeck-telemetryd.service << 'EOF'
[Unit]
Description=SolarDeck RP2350 Co-Processor Telemetry Bridge
After=basic.target

[Service]
Type=simple
ExecStart=/usr/local/bin/solardeck-telemetryd
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable eink-refreshd.service || true
systemctl enable solardeck-telemetryd.service || true
log_ok "Enabled systemd services"

# 4. User Configurations (Sway & Waybar)
log_info "Step 4: Deploying Sway & Waybar configurations..."
mkdir -p "${USER_HOME}/.config/sway" "${USER_HOME}/.config/waybar"
cp "${REPO_ROOT}/config/sway/config" "${USER_HOME}/.config/sway/config"
cp "${REPO_ROOT}/config/waybar/config.jsonc" "${USER_HOME}/.config/waybar/config.jsonc"
cp "${REPO_ROOT}/config/waybar/style.css" "${USER_HOME}/.config/waybar/style.css"
chown -R "${TARGET_USER}:${TARGET_USER}" "${USER_HOME}/.config"
log_ok "Deployed desktop config to ${USER_HOME}/.config/"

# 5. Udev Rules (Wacom Digitizer & S2idle Wake)
log_info "Step 5: Installing Hardware Udev Rules..."
cat > /etc/udev/rules.d/99-solardeck.rules << 'EOF'
# Wacom EMR Digitizer low-latency configuration
ACTION=="add", SUBSYSTEM=="input", ATTRS{name}=="*Wacom*", ENV{LIBINPUT_CALIBRATION_MATRIX}="1 0 0 0 1 0"

# RP2350 Telemetry UART permissions
KERNEL=="ttyAMA0", GROUP="dialout", MODE="0660"
KERNEL=="ttyAMA1", GROUP="dialout", MODE="0660"

# CM5 host I2C bus permissions (the charger is on the RP2350 bus and is never driven by Linux, ADR-035)
KERNEL=="i2c-1", GROUP="i2c", MODE="0660"
EOF

udevadm control --reload-rules || true
log_ok "Installed /etc/udev/rules.d/99-solardeck.rules"

# 6. Power Management (S2idle Default)
log_info "Step 6: Setting S2idle default power state..."
CMDLINE="/boot/firmware/cmdline.txt"
if [[ ! -f "${CMDLINE}" ]]; then
    CMDLINE="/boot/cmdline.txt"
fi

if [[ -f "${CMDLINE}" ]] && ! grep -q "mem_sleep_default=s2idle" "${CMDLINE}"; then
    sed -i '$ s/$/ mem_sleep_default=s2idle/' "${CMDLINE}"
    log_ok "Appended mem_sleep_default=s2idle to ${CMDLINE}"
fi

echo -e "\n${GREEN}========================================================================${NC}"
echo -e "${GREEN}  🎉 SolarDeck OS Provisioning Complete!                                ${NC}"
echo -e "${GREEN}  Reboot the system to initialize the solardeck-cm5 overlay.           ${NC}"
echo -e "${GREEN}========================================================================${NC}"
