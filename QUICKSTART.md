# 🚀 QUICK START GUIDE

**Get the Nexus Barcode Scanner running in 5 minutes!**

---

## ⚡ Fast Installation (Raspberry Pi)

```bash
# 1. Navigate to project directory
cd ~/barcode_scanner

# 2. Make install script executable
chmod +x install.sh

# 3. Run installation
sudo ./install.sh

# 4. Test run
python3 scanner_main.py
```

---

## 🎯 First Run

1. **Register Reference Barcode**
   - Click "▶ REGISTER" button
   - Scan or wait for simulated barcode
   - Reference displays on screen

2. **Start Scanning**
   - Click "▶ START SCAN" button
   - Watch real-time results on chart
   - See statistics update live

3. **Exit**
   - Press ESC key
   - Or close window normally

---

## ⚙️ Basic Configuration

Edit `config/config.ini`:

### For Production
```ini
[Scanner]
simulate_camera = false

[Display]
fullscreen = true
```

### For Testing
```ini
[Scanner]
simulate_camera = true

[Display]
fullscreen = false
```

---

## 🔄 Auto-Start on Boot

```bash
# Enable service
sudo systemctl enable nexus-scanner.service

# Start now
sudo systemctl start nexus-scanner.service

# Check if running
sudo systemctl status nexus-scanner.service
```

---

## 📝 Check Logs

```bash
# Application logs
tail -f logs/scanner.log

# System logs (if running as service)
journalctl -u nexus-scanner.service -f

# Scan results
cat data/scan_results.txt
```

---

## 🛠️ Common Commands

```bash
# Run manually
python3 scanner_main.py

# Or use installed command
nexus-scanner

# Stop service
sudo systemctl stop nexus-scanner.service

# Restart service
sudo systemctl restart nexus-scanner.service

# Disable auto-start
sudo systemctl disable nexus-scanner.service
```

---

## ❓ Troubleshooting

### App won't start?
```bash
# Check Python
python3 --version

# Check config file
cat config/config.ini

# View recent logs
tail -n 50 logs/scanner.log
```

### Display issues?
```bash
# Check screen resolution
xrandr

# Update config.ini to match your screen
nano config/config.ini
```

### Permission errors?
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/barcode_scanner

# Ensure directories exist
mkdir -p logs data config
```

---

## 🎨 Keyboard Shortcuts

- **ESC** - Exit application
- **F11** - Toggle fullscreen

---

## 📊 Understanding the Interface

### Top Bar
- **◢ NEXUS SCAN** - Application title
- **●  Status** - System status with pulse indicator
- **SESSION timer** - Current session duration

### Main Area
- **Left Panel:**
  - Reference barcode display
  - Recent scans chart with metrics
  
- **Right Panel:**
  - Total scans count
  - Match count (green)
  - Error count (red)
  - Last scan result

### Bottom
- **▶ REGISTER** - Register reference barcode
- **▶ START SCAN** - Begin/stop scanning
- **▸ ACTIVITY** - Live activity log

### Chart Metrics
- **SUCCESS RATE** - Percentage of matches
- **✓ Count** - Number of matches
- **✗ Count** - Number of errors
- **TREND** - ↗ improving, → stable, ↘ declining

---

## 🎯 Production Checklist

Before deploying:

- [ ] Test scanner with real barcodes
- [ ] Set `simulate_camera = false`
- [ ] Enable `fullscreen = true`
- [ ] Test auto-start functionality
- [ ] Configure log rotation
- [ ] Document the reference barcode
- [ ] Train operators

---

## 📞 Need More Help?

See full documentation: **[README.md](README.md)**

---

**Ready to scan! 🎉**

