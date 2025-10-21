# ◢ NEXUS BARCODE SCANNER

**Production-ready barcode scanner with futuristic GUI for Raspberry Pi 5**

A professional-grade barcode scanning system featuring a modern, animated touchscreen interface optimized for 5-inch 800x480 displays. Designed for industrial production lines with Tesla/SpaceX-inspired aesthetics.

---

## ✨ Features

### 🎨 Futuristic GUI
- **Cyber-industrial design** with neon accents and dark theme
- **Animated components** with smooth transitions and glow effects
- **Real-time metrics chart** showing scan history and trends
- **Touch-optimized** interface for 5-inch displays
- **Visual feedback** with color-coded status and flash effects

### 📊 Analytics & Monitoring
- Live statistics (total scans, matches, errors)
- Success rate calculation with color-coded indicators
- Recent scan history chart (last 15 scans)
- Trend analysis (improving/declining/stable)
- Session timer and logging

### 🔧 Production Features
- **Modular architecture** with clean separation of concerns
- **Comprehensive logging** with rotation
- **Configuration file** for easy customization
- **Error handling** and recovery
- **Auto-start support** via systemd
- **Simulation mode** for testing without hardware

---

## 📋 Requirements

### Hardware
- Raspberry Pi 5 (or 4/3 with compatible OS)
- 5-inch touchscreen (800x480 recommended)
- Barcode scanner (camera or USB scanner)
- Optional: GPIO button and LED for physical controls

### Software
- **Python 3.7+**
- **Raspberry Pi OS** (or compatible Linux distribution)
- **Tkinter** (usually pre-installed)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or copy the project to your Raspberry Pi
cd ~/
git clone <your-repo> barcode_scanner
cd barcode_scanner

# Make installation script executable
chmod +x install.sh

# Run installation script
sudo ./install.sh
```

### 2. Configuration

Edit `config/config.ini` to customize settings:

```ini
[Scanner]
output_file = data/scan_results.txt
scan_interval = 1.0
simulate_camera = true  # Set to false for production

[Display]
screen_width = 800
screen_height = 480
fullscreen = false  # Set to true for production

[Logging]
log_level = INFO
```

### 3. Run the Scanner

```bash
# Test mode
python3 scanner_main.py

# Or use the installed command
nexus-scanner
```

### 4. Production Deployment

```bash
# Enable auto-start on boot
sudo systemctl enable nexus-scanner.service

# Start the service
sudo systemctl start nexus-scanner.service

# Check status
sudo systemctl status nexus-scanner.service

# View logs
journalctl -u nexus-scanner.service -f
```

---

## 📁 Project Structure

```
barcode_scanner/
├── config/
│   └── config.ini          # Configuration file
├── src/
│   ├── __init__.py         # Package initialization
│   ├── utils.py            # Utilities and config loader
│   ├── scanner.py          # Core scanning logic
│   └── gui.py              # GUI implementation
├── logs/
│   └── scanner.log         # Application logs
├── data/
│   └── scan_results.txt    # Scan results output
├── scanner_main.py         # Main entry point
├── requirements.txt        # Python dependencies
├── install.sh              # Installation script
├── nexus-scanner.service   # Systemd service file
└── README.md               # This file
```

---

## 🎮 Usage

### Basic Operation

1. **Start the application**
   - Click "REGISTER" button
   - Scan reference barcode
   - Reference will be displayed on screen

2. **Begin scanning**
   - Click "START SCAN" button
   - Scans will be compared to reference automatically
   - Results shown in real-time on chart and statistics

3. **Monitor performance**
   - View success rate and trend indicators
   - Check recent scan history chart
   - Review activity log

### Keyboard Shortcuts

- **ESC** - Exit application
- **F11** - Toggle fullscreen mode

---

## ⚙️ Configuration Options

### Scanner Settings

```ini
[Scanner]
output_file = data/scan_results.txt  # Where to save results
scan_interval = 1.0                  # Seconds between scans
simulate_camera = true               # Use simulation mode
max_chart_scans = 15                 # Max scans in chart
```

### Display Settings

```ini
[Display]
screen_width = 800          # Screen width in pixels
screen_height = 480         # Screen height in pixels
fullscreen = false          # Start in fullscreen mode
```

### Logging Settings

```ini
[Logging]
log_file = logs/scanner.log  # Log file location
log_level = INFO             # DEBUG, INFO, WARNING, ERROR, CRITICAL
max_log_size = 10            # Max size in MB before rotation
backup_count = 3             # Number of backup logs to keep
```

### Theme Customization

All colors can be customized in the `[Theme]` section of `config.ini`.

---

## 🔍 Troubleshooting

### Application Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.7+

# Verify configuration
cat config/config.ini

# Check logs
tail -f logs/scanner.log
```

### Display Issues

```bash
# Test display resolution
xrandr

# Update config.ini with correct resolution
[Display]
screen_width = YOUR_WIDTH
screen_height = YOUR_HEIGHT
```

### Service Not Starting

```bash
# Check service status
sudo systemctl status nexus-scanner.service

# View detailed logs
journalctl -u nexus-scanner.service -n 50

# Restart service
sudo systemctl restart nexus-scanner.service
```

### Permission Issues

```bash
# Ensure proper ownership
sudo chown -R $USER:$USER ~/barcode_scanner

# Make sure directories exist
mkdir -p logs data config
```

---

## 🔧 Development

### Running in Development Mode

```bash
# Enable simulation mode in config.ini
simulate_camera = true

# Run with debug logging
# Edit config.ini:
log_level = DEBUG

# Run application
python3 scanner_main.py
```

### Adding Real Camera Support

Uncomment in `requirements.txt`:
```
opencv-python>=4.5.0
pyzbar>=0.1.9
```

Then implement camera scanning in `src/scanner.py`:
```python
def scan_barcode(self):
    if not self.simulate:
        # Add your camera scanning code here
        # Example: Use opencv + pyzbar
        pass
```

---

## 📝 Logging

Logs are written to `logs/scanner.log` with automatic rotation.

### Log Levels
- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages
- **WARNING** - Warning messages
- **ERROR** - Error messages
- **CRITICAL** - Critical errors

### View Logs

```bash
# Real-time log viewing
tail -f logs/scanner.log

# View last 100 lines
tail -n 100 logs/scanner.log

# View with systemd
journalctl -u nexus-scanner.service -f
```

---

## 🎨 Customization

### Changing Colors

Edit `config/config.ini` under `[Theme]` section:

```ini
[Theme]
bg_primary = #0a0e14      # Main background
accent_cyan = #00d9ff      # Primary accent
accent_lime = #39ff14      # Success color
accent_red = #ff3366       # Error color
```

### Changing Fonts

Edit `src/utils.py` in the `Theme` class:

```python
self.font_title = ('Segoe UI', 18, 'bold')
self.font_stat = ('Segoe UI', 24, 'bold')
```

---

## 🤝 Production Deployment Checklist

- [ ] Update `config.ini` with production settings
- [ ] Set `simulate_camera = false`
- [ ] Set `fullscreen = true`
- [ ] Test all scanning functionality
- [ ] Enable systemd service
- [ ] Configure auto-start on boot
- [ ] Set up log monitoring
- [ ] Document backup procedures
- [ ] Train operators on usage

---

## 📊 Output Files

### Scan Results (`data/scan_results.txt`)

```
========================================================
Session started: 2025-01-20 10:30:15
Mode: Production
========================================================
REFERENCE REGISTERED: 123456789
========================================================
SCANNING STARTED - Reference: 123456789
========================================================
[2025-01-20 10:30:20] OK: 123456789
[2025-01-20 10:30:22] ERROR: 987654321
[2025-01-20 10:30:25] OK: 123456789
```

---

## 🛡️ Safety & Reliability

- **Error recovery** - Application handles errors gracefully
- **Log rotation** - Prevents disk space issues
- **Auto-restart** - Systemd restarts on crashes
- **Configuration validation** - Validates settings on startup
- **Graceful shutdown** - Saves data before exit

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/scanner.log`
2. Review configuration in `config/config.ini`
3. Consult this README
4. Check system journal: `journalctl -u nexus-scanner.service`

---

## 📄 License

Production-ready code for internal use.

---

## 🔮 Future Enhancements

Potential additions:
- Database integration
- Network monitoring/remote access
- Multi-camera support
- Advanced analytics dashboard
- Export to CSV/Excel
- Integration with ERP systems
- Sound notifications
- Email/SMS alerts

---

**Built with ❤️ for Production Excellence**

