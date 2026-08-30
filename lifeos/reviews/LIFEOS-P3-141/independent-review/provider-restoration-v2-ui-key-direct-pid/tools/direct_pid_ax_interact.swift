import ApplicationServices
import CoreGraphics
import Foundation

func emit(_ value: Any) {
  let data = try! JSONSerialization.data(withJSONObject: value, options: [.sortedKeys])
  FileHandle.standardOutput.write(data)
  FileHandle.standardOutput.write(Data("\n".utf8))
}

func axString(_ element: AXUIElement, _ attribute: CFString) -> String? {
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success else { return nil }
  return value as? String
}

func axChildren(_ element: AXUIElement) -> [AXUIElement] {
  var value: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &value) == .success else { return [] }
  return value as? [AXUIElement] ?? []
}

func frame(_ element: AXUIElement) -> CGRect? {
  var positionValue: CFTypeRef?
  var sizeValue: CFTypeRef?
  guard AXUIElementCopyAttributeValue(element, kAXPositionAttribute as CFString, &positionValue) == .success,
        AXUIElementCopyAttributeValue(element, kAXSizeAttribute as CFString, &sizeValue) == .success,
        let positionValue, let sizeValue else { return nil }
  let positionAX = positionValue as! AXValue
  let sizeAX = sizeValue as! AXValue
  var point = CGPoint.zero
  var size = CGSize.zero
  guard AXValueGetValue(positionAX, .cgPoint, &point), AXValueGetValue(sizeAX, .cgSize, &size) else { return nil }
  return CGRect(origin: point, size: size)
}

func frameValue(_ value: CGRect) -> [String: Double] {
  ["x": Double(value.origin.x), "y": Double(value.origin.y), "width": Double(value.size.width), "height": Double(value.size.height)]
}

func hasWebView(_ element: AXUIElement, depth: Int = 0) -> Bool {
  guard depth <= 14 else { return false }
  let role = axString(element, kAXRoleAttribute as CFString)
  if role == "AXWebArea" || role == "AXWebView" { return true }
  return axChildren(element).contains { hasWebView($0, depth: depth + 1) }
}

func exactWindow(pid: pid_t) -> (AXUIElement, CGRect, Int)? {
  let app = AXUIElementCreateApplication(pid)
  var appPid: pid_t = 0
  guard AXUIElementGetPid(app, &appPid) == .success, appPid == pid else { return nil }
  var rawWindows: CFTypeRef?
  guard AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &rawWindows) == .success,
        let windows = rawWindows as? [AXUIElement] else { return nil }
  for (index, window) in windows.enumerated() {
    if let bounds = frame(window), hasWebView(window) { return (window, bounds, index) }
  }
  return nil
}

func exactCGWindow(pid: pid_t) -> (CGWindowID, [String: Any])? {
  let all = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
  let matches = all.filter { ($0[kCGWindowOwnerPID as String] as? Int) == Int(pid) && ($0[kCGWindowLayer as String] as? Int) == 0 }
  guard matches.count == 1, let item = matches.first, let number = item[kCGWindowNumber as String] as? Int else { return nil }
  return (CGWindowID(number), item)
}

func fail(_ pid: pid_t, _ action: String, _ reason: String) -> Never {
  emit(["schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(pid), "action": action, "success": false, "reason": reason])
  exit(3)
}

guard CommandLine.arguments.count >= 3, let rawPid = Int32(CommandLine.arguments[2]), rawPid > 0 else {
  emit(["status": "invalid_argument", "usage": "direct_pid_ax_interact <identity|raise|resize|click|click-global-bound|scroll-global-bound|key-global-bound> <pid> [arguments]"])
  exit(64)
}
let action = CommandLine.arguments[1]
let pid = pid_t(rawPid)
guard let (window, currentFrame, windowIndex) = exactWindow(pid: pid) else { fail(pid, action, "direct_pid_ax_window_webview_binding_unavailable") }

switch action {
case "identity":
  guard CommandLine.arguments.count == 3 else { fail(pid, action, "identity_accepts_only_pid") }
  guard let (cgID, cgInfo) = exactCGWindow(pid: pid) else { fail(pid, action, "exact_pid_core_graphics_window_not_unique") }
  emit([
    "schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(rawPid), "action": action,
    "success": true, "ax_window_index": windowIndex, "ax_window_frame": frameValue(currentFrame),
    "core_graphics_window_number": Int(cgID), "core_graphics_title": cgInfo[kCGWindowName as String] as? String ?? "",
    "binding_rule": "rechecks exact PID -> AXWindow -> AXWebArea/AXWebView before every operation"
  ])
case "raise":
  guard CommandLine.arguments.count == 3 else { fail(pid, action, "raise_accepts_only_pid") }
  let result = AXUIElementPerformAction(window, kAXRaiseAction as CFString)
  guard result == .success else { fail(pid, action, "ax_raise_error_\(result.rawValue)") }
  emit([
    "schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(rawPid), "action": action,
    "success": true, "ax_window_index": windowIndex, "ax_window_frame": frameValue(currentFrame),
    "binding_rule": "raises only the already exact-PID-bound AXWindow, never an app-name or frontmost-window selection"
  ])
case "resize":
  guard CommandLine.arguments.count == 5, let width = Double(CommandLine.arguments[3]), let height = Double(CommandLine.arguments[4]), width > 0, height > 0 else { fail(pid, action, "resize_requires_positive_width_height") }
  var targetSize = CGSize(width: width, height: height)
  guard let value = AXValueCreate(.cgSize, &targetSize) else { fail(pid, action, "ax_size_value_failed") }
  let result = AXUIElementSetAttributeValue(window, kAXSizeAttribute as CFString, value)
  guard result == .success else { fail(pid, action, "ax_resize_error_\(result.rawValue)") }
  Thread.sleep(forTimeInterval: 0.55)
  guard let observed = frame(window) else { fail(pid, action, "ax_frame_unavailable_after_resize") }
  emit([
    "schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(rawPid), "action": action,
    "success": true, "ax_window_index": windowIndex, "before": frameValue(currentFrame), "after": frameValue(observed),
    "requested_size": ["width": width, "height": height], "binding_rule": "rechecks exact PID -> AXWindow -> AXWebArea/AXWebView before every operation"
  ])
case "click", "click-global-bound":
  guard CommandLine.arguments.count == 5, let x = Double(CommandLine.arguments[3]), let y = Double(CommandLine.arguments[4]) else { fail(pid, action, "click_requires_absolute_x_y") }
  let point = CGPoint(x: x, y: y)
  guard currentFrame.contains(point) else { fail(pid, action, "click_point_outside_bound_ax_window") }
  guard let down = CGEvent(mouseEventSource: nil, mouseType: .leftMouseDown, mouseCursorPosition: point, mouseButton: .left),
        let up = CGEvent(mouseEventSource: nil, mouseType: .leftMouseUp, mouseCursorPosition: point, mouseButton: .left) else { fail(pid, action, "core_graphics_event_creation_failed") }
  let route: String
  if action == "click-global-bound" {
    let raiseResult = AXUIElementPerformAction(window, kAXRaiseAction as CFString)
    guard raiseResult == .success else { fail(pid, action, "ax_raise_before_global_click_error_\(raiseResult.rawValue)") }
    down.post(tap: .cghidEventTap)
    route = "global_event_after_rechecking_and_raising_exact_pid_bound_AXWindow"
  } else {
    down.postToPid(pid)
    route = "CGEventPostToPid_exact_launch_pid"
  }
  usleep(35_000)
  if action == "click-global-bound" { up.post(tap: .cghidEventTap) } else { up.postToPid(pid) }
  emit([
    "schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(rawPid), "action": action,
    "success": true, "ax_window_index": windowIndex, "ax_window_frame": frameValue(currentFrame),
    "point": ["x": x, "y": y], "event_route": route,
    "binding_rule": "rechecks exact PID -> AXWindow -> AXWebArea/AXWebView before every operation; global route is permitted only after this direct binding and exact AX raise, then requires same-PID recapture"
  ])
case "scroll-global-bound":
  guard CommandLine.arguments.count == 6, let x = Double(CommandLine.arguments[3]), let y = Double(CommandLine.arguments[4]), let lines = Int32(CommandLine.arguments[5]) else { fail(pid, action, "scroll_requires_absolute_x_y_lines") }
  let point = CGPoint(x: x, y: y)
  guard currentFrame.contains(point) else { fail(pid, action, "scroll_point_outside_bound_ax_window") }
  let raiseResult = AXUIElementPerformAction(window, kAXRaiseAction as CFString)
  guard raiseResult == .success else { fail(pid, action, "ax_raise_before_scroll_error_\(raiseResult.rawValue)") }
  guard let scroll = CGEvent(scrollWheelEvent2Source: nil, units: .line, wheelCount: 1, wheel1: lines, wheel2: 0, wheel3: 0) else { fail(pid, action, "scroll_event_creation_failed") }
  scroll.location = point
  scroll.post(tap: .cghidEventTap)
  emit([
    "schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(rawPid), "action": action,
    "success": true, "ax_window_index": windowIndex, "ax_window_frame": frameValue(currentFrame),
    "point": ["x": x, "y": y], "lines": Int(lines), "event_route": "global_scroll_after_rechecking_and_raising_exact_pid_bound_AXWindow",
    "binding_rule": "rechecks exact PID -> AXWindow -> AXWebArea/AXWebView before every operation; requires same-PID recapture"
  ])
case "key-global-bound":
  guard CommandLine.arguments.count == 4 else { fail(pid, action, "key_requires_one_named_key") }
  let keyName = CommandLine.arguments[3]
  let keyCode: CGKeyCode
  switch keyName {
  case "down": keyCode = 125
  case "up": keyCode = 126
  case "return": keyCode = 36
  case "tab": keyCode = 48
  case "escape": keyCode = 53
  default: fail(pid, action, "unsupported_named_key")
  }
  let raiseResult = AXUIElementPerformAction(window, kAXRaiseAction as CFString)
  guard raiseResult == .success else { fail(pid, action, "ax_raise_before_global_key_error_\(raiseResult.rawValue)") }
  guard let down = CGEvent(keyboardEventSource: nil, virtualKey: keyCode, keyDown: true),
        let up = CGEvent(keyboardEventSource: nil, virtualKey: keyCode, keyDown: false) else { fail(pid, action, "keyboard_event_creation_failed") }
  down.post(tap: .cghidEventTap)
  usleep(35_000)
  up.post(tap: .cghidEventTap)
  emit([
    "schema": "lifeos.p3-141.direct-pid-ax-interact.v1", "requested_pid": Int(rawPid), "action": action,
    "success": true, "ax_window_index": windowIndex, "ax_window_frame": frameValue(currentFrame),
    "key": keyName, "event_route": "global_key_after_rechecking_and_raising_exact_pid_bound_AXWindow",
    "binding_rule": "rechecks exact PID -> AXWindow -> AXWebArea/AXWebView before every operation; global key route is permitted only after this direct binding and exact AX raise"
  ])
default:
  fail(pid, action, "unsupported_action")
}
