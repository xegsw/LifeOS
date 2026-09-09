import Cocoa
import ApplicationServices
import CryptoKit
let args=CommandLine.arguments
let pid=pid_t(args[1])!
let receiptPath="/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/health-view-restoration/evidence/synthetic-launch.json"
guard let raw=FileManager.default.contents(atPath:receiptPath),let receipt=(try? JSONSerialization.jsonObject(with:raw)) as? [String:Any],receipt["mode"] as? String == "synthetic",(receipt["pid"] as? Int)==Int(pid),let binary=receipt["binary"] as? String,binary == "/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Health View Preview.app/Contents/MacOS/lifeos-p3-152" else {print("synthetic_pid_rejected");exit(3)}
let process=Process();process.executableURL=URL(fileURLWithPath:"/bin/ps");process.arguments=["-p",String(pid),"-o","comm="];let pipe=Pipe();process.standardOutput=pipe;try process.run();process.waitUntilExit();let actual=String(data:pipe.fileHandleForReading.readDataToEndOfFile(),encoding:.utf8)?.trimmingCharacters(in:.whitespacesAndNewlines)
guard actual==binary,let executable=FileManager.default.contents(atPath:binary),SHA256.hash(data:executable).map({String(format:"%02x",$0)}).joined()==receipt["binary_sha256"] as? String else {print("synthetic_identity_rejected");exit(3)}
let app=AXUIElementCreateApplication(pid)
func attr(_ node:AXUIElement,_ key:String)->AnyObject? {var value:CFTypeRef?;return AXUIElementCopyAttributeValue(node,key as CFString,&value) == .success ? value : nil}
func point(_ node:AXUIElement)->[String:Double] {var p=CGPoint.zero;var s=CGSize.zero;if let v=attr(node,kAXPositionAttribute) {AXValueGetValue(v as! AXValue,.cgPoint,&p)};if let v=attr(node,kAXSizeAttribute){AXValueGetValue(v as! AXValue,.cgSize,&s)};return ["x":p.x,"y":p.y,"width":s.width,"height":s.height]}
func walk(_ node:AXUIElement,_ depth:Int)->[[String:String]] {if depth>10{return []};var out:[[String:String]]=[];let role=attr(node,kAXRoleAttribute) as? String ?? "";let title=attr(node,kAXTitleAttribute) as? String ?? "";let desc=attr(node,kAXDescriptionAttribute) as? String ?? "";if ["AXWebArea","AXWebView","AXTextArea","AXButton","AXStaticText","AXCheckBox","AXRadioButton","AXPopUpButton","AXTextField"].contains(role){out.append(["role":role,"title":title,"description":desc,"value":String(describing:attr(node,kAXValueAttribute) ?? "" as AnyObject)])};if let children=attr(node,kAXChildrenAttribute) as? [AXUIElement] {for child in children{out += walk(child,depth+1)}};return out}
AXUIElementSetMessagingTimeout(app, 5)
var windowValue:CFTypeRef?
let windowError=AXUIElementCopyAttributeValue(app,kAXWindowsAttribute as CFString,&windowValue)
var windows=windowValue as? [AXUIElement] ?? []
var windowAttribute="AXWindows"
if windows.isEmpty, let candidate=attr(app,kAXMainWindowAttribute), CFGetTypeID(candidate)==AXUIElementGetTypeID() {
 let main=candidate as! AXUIElement
 if attr(main,kAXRoleAttribute) as? String == "AXWindow" {windows=[main];windowAttribute="AXMainWindow"}
}
guard windows.count == 1, attr(windows[0],kAXTitleAttribute) as? String == "LifeOS P3-152 - Synthetic Conversation" else {print("synthetic_target_rejected");exit(3)}
let own=windows.map { ["title":attr($0,kAXTitleAttribute) as? String ?? "","geometry":point($0),"nodes":walk($0,0)] as [String:Any] }
let cg=(CGWindowListCopyWindowInfo([.optionAll],kCGNullWindowID) as? [[String:Any]] ?? []).filter{($0[kCGWindowOwnerPID as String] as? Int)==Int(pid)}.map{["id":$0[kCGWindowNumber as String] ?? 0,"bounds":$0[kCGWindowBounds as String] ?? [:],"layer":$0[kCGWindowLayer as String] ?? -1]}
let result:[String:Any]=["window_attribute":windowAttribute,"ax_error":windowError.rawValue,"trusted":AXIsProcessTrusted(),"pid":pid,"windows":own,"cg":cg,"timestamp":ISO8601DateFormatter().string(from:Date())]
print(String(data:try JSONSerialization.data(withJSONObject:result,options:[.sortedKeys]),encoding:.utf8)!)
