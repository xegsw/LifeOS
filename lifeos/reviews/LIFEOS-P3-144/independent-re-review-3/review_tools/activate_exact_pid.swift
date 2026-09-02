import AppKit
import ApplicationServices
import Foundation

guard CommandLine.arguments.count == 3, let pid = pid_t(CommandLine.arguments[1]) else {
    fputs("usage: activate_exact_pid <pid> <expected-title>\n", stderr)
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]
func string(_ element: AXUIElement, _ attribute: String) -> String? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute as CFString, &value) == .success else { return nil }
    return value as? String
}
let axApp = AXUIElementCreateApplication(pid)
var value: CFTypeRef?
let windows = AXUIElementCopyAttributeValue(axApp, kAXWindowsAttribute as CFString, &value) == .success ? (value as? [AXUIElement] ?? []) : []
guard windows.contains(where: { string($0, kAXRoleAttribute) == "AXWindow" && string($0, kAXTitleAttribute) == expectedTitle }),
      let app = NSRunningApplication(processIdentifier: pid) else {
    fputs("exact PID/title runnable application not found\n", stderr)
    exit(1)
}
app.unhide()
let activated = app.activate(options: [.activateAllWindows, .activateIgnoringOtherApps])
let receipt: [String: Any] = [
    "schema": "lifeos.p3-144.independent-review.exact-pid-activation.v1",
    "pid": Int(pid),
    "expected_title": expectedTitle,
    "unhide": true,
    "activate_all_windows": true,
    "activated": activated
]
let data = try JSONSerialization.data(withJSONObject: receipt, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
if !activated { exit(1) }
