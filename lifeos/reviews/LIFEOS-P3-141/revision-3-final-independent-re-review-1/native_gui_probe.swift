import AppKit
import ApplicationServices
import Foundation

// Review-owned probe. Its only launch target is supplied explicitly by this
// review invocation; it records the direct Process PID and never substitutes
// another app, frontmost app, or pre-existing window.

struct Arguments {
    let binary: String
    let viewport: String
    let output: String
    let screenshot: String
}

func parseArguments() -> Arguments? {
    let values = Array(CommandLine.arguments.dropFirst())
    guard values.count == 8 else { return nil }
    var fields: [String: String] = [:]
    var index = 0
    while index < values.count {
        fields[values[index]] = values[index + 1]
        index += 2
    }
    guard let binary = fields["--binary"], let viewport = fields["--viewport"],
          let output = fields["--output"], let screenshot = fields["--screenshot"] else {
        return nil
    }
    return Arguments(binary: binary, viewport: viewport, output: output, screenshot: screenshot)
}

func axValue(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var value: CFTypeRef?
    let result = AXUIElementCopyAttributeValue(element, attribute as CFString, &value)
    return result == .success ? value : nil
}

func axText(_ element: AXUIElement, _ attribute: String) -> String? {
    guard let value = axValue(element, attribute) else { return nil }
    return value as? String
}

func axChildren(_ element: AXUIElement) -> [AXUIElement] {
    guard let value = axValue(element, kAXChildrenAttribute as String) else { return [] }
    guard CFGetTypeID(value) == CFArrayGetTypeID() else { return [] }
    let array = unsafeBitCast(value, to: CFArray.self) as [AnyObject]
    return array.compactMap { child in
        guard CFGetTypeID(child) == AXUIElementGetTypeID() else { return nil }
        return unsafeBitCast(child, to: AXUIElement.self)
    }
}

func axPoint(_ element: AXUIElement) -> [String: Double]? {
    guard let rawValue = axValue(element, kAXPositionAttribute as String),
          CFGetTypeID(rawValue) == AXValueGetTypeID() else { return nil }
    let value = unsafeBitCast(rawValue, to: AXValue.self)
    var point = CGPoint.zero
    guard AXValueGetValue(value, .cgPoint, &point) else { return nil }
    return ["x": Double(point.x), "y": Double(point.y)]
}

func axSize(_ element: AXUIElement) -> [String: Double]? {
    guard let rawValue = axValue(element, kAXSizeAttribute as String),
          CFGetTypeID(rawValue) == AXValueGetTypeID() else { return nil }
    let value = unsafeBitCast(rawValue, to: AXValue.self)
    var size = CGSize.zero
    guard AXValueGetValue(value, .cgSize, &size) else { return nil }
    return ["width": Double(size.width), "height": Double(size.height)]
}

func nodeSnapshot(_ element: AXUIElement, depth: Int, nodes: inout [[String: Any]], limit: Int) {
    guard nodes.count < limit, depth <= 10 else { return }
    var entry: [String: Any] = ["depth": depth]
    let role = axText(element, kAXRoleAttribute as String) ?? ""
    entry["role"] = role
    for attr in [kAXTitleAttribute as String, kAXDescriptionAttribute as String, kAXValueAttribute as String] {
        if let text = axText(element, attr), !text.isEmpty { entry[attr] = text }
    }
    nodes.append(entry)
    for child in axChildren(element) {
        nodeSnapshot(child, depth: depth + 1, nodes: &nodes, limit: limit)
    }
}

func findPressableSettings(_ element: AXUIElement, depth: Int = 0) -> AXUIElement? {
    guard depth <= 10 else { return nil }
    let role = axText(element, kAXRoleAttribute as String) ?? ""
    let texts = [
        axText(element, kAXTitleAttribute as String),
        axText(element, kAXDescriptionAttribute as String),
        axText(element, kAXValueAttribute as String)
    ].compactMap { $0 }.joined(separator: " ").lowercased()
    if role == (kAXButtonRole as String) && texts.contains("settings") {
        return element
    }
    for child in axChildren(element) {
        if let found = findPressableSettings(child, depth: depth + 1) { return found }
    }
    return nil
}

func hasText(_ nodes: [[String: Any]], _ needle: String) -> Bool {
    let lowered = needle.lowercased()
    return nodes.contains { node in
        node.values.contains { value in
            (value as? String)?.lowercased().contains(lowered) == true
        }
    }
}

func jsonWrite(_ payload: [String: Any], path: String) {
    let url = URL(fileURLWithPath: path)
    guard JSONSerialization.isValidJSONObject(payload),
          let data = try? JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys]) else {
        fputs("unable to serialize probe output\n", stderr)
        exit(2)
    }
    try? data.write(to: url, options: .atomic)
}

guard let args = parseArguments() else {
    fputs("usage: native_gui_probe --binary PATH --viewport NAME --output JSON --screenshot PNG\n", stderr)
    exit(64)
}

var payload: [String: Any] = [
    "schema": "lifeos.p3-141.review-native-gui-probe.v1",
    "viewport": args.viewport,
    "expected_title": "LifeOS · P3-141 Controlled Pilot Candidate",
    "launch_target": args.binary,
    "timestamp_utc": ISO8601DateFormatter().string(from: Date())
]

let launched = Process()
launched.executableURL = URL(fileURLWithPath: args.binary)
var environment = ProcessInfo.processInfo.environment
environment["LIFEOS_INPUT_MODE"] = "synthetic"
environment["LIFEOS_P3_141_BUILD_MODE"] = "revision_3_synthetic"
environment["LIFEOS_P3_141_EVIDENCE_MODE"] = "1"
environment["LIFEOS_P3_141_VIEWPORT"] = args.viewport
environment["LIFEOS_P3_141_SYNTHETIC_FIXTURE_EVIDENCE"] = "1"
launched.environment = environment

do {
    try launched.run()
} catch {
    payload["status"] = "blocked"
    payload["launch_error"] = String(describing: error)
    jsonWrite(payload, path: args.output)
    exit(0)
}

let pid = launched.processIdentifier
payload["direct_launch_pid"] = Int(pid)
let application = AXUIElementCreateApplication(pid)
var matchedWindow: AXUIElement?
var allWindows: [AXUIElement] = []
var pollErrors: [String] = []
for _ in 0..<50 {
    if let rawWindows = axValue(application, kAXWindowsAttribute as String),
       CFGetTypeID(rawWindows) == CFArrayGetTypeID() {
        let windows = unsafeBitCast(rawWindows, to: CFArray.self) as [AnyObject]
        allWindows = windows.compactMap { candidate in
            guard CFGetTypeID(candidate) == AXUIElementGetTypeID() else { return nil }
            return unsafeBitCast(candidate, to: AXUIElement.self)
        }
        let matches = allWindows.filter { axText($0, kAXTitleAttribute as String) == "LifeOS · P3-141 Controlled Pilot Candidate" }
        if matches.count == 1 {
            matchedWindow = matches[0]
            break
        }
        if matches.count > 1 { pollErrors.append("multiple exact-title windows for direct PID") }
    } else {
        pollErrors.append("AXWindows unavailable")
    }
    Thread.sleep(forTimeInterval: 0.5)
}

payload["ax_poll_observations"] = Array(pollErrors.suffix(8))
payload["pid_window_count"] = allWindows.count

if let window = matchedWindow {
    payload["window_title"] = axText(window, kAXTitleAttribute as String) ?? ""
    payload["window_role"] = axText(window, kAXRoleAttribute as String) ?? ""
    if let position = axPoint(window) { payload["window_position"] = position }
    if let size = axSize(window) { payload["window_size"] = size }
    var beforeNodes: [[String: Any]] = []
    nodeSnapshot(window, depth: 0, nodes: &beforeNodes, limit: 900)
    payload["initial_ax_nodes"] = beforeNodes
    payload["has_web_node_initial"] = beforeNodes.contains { node in
        let role = node["role"] as? String ?? ""
        return role == "AXWebArea" || role == "AXWebView"
    }

    let pressable = findPressableSettings(window)
    payload["settings_control_found"] = pressable != nil
    if let control = pressable {
        payload["settings_press_result"] = AXUIElementPerformAction(control, kAXPressAction as CFString).rawValue
        Thread.sleep(forTimeInterval: 1.0)
    }
    var settingsNodes: [[String: Any]] = []
    nodeSnapshot(window, depth: 0, nodes: &settingsNodes, limit: 1200)
    payload["settings_ax_nodes"] = settingsNodes
    payload["settings_page_visible"] = hasText(settingsNodes, "模型设置") || hasText(settingsNodes, "Model Settings")
    payload["settings_provider_content_visible"] = hasText(settingsNodes, "OpenAI") && hasText(settingsNodes, "Ollama")

    let axWindowNumber = axValue(window, "AXWindowNumber") as? NSNumber
    payload["ax_window_number"] = axWindowNumber?.intValue as Any
    // AXWindowNumber is not exposed by every macOS build.  This fallback is
    // permitted only after the exact direct-PID AXWindow binding above and is
    // itself constrained to the same direct PID and exact title.
    let matchingCGWindows = (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: AnyObject]] ?? []).filter { info in
        let ownerPID = (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
        let name = info[kCGWindowName as String] as? String
        return ownerPID == pid && name == "LifeOS · P3-141 Controlled Pilot Candidate"
    }
    payload["cg_exact_pid_title_window_count"] = matchingCGWindows.count
    let cgWindowNumber = matchingCGWindows.count == 1 ? (matchingCGWindows[0][kCGWindowNumber as String] as? NSNumber) : nil
    payload["cg_exact_pid_title_window_number"] = cgWindowNumber?.intValue as Any
    let captureNumber = axWindowNumber ?? cgWindowNumber
    if let number = captureNumber {
        let capture = Process()
        capture.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
        capture.arguments = ["-x", "-l", String(number.intValue), args.screenshot]
        do {
            try capture.run()
            capture.waitUntilExit()
            payload["screenshot_exit_status"] = capture.terminationStatus
            payload["screenshot_exists"] = FileManager.default.fileExists(atPath: args.screenshot)
        } catch {
            payload["screenshot_error"] = String(describing: error)
        }
    } else {
        payload["screenshot_error"] = "no unique direct-PID exact-title native window number; no screenshot substitution was attempted"
    }
    payload["status"] = "captured"
} else {
    payload["status"] = "blocked"
    payload["block_reason"] = "direct launch PID did not yield one exact-title AXWindow"
}

if launched.isRunning {
    launched.terminate()
    for _ in 0..<20 where launched.isRunning { Thread.sleep(forTimeInterval: 0.25) }
}
payload["direct_launch_pid_exited"] = !launched.isRunning
payload["direct_launch_termination_status"] = launched.terminationStatus
payload["completed_utc"] = ISO8601DateFormatter().string(from: Date())
jsonWrite(payload, path: args.output)
