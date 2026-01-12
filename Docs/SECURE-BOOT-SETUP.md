# Secure Boot Setup for rEFInd + CachyOS

**Date:** 2026-01-09
**System:** Lenovo Legion Pro 7
**Bootloader:** rEFInd with shim
**OS:** CachyOS (Arch-based) + Windows dual-boot

## Overview

Successfully configured Secure Boot for rEFInd bootloader with CachyOS Linux. The setup uses:
- **sbctl** - Simple Secure Boot key management tool
- **shim** - Pre-installed bootloader for Secure Boot
- **MOK Manager** - Machine Owner Key management

## What Was Done

### 1. Entered Setup Mode
- Booted into UEFI/BIOS firmware
- Cleared existing Secure Boot keys to enter Setup Mode
- This allows enrolling custom keys

### 2. Created and Enrolled Keys
```bash
sudo sbctl create-keys              # Generated custom Secure Boot keys
sudo sbctl enroll-keys -m           # Enrolled keys + Microsoft vendor keys
```

**Owner UUID:** `3fd20435-b8e4-4665-8552-62463e9032b5`

The `-m` flag includes Microsoft's keys for Windows compatibility.

### 3. Signed Bootloader Files
```bash
sudo sbctl sign -s /boot/EFI/refind/shimx64.efi
sudo sbctl sign -s /boot/EFI/refind/mmx64.efi
```

### 4. Signed Kernel Files
```bash
sudo sbctl sign -s /boot/vmlinuz-linux-cachyos
sudo sbctl sign -s /boot/vmlinuz-linux-cachyos-lts
```

### 5. Installed Automatic Signing Hook
Created pacman hook at `/etc/pacman.d/hooks/95-sbctl.hook` to automatically sign kernels during updates.

## Verification

After setup, before enabling in BIOS:
```bash
sudo sbctl status
```

Output:
```
Installed:    ✓ sbctl is installed
Owner GUID:   3fd20435-b8e4-4665-8552-62463e9032b5
Setup Mode:   ✓ Disabled
Secure Boot:  ✗ Disabled
Vendor Keys:  microsoft
```

All 4 files signed:
```bash
sudo sbctl list-files
```

## Enabling Secure Boot in Firmware

**Next Steps (to be performed):**
1. Reboot system
2. Enter BIOS/UEFI (F2 or Fn+F2)
3. Navigate to Security → Secure Boot
4. Enable Secure Boot
5. Verify mode shows "User Mode" (not "Setup Mode")
6. Save and exit

## Post-Enable Verification

After rebooting with Secure Boot enabled:
```bash
sudo sbctl status
# Should show: Secure Boot: ✓ Enabled

bootctl status
# Should show: Secure Boot: enabled (user)
```

## Compatibility

### ✅ Works With:
- **CachyOS kernels** - Signed with custom keys
- **Windows** - Microsoft vendor keys enrolled
- **rEFInd bootloader** - Using shim for Secure Boot
- **Dual/Multi-boot** - All signed OSes will boot

### Future Kernel Updates:
Automatically signed by pacman hook - no manual intervention needed.

### Adding New Linux Distributions:
Sign their kernels:
```bash
sudo sbctl sign -s /boot/vmlinuz-<new-distro>
```

## Scripts

Setup scripts located in: `scripts/secure-boot/`

- `setup_secureboot_refind.sh` - Complete automated setup script
- `install_hook.sh` - Install pacman hook for auto-signing
- `sbctl-pacman-hook.hook` - Pacman hook configuration

## References

- [Arch Wiki: Secure Boot](https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface/Secure_Boot)
- [sbctl GitHub](https://github.com/Foxboron/sbctl)
- [rEFInd Secure Boot](https://www.rodsbooks.com/refind/secureboot.html)

## Status

- [x] Keys created
- [x] Keys enrolled
- [x] Bootloader signed
- [x] Kernels signed
- [x] Auto-signing hook installed
- [ ] Secure Boot enabled in firmware (pending reboot)
- [ ] Boot test with Secure Boot active
