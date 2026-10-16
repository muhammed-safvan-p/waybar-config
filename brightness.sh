#!/usr/bin/env bash

DEVICE="intel_backlight"
DIR="/sys/class/backlight/$DEVICE"

if [ ! -d "$DIR" ]; then
    # Fallback to check if any other backlight device exists
    DEVICE=$(ls /sys/class/backlight/ | head -n 1)
    DIR="/sys/class/backlight/$DEVICE"
fi

if [ -z "$DEVICE" ] || [ ! -d "$DIR" ]; then
    echo "No backlight device found."
    exit 1
fi

CURR=$(cat "$DIR/brightness")
MAX=$(cat "$DIR/max_brightness")

# 5% step size
STEP=$(( MAX / 20 ))
if [ "$STEP" -lt 1 ]; then
    STEP=1
fi

ACTION="$1"

if [ "$ACTION" = "up" ]; then
    NEW=$(( CURR + STEP ))
    if [ "$NEW" -gt "$MAX" ]; then
        NEW="$MAX"
    fi
elif [ "$ACTION" = "down" ]; then
    NEW=$(( CURR - STEP ))
    if [ "$NEW" -lt 0 ]; then
        NEW=0
    fi
else
    echo "Usage: $0 {up|down}"
    exit 1
fi

busctl call org.freedesktop.login1 /org/freedesktop/login1/session/auto org.freedesktop.login1.Session SetBrightness ssu "backlight" "$DEVICE" "$NEW"
