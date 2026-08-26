import AppKit
import ApplicationServices
import CryptoKit
import Foundation

// P3-118 native attestation helper.  It accepts exactly one target PID and
// deliberately discards every non-target window before any serializable value
// is constructed.  It never reads window titles, owner names, paths, or AX
// browser content.

struct Bounds: Codable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct TargetWindow: Codable {
    let window_id: Int
    let bounds: Bounds
    let layer: Int
    let onscreen: Bool
}

struct Attestation: Codable {
    let target_pid: Int32
    let executable_sha256: String
    let executable_expected: Bool
    let frontmost: Bool
    let eligible_window_count: Int
    let target_window: TargetWindow?
    let pass: Bool
    let status: String
}

func sha256(of url: URL) -> String? {
    guard let data = try? Data(contentsOf: url) else { return nil }
    return SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}

func emit(_ record: Attestation) {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
    guard let data = try? encoder.encode(record), let text = String(data: data, encoding: .utf8) else {
        exit(70)
    }
    print(text)
}

guard CommandLine.arguments.count == 3, CommandLine.arguments[1] == "--pid",
      let parsedPid = Int32(CommandLine.arguments[2]), parsedPid > 0 else {
    fputs("usage: pid_window_attest --pid <positive-pid>\n", stderr)
    exit(64)
}

let targetPid = pid_t(parsedPid)
let expectedExecutableHash = "97385e62510154852fd10da11c697bf5066dcc300e3b0c31633bd52ad940b984"
guard let targetApp = NSRunningApplication(processIdentifier: targetPid) else {
    emit(Attestation(target_pid: parsedPid, executable_sha256: "", executable_expected: false, frontmost: false, eligible_window_count: 0, target_window: nil, pass: false, status: "TARGET_PID_NOT_RUNNING"))
    exit(2)
}

// This affects only the supplied PID. No app-name or bundle selector is used.
_ = targetApp.activate(options: [.activateIgnoringOtherApps])
RunLoop.current.run(until: Date(timeIntervalSinceNow: 0.25))

let executableHash = targetApp.executableURL.flatMap(sha256(of:)) ?? ""
let frontmost = NSWorkspace.shared.frontmostApplication?.processIdentifier == targetPid

let listed = (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]]) ?? []

// Filtering by target PID occurs before extraction/serialization of window fields.
let owned = listed.filter { item in
    (item[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value == parsedPid
}

let eligible: [TargetWindow] = owned.compactMap { item in
    guard let layer = (item[kCGWindowLayer as String] as? NSNumber)?.intValue,
          let onscreen = (item[kCGWindowIsOnscreen as String] as? NSNumber)?.boolValue,
          let windowID = (item[kCGWindowNumber as String] as? NSNumber)?.intValue,
          let rawBounds = item[kCGWindowBounds as String] as? [String: Any],
          let x = (rawBounds["X"] as? NSNumber)?.doubleValue,
          let y = (rawBounds["Y"] as? NSNumber)?.doubleValue,
          let width = (rawBounds["Width"] as? NSNumber)?.doubleValue,
          let height = (rawBounds["Height"] as? NSNumber)?.doubleValue,
          layer == 0, onscreen else {
        return nil
    }
    return TargetWindow(window_id: windowID, bounds: Bounds(x: x, y: y, width: width, height: height), layer: layer, onscreen: onscreen)
}

let onlyTarget = eligible.count == 1 ? eligible[0] : nil
let pass = executableHash == expectedExecutableHash && frontmost && onlyTarget != nil
emit(Attestation(
    target_pid: parsedPid,
    executable_sha256: executableHash,
    executable_expected: executableHash == expectedExecutableHash,
    frontmost: frontmost,
    eligible_window_count: eligible.count,
    target_window: onlyTarget,
    pass: pass,
    status: pass ? "PASS" : "PID_WINDOW_ATTESTATION_FAILED"
))
exit(pass ? 0 : 2)
