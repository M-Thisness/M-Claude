# Proxmox Installation Parameters - Quick Reference

**Device:** Zimaboard
**Network:** Claude-Slate (GL-BE3600)
**Date:** 2026-01-15

---

## 🎯 Installation Wizard - Fill-in Values

### 1. Target Harddisk

```
┌─ Harddisk ─────────────────────────────────┐
│                                             │
│ Target Harddisk:  /dev/sda ◄────── USB SSD │
│                   (NOT /dev/mmcblk0)        │
│                                             │
│ Filesystem:       ext4                      │
│                                             │
│ [ ] Advanced Options                        │
│                                             │
└─────────────────────────────────────────────┘
```

**Recommended:**
- **Target:** `/dev/sda` (128GB+ USB SSD)
- **Filesystem:** `ext4` (reliable, proven)
- **Skip Advanced** unless you need custom partitioning

---

### 2. Location and Time Zone

```
┌─ Location ─────────────────────────────────┐
│                                             │
│ Country:          United States             │
│ Time zone:        America/New_York          │
│ Keyboard Layout:  en-us                     │
│                                             │
└─────────────────────────────────────────────┘
```

---

### 3. Administration Password

```
┌─ Administration Password ──────────────────┐
│                                             │
│ Password:         [SET_STRONG_PASSWORD]     │
│ Confirm:          [SET_STRONG_PASSWORD]     │
│                                             │
│ Email:            admin@local.domain        │
│                   (for system notifications)│
│                                             │
└─────────────────────────────────────────────┘
```

**Security Tips:**
- Use 16+ character password
- Mix uppercase, lowercase, numbers, symbols
- Store in password manager
- Email is optional but recommended for alerts

---

### 4. Management Network Configuration

```
┌─ Network Configuration ────────────────────┐
│                                             │
│ Hostname (FQDN):  pve.local.domain          │
│                   (or: proxmox-zima.local)  │
│                                             │
│ IP Address:       192.168.8.21/24           │
│                   ^^^^^^^^^^^^^ (CIDR)      │
│                                             │
│ Gateway:          192.168.8.1               │
│                   (Claude-Slate router)     │
│                                             │
│ DNS Server:       192.168.8.1               │
│                   (router with Cloudflare)  │
│                                             │
│ Interface:        eth0 ◄─── First 2.5GbE   │
│                   (any of 4 NICs works)     │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📋 Copy-Paste Values

For easy copy-paste during installation:

| Field | Value |
|-------|-------|
| **Hostname** | `pve.local.domain` |
| **IP/CIDR** | `192.168.8.21/24` |
| **Gateway** | `192.168.8.1` |
| **DNS** | `192.168.8.1` |

---

## 🌐 Network Context (Claude-Slate)

```
Router:  192.168.8.1 (GL-BE3600 "Claude-Slate")
Network: 192.168.8.0/24
Subnet:  255.255.255.0
DHCP:    192.168.8.201-250 (avoid this range)

Proxmox Host:
├─ IP:       192.168.8.21 (Static, wired devices range)
├─ Gateway:  192.168.8.1 (Router)
├─ DNS 1:    192.168.8.1 (Router → Cloudflare)
├─ DNS 2:    1.1.1.1 (Cloudflare, backup)
└─ DNS 3:    1.0.0.1 (Cloudflare, backup)

VM Range (suggested):
├─ 192.168.8.101-149 (50 VMs available)
```

---

## 🔧 Post-Installation Quick Setup

### First Login

```bash
# From another computer on network
ssh root@192.168.8.21
# Enter password set during installation

# Or open browser
https://192.168.8.21:8006
# Username: root
# Password: [password from installation]
```

### Essential First Commands

```bash
# 1. Fix enterprise repository
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

# 5. Reboot to apply updates
reboot
```

---

## 🖧 Network Interface Configuration

After installation, verify `/etc/network/interfaces`:

```bash
cat /etc/network/interfaces
```

Should contain:

```conf
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet manual

auto vmbr0
iface vmbr0 inet static
    address 192.168.8.21/24
    gateway 192.168.8.1
    bridge-ports eth0
    bridge-stp off
    bridge-fd 0
```

---

## 📊 Expected Installation Summary

At the end of installation wizard:

```
┌─ Summary ──────────────────────────────────┐
│                                             │
│ Please verify the following settings:       │
│                                             │
│ Target Disk:    /dev/sda (120 GB)           │
│ Filesystem:     ext4                        │
│ Country:        United States               │
│ Timezone:       America/New_York            │
│ Keymap:         en-us                       │
│ Email:          admin@local.domain          │
│ Hostname:       pve.local.domain            │
│ IP Address:     192.168.8.21/24             │
│ Gateway:        192.168.8.1                 │
│ DNS:            192.168.8.1                 │
│                                             │
│ [ Install ]  [ Previous ]                   │
│                                             │
└─────────────────────────────────────────────┘
```

**VERIFY** all settings match before clicking "Install"!

---

## 🚨 Troubleshooting Quick Checks

If installation fails:

### Check 1: Disk Space

```bash
# Switch to shell (Ctrl+Alt+F2)
lsblk -o NAME,SIZE,TYPE
df -h
```

Expected: Target disk should have 60GB+ free

### Check 2: Network Cable

- Ensure eth0 (any 2.5GbE port) is connected to router
- Check link light on NIC
- Verify cable is CAT5e or better

### Check 3: Wipe Disk

```bash
# If installation fails, wipe and retry
wipefs -a /dev/sda
sgdisk --zap-all /dev/sda
partprobe /dev/sda
reboot
```

---

## ✅ Installation Checklist

- [ ] USB SSD (128GB+) connected to Zimaboard
- [ ] Ethernet cable from Zimaboard to router (192.168.8.1)
- [ ] Proxmox installer USB created and inserted
- [ ] Keyboard and monitor connected
- [ ] Zimaboard powered on
- [ ] Boot from Proxmox installer USB
- [ ] Select "Install Proxmox VE" (graphical)
- [ ] Accept EULA
- [ ] Select target disk: `/dev/sda`
- [ ] Set timezone: America/New_York
- [ ] Set strong root password
- [ ] Configure network:
  - [ ] Hostname: `pve.local.domain`
  - [ ] IP: `192.168.8.21/24`
  - [ ] Gateway: `192.168.8.1`
  - [ ] DNS: `192.168.8.1`
- [ ] Verify summary screen
- [ ] Click "Install"
- [ ] Wait for installation (10-15 minutes)
- [ ] Remove installer USB when prompted
- [ ] Reboot
- [ ] Access web GUI: https://192.168.8.21:8006
- [ ] Login as root
- [ ] Update system
- [ ] Done!

---

## 📞 Quick Access Information

**After successful installation:**

| Service | Access Method |
|---------|---------------|
| **Web GUI** | https://192.168.8.21:8006 |
| **SSH** | `ssh root@192.168.8.21` |
| **VNC** | Through web GUI (VM console) |
| **API** | https://192.168.8.21:8006/api2/json |

**Default Credentials:**
- Username: `root`
- Password: [set during installation]

---

## 🔗 Next Steps After Installation

1. **Update System**
   - Fix repository warnings
   - Run apt update & upgrade
   - Reboot

2. **Configure Storage**
   - Add additional disks (if any)
   - Set up NFS/iSCSI (optional)
   - Configure backup storage

3. **Create First VM**
   - Upload ISO images
   - Create VM with 192.168.8.101-149 IP range
   - Install OS and test connectivity

4. **Security Hardening**
   - Set up SSH keys
   - Disable root password login
   - Configure firewall rules
   - Set up automatic updates

5. **Backup Configuration**
   - Export /etc/network/interfaces
   - Backup /etc/pve/
   - Document VM assignments

---

**Created:** 2026-01-15
**Status:** Ready for installation
**Target:** Zimaboard with USB SSD
