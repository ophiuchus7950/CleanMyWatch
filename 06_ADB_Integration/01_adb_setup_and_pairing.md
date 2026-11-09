# ADB Setup and Pairing

## 1 Purpose

This document describes how to enable ADB on a Wear OS watch and pair it with a computer.

## 2 Prerequisites

- ADB version 30.0.0 or newer (Android platform-tools)
- Watch and computer on the same Wi-Fi network
- Router AP/client isolation OFF (required for device discovery)

## 3 Enable Developer Options

### Samsung Galaxy Watch

1. Open Settings on the watch
2. Go to About watch → Software
3. Tap **Software version** 5 times
4. Developer options appear in Settings

### Google Pixel Watch

1. Open Settings on the watch
2. Go to System → About → Versions
3. Tap **Build number** 7 times
3. Developer options appear in Settings

## 4 Enable Wireless Debugging

1. Open Developer options on the watch
2. Enable **Wireless debugging**
3. The watch shows a pairing code and IP:port

## 5 Pair and Connect

```bash
# Pair (one-time, enter the pairing code from the watch)
adb pair <ip:port>

# Connect
adb connect <ip:port>

# Verify
adb devices
# Should show: <ip:port>    device
```

## 6 Battery Warning

Leaving wireless ADB enabled drains the watch battery significantly. Disable wireless debugging in Developer options when not actively debloating.

## 7 Known Issues

- **One UI 5 Watch** broke older sideload tools (Easy Fire Tools). The pairing code flow is mandatory on Wear OS 3+.
- **Wear OS 5.1 restriction claim** — not verified in this project. Do not assume wireless debugging is removed.
- **Legacy Wear OS 2** devices use a different developer options path and may not support pairing code flow.

## 8 USB Debugging Alternative

USB debugging is only available on watches with a data-capable charging cradle. Enable USB debugging in Developer options, connect the cradle to the computer, and run `adb devices`.

## 9 Verification

After pairing, run `python 14_Automation_and_Scripting/tools/sw.py identify` to confirm the tool can communicate with the watch and read its properties.
