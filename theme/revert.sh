#!/bin/bash
# Go back to Ubuntu's default boot splash (bgrt, with the vendor logo).
set -euo pipefail
if [ "$(id -u)" -ne 0 ]; then exec sudo "$0" "$@"; fi
update-alternatives --remove default.plymouth /usr/share/plymouth/themes/earth-dots/earth-dots.plymouth || true
update-alternatives --auto default.plymouth
rm -rf /usr/share/plymouth/themes/earth-dots
update-initramfs -u
echo "Reverted. Default theme is now: $(readlink -f /etc/alternatives/default.plymouth)"
