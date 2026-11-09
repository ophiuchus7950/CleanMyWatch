# Smartwatch Platform Compatibility Matrix

> Evidence base: fetch-verified sources from one research session.
> Labels follow section 2. UNCERTAIN marks stay attached to every weak claim.

## 1. Purpose

1. This file defines platform capability for the debloat engine.
2. The engine reads a row before it touches a device.
3. Each row states what is possible, and what the engine must refuse.
4. Sources stay inline. UNCERTAIN and UNVERIFIED marks stay attached.

## 2. Matrix Legend

Column definitions:

- **Platform** — device family or operating system generation.
- **OS family** — the base operating system line.
- **Package manager concept** — the formal install and removal channel.
- **ADB availability** — an adb bridge, or a vendor bridge such as sdb.
- **Package enumeration possible** — whether a tool can list installed packages.
- **Disable/remove via ADB possible** — whether user-scope disable or uninstall works over a bridge.
- **Restore mechanism** — the documented way back.
- **Notes** — evidence notes, per-OEM quirks, and warnings.

Evidence labels:

- **VERIFIED** — a fetched official or primary source from this session supports the claim. The URL appears inline.
- **PARTIALLY VERIFIED** — part of the claim has a fetched source. Another part (a version number, a model boundary) does not. The weak part keeps its UNCERTAIN mark.
- **UNVERIFIED** — community or secondary text only. A URL can exist. Treat it as a lead, not as proof.
- **UNKNOWN** — no usable source was found in this session. The engine prints UNKNOWN and stops.

Label rule: when a decision depends on a claim with a label below VERIFIED, the engine prints the label and the reason. Then it stops.

## 3. Compatibility Matrix

| Platform | OS family | Package manager concept | ADB availability | Package enumeration possible | Disable/remove via ADB possible | Restore mechanism | Notes |
|---|---|---|---|---|---|---|---|
| Wear OS 3 and newer (Galaxy Watch 4+, Pixel Watch, Xiaomi Watch 2-family, Suunto 7) | Android-based. Wear OS 3 = API 30 through Wear OS 6 = API 36 [https://en.wikipedia.org/wiki/Wear_OS] | Android APKs via Google Play. The store package com.android.vending appears in a verified package dump [https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/] | Wi-Fi wireless debugging with a pairing code. adb 30.0.0 or newer. AP isolation off [https://developer.android.com/training/wearables/get-started/debug-wifi]. USB through a data-capable cradle [https://developer.android.com/training/wearables/get-started/debugging]. Bluetooth is not supported [https://developer.android.com/training/wearables/get-started/debugging]. VERIFIED | Yes. pm list packages. A 143-entry Galaxy Watch 4 dump is recorded [https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/]. VERIFIED | Yes. pm uninstall -k --user 0 and pm disable-user --user 0, both verified on Galaxy Watch 4 and Watch 6/7 [https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/]. VERIFIED | pm enable --user 0. pm install-existing. OTA or factory-image re-flash [https://developers.google.com/android/images-watch], [https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/]. VERIFIED | Developer options differ per OEM. Samsung: tap Software version five times [https://developer.samsung.com/health/sensor/guide/device-settings.html]. Pixel: About > Versions > Build number [https://developer.android.com/studio/debug/dev-options]. Samsung's phone app uninstall path covers some third-party pre-installs [https://www.samsung.com/us/support/answer/ANS10002865/]. A wrong disable batch once ended in recovery with "No android system found" [https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/]. OTAs can restore removed apps [https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/] |
| Wear OS 5.1 specific ADB restriction claims | Android-based | Same as above | UNKNOWN. This session found no source for added 5.1 restrictions. UNCERTAIN | Same as above | Same as above | Same as above | Do not print the claim as fact. Community Wi-Fi debugging reports exist for older builds [https://www.reddit.com/r/GalaxyWatch/comments/16gt6l0/], [https://www.reddit.com/r/GalaxyWatch/comments/1b9i8yg/]. A tertiary overview page exists [https://grokipedia.com/page/Sideloading_on_Galaxy_Watch]; treat it as context only |
| Wear OS 2 and older (Fossil Gen 5, TicWatch, Casio WSD) | Android-based (pre-API 30) | Android APKs via Play Store | ADB present. Legacy settings flow. The Wear OS 3 pairing-code flow does not apply. PARTIALLY VERIFIED — this session verified only the Wear OS 3+ flow [https://developer.android.com/training/wearables/get-started/debug-wifi] | Yes — pm list packages (standard Wear OS mechanics) | Yes — the same pm family | pm install-existing, or a vendor re-flash | No verified package dumps for these OEMs this session. UNCERTAIN for individual package names. Gen 5 anchor: Wear OS 2 on Snapdragon Wear 3100 [https://www.androidauthority.com/fossil-gen-5-smartwatch-review-1020794/], [https://smartwatchspex.com/fossil-the-carlyle-hr-gen-5-specs/]. PARTIALLY VERIFIED |
| Samsung Tizen (pre-Wear OS Samsung line) | Tizen (vendor OS) | Closed-store applications. The TPK format name is UNCERTAIN in-session | No ADB. sdb (Smart Development Bridge) exists for developers [https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md]. VERIFIED as a tool; not a debloat channel | Not for users. The sdb list command is UNCERTAIN (U-10) | No | Reinstall from the Galaxy Store. UNVERIFIED in-session | Verdict: refuse. Recent Galaxy watches moved to Wear OS. UNCERTAIN (U-12) |
| Apple watchOS | watchOS (Apple) | App Store distribution, on the watch or through the paired iPhone [https://support.apple.com/en-us/109028]. VERIFIED | No ADB for users. UNVERIFIED engineering-only path | Not exposed to users | No | Re-download from the App Store [https://support.apple.com/en-us/109028]. Some built-in apps became deletable with watchOS 9.4 or later [https://support.apple.com/en-us/118582]. VERIFIED | Deletion is Apple-managed. The engine refuses [https://support.apple.com/en-us/109028] |
| Garmin (Connect IQ on RTOS) | Proprietary RTOS + Connect IQ layer | Connect IQ apps, widgets, data fields, watch faces, audio providers [https://developer.garmin.com/connect-iq/overview/], [https://apps.garmin.com/en-US/]. VERIFIED | No consumer bridge. The SDK serves developers [https://developer.garmin.com/connect-iq/sdk/]. VERIFIED | No | No | Reinstall from the Connect IQ Store [https://apps.garmin.com/en-US/] | Content is managed through the Connect IQ store app [https://support.garmin.com/en-US/?faq=DnXHorjkxT106X9AGsOoC8]. The RTOS core is unreachable |
| Fitbit OS (Ionic / Versa family) | Fitbit OS | Fitbit App Gallery clocks and apps | No ADB | Watch and Fitbit app UI only | No | None after 28 November 2026. "Starting on November 28, 2026, you can no longer install or update third-party apps and clocks on Fitbit smartwatches" [https://support.google.com/googlehealth/answer/14226056]. VERIFIED | An EEA mid-2024 app removal is UNVERIFIED (secondary sources only). Newer models with no third-party store: UNVERIFIED |
| Huawei watch line (LiteOS / HarmonyOS) | Vendor RTOS family. LiteOS core; some models carry vendor HarmonyOS builds. UNCERTAIN (per-model mapping) | No public app install channel | No ADB and no developer settings. Community records: [https://xdaforums.com/tags/huawei-watch/]. No public SDK path: [https://github.com/LiteOS/LiteOS/issues/630]. PARTIALLY VERIFIED | No | No | Not applicable | A community APK hack exists [https://consumer.huawei.com/en/community/details/topicId-161034/]. It is not a bridge. UNVERIFIED — do not use it |
| Zepp OS (Amazfit) | Zepp OS (RTOS + Mini Programs) | Mini Programs via the Zepp app store [https://developer.zepp.com/os/home]. VERIFIED | No device bridge. Developers use the Zeus toolchain [https://docs.zepp.com/docs/intro/using/]. VERIFIED | Via the Zepp companion app UI only | No | Reinstall from the Zepp store | Mini Programs are the only user content class |
| Xiaomi — proprietary track (Watch S1, S1 Pro) | Xiaomi proprietary OS | Companion-store apps and watch faces [https://www.mi.com/global/product/xiaomi-watch-s1-pro/]. VERIFIED for the product line; store details UNVERIFIED in-session | None found this session | Via the Xiaomi companion app UI only | No | Reinstall from the store | UNCERTAIN — the Redmi watch variant boundary is not verified |
| Xiaomi Watch 2 / 2 Pro | Wear OS [https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/], [https://www.mundoxiaomi.com/especiales/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-estas-principales-diferencias-mejores-relojes-inteligentes-marca], [https://versus.com/en/xiaomi-watch-2-pro-vs-xiaomi-watch-s1]. VERIFIED as Wear OS | Android APKs via Play Store | Same as the Wear OS row | Yes | Yes | Wear OS restore paths | UNCERTAIN — exact Wear OS version. Common reporting says 3.x. PARTIALLY VERIFIED |
| Polar (Vantage, Grit, Pacer) | Polar proprietary firmware | None on the watch. Third-party apps are phone-side integrations [https://www.polar.com/en/compatible-apps/], [https://support.polar.com/us-en/what-third-party-apps-and-devices-are-compatible-with-polar-products]. VERIFIED | None documented | No | No | Switch integrations back on in Polar's phone services | No packages exist. The debloat concept has no objects here |
| Suunto — proprietary models (9 Baro, Race, Vertical) | Suunto proprietary firmware | None on the watch | None documented | No | No | Phone-side Suunto App services | The Suunto 7 exception sits in its own row |
| Suunto 7 (exception) | Wear OS by Google [https://www.suunto.com/Support/Product-support/suunto_7/suunto_7/wear-os-by-google/]. VERIFIED | Android APKs via Play Store | Yes. The Wear OS flow applies | Yes | Yes | Wear OS restore paths | Qualcomm records Snapdragon Wear 3100 silicon [https://www.qualcomm.com/wearables/device-finder/suunto-suunto-7]. VERIFIED. UNCERTAIN — the exact Wear OS version (U-11) |

## 4. Wear OS Version to Android API Level Mapping

Source for every row below: [https://en.wikipedia.org/wiki/Wear_OS].

| Wear OS version | Android version | API level | Status |
|---|---|---|---|
| Wear OS 3 | Android 11 | API 30 | VERIFIED |
| Wear OS 4 | Android 13 | API 33 | VERIFIED |
| Wear OS 5 | Android 14 | API 34 | VERIFIED |
| Wear OS 5.1 | Android 15 | API 35 | VERIFIED |
| Wear OS 6 | Android 16 | API 36 | VERIFIED |
| Wear OS 6.1 | — | — | UNVERIFIED as a date note. The source lists a December 2025 release. Check release notes before use. |
| Wear OS 7 | Android 17 (expected) | — | UNVERIFIED. The same source calls it expected for 2026. Treat it as a forecast. |

Why the mapping matters: the developer options flow and the pm behavior expectations differ across API levels. Version detection uses About > Versions > Build number [https://support.google.com/googlepixelwatch/answer/12651869], [https://developer.android.com/studio/debug/dev-options].

## 5. Decision Rules

Codes DR-01 onward. The engine applies the first rule that matches.

- **DR-01 — Identify first.** The engine identifies the platform before any command. If no row matches, see DR-08.
- **DR-02 — Wear OS 3 and newer: allowed with guards.** Guards: operate on user 0 only. Exclude load-bearing packages: system UI, telephony, wake-up handlers, and providers. Log every change. Print the restore path. End work with ADB off. State that OTAs can restore removed apps [https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/]. Community practice supports disable-by-default actions and generated restore scripts [https://github.com/dmitthedazed/wearforge], [https://github.com/Vermaarp/galaxy-watch-debloat-toolkit].
- **DR-03 — Wear OS 2 legacy: allowed, different flow.** The Wear OS 3 pairing-code flow does not apply. Use the legacy developer options path. Its details are UNCERTAIN in this session [https://developer.android.com/training/wearables/get-started/debug-wifi].
- **DR-04 — Samsung Tizen: refuse.** No ADB and no user package state exist. sdb is the developer tool. It stays out of scope [https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md].
- **DR-05 — Apple watchOS: refuse. Apple-managed deletion only.** Users delete apps through the Apple flow [https://support.apple.com/en-us/109028]. The engine offers that link. It runs no commands.
- **DR-06 — Garmin, Fitbit, Huawei, Zepp OS, Polar, Suunto (proprietary), Xiaomi (proprietary): refuse with explanation.** Each row lacks a bridge, an enumerable state, and a restore path. The refusal prints the matching platform record from file 02. For Fitbit, add the 28 November 2026 stop [https://support.google.com/googlehealth/answer/14226056]. For Huawei, add: no brute-force or community-hack commands [https://consumer.huawei.com/en/community/details/topicId-161034/].
- **DR-07 — Xiaomi Watch 2-family and Suunto 7: treat as Wear OS.** Their records show Wear OS [https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/], [https://www.suunto.com/Support/Product-support/suunto_7/suunto_7/wear-os-by-google/]. Then DR-02 guards apply.
- **DR-08 — Unknown platform: refuse and report.** The engine prints UNKNOWN. It asks for the OS name. It runs nothing. It must not guess.
- **DR-09 — Damage class warning.** Every Wear OS guard log mentions the recovery-failure case from a wrong disable batch [https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/]. The warning uses simple words. It does not overstate.

## 6. Hardware Reference Points

| Device / part | SoC | Storage | RAM | Wear OS context | Sources | Status |
|---|---|---|---|---|---|---|
| Galaxy Watch 4 | Exynos W920 | 16 GB | 1.5 GB | Wear OS platform device | [https://www.gsmarena.com/samsung_galaxy_watch4-11045.php] | VERIFIED |
| Pixel Watch | Exynos 9110 | 32 GB | 2 GB | Wear OS platform device | [https://www.gsmarena.com/google_pixel_watch-11546.php] | VERIFIED |
| Pixel Watch 2 | reported Snapdragon W5 Gen 1 | — | — | — | [https://legendarytech.io/google/pixel-watch/pixel-watch-2] | UNCERTAIN — secondary source only |
| Pixel Watch 3 | not verified; reported names only | — | — | — | none fetched | UNKNOWN |
| Pixel Watch 4 | Snapdragon W5 Gen 2 | 32 GB | 2 GB | ships Wear OS 6.0 | [https://www.gsmarena.com/google_pixel_watch_4-14088.php], [https://www.androidcentral.com/wearables/snapdragon-w5-gen-2-revealed-with-satellite-sos-but-no-major-power-boost] | VERIFIED |
| Pixel Watch 5 | Snapdragon W5 Gen 2 | 64 GB | 3 GB | Wear OS platform device | [https://www.gsmarena.com/google_pixel_watch_5-14860.php], [https://support.google.com/googlepixelwatch/answer/12651869] | VERIFIED |
| Snapdragon W5+ Gen 1 platform | SoC + QCC5100 always-on co-processor. Part numbers: SW5100 and SW5100P | — | — | platform silicon | [https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-W5-Plus-Gen-1-Wearable-Platforms-product-brief.pdf] | VERIFIED |

Rules for this table:

1. Use only the part numbers in the table. Part numbers absent here are not verified.
2. Pixel Watch 2 silicon stays UNCERTAIN until Google states it.
3. Pixel Watch 3 silicon is UNKNOWN. Do not print a SoC name for it.

## 7. References

Official Google and Android documentation:

- https://developer.android.com/training/wearables/get-started/debug-wifi
- https://developer.android.com/training/wearables/get-started/debugging
- https://developer.android.com/studio/debug/dev-options
- https://developers.google.com/android/images-watch
- https://support.google.com/googlehealth/answer/14226056
- https://support.google.com/googlepixelwatch/answer/12651869

Wear OS reference table:

- https://en.wikipedia.org/wiki/Wear_OS

XDA evidence dumps (verified command and package evidence):

- https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/
- https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/

Samsung (official):

- https://developer.samsung.com/health/sensor/guide/device-settings.html
- https://www.samsung.com/us/support/answer/ANS10002865/
- https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md

Apple (official):

- https://support.apple.com/en-us/109028
- https://support.apple.com/en-us/118582

Garmin (official):

- https://apps.garmin.com/en-US/
- https://developer.garmin.com/connect-iq/overview/
- https://developer.garmin.com/connect-iq/sdk/
- https://support.garmin.com/en-US/?faq=DnXHorjkxT106X9AGsOoC8

Huawei (community and issue trackers):

- https://xdaforums.com/tags/huawei-watch/
- https://github.com/LiteOS/LiteOS/issues/630
- https://consumer.huawei.com/en/community/details/topicId-161034/

Zepp, Xiaomi, Polar, Suunto (official and comparison pages):

- https://developer.zepp.com/os/home
- https://docs.zepp.com/docs/intro/using/
- https://www.mi.com/global/product/xiaomi-watch-s1-pro/
- https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/
- https://www.mundoxiaomi.com/especiales/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-estas-principales-diferencias-mejores-relojes-inteligentes-marca
- https://versus.com/en/xiaomi-watch-2-pro-vs-xiaomi-watch-s1
- https://www.polar.com/en/compatible-apps/
- https://support.polar.com/us-en/what-third-party-apps-and-devices-are-compatible-with-polar-products
- https://www.suunto.com/Support/Product-support/suunto_7/suunto_7/wear-os-by-google/
- https://www.qualcomm.com/wearables/device-finder/suunto-suunto-7

Fossil Gen 5 (reviews and product pages):

- https://www.androidauthority.com/fossil-gen-5-smartwatch-review-1020794/
- https://smartwatchspex.com/fossil-the-carlyle-hr-gen-5-specs/
- https://www.fossil.com/products/gen-5-lte-smartwatch-black-silicone/FTW40531F.html
- https://www.neowin.net/reviews/fossil-gen-5-smartwatch-review-the-best-wear-os-smartwatch/

Hardware spec pages:

- https://www.gsmarena.com/samsung_galaxy_watch4-11045.php
- https://www.gsmarena.com/google_pixel_watch-11546.php
- https://www.gsmarena.com/google_pixel_watch_4-14088.php
- https://www.gsmarena.com/google_pixel_watch_5-14860.php
- https://www.androidcentral.com/wearables/snapdragon-w5-gen-2-revealed-with-satellite-sos-but-no-major-power-boost
- https://www.qualcomm.com/content/dam/qcomm-martech/dm-assets/documents/Snapdragon-W5-Plus-Gen-1-Wearable-Platforms-product-brief.pdf

Community tooling (Wear OS practice evidence):

- https://github.com/dmitthedazed/wearforge
- https://github.com/Vermaarp/galaxy-watch-debloat-toolkit
- https://github.com/Vermaarp/galaxy-watch-debloat-toolkit/blob/main/GUIDE.md

Community reports (quirk leads, not proof):

- https://www.reddit.com/r/GalaxyWatch/comments/16gt6l0/
- https://www.reddit.com/r/GalaxyWatch/comments/1b9i8yg/

UNCERTAIN and tertiary sources:

- https://legendarytech.io/google/pixel-watch/pixel-watch-2
- https://grokipedia.com/page/Sideloading_on_Galaxy_Watch

END OF DOCUMENT.
