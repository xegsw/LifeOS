import Cocoa
import ApplicationServices
let args=CommandLine.arguments
guard args.count>=4, let pid=pid_t(args[1]) else {exit(2)}
let app=AXUIElementCreateApplication(pid)
func attr(_ n:AXUIElement,_ k:String)->AnyObject?{var v:CFTypeRef?;return AXUIElementCopyAttributeValue(n,k as CFString,&v) == .success ? v:nil}
var windows=attr(app,kAXWindowsAttribute) as? [AXUIElement] ?? []
if windows.isEmpty, let main=attr(app,kAXMainWindowAttribute), CFGetTypeID(main)==AXUIElementGetTypeID(){windows=[main as! AXUIElement]}
guard windows.count==1, attr(windows[0],kAXTitleAttribute) as? String == "LifeOS P3-149 - Synthetic Offline" else {print("target_window_rejected");exit(3)}
func nodes(_ n:AXUIElement)->[AXUIElement]{var result=[n];for child in attr(n,kAXChildrenAttribute) as? [AXUIElement] ?? []{result+=nodes(child)};return result}
let all=nodes(windows[0]);let action=args[2];let label=args[3]
NSRunningApplication(processIdentifier:pid)?.activate(options:[.activateIgnoringOtherApps])
if action == "resize" {let parts=label.split(separator:"x").compactMap{Double($0)};guard parts.count==2 else{exit(4)};var size=CGSize(width:parts[0],height:parts[1]);print(AXUIElementSetAttributeValue(windows[0],kAXSizeAttribute as CFString,AXValueCreate(.cgSize,&size)!).rawValue);exit(0)}
if action == "scroll" {let bars=all.filter{attr($0,kAXRoleAttribute) as? String == "AXScrollBar"};guard bars.count == 1, let v=Double(label) else{exit(4)};print(AXUIElementSetAttributeValue(bars[0],kAXValueAttribute as CFString,NSNumber(value:v)).rawValue);exit(0)}
let matches=all.filter{n in let role=attr(n,kAXRoleAttribute) as? String ?? "";if action=="type"{return role=="AXTextArea"};if action=="query"{return role=="AXTextField"};return role=="AXButton" && ((attr(n,kAXTitleAttribute) as? String)==label || (attr(n,kAXDescriptionAttribute) as? String)==label)}
guard matches.count==1 else {print("target_count_\(matches.count)");exit(4)}
if action=="press"{print(AXUIElementPerformAction(matches[0],kAXPressAction as CFString).rawValue)}
else if action=="type" || action=="query"{
 NSRunningApplication(processIdentifier:pid)?.activate(options:[.activateIgnoringOtherApps])
 AXUIElementSetAttributeValue(matches[0],kAXFocusedAttribute as CFString,kCFBooleanTrue)
 let setResult=AXUIElementSetAttributeValue(matches[0],kAXValueAttribute as CFString,label as CFString)
 print("set_value_\(setResult.rawValue)")
 if setResult == .success {exit(0)}
 let text=Array(label.utf16)
 let event=CGEvent(keyboardEventSource:nil,virtualKey:0,keyDown:true)!
 event.keyboardSetUnicodeString(stringLength:text.count,unicodeString:text)
 event.postToPid(pid)
 let up=CGEvent(keyboardEventSource:nil,virtualKey:0,keyDown:false)!
 up.postToPid(pid)
 print("typed_synthetic_text")
}else{exit(5)}
