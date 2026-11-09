# Non-Android Smartwatch Platforms

> Evidence base: web research from one session. Sources are inline on every fact.
> Package-level verified evidence covers Samsung and Google names only, from two XDA dumps.
> UNCERTAIN items carry their own register in section 6.

## 1. Purpose

1. This file records every smartwatch platform that does not use an Android package manager.
2. The debloat tool in this repository reads this file before it acts on a device.
3. The tool needs a verdict for each platform family.
4. This file stores that verdict and the supporting evidence.
5. Every fact carries its source URL, or an explicit UNCERTAIN mark.
6. This file does not describe Wear OS procedures. The compatibility matrix file covers them.

## 2. Scope — platforms with no Android package manager

This record lists platforms without an Android package manager:

- Samsung Tizen watches (the pre-Wear OS Samsung line).
- Apple watchOS (Apple Watch).
- Garmin devices on vendor RTOS firmware with a Connect IQ app layer.
- Fitbit OS devices (Ionic and Versa family).
- Huawei watches on LiteOS or a vendor HarmonyOS variant.
- Amazfit watches on Zepp OS.
- Xiaomi watches on Xiaomi proprietary OS (S1-family).
- Polar watches on Polar proprietary firmware.
- Suunto watches on proprietary firmware, with the Suunto 7 exception.

Two boundary notes:

- Xiaomi Watch 2 and Watch 2 Pro run Wear OS [https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/]. This file records them. Their engine path follows the Wear OS rules.
- Fossil Gen 5 ran Wear OS 2 [https://www.androidauthority.com/fossil-gen-5-smartwatch-review-1020794/]. It is an Android-family device with a legacy settings flow. This file records it as a legacy note only.

**Standing rule: do not apply Android debloat procedures to the platforms above.**

## 3. Platform Records

Each record uses the same six fields. Field values carry sources.
Labels: "UNCERTAIN" means this session found no source. "UNVERIFIED" means secondary or community sources only.

### 3.1 Samsung Tizen

- **OS family:** Samsung Tizen, a Linux-based vendor OS.
- **Package concept:** applications from a closed store (Galaxy Store channel). UNCERTAIN — the TPK package format name is general knowledge. No fetched source confirmed it in this session.
- **Connection bridge:** Smart Development Bridge (sdb) for developers [https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md]. sdb is not ADB. sdb is not a user tool.
- **User-removable surface:** store apps only, through the watch UI or the phone app. UNVERIFIED — community-level knowledge only in this session.
- **Restore surface:** reinstall from the Galaxy Store. UNVERIFIED in-session.
- **Debloat verdict:** refuse. No package enumeration exists. No user-space package state exists. sdb gives no debloat path.
- Boundary note: recent Samsung Galaxy watches moved to Wear OS. UNCERTAIN — this session did not verify the model boundary.

### 3.2 Apple watchOS

- **OS family:** watchOS on Apple Watch.
- **Package concept:** apps arrive from the App Store, on the watch or through the paired iPhone [https://support.apple.com/en-us/109028].
- **Connection bridge:** none for end users. A developer-only Mac install path exists. UNVERIFIED — not checked in this session.
- **User-removable surface:** users delete apps on the watch. The flow is touch and hold, then "Edit Apps" or "Delete app" [https://support.apple.com/en-us/109028]. Some built-in Apple apps became deletable with watchOS 9.4 or later [https://support.apple.com/en-us/118582].
- **Restore surface:** re-download from the App Store [https://support.apple.com/en-us/109028].
- **Debloat verdict:** refuse. Deletion is Apple-managed. No ADB exists. No package enumeration exists.
- Register note: the full removable built-in app set across watchOS versions is UNCERTAIN. This session verified only the "watchOS 9.4 or later" capability [https://support.apple.com/en-us/118582].

### 3.3 Garmin (Connect IQ on vendor RTOS)

- **OS family:** proprietary RTOS firmware with a Connect IQ app layer.
- **Package concept:** Connect IQ apps, widgets, data fields, watch faces, and audio content providers [https://developer.garmin.com/connect-iq/overview/]. Distribution runs through the Connect IQ Store [https://apps.garmin.com/en-US/].
- **Connection bridge:** none for consumers. The Connect IQ SDK serves developers only [https://developer.garmin.com/connect-iq/sdk/].
- **User-removable surface:** install and manage Connect IQ content through the Connect IQ store app on the phone [https://support.garmin.com/en-US/?faq=DnXHorjkxT106X9AGsOoC8].
- **Restore surface:** reinstall from the Connect IQ Store [https://apps.garmin.com/en-US/].
- **Debloat verdict:** refuse. The RTOS core is unreachable. Nothing is a valid debloat object.

### 3.4 Fitbit OS

- **OS family:** Fitbit OS on Fitbit smartwatches.
- **Package concept:** third-party clock faces and apps from the Fitbit App Gallery.
- **Connection bridge:** none exists.
- **User-removable surface:** the watch UI and the Fitbit app UI. The store line now closes. Google states: "Starting on November 28, 2026, you can no longer install or update third-party apps and clocks on Fitbit smartwatches" [https://support.google.com/googlehealth/answer/14226056].
- An EEA-side removal of some partner apps in mid-2024 appears in secondary sources. UNVERIFIED — no primary URL was fetched this session.
- Newer Fitbit models show no third-party app store at all. UNVERIFIED in-session.
- **Restore surface:** re-install from the gallery until the stop date. After 28 November 2026: none [https://support.google.com/googlehealth/answer/14226056].
- **Debloat verdict:** refuse. No bridge, no package state, and a closing store make debloat impossible.

### 3.5 Huawei (LiteOS / HarmonyOS)

- **OS family:** vendor RTOS family. LiteOS is the core line; some models carry vendor HarmonyOS builds. UNCERTAIN — the per-model OS mapping is not verified in this session.
- **Package concept:** no documented public app install channel.
- **Connection bridge:** no developer settings and no ADB. Community threads on XDA's huawei-watch tag record this [https://xdaforums.com/tags/huawei-watch/]. Official LiteOS developer discussion also shows no public SDK path [https://github.com/LiteOS/LiteOS/issues/630].
- **User-removable surface:** none documented. Vendor apps stay fixed.
- **Community hack:** a Huawei community thread describes an APK workaround for companion features [https://consumer.huawei.com/en/community/details/topicId-161034/]. It is not a package manager. The engine must not treat it as a bridge.
- **Restore surface:** not applicable.
- **Debloat verdict:** refuse with explanation. Nothing can be enumerated or disabled. Forced experiments risk an unusable device.

### 3.6 Amazfit (Zepp OS)

- **OS family:** Zepp OS, an RTOS with a Mini Program app layer.
- **Package concept:** Mini Programs install from the Zepp app store on the phone [https://developer.zepp.com/os/home].
- **Connection bridge:** none on the device. Developers use the Zeus toolchain, not a device shell [https://docs.zepp.com/docs/intro/using/].
- **User-removable surface:** Mini Programs, through the Zepp companion app.
- **Restore surface:** reinstall from the Zepp store.
- **Debloat verdict:** refuse. No enumeration exists. No user-scope package state exists.

### 3.7 Xiaomi

Xiaomi runs a dual-track watch line:

- **Proprietary track:** Watch S1 and Watch S1 Pro run Xiaomi's own OS with a long-battery design [https://www.mi.com/global/product/xiaomi-watch-s1-pro/].
- **Wear OS track:** Watch 2 and Watch 2 Pro run Wear OS. A comparison page states the OS difference plainly [https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/]. Reporting also frames the arrival of Wear OS at the Watch 2 Pro [https://www.mundoxiaomi.com/especiales/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-estas-principales-diferencias-mejores-relojes-inteligentes-marca]. A third comparison matches this split [https://versus.com/en/xiaomi-watch-2-pro-vs-xiaomi-watch-s1].

Fields:

- **OS family:** proprietary OS (S1-family) or Wear OS (Watch 2-family).
- **Package concept:** proprietary track — companion-store apps and watch faces. Wear OS track — Android APKs through the Play Store.
- **Connection bridge:** proprietary track — none found this session. Wear OS track — ADB (Wear OS rules apply).
- **User-removable surface:** proprietary track — store apps through the Xiaomi companion app. Wear OS track — the Wear OS surface.
- **Restore surface:** reinstall from the respective store, or Play Store restore paths.
- **Debloat verdict:** proprietary track — refuse. Wear OS track — treat as Wear OS. UNCERTAIN — the exact Wear OS version is not verified in-session. Common reporting says 3.x.

### 3.8 Polar

- **OS family:** Polar proprietary firmware.
- **Package concept:** no on-watch app store. Third-party "apps" are phone-side integrations, listed in the official compatible-apps portal [https://www.polar.com/en/compatible-apps/]. Support confirms integration-based compatibility, such as Strava and TrainingPeaks [https://support.polar.com/us-en/what-third-party-apps-and-devices-are-compatible-with-polar-products].
- **Connection bridge:** none documented.
- **User-removable surface:** integration toggles in Polar's phone services. Sensor pairing only.
- **Restore surface:** switch the integrations back on. Not package restore.
- **Debloat verdict:** refuse. No packages exist. The debloat concept has no objects here.

### 3.9 Suunto

- **OS family:** proprietary firmware on most models. One exception exists.
- **Exception:** the Suunto 7 ran with Wear OS by Google [https://www.suunto.com/Support/Product-support/suunto_7/suunto_7/wear-os-by-google/]. Qualcomm records it on the Snapdragon Wear 3100 platform [https://www.qualcomm.com/wearables/device-finder/suunto-suunto-7].
- **Package concept:** proprietary models — no watch-side store. Suunto 7 — Android APKs through Play.
- **Connection bridge:** proprietary models — none. Suunto 7 — ADB (Wear OS rules apply).
- **User-removable surface:** phone-side app integrations for proprietary models. Suunto 7 uses the Wear OS surface.
- **Restore surface:** store reinstall (proprietary models). Wear OS restore paths (Suunto 7).
- **Debloat verdict:** proprietary models — refuse. Suunto 7 — treat as Wear OS. UNCERTAIN — the Suunto 7 Wear OS version is not verified in-session.

### 3.10 Fossil Gen 5 (legacy Wear OS 2)

- **OS family:** Wear OS 2 (Android-based legacy).
- **Package concept:** Android APKs through the Play Store.
- **Hardware anchor:** Snapdragon Wear 3100 SoC [https://smartwatchspex.com/fossil-the-carlyle-hr-gen-5-specs/]. 1 GB RAM [https://www.neowin.net/reviews/fossil-gen-5-smartwatch-review-the-best-wear-os-smartwatch/]. Up to 8 GB storage on the LTE model [https://www.fossil.com/products/gen-5-lte-smartwatch-black-silicone/FTW40531F.html].
- **Connection bridge:** ADB over the legacy settings flow. UNCERTAIN — this session verified the Wear OS 3 or newer pairing flow [https://developer.android.com/training/wearables/get-started/debug-wifi], but not the exact Gen 5 settings path.
- **User-removable surface:** the standard Wear OS pm family, plus Play Store management.
- **Restore surface:** pm install-existing, or a factory re-flash.
- **Debloat verdict:** allow as an Android-family device, with the legacy-build caution. UNCERTAIN — no verified Fossil package dump exists. See the compatibility matrix for the evidence rule.

## 4. Common Design Differences from Android

The platforms above differ from Android in four structural ways:

1. **Closed app stores.** A vendor controls the store gate. Users see only curated content types. Examples: Connect IQ content classes [https://developer.garmin.com/connect-iq/overview/], and Zepp Mini Programs [https://developer.zepp.com/os/home].
2. **No package enumeration.** The Android command pm list packages has no equivalent on these platforms. The engine cannot discover installed packages. For the Android contrast, see the verified Wear OS dump [https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/].
3. **No user-space package state.** The ideas "disable for user 0" and "restore a removed system package" do not exist here. Removal is store-level delete, or nothing.
4. **Engineer-only bridges.** sdb and vendor SDKs exist. They connect developer tools, not debloat actions [https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md], [https://developer.garmin.com/connect-iq/sdk/].

Consequence: the debloat tool has no reversible, package-level operation on these platforms.

## 5. Safety Information

Why the debloat tools in this repository refuse to operate on these platforms:

1. **No target.** Without enumeration, the tool cannot name a package. A "debloat" step would act blind.
2. **No reversible state.** Android user-scope uninstall keeps the APK on the device and allows a restore. The verified Wear OS thread shows that layer [https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/]. These platforms have no such layer. Deletion is final at the store level.
3. **No sanctioned bridge.** sdb, Xcode, and vendor SDKs exist for development. Using them as debloat channels is unsanctioned and out of scope [https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md].
4. **Brick risk from forced methods.** A community hack exists for Huawei [https://consumer.huawei.com/en/community/details/topicId-161034/]. Forced experiments on closed firmware can leave an unusable device. On Wear OS, a wrong batch of disables already produced a recovery failure. This shows the risk class [https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/].
5. **Closing surfaces.** Fitbit ends third-party app and clock installs on 28 November 2026 [https://support.google.com/googlehealth/answer/14226056]. A tool that acts otherwise misleads the user.

Required refusals:

- The engine must refuse every command against these platforms.
- The refusal prints the matching platform record and its verdict.
- The engine must not run hidden or forced commands after a refusal.

## 6. UNCERTAIN Facts Register

Codes U-01 onward. Each entry states the item, the label, and the reason it stayed UNCERTAIN.

- **U-01 — Wear OS 5.1 wireless-debugging restriction.** UNCERTAIN. No source supported the claim in any search this session. Do not publish as fact. (Cross-file item; the matrix keeps it too.)
- **U-02 — Pixel Watch debloat package list.** UNCERTAIN. No dedicated Pixel package dump was found. Only Google-common names from the Galaxy Watch dumps count as verified evidence [https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/].
- **U-03 — Pixel Watch 3 SoC.** UNCERTAIN. The reported Exynos W930 had no fetched source in this session.
- **U-04 — "SW5180" part number.** UNCERTAIN. No fetched source contained this part number. Do not cite it.
- **U-05 — Fitbit EEA mid-2024 app removal.** UNVERIFIED. Secondary aggregator sources only. No primary URL was fetched.
- **U-06 — Xiaomi Watch 2 / 2 Pro Wear OS version.** UNCERTAIN. The Wear OS platform itself is verified [https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/]. The version number is not.
- **U-07 — Mobvoi, Casio, Withings package lists.** UNCERTAIN. No brand package dumps were collected this session.
- **U-08 — Fossil Gen 5 package names.** UNCERTAIN. No Fossil dump exists in the evidence base.
- **U-09 — Tizen package format name (TPK/TPKG).** UNCERTAIN. General knowledge only. No fetched source confirmed the format or the channel in-session.
- **U-10 — Tizen sdb enumeration commands.** UNCERTAIN. The sdb tool itself is documented [https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md]. An installed-app list command was not verified.
- **U-11 — Suunto 7 Wear OS version.** UNCERTAIN. The Wear OS platform itself is verified [https://www.suunto.com/Support/Product-support/suunto_7/suunto_7/wear-os-by-google/]. The version is not.
- **U-12 — Samsung Tizen to Wear OS switch boundary.** UNCERTAIN. This session did not fetch a source for the model boundary.
- **U-13 — Apple removable built-in app set across watchOS versions.** UNCERTAIN. The "watchOS 9.4 or later" capability is verified [https://support.apple.com/en-us/118582]. The complete current set is not.
- **U-14 — Fitbit Sense 2 / Versa 4 with no third-party store.** UNVERIFIED. Community-level knowledge only.

## 7. References

Apple (official):

- https://support.apple.com/en-us/109028
- https://support.apple.com/en-us/118582

Garmin (official):

- https://apps.garmin.com/en-US/
- https://developer.garmin.com/connect-iq/overview/
- https://developer.garmin.com/connect-iq/sdk/
- https://support.garmin.com/en-US/?faq=DnXHorjkxT106X9AGsOoC8

Google — Fitbit (official):

- https://support.google.com/googlehealth/answer/14226056

Huawei (community and issue trackers):

- https://xdaforums.com/tags/huawei-watch/
- https://github.com/LiteOS/LiteOS/issues/630
- https://consumer.huawei.com/en/community/details/topicId-161034/

Samsung — Tizen (official docs):

- https://github.com/Samsung/tizen-docs/blob/master/docs/sdk-tools/baseline-sdk/common-tools/smart-development-bridge.md

Suunto (official):

- https://www.suunto.com/Support/Product-support/suunto_7/suunto_7/wear-os-by-google/
- https://www.qualcomm.com/wearables/device-finder/suunto-suunto-7

Xiaomi, Zepp, Polar (official and comparison pages):

- https://www.mi.com/global/product/xiaomi-watch-s1-pro/
- https://www.gizmochina.com/guides/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-comparison/
- https://www.mundoxiaomi.com/especiales/xiaomi-watch-2-pro-vs-xiaomi-watch-s1-pro-estas-principales-diferencias-mejores-relojes-inteligentes-marca
- https://versus.com/en/xiaomi-watch-2-pro-vs-xiaomi-watch-s1
- https://developer.zepp.com/os/home
- https://docs.zepp.com/docs/intro/using/
- https://www.polar.com/en/compatible-apps/
- https://support.polar.com/us-en/what-third-party-apps-and-devices-are-compatible-with-polar-products

Fossil Gen 5 (reviews and product pages):

- https://www.androidauthority.com/fossil-gen-5-smartwatch-review-1020794/
- https://smartwatchspex.com/fossil-the-carlyle-hr-gen-5-specs/
- https://www.fossil.com/products/gen-5-lte-smartwatch-black-silicone/FTW40531F.html
- https://www.neowin.net/reviews/fossil-gen-5-smartwatch-review-the-best-wear-os-smartwatch/

Cross-reference (Android-family evidence, used for contrast):

- https://developer.android.com/training/wearables/get-started/debug-wifi
- https://xdaforums.com/t/wearos-watch-adb-commands-disable-enable-uninstall-restore-system-app-install-pull-apps.4324063/
- https://xdaforums.com/t/galaxy-watch-6-7-adb-debloat-connecting.4613093/

END OF DOCUMENT.
