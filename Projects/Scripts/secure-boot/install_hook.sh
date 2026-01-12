#!/bin/bash
# Install the pacman hook for automatic kernel signing
sudo cp /home/mischa/sbctl-pacman-hook.hook /etc/pacman.d/hooks/95-sbctl.hook
sudo chmod 644 /etc/pacman.d/hooks/95-sbctl.hook
echo "✓ Pacman hook installed at /etc/pacman.d/hooks/95-sbctl.hook"
echo "Future kernel updates will be automatically signed!"
