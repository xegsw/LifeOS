import AppKit
import ApplicationServices
import Foundation

let title = "LifeOS · P3-141 Controlled Pilot Candidate"

func stringAttribute(_ element: AXUIElement, _ attribute: CFString) -> String? {
    var raw: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute, &raw) == .success else { return nil }
    return raw as? String
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    var raw: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &raw) == .success else { return [] }
    return raw as? [AXUIElement] ?? []
}

func frame(_ element: AXUIElement) -> [String: Double]? {
    var rawPosition: CFTypeRef?
    var rawSize: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, kAXPositionAttribute as CFString, &rawPosition) == .success,
          AXUIElementCopyAttributeValue(element, kAXSizeAttribute as CFString, &rawSize) == .success,
          let positionValue = rawPosition, let sizeValue = rawSize,
          CFGetTypeID(positionValue) == AXValueGetTypeID(), CFGetTypeID(sizeValue) == AXValueGetTypeID() else { return nil }
    var position = CGPoint.zero
    var size = CGSize.zero
    guard AXValueGetValue(unsafeBitCast(positionValue, to: AXValue.self), .cgPoint, &position),
          AXValueGetValue(unsafeBitCast(sizeValue, to: AXValue.self), .cgSize, &size) else { return nil }
    return ["x": Double(position.x), "y": Double(position.y), "width": Double(size.width), "height": Double(size.height)]
}

func descendantRoles(_ root: AXUIElement) -> [String] {
    var result: [String] = []
    var queue = children(root)
    var index = 0
    while index < queue.count && result.count < 512 {
        let item = queue[index]
        index += 1
        if let role = stringAttribute(item, kAXRoleAttribute as CFString) { result.append(role) }
        queue.append(contentsOf: children(item))
    }
    return result
}

func acceptsBinding(windowRole: String, descendantRoles: [String]) -> Bool {
    windowRole == "AXWindow" && descendantRoles.contains { $0 == "AXWebArea" || $0 == "AXWebView" }
}

func emit(_ object: [String: Any]) -> Never {
    let data = try! JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted, .sortedKeys])
    FileHandle.standardOutput.write(data)
    FileHandle.standardOutput.write("\n".data(using: .utf8)!)
    exit(0)
}

if CommandLine.arguments.count == 2 && CommandLine.arguments[1] == "--negative-selftest" {
    let controls = [
        "window_only_rejected": !acceptsBinding(windowRole: "AXWindow", descendantRoles: []),
        "axhtmlcontent_only_rejected": !acceptsBinding(windowRole: "AXWindow", descendantRoles: ["AXHTMLContent"]),
    ]
    emit(["verdict": controls.values.allSatisfy { $0 } ? "Pass" : "Rejected", "controls": controls])
}

guard CommandLine.arguments.count == 2, let pid = pid_t(CommandLine.arguments[1]) else {
    emit(["verdict": "Rejected", "reason": "usage_requires_direct_pid"])
}

let app = AXUIElementCreateApplication(pid)
var rawWindows: CFTypeRef?
guard AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &rawWindows) == .success,
      let windows = rawWindows as? [AXUIElement] else {
    emit(["verdict": "Rejected", "pid": Int(pid), "reason": "direct_pid_has_no_ax_windows"])
}
let matching = windows.filter { stringAttribute($0, kAXTitleAttribute as CFString) == title }
guard matching.count == 1 else {
    emit(["verdict": "Rejected", "pid": Int(pid), "reason": "exact_title_window_not_unique", "matching_window_count": matching.count])
}
let window = matching[0]
let windowRole = stringAttribute(window, kAXRoleAttribute as CFString) ?? ""
let roles = descendantRoles(window)
let webRoles = roles.filter { $0 == "AXWebArea" || $0 == "AXWebView" }
let htmlOnlyProbeRejected = !acceptsBinding(windowRole: "AXWindow", descendantRoles: ["AXHTMLContent"])
let windowOnlyRejected = !acceptsBinding(windowRole: "AXWindow", descendantRoles: [])
let cgWindows = (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]]) ?? []
let cgMatches = cgWindows.filter {
    ($0[kCGWindowOwnerPID as String] as? Int32) == Int32(pid)
        && ($0[kCGWindowName as String] as? String) == title
}
let cgWindowID = cgMatches.first?[kCGWindowNumber as String] as? Int
guard acceptsBinding(windowRole: windowRole, descendantRoles: roles) else {
    emit([
        "verdict": "Rejected", "pid": Int(pid), "reason": "window_only_or_non_native_webview_binding",
        "window_role": windowRole, "descendant_roles": roles,
        "window_only_rejected": windowOnlyRejected, "axhtmlcontent_only_rejected": htmlOnlyProbeRejected
    ])
}
emit([
    "verdict": "Pass", "pid": Int(pid), "exact_title": title,
    "matching_window_count": matching.count, "window_role": windowRole,
    "window_frame": frame(window) as Any, "native_web_roles": webRoles,
    "descendant_roles": roles, "window_only_rejected": windowOnlyRejected,
    "axhtmlcontent_only_rejected": htmlOnlyProbeRejected,
    "cg_exact_title_window_count": cgMatches.count, "cg_window_id": cgWindowID as Any,
    "binding": "direct PID -> unique exact-title AXWindow -> native AXWebArea/AXWebView"
])
