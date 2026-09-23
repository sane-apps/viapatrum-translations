import Foundation
import AppKit
let src = CommandLine.arguments[1]
let dest = CommandLine.arguments[2]
let frac = Double(CommandLine.arguments[3])!
guard let img = NSImage(contentsOfFile: src), let tiff = img.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff), let cg = rep.cgImage else { exit(1) }
let w = cg.width, h = cg.height
let y0 = Int(Double(h) * frac)
let rect = CGRect(x: 0, y: 0, width: w, height: h - y0) // bottom in CG coords is y=0
// Actually CGImage y=0 is bottom. For top-left bitmap, crop bottom of page = lower part of image = higher y in CG?
// NSBitmap: use cropping from top
let topSkip = Int(Double(h) * frac)
let cropped = cg.cropping(to: CGRect(x: 0, y: topSkip, width: w, height: h - topSkip))!
let out = NSBitmapImageRep(cgImage: cropped)
let png = out.representation(using: .png, properties: [:])!
try! png.write(to: URL(fileURLWithPath: dest))
print("wrote", dest, cropped.width, cropped.height)
