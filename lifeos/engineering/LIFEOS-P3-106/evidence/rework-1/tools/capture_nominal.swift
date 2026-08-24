import CoreGraphics
import Darwin
import Foundation
import ImageIO
import UniformTypeIdentifiers
typealias CaptureFunction = @convention(c) (CGRect, UInt32, UInt32, UInt32) -> Unmanaged<CGImage>?
guard CommandLine.arguments.count == 3, let windowID = UInt32(CommandLine.arguments[1]) else { fatalError("usage: capture_nominal.swift WINDOW_ID OUTPUT.png") }
guard let handle=dlopen("/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics",RTLD_LAZY), let symbol=dlsym(handle,"CGWindowListCreateImage") else { fatalError("capture symbol unavailable") }
let capture=unsafeBitCast(symbol,to:CaptureFunction.self)
let options=CGWindowImageOption.boundsIgnoreFraming.rawValue | CGWindowImageOption.nominalResolution.rawValue
guard let raw=capture(.null,CGWindowListOption.optionIncludingWindow.rawValue,windowID,options) else { fatalError("capture failed") }
let image=raw.takeRetainedValue(); guard image.width==1280 && image.height==1024 else { fatalError("unexpected nominal canvas: \(image.width)x\(image.height)") }
let output=URL(fileURLWithPath:CommandLine.arguments[2]) as CFURL
guard let dest=CGImageDestinationCreateWithURL(output,UTType.png.identifier as CFString,1,nil) else { fatalError("destination failed") }
CGImageDestinationAddImage(dest,image,nil); guard CGImageDestinationFinalize(dest) else { fatalError("finalize failed") }
print("window_id=\(windowID) width=\(image.width) height=\(image.height)")
