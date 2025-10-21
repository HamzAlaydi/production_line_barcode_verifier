#!/bin/bash
#
# Nexus Barcode Scanner - Installation Script
# Run with: sudo ./install.sh
#

set -e  # Exit on error

echo "=========================================="
echo "  NEXUS BARCODE SCANNER - Installation"
echo "=========================================="
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: Please run as root (use sudo)"
    exit 1
fi

# Get the actual user (not root)
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER=$SUDO_USER
else
    ACTUAL_USER=$(whoami)
fi

# Get installation directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Installation directory: $INSTALL_DIR"
echo "User: $ACTUAL_USER"
echo

# Create directories
echo "[1/6] Creating directories..."
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/config"

# Fix permissions
chown -R $ACTUAL_USER:$ACTUAL_USER "$INSTALL_DIR"
echo "✓ Directories created"
echo

# Check Python version
echo "[2/6] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Install with: sudo apt-get install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python $PYTHON_VERSION found"
echo

# Install dependencies (if requirements.txt has any)
echo "[3/6] Installing dependencies..."
if command -v pip3 &> /dev/null; then
    sudo -u $ACTUAL_USER pip3 install --user -r "$INSTALL_DIR/requirements.txt" || true
    echo "✓ Dependencies installed"
else
    echo "⚠ pip3 not found, skipping dependency installation"
    echo "  (Standard library only, no external dependencies needed)"
fi
echo

# Create systemd service
echo "[4/6] Installing systemd service..."
cat > /etc/systemd/system/nexus-scanner.service << EOF
[Unit]
Description=Nexus Barcode Scanner
After=graphical.target

[Service]
Type=simple
User=$ACTUAL_USER
WorkingDirectory=$INSTALL_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$ACTUAL_USER/.Xauthority"
ExecStart=/usr/bin/python3 $INSTALL_DIR/scanner_main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=graphical.target
EOF

systemctl daemon-reload
echo "✓ Systemd service installed"
echo

# Create command alias
echo "[5/6] Creating command alias..."
cat > /usr/local/bin/nexus-scanner << EOF
#!/bin/bash
cd "$INSTALL_DIR"
python3 scanner_main.py "\$@"
EOF

chmod +x /usr/local/bin/nexus-scanner
echo "✓ Command 'nexus-scanner' installed"
echo

# Verify configuration
echo "[6/6] Verifying configuration..."
if [ ! -f "$INSTALL_DIR/config/config.ini" ]; then
    echo "ERROR: config/config.ini not found!"
    exit 1
fi
echo "✓ Configuration verified"
echo

# Installation complete
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "1. Test the scanner:"
echo "   python3 $INSTALL_DIR/scanner_main.py"
echo "   OR"
echo "   nexus-scanner"
echo
echo "2. Edit configuration (if needed):"
echo "   nano $INSTALL_DIR/config/config.ini"
echo
echo "3. Enable auto-start on boot:"
echo "   sudo systemctl enable nexus-scanner.service"
echo
echo "4. Start the service:"
echo "   sudo systemctl start nexus-scanner.service"
echo
echo "5. Check service status:"
echo "   sudo systemctl status nexus-scanner.service"
echo
echo "6. View logs:"
echo "   tail -f $INSTALL_DIR/logs/scanner.log"
echo "   OR"
echo "   journalctl -u nexus-scanner.service -f"
echo
echo "=========================================="
echo "For more information, see README.md"
echo "=========================================="

