#!/bin/bash
# Install the "earth-dots" Plymouth theme and make it the default boot splash.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
THEMES=/usr/share/plymouth/themes
NEW="$THEMES/earth-dots/earth-dots.plymouth"
BACKUP=/etc/plymouth/default-theme.backup

if [ "$(id -u)" -ne 0 ]; then exec sudo "$0" "$@"; fi

echo "== Backing up the current default theme setting to $BACKUP"
if [ ! -e "$BACKUP" ]; then
    { echo "# Saved $(date -Is) before installing earth-dots"
      update-alternatives --query default.plymouth; } > "$BACKUP"
else
    echo "   (backup already exists, keeping the original one)"
fi

echo "== Copying theme to $THEMES/earth-dots"
rm -rf "$THEMES/earth-dots"
install -d -m 755 "$THEMES/earth-dots"
install -m 644 "$HERE"/earth-dots/* "$THEMES/earth-dots/"

echo "== Registering and selecting the theme"
update-alternatives --install "$THEMES/default.plymouth" default.plymouth "$NEW" 100
update-alternatives --set default.plymouth "$NEW"

echo "== Rebuilding the initramfs (this takes a minute)"
update-initramfs -u

echo
echo "Done. Default theme is now: $(readlink -f /etc/alternatives/default.plymouth)"
