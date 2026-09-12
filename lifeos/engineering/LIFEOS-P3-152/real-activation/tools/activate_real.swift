import Cocoa
let args=CommandLine.arguments
guard args.count==2,let pid=Int32(args[1]),let app=NSRunningApplication(processIdentifier:pid),app.executableURL?.path=="/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Unified Real.app/Contents/MacOS/lifeos-p3-152" else{exit(2)}
print(app.activate(options:[]) ? "activation_requested" : "activation_not_confirmed")
