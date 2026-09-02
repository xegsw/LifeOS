import ApplicationServices
import Foundation

struct RoleProbe: Codable {
    let directPid: Int32
    let exactTitle: String
    let axTrusted: Bool
    let exactTitleWindowFound: Bool
    let windowAttributeNames: [String]
    let childAttributeResults: [String: String]
    let discoveredRoles: [String]
    let webRoles: [String]
    let boundaryNote: String
}

func rawValue(_ element: AXUIElement, _ attribute: String) -> (AXError, CFTypeRef?) {
    var result: CFTypeRef?
    let error = AXUIElementCopyAttributeValue(element, attribute as CFString, &result)
    return (error, result)
}

func cfArrayElements(_ raw: CFTypeRef?) -> [AXUIElement] {
    guard let raw, CFGetTypeID(raw) == CFArrayGetTypeID() else { return [] }
    let array = unsafeBitCast(raw, to: CFArray.self)
    return (0..<CFArrayGetCount(array)).map { index in
        unsafeBitCast(CFArrayGetValueAtIndex(array, index), to: AXUIElement.self)
    }
}

func role(_ element: AXUIElement) -> String? {
    let (_, raw) = rawValue(element, kAXRoleAttribute as String)
    return raw as? String
}

func collectRoles(_ element: AXUIElement, _ depth: Int, _ output: inout [String]) {
    guard depth <= 8, output.count < 128 else { return }
    let (_, raw) = rawValue(element, kAXChildrenAttribute as String)
    for child in cfArrayElements(raw) {
        if let childRole = role(child) { output.append(childRole) }
        collectRoles(child, depth + 1, &output)
    }
}

guard CommandLine.arguments.count == 4, let pid = Int32(CommandLine.arguments[1]) else {
    fputs("usage: probe_exact_pid_ax.swift <pid> <exact-title> <output.json>\\n", stderr)
    exit(64)
}
let exactTitle = CommandLine.arguments[2]
let outputPath = CommandLine.arguments[3]
let app = AXUIElementCreateApplication(pid)
let (_, windowsRaw) = rawValue(app, kAXWindowsAttribute as String)
let window = cfArrayElements(windowsRaw).first { candidate in
    let (_, titleRaw) = rawValue(candidate, kAXTitleAttribute as String)
    return (titleRaw as? String) == exactTitle
}

guard let window else {
    let result = RoleProbe(directPid: pid, exactTitle: exactTitle, axTrusted: AXIsProcessTrusted(), exactTitleWindowFound: false, windowAttributeNames: [], childAttributeResults: [:], discoveredRoles: [], webRoles: [], boundaryNote: "Only the direct PID and contract title were queried through AX; no UI content, credentials, provider, network or personal data was read.")
    let data = try! JSONEncoder().encode(result)
    try! data.write(to: URL(fileURLWithPath: outputPath), options: .atomic)
    exit(2)
}
var names: CFArray?
_ = AXUIElementCopyAttributeNames(window, &names)
let attributeNames = (names as? [String] ?? []).sorted()
var childResults: [String: String] = [:]
for attribute in [kAXChildrenAttribute as String, "AXVisibleChildren", "AXContents"] {
    let (error, raw) = rawValue(window, attribute)
    if error == .success {
        childResults[attribute] = "success:array-count=" + String(cfArrayElements(raw).count)
    } else {
        childResults[attribute] = "error=" + String(error.rawValue)
    }
}
var discovered: [String] = []
collectRoles(window, 0, &discovered)
let result = RoleProbe(directPid: pid, exactTitle: exactTitle, axTrusted: AXIsProcessTrusted(), exactTitleWindowFound: true, windowAttributeNames: attributeNames, childAttributeResults: childResults, discoveredRoles: discovered, webRoles: Array(Set(discovered.filter { $0 == "AXWebArea" || $0 == "AXWebView" })).sorted(), boundaryNote: "Only the direct PID and contract title were queried through AX; no UI content, credentials, provider, network or personal data was read.")
let encoder = JSONEncoder()
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
try! encoder.encode(result).write(to: URL(fileURLWithPath: outputPath), options: .atomic)
exit(result.webRoles.isEmpty ? 3 : 0)
