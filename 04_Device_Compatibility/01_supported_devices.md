# Supported Devices

## 1 Purpose

This document lists the devices supported by the debloating system and the compatibility decision rules.

## 2 Supported Devices (Verified)

| Device Family | Models | OS | ADB | Package Evidence |
|---------------|--------|----|-----|------------------|
| Samsung Galaxy Watch | Watch 4, Watch 4 Classic | Wear OS 3 | Wi-Fi + USB cradle | GW4 dump (143 pkgs, `UNKNOWN`) |
| Samsung Galaxy Watch | Watch 6, Watch 6 Classic, Watch 7, Watch 7 Classic | Wear OS 4/5 | Wi-Fi + USB cradle | GW6/7 debloat thread |
| Samsung Galaxy Watch | Watch 8 (SM-L330) | Wear OS 6 | Wi-Fi + USB cradle | No package evidence yet (guard profile) |
| Google Pixel Watch | Pixel Watch, Pixel Watch 2, Pixel Watch 3 | Wear OS 3/4/5 | Wi-Fi + USB cradle | Google core packages only |
| Google Pixel Watch | Pixel Watch 4, Pixel Watch 5 | Wear OS 6 | Wi-Fi + USB cradle | Google core packages only |
| Suunto | Suunto 7 | Wear OS 2 | Wi-Fi (legacy) | Not verified |
| Xiaomi | Watch 2, Watch 2 Pro | Wear OS 3.x | Wi-Fi + USB cradle | Not verified |

## 3 Compatibility Decision Rules

Reference: `03_Platform_Architecture/03_platform_compatibility_matrix.md` rules DR-01 to DR-09.

| Rule | Condition | Action |
|------|-----------|--------|
| DR-01 | Platform is Wear OS 3+ | Supported — full ADB + pm operations |
| DR-02 | Platform is Wear OS 2 | Supported — legacy ADB flow, no verified packages |
| DR-03 | Platform is Samsung Tizen | Not supported — sdb only, no pm |
| DR-04 | Platform is watchOS | Not supported — UI deletion only |
| DR-05 | Platform is Garmin/Zepp/LiteOS/Fitbit | Not supported — no ADB, no pm |
| DR-06 | Platform is unknown Android-based | Unknown — require package dump first |
| DR-07 | ADB not available on device | Not supported — cannot enumerate |
| DR-08 | Package names not verified | Unknown — classifications not applied |
| DR-09 | Device requires root for pm operations | Not supported — no root in this system |

## 4 Device Identification

See `05_Device_Identification/01_device_identification.md`.

## 5 Unknown Platforms

Devices not listed above must be investigated before use. Run `python 14_Automation_and_Scripting/tools/sw.py identify` to get the device identity and SDK. If the device reports an Android SDK and `pm list packages` works, the device may be compatible but package classifications will be `UNKNOWN` until a verified dump exists.

## 6 Refusal Behaviour

The tool refuses to operate on:
- Non-Android platforms (no ADB, no pm)
- Devices with no verified package evidence for the target operation
- Multiple connected devices (set `SW_SERIAL` to disambiguate)
- A device that does not match the profile `device_match` or `software_scope`
