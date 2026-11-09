# Device Identification

## 1 Purpose

This document describes how the system identifies a connected watch and maps it to a device profile.

## 2 Identification Procedure

Run `python 14_Automation_and_Scripting/tools/sw.py identify`. The tool queries the following `getprop` values:

| Property | Description | Example |
|----------|-------------|---------|
| `ro.product.brand` | Brand name | `Samsung` |
| `ro.product.model` | Marketing model | `SM-R870` |
| `ro.product.device` | Device codename | `one` |
| `ro.product.manufacturer` | Manufacturer | `Samsung` |
| `ro.build.version.release` | Android version | `14` |
| `ro.build.version.sdk` | API level (integer) | `34` |
| `ro.build.display.id` | Build fingerprint | `...` |
| `ro.build.version.incremental` | Incremental build | `...` |

## 3 Wear OS Label Mapping

The SDK integer maps to a Wear OS label:

| SDK | Label |
|-----|-------|
| 30 | Wear OS 3 (Android 11) |
| 33 | Wear OS 4 (Android 13) |
| 34 | Wear OS 5 (Android 14) |
| 35 | Wear OS 5.1 (Android 15) |
| 36 | Wear OS 6 (Android 16) |
| other | outside the verified mapping |

## 4 Profile Selection

The device identity and Wear OS label are used to select a profile from `13_Device_Specific_Profiles/`. The profile's `device_scope` and `software_scope` must match the detected device.

The tool enforces this rule in two places:

1. `swdb.py plan` skips an entry when its scope does not intersect the profile scope.
2. `sw.py apply` reads `ro.product.model` and `ro.product.device`, and refuses a device that matches no `device_match` prefix. It also refuses a Wear OS label that is not in `software_scope`.

The tool returns exit code 2 and changes nothing when the check fails. A named override, `SW_ALLOW_DEVICE_MISMATCH=1`, bypasses the check and prints a warning.

## 5 SW_SERIAL Override

When multiple devices are connected, set `SW_SERIAL` to the watch's ADB serial (from `adb devices`). The tool will use that device without prompting.

## 6 Limitations

- Pixel Watch 2/3 exact SoC and Wear OS version not verified
- Fossil Gen 5 individual package names not verified
- Device codenames may vary by region/carrier
