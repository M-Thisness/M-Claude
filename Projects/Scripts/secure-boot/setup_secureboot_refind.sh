#!/bin/bash
# Secure Boot Setup Script for rEFInd + CachyOS
# Run this in your terminal where you can Touch_Key for sudo prompts

set -e  # Exit on error

echo "=========================================="
echo "rEFInd + CachyOS Secure Boot Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check current status
echo -e "${YELLOW}Step 1: Checking current Secure Boot status...${NC}"
sudo sbctl status
echo ""

# Step 2: Create keys if they don't exist
echo -e "${YELLOW}Step 2: Creating sbctl keys...${NC}"
if [ ! -d "/usr/share/secureboot/keys" ]; then
    echo "Creating new Secure Boot keys..."
    sudo sbctl create-keys
    echo -e "${GREEN}✓ Keys created${NC}"
else
    echo -e "${GREEN}✓ Keys already exist${NC}"
fi
echo ""

# Step 3: Enroll keys (you're in Setup Mode)
echo -e "${YELLOW}Step 3: Enrolling keys to firmware...${NC}"
echo "This will enroll your custom keys + Microsoft keys (for Windows compatibility)"
sudo sbctl enroll-keys -m
echo -e "${GREEN}✓ Keys enrolled${NC}"
echo ""

# Step 4: Sign bootloader files
echo -e "${YELLOW}Step 4: Signing bootloader files...${NC}"
sudo sbctl sign -s /boot/EFI/refind/shimx64.efi
sudo sbctl sign -s /boot/EFI/refind/mmx64.efi
echo -e "${GREEN}✓ Bootloader files signed${NC}"
echo ""

# Step 5: Sign kernels
echo -e "${YELLOW}Step 5: Signing kernel files...${NC}"
sudo sbctl sign -s /boot/vmlinuz-linux-cachyos
sudo sbctl sign -s /boot/vmlinuz-linux-cachyos-lts
echo -e "${GREEN}✓ Kernels signed${NC}"
echo ""

# Step 6: Verify all signatures
echo -e "${YELLOW}Step 6: Verifying all signatures...${NC}"
sudo sbctl verify
echo ""

# Step 7: Final status check
echo -e "${YELLOW}Step 7: Final status check...${NC}"
sudo sbctl status
echo ""

echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Reboot your system"
echo "2. Enter BIOS/UEFI (F2 or Fn+F2 on boot)"
echo "3. Navigate to Security > Secure Boot"
echo "4. Change from 'Setup Mode' to 'User Mode' or enable Secure Boot"
echo "5. Save and exit"
echo ""
echo "Your system will boot with Secure Boot enabled!"
echo "Windows dual-boot will continue working (Microsoft keys enrolled)"
echo ""
echo -e "${YELLOW}Note: If you add new kernels or update, sign them with:${NC}"
echo "sudo sbctl sign -s /boot/vmlinuz-<kernel-name>"
