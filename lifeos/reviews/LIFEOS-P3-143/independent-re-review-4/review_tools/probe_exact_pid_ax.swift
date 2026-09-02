import ApplicationServices
import Foundation

struct Probe: Codable {
    let schema: String
    let directPid: Int32
    let exactTitle: String
    let axTrusted: Bool
    let titleMatched: Bool
    let queriedChildAttributes: [String: String]
    let roles: [String]
    let webRoles: [String]
    let result: String
    let boundaryNote: String
}

func raw(_ element: AXUIElement, _ attribute: String) -> CFTypeRef? { var value: CFTypeRef?; return AXUIElementCopyAttributeValue(element, attribute as CFString, &value) == .success ? value : nil }
func text(_ element: AXUIElement, _ attribute: String) -> String? { raw(element, attribute) as? String }
func elements(_ value: CFTypeRef?) -> [AXUIElement] {
    guard let value, CFGetTypeID(value) == CFArrayGetTypeID() else { return [] }
    let array = unsafeBitCast(value, to: CFArray.self)
    return (0..<CFArrayGetCount(array)).map { unsafeBitCast(CFArrayGetValueAtIndex(array, $0), to: AXUIElement.self) }
}
func descendants(_ element: AXUIElement, _ depth: Int, _ seen: inout Set<String>, _ roles: inout [String]) {
    guard depth < 8 else { return }
    for attribute in [kAXChildrenAttribute as String, "AXVisibleChildren", "AXContents"] {
        for child in elements(raw(element, attribute)) {
            if let role = text(child, kAXRoleAttribute as String) { roles.append(role) }
            let key = "\(ObjectIdentifier(child as AnyObject))"
            if seen.insert(key).inserted { descendants(child, depth + 1, &seen, &roles) }
        }
    }
}
func write(_ value: Probe, _ path: String) { let encoder = JSONEncoder(); encoder.outputFormatting = [.prettyPrinted, .sortedKeys]; try! encoder.encode(value).write(to: URL(fileURLWithPath: path), options: .atomic) }

guard CommandLine.arguments.count == 4, let pid = Int32(CommandLine.arguments[1]) else { exit(64) }
let exactTitle = CommandLine.arguments[2]; let output = CommandLine.arguments[3]
let application = AXUIElementCreateApplication(pid)
guard let window = elements(raw(application, kAXWindowsAttribute as String)).first(where: { text($0, kAXTitleAttribute as String) == exactTitle }) else {
    write(Probe(schema: "lifeos.p3-143.independent-rereview4.ax-role-probe.v1", directPid: pid, exactTitle: exactTitle, axTrusted: AXIsProcessTrusted(), titleMatched: false, queriedChildAttributes: [:], roles: [], webRoles: [], result: "PAUSED_RESUMABLE", boundaryNote: "Only direct PID, contract title, AX roles and AX child-attribute availability are queried; no page text, credential, Provider, network, or personal data is read."), output); exit(2)
}
var attributes: [String: String] = [:]
for attribute in [kAXChildrenAttribute as String, "AXVisibleChildren", "AXContents"] { attributes[attribute] = raw(window, attribute).map { "available_count=\(elements($0).count)" } ?? "unavailable" }
var seen = Set<String>(); var roles: [String] = []; descendants(window, 0, &seen, &roles)
let web = Array(Set(roles.filter { $0 == "AXWebArea" || $0 == "AXWebView" })).sorted()
write(Probe(schema: "lifeos.p3-143.independent-rereview4.ax-role-probe.v1", directPid: pid, exactTitle: exactTitle, axTrusted: AXIsProcessTrusted(), titleMatched: true, queriedChildAttributes: attributes, roles: Array(Set(roles)).sorted(), webRoles: web, result: web.isEmpty ? "PAUSED_RESUMABLE" : "PASS", boundaryNote: "Only direct PID, contract title, AX roles and AX child-attribute availability are queried; no page text, credential, Provider, network, or personal data is read."), output)
exit(web.isEmpty ? 3 : 0)
