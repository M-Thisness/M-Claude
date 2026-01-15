# Proxmox VE - Terminal UI Installation Guide

**Installer Mode:** Terminal UI (Text-based)
**Target Device:** Zimaboard SATA SSD/HDD
**Network:** Claude-Slate (192.168.8.0/24)

---

## ❓ Does Terminal UI vs Graphical Matter?

### **NO - The Final System is Identical**

| Installer Type | Final Proxmox System |
|----------------|---------------------|
| Terminal UI    | ✅ Same Proxmox VE OS |
| Graphical UI   | ✅ Same Proxmox VE OS |

**Both produce:**
- Same web GUI (https://192.168.8.21:8006)
- Same CLI/SSH access
- Same features
- Same performance

**Only difference:** Installation process interface

---

## 🖥️ Terminal UI Installation - Step by Step

### Navigation Controls

```
Keyboard Shortcuts:
├─ Tab          → Move between fields
├─ Shift+Tab    → Move backwards
├─ Space        → Toggle checkboxes/select
├─ Enter        → Confirm/OK button
├─ Arrow keys   → Navigate lists/menus
├─ Backspace    → Delete characters
└─ Esc          → Cancel (be careful!)

Mouse: NOT supported in Terminal UI
```

---

### Step 1: Welcome Screen

```
┌─────────────────────────────────────────────┐
│  Welcome to the Proxmox Virtual Environment │
│                                             │
│  This wizard will guide you through the     │
│  Proxmox VE installation.                   │
│                                             │
│  [ I agree to the EULA ]  [ Exit ]          │
└─────────────────────────────────────────────┘

Action: Tab to checkbox, Space to select, Enter to continue
```

---

### Step 2: Target Harddisk Selection

```
┌─ Please select the target harddisk ────────┐
│                                             │
│ Target Harddisk:                            │
│   (*) /dev/sda (120 GB, SATA SSD)   ◄──────┤
│   ( ) /dev/mmcblk0 (32 GB, eMMC)            │
│   ( ) /dev/sdb (8 GB, USB - installer)      │
│                                             │
│ Filesystem:                                 │
│   (*) ext4 (recommended)            ◄──────┤
│   ( ) xfs                                   │
│   ( ) zfs (RAID0)                           │
│   ( ) zfs (RAID1)                           │
│   ( ) zfs (RAID10)                          │
│   ( ) zfs (RAIDZ-1)                         │
│                                             │
│ [x] Advanced Options                        │
│     ├─ hdsize: (leave default for full)     │
│     ├─ swapsize: 4 (GB)                     │
│     ├─ maxroot: (leave default)             │
│     └─ minfree: (leave default)             │
│                                             │
│ [ Options ]  [ OK ]  [ Back ]               │
└─────────────────────────────────────────────┘

CRITICAL: Select /dev/sda (SATA), NOT /dev/mmcblk0 (eMMC)!

Actions:
1. Arrow keys to select /dev/sda
2. Space to select ext4 (already default)
3. Tab to "OK", Enter to continue
```

**Important Disk Selection:**

| Device | Type | Size | Use For Proxmox? |
|--------|------|------|------------------|
| `/dev/sda` | SATA SSD/HDD | 120GB+ | ✅ **YES - Select This** |
| `/dev/mmcblk0` | eMMC | 32GB | ❌ NO - Too small |
| `/dev/sdb` | USB | 8GB | ❌ NO - Installer USB |

---

### Step 3: Location and Timezone

```
┌─ Location and Time Zone Selection ─────────┐
│                                             │
│ Country:                                    │
│   [United States          ▼]                │
│                                             │
│ Time zone:                                  │
│   [America/New_York       ▼]                │
│                                             │
│ Keyboard Layout:                            │
│   [en-us                  ▼]                │
│                                             │
│ [ OK ]  [ Back ]                            │
└─────────────────────────────────────────────┘

Actions:
1. Tab through fields
2. Use arrow keys to select from dropdowns
3. Enter to confirm selection
4. Tab to "OK", Enter to continue
```

**Common Time Zones:**
- `America/New_York` - Eastern
- `America/Chicago` - Central
- `America/Denver` - Mountain
- `America/Los_Angeles` - Pacific
- `UTC` - Universal (if unsure)

---

### Step 4: Administration Password

```
┌─ Set Administration Password ──────────────┐
│                                             │
│ Password:                                   │
│   [****************]                        │
│                                             │
│ Confirm Password:                           │
│   [****************]                        │
│                                             │
│ Email Address (for notifications):          │
│   [admin@local.domain]                      │
│                                             │
│ [ OK ]  [ Back ]                            │
└─────────────────────────────────────────────┘

Password Requirements:
✓ Minimum 5 characters (recommend 16+)
✓ No special requirements (but use strong password!)
✓ Will be used for:
  - Web GUI login (root user)
  - SSH access
  - API authentication

Recommended: 16+ chars, mixed case, numbers, symbols
Example: MyProxm0x!2026@Zima

Email: Optional but recommended for system alerts
```

---

### Step 5: Management Network Configuration

```
┌─ Management Network Configuration ─────────┐
│                                             │
│ Hostname (FQDN):                            │
│   [pve.local.domain_____]           ◄───────┤ CRITICAL
│                                             │
│ IP Address (CIDR):                          │
│   [192.168.8.21/24______]           ◄───────┤ CRITICAL
│                                             │
│ Gateway:                                    │
│   [192.168.8.1__________]           ◄───────┤ CRITICAL
│                                             │
│ DNS Server:                                 │
│   [192.168.8.1__________]           ◄───────┤ CRITICAL
│                                             │
│ Management Interface:                       │
│   (*) eth0 (Link detected)          ◄───────┤ Select
│   ( ) eth1 (No link)                        │
│   ( ) eth2 (No link)                        │
│   ( ) eth3 (No link)                        │
│                                             │
│ [ OK ]  [ Back ]                            │
└─────────────────────────────────────────────┘

EXACT VALUES TO ENTER:
```

| Field | Value to Type | Notes |
|-------|---------------|-------|
| **Hostname** | `pve.local.domain` | Must be FQDN format |
| **IP/CIDR** | `192.168.8.21/24` | Include `/24` suffix! |
| **Gateway** | `192.168.8.1` | Router IP |
| **DNS** | `192.168.8.1` | Router (forwarding to 1.1.1.1) |
| **Interface** | `eth0` | First 2.5GbE NIC with cable |

**Common Mistakes to Avoid:**
- ❌ `192.168.8.21` (missing /24)
- ✅ `192.168.8.21/24` (correct CIDR)
- ❌ `pve` (not FQDN)
- ✅ `pve.local.domain` (correct FQDN)

---

### Step 6: Summary and Confirmation

```
┌─ Summary ──────────────────────────────────┐
│                                             │
│ Please verify the following configuration:  │
│                                             │
│ Target Disk:    /dev/sda (120 GB)   ◄───── CHECK!
│ Filesystem:     ext4                        │
│ Country:        United States               │
│ Timezone:       America/New_York            │
│ Keymap:         en-us                       │
│ Email:          admin@local.domain          │
│ Hostname:       pve.local.domain    ◄───── CHECK!
│ IP Address:     192.168.8.21/24     ◄───── CHECK!
│ Gateway:        192.168.8.1         ◄───── CHECK!
│ DNS:            192.168.8.1         ◄───── CHECK!
│                                             │
│ [ Install ]  [ Previous ]  [ Abort ]        │
└─────────────────────────────────────────────┘

VERIFY CHECKLIST:
[ ] Target is /dev/sda (NOT mmcblk0)
[ ] IP is 192.168.8.21/24
[ ] Gateway is 192.168.8.1
[ ] DNS is 192.168.8.1
[ ] Hostname is pve.local.domain

If ALL correct → Tab to "Install", press Enter
If WRONG → Tab to "Previous", fix the error
```

---

### Step 7: Installation Progress

```
┌─ Installing Proxmox VE ────────────────────┐
│                                             │
│ Partitioning disk...                        │
│ [████████████████████████] 100%             │
│                                             │
│ Copying files...                            │
│ [████████████░░░░░░░░░░░░]  45%             │
│                                             │
│ Estimated time remaining: 8 minutes         │
│                                             │
│ (Do not power off or remove media)          │
└─────────────────────────────────────────────┘

Typical installation time: 10-15 minutes

Stages:
1. Partitioning disk (30 seconds)
2. Creating filesystems (1 minute)
3. Copying system files (5-8 minutes)
4. Installing bootloader (1 minute)
5. Configuring system (2-3 minutes)

DO NOT:
- Power off system
- Remove installer USB (yet)
- Press any keys
- Disconnect network cable
```

---

### Step 8: Installation Complete

```
┌─ Installation Complete ────────────────────┐
│                                             │
│ Proxmox VE has been successfully installed! │
│                                             │
│ Please remove the installation medium and   │
│ press Enter to reboot.                      │
│                                             │
│ After reboot, access the web interface at:  │
│                                             │
│   https://192.168.8.21:8006                 │
│                                             │
│ [ Reboot ]                                  │
└─────────────────────────────────────────────┘

Actions:
1. Remove installer USB from Zimaboard
2. Press Enter to reboot
3. Wait for system to boot (~2 minutes)
4. Access web GUI from another device
```

---

## 🎯 After Reboot - What to Expect

### Text Console (at monitor/keyboard)

You'll see a login prompt:

```
Proxmox VE 8.x

pve login: _
```

**You can login here, but it's NOT necessary!**
- This is just a text console (rarely used)
- Everything is managed via Web GUI

**If you want to login at console:**
```
Login: root
Password: [your_password]

# Then you have a bash shell
root@pve:~#
```

---

### Web GUI Access (RECOMMENDED)

From **any device on the network** (laptop, phone, etc.):

```
1. Open browser
2. Go to: https://192.168.8.21:8006

3. You'll see security warning (expected)
   "Your connection is not private"
   → Click "Advanced"
   → Click "Proceed to 192.168.8.21 (unsafe)"
   (This is normal - self-signed certificate)

4. Proxmox VE Login:
   Username: root
   Realm: Linux PAM standard authentication
   Password: [your_password]
   Language: English
   → [ Login ]

5. You'll see the Proxmox dashboard!
```

**Web GUI is the PRIMARY interface** - use this for everything!

---

### SSH Access (for advanced users)

```bash
# From Linux/Mac terminal or Windows PowerShell
ssh root@192.168.8.21

# First time:
The authenticity of host '192.168.8.21' can't be established.
Are you sure you want to continue connecting (yes/no)? yes

# Enter password
root@192.168.8.21's password: [your_password]

# You're in!
root@pve:~#
```

---

## 🔧 Post-Installation - First Commands

### Via Web GUI

```
After login:
1. Dismiss "No valid subscription" message (normal)
2. Click "pve" in left sidebar
3. Click "Updates" → "Refresh"
4. Click "Upgrade" to update system
```

### Via SSH (Alternative)

```bash
# 1. Fix repository warning
echo "# deb https://enterprise.proxmox.com/debian/pve bookworm pve-enterprise" > /etc/apt/sources.list.d/pve-enterprise.list

echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list

# 2. Update system
apt update
apt full-upgrade -y

# 3. Verify network
ping -c 4 192.168.8.1   # Gateway
ping -c 4 1.1.1.1       # Internet
ping -c 4 google.com    # DNS

# 4. Check storage
df -h
pvesm status

# 5. Reboot
reboot
```

---

## 📊 Terminal UI vs Graphical - Feature Comparison

| Feature | Terminal UI | Graphical UI | Final System |
|---------|-------------|--------------|--------------|
| **Installation Method** | Text menus | Point-click GUI | N/A |
| **Keyboard Navigation** | Required | Optional (mouse) | N/A |
| **Resource Usage** | Low | Higher | N/A |
| **Remote Install** | ✅ Works over serial | ❌ Needs graphics | N/A |
| **Web GUI After Install** | ✅ Available | ✅ Available | **Identical** |
| **SSH Access** | ✅ Available | ✅ Available | **Identical** |
| **Performance** | ✅ Same | ✅ Same | **Identical** |
| **Features** | ✅ All | ✅ All | **Identical** |
| **VMs** | ✅ Same | ✅ Same | **Identical** |

### Bottom Line:

**Terminal UI = Graphical UI** (after installation completes)

The installer is just a **one-time configuration wizard**.
Once Proxmox is installed, the system is **identical**.

---

## ✅ Installation Checklist

### Pre-Installation
- [ ] SATA disk connected to Zimaboard (120GB+ recommended)
- [ ] Network cable: Zimaboard eth0 → Claude-Slate router
- [ ] Proxmox installer USB inserted
- [ ] Keyboard connected (for Terminal UI input)
- [ ] Monitor connected (optional, to see installer)
- [ ] Know your network settings (192.168.8.21/24)

### During Installation (Terminal UI)
- [ ] Select "Install Proxmox VE (Terminal UI)"
- [ ] Accept EULA
- [ ] Select target: `/dev/sda` (SATA)
- [ ] Filesystem: `ext4`
- [ ] Timezone: America/New_York (or yours)
- [ ] Set strong root password (16+ chars)
- [ ] Hostname: `pve.local.domain`
- [ ] IP: `192.168.8.21/24` (include /24!)
- [ ] Gateway: `192.168.8.1`
- [ ] DNS: `192.168.8.1`
- [ ] Interface: `eth0` (with link detected)
- [ ] Verify summary screen
- [ ] Wait for installation (~10-15 min)
- [ ] Remove installer USB
- [ ] Reboot

### Post-Installation
- [ ] Web GUI loads: https://192.168.8.21:8006
- [ ] Login as root works
- [ ] SSH access works
- [ ] Network connectivity verified (ping tests)
- [ ] System updated (apt update && upgrade)
- [ ] Storage verified (df -h, pvesm status)
- [ ] Repository warnings fixed
- [ ] Ready to create first VM!

---

## 🎓 Why Choose Terminal UI?

### Advantages:

1. **Lower Resource Usage**
   - No GUI rendering overhead
   - Faster on low-spec systems
   - Less RAM/CPU during install

2. **Remote Installation**
   - Works over serial console
   - Can install headless
   - Professional server practice

3. **More Reliable**
   - Fewer dependencies
   - Less can go wrong
   - Text is universal

4. **Professional Standard**
   - Most sysadmins use TUI
   - Industry best practice
   - Learn proper server management

### When to Use Graphical:

- Local installation with monitor
- Prefer mouse navigation
- First time installing Proxmox
- Want visual feedback

**Both produce the same result!**

---

## 🔗 Quick Reference - Network Settings

```yaml
Network Configuration Summary:
============================
Hostname:     pve.local.domain
IP/CIDR:      192.168.8.21/24
Netmask:      255.255.255.0
Gateway:      192.168.8.1
DNS:          192.168.8.1
Broadcast:    192.168.8.255
Network:      192.168.8.0

Router:       Claude-Slate (GL-BE3600)
Router IP:    192.168.8.1
Upstream DNS: 1.1.1.1, 1.0.0.1 (Cloudflare)
Network:      192.168.8.0/24

Interface:    eth0 (2.5 Gbps)
Bridge:       vmbr0 (created automatically)

Access After Install:
====================
Web GUI:      https://192.168.8.21:8006
SSH:          ssh root@192.168.8.21
API:          https://192.168.8.21:8006/api2/json
```

---

## 📚 Related Documentation

- [INSTALLATION_TROUBLESHOOTING.md](./INSTALLATION_TROUBLESHOOTING.md) - Error recovery
- [INSTALLATION_PARAMETERS.md](./INSTALLATION_PARAMETERS.md) - Quick reference
- [Proxmox Wiki](https://pve.proxmox.com/wiki/Installation) - Official docs

---

**Last Updated:** 2026-01-15
**Status:** Terminal UI installation in progress on SATA
**Next:** Post-install configuration and first VM
