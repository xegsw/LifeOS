import ApplicationServices
import Foundation

guard CommandLine.arguments.count == 5, let pid = pid_t(CommandLine.arguments[1]) else {
    fputs("usage: set_exact_pid_text <pid> <expected-title> <field-label> <synthetic-text>\n", stderr)
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]
let wanted = CommandLine.arguments[3]
let text = CommandLine.arguments[4]
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
    let role = string(element, kAXRoleAttribute) ?? ""
    let label = string(element, kAXTitleAttribute) ?? string(element, kAXDescriptionAttribute) ?? ""
    if (role == "AXTextField" || role == "AXTextArea") && label == wanted { return element }
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
guard let field = find(window, &visited) else {
    fputs("exact PID labelled text field not found\n", stderr)
    exit(1)
}
let status = AXUIElementSetAttributeValue(field, kAXValueAttribute as CFString, text as CFString)
let receipt: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.exact-pid-text.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "field_label": wanted,
    "synthetic_input": true,
    "input_length": text.count,
    "status": status.rawValue,
    "scope": "direct PID/exact AXWindow only; value intentionally omitted"
]
let data = try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
if status != .success { exit(1) }
