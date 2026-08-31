import ApplicationServices
import Cocoa
import Foundation

private func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var result: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success ? result : nil
}

private func text(_ element: AXUIElement, _ attribute: String) -> String? {
    return value(element, attribute) as? String
}

private func frame(_ element: AXUIElement) -> [String: Double]? {
    guard let positionValue = value(element, kAXPositionAttribute),
          let sizeValue = value(element, kAXSizeAttribute) else { return nil }
    var position = CGPoint.zero
    var size = CGSize.zero
    guard AXValueGetValue(positionValue as! AXValue, .cgPoint, &position),
          AXValueGetValue(sizeValue as! AXValue, .cgSize, &size) else { return nil }
    return ["x": position.x, "y": position.y, "width": size.width, "height": size.height]
}

private func rolesBelow(_ root: AXUIElement, depth: Int, seen: inout Set<String>) -> [String] {
    guard depth <= 12 else { return [] }
    var found: [String] = []
    if let role = text(root, kAXRoleAttribute), role == "AXWebArea" || role == "AXWebView" {
        found.append(role)
    }
    guard let children = value(root, kAXChildrenAttribute) as? [AXUIElement] else { return found }
    for child in children {
        let identity = String(describing: child)
        guard !seen.contains(identity) else { continue }
        seen.insert(identity)
        found.append(contentsOf: rolesBelow(child, depth: depth + 1, seen: &seen))
    }
    return found
}

func emit(_ object: [String: Any]) {
    let data = try! JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
}

guard CommandLine.arguments.count == 3,
      let pid = Int32(CommandLine.arguments[1]) else {
    fputs("usage: native_gui_probe <pid> <screenshot-path>\n", stderr)
    exit(64)
}

let expectedTitle = "LifeOS · P3-141 Controlled Pilot Candidate"
let app = AXUIElementCreateApplication(pid_t(pid))
guard let windowValues = value(app, kAXWindowsAttribute) as? [AXUIElement] else {
    emit(["pass": false, "pid": pid, "reason": "ax_windows_unavailable"])
    exit(2)
}

let matching = windowValues.filter { text($0, kAXTitleAttribute) == expectedTitle }
guard matching.count == 1, let target = matching.first else {
    emit(["pass": false, "pid": pid, "expected_title": expectedTitle, "matching_windows": matching.count, "windows_count": windowValues.count, "reason": "exact_title_window_missing_or_nonunique"])
    exit(3)
}

var seen = Set<String>()
let webRoles = rolesBelow(target, depth: 0, seen: &seen)
let windowNumber = value(target, "AXWindowNumber") as? NSNumber
let screenshotPath = CommandLine.arguments[2]
var screenshotExit: Int32? = nil
let captureScope: String
NSRunningApplication(processIdentifier: pid_t(pid))?.activate(options: [.activateIgnoringOtherApps])
if let number = windowNumber {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    process.arguments = ["-x", "-l", number.stringValue, screenshotPath]
    do {
        try process.run()
        process.waitUntilExit()
        screenshotExit = process.terminationStatus
    } catch {
        screenshotExit = -1
    }
    captureScope = "ax-window-number"
} else {
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    process.arguments = ["-x", screenshotPath]
    do {
        try process.run()
        process.waitUntilExit()
        screenshotExit = process.terminationStatus
    } catch {
        screenshotExit = -1
    }
    captureScope = "display-fallback-after-direct-pid-exact-window-binding"
}

let pass = !webRoles.isEmpty && screenshotExit == 0
emit([
    "pass": pass,
    "pid": pid,
    "expected_title": expectedTitle,
    "windows_count": windowValues.count,
    "matching_windows": matching.count,
    "frame": frame(target) as Any,
    "web_roles": Array(Set(webRoles)).sorted(),
    "window_number": windowNumber?.intValue as Any,
    "screenshot_path": screenshotPath,
    "capture_scope": captureScope,
    "screenshot_exit": screenshotExit as Any,
    "reason": pass ? "direct_pid_exact_window_webview_and_window_capture" : "webview_or_window_capture_missing"
])
exit(pass ? 0 : 4)
