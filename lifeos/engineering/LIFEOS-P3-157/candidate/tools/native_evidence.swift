import Cocoa
import ApplicationServices
let args=CommandLine.arguments
let pid=pid_t(args[1])!
let app=AXUIElementCreateApplication(pid)
func attr(_ node:AXUIElement,_ key:String)->AnyObject? {var value:CFTypeRef?;return AXUIElementCopyAttributeValue(node,key as CFString,&value) == .success ? value : nil}
func point(_ node:AXUIElement)->[String:Double] {var p=CGPoint.zero;var s=CGSize.zero;if let v=attr(node,kAXPositionAttribute) {AXValueGetValue(v as! AXValue,.cgPoint,&p)};if let v=attr(node,kAXSizeAttribute){AXValueGetValue(v as! AXValue,.cgSize,&s)};return ["x":p.x,"y":p.y,"width":s.width,"height":s.height]}
func walk(_ node:AXUIElement,_ depth:Int)->[[String:String]] {if depth>10{return []};var out:[[String:String]]=[];let role=attr(node,kAXRoleAttribute) as? String ?? "";let title=attr(node,kAXTitleAttribute) as? String ?? "";let desc=attr(node,kAXDescriptionAttribute) as? String ?? "";if ["AXWebArea","AXWebView","AXTextArea","AXButton","AXStaticText"].contains(role){out.append(["role":role,"title":title,"description":desc])};if let children=attr(node,kAXChildrenAttribute) as? [AXUIElement] {for child in children{out += walk(child,depth+1)}};return out}
AXUIElementSetMessagingTimeout(app, 5)
var windowValue:CFTypeRef?
let windowError=AXUIElementCopyAttributeValue(app,kAXWindowsAttribute as CFString,&windowValue)
var windows=windowValue as? [AXUIElement] ?? []
var windowAttribute="AXWindows"
if windows.isEmpty, let candidate=attr(app,kAXMainWindowAttribute), CFGetTypeID(candidate)==AXUIElementGetTypeID() {
 let main=candidate as! AXUIElement
 if attr(main,kAXRoleAttribute) as? String == "AXWindow" {windows=[main];windowAttribute="AXMainWindow"}
}
let own=windows.map { ["title":attr($0,kAXTitleAttribute) as? String ?? "","geometry":point($0),"nodes":walk($0,0)] as [String:Any] }
let cg=(CGWindowListCopyWindowInfo([.optionAll],kCGNullWindowID) as? [[String:Any]] ?? []).filter{($0[kCGWindowOwnerPID as String] as? Int)==Int(pid)}.map{["id":$0[kCGWindowNumber as String] ?? 0,"bounds":$0[kCGWindowBounds as String] ?? [:],"layer":$0[kCGWindowLayer as String] ?? -1]}
let result:[String:Any]=["window_attribute":windowAttribute,"ax_error":windowError.rawValue,"trusted":AXIsProcessTrusted(),"pid":pid,"windows":own,"cg":cg,"timestamp":ISO8601DateFormatter().string(from:Date())]
print(String(data:try JSONSerialization.data(withJSONObject:result,options:[.sortedKeys]),encoding:.utf8)!)
