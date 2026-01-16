# Custom Display Information - Quick Start

**Display:** 284×76 pixels touchscreen on GL-BE3600

---

## 🚀 Quick Install

```bash
cd ~/M-Claude/Claude-Slate/
./install_custom_display.sh
```

**What it does:**
- Installs 5 monitoring scripts
- Creates auto-updating dashboard
- Sets up web interface
- Updates every minute automatically

---

## 📊 Information Available

### Network Statistics
- ✓ WAN IP address
- ✓ Download/Upload traffic (total MB)
- ✓ WiFi clients (5GHz + 2.4GHz count)
- ✓ Connected device count

### System Health
- ✓ Uptime
- ✓ CPU load
- ✓ Memory usage (%)
- ✓ Temperature (°C)
- ✓ Storage usage (%)

### Security Status
- ✓ VPN status (Mullvad WireGuard)
- ✓ Blocky DNS status
- ✓ Firewall status
- ✓ VPN traffic stats

### Connected Devices
- ✓ Total device count
- ✓ Top 5 device names
- ✓ IP addresses

---

## 🌐 How to View

### Method 1: Web Browser (Recommended)

**Open:** http://192.168.8.1/dashboard.html

- Auto-refreshes every 10 seconds
- Works on phone, tablet, laptop
- Clean terminal-style interface
- Manual refresh button

### Method 2: SSH Terminal

```bash
ssh root@192.168.8.1 "cat /tmp/custom_dashboard.txt"
```

### Method 3: Continuous Monitor

```bash
ssh root@192.168.8.1
watch -n 5 cat /tmp/custom_dashboard.txt
```

---

## 📱 Example Dashboard Output

```
╔════════════════════════════════════════╗
║   GL-BE3600 Status Dashboard           ║
║   2026-01-10 19:30:45                  ║
╚════════════════════════════════════════╝

Network Statistics
==================
WAN IP: 192.168.1.38
Download: 1234.5 MB
Upload: 567.8 MB
WiFi 5GHz: 3 clients
WiFi 2.4GHz: 8 clients
Total: 11 clients

System Health
=============
Uptime: 6:15
Load: 0.45
Memory: 35%
Temp: 45.2°C
Storage: 1%

Security Status
===============
VPN: ✓ Connected
Blocky: ✓ Running
Firewall: ✓ Active

Connected Devices
=================
Total: 11

  • pixel (192.168.8.51)
  • macbook-wifi (192.168.8.52)
  • legion-wifi (192.168.8.53)
  • zimaboard (192.168.8.21)
  • ESP32-01 (192.168.8.151)
```

---

## 🛠️ Customization

### Add More Information

**Edit any script:**

```bash
ssh root@192.168.8.1
vi /etc/gl_screen/scripts/network_stats.sh
# Add your custom data
```

### Change Update Frequency

```bash
ssh root@192.168.8.1
crontab -e
# Change: * * * * *  (every minute)
# To:     */5 * * * * (every 5 minutes)
```

### Add Custom Sections

```bash
ssh root@192.168.8.1

# Create new monitoring script
cat > /etc/gl_screen/scripts/my_custom.sh << 'EOF'
#!/bin/sh
# Your custom monitoring here
cat > /tmp/my_custom.txt << EOD
Custom Section
==============
Your data here
EOD
EOF

chmod +x /etc/gl_screen/scripts/my_custom.sh

# Add to dashboard
vi /etc/gl_screen/scripts/custom_dashboard.sh
# Add: /etc/gl_screen/scripts/my_custom.sh
# Add: cat /tmp/my_custom.txt >> /tmp/custom_dashboard.txt
```

---

## 💡 Custom Information Ideas

### What You Could Add:

**Network:**
- Internet speed test results
- Starlink signal quality
- Bandwidth graphs (daily/weekly)
- DNS query counts (from Blocky)
- Top blocked domains

**Security:**
- Failed login attempts
- Firewall block counts
- VPN reconnection count
- DNS leak test results

**System:**
- Service uptime stats
- Storage I/O stats
- Network interface errors
- Kernel messages

**Custom:**
- Weather (via API)
- Calendar events
- To-do list
- Custom alerts
- Cryptocurrency prices
- Stock prices

---

## 📋 Installed Files

| File | Purpose |
|------|---------|
| `/etc/gl_screen/scripts/network_stats.sh` | Network monitoring |
| `/etc/gl_screen/scripts/system_health.sh` | CPU/Memory/Temp |
| `/etc/gl_screen/scripts/security_status.sh` | VPN/Blocky/FW |
| `/etc/gl_screen/scripts/device_list.sh` | Connected devices |
| `/etc/gl_screen/scripts/custom_dashboard.sh` | Main dashboard |
| `/www/dashboard.html` | Web interface |
| `/www/cgi-bin/dashboard_data` | Web API |
| `/tmp/custom_dashboard.txt` | Current dashboard |

---

## 🔧 Troubleshooting

### Dashboard not updating?

```bash
ssh root@192.168.8.1

# Check cron
cat /etc/crontabs/root | grep dashboard

# Manually run
/etc/gl_screen/scripts/custom_dashboard.sh

# Check output
cat /tmp/custom_dashboard.txt
```

### Web page not loading?

```bash
# Check if file exists
ssh root@192.168.8.1 "ls -la /www/dashboard.html"

# Check uhttpd
ssh root@192.168.8.1 "ps | grep uhttpd"

# Restart web server
ssh root@192.168.8.1 "/etc/init.d/uhttpd restart"
```

### Missing data?

```bash
# Test individual scripts
ssh root@192.168.8.1 "/etc/gl_screen/scripts/network_stats.sh && cat /tmp/network_stats.txt"
```

---

## 🎨 Advanced: Custom Display Themes

### Dark Green Matrix Theme (Default)

Already applied in web interface.

### Blue Terminal Theme

Edit `/www/dashboard.html`:
```css
body { color: #00ffff; }
h1 { color: #00ffff; border-bottom: 2px solid #00ffff; }
```

### Amber Retro Theme

Edit `/www/dashboard.html`:
```css
body { color: #ffb000; }
h1 { color: #ffb000; border-bottom: 2px solid #ffb000; }
```

---

## 📖 Related Documentation

- **Full Guide:** `custom_display_guide.md`
- **Router Optimization:** `OPTIMIZATION_SUMMARY.md`
- **Network Plan:** `network_optimization_plan.md`

---

## 🤔 Need Help?

### Common Questions:

**Q: Can the physical touchscreen show this data?**
A: The GL.iNet touchscreen uses a proprietary system. These scripts create viewable dashboards via web/SSH. The touchscreen shows predefined screens (overview, network_status, etc.).

**Q: Can I add real-time graphs?**
A: Yes! Use a graphing tool like `vnstat` or create charts with JavaScript in the web interface.

**Q: Does this affect performance?**
A: Minimal impact. Scripts run once per minute and use <1% CPU.

**Q: Can I access this remotely?**
A: Yes, if you set up port forwarding or use ZeroTier/VPN.

---

## ⚡ Quick Commands

```bash
# View dashboard
ssh root@192.168.8.1 "cat /tmp/custom_dashboard.txt"

# Update now
ssh root@192.168.8.1 "/etc/gl_screen/scripts/custom_dashboard.sh"

# Check VPN
ssh root@192.168.8.1 "cat /tmp/security_status.txt"

# See devices
ssh root@192.168.8.1 "cat /tmp/device_list.txt"

# Watch live
ssh root@192.168.8.1
watch -n 5 cat /tmp/custom_dashboard.txt
```

---

**Ready to install? Run:** `./install_custom_display.sh`
