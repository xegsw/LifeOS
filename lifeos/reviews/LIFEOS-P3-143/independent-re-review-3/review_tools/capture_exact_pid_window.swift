import ApplicationServices
import CoreGraphics
import Foundation

struct TargetCapture: Codable {
    let directPid: Int32
    let exactTitle: String
    let axWindowRole: String?
    let axFrame: [String: CGFloat]?
    let cgWindowId: UInt32?
    let cgFrame: [String: CGFloat]?
    let screenshotPath: String?
    let result: String
    let failure: String?
    let boundaryNote: String
}

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var result: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success else { return nil }
    return result
}

func elements(_ raw: CFTypeRef?) -> [AXUIElement] {
    guard let raw, CFGetTypeID(raw) == CFArrayGetTypeID() else { return [] }
    let array = unsafeBitCast(raw, to: CFArray.self)
    return (0..<CFArrayGetCount(array)).map { unsafeBitCast(CFArrayGetValueAtIndex(array, $0), to: AXUIElement.self) }
}

func text(_ element: AXUIElement, _ attribute: String) -> String? { value(element, attribute) as? String }

func axFrame(_ window: AXUIElement) -> [String: CGFloat]? {
    guard let positionRaw = value(window, kAXPositionAttribute as String), let sizeRaw = value(window, kAXSizeAttribute as String) else { return nil }
    let position = unsafeBitCast(positionRaw, to: AXValue.self)
    let size = unsafeBitCast(sizeRaw, to: AXValue.self)
    var point = CGPoint.zero
    var dimensions = CGSize.zero
    guard AXValueGetValue(position, .cgPoint, &point), AXValueGetValue(size, .cgSize, &dimensions) else { return nil }
    return ["x": point.x, "y": point.y, "width": dimensions.width, "height": dimensions.height]
}

func cgFrame(_ info: [String: Any]) -> [String: CGFloat]? {
    guard let bounds = info[kCGWindowBounds as String] as? [String: NSNumber] else { return nil }
    guard let x = bounds["X"]?.doubleValue, let y = bounds["Y"]?.doubleValue, let width = bounds["Width"]?.doubleValue, let height = bounds["Height"]?.doubleValue else { return nil }
    return ["x": x, "y": y, "width": width, "height": height]
}

func write(_ record: TargetCapture, _ path: String) {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    try! encoder.encode(record).write(to: URL(fileURLWithPath: path), options: .atomic)
}

guard CommandLine.arguments.count == 5, let pid = Int32(CommandLine.arguments[1]) else {
    fputs("usage: capture_exact_pid_window.swift <pid> <title> <screenshot.png> <output.json>\\n", stderr)
    exit(64)
}
let exactTitle = CommandLine.arguments[2]
let screenshotPath = CommandLine.arguments[3]
let outputPath = CommandLine.arguments[4]
let app = AXUIElementCreateApplication(pid)
let window = elements(value(app, kAXWindowsAttribute as String)).first { text($0, kAXTitleAttribute as String) == exactTitle }
guard let window else {
    write(TargetCapture(directPid: pid, exactTitle: exactTitle, axWindowRole: nil, axFrame: nil, cgWindowId: nil, cgFrame: nil, screenshotPath: nil, result: "PAUSED_RESUMABLE", failure: "exact-title AXWindow unavailable", boundaryNote: "Only the direct PID, contract title, roles and geometry were queried; screenshot selection is restricted to the matching PID window id."), outputPath)
    exit(2)
}
let matching = ((CGWindowListCopyWindowInfo(.optionAll, kCGNullWindowID) as? [[String: Any]]) ?? []).first { info in
    let owner = (info[kCGWindowOwnerPID as String] as? NSNumber)?.int32Value
    let name = info[kCGWindowName as String] as? String
    let layer = (info[kCGWindowLayer as String] as? NSNumber)?.intValue
    return owner == pid && name == exactTitle && layer == 0
}
guard let matching, let number = (matching[kCGWindowNumber as String] as? NSNumber)?.uint32Value else {
    write(TargetCapture(directPid: pid, exactTitle: exactTitle, axWindowRole: text(window, kAXRoleAttribute as String), axFrame: axFrame(window), cgWindowId: nil, cgFrame: nil, screenshotPath: nil, result: "PAUSED_RESUMABLE", failure: "exact-PID titled CGWindow unavailable", boundaryNote: "Only the direct PID, contract title, roles and geometry were queried; screenshot selection is restricted to the matching PID window id."), outputPath)
    exit(3)
}
let screenshot = Process()
screenshot.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
screenshot.arguments = ["-x", "-l" + String(number), screenshotPath]
do {
    try screenshot.run()
    screenshot.waitUntilExit()
} catch {
    write(TargetCapture(directPid: pid, exactTitle: exactTitle, axWindowRole: text(window, kAXRoleAttribute as String), axFrame: axFrame(window), cgWindowId: number, cgFrame: cgFrame(matching), screenshotPath: nil, result: "PAUSED_RESUMABLE", failure: "target-only screenshot launch failed", boundaryNote: "Only the direct PID, contract title, roles and geometry were queried; screenshot selection is restricted to the matching PID window id."), outputPath)
    exit(4)
}
let exists = FileManager.default.fileExists(atPath: screenshotPath)
let pass = screenshot.terminationStatus == 0 && exists
write(TargetCapture(directPid: pid, exactTitle: exactTitle, axWindowRole: text(window, kAXRoleAttribute as String), axFrame: axFrame(window), cgWindowId: number, cgFrame: cgFrame(matching), screenshotPath: pass ? screenshotPath : nil, result: pass ? "PASS" : "PAUSED_RESUMABLE", failure: pass ? nil : "target-only screenshot write failed", boundaryNote: "Only the direct PID, contract title, roles and geometry were queried; screenshot selection is restricted to the matching PID window id."), outputPath)
exit(pass ? 0 : 5)
