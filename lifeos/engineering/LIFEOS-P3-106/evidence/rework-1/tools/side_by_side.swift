import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers
guard CommandLine.arguments.count==4 else { fatalError("usage: side_by_side.swift REF ACTUAL OUT") }
func load(_ path:String)->CGImage { let u=URL(fileURLWithPath:path) as CFURL; guard let s=CGImageSourceCreateWithURL(u,nil),let i=CGImageSourceCreateImageAtIndex(s,0,nil),i.width==1280,i.height==1024 else { fatalError("invalid source") }; return i }
let ref=load(CommandLine.arguments[1]),actual=load(CommandLine.arguments[2]),space=CGColorSpaceCreateDeviceRGB()
guard let ctx=CGContext(data:nil,width:2560,height:1024,bitsPerComponent:8,bytesPerRow:0,space:space,bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue) else { fatalError("context") }
ctx.draw(ref,in:CGRect(x:0,y:0,width:1280,height:1024)); ctx.draw(actual,in:CGRect(x:1280,y:0,width:1280,height:1024)); guard let img=ctx.makeImage() else { fatalError("image") }
let out=URL(fileURLWithPath:CommandLine.arguments[3]) as CFURL; guard let dest=CGImageDestinationCreateWithURL(out,UTType.png.identifier as CFString,1,nil) else { fatalError("dest") }; CGImageDestinationAddImage(dest,img,nil); guard CGImageDestinationFinalize(dest) else { fatalError("finalize") }; print("reference_left actual_right width=2560 height=1024")
