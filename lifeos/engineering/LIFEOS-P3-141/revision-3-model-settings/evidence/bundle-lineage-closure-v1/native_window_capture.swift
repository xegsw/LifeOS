import ApplicationServices
import Cocoa
import CoreGraphics
import Foundation
import ImageIO

struct Frame: Codable { let x: Double; let y: Double; let width: Double; let height: Double }
struct CGCandidate: Codable { let windowID: UInt32; let name: String; let frame: Frame }
struct Capture: Codable {
  let schema = "lifeos.p3-141.bundle-lineage.window-capture.v1"
  let pid: Int32
  let expectedTitle: String
  let windowCount: Int
  let matchingWindowCount: Int
  let frame: Frame?
  let positionNormalization: String
  let webRoles: [String]
  let settingsPress: String
  let cgCandidates: [CGCandidate]
  let matchingCGWindowCount: Int
  let cgWindowID: UInt32?
  let captureScope: String
  let screenshotExit: Int32?
  let visibleText: [String]
  let positiveTextPresent: Bool
  let forbiddenTextPresent: Bool
  let pass: Bool
  let reason: String
  let captureMethod: String
  let appWasFrontmost: Bool
  let windowWasFocused: Bool
  let foreignOverlayCount: Int
  let requestedRegion: Frame?
  let backingScaleFactor: Double?
  let outputPixelWidth: Int?
  let outputPixelHeight: Int?
  let pixelDimensionsMatch: Bool?
}

let title = "LifeOS · P3-141 Controlled Pilot Candidate"
let required = ["模型设置", "API Key", "加密保存", "SQLite"]
let forbidden = ["本次会话 API Key", "API Key 仅保留在本次会话", "清除本次会话 API Key", "环境变量名引用"]

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
  var output: CFTypeRef?
  return AXUIElementCopyAttributeValue(element, attribute as CFString, &output) == .success ? output : nil
}

func text(_ element: AXUIElement, _ attribute: String) -> String? { value(element, attribute) as? String }
func children(_ element: AXUIElement) -> [AXUIElement] { (value(element, kAXChildrenAttribute) as? [AXUIElement]) ?? [] }

func descendants(_ root: AXUIElement, limit: Int = 8192) -> [AXUIElement] {
  var queue = children(root), result: [AXUIElement] = []
  while !queue.isEmpty && result.count < limit {
    let next = queue.removeFirst()
    result.append(next)
    queue.append(contentsOf: children(next))
  }
  return result
}

func frame(_ element: AXUIElement) -> Frame? {
  guard let rawPosition = value(element, kAXPositionAttribute), let rawSize = value(element, kAXSizeAttribute) else { return nil }
  let positionBox = unsafeBitCast(rawPosition, to: AXValue.self)
  let sizeBox = unsafeBitCast(rawSize, to: AXValue.self)
  var position = CGPoint.zero
  var size = CGSize.zero
  guard AXValueGetValue(positionBox, .cgPoint, &position), AXValueGetValue(sizeBox, .cgSize, &size) else { return nil }
  return Frame(x: Double(position.x), y: Double(position.y), width: Double(size.width), height: Double(size.height))
}

func sameBounds(_ ax: Frame, _ cg: CGRect) -> Bool {
  let tolerance = 2.0
  let matchingY = abs(ax.y - Double(cg.origin.y)) <= tolerance
    || abs((NSScreen.main?.frame.height ?? 0) - ax.y - ax.height - Double(cg.origin.y)) <= tolerance
  return abs(ax.x - Double(cg.origin.x)) <= tolerance
    && matchingY
    && abs(ax.width - Double(cg.size.width)) <= tolerance
    && abs(ax.height - Double(cg.size.height)) <= tolerance
}

func overlaps(_ left: CGRect, _ right: CGRect) -> Bool {
  !left.intersection(right).isNull && !left.intersection(right).isEmpty
}

func imagePixels(_ path: String) -> (Int, Int)? {
  guard let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
        let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
        let width = properties[kCGImagePropertyPixelWidth] as? Int,
        let height = properties[kCGImagePropertyPixelHeight] as? Int else { return nil }
  return (width, height)
}

func emit(_ result: Capture, code: Int32) -> Never {
  let encoder = JSONEncoder()
  encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
  FileHandle.standardOutput.write(try! encoder.encode(result))
  FileHandle.standardOutput.write(Data("\n".utf8))
  exit(code)
}

guard CommandLine.arguments.count == 3, let pid = Int32(CommandLine.arguments[1]) else {
  fputs("usage: native_window_capture <direct-pid> <target-window-png>\n", stderr)
  exit(64)
}

let screenshotPath = CommandLine.arguments[2]
let application = AXUIElementCreateApplication(pid_t(pid))
_ = AXUIElementSetAttributeValue(application, "AXManualAccessibility" as CFString, kCFBooleanTrue)
let runningApplication = NSRunningApplication(processIdentifier: pid_t(pid))
_ = runningApplication?.activate(options: [.activateAllWindows, .activateIgnoringOtherApps])
usleep(400_000)
let windows = (value(application, kAXWindowsAttribute) as? [AXUIElement]) ?? []
let matching = windows.filter { text($0, kAXTitleAttribute) == title }
guard matching.count == 1, let window = matching.first, let axFrame = frame(window) else {
  emit(Capture(pid: pid, expectedTitle: title, windowCount: windows.count, matchingWindowCount: matching.count, frame: nil, positionNormalization: "not_attempted", webRoles: [], settingsPress: "not_attempted", cgCandidates: [], matchingCGWindowCount: 0, cgWindowID: nil, captureScope: "fail_closed_no_exact_ax_window", screenshotExit: nil, visibleText: [], positiveTextPresent: false, forbiddenTextPresent: false, pass: false, reason: "direct PID did not expose one exact-title AXWindow", captureMethod: "none", appWasFrontmost: false, windowWasFocused: false, foreignOverlayCount: 0, requestedRegion: nil, backingScaleFactor: nil, outputPixelWidth: nil, outputPixelHeight: nil, pixelDimensionsMatch: nil), code: 2)
}
let positionNormalization = "not_requested"

let initialNodes = descendants(window)
let settingsButton = initialNodes.first { element in
  guard text(element, kAXRoleAttribute) == kAXButtonRole else { return false }
  return [text(element, kAXTitleAttribute), text(element, kAXDescriptionAttribute), text(element, kAXHelpAttribute)].contains("Settings")
}
let settingsPress: String
if let button = settingsButton {
  settingsPress = AXUIElementPerformAction(button, kAXPressAction as CFString) == .success ? "pressed" : "press_rejected"
} else {
  settingsPress = "settings_button_missing"
}
guard settingsPress == "pressed" else {
  emit(Capture(pid: pid, expectedTitle: title, windowCount: windows.count, matchingWindowCount: matching.count, frame: axFrame, positionNormalization: positionNormalization, webRoles: [], settingsPress: settingsPress, cgCandidates: [], matchingCGWindowCount: 0, cgWindowID: nil, captureScope: "fail_closed_before_capture", screenshotExit: nil, visibleText: [], positiveTextPresent: false, forbiddenTextPresent: false, pass: false, reason: "Settings could not be activated from the exact target window", captureMethod: "none", appWasFrontmost: false, windowWasFocused: false, foreignOverlayCount: 0, requestedRegion: nil, backingScaleFactor: nil, outputPixelWidth: nil, outputPixelHeight: nil, pixelDimensionsMatch: nil), code: 3)
}
usleep(1_000_000)

let nodes = descendants(window)
let roles = Array(Set(nodes.compactMap { text($0, kAXRoleAttribute) }.filter { $0 == "AXWebArea" || $0 == "AXWebView" })).sorted()
let visibleText = Array(Set(nodes.flatMap { element -> [String] in
  [text(element, kAXTitleAttribute), text(element, kAXValueAttribute), text(element, kAXDescriptionAttribute)].compactMap { $0 }.filter { !$0.isEmpty }
})).sorted()
let joined = visibleText.joined(separator: "\n")
let positive = required.allSatisfy { joined.contains($0) }
let forbiddenPresent = forbidden.contains { joined.contains($0) }

let options = CGWindowListOption.optionOnScreenOnly
let cgInfos = (CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]]) ?? []
let cgCandidates = cgInfos.compactMap { info -> CGCandidate? in
  guard let owner = info[kCGWindowOwnerPID as String] as? Int, owner == Int(pid),
        let number = info[kCGWindowNumber as String] as? NSNumber,
        let name = info[kCGWindowName as String] as? String,
        let bounds = info[kCGWindowBounds as String] as? [String: Any],
        let rect = CGRect(dictionaryRepresentation: bounds as CFDictionary) else { return nil }
  return CGCandidate(windowID: number.uint32Value, name: name, frame: Frame(x: Double(rect.origin.x), y: Double(rect.origin.y), width: Double(rect.size.width), height: Double(rect.size.height)))
}
let cgMatches = cgInfos.filter { info in
  guard let owner = info[kCGWindowOwnerPID as String] as? Int, owner == Int(pid),
        let name = info[kCGWindowName as String] as? String, name == title,
        let bounds = info[kCGWindowBounds as String] as? [String: Any],
        let rect = CGRect(dictionaryRepresentation: bounds as CFDictionary) else { return false }
  return sameBounds(axFrame, rect)
}
let focused = (value(window, kAXFocusedAttribute) as? Bool) ?? false
let frontmost = NSWorkspace.shared.frontmostApplication?.processIdentifier == pid_t(pid) && (runningApplication?.isActive ?? false)
let targetCGFrame = CGRect(x: axFrame.x, y: (NSScreen.main?.frame.height ?? 0) - axFrame.y - axFrame.height, width: axFrame.width, height: axFrame.height)
let foreignOverlayCount = cgInfos.filter { info in
  guard let owner = info[kCGWindowOwnerPID as String] as? Int, owner != Int(pid),
        let layer = info[kCGWindowLayer as String] as? Int, layer > 0,
        let bounds = info[kCGWindowBounds as String] as? [String: Any],
        let rect = CGRect(dictionaryRepresentation: bounds as CFDictionary) else { return false }
  return overlaps(targetCGFrame, rect)
}.count
let screen = NSScreen.screens.first { $0.frame.intersects(targetCGFrame) } ?? NSScreen.main
let scale = screen?.backingScaleFactor ?? 1.0
let expectedWidth = Int((axFrame.width * Double(scale)).rounded())
let expectedHeight = Int((axFrame.height * Double(scale)).rounded())
let screenshot = Process()
screenshot.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
let captureMethod: String
let captureScope: String
let cgWindowID: UInt32?
if cgMatches.count == 1, let selected = cgMatches.first, let number = selected[kCGWindowNumber as String] as? NSNumber {
  screenshot.arguments = ["-x", "-l", number.stringValue, screenshotPath]
  captureMethod = "pid-title-bounds-cgwindow-id"
  captureScope = "direct_pid_exact_title_axwindow_webview_and_pid_title_bounds_cgwindow_only"
  cgWindowID = number.uint32Value
} else {
  guard frontmost && focused && foreignOverlayCount == 0 else {
    emit(Capture(pid: pid, expectedTitle: title, windowCount: windows.count, matchingWindowCount: matching.count, frame: axFrame, positionNormalization: "AX top-left frame; CoreGraphics comparison uses screen-height flip", webRoles: roles, settingsPress: settingsPress, cgCandidates: cgCandidates, matchingCGWindowCount: cgMatches.count, cgWindowID: nil, captureScope: "fail_closed_ax_bounded_region_preconditions", screenshotExit: nil, visibleText: visibleText, positiveTextPresent: positive, forbiddenTextPresent: forbiddenPresent, pass: false, reason: "no unique CoreGraphics target and AX-bounded-region preconditions were not all proven", captureMethod: "none", appWasFrontmost: frontmost, windowWasFocused: focused, foreignOverlayCount: foreignOverlayCount, requestedRegion: axFrame, backingScaleFactor: Double(scale), outputPixelWidth: nil, outputPixelHeight: nil, pixelDimensionsMatch: nil), code: 4)
  }
  screenshot.arguments = ["-x", "-R", "\(Int(axFrame.x.rounded())) ,\(Int(axFrame.y.rounded())) ,\(Int(axFrame.width.rounded())) ,\(Int(axFrame.height.rounded()))".replacingOccurrences(of: " ", with: ""), screenshotPath]
  captureMethod = "ax-bounded-region"
  captureScope = "direct_pid_exact_title_axwindow_webview_frontmost_focused_ax_bounded_region_only"
  cgWindowID = nil
}
var status: Int32? = nil
do {
  try screenshot.run()
  screenshot.waitUntilExit()
  status = screenshot.terminationStatus
} catch {
  status = -1
}
let pixels = imagePixels(screenshotPath)
let pixelMatch = pixels.map { $0.0 == expectedWidth && $0.1 == expectedHeight }
let passed = !roles.isEmpty && positive && !forbiddenPresent && status == 0 && pixelMatch == true
emit(Capture(pid: pid, expectedTitle: title, windowCount: windows.count, matchingWindowCount: matching.count, frame: axFrame, positionNormalization: "AX top-left frame; CoreGraphics comparison uses screen-height flip", webRoles: roles, settingsPress: settingsPress, cgCandidates: cgCandidates, matchingCGWindowCount: cgMatches.count, cgWindowID: cgWindowID, captureScope: captureScope, screenshotExit: status, visibleText: visibleText, positiveTextPresent: positive, forbiddenTextPresent: forbiddenPresent, pass: passed, reason: passed ? "target-window capture and Settings text verified" : "target-window capture or required Settings text verification failed", captureMethod: captureMethod, appWasFrontmost: frontmost, windowWasFocused: focused, foreignOverlayCount: foreignOverlayCount, requestedRegion: axFrame, backingScaleFactor: Double(scale), outputPixelWidth: pixels?.0, outputPixelHeight: pixels?.1, pixelDimensionsMatch: pixelMatch), code: passed ? 0 : 5)
