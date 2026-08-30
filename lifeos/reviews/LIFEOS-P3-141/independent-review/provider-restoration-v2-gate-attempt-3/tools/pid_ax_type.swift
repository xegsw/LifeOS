import ApplicationServices
import CoreGraphics
import Foundation

func value(_ element: AXUIElement, _ attribute: String) -> AnyObject? { var raw: CFTypeRef?; guard AXUIElementCopyAttributeValue(element, attribute as CFString, &raw) == .success else { return nil }; return raw }
func text(_ element: AXUIElement, _ attribute: String) -> String { value(element, attribute) as? String ?? "" }
func children(_ element: AXUIElement) -> [AXUIElement] { value(element, kAXChildrenAttribute) as? [AXUIElement] ?? [] }
func find(_ element: AXUIElement, _ wantedRole: String, _ wantedTitle: String, _ depth: Int = 0) -> AXUIElement? { if depth > 16 { return nil }; if text(element, kAXRoleAttribute) == wantedRole && text(element, kAXTitleAttribute) == wantedTitle { return element }; for child in children(element) { if let match = find(child, wantedRole, wantedTitle, depth + 1) { return match } }; return nil }
func post(_ event: CGEvent, _ pid: pid_t) { event.postToPid(pid) }

guard CommandLine.arguments.count == 4, let pid = pid_t(CommandLine.arguments[1]) else { fputs("usage: pid_ax_type <pid> <textfield title> <text>\n", stderr); exit(64) }
let app = AXUIElementCreateApplication(pid)
guard let target = find(app, "AXTextField", CommandLine.arguments[2]) else { fputs("textfield_not_found\n", stderr); exit(2) }
guard AXUIElementPerformAction(target, kAXPressAction as CFString) == .success else { fputs("textfield_focus_failed\n", stderr); exit(3) }
let source = CGEventSource(stateID: .hidSystemState)
let selectDown = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: true)!; selectDown.flags = .maskCommand; post(selectDown, pid)
let selectUp = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: false)!; selectUp.flags = .maskCommand; post(selectUp, pid)
let units = Array(CommandLine.arguments[3].utf16)
let typeDown = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: true)!; units.withUnsafeBufferPointer { typeDown.keyboardSetUnicodeString(stringLength: units.count, unicodeString: $0.baseAddress!) }; post(typeDown, pid)
let typeUp = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: false)!; units.withUnsafeBufferPointer { typeUp.keyboardSetUnicodeString(stringLength: units.count, unicodeString: $0.baseAddress!) }; post(typeUp, pid)
let payload: [String: Any] = ["schema": "lifeos.p3-141.pid-ax-type.v1", "pid": pid, "title": CommandLine.arguments[2], "utf16_length": units.count, "targeted_pid": true, "text_content_recorded": false]
let data = try JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys]); FileHandle.standardOutput.write(data); FileHandle.standardOutput.write("\n".data(using: .utf8)!)
