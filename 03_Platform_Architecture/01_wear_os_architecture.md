# Wear OS Architecture

## 1 Purpose

This document describes the Wear OS package architecture relevant to debloating operations.

## 2 Scope

Covers Wear OS 3 (Android 11/API 30) through Wear OS 6 (Android 16/API 36).

## 3 Package Model

Wear OS uses standard Android APK/APKS packages managed by the Android package manager (`pm`). Packages are installed from Google Play on the watch (`com.android.vending` present in verified dumps) or side-loaded via ADB.

## 4 Package Layers

| Layer | Description | Examples |
|-------|-------------|----------|
| AOSP core | Android framework packages | `android`, `com.android.bluetooth`, `com.android.phone`, `com.android.shell`, `com.android.vending` |
| Google Wear OS core | Google services for Wear OS | `com.google.android.gms`, `com.google.android.wearable.*`, `com.google.android.apps.wearable.*` |
| OEM system | Manufacturer pre-installed apps and services | `com.samsung.android.*`, `com.sec.*` |
| Third-party pre-installed | Partner apps installed by default | `com.microsoft.office.outlook` |

## 5 Play Store on Watch

- Wear APKs are uploaded independently in Play Console
- Must declare `<uses-feature android:name="android.hardware.type.watch" />`
- Standalone flag: `<meta-data android:name="com.google.android.wearable.standalone" android:value="true|false" />`
- Remote install from phone/desktop Play re-populates debloated surface

## 6 Samsung Official Removal Paths

- Galaxy Wearable app: Watch settings → Apps → Uninstall
- On-watch long-press → Uninstall (third-party pre-installs only)
- System pre-installs are NOT offered Uninstall
- Companion package: `com.samsung.android.app.watchmanager`

## 7 Android API to Wear OS Mapping

| Wear OS | Android | API Level |
|---------|---------|-----------|
| Wear OS 3 | Android 11 | 30 |
| Wear OS 4 | Android 13 | 33 |
| Wear OS 5 | Android 14 | 34 |
| Wear OS 5.1 | Android 15 | 35 |
| Wear OS 6 | Android 16 | 36 |

## 8 Verified Hardware

| Device | SoC | Storage | RAM | Wear OS |
|--------|-----|---------|-----|---------|
| Galaxy Watch 4 | Exynos W920 | 16 GB | 1.5 GB | 3 |
| Pixel Watch 1 | Exynos 9110 | 32 GB | 2 GB | 3 |
| Pixel Watch 4 | Snapdragon W5 Gen 2 | 32 GB | 2 GB | 6 |
| Pixel Watch 5 | Snapdragon W5 Gen 2 | 64 GB | 3 GB | 6 |

## 9 Limitations

- Pixel Watch 2/3 SoC not verified in this project
- Fossil Gen 5 individual package names not verified
- Mobvoi, Casio, Withings package lists absent
