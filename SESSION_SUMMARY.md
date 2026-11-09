# Universal Smartwatch Debloater - Session Summary

**Date:** Mon Nov 09 2026  
**Project:** Universal Smartwatch Debloater  
**Status:** Phase 3 Complete - All tools, database, profiles, docs, tests validated

---

## Project Specification

### Objective
Build a **Universal Smartwatch Debloating and Package Knowledge System** combining:
- CleanMyTV methodology (device optimization, recovery protocols)
- UAD-ng package management (ADB integration, state transitions, safety gates)
- Pre-installed Lists database (package schema, classification taxonomy)
- Smartwatch-specific compatibility/safety analysis
- ASD-STE100 Simplified Technical English documentation

### Core Modules Required
| Module | Description |
|--------|-------------|
| A | Device Identification (manufacturer, model, codename, OS, version, build, API level, management interfaces) |
| B | Package Discovery (system, manufacturer, carrier, Google, third-party, background services, framework, watch-specific) |
| C | Package Database (package name, app name, description, manufacturer, device compatibility, category, system dependency, removal recommendation, risk classification, reversibility, evidence source) |
| D | Debloating Engine (ADB connectivity, wireless debugging, package enumeration, disabling, uninstall-for-current-user, restoration, batch operations, execution logging, error handling) |
| E | Safety Analysis (Bluetooth, WiFi, health/fitness, sensors, GPS, notifications, calling/messaging, battery, charging, system updates, device sync, emergency, security, authentication, payment) |
| F | Device-Specific Databases (per-manufacturer/OS version package recommendations with documented scope) |
| G | Restoration & Recovery (restoration, re-enablement, factory reset implications, recovery procedures, ADB troubleshooting) |

### Risk Classifications (6 levels)
1. `SAFE_TO_REMOVE`
2. `SAFE_TO_DISABLE`
3. `ADVANCED_USERS_ONLY`
4. `NOT_RECOMMENDED`
5. `DO_NOT_REMOVE`
6. `UNKNOWN`

### Architecture (20 numbered directories)
```
01_Project_Overview          11_Debloating_Procedures
02_Reference_Repository_Analysis  12_Restoration_and_Recovery
03_Platform_Architecture     13_Device_Specific_Profiles
04_Device_Compatibility      14_Automation_and_Scripting
05_Device_Identification     15_Testing_and_Validation
06_ADB_Integration           16_Troubleshooting
07_Package_Discovery         17_Technical_Documentation
08_Package_Database          18_ASD_STE100_Terminology
09_Package_Classification    19_References
10_Safety_and_Dependencies   20_Change_History
```

### Key Rules
- Never modify reference repos (read-only)
- Evidence-first: SAFE_TO_* requires PARTIALLY_VERIFIED+
- First record wins (recovery protocol)
- Protected core never targeted
- One shell call per pm command (no chaining)
- Read-back verification mandatory
- --yes required for all mutations
- STE compliance enforced
- Tests must pass before PR

---

## Phase 1: Reference Repository Analysis

### CleanMyTV (reference/cleanyourtv)
**Methodology extracted:**
- Pure-Python ADB-over-TCP client (`adb_shell` package) with native `adb` fallback
- State-record restore protocol: first record wins, atomic write, schema `{version, created, host, list, home, settings, packages:{enabled|disabled|absent}}`
- Disable-never-uninstall + user-0 scoping (`pm disable-user --user 0` per shell call)
- Read-back verification instead of exit-code trust
- Fail-closed guard framework (4 gates: protected core, Wi-Fi owner, Home owner, TV-input handlers) with named env overrides
- Curated per-device profile format: `debloat.txt` + `tv.json`
- Offline consensus classifier (`match.py`) and honest-evidence audit (`privacy.py`)
- ~250 tests with fake-TV harnesses, no hardware needed
- Agent routing via AGENTS.md/CLAUDE.md/GEMINI.md

**Transferable:** State-record protocol, user-0 scoping, read-back verification, guard framework, exit-code contract, pure-Python transport, per-device profile format, consensus classifier, honest-evidence audit, drift check, test strategy without hardware, docs architecture, pinned fact citation, agent routing, generated-vs-authored separation.

### UAD-ng (reference/universal-android-debloater-next-generation)
**Architecture:** Rust workspace (uad-core, uad-cli, uad-gui)
**Key components:**
- Typed ADB wrapper (`adb.rs`): 1-to-1 method↔command, `PackageId` validation, `PmCommand` for package ops
- State model (`sync.rs`): `Phone`, `User`, `CorePackage`, transition matrix with SDK branching
- Package list (`uad_lists.rs`): JSON keyed by package name, 3-layer load (embedded→cache→remote retry+cap)
- Config/backup (`config.rs`, `save.rs`): per-device TOML config, JSON backups
- Safety: removal-category gating (Unsafe requires expert mode), disable vs uninstall choice, verify→fallback loop, protected-user guards

**Transferable:** Typed ADB builder, `parse_package_list`+`PackageId` validation, default-device strategy, triple-list state derivation, SDK-branching transition matrix, `request_builder`+`user_flag` hygiene, verify→fallback loop, OEM error translation, JSON package schema with Removal ladder, three-layer list load, soft-safety UI gates, retry tolerances, Windows hygiene, per-device keying, CSV/selection export.

### Universal Android Pre-installed Lists (reference/universal-android-preinstalled-lists)
**Purpose:** Data layer for UAD-ng (LGPL-3)
**Schema:** JSON keyed by package name → `{list, description, dependencies, neededBy, labels, removal}`
**Removal categories:** Recommended, Advanced, Expert, Unsafe, Unlisted
**Description grammar:** First line = identity; triplet template for replaceable apps; conditional-safety phrasing; ALL-CAPS WARNING blocks with legality rationale
**Contribution:** Mass-automation disclosure required, trunk-based, labels for release notes

---

## Phase 2: Smartwatch Platform Research

### Verified Platform: Wear OS (Only debloatable family)
| Aspect | Details |
|--------|---------|
| **ADB** | Wi-Fi wireless debugging (pairing code + IP:port, adb ≥30.0.0, AP isolation OFF); USB via data cradle; **No Bluetooth ADB** |
| **Package Manager** | Standard Android `pm` (list/enable/disable/uninstall/install-existing) |
| **Play Store** | On-watch (`com.android.vending` verified); remote install re-populates debloated apps |
| **Verified Commands** | `pm list packages`, `pm disable-user --user 0`, `pm uninstall -k --user 0`, `pm enable --user 0`, `pm install-existing --user 0`, `pm path` + `adb pull`, `adb install --user 0` |
| **Failure Modes** | Batch disable `routines`+`smartgesture` → boot failure "No android system found"; `scloud`/`contacts` removal → battery drain retry loops; OTA restores debloated packages |

### Verified Package Evidence (Only Samsung/Google from GW4 + GW6/7)
- **GW4 dump** (143 recorded packages, XDA tid 4324063): AOSP core, Google Wear OS core, Samsung apps + infra/diag + 23 watchfaces. Classifications are `UNKNOWN`.
- **GW6/7 debloat thread** (34 classified, XDA tid 4613093): SAFE_TO_REMOVE (compass, reminder, worldclock, timer, stopwatch, cameracontroller, bixby.wakeup, wearable.music, video.wearable, gallery.watch, voicerecorder, budscontroller, findmyphone, mediacontroller, userdictionary, retailattractloop), SAFE_TO_DISABLE (bixby.agent), ADVANCED (shealth, shealthmonitor conditional, talkback, alarm, calendar, easyMover, smartswitchassistant, oneconnect, sree*), NOT_RECOMMENDED (samsungpay.gear, scloud, app.contacts, batterysavingsettings), DO_NOT_REMOVE (app.routines, smartgesture, watch.safety_assistance)

### Non-Android Platforms (No debloat surface)
- **Tizen** (Gear S2/S3, GW≤3): sdb only, TPKG via Galaxy Store
- **watchOS**: UI deletion only, no ADB
- **Garmin**: Connect IQ store only, RTOS
- **Fitbit**: .fba deprecated Nov 28 2026, no ADB
- **Huawei/LiteOS**: No dev settings/ADB
- **Zepp OS**: Mini Programs via Zepp app
- **Xiaomi S1-family**: Proprietary OS, no ADB
- **Polar/Suunto (except 7)**: Proprietary, phone-side integrations only

### Compatibility Matrix (14 platforms)
| Platform | ADB | pm list | disable/remove | Restore | Evidence |
|----------|-----|---------|----------------|---------|----------|
| Wear OS 3+ (GW4+, PW, Suunto 7, Xiaomi Watch 2) | ✅ Wi-Fi pairing | ✅ 143-package GW4 dump | ✅ pm -k/user 0 | pm enable/install-existing + OTA/image | VERIFIED |
| Wear OS 2 (Fossil Gen 5, TicWatch) | Legacy flow | No dumps | Same pm family | install-existing | UNKNOWN |
| Samsung Tizen | ❌ sdb only | ❌ | ❌ | Galaxy Store | N/A |
| watchOS | ❌ | ❌ | UI delete | App Store | N/A |
| Garmin/Fitbit/Zepp/LiteOS/Polar/Suunto-prop | ❌ | ❌ | ❌ | Store/UI | N/A |

---

## Phase 3: Implementation Complete

### Tools Built (stdlib-only, Python 3.10+)

#### 1. `swdb.py` - Package Database Validator/Planner
```bash
python 14_Automation_and_Scripting/tools/swdb.py validate                    # Validate all datasets
python 14_Automation_and_Scripting/tools/swdb.py stats                       # Per-dataset counts + risk breakdown
python 14_Automation_and_Scripting/tools/swdb.py query <pkg>                 # Show all entries for package
python 14_Automation_and_Scripting/tools/swdb.py packages [--risk] [--dataset]  # List packages
python 14_Automation_and_Scripting/tools/swdb.py match <dump.txt>            # Match device dump
python 14_Automation_and_Scripting/tools/swdb.py drift <dump> --profile <id> # Detect post-OTA drift
python 14_Automation_and_Scripting/tools/swdb.py plan --profile <id> [--op disable|restore]  # Show ADB commands
python 14_Automation_and_Scripting/tools/swdb.py export <path.csv>           # Export to CSV
```
**Features:** Schema validation (watchdb-1), protected core enforcement (exact + prefix rules + CORE_OK=userdictionary), risk→operation planning per profile, drift detection, CSV export.

#### 2. `sw.py` - Guarded ADB Client for Wear OS
```bash
python 14_Automation_and_Scripting/tools/sw.py identify                      # Show brand, model, SDK, Wear OS label
python 14_Automation_and_Scripting/tools/sw.py record [--out]                # Baseline state (first record wins)
python 14_Automation_and_Scripting/tools/sw.py packages [--state] [--out]    # Enumerate watch packages
python 14_Automation_and_Scripting/tools/sw.py disable <pkg> --yes           # Single package disable
python 14_Automation_and_Scripting/tools/sw.py enable <pkg> --yes            # Single package enable
python 14_Automation_and_Scripting/tools/sw.py uninstall-keep <pkg> --yes    # Uninstall with -k (keep data)
python 14_Automation_and_Scripting/tools/sw.py uninstall-purge <pkg> --yes   # Uninstall no -k (data lost)
python 14_Automation_and_Scripting/tools/sw.py restore --record <file> --yes # Full restore from record
python 14_Automation_and_Scripting/tools/sw.py one "getprop ..."             # Read-only command
python 14_Automation_and_Scripting/tools/sw.py apply --profile <id> --yes [--dry-run]  # Batch apply profile
```
**Safety:** Protected refusal, one shell call per command, read-back verification (exit 1 on mismatch), --yes required, first-record-wins state capture.

#### 3. `ste_check.py` - ASD-STE100 Subset Checker
```bash
python 14_Automation_and_Scripting/tools/ste_check.py <paths...> [--strict]
```
**Checks:** Banned words (`utilize`, `commence`, `prior to`, `in order to`, `shall`, `please`, `furthermore`, `very`, `easily`, `incorrect`), sentence length >25 words (warning), semicolons (warning). Excludes code blocks, inline code, and blockquote lines.

### Package Database (4 datasets, 207 entries)

| Dataset | Entries | Evidence | Risk Breakdown |
|---------|---------|----------|----------------|
| `discovery_galaxy_watch4` | 143 | VERIFIED (XDA tid 4324063) | UNKNOWN=143 |
| `knowledge_galaxy_watch` | 36 | PARTIALLY_VERIFIED (XDA tid 4613093) | SAFE_TO_REMOVE=15, SAFE_TO_DISABLE=1, ADVANCED=13, NOT_RECOMMENDED=4, DO_NOT_REMOVE=3 |
| `knowledge_google_wear_os` | 27 | code_analysis/dump | DO_NOT_REMOVE=24, ADVANCED=1, SAFE_TO_REMOVE=2 |
| `knowledge_third_party_watch` | 1 | verified third-party | SAFE_TO_REMOVE=1 |

### Device Profiles (4)

| Profile | Datasets | Operation Map | Scope |
|---------|----------|---------------|-------|
| `samsung_galaxy_watch4` | knowledge_galaxy_watch, knowledge_google_wear_os, knowledge_third_party_watch | SAFE_TO_REMOVE→uninstall_keep_apk, SAFE_TO_DISABLE→disable | GW4, Wear OS 3. Guard profile: all verified entries are scoped to Watch 6/7, so the plan is empty. |
| `samsung_galaxy_watch6_7` | Same | Same | GW6/GW7, Wear OS 4/5 |
| `samsung_galaxy_watch8` | Same | (empty - guard only) | GW8 (SM-L330), Wear OS 6. No verified package evidence yet. |
| `google_core` | knowledge_google_wear_os | (empty - guard only) | All Wear OS 3-6 |

### Tests (37 passing)
- **19 swdb tests:** validate (including profile validation), stats, query, packages, protected, plan scope filter, match, export
- **18 sw tests:** identify, record first-wins, record path safety, SW_SERIAL refusal, device scope check, apply dry-run, apply mismatch refusal, one, protected refusal, change_state

### Documentation (All 20 directories + root files)

All docs follow ASD-STE100 12-section structure for procedures. Key documents:
- `09_Package_Classification/01_classification_methodology.md` - 6 risk levels, 7 decision rules, reversibility table
- `09_Package_Classification/02_evidence_labels.md` - VERIFIED/PARTIALLY_VERIFIED/UNVERIFIED/UNKNOWN
- `08_Package_Database/01_database_schema.md` - watchdb-1 schema with defaults
- `10_Safety_and_Dependencies/01_safety_analysis.md` - Protected core (3 groups), failure evidence table, function risk table
- `11_Debloating_Procedures/` - Preparation, disable, uninstall, batch (STE structure)
- `12_Restoration_and_Recovery/` - Restore procedure, recovery procedures (boot failure, battery drain, OTA)
- `13_Device_Specific_Profiles/README.md` - Profile schema documentation
- `14_Automation_and_Scripting/tool_guide.md` - Complete tool usage guide
- `16_Troubleshooting/01_troubleshooting.md` - Symptom→cause→fix tables
- `18_ASD_STE100_Terminology/` - Approved terms, writing rules, checker limitations

### Root Files
- `README.md` - Project banner, methodology sources, quick start, evidence policy
- `AGENTS.md` - Job routing, repo map, hard rules, PR checklist
- `CONTRIBUTING.md` - Evidence-first, automation disclosure, reference protection, pre-commit checks
- `LICENSE` - MIT
- `.editorconfig` - Spaces/2, LF
- `.gitignore` - state records, logs, caches, generated dumps, and local reference copies

### Validation Results
```
✅ python 14_Automation_and_Scripting/tools/swdb.py validate
   Valid: 4 dataset(s), 207 package(s), 4 profile(s).

✅ python -m unittest test_swdb test_sw -v
   Ran 37 tests in 2.7s - OK

✅ python 14_Automation_and_Scripting/tools/ste_check.py <all doc dirs>
   0 error(s), 298 warning(s) [sentence length and semicolon warnings only]
```

---

## Safety Rules Enforced (from AGENTS.md)

1. **Never modify `reference/`** — read-only analysis sources
2. **Evidence first** — no classification without source + testing status
3. **SAFE_TO_* requires PARTIALLY_VERIFIED+** — enforced by `swdb.py validate`
4. **First record wins** — `sw.py record` refuses overwrite
5. **Protected core never targeted** — enforced by `is_protected()` in both tools
6. **One shell call per command** — no chaining in `sw.py`
7. **Read-back verification mandatory** — `sw.py` exits 1 on mismatch
8. **`--yes` required for mutations** — no silent destructive operations
9. **STE compliance** — `ste_check.py` must pass (no banned words)
10. **Tests must pass** — `python -m unittest ...` before PR

---

## Verified Sources (All URLs in 19_References/01_references.md)

| Category | Sources |
|----------|---------|
| **Official Android/Wear OS** | Debug Wi-Fi, Debug USB, Dev Options, Samsung Device Settings, Samsung Connect Watch, SDP Blog, Wear OS Packaging, Factory Images, Samsung App Uninstall, Wear OS Wikipedia |
| **Community (XDA/Reddit)** | WearOS Watch ADB Commands (Dante63 tid 4324063), GW6/7 Debloat (Seanie280672 tid 4613093), Easy Fire Tools broken One UI 5, Debug WiFi missing GW5 |
| **Hardware Specs** | GSMArena GW4, PW1, PW4, PW5; Qualcomm Snapdragon W5+ Gen 1 Brief; Fossil Gen 5 Review |
| **Non-Android Platforms** | Tizen sdb, Apple Watch deletion, Garmin Connect IQ, Fitbit EOL, Huawei LiteOS issue, Zepp OS, Polar, Suunto 7, Qualcomm Device Finder |
| **Reference Repos** | CleanMyTV, UAD-NG, Universal Android Pre-installed Lists |
| **Community Tools** | GeminiMan WearOS Manager, wearforge, galaxy-watch-debloat-toolkit |

---

## Known Limitations (Documented)

1. Pixel Watch 2/3 SoC unverified
2. Fossil Gen 5 individual package names unverified
3. Mobvoi/Casio/Withings package lists absent
4. Wear OS 5.1 restriction claim not verified
5. No lab recovery validation performed
6. Only Samsung GW4/GW6-7 and Google core packages have verified evidence
7. Xiaomi Watch 2/2 Pro exact Wear OS version unverified
8. SW5180 Snapdragon part number unverified
9. No Galaxy Watch 4 removal evidence exists. Every verified debloat entry is scoped to Watch 6/7, so the GW4 profile has no commands.

---

## Quick Start (from README.md)

```bash
# 1. Pair watch (one-time)
adb pair <ip:port>     # Enter pairing code from watch
adb connect <ip:port>

# 2. Identify watch
python 14_Automation_and_Scripting/tools/sw.py identify

# 3. Record baseline (CRITICAL - first record wins)
python 14_Automation_and_Scripting/tools/sw.py record

# 4. Preview plan
python 14_Automation_and_Scripting/tools/swdb.py plan --profile samsung_galaxy_watch6_7

# 5. Apply with confirmation
python 14_Automation_and_Scripting/tools/sw.py apply --profile samsung_galaxy_watch6_7 --yes

# 6. Restore if needed
python 14_Automation_and_Scripting/tools/sw.py restore --record sw-record-<serial-sha1-8>.json --yes

# 7. Check drift after OTA
python 14_Automation_and_Scripting/tools/sw.py packages --out current.txt
python 14_Automation_and_Scripting/tools/swdb.py drift current.txt --profile samsung_galaxy_watch6_7
```

---

## Project Structure (Final)

```
cleanmysmartwatch/
├── 01_Project_Overview/
│   └── 01_project_overview.md
├── 02_Reference_Repository_Analysis/
│   ├── 01_cleanyourtv_analysis.md
│   ├── 02_uad_ng_analysis.md
│   └── 03_preinstalled_lists_analysis.md
├── 03_Platform_Architecture/
│   ├── 01_wear_os_architecture.md
│   ├── 02_non_android_platforms.md
│   └── 03_platform_compatibility_matrix.md
├── 04_Device_Compatibility/
│   └── 01_supported_devices.md
├── 05_Device_Identification/
│   └── 01_device_identification.md
├── 06_ADB_Integration/
│   ├── 01_adb_setup_and_pairing.md
│   └── 02_adb_command_reference.md
├── 07_Package_Discovery/
│   └── 01_package_discovery.md
├── 08_Package_Database/
│   ├── 01_database_schema.md
│   └── data/
│       ├── discovery_galaxy_watch4.json
│       ├── knowledge_galaxy_watch.json
│       ├── knowledge_google_wear_os.json
│       └── knowledge_third_party_watch.json
├── 09_Package_Classification/
│   ├── 01_classification_methodology.md
│   └── 02_evidence_labels.md
├── 10_Safety_and_Dependencies/
│   └── 01_safety_analysis.md
├── 11_Debloating_Procedures/
│   ├── 01_preparation.md
│   ├── 02_disable_procedure.md
│   ├── 03_uninstall_procedure.md
│   └── 04_batch_procedures.md
├── 12_Restoration_and_Recovery/
│   ├── 01_restoration_procedure.md
│   └── 02_recovery_procedures.md
├── 13_Device_Specific_Profiles/
│   ├── README.md
│   ├── samsung_galaxy_watch4/profile.json
│   ├── samsung_galaxy_watch6_7/profile.json
│   └── google_core/profile.json
├── 14_Automation_and_Scripting/
│   ├── tools/
│   │   ├── swdb.py
│   │   ├── sw.py
│   │   └── ste_check.py
│   └── tool_guide.md
├── 15_Testing_and_Validation/
│   └── tests/
│       ├── test_swdb.py
│       └── test_sw.py
├── 16_Troubleshooting/
│   └── 01_troubleshooting.md
├── 17_Technical_Documentation/
│   └── 01_documentation_standards.md
├── 18_ASD_STE100_Terminology/
│   ├── 01_approved_terminology.md
│   ├── 02_writing_rules.md
│   └── 03_checker_limitations.md
├── 19_References/
│   └── 01_references.md
├── 20_Change_History/
│   └── 01_change_history.md
├── reference/                    # READ-ONLY - NEVER MODIFY
│   ├── cleanyourtv/
│   ├── universal-android-debloater-next-generation/
│   └── universal-android-preinstalled-lists/
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── .editorconfig
└── .gitignore
```

---

## Next Steps (If Continuing)

1. **Add more device profiles** as package dumps become available (Pixel Watch, Xiaomi Watch 2, Suunto 7, Fossil)
2. **Expand knowledge datasets** with community-verified classifications
3. **Add GUI/TUI** for non-CLI users (optional)
4. **CI/CD pipeline** for automated validation on PR
5. **Watch 8 research** - when released, add specifications and package dump

---

**End of Session Summary**  
All Phase 3 deliverables complete and validated.
