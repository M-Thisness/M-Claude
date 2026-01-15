# Troubleshooting: Slate Dropped Zima Connection

**Issue:** Claude-Slate router dropped connection to Zimaboard during Proxmox installation
**Time:** During Terminal UI installation to SATA
**Network:** 192.168.8.0/24

---

## 🔍 Diagnostic Steps

### Step 1: Check from Router (Claude-Slate)

From another device, SSH to router:

```bash
ssh root@192.168.8.1

# 1. Check if Zimaboard is still in DHCP leases
cat /tmp/dhcp.leases | grep -i zima
cat /tmp/dhcp.leases | grep 192.168.8.21

# 2. Check ARP table (Layer 2 connectivity)
ip neigh show | grep 192.168.8.21
# Look for "REACHABLE" or "STALE"

# 3. Try to ping Zimaboard
ping -c 5 192.168.8.21

# 4. Check connected clients
cat /proc/net/arp | grep 192.168.8.21

# 5. Check router port status
ip link show eth1  # Adjust if different port
```

**Expected Outputs:**

**Good (Connected):**
```
192.168.8.21 dev br-lan lladdr aa:bb:cc:dd:ee:ff REACHABLE
```

**Bad (Disconnected):**
```
(no output or "FAILED")
```

---

### Step 2: Check Physical Layer

```
Zimaboard Side:
├─ Check eth0 port for link light (green LED)
├─ Should be: Solid or blinking
├─ If OFF: No physical connection
└─ Try: Reseat cable, try different cable

Router Side (Claude-Slate):
├─ Check LAN port for link light
├─ Should be: Solid or blinking
├─ If OFF: Port may have disabled
└─ Try: Different router port (eth1 has 2.5GbE)
```

---

### Step 3: Check on Zimaboard (If Accessible)

During installation, press **Ctrl+Alt+F2** to access shell:

```bash
# Check network interface status
ip link show

# Look for eth0:
# <BROADCAST,MULTICAST,UP,LOWER_UP> ← GOOD
# <NO-CARRIER> ← BAD (cable issue)

# Check eth0 specifically
ip link show eth0

# If DOWN, bring it up
ip link set eth0 up

# Check if IP assigned (might not be during install)
ip addr show eth0

# Try to ping gateway
ping -c 3 192.168.8.1

# Check if DHCP client running
ps aux | grep dhcp
```

---

## 🛠️ Common Causes & Solutions

### Cause 1: Installation Temporarily Disabled Network
**Symptom:** Connection drops during disk partitioning/formatting
**Why:** Installer may briefly reconfigure network stack
**Fix:** Wait 60-90 seconds, should auto-reconnect
**Severity:** Low (normal behavior)

---

### Cause 2: Cable/Physical Connection Issue
**Symptom:** Link lights OFF on NIC or router port
**Why:** Loose cable, bad cable, port issue
**Fix:**
```bash
1. Reseat both ends of ethernet cable
2. Try different ethernet cable (CAT5e or better)
3. Try different router port
4. Try different Zimaboard NIC (eth1/eth2/eth3)
```
**Severity:** Medium (easily fixed)

---

### Cause 3: Router Port Power Management (EEE)
**Symptom:** Port was working, suddenly drops, especially on 2.5GbE
**Why:** Energy Efficient Ethernet (802.3az) puts port to sleep
**Fix on Router:**
```bash
ssh root@192.168.8.1

# Disable EEE on eth1 (2.5GbE port)
ethtool --set-eee eth1 eee off

# Or restart network to reset port
/etc/init.d/network restart

# Check port status
ethtool eth1
```
**Severity:** Medium (GL.iNet routers sometimes have this)

---

### Cause 4: MAC Address Filter or Firewall
**Symptom:** Device connected before, now blocked
**Why:** Router firewall rule or MAC filter activated
**Fix on Router:**
```bash
ssh root@192.168.8.1

# Check firewall rules
nft list ruleset | grep 192.168.8.21

# Check MAC filters
uci show wireless | grep -i mac

# Temporarily disable firewall for testing
/etc/init.d/firewall stop

# Try ping again
ping -c 3 192.168.8.21

# Re-enable firewall
/etc/init.d/firewall start
```
**Severity:** Low (unlikely during fresh install)

---

### Cause 5: Network Loop or Broadcast Storm
**Symptom:** Multiple devices dropping, router unstable
**Why:** Network misconfiguration causing loops
**Fix:**
```bash
# Disconnect all devices except router and Zimaboard
# Reboot router
ssh root@192.168.8.1
reboot
```
**Severity:** High (but rare)

---

### Cause 6: DHCP Pool Exhausted
**Symptom:** New devices can't get IP addresses
**Why:** All DHCP addresses assigned
**Fix on Router:**
```bash
ssh root@192.168.8.1

# Check DHCP leases
cat /tmp/dhcp.leases | wc -l
# If close to 50 (your pool is 192.168.8.201-250)

# View all leases
cat /tmp/dhcp.leases

# Restart DHCP to clear stale leases
/etc/init.d/dnsmasq restart
```
**Severity:** Low (pool is 50 IPs, unlikely full)

---

## ✅ Quick Fix Procedures

### Procedure A: Physical Reset (2 minutes)

```
1. On Zimaboard:
   └─ Unplug ethernet cable from eth0
   └─ Wait 5 seconds
   └─ Plug back in
   └─ Check for link light (green LED)

2. On Router:
   └─ Note which port Zimaboard is connected to
   └─ Unplug cable
   └─ Wait 5 seconds
   └─ Plug back in
   └─ Check for link light

3. Test:
   └─ From another device: ping 192.168.8.21
```

---

### Procedure B: Router Port Reset (2 minutes)

```bash
# SSH to router
ssh root@192.168.8.1

# Restart network service
/etc/init.d/network restart

# Wait 30 seconds

# Check if Zimaboard reappeared
ping -c 5 192.168.8.21

# Check ARP
ip neigh show | grep 192.168.8.21
```

---

### Procedure C: Try Different Network Interface (5 minutes)

Zimaboard has **4x 2.5GbE ports** - try another one!

```
1. Unplug cable from eth0
2. Plug into eth1 (second port)
3. During installation, select eth1 instead of eth0
4. Continue installation with same IP settings
```

---

### Procedure D: Static IP Override (Advanced)

If DHCP isn't working during installation:

```bash
# At installer shell (Ctrl+Alt+F2)

# Manually configure network
ip addr add 192.168.8.21/24 dev eth0
ip link set eth0 up
ip route add default via 192.168.8.1

# Test connectivity
ping -c 3 192.168.8.1
ping -c 3 1.1.1.1

# Then continue installation
# (Network settings will be reconfigured by installer)
```

---

## 🔍 Diagnostic Commands Reference

### On Router (Claude-Slate)

```bash
# Device discovery
ip neigh show                    # ARP table
cat /tmp/dhcp.leases            # DHCP leases
arp -a                          # All ARP entries

# Network status
ip link show                    # All interfaces
ethtool eth1                    # Port details (2.5GbE)
brctl show                      # Bridge status

# Connectivity tests
ping 192.168.8.21               # Ping Zimaboard
arping -I br-lan 192.168.8.21  # ARP ping

# Logs
logread | grep -i dhcp          # DHCP logs
logread | tail -n 50            # Recent logs
```

### On Zimaboard (During Install)

```bash
# Interface status
ip link show                    # All NICs
ip addr show                    # IP addresses
ip route show                   # Routing table

# Connectivity
ping -c 3 192.168.8.1           # Ping gateway
ping -c 3 1.1.1.1               # Ping internet

# Hardware info
ethtool eth0                    # NIC details
lspci | grep -i ethernet        # PCI ethernet devices
dmesg | grep -i eth             # Kernel messages
```

---

## 📊 Decision Tree

```
Connection dropped?
│
├─ Link lights OFF?
│  ├─ YES → Physical issue
│  │  └─ Fix: Reseat cable, try different port
│  └─ NO → Continue
│
├─ Can ping from router?
│  ├─ YES → Router can reach Zima
│  │  └─ Problem may be temporary, continue install
│  └─ NO → Continue troubleshooting
│
├─ Does ARP show device?
│  ├─ YES → Layer 2 working
│  │  └─ Check IP configuration
│  └─ NO → Layer 2 issue
│     └─ Fix: Restart network, check cable
│
└─ Try different NIC port (eth1/2/3)
```

---

## ⚠️ During Proxmox Installation

**IMPORTANT:** Network connectivity may be inconsistent during installation!

**Why:**
- Installer reconfigures network interfaces
- Switches from DHCP to static IP
- May bring interfaces down/up multiple times

**Expected behavior:**
1. **Before install:** May have DHCP IP or no IP
2. **During install:** Network may go up/down
3. **After install:** Static IP (192.168.8.21/24) configured

**Recommendation:**
- Don't panic if connection drops during install
- Installation can complete without network (for disk formatting)
- Network will be configured at end of installation
- Verify connectivity AFTER installation completes and system reboots

---

## ✅ Post-Installation Verification

After installation completes and Zimaboard reboots:

```bash
# From another device, test connectivity
ping 192.168.8.21

# Should respond:
# 64 bytes from 192.168.8.21: icmp_seq=1 ttl=64 time=1.2 ms

# Try SSH
ssh root@192.168.8.21

# Try web GUI
https://192.168.8.21:8006
```

**If still no connection after reboot:**
1. Check Zimaboard monitor/console for IP address
2. Verify network settings in `/etc/network/interfaces`
3. Try DHCP temporarily to get online
4. Reconfigure static IP once accessible

---

## 🆘 Emergency Recovery

If completely unable to connect after installation:

### Option 1: Console Access
```
1. Connect monitor + keyboard to Zimaboard
2. Login at console (root + password)
3. Check network: ip addr show
4. Reconfigure if needed
```

### Option 2: Reinstall with Different Settings
```
1. Boot installer again
2. Try different network interface (eth1 instead of eth0)
3. Or use DHCP first, then change to static later
```

### Option 3: Router DHCP Reservation
```bash
# On router, create static DHCP lease
ssh root@192.168.8.1

uci add dhcp host
uci set dhcp.@host[-1].name='proxmox-zima'
uci set dhcp.@host[-1].mac='[ZIMABOARD_MAC]'
uci set dhcp.@host[-1].ip='192.168.8.21'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

---

## 📞 Quick Checks (30 Second Version)

```bash
# 1. Physical
Look at ethernet ports → link lights on?

# 2. From router
ssh root@192.168.8.1
ping 192.168.8.21

# 3. Reseat cable
Unplug, wait 5 sec, replug

# 4. Try different port
Move cable to eth1 on Zimaboard

# 5. Continue installation
Network will be configured at end
```

---

**Status:** Troubleshooting network drop during installation
**Next:** Verify connectivity after installation completes
**Network:** 192.168.8.21/24 via 192.168.8.1 (Claude-Slate)
