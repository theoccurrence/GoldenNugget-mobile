// GENERATED FILE — do not edit by hand.
//
// Source of truth: GoldenNugget's `src/tweaks/registry.py` (the tweak
// spec table) and `src/tweaks/basic_plist_locations.py` (the
// `FileLocation` enum).  Regenerate with:
//
//     scripts/gen-tweaks-from-goldennugget.py [--goldennugget <path>]
//
// The port is a generation, not a retype: the table is emitted from
// the reference module itself, so a tweak added upstream appears here
// without a hand edit and a spec cannot silently drift from the source.
// The rows themselves live in the `TweakCatalog+RegistryN.swift` chunks;
// this file carries the enums and the assembly.

import Foundation

/// An absolute device path a tweak writes to.
///
/// Ported from GoldenNugget's `FileLocation` enum; the raw value is the
/// absolute path, and `TweakDomainMap` turns it into the
/// `(backup domain, relative path)` pair a restorable row needs.
enum TweakFileLocation: String, CaseIterable, Sendable {
    case featureflags = "/var/preferences/FeatureFlags/Global.plist"
    case ota = "/var/Managed Preferences/mobile/com.apple.MobileAsset.plist"
    case springboard = "/var/Managed Preferences/mobile/com.apple.springboard.plist"
    case springboardPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.springboard.plist"
    case footnote = "/var/containers/Shared/SystemGroup/systemgroup.com.apple.configurationprofiles/Library/ConfigurationProfiles/SharedDeviceConfiguration.plist"
    case airdrop = "/var/Managed Preferences/mobile/com.apple.sharingd.plist"
    case nanoregistry = "/var/mobile/Library/Preferences/com.apple.NanoRegistry.plist"
    case chronod = "/var/Managed Preferences/mobile/com.apple.chronod.plist"
    case ambient = "/var/Managed Preferences/mobile/com.apple.ambient.plist"
    case statusBarOverridesArchive = "/var/mobile/Library/SpringBoard/StatusBarOverrides.archive"
    case accessibility = "/var/Managed Preferences/mobile/com.apple.Accessibility.plist"
    case siriAIOverrides = "/var/containers/Data/SystemGroup/com.apple.eligibilityd/Library/Caches/NeverRestore/eligibility_overrides.data"
    case globalPreferences = "/var/Managed Preferences/mobile/.GlobalPreferences.plist"
    case globalPreferencesHomeDomain = "/var/mobile/Library/Preferences/.GlobalPreferences.plist"
    case appStore = "/var/Managed Preferences/mobile/com.apple.AppStore.plist"
    case backboardd = "/var/Managed Preferences/mobile/com.apple.backboardd.plist"
    case coreMotion = "/var/Managed Preferences/mobile/com.apple.CoreMotion.plist"
    case pasteboard = "/var/Managed Preferences/mobile/com.apple.Pasteboard.plist"
    case notes = "/var/Managed Preferences/mobile/com.apple.mobilenotes.plist"
    case keyboardPreferences = "/var/Managed Preferences/mobile/com.apple.keyboard.preferences.plist"
    case uikit = "/var/Managed Preferences/mobile/com.apple.UIKit.plist"
    case swiftui = "/var/Managed Preferences/mobile/com.apple.SwiftUI.plist"
    case disabledDaemons = "/var/db/com.apple.xpc.launchd/disabled.plist"
    case screentime = "/var/mobile/Library/Preferences/com.apple.ScreenTimeAgent.plist"
    case chronodPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.chronod.plist"
    case prototypeToolsPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.PrototypeTools.plist"
    case uikitPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.UIKit.plist"
    case carrierBundleOverlay = "/var/mobile/Library/Carrier Bundles/Overlay"
    case keyboardPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.keyboard.preferences.plist"
    case keyboardContinuousPath = "/var/mobile/Library/Preferences/com.apple.keyboard.ContinuousPath.plist"
    case locationPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.locationd.plist"
    case swiftuiPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.SwiftUI.plist"
    case accessibilityPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.Accessibility.plist"
    case applicationAccess = "/var/Managed Preferences/mobile/com.apple.applicationaccess.plist"
    case celestialPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.celestial.plist"
    case mobilecalPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.mobilecal.plist"
    case apsPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.apsd.plist"
    case avatarPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.AvatarUI.Staryu.plist"
    case suggestionsPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.suggestions.plist"
    case locationStatusBarPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.locationd.StatusBarIconManager.plist"
    case preferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.Preferences.plist"
    case imdPersistencePreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.imdpersistence.IMDPersistenceAgent.plist"
    case diagnosticExtensionTracker = "/var/mobile/Library/Preferences/com.apple.DiagnosticExtensions.extensionTracker.plist"
    case spotlightUIPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.spotlightui.plist"
    case adPlatformsPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.AdPlatforms.plist"
    case itunesstoredPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.itunesstored.plist"
    case coreSpotlightUIPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.corespotlightui.plist"
    case backgroundSystemTaskPreferencesHomeDomain = "/var/mobile/Library/Preferences/com.apple.bg.system.task.plist"
    case none = ""
}

/// A tweaks-page section.  Raw values match GoldenNugget's `Section` enum.
enum TweakSection: String, CaseIterable, Identifiable, Sendable {
    case posterBoard = "PosterBoard"
    case liquidGlass = "Liquid Glass"
    case springboard = "SpringBoard"
    case internalOptions = "Internal Options"
    case daemons = "Daemons to Disable"
    var id: String { rawValue }
}

/// The UI editor a spec wants.  Matches GoldenNugget's `Kind` enum.
enum TweakKind: Sendable {
    case toggle
    case text
    case number
    /// Edits fields inside the wallpaper archives a restore already
    /// carries (`PosterKitOverrides`).  Staged by the engine, not here.
    case posterArchive
    /// Writes a wallpaper dictionary into SpringBoard preferences.
    case wallpaper
    /// A single wallpaper feature flag.  No registry spec uses this yet;
    /// the case keeps the port's enum in lockstep with the reference's.
    case posterFlag
}

/// Every registry-defined tweak, in the reference's own order.
///
/// Iteration order is load-bearing: the compiler merges several tweaks into
/// one plist, and GoldenNugget iterates `tweaks` in this same order, so a
/// later key wins exactly as it does upstream.  Do not sort this array.
enum TweakCatalog {
    /// Every registry-defined tweak, in the reference's own order, then the
    /// fork's own mobile-only rows.  The mobile-only array is separate so the
    /// reference chunks stay byte-identical to a regeneration.
    static let all: [TweakSpec] = registry0 + registry1 + registry2 + registry3 + registry4 + registry5 + registry6 + registry7 + registry8 + registry9 + registryMobileOnly

    /// The daemon groups, appended after the registry rows.  They are not in
    /// `registry.py` upstream -- `gen-daemons-from-goldennugget.py` emits them
    /// from `daemons_tweak.py` -- and they are last so every registry key still
    /// merges into a shared plist before any daemon label does.
    static let allWithDaemons: [TweakSpec] = all + daemonSpecs + [screenTimeSpec]

    static let byID: [String: TweakSpec] =
        Dictionary(uniqueKeysWithValues: allWithDaemons.map { ($0.id, $0) })

    static func inSection(_ section: TweakSection) -> [TweakSpec] {
        all.filter { $0.section == section }
    }
}


extension TweakCatalog {
    /// The eligibility-override archives this app can deliver, keyed by the
    /// exact set of enabled operations.
    ///
    /// The device holds exactly ONE override map
    /// (`SysContainerDomain-com.apple.eligibilityd` / `Library/Caches/NeverRestore/
    /// eligibility_overrides.data`), so two enabled operations cannot each write
    /// their own file: the set of enabled operations selects one pre-combined
    /// archive.  `eligibilityCombination(for:)` maps a selection to a key.
    ///
    /// Every entry is an opaque `NSKeyedArchive` from Apple's own
    /// `NSKeyedArchiver` and is never reserialized; the runtime verifies each
    /// against `eligibilityHashes` before it reaches the device.
    ///
    /// Sources: `siri` and `reset` are the Project Linwood archives the desktop
    /// ships (`siri_ai.HASHES`).  `mirroring` and `siri+mirroring` were produced
    /// by Project Linwood's `tools/override_archive/make_override_archive.swift`
    /// on 2026-11-14 for `OS_ELIGIBILITY_DOMAIN_IRON` (27).
    static let eligibilityArchives: [String: Data] = [
        "siri": Data(base64Encoded: "YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMSAAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGvEBALDBEdHh8gJCUsLzQ6Ozw/VSRudWxs0g0ODxBbb3ZlcnJpZGVNYXBWJGNsYXNzgAKAD9MSEw4UGBxXTlMua2V5c1pOUy5vYmplY3RzoxUWF4ADgASABaMZGhuABoAJgAqADhB6EJsQYNIhDiIjVmFuc3dlcoAHgAgQBNImJygpWiRjbGFzc25hbWVYJGNsYXNzZXNfEBdFbGlnaWJpbGl0eU92ZXJyaWRlRGF0YaIqK18QF0VsaWdpYmlsaXR5T3ZlcnJpZGVEYXRhWE5TT2JqZWN00iEOIiOAB4AI0yEwDiIyI1djb250ZXh0gAeAC4AI0xITDjU3HKE2gAyhOIANgA5fECtPU19FTElHSUJJTElUWV9DT05URVhUX0xJTldPT0RfQVZBSUxBQklMSVRZEALSJic9PlxOU0RpY3Rpb25hcnmiPSvSJidAQV8QE0VsaWdpYmlsaXR5T3ZlcnJpZGWiQitfEBNFbGlnaWJpbGl0eU92ZXJyaWRlAAgAEQAaACQAKQAyADcASQBMAFEAUwBmAGwAcQB9AIQAhgCIAI8AlwCiAKYAqACqAKwAsACyALQAtgC4ALoAvAC+AMMAygDMAM4A0ADVAOAA6QEDAQYBIAEpAS4BMAEyATkBQQFDAUUBRwFOAVABUgFUAVYBWAGGAYgBjQGaAZ0BogG4AbsAAAAAAAACAQAAAAAAAABDAAAAAAAAAAAAAAAAAAAB0Q==")!,
        "reset": Data(base64Encoded: "YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMSAAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGlCwwRFx1VJG51bGzSDQ4PEFtvdmVycmlkZU1hcFYkY2xhc3OAAoAE0xITDhQVFldOUy5rZXlzWk5TLm9iamVjdHOgoIAD0hgZGhtaJGNsYXNzbmFtZVgkY2xhc3Nlc1xOU0RpY3Rpb25hcnmiGhxYTlNPYmplY3TSGBkeH18QE0VsaWdpYmlsaXR5T3ZlcnJpZGWiIBxfEBNFbGlnaWJpbGl0eU92ZXJyaWRlCBEaJCkyN0lMUVNZX2Rwd3l7goqVlpeZnqmyv8LL0ObpAAAAAAAAAQEAAAAAAAAAIQAAAAAAAAAAAAAAAAAAAP8=")!,
        "mirroring": Data(base64Encoded: "YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMSAAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGpCwwRGRoeHyYqVSRudWxs0g0ODxBbb3ZlcnJpZGVNYXBWJGNsYXNzgAKACNMSEw4UFhhXTlMua2V5c1pOUy5vYmplY3RzoRWAA6EXgASABxAb0hsOHB1WYW5zd2VygAWABhAE0iAhIiNaJGNsYXNzbmFtZVgkY2xhc3Nlc18QF0VsaWdpYmlsaXR5T3ZlcnJpZGVEYXRhoiQlXxAXRWxpZ2liaWxpdHlPdmVycmlkZURhdGFYTlNPYmplY3TSICEnKF8QE05TTXV0YWJsZURpY3Rpb25hcnmjJyklXE5TRGljdGlvbmFyedIgISssXxATRWxpZ2liaWxpdHlPdmVycmlkZaItJV8QE0VsaWdpYmlsaXR5T3ZlcnJpZGUACAARABoAJAApADIANwBJAEwAUQBTAF0AYwBoAHQAewB9AH8AhgCOAJkAmwCdAJ8AoQCjAKUAqgCxALMAtQC3ALwAxwDQAOoA7QEHARABFQErAS8BPAFBAVcBWgAAAAAAAAIBAAAAAAAAAC4AAAAAAAAAAAAAAAAAAAFw")!,
        "siri+mirroring": Data(base64Encoded: "YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMSAAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGvEBMLDBEfICEiIycoLzI3PT4/QkVIVSRudWxs0g0ODxBbb3ZlcnJpZGVNYXBWJGNsYXNzgAKAEtMSEw4UGR5XTlMua2V5c1pOUy5vYmplY3RzpBUWFxiAA4AEgAWABqQaGxwdgAeACoALgBCAERB6EBsQYBCb0iQOJSZWYW5zd2VygAiACRAE0ikqKyxaJGNsYXNzbmFtZVgkY2xhc3Nlc18QF0VsaWdpYmlsaXR5T3ZlcnJpZGVEYXRhoi0uXxAXRWxpZ2liaWxpdHlPdmVycmlkZURhdGFYTlNPYmplY3TSJA4lJoAIgAnTJDMOJTUmV2NvbnRleHSACIAMgAnTEhMOODo8oTmADaE7gA6AD18QK09TX0VMSUdJQklMSVRZX0NPTlRFWFRfTElOV09PRF9BVkFJTEFCSUxJVFkQAtIpKkBBXE5TRGljdGlvbmFyeaJALtIkDiUmgAiACdIpKkZHXxATTlNNdXRhYmxlRGljdGlvbmFyeaNGQC7SKSpJSl8QE0VsaWdpYmlsaXR5T3ZlcnJpZGWiSy5fEBNFbGlnaWJpbGl0eU92ZXJyaWRlAAgAEQAaACQAKQAyADcASQBMAFEAUwBpAG8AdACAAIcAiQCLAJIAmgClAKoArACuALAAsgC3ALkAuwC9AL8AwQDDAMUAxwDJAM4A1QDXANkA2wDgAOsA9AEOAREBKwE0ATkBOwE9AUQBTAFOAVABUgFZAVsBXQFfAWEBYwGRAZMBmAGlAagBrQGvAbEBtgHMAdAB1QHrAe4AAAAAAAACAQAAAAAAAABMAAAAAAAAAAAAAAAAAAACBA==")!,
    ]

    /// sha256 of each embedded archive, verbatim.
    static let eligibilityHashes: [String: String] = [
        "siri": "4290e93faf86fd4f0d38364d2bb67398d9acb77f637555790c3339ad44f64d17",
        "mirroring": "fb5eb97de65dd31268303af3282b8e1f5b8f1c7b9bb20ba1eca770e6fa1af05a",
        "siri+mirroring": "65ad959e0920ea1136d011dd6847df60146d937dcf502aa22f0804812bd32b68",
        "reset": "f9b394804d478874f40eedcade937ab1d4a73773b4c8ed018ce51fb407a00818",
    ]

    /// The registry ids that write the one override map, in apply order.
    static let eligibilityOperationIDs = ["SiriAI", "IPhoneMirroring", "ResetSiriAIOverrides"]

    /// The archive key for a set of enabled eligibility operations.
    ///
    /// `reset` wins: an empty map is the only combination a reset can mean, and
    /// the UI already refuses reset alongside either enable operation
    /// (`exclusiveWith`).  `siri` and `mirroring` combine into the union
    /// archive, because the one override map has to carry both.
    static func eligibilityCombination(for ids: [String]) -> String? {
        guard !ids.isEmpty else { return nil }
        if ids.contains("ResetSiriAIOverrides") { return "reset" }
        switch (ids.contains("SiriAI"), ids.contains("IPhoneMirroring")) {
        case (true, true): return "siri+mirroring"
        case (true, false): return "siri"
        case (false, true): return "mirroring"
        case (false, false): return nil
        }
    }
}

/// Device capabilities generated from desktop device_capabilities.py.
enum TweakDeviceCapabilities {
    static func hasDynamicIsland(_ model: String) -> Bool {
        let models: Set<String> = [
            "iPhone15,2",
            "iPhone15,3",
            "iPhone15,4",
            "iPhone15,5",
            "iPhone16,1",
            "iPhone16,2",
            "iPhone17,1",
            "iPhone17,2",
            "iPhone17,3",
            "iPhone17,4",
            "iPhone18,1",
            "iPhone18,2",
            "iPhone18,3",
            "iPhone18,4",
        ]
        return models.contains(model.trimmingCharacters(in: .whitespacesAndNewlines))
    }
    static func hasCameraControl(_ model: String) -> Bool {
        let models: Set<String> = [
            "iPhone17,1",
            "iPhone17,2",
            "iPhone17,3",
            "iPhone17,4",
            "iPhone18,1",
            "iPhone18,2",
            "iPhone18,3",
            "iPhone18,4",
            "iPhone19,2",
            "iPhone19,3",
            "iPhone19,7",
        ]
        return models.contains(model.trimmingCharacters(in: .whitespacesAndNewlines))
    }
    static func hasActionButton(_ model: String) -> Bool {
        let models: Set<String> = [
            "iPhone16,1",
            "iPhone16,2",
            "iPhone17,1",
            "iPhone17,2",
            "iPhone17,3",
            "iPhone17,4",
            "iPhone17,5",
            "iPhone18,1",
            "iPhone18,2",
            "iPhone18,3",
            "iPhone18,4",
            "iPhone18,5",
            "iPhone19,2",
            "iPhone19,3",
            "iPhone19,7",
        ]
        return models.contains(model.trimmingCharacters(in: .whitespacesAndNewlines))
    }
    static func hasHomeButton(_ model: String) -> Bool {
        let models: Set<String> = [
            "iPad11,1",
            "iPad11,2",
            "iPad11,3",
            "iPad11,4",
            "iPad11,6",
            "iPad11,7",
            "iPad12,1",
            "iPad12,2",
            "iPad5,1",
            "iPad5,2",
            "iPad5,3",
            "iPad5,4",
            "iPad6,11",
            "iPad6,12",
            "iPad6,3",
            "iPad6,4",
            "iPad6,7",
            "iPad6,8",
            "iPad7,1",
            "iPad7,11",
            "iPad7,12",
            "iPad7,2",
            "iPad7,3",
            "iPad7,4",
            "iPad7,5",
            "iPad7,6",
            "iPhone10,1",
            "iPhone10,2",
            "iPhone10,4",
            "iPhone10,5",
            "iPhone12,8",
            "iPhone14,6",
            "iPhone8,1",
            "iPhone8,2",
            "iPhone8,4",
            "iPhone9,1",
            "iPhone9,2",
            "iPhone9,3",
            "iPhone9,4",
        ]
        return models.contains(model.trimmingCharacters(in: .whitespacesAndNewlines))
    }
    static func hasAlwaysOn(_ model: String) -> Bool {
        let models: Set<String> = [
            "iPhone15,2",
            "iPhone15,3",
            "iPhone16,1",
            "iPhone16,2",
            "iPhone17,1",
            "iPhone17,2",
            "iPhone18,1",
            "iPhone18,2",
            "iPhone18,3",
            "iPhone18,4",
            "iPhone19,2",
            "iPhone19,3",
            "iPhone19,7",
        ]
        return models.contains(model.trimmingCharacters(in: .whitespacesAndNewlines))
    }
}
