import Foundation
import Vision
import AppKit
import CoreGraphics

func ocr(_ img: CGImage) -> String {
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.recognitionLanguages = ["el-GR", "la", "en-US"]
    let handler = VNImageRequestHandler(cgImage: img, options: [:])
    try! handler.perform([req])
    return (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
}

let page = CommandLine.arguments[1]
let y0 = Double(CommandLine.arguments[2])!
let y1 = Double(CommandLine.arguments[3])!
let url = URL(fileURLWithPath: "p-\(page).png")
let img = NSImage(contentsOf: url)!
let tiff = img.tiffRepresentation!
let rep = NSBitmapImageRep(data: tiff)!
let cg = rep.cgImage!
let w = cg.width, h = cg.height
let rect = CGRect(x: Int(Double(w)*0.06), y: Int(Double(h)*y0), width: Int(Double(w)*0.88), height: Int(Double(h)*(y1-y0)))
let cropped = cg.cropping(to: rect)!
print(ocr(cropped))
