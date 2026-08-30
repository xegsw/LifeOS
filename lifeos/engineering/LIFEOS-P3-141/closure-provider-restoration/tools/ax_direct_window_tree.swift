import ApplicationServices
import Foundation

private func stringAttribute(_ element: AXUIElement, _ attribute: CFString) -> String {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, attribute, &value) == .success else { return "" }
    return value as? String ?? ""
}

private func children(_ element: AXUIElement) -> [AXUIElement] {
    var value: CFTypeRef?
    guard AXUIElementCopyAttributeValue(element, kAXChildrenAttribute as CFString, &value) == .success else { return [] }
    return value as? [AXUIElement] ?? []
}

guard CommandLine.arguments.count == 3,
      let rawPid = Int32(CommandLine.arguments[1]), rawPid > 0 else {
    FileHandle.standardError.write(Data("usage: ax_direct_window_tree <direct-pid> <exact-title>\n".utf8))
    exit(64)
}
let expectedTitle = CommandLine.arguments[2]
let app = AXUIElementCreateApplication(rawPid)
var windowsValue: CFTypeRef?
guard AXUIElementCopyAttributeValue(app, kAXWindowsAttribute as CFString, &windowsValue) == .success,
      let windows = windowsValue as? [AXUIElement] else {
    exit(65)
}
let matching = windows.filter { stringAttribute($0, kAXTitleAttribute as CFString) == expectedTitle }
guard matching.count == 1 else { exit(66) }

var rows: [[String: String]] = []
var queue: [(AXUIElement, Int)] = [(matching[0], 0)]
var seen = Set<UInt>()
while !queue.isEmpty && rows.count < 400 {
    let (element, depth) = queue.removeFirst()
    let ptr = UInt(bitPattern: Unmanaged.passUnretained(element).toOpaque())
    if !seen.insert(ptr).inserted { continue }
    let row = [
        "depth": String(depth),
        "role": stringAttribute(element, kAXRoleAttribute as CFString),
        "title": stringAttribute(element, kAXTitleAttribute as CFString),
        "description": stringAttribute(element, kAXDescriptionAttribute as CFString),
        "value": stringAttribute(element, kAXValueAttribute as CFString)
    ]
    rows.append(row)
    for child in children(element) { queue.append((child, depth + 1)) }
}
let result: [String: Any] = ["direct_pid": Int(rawPid), "exact_title": expectedTitle, "rows": rows]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
FileHandle.standardOutput.write(data)
FileHandle.standardOutput.write(Data("\n".utf8))
