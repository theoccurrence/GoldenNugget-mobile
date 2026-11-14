// GENERATED FILE — do not edit by hand.
//
// Mobile-only rows: registry entries this fork adds on top of GoldenNugget's
// `src/tweaks/registry.py`.  They have no desktop counterpart, so they are
// emitted from the generator's own table rather than from the reference.
// Regenerate all parts with:
//
//     scripts/gen-tweaks-from-goldennugget.py [--goldennugget <path>]
//
// Kept in their own file so the reference's own chunks stay byte-identical to
// a regeneration; `TweakCatalog.all` appends this array after `registry9`.

import Foundation

extension TweakCatalog {
    static let registryMobileOnly: [TweakSpec] = [
        TweakSpec(
            id: "IPhoneMirroring",
            section: .internalOptions,
            title: "iPhone Mirroring (Ineligible Regions)",
            location: .siriAIOverrides,
            key: "IPhoneMirroring",
            value: .bool(true),
            kind: .toggle,
            minValue: 0.0,
            maxValue: 999.0,
            step: 1.0,
            minVersion: "27.0",
            maxVersion: nil,
            iphoneOnly: true,
            ipadOnly: false,
            disabled: false,
            detail: "Forces OS_ELIGIBILITY_DOMAIN_IRON (27) eligible. The iPhone evaluates its own mirroring region check locally and signs it into the authentication response, so the Mac-side patch alone is rejected on iOS 26+. Independent of Apple Intelligence; the Mac still needs its own IRON patch.",
            multiValues: nil,
            reversibleBoolean: false,
            requiresDynamicIsland: false,
            showWhenUnavailable: false,
            factory: "SiriAITweak",
            offValue: nil,
            integerBoolean: false,
            requiresCameraControl: false,
            requiresActionButton: false,
            requiresHomeButton: false,
            requiresAlwaysOn: false,
            warning: "Requires an unencrypted protective backup and a reboot. The device keeps ONE override map: with Siri AI also selected the combined archive is written, otherwise this replaces ALL existing eligibility overrides. Other builds are untested. Turning this switch off does not undo an applied override; use Reset Siri AI Overrides and apply.",
            requires: [],
            exclusiveWith: "ResetSiriAIOverrides",
            unavailableReason: nil,
            supportedModels: []
        ),
    ]
}