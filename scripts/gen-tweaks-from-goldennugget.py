#!/usr/bin/env python3
"""Generate Nugget/Core/TweakCatalog*.swift from GoldenNugget's tweak registry.

Why generate instead of retype: the reference defines every plist tweak exactly
once, as a ``TweakSpec`` in ``src/tweaks/registry.py`` (id / section / title /
location / key / default value / kind / version + device gating / description).
That table is ~130 entries of pure data.  Retyping it into Swift would be a
transcription exercise with 130 chances to drift, and any later upstream tweak
would have to be copied by hand.  This script imports the reference module and
emits the Swift table from it, so a spec cannot disagree with the source.

The reference module imports ``PySide6.QtCore.QT_TRANSLATE_NOOP`` (a no-op marker
for lupdate).  Importing PySide6 would pull in a Qt install this script has no
business needing, so a stub module is installed first: the marker is
identity-with-strings and nothing else in the tweak-definition chain needs Qt.
``src/__init__.py`` is empty and ``src/tweaks/__init__.py`` is empty, so the
import stops at the two data modules (registry + basic_plist_locations).

The rows are emitted as ``TweakCatalog+RegistryN.swift`` chunks of CHUNK_SIZE
instead of one giant ``static let all: [TweakSpec]`` array literal: Swift
type-checks an array literal as a single expression, and a 369-row literal made
the per-file frontend want gigabytes of memory (the build was OOM-killed for
that alone, with or without batched compilation).

Usage:
    scripts/gen-tweaks-from-goldennugget.py                 # write the catalog
    scripts/gen-tweaks-from-goldennugget.py --check          # exit 1 on drift
    scripts/gen-tweaks-from-goldennugget.py --goldennugget ~/GoldenNugget
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "Nugget" / "Core" / "TweakCatalog.swift"
DEFAULT_SOURCE = os.path.expanduser("~/GoldenNugget")

# Python Section member name -> Swift case name.
DAEMONS_SECTION_TITLE = "Daemons to Disable"

SECTION_CASES = {
    "POSTERBOARD": "posterBoard",
    "LIQUID_GLASS": "liquidGlass",
    "SPRINGBOARD": "springboard",
    "INTERNAL": "internalOptions",
}
KIND_CASES = {"SWITCH": "toggle", "TEXT": "text", "NUMBER": "number",
              "POSTER_ARCHIVE": "posterArchive", "WALLPAPER": "wallpaper",
              "POSTER_FLAG": "posterFlag"}

# Factories whose instance is a `TriStateBooleanPlistTweak` (possibly through
# `FeatureFlagTweak`): the selection is "used on" / "used off" / "not used",
# and switching the master toggle off discards the stored state instead of
# persisting an off value the way `ExperimentalBooleanPlistTweak` does.
TRI_STATE_FACTORIES = {
    "TriStateBooleanPlistTweak",
    "FeatureFlagTweak",
    "GlassFeatureFlagTweak",
    "UIKitInternalBooleanTweak",
    "MailSearchReceiverPreference",
}
# Factories the compiler dispatches on by name; anything else must be in one of
# the sets above or the plain shapes (`BasicPlistTweak`, `AdvancedPlistTweak`,
# `ExperimentalBooleanPlistTweak`, `ResettableNumericPreferenceTweak`,
# `OptionalBundlePreferenceTweak`, `SiriAITweak`, `ReversibleBooleanPlistTweak`).
SUPPORTED_NAMED_FACTORIES = {
    "TriStateBooleanPlistTweak", "FeatureFlagTweak", "GlassFeatureFlagTweak",
    "UIKitInternalBooleanTweak", "MailSearchReceiverPreference",
    "ResearchOnlyTweak", "NestedNumericPreference", "DiagnosticTrackerDates",
    "MailSearchTaskBaseDate", "DiscreteScrollDurationTweak",
    "DirectionalScrollDurationTweak", "UIKitAnimationScaleTweak",
    "GlassLegibilityTweak", "DisableDynamicIslandTweak",
    "PosterKitOverrides", "WallpaperPreferencesTweak",
}

# How many registry rows one chunk file carries.  Small files of small
# initializers keep every per-file compile job bounded; see the module docstring.
CHUNK_SIZE = 40

# --------------------------------------------------------------------------
# Mobile-only additions
# --------------------------------------------------------------------------
# Rows this fork adds on top of the reference registry.  They are emitted
# verbatim into `TweakCatalog+RegistryMobileOnly.swift`, so the reference
# chunks stay byte-identical to a regeneration.
MOBILE_ONLY_CHUNK = "TweakCatalog+RegistryMobileOnly.swift"

MOBILE_ONLY_ROWS = '''        TweakSpec(
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
        ),'''

# `mirroring` and `siri+mirroring` are the IRON (27) eligibility archives,
# produced by Project Linwood's `tools/override_archive/make_override_archive.swift`
# on 2026-11-14 and carried here as base64 so a regeneration needs no extra
# checkout.  `siri` and `reset` still come from desktop's `siri_ai`, so the
# desktop byte contract is unchanged.  The device keeps exactly ONE override
# map, hence one archive per combination of enabled operations.
MOBILE_ONLY_ARCHIVES_B64 = {
    "mirroring": "YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMSAAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGpCwwRGRoeHyYqVSRudWxs0g0ODxBbb3ZlcnJpZGVNYXBWJGNsYXNzgAKACNMSEw4UFhhXTlMua2V5c1pOUy5vYmplY3RzoRWAA6EXgASABxAb0hsOHB1WYW5zd2VygAWABhAE0iAhIiNaJGNsYXNzbmFtZVgkY2xhc3Nlc18QF0VsaWdpYmlsaXR5T3ZlcnJpZGVEYXRhoiQlXxAXRWxpZ2liaWxpdHlPdmVycmlkZURhdGFYTlNPYmplY3TSICEnKF8QE05TTXV0YWJsZURpY3Rpb25hcnmjJyklXE5TRGljdGlvbmFyedIgISssXxATRWxpZ2liaWxpdHlPdmVycmlkZaItJV8QE0VsaWdpYmlsaXR5T3ZlcnJpZGUACAARABoAJAApADIANwBJAEwAUQBTAF0AYwBoAHQAewB9AH8AhgCOAJkAmwCdAJ8AoQCjAKUAqgCxALMAtQC3ALwAxwDQAOoA7QEHARABFQErAS8BPAFBAVcBWgAAAAAAAAIBAAAAAAAAAC4AAAAAAAAAAAAAAAAAAAFw",
    "siri+mirroring": "YnBsaXN0MDDUAQIDBAUGBwpYJHZlcnNpb25ZJGFyY2hpdmVyVCR0b3BYJG9iamVjdHMSAAGGoF8QD05TS2V5ZWRBcmNoaXZlctEICVRyb290gAGvEBMLDBEfICEiIycoLzI3PT4/QkVIVSRudWxs0g0ODxBbb3ZlcnJpZGVNYXBWJGNsYXNzgAKAEtMSEw4UGR5XTlMua2V5c1pOUy5vYmplY3RzpBUWFxiAA4AEgAWABqQaGxwdgAeACoALgBCAERB6EBsQYBCb0iQOJSZWYW5zd2VygAiACRAE0ikqKyxaJGNsYXNzbmFtZVgkY2xhc3Nlc18QF0VsaWdpYmlsaXR5T3ZlcnJpZGVEYXRhoi0uXxAXRWxpZ2liaWxpdHlPdmVycmlkZURhdGFYTlNPYmplY3TSJA4lJoAIgAnTJDMOJTUmV2NvbnRleHSACIAMgAnTEhMOODo8oTmADaE7gA6AD18QK09TX0VMSUdJQklMSVRZX0NPTlRFWFRfTElOV09PRF9BVkFJTEFCSUxJVFkQAtIpKkBBXE5TRGljdGlvbmFyeaJALtIkDiUmgAiACdIpKkZHXxATTlNNdXRhYmxlRGljdGlvbmFyeaNGQC7SKSpJSl8QE0VsaWdpYmlsaXR5T3ZlcnJpZGWiSy5fEBNFbGlnaWJpbGl0eU92ZXJyaWRlAAgAEQAaACQAKQAyADcASQBMAFEAUwBpAG8AdACAAIcAiQCLAJIAmgClAKoArACuALAAsgC3ALkAuwC9AL8AwQDDAMUAxwDJAM4A1QDXANkA2wDgAOsA9AEOAREBKwE0ATkBOwE9AUQBTAFOAVABUgFZAVsBXQFfAWEBYwGRAZMBmAGlAagBrQGvAbEBtgHMAdAB1QHrAe4AAAAAAAACAQAAAAAAAABMAAAAAAAAAAAAAAAAAAACBA==",
}
MOBILE_ONLY_ARCHIVE_HASHES = {
    "mirroring": "fb5eb97de65dd31268303af3282b8e1f5b8f1c7b9bb20ba1eca770e6fa1af05a",
    "siri+mirroring": "65ad959e0920ea1136d011dd6847df60146d937dcf502aa22f0804812bd32b68",
}
# Write order of the archive table, so a regeneration is deterministic.  This is
# the order the table is committed in (the two renamed Siri-era entries first,
# then the fork's additions).
ARCHIVE_ORDER = ["siri", "reset", "mirroring", "siri+mirroring"]


def chunk_name(number: int) -> str:
    return f"TweakCatalog+Registry{number}.swift"


def die(message: str):
    sys.exit(f"gen-tweaks: {message}")


def install_pyside_stub() -> None:
    """Make ``from PySide6.QtCore import QT_TRANSLATE_NOOP`` work without Qt."""
    pyside = types.ModuleType("PySide6")
    qtcore = types.ModuleType("PySide6.QtCore")
    qtcore.QT_TRANSLATE_NOOP = lambda context, text: text
    pyside.QtCore = qtcore
    sys.modules["PySide6"] = pyside
    sys.modules["PySide6.QtCore"] = qtcore


def load_reference(source: Path):
    if not (source / "src" / "tweaks" / "registry.py").is_file():
        die(f"{source} does not look like a GoldenNugget checkout "
            f"(no src/tweaks/registry.py)")
    install_pyside_stub()
    sys.path.insert(0, str(source))
    # Imported after the stub is installed, and only ever as the reference.
    from src.tweaks.basic_plist_locations import FileLocation  # noqa: E402
    from src.tweaks.registry import SPECS, Kind, Section  # noqa: E402
    return FileLocation, SPECS, Kind, Section


# --------------------------------------------------------------- Swift emission


def swift_string(value: str) -> str:
    escaped = (value.replace("\\", "\\\\")
                    .replace('"', '\\"')
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t"))
    return f'"{escaped}"'


def swift_value(value) -> str:
    # bool must be tested before int: Python's bool is an int subclass, so a
    # True would otherwise be emitted as `.int(1)`.
    if isinstance(value, bool):
        return f".bool({'true' if value else 'false'})"
    if isinstance(value, int):
        return f".int({value})"
    if isinstance(value, float):
        return f".double({value!r})"
    if isinstance(value, str):
        return f".string({swift_string(value)})"
    if isinstance(value, dict):
        # Nested dictionaries (`WallpaperPreferencesTweak`'s `{"none": …}`,
        # `_clock_animation`'s flag tree) ride the registry default as a
        # `.dictionary` value; `TweakValue.plistObject` hands the nested
        # mapping to `PropertyListSerialization` unchanged.  An empty mapping
        # is emitted as `[:]`: a bare `[]` gives the type-checker nothing to
        # infer the dictionary type from.
        if not value:
            return ".dictionary([:])"
        inner = ", ".join(f"{swift_string(key)}: {swift_value(item)}"
                          for key, item in value.items())
        return f".dictionary([{inner}])"
    raise SystemExit(f"gen-tweaks: unsupported plist value {value!r} "
                     f"({type(value).__name__})")


def swift_number(value: float) -> str:
    return repr(float(value))


def emit_spec(w, spec) -> None:
    """Emit one `TweakSpec(...)` initializer, arguments in registry order."""
    w(f"        TweakSpec(")
    w(f"            id: {swift_string(spec.id.name)},")
    w(f"            section: .{SECTION_CASES[spec.section.name]},")
    w(f"            title: {swift_string(spec.title)},")
    location = f".{spec.location.name}" if spec.location is not None else ".none"
    w(f"            location: {location},")
    w(f"            key: {swift_string(spec.key)},")
    instance = spec.factory() if spec.factory is not None else None
    factory = type(instance).__name__ if instance is not None else "BasicPlistTweak"
    # The selection value: the registry's own, except for the tri-state
    # shapes whose instance holds `None` until used — the port carries the
    # instance's `on_value` as the default instead (a tri-state row starts
    # "used on"), and a research-only row's unusable default is a harmless
    # `false` because the row can never be enabled.
    if spec.value is None and instance is not None and factory in TRI_STATE_FACTORIES:
        value = f".bool({'true' if instance.on_value else 'false'})"
    elif spec.value is None:
        value = ".bool(false)"
    else:
        value = swift_value(spec.value)
    w(f"            value: {value},")
    w(f"            kind: .{KIND_CASES[spec.kind.name]},")
    w(f"            minValue: {swift_number(spec.min_value)},")
    w(f"            maxValue: {swift_number(spec.max_value)},")
    w(f"            step: {swift_number(spec.step)},")
    w(f"            minVersion: {swift_string(spec.min_version) if spec.min_version else 'nil'},")
    w(f"            maxVersion: {swift_string(spec.max_version) if spec.max_version else 'nil'},")
    w(f"            iphoneOnly: {'true' if spec.iphone_only else 'false'},")
    w(f"            ipadOnly: {'true' if spec.ipad_only else 'false'},")
    w(f"            disabled: {'true' if spec.disabled else 'false'},")
    detail = spec.description
    if spec.id.name == "SiriAI":
        detail += " Mobile permits all iPhone models; devices without Apple Intelligence hardware are untested."
    w(f"            detail: {swift_string(detail) if detail else 'nil'},")
    reversible = instance is not None and factory in ("ReversibleBooleanPlistTweak", "DisableDynamicIslandTweak")
    if instance is not None and factory == "AdvancedPlistTweak":
        w("            multiValues: [")
        for key, value in instance.value.items():
            w(f"                {swift_string(key)}: {swift_value(value)},")
        w("            ],")
    else:
        w("            multiValues: nil,")
    w(f"            reversibleBoolean: {'true' if reversible else 'false'},")
    w(f"            requiresDynamicIsland: {'true' if spec.requires_dynamic_island else 'false'},")
    if factory in TRI_STATE_FACTORIES:
        w(f"            triState: true,")
        w(f"            onValue: {swift_value(instance.on_value)},")
        if factory in ("FeatureFlagTweak", "GlassFeatureFlagTweak"):
            w(f"            flagCategory: {swift_string(instance.flag_category)},")
            w(f"            flagNames: [{', '.join(swift_string(x) for x in instance.flag_names)}],")
    if factory == "NestedNumericPreference":
        w(f"            childKey: {swift_string(instance.child)},")
    w(f"            showWhenUnavailable: {'true' if spec.show_when_unavailable else 'false'},")
    w(f"            factory: {swift_string(factory)},")
    w(f"            offValue: {swift_value(instance.off_value) if factory == 'ExperimentalBooleanPlistTweak' else 'nil'},")
    w(f"            integerBoolean: {'true' if getattr(instance, 'integer_value', False) else 'false'},")
    for field, attr in [('requiresCameraControl', 'requires_camera_control'), ('requiresActionButton', 'requires_action_button'), ('requiresHomeButton', 'requires_home_button'), ('requiresAlwaysOn', 'requires_always_on')]:
        w(f"            {field}: {'true' if getattr(spec, attr) else 'false'},")
    w(f"            warning: {swift_string(spec.warning) if spec.warning else 'nil'},")
    w(f"            requires: [{', '.join(swift_string(x.name) for x in spec.requires)}],")
    w(f"            exclusiveWith: {swift_string(spec.exclusive_with.name) if spec.exclusive_with else 'nil'},")
    # The blacklist factory collects the device's installed apps through
    # desktop's installation proxy; the mobile app has no such channel, so
    # the row ships unavailable with an honest reason instead of a toggle
    # that can only fail at apply time.
    unavailable_reason = spec.unavailable_reason
    if factory == "InstalledAppSuggestionsBlacklist" and unavailable_reason is None:
        unavailable_reason = ("Collecting installed apps needs desktop's installation "
                              "proxy, which the mobile app does not have.")
    w(f"            unavailableReason: {swift_string(unavailable_reason) if unavailable_reason else 'nil'},")
    # Mobile allows both eligibility operations on any iPhone; upstream's
    # verified device remains documented in the description and warning.
    supported_models = () if factory == "SiriAITweak" else spec.supported_models
    w(f"            supportedModels: [{', '.join(swift_string(x) for x in supported_models)}]")
    w(f"        ),")


def chunk_header(number: int, first: int, last: int) -> list[str]:
    return [
        "// GENERATED FILE — do not edit by hand.",
        "//",
        f"// Registry rows {first}–{last} of GoldenNugget's"
        " `src/tweaks/registry.py`, split out of",
        "// `TweakCatalog.swift` so the Swift type-checker never sees one giant",
        "// array literal (see CHUNK_SIZE in the generator).  Regenerate all",
        "// parts with:",
        "//",
        "//     scripts/gen-tweaks-from-goldennugget.py [--goldennugget <path>]",
        "//",
        "// The parts concatenate in number order — do not sort or reorder them;",
        "// iteration order is load-bearing (`TweakCatalog.all`'s comment).",
        "",
        "import Foundation",
        "",
        "extension TweakCatalog {",
    ]


def emit(main: list[str], chunks: list[tuple[str, list[str]]],
         FileLocation, SPECS, Kind, Section) -> None:
    """Fill `main` with `TweakCatalog.swift` and `chunks` with the row files."""
    w = main.append

    w("// GENERATED FILE — do not edit by hand.")
    w("//")
    w("// Source of truth: GoldenNugget's `src/tweaks/registry.py` (the tweak")
    w("// spec table) and `src/tweaks/basic_plist_locations.py` (the")
    w("// `FileLocation` enum).  Regenerate with:")
    w("//")
    w("//     scripts/gen-tweaks-from-goldennugget.py [--goldennugget <path>]")
    w("//")
    w("// The port is a generation, not a retype: the table is emitted from")
    w("// the reference module itself, so a tweak added upstream appears here")
    w("// without a hand edit and a spec cannot silently drift from the source.")
    w("// The rows themselves live in the `TweakCatalog+RegistryN.swift` chunks;")
    w("// this file carries the enums and the assembly.")
    w("")
    w("import Foundation")
    w("")

    # --- FileLocation -------------------------------------------------------
    w("/// An absolute device path a tweak writes to.")
    w("///")
    w("/// Ported from GoldenNugget's `FileLocation` enum; the raw value is the")
    w("/// absolute path, and `TweakDomainMap` turns it into the")
    w("/// `(backup domain, relative path)` pair a restorable row needs.")
    w("enum TweakFileLocation: String, CaseIterable, Sendable {")
    for loc in FileLocation:
        w(f"    case {loc.name} = {swift_string(loc.value)}")
    # Registry entries may carry `location=None` (`_research_entry`'s
    # research-only rows have no plist to write).  The port keeps them in the
    # catalog so their reason still renders, but no location can name them.
    w('    case none = ""')
    w("}")
    w("")

    # --- Section ------------------------------------------------------------
    w("/// A tweaks-page section.  Raw values match GoldenNugget's `Section` enum.")
    w("enum TweakSection: String, CaseIterable, Identifiable, Sendable {")
    for member in Section:
        w(f"    case {SECTION_CASES[member.name]} = {swift_string(member.value)}")
    # Daemons is not a member of the reference's `Section`: upstream renders it
    # as its own page built in code (`load_daemons()` plus `gui/ios/daemons.py`)
    # rather than from the registry.  The port folds it into the same enum so
    # one catalog drives both pages; the raw value is the page's own header text.
    w(f"    case daemons = {swift_string(DAEMONS_SECTION_TITLE)}")
    w("    var id: String { rawValue }")
    w("}")
    w("")

    # --- Kind ---------------------------------------------------------------
    w("/// The UI editor a spec wants.  Matches GoldenNugget's `Kind` enum.")
    w("enum TweakKind: Sendable {")
    w("    case toggle")
    w("    case text")
    w("    case number")
    w("    /// Edits fields inside the wallpaper archives a restore already")
    w("    /// carries (`PosterKitOverrides`).  Staged by the engine, not here.")
    w("    case posterArchive")
    w("    /// Writes a wallpaper dictionary into SpringBoard preferences.")
    w("    case wallpaper")
    w("    /// A single wallpaper feature flag.  No registry spec uses this yet;")
    w("    /// the case keeps the port's enum in lockstep with the reference's.")
    w("    case posterFlag")
    w("}")
    w("")

    # --- Catalog ------------------------------------------------------------
    w("/// Every registry-defined tweak, in the reference's own order.")
    w("///")
    w("/// Iteration order is load-bearing: the compiler merges several tweaks into")
    w("/// one plist, and GoldenNugget iterates `tweaks` in this same order, so a")
    w("/// later key wins exactly as it does upstream.  Do not sort this array.")
    w("enum TweakCatalog {")
    for index in range(0, len(SPECS), CHUNK_SIZE):
        part = SPECS[index:index + CHUNK_SIZE]
        number = index // CHUNK_SIZE
        chunk = chunk_header(number, index, index + len(part) - 1)
        cw = chunk.append
        cw(f"    static let registry{number}: [TweakSpec] = [")
        for spec in part:
            emit_spec(cw, spec)
        cw("    ]")
        cw("}")
        chunks.append((chunk_name(number), chunk))
    total = (len(SPECS) + CHUNK_SIZE - 1) // CHUNK_SIZE

    # Mobile-only rows.  This fork's additions have no desktop counterpart, so
    # they are emitted from the table at the top of this file into their own
    # chunk and appended to `all`.  Keeping them out of the reference chunks
    # means those stay byte-identical to a regeneration.
    mobile = [
        "// GENERATED FILE — do not edit by hand.",
        "//",
        "// Mobile-only rows: registry entries this fork adds on top of GoldenNugget's",
        "// `src/tweaks/registry.py`.  They have no desktop counterpart, so they are",
        "// emitted from the generator's own table rather than from the reference.",
        "// Regenerate all parts with:",
        "//",
        "//     scripts/gen-tweaks-from-goldennugget.py [--goldennugget <path>]",
        "//",
        "// Kept in their own file so the reference's own chunks stay byte-identical to",
        "// a regeneration; `TweakCatalog.all` appends this array after `registry9`.",
        "",
        "import Foundation",
        "",
        "extension TweakCatalog {",
        "    static let registryMobileOnly: [TweakSpec] = [",
    ]
    mobile += MOBILE_ONLY_ROWS.strip("\n").split("\n")
    mobile += ["    ]", "}"]
    chunks.append((MOBILE_ONLY_CHUNK, mobile))

    w("    /// Every registry-defined tweak, in the reference's own order, then the")
    w("    /// fork's own mobile-only rows.  The mobile-only array is separate so the")
    w("    /// reference chunks stay byte-identical to a regeneration.")
    w("    static let all: [TweakSpec] = "
      + " + ".join(f"registry{number}" for number in range(total))
      + " + registryMobileOnly")
    w("")

    w("    /// The daemon groups, appended after the registry rows.  They are not in")
    w("    /// `registry.py` upstream -- `gen-daemons-from-goldennugget.py` emits them")
    w("    /// from `daemons_tweak.py` -- and they are last so every registry key still")
    w("    /// merges into a shared plist before any daemon label does.")
    w("    static let allWithDaemons: [TweakSpec] = all + daemonSpecs + [screenTimeSpec]")
    w("")
    w("    static let byID: [String: TweakSpec] =")
    w("        Dictionary(uniqueKeysWithValues: allWithDaemons.map { ($0.id, $0) })")
    w("")
    w("    static func inSection(_ section: TweakSection) -> [TweakSpec] {")
    w("        all.filter { $0.section == section }")
    w("    }")
    w("}")
    w("")


def generated_outputs(args, FileLocation, SPECS, Kind, Section) -> dict[str, str]:
    """Every file this generation produces, name → contents."""
    main: list[str] = []
    chunks: list[tuple[str, list[str]]] = []
    emit(main, chunks, FileLocation, SPECS, Kind, Section)
    # The opaque keyed archives.  `siri` and `reset` come from desktop's
    # `siri_ai` byte-for-byte (`HASHES` verbatim, the desktop contract);
    # `mirroring` and `siri+mirroring` are this fork's IRON (27) additions.
    import base64
    from src.tweaks.siri_ai import payload_file, HASHES
    archives = {
        "siri": payload_file("enable").contents,
        "mirroring": base64.b64decode(MOBILE_ONLY_ARCHIVES_B64["mirroring"]),
        "siri+mirroring": base64.b64decode(MOBILE_ONLY_ARCHIVES_B64["siri+mirroring"]),
        "reset": payload_file("reset").contents,
    }
    hashes = {
        "siri": HASHES["enable"],
        "mirroring": MOBILE_ONLY_ARCHIVE_HASHES["mirroring"],
        "siri+mirroring": MOBILE_ONLY_ARCHIVE_HASHES["siri+mirroring"],
        "reset": HASHES["reset"],
    }
    main += [
        "",
        "extension TweakCatalog {",
        "    /// The eligibility-override archives this app can deliver, keyed by the",
        "    /// exact set of enabled operations.",
        "    ///",
        "    /// The device holds exactly ONE override map",
        "    /// (`SysContainerDomain-com.apple.eligibilityd` / `Library/Caches/NeverRestore/",
        "    /// eligibility_overrides.data`), so two enabled operations cannot each write",
        "    /// their own file: the set of enabled operations selects one pre-combined",
        "    /// archive.  `eligibilityCombination(for:)` maps a selection to a key.",
        "    ///",
        "    /// Every entry is an opaque `NSKeyedArchive` from Apple's own",
        "    /// `NSKeyedArchiver` and is never reserialized; the runtime verifies each",
        "    /// against `eligibilityHashes` before it reaches the device.",
        "    ///",
        "    /// Sources: `siri` and `reset` are the Project Linwood archives the desktop",
        "    /// ships (`siri_ai.HASHES`).  `mirroring` and `siri+mirroring` were produced",
        "    /// by Project Linwood's `tools/override_archive/make_override_archive.swift`",
        "    /// on 2026-11-14 for `OS_ELIGIBILITY_DOMAIN_IRON` (27).",
        "    static let eligibilityArchives: [String: Data] = [",
    ]
    for name in ARCHIVE_ORDER:
        main += [f'        "{name}": Data(base64Encoded: "{base64.b64encode(archives[name]).decode()}")!,']
    main += [
        "    ]",
        "",
        "    /// sha256 of each embedded archive, verbatim.",
        "    static let eligibilityHashes: [String: String] = [",
    ]
    for name in ARCHIVE_ORDER:
        main += [f'        "{name}": "{hashes[name]}",']
    main += [
        "    ]",
        "",
        "    /// The registry ids that write the one override map, in apply order.",
        '    static let eligibilityOperationIDs = ["SiriAI", "IPhoneMirroring", "ResetSiriAIOverrides"]',
        "",
        "    /// The archive key for a set of enabled eligibility operations.",
        "    ///",
        "    /// `reset` wins: an empty map is the only combination a reset can mean, and",
        "    /// the UI already refuses reset alongside either enable operation",
        "    /// (`exclusiveWith`).  `siri` and `mirroring` combine into the union",
        "    /// archive, because the one override map has to carry both.",
        "    static func eligibilityCombination(for ids: [String]) -> String? {",
        "        guard !ids.isEmpty else { return nil }",
        '        if ids.contains("ResetSiriAIOverrides") { return "reset" }',
        '        switch (ids.contains("SiriAI"), ids.contains("IPhoneMirroring")) {',
        '        case (true, true): return "siri+mirroring"',
        '        case (true, false): return "siri"',
        '        case (false, true): return "mirroring"',
        '        case (false, false): return nil',
        "        }",
        "    }",
        "}",
    ]
    import runpy
    capabilities = runpy.run_path(str(Path(args.goldennugget) / "src/devicemanagement/device_capabilities.py"))
    main += ["", "/// Device capabilities generated from desktop device_capabilities.py.", "enum TweakDeviceCapabilities {"]
    for method, predicate in [('hasDynamicIsland', 'has_dynamic_island'), ('hasCameraControl', 'has_camera_control'), ('hasActionButton', 'has_action_button'), ('hasHomeButton', 'has_home_button'), ('hasAlwaysOn', 'has_always_on_display')]:
        # Enumerating known product identifiers through the actual predicates also
        # covers the desktop sets defined locally inside functions.
        models = {node.value for node in ast.walk(ast.parse((Path(args.goldennugget) / "src/devicemanagement/device_capabilities.py").read_text())) if isinstance(node, ast.Constant) and isinstance(node.value, str) and re.fullmatch(r"(?:iPhone|iPad)\d+,\d+", node.value)}
        main += [f"    static func {method}(_ model: String) -> Bool {{", "        let models: Set<String> = ["]
        main += [f"            {swift_string(model)}," for model in sorted(models) if capabilities[predicate](model)]
        main += ["        ]", "        return models.contains(model.trimmingCharacters(in: .whitespacesAndNewlines))", "    }"]
    main += ["}", ""]
    outputs = {OUTPUT.name: "\n".join(main)}
    for name, lines in chunks:
        outputs[name] = "\n".join(lines)
    return outputs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--goldennugget", default=DEFAULT_SOURCE,
                    help=f"path to the GoldenNugget checkout (default: {DEFAULT_SOURCE})")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the catalog would change; never writes")
    args = ap.parse_args()

    FileLocation, SPECS, Kind, Section = load_reference(Path(args.goldennugget))
    outputs = generated_outputs(args, FileLocation, SPECS, Kind, Section)

    current: dict[str, str] = {}
    # Only this generator's own files: the main file plus its chunks.  A wider
    # glob (`TweakCatalog*.swift`) would swallow TweakCatalogDaemons.swift,
    # which gen-daemons-from-goldennugget.py owns, and delete it as "stale".
    for path in OUTPUT.parent.glob("TweakCatalog+Registry*.swift"):
        current[path.name] = path.read_text(encoding="utf-8")
    if OUTPUT.is_file():
        current[OUTPUT.name] = OUTPUT.read_text(encoding="utf-8")

    if args.check:
        stale = sorted(set(current) - set(outputs))
        drifted = sorted(name for name in set(current) & set(outputs)
                         if current[name] != outputs[name])
        missing = sorted(set(outputs) - set(current))
        if drifted or stale or missing:
            print("TweakCatalog*.swift is out of date with the reference registry "
                  f"(drifted: {drifted or '—'}, stale: {stale or '—'}, "
                  f"missing: {missing or '—'})", file=sys.stderr)
            return 1
        print(f"TweakCatalog*.swift matches the reference ({len(SPECS)} tweaks, "
              f"{len(outputs)} files)")
        return 0

    for name in sorted(set(current) - set(outputs)):
        (OUTPUT.parent / name).unlink()
        print(f"removed stale {name}")
    written = 0
    for name, content in outputs.items():
        if current.get(name) == content:
            continue
        (OUTPUT.parent / name).write_text(content, encoding="utf-8")
        written += 1
    if written == 0:
        print(f"TweakCatalog*.swift already up to date ({len(SPECS)} tweaks, "
              f"{len(outputs)} files)")
    else:
        print(f"wrote {written} file(s): {len(SPECS)} tweaks across "
              f"{len(outputs)} files ({OUTPUT.name} + {len(outputs) - 1} chunk(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
