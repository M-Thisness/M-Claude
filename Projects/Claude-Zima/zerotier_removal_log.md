# ZeroTier Removal Log

**Date:** 2026-01-10
**Router:** GL-BE3600 (192.168.8.1)

---

## What Was Removed

### Packages Removed:
1. **zerotier** (v1.14.1-1) - Main ZeroTier service
2. **gl-sdk4-zerotier** - GL.iNet ZeroTier integration
3. **gl-sdk4-ui-zerotierview** - GL.iNet ZeroTier web UI

### Files/Directories Cleaned:
- `/etc/config/zerotier` - Configuration file
- `/var/lib/zerotier-one` - Data directory
- `/etc/zerotier` - Additional config directory
- `/etc/init.d/zerotier` - Init script
- `/usr/bin/zerotier-cli` - Binary removed

---

## Status Before Removal

- **Service Status:** Not running
- **Networks Joined:** None
- **Location:** Router only (not on local machine)

---

## Verification

✅ All ZeroTier packages removed
✅ ZeroTier binary removed
✅ Configuration files removed
✅ Data directories removed

---

## What This Means

**ZeroTier is now completely removed from your router.**

- No ZeroTier processes running
- No configuration files remaining
- No packages to reinstall or clean up
- Router network functionality unchanged

---

## Impact on Your Network

**No impact:**
- Mullvad WireGuard VPN: Still active
- Router WiFi/LAN: Unchanged
- Static IP assignments: Unchanged
- IoT network isolation: Unchanged
- All router optimizations: Intact

**ZeroTier was:**
- Installed but not actively used
- Not connected to any networks
- Not providing any services

**After removal:**
- Slightly less memory/storage usage
- One less service in the package list
- Cleaner system

---

## If You Need ZeroTier Again

**To reinstall:**
```bash
ssh root@192.168.8.1
opkg update
opkg install zerotier
opkg install gl-sdk4-zerotier gl-sdk4-ui-zerotierview
```

**Or via web UI:**
- System → Software
- Update lists
- Search "zerotier"
- Install packages

---

## Notes

- ZeroTier was pre-installed by GL.iNet firmware
- It was never configured or used in your setup
- Removal is safe and reversible
- No network downtime during removal

---

**Removal completed successfully with no errors.**
