import ApplicationServices
import Cocoa
import Foundation

guard CommandLine.arguments.count == 5,
      let pid = Int32(CommandLine.arguments[1]) else {
    fputs("usage: native_pid_ax_capture PID EXACT_TITLE TARGET_PNG REPORT_JSON\n", stderr)
    exit(64)
}

let expectedTitle = CommandLine.arguments[2]
let screenshotPath = CommandLine.arguments[3]
let reportPath = CommandLine.arguments[4]

func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success ? value : nil
}

func stringAttribute(_ element: AXUIElement, _ name: String) -> String? {
    attribute(element, name) as? String
}

func children(_ element: AXUIElement) -> [AXUIElement] {
    guard let values = attribute(element, kAXChildrenAttribute as String) as? [Any] else { return [] }
    return values.compactMap { $0 as! AXUIElement? }
}

func cgPoint(_ element: AXUIElement, _ name: String) -> [String: Double]? {
    guard let value = attribute(element, name) else { return nil }
    var point = CGPoint.zero
    guard AXValueGetType(value as! AXValue) == .cgPoint,
          AXValueGetValue(value as! AXValue, .cgPoint, &point) else { return nil }
    return ["x": Double(point.x), "y": Double(point.y)]
}

func cgSize(_ element: AXUIElement, _ name: String) -> [String: Double]? {
    guard let value = attribute(element, name) else { return nil }
    var size = CGSize.zero
    guard AXValueGetType(value as! AXValue) == .cgSize,
          AXValueGetValue(value as! AXValue, .cgSize, &size) else { return nil }
    return ["width": Double(size.width), "height": Double(size.height)]
}

func descendants(_ element: AXUIElement, depth: Int = 0) -> [[String: Any]] {
    guard depth < 16 else { return [] }
    let role = stringAttribute(element, kAXRoleAttribute as String) ?? ""
    let subrole = stringAttribute(element, kAXSubroleAttribute as String) ?? ""
    var rows: [[String: Any]] = [["role": role, "subrole": subrole]]
    for child in children(element) { rows.append(contentsOf: descendants(child, depth: depth + 1)) }
    return rows
}

let application = AXUIElementCreateApplication(pid)
let windows = (attribute(application, kAXWindowsAttribute as String) as? [Any] ?? []).compactMap { $0 as! AXUIElement? }
let matches = windows.filter { stringAttribute($0, kAXTitleAttribute as String) == expectedTitle }
let windowRows = matches.map { window -> [String: Any] in
    let tree = descendants(window)
    let webRoles = tree.filter { row in
        let role = row["role"] as? String ?? ""
        return role == "AXWebArea" || role == "AXWebView"
    }
    var row: [String: Any] = [
        "title": stringAttribute(window, kAXTitleAttribute as String) ?? "",
        "role": stringAttribute(window, kAXRoleAttribute as String) ?? "",
        "subrole": stringAttribute(window, kAXSubroleAttribute as String) ?? "",
        "webDescendants": webRoles,
    ]
    if let position = cgPoint(window, kAXPositionAttribute as String) { row["position"] = position }
    if let size = cgSize(window, kAXSizeAttribute as String) { row["size"] = size }
    return row
}

let cgInfo = (CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]]) ?? []
let cgMatches = cgInfo.filter { info in
    let owner = (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
    let name = info[kCGWindowName as String] as? String
    return owner == pid && name == expectedTitle
}
let windowNumber = (cgMatches.first?[kCGWindowNumber as String] as? NSNumber)?.intValue
var screenshotExit: Int32? = nil
if let windowNumber {
    let capture = Process()
    capture.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    capture.arguments = ["-x", "-l", String(windowNumber), screenshotPath]
    do {
        try capture.run()
        capture.waitUntilExit()
        screenshotExit = capture.terminationStatus
    } catch {
        screenshotExit = -1
    }
}

let targetHasWebContent = windowRows.contains { ($0["webDescendants"] as? [[String: Any]] ?? []).isEmpty == false }
let report: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.native-pid-ax.v1",
    "pid": Int(pid),
    "expectedTitle": expectedTitle,
    "matchedAXWindowCount": matches.count,
    "windows": windowRows,
    "matchedCGWindowCount": cgMatches.count,
    "windowNumber": windowNumber as Any,
    "screenshot": ["path": screenshotPath, "exit": screenshotExit as Any],
    "pass": matches.count == 1 && targetHasWebContent && windowNumber != nil && screenshotExit == 0,
]
let data = try JSONSerialization.data(withJSONObject: report, options: [.prettyPrinted, .sortedKeys])
try data.write(to: URL(fileURLWithPath: reportPath), options: .atomic)
print(String(data: data, encoding: .utf8)!)
if !(report["pass"] as? Bool ?? false) { exit(1) }
