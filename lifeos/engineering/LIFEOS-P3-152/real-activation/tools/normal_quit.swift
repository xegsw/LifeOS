import Cocoa
let args=CommandLine.arguments
guard args.count==3,let pid=Int32(args[1]),args[2]=="/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Controlled.app/Contents/MacOS/lifeos-p3-152",let app=NSRunningApplication(processIdentifier:pid),app.executableURL?.path==args[2] else {print("identity_rejected");exit(2)}
let accepted=app.terminate()
print(accepted ? "normal_quit_requested" : "normal_quit_refused")
