import ApplicationServices
import CoreGraphics
import Foundation
import ImageIO
import ScreenCaptureKit
import UniformTypeIdentifiers

func writeJSON(_ value: Any) {
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

func hasNativeWebView(_ element: AXUIElement, depth: Int = 0) -> Bool {
  guard depth <= 14 else { return false }
  let role = axString(element, kAXRoleAttribute as CFString)
  if role == "AXWebArea" || role == "AXWebView" { return true }
  return axChildren(element).contains { hasNativeWebView($0, depth: depth + 1) }
}

func exactAXWindow(pid: pid_t) -> Bool {
  let application = AXUIElementCreateApplication(pid)
  var applicationPid: pid_t = 0
  guard AXUIElementGetPid(application, &applicationPid) == .success, applicationPid == pid else { return false }
  var rawWindows: CFTypeRef?
  guard AXUIElementCopyAttributeValue(application, kAXWindowsAttribute as CFString, &rawWindows) == .success,
        let windows = rawWindows as? [AXUIElement] else { return false }
  return windows.contains { hasNativeWebView($0) }
}

func exactCGWindow(pid: pid_t) -> CGWindowID? {
  let all = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] ?? []
  let matches = all.filter { ($0[kCGWindowOwnerPID as String] as? Int) == Int(pid) && ($0[kCGWindowLayer as String] as? Int) == 0 }
  guard matches.count == 1, let number = matches[0][kCGWindowNumber as String] as? Int else { return nil }
  return CGWindowID(number)
}

@main
struct DirectPidWindowCapture {
  static func main() async {
    guard CommandLine.arguments.count == 3, let requested = Int32(CommandLine.arguments[1]), requested > 0 else {
      writeJSON(["status": "invalid_argument", "usage": "direct_pid_window_capture <pid> <absolute-output-png>"])
      return
    }
    let pid = pid_t(requested)
    guard exactAXWindow(pid: pid) else {
      writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "direct_pid_ax_window_webview_binding_unavailable"])
      return
    }
    guard let cgWindow = exactCGWindow(pid: pid) else {
      writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "exact_pid_core_graphics_window_not_unique"])
      return
    }
    guard #available(macOS 14.0, *) else {
      writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "screencapturekit_unavailable"])
      return
    }
    do {
      let content = try await SCShareableContent.excludingDesktopWindows(false, onScreenWindowsOnly: true)
      let matches = content.windows.filter { $0.windowID == cgWindow && $0.owningApplication?.processID == pid }
      guard matches.count == 1, let window = matches.first else {
        writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "screencapturekit_window_not_exact_pid_bound", "core_graphics_window_number": Int(cgWindow)])
        return
      }
      let configuration = SCStreamConfiguration()
      configuration.width = max(1, Int(window.frame.width))
      configuration.height = max(1, Int(window.frame.height))
      configuration.showsCursor = false
      let image = try await SCScreenshotManager.captureImage(contentFilter: SCContentFilter(desktopIndependentWindow: window), configuration: configuration)
      let output = URL(fileURLWithPath: CommandLine.arguments[2])
      guard let destination = CGImageDestinationCreateWithURL(output as CFURL, UTType.png.identifier as CFString, 1, nil) else {
        writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "png_destination_failed"])
        return
      }
      CGImageDestinationAddImage(destination, image, nil)
      guard CGImageDestinationFinalize(destination) else {
        writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "png_write_failed"])
        return
      }
      writeJSON([
        "schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": true,
        "core_graphics_window_number": Int(cgWindow), "screen_capture_window_id": Int(window.windowID),
        "screen_capture_owner_pid": Int(window.owningApplication?.processID ?? 0), "output": output.path,
        "binding_rule": "AXWebArea/AXWebView and CoreGraphics identities are re-established for the exact launch PID before ScreenCaptureKit capture"
      ])
    } catch {
      writeJSON(["schema": "lifeos.p3-141.direct-pid-window-capture.v1", "requested_pid": Int(requested), "success": false, "reason": "screencapturekit_error", "raw_error": String(describing: error)])
    }
  }
}
