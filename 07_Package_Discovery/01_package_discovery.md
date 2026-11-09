# Package Discovery

## 1 Purpose

This document describes how packages are discovered, categorised, and recorded.

## 2 Enumeration Procedure

Run `python 14_Automation_and_Scripting/tools/sw.py packages` or `python 14_Automation_and_Scripting/tools/sw.py packages --state all` to enumerate all system packages on the watch. The tool executes:

```bash
pm list packages -s -e --user 0   # enabled
pm list packages -s -d --user 0   # disabled
pm list packages -s -u --user 0   # all (including uninstalled-for-user)
```

Results are parsed and categorised by state.

## 3 Package Categories

Each package in the database has a `category` field:

| Category | Description |
|----------|-------------|
| Android core | AOSP framework packages (`android`, `com.android.*`) |
| Connectivity | Bluetooth, Wi-Fi, mobile data |
| Communication | Phone, messaging, dialer |
| Health engine | Sensor recording, fitness tracking |
| System UI | Watch face, notifications, launcher |
| App store | Google Play on watch |
| Google services core | GMS, GSF, permissions |
| Watch framework | Wear OS ambient, batteries, overlay |
| Setup | OEM setup, partner setup |
| Accessibility | TalkBack, TTS |
| Navigation | Maps |
| Account sync | Samsung/Google account services |
| Retail demo | Store demo loops |
| Watch face | Individual watch face packages |
| Diagnostics | Factory test, hardware modules |
| Security | Knox, attestation, SELinux |
| Payment | Samsung Pay, Google Pay |
| Third-party | Pre-installed partner apps |

## 4 Function Not Established

Packages with unknown function are marked with `category: "Function not established"` and `risk: "UNKNOWN"`. This applies to infrastructure components like `com.samsung.sree.*` where the purpose is not documented in any verified source.

## 5 Discovery vs Knowledge Datasets

- **Discovery datasets** (`discovery_*`) — raw enumeration from a device dump. Only `risk: "UNKNOWN"` and minimal metadata. No removal recommendations.
- **Knowledge datasets** (`knowledge_*`) — classified entries with risk levels, evidence, and removal recommendations. Built from community threads, manufacturer docs, and code analysis.

## 6 Recording a New Dump

```bash
python 14_Automation_and_Scripting/tools/sw.py packages --out dump.txt
python 14_Automation_and_Scripting/tools/swdb.py match dump.txt
```

The `match` command shows protected packages, unknown packages, and known entry counts.
