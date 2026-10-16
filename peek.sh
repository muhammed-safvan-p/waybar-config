#!/usr/bin/env bash

# File used to mark when Waybar is permanently pinned/locked open
LOCK_FILE="/run/user/$(id -u)/waybar_pinned"

# Check if Waybar is currently visible on the top layer
is_visible() {
    hyprctl layers -j 2>/dev/null | jq -e '.[].levels["2"][]? | select(.namespace == "laptop-bar" or .namespace == "waybar" or .namespace == "hdmi-bar")' >/dev/null 2>&1
}

case "$1" in
    show)
        # Show on Super+Alt press only if not pinned
        if [ ! -f "$LOCK_FILE" ]; then
            if ! is_visible; then
                pkill -SIGUSR1 waybar
            fi
            # Spawn hardware key release watcher
            /home/safvan/.config/waybar/peek_watcher.py >/dev/null 2>&1 &
        fi
        ;;
    hide)
        # Hide on Super release only if not pinned
        if [ ! -f "$LOCK_FILE" ] && is_visible; then
            pkill -SIGUSR1 waybar
        fi
        ;;
    toggle)
        # Toggle pin mode with SUPER + SHIFT + Space
        if [ -f "$LOCK_FILE" ]; then
            rm -f "$LOCK_FILE"
            if is_visible; then
                pkill -SIGUSR1 waybar
            fi
        else
            touch "$LOCK_FILE"
            if ! is_visible; then
                pkill -SIGUSR1 waybar
            fi
        fi
        ;;
    status)
        if [ -f "$LOCK_FILE" ]; then
            echo "pinned"
        elif is_visible; then
            echo "visible"
        else
            echo "hidden"
        fi
        ;;
    *)
        echo "Usage: $0 {show|hide|toggle|status}"
        exit 1
        ;;
esac
