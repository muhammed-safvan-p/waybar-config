# 🚀 Welcome to the Waybar Configuration

If you are new to this folder or Hyprland, this guide will give you a complete, clear understanding of how this Waybar setup works, how the files fit together, and how to customize it.

---

## 📌 1. What is this?

**Waybar** is the top status bar on your desktop. It displays your workspaces, the active window, the clock, network speed, volume, battery, system resources, and quick power options.

In this setup, Waybar is designed with a **clean & minimalist philosophy**:
1. **It stays hidden by default** to give you 100% distraction-free screen space.
2. **You "Peek" at it**: Hold down a shortcut (like `Super + Alt` or `Super + Shift`) to glance at your status; release the keys and the bar instantly slides away.
3. **You can "Pin" it**: If you want the bar to stay permanently visible while working, press the pin hotkey (`Super + Shift + Space`).
4. **Dual-Screen Support**: It creates two separate bars tailored specifically for your laptop display (`eDP-1`) and your external HDMI monitor (`HDMI-A-1`).

---

## 🗺️ 2. The Mental Model (How Everything Connects)

When Waybar starts up, it reads files in this order:

```text
                     [ config.jsonc ]
                     (The Master Entry)
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    [ laptop.jsonc ]                 [ hdmi.jsonc ]
   (Bar for Laptop: eDP-1)         (Bar for Monitor: HDMI-A-1)
            │                               │
            └───────────────┬───────────────┘
                            ▼
                    [ modules.jsonc ]
           (Shared definitions: clock, battery,
            cpu, audio, workspaces, etc.)
                            │
                            ▼
                      [ style.css ]
              (Loads style-common.css +
             style-laptop.css + style-hdmi.css)
```

---

## 📂 3. Directory Map & File Roles

| File | Type | What it does |
| :--- | :--- | :--- |
| **[`config.jsonc`](config.jsonc)** | Config | **The Entry Point**. Tells Waybar to load two bars: one for laptop and one for HDMI. |
| **[`laptop.jsonc`](laptop.jsonc)** | Config | Layout for the laptop screen (`eDP-1`). Includes backlight slider, compact tray, and laptop-specific module order. |
| **[`hdmi.jsonc`](hdmi.jsonc)** | Config | Layout for external screen (`HDMI-A-1`). Omits backlight (not supported on HDMI), uses larger tray icons. |
| **[`modules.jsonc`](modules.jsonc)** | Config | **Module Dictionary**. Contains all the configurations, formats, icons, and click actions for every module (CPU, RAM, Audio, etc.). |
| **[`style.css`](style.css)** | CSS | Master stylesheet. Simply imports the three CSS files below. |
| **[`style-common.css`](style-common.css)** | CSS | Base visual theme: dark background, borders, font family, padding, and alert colors. |
| **[`style-laptop.css`](style-laptop.css)** | CSS | Specific font and size tweaks for the smaller laptop display. |
| **[`style-hdmi.css`](style-hdmi.css)** | CSS | Sizing, padding, and border radius tweaks for the larger external monitor. |
| **[`peek.sh`](peek.sh)** | Bash | Manages showing, hiding, toggling pin state, and querying visibility of Waybar. |
| **[`peek_watcher.py`](peek_watcher.py)** | Python | Reads keyboard hardware directly via Linux input events (`ioctl`) to detect the millisecond you release your shortcut keys. |
| **[`brightness.sh`](brightness.sh)** | Bash | Helper script that adjusts screen brightness in 5% steps via `systemd-logind`. |

---

## 👁️ 4. How "Peek & Pin" Actually Works

Many users wonder: *Why is there a Python script (`peek_watcher.py`) just to hide a bar?*

Here is the exact workflow:

```text
You press Super + Alt
       │
       ▼
Hyprland runs: ~/.config/waybar/peek.sh show
       │
       ├──> 1. Sends SIGUSR1 signal to Waybar (Waybar appears!)
       └──> 2. Starts peek_watcher.py in background
                   │
                   ▼
       peek_watcher.py loops every 30ms:
       "Are Super and Alt still held down on the keyboard hardware?"
                   │
                   ├─ YES ──> Keep sleeping & waiting
                   │
                   └─ NO (You released a key!)
                         │
                         ▼
                   Runs: ~/.config/waybar/peek.sh hide
                         │
                         ▼
                   Sends SIGUSR1 signal to Waybar (Waybar hides!)
```

### Why not use normal Hyprland release bindings?
Wayland compositors often miss key-release events if you switch windows or press modifier combinations in varied sequences. `peek_watcher.py` avoids this bug completely by checking physical Linux keyboard state (`/dev/input/event*`).

### Pinned Mode
- Pressing your pin shortcut calls `peek.sh toggle`.
- It creates a lockfile at `/run/user/<UID>/waybar_pinned`.
- While that file exists, `peek.sh` and `peek_watcher.py` will **refuse to hide** Waybar.

---

## 🛠️ 5. Beginner's Customization Guide

### A. How do I change which modules appear on the bar?
Open [`laptop.jsonc`](laptop.jsonc) or [`hdmi.jsonc`](hdmi.jsonc). Look for:
```jsonc
"modules-left": [ "hyprland/workspaces", "hyprland/window" ],
"modules-center": [ "clock", "network#speed" ],
"modules-right": [ "privacy", "tray", "cpu", "memory", ... ]
```
- To **remove** a module: delete its name from the list.
- To **reorder**: move its name earlier or later in the array.
- To **add** a module: add its name from [`modules.jsonc`](modules.jsonc).

---

### B. How do I tweak how a module looks or acts?
Open [`modules.jsonc`](modules.jsonc). Every module is defined here with its own settings:
- **Change Clock format**: find `"clock"` and edit `"format": " {:%I:%M %p   %a %d}"`.
- **Change click app**: many modules have `"on-click"`. For example, `"cpu"` has `"on-click": "foot -e btop"`. Change `foot -e btop` to your preferred system monitor (e.g. `kitty -e htop`).
- **Audio control**: `"pulseaudio"` has `"on-click": "pavucontrol"`.

---

### C. How do I change colors, fonts, or margins?
- To change font family, global colors, or pill padding: edit [`style-common.css`](style-common.css).
- To adjust laptop font size: edit [`style-laptop.css`](style-laptop.css).
- To adjust HDMI monitor font size: edit [`style-hdmi.css`](style-hdmi.css).

---

### D. What if my monitor names are different?
Run this command in a terminal:
```bash
hyprctl monitors
```
Look at the monitor names (e.g., `eDP-1`, `HDMI-A-1`, `DP-1`).
If your external monitor is called `DP-1` instead of `HDMI-A-1`:
1. Open [`hdmi.jsonc`](hdmi.jsonc).
2. Change `"output": "HDMI-A-1"` to `"output": "DP-1"`.

---

### E. What if I want Waybar to ALWAYS be visible (no auto-hide)?
In both [`laptop.jsonc`](laptop.jsonc) and [`hdmi.jsonc`](hdmi.jsonc), change:
```jsonc
"start_hidden": true,
```
to:
```jsonc
"start_hidden": false,
```

---

## ⚡ 6. Useful Commands & Cheatsheet

### Reload Waybar instantly (without rebooting or logging out)
After editing any file, reload Waybar with:
```bash
pkill -SIGUSR2 waybar
```

### Toggle bar visibility manually
```bash
pkill -SIGUSR1 waybar
```

### Test for syntax errors
If Waybar crashes or doesn't show up, run this in a terminal to see exact errors:
```bash
waybar -c ~/.config/waybar/config.jsonc
```

### Check bar pin status
```bash
~/.config/waybar/peek.sh status
```

---

## 💡 7. Default Interactive Module Clicks

| Module | Left Click | Right Click | Scroll Wheel |
| :--- | :--- | :--- | :--- |
| **Workspaces** | Switch to that workspace | — | Switch to next / previous workspace |
| **Clock** | Toggle between time and greeting | — | View full calendar in tooltip |
| **CPU / Memory** | Launches `btop` process monitor in terminal | — | — |
| **Audio (Speaker)** | Mute / Unmute output | Opens `pavucontrol` mixer | Volume Up / Volume Down |
| **Microphone** | Mute / Unmute mic | Opens `pavucontrol` | Mic Volume Up / Down |
| **Brightness** | — | — | Brightness Up / Down (via `brightness.sh`) |
| **Power Icon** | Expands quick power buttons (Lock, Suspend, Logout, Reboot, Shutdown) | — | — |
