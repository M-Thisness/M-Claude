# Proxmox Installation Troubleshooting Guide

**Target Device:** Zimaboard (Intel I225 4x2.5GbE)
**Installation Date:** 2026-01-15
**Network:** Claude-Slate (192.168.8.0/24)
**Issue:** Installation errors on eMMC storage

---

## 🚨 Observed Installation Errors

### Error Log Analysis

```
dd: error writing '/dev/mmcblk0p6': No space left on device
unable to get device for partition 1 on device /dev/mmcblk0
umount: /target/xxx: no mount point specified
umount: /target: not mounted
```

### Root Causes

1. **Insufficient eMMC space** - Partition 6 ran out of space during write
2. **GPT partition table destroyed** - Old partitions wiped but new ones not created
3. **Installation incomplete** - Mounting failed, installation did not finish
4. **Pixbuf warning** - Non-critical GUI rendering issue

---

## ✅ Solution Strategies

### Strategy 1: Use External Storage (RECOMMENDED)

**Why External Storage?**
- eMMC has limited write endurance (not ideal for Proxmox)
- Better performance with SSD
- Easier to replace if fails
- Larger capacity for VMs

**Recommended Storage Options:**

| Storage Type | Capacity | Performance | Reliability | Cost |
|--------------|----------|-------------|-------------|------|
| **USB 3.0 SSD** | 128GB+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $ |
| M.2 NVMe (if supported) | 256GB+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $$ |
| USB 3.0 Flash Drive | 64GB+ | ⭐⭐ | ⭐⭐ | $ |
| eMMC (internal) | 32GB | ⭐⭐ | ⭐⭐ | (included) |

**Installation Steps with External Storage:**

1. Connect USB SSD to Zimaboard
2. Boot from Proxmox installer USB
3. Select `/dev/sda` (USB SSD) as installation target
4. Continue with standard installation

---

### Strategy 2: Optimize eMMC Installation

If you must use the internal eMMC:

#### Step 1: Boot to Installer Shell

```bash
# Press Ctrl+Alt+F2 during installation to access shell
# Or Ctrl+Alt+F3 for another TTY
```

#### Step 2: Check Available Storage

```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
fdisk -l /dev/mmcblk0
df -h
```

Expected output:
```
NAME         SIZE TYPE
mmcblk0      32G  disk
├─mmcblk0p1  512M part  (should be EFI)
├─mmcblk0p2  27G  part  (should be root)
└─mmcblk0p3  4G   part  (should be swap)
```

#### Step 3: Wipe Disk Completely

```bash
# Clear all existing partitions
wipefs -a /dev/mmcblk0

# Destroy GPT and MBR
sgdisk --zap-all /dev/mmcblk0

# Update kernel partition table
partprobe /dev/mmcblk0

# Verify clean disk
fdisk -l /dev/mmcblk0
# Should show: "Disk /dev/mmcblk0: 32 GiB" with no partitions
```

#### Step 4: Restart Installation

```bash
reboot
# Then restart Proxmox installer from USB
```

---

## 📋 Installation Configuration

### Network Configuration (Claude-Slate Network)

```yaml
# Proxmox VE Installation Wizard

Target Harddisk:
  Device:           /dev/sda          # USB SSD (recommended)
                    /dev/mmcblk0      # eMMC (if no USB SSD)

  Filesystem:       ext4              # Default, reliable
                    # OR zfs          # Advanced features, needs >32GB

  Advanced Options:
    hdsize:         120               # Use 120GB of 128GB SSD
    swapsize:       4                 # 4GB swap
    maxroot:        30                # 30GB for root (rest for data)
    minfree:        8                 # 8GB free space reserve

Location:
  Country:          United States
  Time zone:        America/New_York  # Or your timezone
  Keyboard Layout:  en-us

Administration:
  Password:         [STRONG_PASSWORD]
  Confirm Password: [STRONG_PASSWORD]
  Email:            admin@local.domain

Network Configuration:
  Hostname (FQDN):  pve.local.domain
                    # OR proxmox-zima.local.domain

  IP Address:       192.168.8.21/24
  Gateway:          192.168.8.1
  DNS Server:       192.168.8.1

  Management Interface:
    - eth0          # First 2.5GbE port connected to Claude-Slate router
```

---

## 🔍 Verification After Installation

### Step 1: Check Network Connectivity

```bash
# SSH into Proxmox (from another device)
ssh root@192.168.8.21

# Or access web GUI
# https://192.168.8.21:8006

# On Proxmox host, verify:
ip addr show
# Should show: eth0 with 192.168.8.21/24

ip route show
# Should show: default via 192.168.8.1 dev vmbr0

cat /etc/resolv.conf
# Should show: nameserver 192.168.8.1

ping -c 4 192.168.8.1    # Test gateway
ping -c 4 1.1.1.1        # Test internet
ping -c 4 google.com     # Test DNS
```

### Step 2: Check Storage

```bash
df -h
# Should show:
# /dev/sda2 or /dev/mmcblk0p2 mounted on /
# Plenty of free space available

lsblk
# Should show proper partition layout

pvesm status
# Should show local and local-lvm storage
```

### Step 3: Update System

```bash
# Fix enterprise repo if no subscription
echo "# deb https://enterprise.proxmox.com/debian/pve bookworm pve-enterprise" > /etc/apt/sources.list.d/pve-enterprise.list

echo "deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription" > /etc/apt/sources.list.d/pve-no-subscription.list

apt update
apt full-upgrade -y
reboot
```

---

## 🛠️ Common Installation Issues & Fixes

### Issue 1: "No space left on device"

**Cause:** Disk too small or partitioning failed

**Solutions:**
- Use larger storage device (128GB+ USB SSD)
- Reduce swap size (2GB instead of 4GB)
- Use ext4 instead of ZFS
- Manually partition disk before installation

**Manual Partitioning:**

```bash
# Create GPT partition table
sgdisk -o /dev/sda

# Create partitions
sgdisk -n 1:0:+512M -t 1:ef00 /dev/sda   # EFI
sgdisk -n 2:0:+100G -t 2:8300 /dev/sda   # Root
sgdisk -n 3:0:0 -t 3:8200 /dev/sda       # Swap

# Verify
sgdisk -p /dev/sda
```

---

### Issue 2: "unable to get device for partition"

**Cause:** Kernel hasn't reloaded partition table

**Solution:**

```bash
partprobe /dev/mmcblk0
udevadm settle
```

---

### Issue 3: Installation hangs or freezes

**Cause:** Hardware compatibility or USB drive issues

**Solutions:**
- Use different USB port
- Try USB 2.0 port instead of 3.0
- Verify Proxmox ISO integrity (checksum)
- Re-create bootable USB with different tool (Rufus, Etcher, dd)

**Recreate USB (Linux):**

```bash
# Find USB device
lsblk

# Write ISO (replace sdX with your USB device)
sudo dd if=proxmox-ve_8.x.iso of=/dev/sdX bs=4M status=progress && sync
```

---

### Issue 4: Cannot access web GUI after installation

**Cause:** Network misconfiguration or firewall

**Solutions:**

```bash
# Check Proxmox web service
systemctl status pveproxy

# Restart if needed
systemctl restart pveproxy

# Check if port 8006 is listening
ss -tlnp | grep 8006

# Check firewall (should be off by default)
pve-firewall status
```

**From router (Claude-Slate):**

```bash
# SSH to router
ssh root@192.168.8.1

# Test connectivity to Proxmox
ping 192.168.8.21
curl -k https://192.168.8.21:8006
```

---

## 📊 Zimaboard Hardware Specifications

```yaml
CPU:           Intel Celeron N3450/N3350 (Quad-core)
RAM:           4GB/8GB LPDDR4
Storage:       32GB eMMC (internal)
Network:       4x Intel I225 2.5GbE
USB:           2x USB 3.0, 2x USB 2.0
Display:       Mini DisplayPort
PCIe:          1x PCIe 2.0 x4 (M.2 M-Key for NVMe)
SATA:          2x SATA 3.0 ports
Power:         12V DC
```

**Recommended Proxmox Configuration:**
- RAM: 4GB minimum (8GB recommended)
- Storage: 128GB USB SSD or NVMe (NOT eMMC)
- Network: Use eth0 (any I225 port) for management

---

## 🎯 Recommended Installation Path

### Best Practice Installation Steps:

1. **Prepare Hardware**
   - Connect 128GB+ USB 3.0 SSD to Zimaboard
   - Connect eth0 to Claude-Slate router (192.168.8.1)
   - Connect monitor and keyboard (for installation)

2. **Boot Proxmox Installer**
   - Insert Proxmox USB installer
   - Power on Zimaboard
   - Select USB boot device

3. **Run Installation Wizard**
   - Target Disk: `/dev/sda` (USB SSD)
   - Filesystem: `ext4`
   - Hostname: `pve.local.domain`
   - IP: `192.168.8.21/24`
   - Gateway: `192.168.8.1`
   - DNS: `192.168.8.1`

4. **Post-Installation**
   - Remove installer USB
   - Reboot
   - Access web GUI: `https://192.168.8.21:8006`
   - Update system
   - Configure storage
   - Create first VM

5. **Document Configuration**
   - Save network settings
   - Backup `/etc/network/interfaces`
   - Document VM IP assignments

---

## 📝 Network Integration with Claude-Slate

### Static DHCP Reservation (Recommended)

On Claude-Slate router (192.168.8.1):

```bash
# Find Proxmox MAC address
ssh root@192.168.8.21
ip link show eth0
# Note the MAC address (e.g., aa:bb:cc:dd:ee:ff)

# On router, add static lease
ssh root@192.168.8.1
uci add dhcp host
uci set dhcp.@host[-1].name='proxmox-zima'
uci set dhcp.@host[-1].mac='aa:bb:cc:dd:ee:ff'
uci set dhcp.@host[-1].ip='192.168.8.21'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

### DNS Entry

```bash
# On Claude-Slate router
echo "192.168.8.21    pve.local.domain    pve" >> /etc/hosts

# Or use router's DNS service
uci add dhcp domain
uci set dhcp.@domain[-1].name='pve.local.domain'
uci set dhcp.@domain[-1].ip='192.168.8.21'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

---

## 🔗 Related Documentation

- [Proxmox VE Installation Guide](https://pve.proxmox.com/wiki/Installation)
- [Proxmox Network Configuration](https://pve.proxmox.com/wiki/Network_Configuration)
- [Claude-Slate Network Plan](../Claude-Slate/network_optimization_plan.md)
- [Zimaboard Documentation](https://www.zimaboard.com/)

---

## ✅ Post-Installation Checklist

- [ ] Proxmox web GUI accessible at https://192.168.8.21:8006
- [ ] SSH access working: `ssh root@192.168.8.21`
- [ ] Network connectivity verified (gateway, internet, DNS)
- [ ] System updated: `apt update && apt full-upgrade`
- [ ] Enterprise repo disabled (if no subscription)
- [ ] Storage verified: `pvesm status`
- [ ] First VM created and running
- [ ] Backup strategy configured
- [ ] Documentation updated with actual configuration
- [ ] MAC address added to router DHCP reservation
- [ ] DNS entry added for pve.local.domain

---

## 🆘 Getting Help

If issues persist:

1. Check Proxmox forum: https://forum.proxmox.com/
2. Review installation logs: `/var/log/installer/`
3. Boot to rescue mode from installer
4. Consider alternative storage device
5. Verify hardware compatibility

---

**Last Updated:** 2026-01-15
**Status:** Installation in progress - troubleshooting eMMC errors
**Next Steps:** Retry installation with USB SSD instead of eMMC
