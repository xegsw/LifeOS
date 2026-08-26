import AppKit
import CoreGraphics
import CryptoKit
import Foundation

struct Bounds: Codable {
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct TargetWindow: Codable {
    let window_id: Int
    let bounds: Bounds
}

struct Output: Codable {
    let command: String
    let pass: Bool
    let status: String
    let target_pid: Int32?
    let event_id: String?
    let target_window: TargetWindow?
    let observed_target_windows: [TargetWindow]?
    let image_sha256: String?
    let matched_sample_count: Int?
    let total_sample_count: Int?
    let sampled_rgb: String?
}

let chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
let chromeHash = "97385e62510154852fd10da11c697bf5066dcc300e3b0c31633bd52ad940b984"
let pidEventAPISymbol = "CGEventPostToPid"
let arguments = Array(CommandLine.arguments.dropFirst())

func value(_ name: String) -> String? {
    guard let index = arguments.firstIndex(of: name), index + 1 < arguments.count else { return nil }
    return arguments[index + 1]
}

func sha256(_ path: String) -> String? {
    guard let data = try? Data(contentsOf: URL(fileURLWithPath: path)) else { return nil }
    return SHA256.hash(data: data).map { String(format: "%02x", $0) }.joined()
}

func emit(command: String, pass: Bool, status: String, pid: Int32? = nil, eventID: String? = nil, window: TargetWindow? = nil, observedWindows: [TargetWindow]? = nil, imageHash: String? = nil, matchCount: Int? = nil, sampleCount: Int? = nil, sampledRGB: String? = nil, code: Int32) -> Never {
    let value = Output(command: command, pass: pass, status: status, target_pid: pid, event_id: eventID, target_window: window, observed_target_windows: observedWindows, image_sha256: imageHash, matched_sample_count: matchCount, total_sample_count: sampleCount, sampled_rgb: sampledRGB)
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.sortedKeys, .withoutEscapingSlashes]
    if let data = try? encoder.encode(value), let text = String(data: data, encoding: .utf8) {
        print(text)
    }
    exit(code)
}

func parsePID(command: String) -> Int32 {
    guard let raw = value("--pid"), let pid = Int32(raw), pid > 0 else {
        emit(command: command, pass: false, status: "INVALID_PID", code: 64)
    }
    if let rawExpected = value("--expected-pid"), let expected = Int32(rawExpected), expected != pid {
        emit(command: command, pass: false, status: "TARGET_PID_MISMATCH", pid: pid, code: 41)
    }
    return pid
}

func listedTargetWindows(pid: Int32) -> [TargetWindow] {
    let listed = (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]]) ?? []
    let owned = listed.filter { row in
        (row[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value == pid
    }
    return owned.compactMap { row in
        guard let layer = (row[kCGWindowLayer as String] as? NSNumber)?.intValue,
              let onscreen = (row[kCGWindowIsOnscreen as String] as? NSNumber)?.boolValue,
              let number = (row[kCGWindowNumber as String] as? NSNumber)?.intValue,
              let rawBounds = row[kCGWindowBounds as String] as? [String: Any],
              let x = (rawBounds["X"] as? NSNumber)?.doubleValue,
              let y = (rawBounds["Y"] as? NSNumber)?.doubleValue,
              let width = (rawBounds["Width"] as? NSNumber)?.doubleValue,
              let height = (rawBounds["Height"] as? NSNumber)?.doubleValue,
              layer == 0, onscreen else { return nil }
        return TargetWindow(window_id: number, bounds: Bounds(x: x, y: y, width: width, height: height))
    }
}

func verifiedWindow(command: String, pid: Int32, eventID: String?) -> TargetWindow {
    guard let app = NSRunningApplication(processIdentifier: pid_t(pid)) else {
        emit(command: command, pass: false, status: "TARGET_PID_NOT_RUNNING", pid: pid, eventID: eventID, code: 2)
    }
    guard app.executableURL?.path == chromePath else {
        emit(command: command, pass: false, status: "EXECUTABLE_PATH_MISMATCH", pid: pid, eventID: eventID, code: 3)
    }
    let expectedHash = value("--expected-hash") ?? chromeHash
    guard sha256(chromePath) == expectedHash else {
        emit(command: command, pass: false, status: "EXECUTABLE_HASH_MISMATCH", pid: pid, eventID: eventID, code: 4)
    }
    _ = app.activate(options: [.activateIgnoringOtherApps])
    RunLoop.current.run(until: Date(timeIntervalSinceNow: 0.2))
    guard NSWorkspace.shared.frontmostApplication?.processIdentifier == pid_t(pid) else {
        emit(command: command, pass: false, status: "TARGET_NOT_FRONTMOST", pid: pid, eventID: eventID, code: 5)
    }
    let windows = listedTargetWindows(pid: pid)
    if let expectedRaw = value("--expected-window-count"), let expected = Int(expectedRaw), expected != windows.count {
        emit(command: command, pass: false, status: "WINDOW_COUNT_EXPECTED_\(expected)_ACTUAL_\(windows.count)", pid: pid, eventID: eventID, observedWindows: windows, code: 42)
    }
    guard windows.count == 1, let window = windows.first else {
        emit(command: command, pass: false, status: "TARGET_WINDOW_COUNT_\(windows.count)", pid: pid, eventID: eventID, observedWindows: windows, code: 6)
    }
    if let rawID = value("--window-id"), let expectedID = Int(rawID), expectedID != window.window_id {
        emit(command: command, pass: false, status: "WINDOW_ID_MISMATCH", pid: pid, eventID: eventID, window: window, code: 43)
    }
    return window
}

func capture(command: String, pid: Int32, eventID: String?, window: TargetWindow) {
    guard let output = value("--out"), output.hasPrefix("/private/tmp/lifeos-p3-119-pid-gui-spike-v1/") else {
        emit(command: command, pass: false, status: "INVALID_CAPTURE_PATH", pid: pid, eventID: eventID, window: window, code: 7)
    }
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    process.arguments = ["-x", "-l", String(window.window_id), "-t", "png", output]
    do {
        try process.run()
        process.waitUntilExit()
    } catch {
        emit(command: command, pass: false, status: "CAPTURE_LAUNCH_FAILED", pid: pid, eventID: eventID, window: window, code: 8)
    }
    guard process.terminationStatus == 0,
          let attributes = try? FileManager.default.attributesOfItem(atPath: output),
          let size = attributes[.size] as? NSNumber, size.intValue > 0,
          let imageHash = sha256(output) else {
        emit(command: command, pass: false, status: "WINDOW_CAPTURE_FAILED", pid: pid, eventID: eventID, window: window, code: 9)
    }
    emit(command: command, pass: true, status: "PASS", pid: pid, eventID: eventID, window: window, imageHash: imageHash, code: 0)
}

func postClick(command: String, pid: Int32, eventID: String?, window: TargetWindow) {
    guard let rawX = value("--x"), let x = Double(rawX), let rawY = value("--y"), let y = Double(rawY) else {
        emit(command: command, pass: false, status: "INVALID_COORDINATES", pid: pid, eventID: eventID, window: window, code: 10)
    }
    let bounds = window.bounds
    guard x >= bounds.x, x <= bounds.x + bounds.width, y >= bounds.y, y <= bounds.y + bounds.height else {
        emit(command: command, pass: false, status: "CLICK_OUT_OF_BOUNDS", pid: pid, eventID: eventID, window: window, code: 44)
    }
    let point = CGPoint(x: x, y: y)
    let source = CGEventSource(stateID: .hidSystemState)
    guard let move = CGEvent(mouseEventSource: source, mouseType: .mouseMoved, mouseCursorPosition: point, mouseButton: .left),
          let down = CGEvent(mouseEventSource: source, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
          let up = CGEvent(mouseEventSource: source, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else {
        emit(command: command, pass: false, status: "EVENT_CONSTRUCTION_FAILED", pid: pid, eventID: eventID, window: window, code: 11)
    }
    move.postToPid(pid_t(pid))
    down.postToPid(pid_t(pid))
    up.postToPid(pid_t(pid))
    emit(command: command, pass: true, status: "PID_CLICK_POSTED", pid: pid, eventID: eventID, window: window, code: 0)
}

func postKey(command: String, pid: Int32, eventID: String?, window: TargetWindow) {
    guard let key = value("--key"), let keyCode: CGKeyCode = key == "tab" ? 48 : (key == "enter" ? 36 : nil) else {
        emit(command: command, pass: false, status: "INVALID_KEY", pid: pid, eventID: eventID, window: window, code: 12)
    }
    let source = CGEventSource(stateID: .hidSystemState)
    guard let down = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: true),
          let up = CGEvent(keyboardEventSource: source, virtualKey: keyCode, keyDown: false) else {
        emit(command: command, pass: false, status: "EVENT_CONSTRUCTION_FAILED", pid: pid, eventID: eventID, window: window, code: 13)
    }
    down.postToPid(pid_t(pid))
    up.postToPid(pid_t(pid))
    emit(command: command, pass: true, status: "PID_KEY_POSTED_\(key.uppercased())", pid: pid, eventID: eventID, window: window, code: 0)
}

func verifyPixels(command: String) {
    guard let imagePath = value("--image"), imagePath.hasPrefix("/private/tmp/lifeos-p3-119-pid-gui-spike-v1/"),
          let rawColor = value("--rgb") else {
        emit(command: command, pass: false, status: "INVALID_PIXEL_ARGUMENTS", code: 14)
    }
    let pieces = rawColor.split(separator: ",").compactMap { Double($0) }
    guard pieces.count == 3,
          let image = NSImage(contentsOf: URL(fileURLWithPath: imagePath)),
          let data = image.tiffRepresentation,
          let bitmap = NSBitmapImageRep(data: data),
          bitmap.pixelsWide > 0, bitmap.pixelsHigh > 0 else {
        emit(command: command, pass: false, status: "IMAGE_DECODE_FAILED", code: 15)
    }
    let minX = Int(Double(bitmap.pixelsWide) * 0.25)
    let maxX = Int(Double(bitmap.pixelsWide) * 0.35)
    let minY = Int(Double(bitmap.pixelsHigh) * 0.45)
    let maxY = Int(Double(bitmap.pixelsHigh) * 0.55)
    var total = 0
    var matches = 0
    var sampledRGB = ""
    for x in stride(from: minX, through: maxX, by: max(1, (maxX - minX) / 8)) {
        for y in stride(from: minY, through: maxY, by: max(1, (maxY - minY) / 8)) {
            guard let color = bitmap.colorAt(x: x, y: y)?.usingColorSpace(.deviceRGB) else { continue }
            total += 1
            if sampledRGB.isEmpty {
                sampledRGB = String(format: "%.1f,%.1f,%.1f", color.redComponent * 255, color.greenComponent * 255, color.blueComponent * 255)
            }
            if abs(color.redComponent * 255 - pieces[0]) <= 50,
               abs(color.greenComponent * 255 - pieces[1]) <= 50,
               abs(color.blueComponent * 255 - pieces[2]) <= 50 {
                matches += 1
            }
        }
    }
    guard total > 0, matches * 100 >= total * 80, let imageHash = sha256(imagePath) else {
        emit(command: command, pass: false, status: "PIXEL_COLOR_MISMATCH", matchCount: matches, sampleCount: total, sampledRGB: sampledRGB, code: 45)
    }
    emit(command: command, pass: true, status: "PIXEL_COLOR_PASS_\(matches)_OF_\(total)", imageHash: imageHash, matchCount: matches, sampleCount: total, sampledRGB: sampledRGB, code: 0)
}

guard let command = arguments.first else {
    emit(command: "none", pass: false, status: "MISSING_COMMAND", code: 64)
}
let eventID = value("--event-id")
switch command {
case "attest":
    let pid = parsePID(command: command)
    let window = verifiedWindow(command: command, pid: pid, eventID: eventID)
    emit(command: command, pass: true, status: "PID_WINDOW_ATTESTED", pid: pid, eventID: eventID, window: window, code: 0)
case "click":
    let pid = parsePID(command: command)
    let window = verifiedWindow(command: command, pid: pid, eventID: eventID)
    postClick(command: command, pid: pid, eventID: eventID, window: window)
case "key":
    let pid = parsePID(command: command)
    let window = verifiedWindow(command: command, pid: pid, eventID: eventID)
    postKey(command: command, pid: pid, eventID: eventID, window: window)
case "capture":
    let pid = parsePID(command: command)
    let window = verifiedWindow(command: command, pid: pid, eventID: eventID)
    capture(command: command, pid: pid, eventID: eventID, window: window)
case "pixels":
    verifyPixels(command: command)
default:
    emit(command: command, pass: false, status: "UNKNOWN_COMMAND", code: 64)
}
