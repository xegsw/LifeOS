import ApplicationServices
import Foundation

guard CommandLine.arguments.count == 5,
      let pid = pid_t(CommandLine.arguments[1]),
      let width = Double(CommandLine.arguments[3]),
      let height = Double(CommandLine.arguments[4]) else {
    fputs("usage: set_exact_pid_window_geometry <pid> <expected-title> <width> <height>\n", stderr)
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]
func attribute(_ element: AXUIElement, _ name: String) -> CFTypeRef? {
    var value: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, name as CFString, &value) == .success ? value : nil
}
func string(_ element: AXUIElement, _ name: String) -> String? { attribute(element, name) as? String }
let app = AXUIElementCreateApplication(pid)
let windows = (attribute(app, kAXWindowsAttribute) as? [AXUIElement]) ?? []
guard let window = windows.first(where: { string($0, kAXTitleAttribute) == expectedTitle && string($0, kAXRoleAttribute) == "AXWindow" }) else {
    fputs("exact PID/title AXWindow not found\n", stderr)
    exit(1)
}
var position = CGPoint(x: 48, y: 36)
var size = CGSize(width: width, height: height)
let positionValue = AXValueCreate(.cgPoint, &position)!
let sizeValue = AXValueCreate(.cgSize, &size)!
let positionStatus = AXUIElementSetAttributeValue(window, kAXPositionAttribute as CFString, positionValue)
let sizeStatus = AXUIElementSetAttributeValue(window, kAXSizeAttribute as CFString, sizeValue)
let raiseStatus = AXUIElementPerformAction(window, kAXRaiseAction as CFString)
let result: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.exact-pid-geometry.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "requested": ["width": width, "height": height],
    "position_status": positionStatus.rawValue,
    "size_status": sizeStatus.rawValue,
    "raise_status": raiseStatus.rawValue
]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
if positionStatus != .success || sizeStatus != .success || raiseStatus != .success { exit(1) }
