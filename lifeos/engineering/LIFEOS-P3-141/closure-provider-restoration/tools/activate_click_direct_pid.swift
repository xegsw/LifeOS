import AppKit
import ApplicationServices
import Foundation

private func stringAttribute(_ element: AXUIElement, _ attribute: CFString) -> String {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success else { return "" }
    return value as? String ?? ""
}

private func frameAttribute(_ element: AXUIElement) -> CGRect? {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, "AXFrame" as CFString, &value) == .success,
          let axValue = value, CFGetTypeID(axValue) == AXValueGetTypeID() else { return nil }
    var frame = CGRect.zero
    guard AXValueGetValue((axValue as! AXValue), .cgRect, &frame) else { return nil }
    return frame
}

guard CommandLine.arguments.count == 5,
      let rawPid = Int32(CommandLine.arguments[1]), rawPid > 0,
      let relativeX = Double(CommandLine.arguments[3]),
      let relativeY = Double(CommandLine.arguments[4]),
      let application = NSRunningApplication(processIdentifier: rawPid) else {
    FileHandle.standardError.write(Data("usage: activate_click_direct_pid <direct-pid> <exact-title> <relative-x> <relative-y>\n".utf8))
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]
let app = AXUIElementCreateApplication(rawPid)
var windowsValue: CFTypeRef?
guard AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &windowsValue) == .success,
      let windows = windowsValue as? [AXUIElement] else { exit(65) }
let matching = windows.filter { stringAttribute($0, kAXTitleAttribute as CFString) == expectedTitle }
guard matching.count == 1, let frame = frameAttribute(matching[0]) else { exit(66) }
guard relativeX >= 0, relativeY >= 0, relativeX < frame.width, relativeY < frame.height else { exit(67) }
guard application.activate(options: []) else { exit(68) }
let point = CGPoint(x: frame.origin.x + relativeX, y: frame.origin.y + relativeY)
guard let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
      let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else { exit(69) }
down.post(tap: .cghidEventTap)
up.post(tap: .cghidEventTap)
let result: [String: Any] = [
    "direct_pid": Int(rawPid), "exact_title": expectedTitle,
    "window_frame": ["x": frame.origin.x, "y": frame.origin.y, "width": frame.width, "height": frame.height],
    "relative_click": ["x": relativeX, "y": relativeY],
    "global_click": ["x": point.x, "y": point.y]
]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
