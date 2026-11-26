#!/bin/bash
# Show the installed default splash for ~20 s, straight from the GNOME desktop.
# Switches to spare console tty3 by itself (no Ctrl+Alt+F3 needed) and always
# switches back to the desktop at the end, even if something goes wrong.
set -u
if [ "$(id -u)" -ne 0 ]; then exec sudo "$0" "$@"; fi

# plymouthd skips udev (and so picks the wrong GPU, card0) when it sees a
# desktop display, so hide the desktop's display variables from it.
unset DISPLAY WAYLAND_DISPLAY XAUTHORITY

LOG=/tmp/plymouth-test.log
TEST_VT=3
BACK_VT=$(sed 's/^tty//' /sys/class/tty/tty0/active)   # your desktop's console

cleanup() {
    plymouth --quit 2>/dev/null
    pkill -x plymouthd 2>/dev/null
    chvt "$BACK_VT"
}
trap cleanup EXIT

echo "Switching to console $TEST_VT in 3 s. You'll be back on the desktop after ~20 s."
sleep 3
chvt "$TEST_VT"
sleep 1

rm -f "$LOG"
plymouthd --debug --debug-file="$LOG" --tty="/dev/tty$TEST_VT" || { echo "plymouthd failed to start"; exit 1; }
plymouth --show-splash
sleep 8
plymouth display-message --text="Starting up, set in Inter"
sleep 5
plymouth hide-message --text="Starting up, set in Inter"
# Password prompt: type something and press Enter (gives up after 10 s)
timeout 10 plymouth ask-for-password --prompt="Test prompt: type anything, then Enter" >/dev/null 2>&1
sleep 2

cleanup
trap - EXIT
echo
echo "Finished. Script/theme problems found in the log, if any:"
grep -i -E 'script|parse|error|fail' "$LOG" | grep -v -i -E 'loading|ply-image' | tail -20
echo "Renderer used:"
grep -E 'udev|Opening .*/dev/dri|no pixel displays|adding .* pixel display|Could not initialize heads' "$LOG" | cut -c14-200 | head -10
cp "$LOG" "$(dirname "$0")/plymouth-test.log" && chmod 644 "$(dirname "$0")/plymouth-test.log"
echo "(Full log: $LOG, copy next to this script)"
