# Change History

## 1 Purpose

This document tracks changes to the project.

## 2 Version 1.0.0 (2026-11-09)

### Added

- Project structure with 20 numbered directories per specification
- Package database schema (watchdb-1) with 4 datasets:
  - `discovery_galaxy_watch4` — 143 packages (VERIFIED dump)
  - `knowledge_galaxy_watch` — 35 packages (PARTIALLY_VERIFIED community)
  - `knowledge_google_wear_os` — 27 packages (code_analysis/dump)
  - `knowledge_third_party_watch` — 2 packages (verified third-party)
- Risk classification methodology (6 levels)
- Evidence labels (VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, UNKNOWN)
- Safety analysis with protected core set (~45 exact packages + prefixes)
- Failure evidence table (boot failure, battery drain, OTA restore)
- Device profiles: `samsung_galaxy_watch4`, `samsung_galaxy_watch6_7`, `google_core`
- Tools: `swdb.py` (database validator/planner), `sw.py` (ADB client)
- STE checker: `ste_check.py`
- Unit tests: 26 tests passing (16 swdb + 10 sw)
- Documentation per ASD-STE100 structure

### Verified Package Sources

- Samsung Galaxy Watch 4 `pm list packages` dump (XDA REF-11, ~190 packages)
- Galaxy Watch 6/7 debloat thread (XDA REF-12, 34 classified packages)
- Google Wear OS core packages (code analysis + dump correlation)

### Limitations Documented

- Pixel Watch 2/3 SoC unverified
- Fossil Gen 5 individual packages unverified
- Mobvoi/Casio/Withings package lists absent
- Wear OS 5.1 restriction claim not verified
- No lab recovery validation

---

## 3 Version 1.0.1 (2026-11-09)

### Fixed

- `sw.py record` on Windows: the Wi-Fi serial (for example `IP:port`)
  no longer reaches the record filename. The filename is
  `sw-record-<serial-sha1-8>.json`. The record write works over Wi-Fi.
- Profile scope enforcement: `swdb.py plan` now skips entries whose
  `device_scope` or `software_scope` does not intersect the profile.
  Earlier plans applied Galaxy Watch 6/7 evidence to the Watch 4 profile.
- Device guard: `sw.py apply` now reads the connected watch identity and
  refuses a device outside `device_match` or `software_scope`. The
  named override is `SW_ALLOW_DEVICE_MISMATCH=1`.
- `require_one_device` returned an `IndexError` when `SW_SERIAL` was set
  and no watch was connected. It now refuses with exit code 2.
- `swdb.py validate` now validates every profile and reports problems.
  Result: 4 datasets, 207 packages, 4 profiles.
- Tool paths in all documents now use
  `14_Automation_and_Scripting/tools/`.
- `README.md` match example now uses the real positional `DUMP_FILE`
  argument.
- Package data: Calculator moved from `knowledge_third_party_watch` to
  `knowledge_galaxy_watch`. The third-party dataset now has one entry.

### Added

- `device_match` field in each operation profile.
- `samsung_galaxy_watch8` guard profile for Galaxy Watch 8 (SM-L330).
  It has no operation map because no verified package evidence exists.
- Tests for record paths, `SW_SERIAL` refusal, device scope refusal, plan
  scope filter, the Watch 8 guard profile, and profile validation.
