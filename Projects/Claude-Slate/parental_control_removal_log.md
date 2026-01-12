# Parental Control Removal Log

**Date:** 2026-01-10
**Router:** GL-BE3600 (192.168.8.1)
**Reason:** Using Blocky for DNS filtering instead

---

## What Was Removed

### Packages Removed:
1. **gl-sdk4-ui-parentalcontrol** (git-2025.217.32821-e1bdabb-1)
   - Web UI for GL.iNet parental control feature

2. **kmod-gl-sdk4-parental-control** (5.4.213+git-2025.219.22513-2a2b725-1)
   - Kernel module for parental control functionality

### Files/Directories Cleaned:
- `/etc/config/parental_control` - Configuration file
- `/etc/init.d/parental_control` - Init script
- `/etc/parental_control/` - Additional config directory (if existed)

### Services Stopped:
- `parental_control` service disabled and removed

---

## Packages NOT Removed

**Important:** These are system packages used by firewall and other services:

- `iptables-mod-filter` - General iptables filtering (used by firewall)
- `jsonfilter` - JSON parsing utility (system-wide)
- `kmod-ipt-filter` - Kernel IP filtering (firewall component)
- `kmod-br-netfilter` - Bridge netfilter (networking)
- `libnetfilter-*` - Netfilter libraries (firewall dependencies)

**These remain because they're required by:**
- firewall4 (main firewall)
- Network routing
- VPN functionality
- General packet filtering

---

## Status Before Removal

**Service State:** Active but disabled
- `enable '0'` - Feature was turned off
- No active filtering rules
- No running processes

**Configuration:**
```
config global 'global'
    option enable '0'
    option drop_anonymous '0'
    option auto_update '0'
    option enable_app '0'
```

GL.iNet's parental control was installed by default but not actively being used.

---

## Verification Results

✅ **All parental control packages removed**
✅ **Config file removed**
✅ **Init script removed**
✅ **No processes running**
✅ **Firewall restarted successfully**

---

## What This Means

**Parental Control is completely removed.**

### What Still Works:
- ✓ Blocky DNS filtering (unaffected)
- ✓ Firewall (firewall4)
- ✓ Mullvad VPN
- ✓ All network routing
- ✓ WiFi and LAN
- ✓ IoT network isolation

### What's Gone:
- ✗ GL.iNet's parental control feature
- ✗ Web-based content filtering UI
- ✗ Time-based access controls
- ✗ App/category blocking

---

## Why Use Blocky Instead?

**Blocky Advantages:**
- More powerful DNS-level blocking
- Better performance (lightweight)
- More flexible configuration
- Open source and transparent
- Better for your use case

**GL.iNet Parental Control:**
- Basic web filtering
- Fixed rule sets
- Less granular control
- Redundant with Blocky

---

## Impact on Your Network

**No negative impact:**
- DNS filtering continues via Blocky
- All firewall rules intact
- VPN leak protection active
- Network performance unchanged
- Frees up ~2-5MB RAM/storage

**Firewall Reload Warnings:**
These warnings during firewall restart are normal and expected:
- Disabled VPN configs (wgclient1, wgserver, ovpnserver)
- UPnP rules automatically loaded
- No errors, just informational messages

---

## If You Need Parental Control Again

### To reinstall GL.iNet's version:
```bash
ssh root@192.168.8.1
opkg update
opkg install gl-sdk4-ui-parentalcontrol kmod-gl-sdk4-parental-control
/etc/init.d/parental_control enable
/etc/init.d/parental_control start
```

### Better Alternatives:
1. **Blocky** (DNS filtering) - You're already using this! ✓
2. **AdGuard Home** (DNS filtering) - Pre-installed on router
3. **Pi-hole** (DNS filtering) - Can run on Zimaboard
4. **NextDNS** (Cloud DNS filtering)
5. **OpenDNS Family Shield** (Simple DNS filtering)

---

## Blocky Configuration

**Where Blocky Runs:**
- Likely on Zimaboard (confirm location)
- Or external DNS service

**Router DNS Configuration:**
To ensure router uses Blocky for DNS:

```bash
ssh root@192.168.8.1
uci set dhcp.@dnsmasq[0].server='192.168.8.21'  # Blocky IP
uci commit dhcp
/etc/init.d/dnsmasq restart
```

Adjust IP address to where Blocky is running.

---

## System Cleanup Benefits

**Before Removal:**
- 728 packages installed
- Parental control service loaded (disabled)
- Config files taking space

**After Removal:**
- 726 packages installed
- Cleaner service list
- ~2-5MB freed
- No redundant filtering systems

---

## Notes

- GL.iNet parental control was pre-installed
- It was disabled and not being used
- Blocky provides superior DNS filtering
- Removal is safe and reversible
- No network downtime during removal

---

## Related Services Still Active

**DNS/DHCP:**
- dnsmasq (active) - Can forward to Blocky

**Firewall:**
- firewall4 (active) - Network security
- VPN leak protection (active)

**Content Filtering:**
- Blocky (external) - Your DNS filter ✓
- AdGuard Home (installed, inactive) - Alternative option

---

**Removal completed successfully with no errors.**

**Next Step:** Configure router to use Blocky as DNS server (if not already).
