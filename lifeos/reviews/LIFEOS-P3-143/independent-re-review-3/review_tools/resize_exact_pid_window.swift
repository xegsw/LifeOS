import ApplicationServices
import Foundation

struct ResizeRecord: Codable {
    let directPid: Int32
    let exactTitle: String
    let requestedWidth: CGFloat
    let requestedHeight: CGFloat
    let observedWidth: CGFloat?
    let observedHeight: CGFloat?
    let result: String
    let failure: String?
    let boundaryNote: String
}

func value(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? {
    var result: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute as CFString, &result) == .success else { return nil }
    return result
}

func title(_ element: AXUIElement) -> String? { value(element, kAXTitleAttribute as String) as? String }

func elements(_ raw: CFTypeRef?) -> [AXUIElement] {
    guard let raw, CFGetTypeID(raw) == CFArrayGetTypeID() else { return [] }
    let array = unsafeBitCast(raw, to: CFArray.self)
    return (0..<CFArrayGetCount(array)).map { unsafeBitCast(CFArrayGetValueAtIndex(array, $0), to: AXUIElement.self) }
}

func observedSize(_ window: AXUIElement) -> CGSize? {
    guard let raw = value(window, kAXSizeAttribute as String) else { return nil }
    let axValue = unsafeBitCast(raw, to: AXValue.self)
    var output = CGSize.zero
    return AXValueGetValue(axValue, .cgSize, &output) ? output : nil
}

guard CommandLine.arguments.count == 6, let pid = Int32(CommandLine.arguments[1]), let width = Double(CommandLine.arguments[3]), let height = Double(CommandLine.arguments[4]) else {
    fputs("usage: resize_exact_pid_window.swift <pid> <title> <width> <height> <output.json>\\n", stderr)
    exit(64)
}
let exactTitle = CommandLine.arguments[2]
let outputPath = CommandLine.arguments[5]
let app = AXUIElementCreateApplication(pid)
let window = elements(value(app, kAXWindowsAttribute as String)).first { title($0) == exactTitle }
guard let window else {
    let record = ResizeRecord(directPid: pid, exactTitle: exactTitle, requestedWidth: width, requestedHeight: height, observedWidth: nil, observedHeight: nil, result: "PAUSED_RESUMABLE", failure: "exact-title AXWindow unavailable", boundaryNote: "Only the exact-PID window geometry was changed; no UI content, credential, provider, network or personal data was read or written.")
    try! JSONEncoder().encode(record).write(to: URL(fileURLWithPath: outputPath), options: .atomic)
    exit(2)
}
var requested = CGSize(width: width, height: height)
guard let requestedValue = AXValueCreate(.cgSize, &requested) else { exit(3) }
let setResult = AXUIElementSetAttributeValue(window, kAXSizeAttribute as CFString, requestedValue)
Thread.sleep(forTimeInterval: 0.8)
let actual = observedSize(window)
let pass = setResult == .success && actual.map { abs($0.width - width) < 0.5 && abs($0.height - height) < 0.5 } == true
let record = ResizeRecord(directPid: pid, exactTitle: exactTitle, requestedWidth: width, requestedHeight: height, observedWidth: actual?.width, observedHeight: actual?.height, result: pass ? "PASS" : "PAUSED_RESUMABLE", failure: pass ? nil : "AX geometry change unavailable or not exact", boundaryNote: "Only the exact-PID window geometry was changed; no UI content, credential, provider, network or personal data was read or written.")
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
try! encoder.encode(record).write(to: URL(fileURLWithPath: outputPath), options: .atomic)
exit(pass ? 0 : 4)
