#!/usr/bin/env python3
import sys
import time
import fcntl
import array
import subprocess
import os
import re
import glob

LOCK_FILE = f"/run/user/{os.getuid()}/waybar_pinned"
PID_FILE = f"/run/user/{os.getuid()}/waybar_watcher.pid"

# Check if pinned
if os.path.exists(LOCK_FILE):
    sys.exit(0)

# Check if another watcher is already running
if os.path.exists(PID_FILE):
    try:
        with open(PID_FILE, "r") as f:
            old_pid = int(f.read().strip())
        # Check if still running
        os.kill(old_pid, 0)
        # Old watcher is still active, don't run duplicate
        sys.exit(0)
    except Exception:
        pass

# Write current PID
try:
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
except Exception:
    pass

# Dynamically discover all keyboard event nodes
def get_keyboard_fds():
    devs = set()
    try:
        with open("/proc/bus/input/devices", "r") as f:
            content = f.read()
        for section in content.split("\n\n"):
            if "Handlers=" in section and ("kbd" in section or "sysrq" in section):
                for ev in re.findall(r"event\d+", section):
                    devs.add(ev)
    except Exception:
        pass

    for p in glob.glob("/dev/input/by-path/*-event-kbd"):
        try:
            devs.add(os.path.basename(os.path.realpath(p)))
        except Exception:
            pass

    # Fallback to scanning standard event nodes if none found
    if not devs:
        devs = [os.path.basename(p) for p in glob.glob("/dev/input/event*")]

    fds = []
    buf = array.array("B", [0] * 64)
    for ev in sorted(devs):
        path = f"/dev/input/{ev}"
        try:
            fd = open(path, "rb")
            fcntl.ioctl(fd, 0x80404518, buf)
            fds.append(fd)
        except Exception:
            pass
    return fds

fds = get_keyboard_fds()
if not fds:
    sys.exit(0)

def is_key_down(key_code):
    byte_idx = key_code // 8
    bit_mask = 1 << (key_code % 8)
    for fd in fds:
        buf = array.array("B", [0] * 64)
        try:
            # EVIOCGKEY ioctl query
            fcntl.ioctl(fd, 0x80404518, buf)
            if buf[byte_idx] & bit_mask:
                return True
        except Exception:
            pass
    return False

try:
    # Give a short grace period (60ms) for keys to be recorded
    time.sleep(0.06)

    # Loop while BOTH Super and secondary key (Shift or Alt) are held down
    # Left Shift: 42, Right Shift: 54
    # Left Alt: 56, Right Alt: 100
    # Left Super: 125, Right Super: 126
    while True:
        super_down = is_key_down(125) or is_key_down(126)
        shift_down = is_key_down(42) or is_key_down(54)
        alt_down = is_key_down(56) or is_key_down(100)
        secondary_down = shift_down or alt_down

        # If either key is released, break immediately
        if not (super_down and secondary_down):
            break

        if os.path.exists(LOCK_FILE):
            break

        time.sleep(0.03)

finally:
    for fd in fds:
        try:
            fd.close()
        except Exception:
            pass
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

# Trigger hide if not pinned
if not os.path.exists(LOCK_FILE):
    subprocess.run(["/home/safvan/.config/waybar/peek.sh", "hide"])
