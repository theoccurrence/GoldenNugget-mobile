#!/usr/bin/env python3
"""Compile the eligibility-override path and assert its combination contract.

The device holds exactly ONE eligibility override map
(`SysContainerDomain-com.apple.eligibilityd` /
`Library/Caches/NeverRestore/eligibility_overrides.data`), so the operations
that write it — Siri AI, iPhone Mirroring, Reset — are resolved as a *set*:
`TweakCompiler.compile` picks one pre-combined, pinned archive from
`TweakCatalog.eligibilityArchives` instead of emitting one write per spec.

This gate compiles that path for macOS and runs the matrix: each operation
alone, both enable operations together, the reset, the exclusivity rules, and
the iPhone-only / iOS-27 compatibility gate.  It needs no device and no
desktop checkout — only the sources under `Nugget/Core`.

Usage:
    scripts/check-eligibility-overrides.py
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `TweakCatalog.all` is assembled from the generated registry chunks, so the
# harness cannot compile without them.
SOURCES = ["TweakModel", "TweakCatalog", "TweakCatalogDaemons", "TweakDomainMap", "TweakCompiler",
           "PosterKitOptions"]
SOURCES += sorted(path.stem for path in (ROOT / "Nugget/Core").glob("TweakCatalog+Registry*.swift"))

HARNESS = r'''
import Foundation

@main
struct Check {
    static var failures = 0

    static func check(_ condition: Bool, _ name: String) {
        print((condition ? "PASS: " : "FAIL: ") + name)
        if !condition { failures += 1 }
    }

    static func eligibilityPayloads(_ selection: TweakSelection) -> [TweakPayload] {
        TweakCompiler.compile(selection: selection, deviceVersion: "27.0",
                              isIPhone: true, deviceModel: "iPhone17,1")
            .payloads.filter { $0.domain == "SysContainerDomain-com.apple.eligibilityd" }
    }

    static func main() {
        let siri = TweakCatalog.byID["SiriAI"]!
        let mirror = TweakCatalog.byID["IPhoneMirroring"]!
        let reset = TweakCatalog.byID["ResetSiriAIOverrides"]!

        check(mirror.factory == "SiriAITweak", "iPhone Mirroring uses the eligibility factory")
        check(mirror.location == .siriAIOverrides, "iPhone Mirroring writes the override file")
        check(mirror.isCompatible(deviceVersion: "27.0", isIPhone: true, deviceModel: "iPhone17,1"),
              "iPhone Mirroring is compatible on an iOS 27 iPhone")
        check(!mirror.isCompatible(deviceVersion: "27.0", isIPhone: false, deviceModel: "iPad16,2"),
              "iPhone Mirroring is iPhone-only")
        check(!mirror.isCompatible(deviceVersion: "26.5", isIPhone: true, deviceModel: "iPhone17,1"),
              "iPhone Mirroring refuses iOS 26")

        var state = TweakSelection()
        check(eligibilityPayloads(state).isEmpty, "no operation selected emits no archive")

        state.setOn(true, for: siri)
        let siriOnly = eligibilityPayloads(state)
        check(siriOnly.count == 1 && siriOnly[0].owner == 0 && siriOnly[0].contents.count == 631,
              "Siri AI alone emits one root-owned 631-byte archive")

        state.setOn(false, for: siri)
        state.setOn(true, for: mirror)
        let mirrorOnly = eligibilityPayloads(state)
        check(mirrorOnly.count == 1 && mirrorOnly[0].contents.count == 492,
              "iPhone Mirroring alone emits one 492-byte archive")

        state.setOn(true, for: siri)
        let both = eligibilityPayloads(state)
        check(both.count == 1 && both[0].contents.count == 700,
              "Siri AI + iPhone Mirroring collapse into one 700-byte union archive")
        check(both[0].contents != siriOnly[0].contents && both[0].contents != mirrorOnly[0].contents,
              "the union archive is its own payload")

        state.setOn(false, for: siri)
        state.setOn(false, for: mirror)
        state.setOn(true, for: reset)
        let resetOnly = eligibilityPayloads(state)
        check(resetOnly.count == 1 && resetOnly[0].contents.count == 320,
              "Reset alone emits one 320-byte archive")

        var conflict = TweakSelection()
        conflict.setOn(true, for: mirror)
        conflict.setOn(true, for: reset)
        check(conflict.validationIssue() != nil, "iPhone Mirroring + Reset is refused")

        var allowed = TweakSelection()
        allowed.setOn(true, for: siri)
        allowed.setOn(true, for: mirror)
        check(allowed.validationIssue() == nil, "Siri AI + iPhone Mirroring is allowed")

        print(failures == 0 ? "\nALL PASS" : "\n\(failures) FAILURE(S)")
        exit(failures == 0 ? 0 : 1)
    }
}
'''


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="goldennugget-eligibility-") as temporary:
        folder = Path(temporary)
        paths = []
        for name in SOURCES:
            path = folder / f"{name}.swift"
            path.write_text((ROOT / "Nugget/Core" / f"{name}.swift").read_text())
            paths.append(path)
        harness = folder / "Check.swift"
        harness.write_text(HARNESS)
        binary = folder / "check"
        subprocess.run(["xcrun", "swiftc", "-swift-version", "5", "-parse-as-library",
                        *map(str, paths), str(harness), "-o", str(binary)], check=True)
        return subprocess.run([str(binary)]).returncode


if __name__ == "__main__":
    raise SystemExit(main())
