import Cocoa
let old="/private/tmp/lifeos-p3-155-source-update-v1/LifeOS P3-155 Source Update.app/Contents/MacOS/lifeos-p3-152"
let new="/private/tmp/lifeos-p3-157-real-actions-v1/LifeOS P3-157 Real Actions.app/Contents/MacOS/lifeos-p3-152"
func emit(_ v:[String:Any]) {let d=try! JSONSerialization.data(withJSONObject:v,options:[.sortedKeys]);print(String(data:d,encoding:.utf8)!)}
let args=CommandLine.arguments
if args.count==2 && args[1]=="inspect" {
 let found=NSWorkspace.shared.runningApplications.filter{[old,new].contains($0.executableURL?.path ?? "")}.map{["pid":$0.processIdentifier,"executable":$0.executableURL!.path,"bundleId":$0.bundleIdentifier ?? "","terminated":$0.isTerminated] as [String:Any]}
 emit(["instances":found]);exit(0)
}
guard args.count==3,let pid=Int32(args[2]),let app=NSRunningApplication(processIdentifier:pid) else {emit(["status":"identity_rejected"]);exit(2)}
if args[1]=="quit" {
 guard app.executableURL?.path==old, app.bundleIdentifier=="local.lifeos.p3-155.source-update", !app.isTerminated else {emit(["status":"identity_rejected"]);exit(2)}
 let accepted=app.terminate();let end=Date().addingTimeInterval(15)
 while accepted && !app.isTerminated && Date()<end {RunLoop.current.run(until:Date().addingTimeInterval(0.1))}
 emit(["pid":pid,"executable":old,"normal_quit_requested":accepted,"exited":app.isTerminated]);exit(app.isTerminated ? 0:3)
}
if args[1]=="activate" {
 guard app.executableURL?.path==new, app.bundleIdentifier=="local.lifeos.p3-157.real-actions", !app.isTerminated else {emit(["status":"identity_rejected"]);exit(2)}
 emit(["pid":pid,"executable":new,"activation_requested":app.activate(options:[]),"running": !app.isTerminated]);exit(0)
}
exit(2)
