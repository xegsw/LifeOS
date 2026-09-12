import Cocoa
import WebKit
let args=CommandLine.arguments
guard args.count==5, let width=Double(args[2]),let height=Double(args[3]),[700.0,1280.0].contains(width),[728.0,917.0].contains(height),["116","142"].contains(args[1]) else{exit(2)}
let base="/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-148/evidence/visual-reference/"
let input=URL(fileURLWithPath:base+args[1]+"/index.html")
let output=URL(fileURLWithPath:base+args[1]+"-"+args[2]+"-"+args[4]+".png")
guard ["today","ai","ai2","settings"].contains(args[4]),!FileManager.default.fileExists(atPath:output.path) else{exit(3)}
let app=NSApplication.shared;app.setActivationPolicy(.accessory)
let config=WKWebViewConfiguration();config.websiteDataStore = .nonPersistent()
let view=WKWebView(frame:NSRect(x:0,y:0,width:width,height:height),configuration:config)
let window=NSWindow(contentRect:view.frame,styleMask:[.borderless],backing:.buffered,defer:false);window.contentView=view;window.orderFront(nil)
class Delegate:NSObject,WKNavigationDelegate{
 func webView(_ w:WKWebView,decidePolicyFor action:WKNavigationAction,decisionHandler:@escaping(WKNavigationActionPolicy)->Void){decisionHandler(action.request.url?.isFileURL==true ? .allow:.cancel)}
 func webView(_ w:WKWebView,didFinish navigation:WKNavigation!){
  let action=CommandLine.arguments[4].hasPrefix("ai") ? "document.querySelector('[data-action=\"ai\"]')?.click()" : "void 0"
  w.evaluateJavaScript(action){_,_ in DispatchQueue.main.asyncAfter(deadline:.now()+0.5){
   w.takeSnapshot(with:nil){im,err in guard let im=im,let tiff=im.tiffRepresentation,let rep=NSBitmapImageRep(data:tiff),let data=rep.representation(using:.png,properties:[:]) else{exit(4)}
    do{try data.write(to:output);print("reference_only \(output.path) content=\(w.bounds.width)x\(w.bounds.height) pixels=\(rep.pixelsWide)x\(rep.pixelsHigh)");exit(0)}catch{exit(5)}
   }
  }}
 }
}
let delegate=Delegate();view.navigationDelegate=delegate
view.loadFileURL(input,allowingReadAccessTo:input.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline:.now()+15){exit(6)}
app.run()
