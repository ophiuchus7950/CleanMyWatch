# Approved Terminology

## 1 Purpose

This document lists approved and unapproved terms for ASD-STE100 compliance.

## 2 Approved Terms

| Term | Definition | Notes |
|------|------------|-------|
| watch | Android-based smartwatch device | Not "smartwatch" (marketing term) |
| package | Android application package (APK) | Identified by reverse-DNS name |
| debloat | Disable or uninstall a package for the current user | Not "remove" (implies system-wide) |
| disable | `pm disable-user --user 0` | Reversible, keeps data |
| uninstall | `pm uninstall -k --user 0` or `pm uninstall --user 0` | May delete data without `-k` |
| restore | Return package to pre-debloat state | `pm enable` or `pm install-existing` |
| record | Baseline state capture before changes | First record wins |
| protected core | Package set that must never be targeted | Enforced by tool |
| risk level | Classification from SAFE_TO_REMOVE to DO_NOT_REMOVE | Six levels |
| evidence | Source supporting a classification | VERIFIED / PARTIALLY_VERIFIED / UNVERIFIED / UNKNOWN |
| drift | Planned target still present on device after OTA | Detected by `swdb.py drift` |
| profile | Device-specific operation map | In `13_Device_Specific_Profiles/` |

## 3 Unapproved Terms (Use Approved Instead)

The following terms are unapproved. Use the approved term instead.

```
| Unapproved | Approved | Reason |
|------------|----------|--------|
| smartwatch | watch | Marketing term |
| app | package | Ambiguous (APK vs installed app) |
| remove | uninstall / disable | Ambiguous (system vs user) |
| delete | uninstall | Implies permanent |
| brick | boot failure | Colloquial |
| debloated | disabled / uninstalled | Past participle unclear |
| safe | SAFE_TO_REMOVE / SAFE_TO_DISABLE | Must specify risk level |
| dangerous | DO_NOT_REMOVE / NOT_RECOMMENDED | Must specify risk level |
| easy / easily | (omit) | Subjective |
| utilise | use | Unapproved |
| commence | start | Unapproved |
| prior to | before | Unapproved |
| in order to | to | Unapproved |
| shall | must | Unapproved |
| please | (omit, use imperative) | Unapproved |
| furthermore | also | Unapproved |
| very | (omit or precise qualifier) | Unapproved |
| incorrect | wrong | Unapproved |
```

## 4 Abbreviations

| Abbreviation | Full Form | First Use |
|--------------|-----------|-----------|
| ADB | Android Debug Bridge | "ADB (Android Debug Bridge)" |
| APK | Android Package Kit | "APK (Android Package Kit)" |
| SDK | Software Development Kit | "SDK (Software Development Kit)" |
| OEM | Original Equipment Manufacturer | "OEM (Original Equipment Manufacturer)" |
| OTA | Over-The-Air | "OTA (Over-The-Air)" |
| MDM | Mobile Device Management | "MDM (Mobile Device Management)" |
| EMM | Enterprise Mobility Management | "EMM (Enterprise Mobility Management)" |
| SAR | Specific Absorption Rate | "SAR (Specific Absorption Rate)" |
| UI | User Interface | "UI (User Interface)" |
| API | Application Programming Interface | "API (Application Programming Interface)" |
