import ApplicationServices
import Foundation

struct ProbeError: Error { let message: String }

func text(_ element: AXUIElement, _ attribute: CFString) -> String? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success,
          let string = value as? String else { return nil }
    return string
}

func number(_ element: AXUIElement, _ attribute: CFString) -> Int? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success,
          let value, CFGetTypeID(value) == CFNumberGetTypeID() else { return nil }
    var result: Int = 0
    guard CFNumberGetValue(unsafeBitCast(value, to: CFNumber.self), .cfIndexType, &result) else { return nil }
    return result
}

func rect(_ element: AXUIElement) -> CGRect? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, "AXFrame" as CFString, &value) == .success,
          let value, AXValueGetType(value as! AXValue) == .cgRect else { return nil }
    var result = CGRect.zero
    return AXValueGetValue(value as! AXValue, .cgRect, &result) ? result : nil
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &value) == .success,
          let items = value as? [AXUIElement] else { return [] }
    return items
}

func attributeNames(_ element: AXUIElement) -> [String] {
    var value: CFArray?
    guard AXUIElementCopyAttributeNames(element, &value) == .success,
          let value else { return [] }
    return (value as NSArray).compactMap { $0 as? String }.sorted()
}

func relatedElements(_ element: AXUIElement) -> [AXUIElement] {
    let relationNames = ["AXChildren", "AXContents", "AXVisibleChildren", "AXFocusedUIElement"]
    return relationNames.flatMap { relation -> [AXUIElement] in
        var value: CFTypeRef?
        guard AXUIElementCopyAttributeValue(element, relation as CFString, &value) == .success,
              let value else { return [] }
        if CFGetTypeID(value) == AXUIElementGetTypeID() {
            return [unsafeBitCast(value, to: AXUIElement.self)]
        }
        return (value as? [AXUIElement]) ?? []
    }
}

func windows(_ application: AXUIElement) -> [AXUIElement] {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(application, "AXWindows" as CFString, &value) == .success,
          let items = value as? [AXUIElement] else { return [] }
    return items
}

func rolesBelow(_ root: AXUIElement) -> [String: Int] {
    var result: [String: Int] = [:]
    var queue: [AXUIElement] = [root]
    var visited = 0
    while !queue.isEmpty && visited < 2048 {
        let item = queue.removeFirst()
        visited += 1
        if let role = text(item, kAXRoleAttribute as CFString) { result[role, default: 0] += 1 }
        queue.append(contentsOf: relatedElements(item))
    }
    result["__visited__"] = visited
    return result
}

func jsonData(_ value: Any) throws -> Data {
    try JSONSerialization.data(withJSONObject: value, options: [.prettyPrinted, .sortedKeys])
}

let arguments = CommandLine.arguments
guard arguments.count == 4 else {
    fputs("usage: ax_pid_probe <pid> <exact-title> <output-json>\\n", stderr)
    exit(64)
}
guard let pid = pid_t(arguments[1]) else { throw ProbeError(message: "invalid pid") }
let expectedTitle = arguments[2]
let output = URL(fileURLWithPath: arguments[3])
guard AXIsProcessTrusted() else { throw ProbeError(message: "accessibility_not_trusted") }

let application = AXUIElementCreateApplication(pid)
let candidates = windows(application)
let matched = candidates.filter { text($0, kAXTitleAttribute as CFString) == expectedTitle }
let records: [[String: Any]] = matched.map { window in
    let frame = rect(window) ?? .zero
    let roles = rolesBelow(window)
    return [
        "title": text(window, kAXTitleAttribute as CFString) ?? "",
        "window_number": number(window, "AXWindowNumber" as CFString) as Any,
        "attribute_names": attributeNames(window),
        "frame": ["x": frame.origin.x, "y": frame.origin.y, "width": frame.size.width, "height": frame.size.height],
        "roles": roles,
        "has_ax_web_area": (roles["AXWebArea"] ?? 0) > 0,
        "has_ax_web_view": (roles["AXWebView"] ?? 0) > 0,
    ]
}
let payload: [String: Any] = [
    "schema": "lifeos.p3-141.attempt6.ax-pid-probe.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "accessibility_trusted": true,
    "application_role": text(application, kAXRoleAttribute as CFString) ?? "",
    "candidate_window_count": candidates.count,
    "exact_title_window_count": records.count,
    "windows": records,
    "status": records.count == 1 && ((records[0]["has_ax_web_area"] as? Bool) == true || (records[0]["has_ax_web_view"] as? Bool) == true) ? "PASS" : "FAIL",
]
try jsonData(payload).write(to: output, options: .atomic)
print(String(data: try jsonData(payload), encoding: .utf8)!)
