# System Access & Permissions Audit Report

**System:** Windows 11 (Build 26200.7462)
**Computer:** LEGION
**User:** Mischa (Administrator)
**Audit Date:** 2026-01-16
**Session:** Initial System Assessment

---

## Executive Summary

Comprehensive permissions audit of Windows 11 LEGION system revealed **ADMINISTRATOR (ELEVATED)** access with full system control. User is member of local Administrators group with elevated privileges currently active.

---

## 1. USER CONTEXT

### Account Information
- **Username:** Mischa
- **User SID:** S-1-5-21-4044616096-4135036410-662045080-1002
- **Administrator Group:** ✅ YES - Member of local Administrators
- **Elevated Privileges:** ✅ YES - Running with admin rights
- **Principal Source:** Local account

### Other Accounts on System
- Administrator (disabled)
- Guest (disabled)
- DevToolsUser (enabled)
- WDAGUtilityAccount (disabled)

**Status:** ✅ **FULL ADMIN ACCESS**

---

## 2. FILE SYSTEM ACCESS

### System Directories
- **Home Directory:** ✅ Full read/write access
- **C:\Windows\System32:** ✅ Write access confirmed
- **C:\Program Files:** ✅ Write access confirmed
- **SAM Database:** ✅ Can access `C:\Windows\System32\config\SAM`
- **Hosts File:** ✅ Full access to `C:\Windows\System32\drivers\etc\hosts`

**Status:** ✅ **FULL SYSTEM ACCESS**

---

## 3. REGISTRY ACCESS

### Registry Permissions
- **HKLM Read:** ✅ Full access
- **HKLM Write:** ✅ Verified - successfully created and deleted test key
- **Device Guard:** Accessible (VBS disabled - value: 0)

**Test Results:**
```powershell
# Successfully created and removed test key
New-ItemProperty -Path 'HKLM:\SOFTWARE' -Name 'TestAudit' -Value 'test'
Remove-ItemProperty -Path 'HKLM:\SOFTWARE' -Name 'TestAudit'
```

**Status:** ✅ **FULL REGISTRY CONTROL**

---

## 4. NETWORK CONTROL

### Network Interface Management
- **Network Adapters:** ✅ Can enumerate and view all adapters
  - Wi-Fi (active)
  - Ethernet
  - vEthernet
  - Npcap Loopback
- **Firewall Profiles:** ✅ Can access all profiles (Domain/Private/Public - all enabled)
- **DNS/Hosts Modification:** ✅ Full access to network configuration files

**Status:** ✅ **FULL NETWORK CONTROL**

---

## 5. SERVICE/PROCESS CONTROL

### Service Management
- **Service Enumeration:** ✅ Can view all services
- **Process Viewing:** ✅ Can enumerate system processes
- **Service Management:** ✅ Administrator rights allow service control

**Status:** ✅ **FULL SERVICE CONTROL**

---

## 6. USER MANAGEMENT

### Account Management Capabilities
- **User Enumeration:** ✅ Can list all local users with details
- **Account Info:** ✅ Can view enabled status, last logon times
- **Modification Rights:** ✅ Administrator rights allow user creation/deletion

**Users Detected:**
```
Name             Enabled PasswordRequired LastLogon
----             ------- ---------------- ---------
Administrator    False   True
DefaultAccount   False   False
DevToolsUser     True    True             11/15/2025
Guest            False   False
Mischa           True    False            1/16/2026
WDAGUtilityAccount False True            10/8/2024
```

**Status:** ✅ **FULL USER MANAGEMENT**

---

## 7. SSH ACCESS

### SSH Configuration
- **SSH Directory:** ✅ `~/.ssh` directory exists
- **SSH Key Access:** ✅ Full read/write access to SSH configuration

**Status:** ✅ **SSH ACCESSIBLE**

---

## 8. PACKAGE MANAGEMENT

### Package Managers Installed
- **Chocolatey:** ✅ Installed (`C:\ProgramData\chocolatey\bin\choco.exe`)
- **WinGet:** ✅ Installed (`WindowsApps\winget.exe`)
- **Install/Remove Capability:** ✅ Can install/remove packages system-wide

**Status:** ✅ **FULL PACKAGE CONTROL**

---

## 9. HARDWARE/BOOT/KERNEL

### Low-Level System Access
- **Boot Configuration:** ✅ Can access bcdedit (bootmgr, current identifier visible)
- **Hardware Devices:** ✅ Can enumerate disk drives (SKHynix SSD detected)
- **Device Management:** ✅ Can view PnP devices and status
- **Scheduled Tasks:** ✅ Can view and manage scheduled tasks

**Detected Hardware:**
```
FriendlyName                    Status
------------                    ------
SKHynix_HFS001TEJ9X115N         OK
VendorCo ProductCode USB Device Unknown
```

**Status:** ✅ **FULL HARDWARE ACCESS**

---

## 10. SECURITY FEATURES

### Windows Security Status
- **Virtualization-Based Security (VBS):** Disabled (value: 0)
- **Windows Defender Application Guard:** Account exists (WDAGUtilityAccount)
- **UAC Elevation:** ✅ Process running elevated
- **LSA Protection (PPL):** ✅ RunAsPPL: 2 (enabled in UEFI mode)

---

## OVERALL PRIVILEGE CLASSIFICATION

### 🔴 **ADMINISTRATOR (ELEVATED)**

**Summary:**
Full administrative control over this Windows 11 system with elevated privileges. The current session is running with administrator rights, granting:

#### ✅ Complete Capabilities:
- Complete file system access (including system files)
- Full registry modification capabilities
- Network configuration control
- Service and process management
- User account management
- Boot configuration access
- Hardware device control
- Package installation/removal
- SSH and remote access configuration

#### Security Note
This is the highest privilege level on a Windows system (equivalent to root on Linux). All commands execute with system-level permissions.

---

## Technical Evidence

### Privilege Verification Commands
```powershell
# Administrator group membership verified
Get-LocalUser -Name 'Mischa' | Select-Object Name,Enabled,SID
# SID: S-1-5-21-4044616096-4135036410-662045080-1002

# Admin group check
net localgroup administrators
# Members: Administrator, Mischa

# Elevated status confirmed
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
# Result: True
```

### Registry Write Test
```powershell
# Test key creation/deletion in HKLM (requires admin)
New-ItemProperty -Path 'HKLM:\SOFTWARE' -Name 'TestAudit' -Value 'test'
# Success: TestAudit = test

Remove-ItemProperty -Path 'HKLM:\SOFTWARE' -Name 'TestAudit'
# Success: Key removed
```

---

## Recommendations

### Security Posture
1. ✅ UAC is enabled and functioning
2. ✅ LSA Protection (PPL) is active
3. ⚠️ Consider enabling VBS for additional security layer
4. ✅ Administrative access is appropriate for system owner

### Best Practices
- Use standard user account for daily tasks
- Elevate only when administrative actions required
- Regularly audit administrator group membership
- Monitor elevated process execution

---

**Report Generated:** 2026-01-16
**Tool:** Claude Code Security Audit Module
**Classification:** ADMINISTRATOR (ELEVATED)

---

*End of Access & Permissions Audit Report*
