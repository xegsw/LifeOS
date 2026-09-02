import ApplicationServices
import Foundation

guard CommandLine.arguments.count == 4, let pid = pid_t(CommandLine.arguments[1]) else {
    fputs("usage: press_exact_pid_button <pid> <expected-title> <button-label>\n", stderr)
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]
let wanted = CommandLine.arguments[3]
func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var result: CFTypeRef?
    return AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success ? result : nil
}
func string(_ element: AXUIElement, _ attribute: String) -> String? { value(element, attribute) as? String }
func related(_ element: AXUIElement) -> [AXUIElement] {
    [kAXChildrenAttribute, "AXContents", "AXVisibleChildren"].flatMap { attribute -> [AXUIElement] in
        guard let result = value(element, attribute) else { return [] }
        if CFGetTypeID(result) == AXUIElementGetTypeID() { return [result as! AXUIElement] }
        return (result as? [AXUIElement]) ?? []
    }
}
func find(_ element: AXUIElement, _ visited: inout Set<Int>) -> AXUIElement? {
    let identity = Int(CFHash(element))
    guard visited.insert(identity).inserted else { return nil }
    if string(element, kAXRoleAttribute) == "AXButton" && (string(element, kAXTitleAttribute) == wanted || string(element, kAXDescriptionAttribute) == wanted) {
        return element
    }
    for child in related(element) {
        if let found = find(child, &visited) { return found }
    }
    return nil
}
let app = AXUIElementCreateApplication(pid)
let windows = (value(app, kAXWindowsAttribute) as? [AXUIElement]) ?? []
guard let window = windows.first(where: { string($0, kAXRoleAttribute) == "AXWindow" && string($0, kAXTitleAttribute) == expectedTitle }) else {
    fputs("exact PID/title AXWindow not found\n", stderr)
    exit(1)
}
var visited = Set<Int>()
guard let button = find(window, &visited) else {
    fputs("exact PID button not found\n", stderr)
    exit(1)
}
let status = AXUIElementPerformAction(button, kAXPressAction as CFString)
let receipt: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.exact-pid-press.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "button_label": wanted,
    "status": status.rawValue,
    "scope": "direct PID/exact AXWindow only"
]
let data = try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
if status != .success { exit(1) }
