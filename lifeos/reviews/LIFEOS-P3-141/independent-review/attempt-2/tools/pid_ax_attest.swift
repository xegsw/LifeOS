import Foundation
import ApplicationServices

func attribute(_ element: AXUIElement, _ key: CFString) -> AnyObject? {
    var value: CFTypeRef?
    let status = AXUIElementCopyAttributeValue(element, key, &value)
    guard status == .success, let value else { return nil }
    return value as AnyObject
}

func point(_ value: AnyObject?) -> [String: Double]? {
    guard let value, CFGetTypeID(value) == AXValueGetTypeID() else { return nil }
    var result = CGPoint.zero
    guard AXValueGetValue(value as! AXValue, .cgPoint, &result) else { return nil }
    return ["x": Double(result.x), "y": Double(result.y)]
}

func size(_ value: AnyObject?) -> [String: Double]? {
    guard let value, CFGetTypeID(value) == AXValueGetTypeID() else { return nil }
    var result = CGSize.zero
    guard AXValueGetValue(value as! AXValue, .cgSize, &result) else { return nil }
    return ["width": Double(result.width), "height": Double(result.height)]
}

func roles(_ element: AXUIElement, depth: Int) -> [String] {
    guard depth > 0 else { return [] }
    let role = attribute(element, kAXRoleAttribute as CFString) as? String
    let children = attribute(element, kAXChildrenAttribute as CFString) as? [AXUIElement] ?? []
    return (role.map { [$0] } ?? []) + children.flatMap { roles($0, depth: depth - 1) }
}

guard CommandLine.arguments.count == 4,
      let pid = pid_t(CommandLine.arguments[1]),
      let expectedTitle = CommandLine.arguments.dropFirst(2).first else {
    fputs("usage: pid_ax_attest PID EXACT_TITLE OUTPUT_JSON\\n", stderr)
    exit(64)
}
let output = URL(fileURLWithPath: CommandLine.arguments[3])
let app = AXUIElementCreateApplication(pid)
let windows = attribute(app, kAXWindowsAttribute as CFString) as? [AXUIElement] ?? []
let matched = windows.filter { (attribute($0, kAXTitleAttribute as CFString) as? String) == expectedTitle }
let selected = matched.first
let roleList = selected.map { roles($0, depth: 12) } ?? []
let webViewCount = roleList.filter { $0 == "AXWebView" }.count
let webAreaCount = roleList.filter { $0 == "AXWebArea" }.count
let windowNumber = selected.flatMap { attribute($0, "AXWindowNumber" as CFString) as? NSNumber }?.intValue
let payload: [String: Any] = [
    "schema_version": "lifeos.p3_141.phase_b.pid_ax_attestation.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "window_count_for_pid": windows.count,
    "matched_title_window_count": matched.count,
    "selected_role": selected.flatMap { attribute($0, kAXRoleAttribute as CFString) as? String } ?? "",
    "window_number": windowNumber as Any,
    "position": selected.flatMap { point(attribute($0, kAXPositionAttribute as CFString)) } as Any,
    "size": selected.flatMap { size(attribute($0, kAXSizeAttribute as CFString)) } as Any,
    "ax_webview_count": webViewCount,
    "ax_webarea_count": webAreaCount,
    "web_content_ax_role": webViewCount == 1 ? "AXWebView" : (webAreaCount == 1 ? "AXWebArea" : "unresolved"),
    "roles": roleList,
    "pass": windows.count == 1 && matched.count == 1 && (webViewCount + webAreaCount) == 1
]
var data = try JSONSerialization.data(withJSONObject: payload, options: [.prettyPrinted, .sortedKeys])
data.append(0x0A)
try data.write(to: output)
if payload["pass"] as? Bool == true { exit(0) }
exit(1)
