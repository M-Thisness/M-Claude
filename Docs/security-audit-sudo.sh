#!/bin/bash
# M-BOOK Security Audit - Privileged Commands
# Generated: 2026-01-15
# Updated: 2026-01-15 (v1.1 - Fixed Remote Management check)
# Purpose: Collect security data requiring elevated privileges
#
# SAFETY: This script only READS configuration - it does NOT modify settings
# All checks are non-destructive and read-only

echo "=============================================="
echo "  M-BOOK Security Audit - Privileged Scan"
echo "=============================================="
echo ""

# Validate sudo access
echo "[*] Validating sudo access..."
sudo -v || { echo "[-] Sudo authentication failed"; exit 1; }
echo "[+] Sudo access confirmed"
echo ""

# 1. Remote Login (SSH) Status
echo "=== Remote Login (SSH) Status ==="
sudo systemsetup -getremotelogin 2>&1
echo ""

# 2. Remote Apple Events Status
echo "=== Remote Apple Events Status ==="
sudo systemsetup -getremoteappleevents 2>&1
echo ""

# 3. Firewall Application Rules
echo "=== Firewall Application Rules ==="
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps 2>&1
echo ""

# 4. User Authentication Authority Details
echo "=== User Authentication Authority (m) ==="
sudo dscl . -read /Users/m AuthenticationAuthority 2>&1
echo ""

# 5. System Launch Daemons (Running)
echo "=== Running System Daemons ==="
sudo launchctl list 2>&1 | head -30
echo "... (truncated to 30 entries)"
echo ""

# 6. Detailed Firewall Preferences
echo "=== Firewall Preferences (ALF) ==="
sudo defaults read /Library/Preferences/com.apple.alf 2>&1
echo ""

# 7. Screen Sharing Status
echo "=== Screen Sharing Status ==="
sudo launchctl list | grep -i screensharing 2>&1
echo ""

# 8. Remote Management Status (READ-ONLY check)
echo "=== Remote Management Status ==="
# Check if ARDAgent is running without activating it
if pgrep -x "ARDAgent" > /dev/null 2>&1; then
    echo "Remote Management: ACTIVE (ARDAgent running)"
else
    echo "Remote Management: Off (ARDAgent not running)"
fi
# Check launchctl for ARD
sudo launchctl list | grep -i "RemoteManagement" 2>/dev/null || echo "No RemoteManagement services loaded"
echo ""

# 9. Printer Sharing Status
echo "=== Printer Sharing Status ==="
sudo cupsctl 2>&1 | grep -E "share|browsing"
echo ""

# 10. Sudo Configuration Check
echo "=== Sudo Configuration ==="
sudo cat /etc/sudoers.d/* 2>/dev/null | grep -v "^#" | grep -v "^$" || echo "No custom sudoers.d files"
echo ""

# 11. TCC Database (Privacy Permissions)
echo "=== TCC Privacy Permissions (Full Disk Access) ==="
sudo sqlite3 /Library/Application\ Support/com.apple.TCC/TCC.db "SELECT client,service,auth_value FROM access WHERE service='kTCCServiceSystemPolicyAllFiles'" 2>&1
echo ""

# 12. Secure Boot Policy
echo "=== Secure Boot Policy ==="
sudo bputil -d 2>&1 | head -10 || echo "bputil not available or requires recovery mode"
echo ""

echo "=============================================="
echo "  Privileged Scan Complete"
echo "=============================================="
