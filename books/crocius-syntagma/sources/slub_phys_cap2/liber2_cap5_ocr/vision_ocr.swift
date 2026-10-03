import Foundation
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1 else { fputs("usage: vision_ocr <png>...\n", stderr); exit(1) }
for path in args.dropFirst() {
    let url = URL(fileURLWithPath: path)
    guard let img = NSImage(contentsOf: url),
          let tiff = img.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let cg = rep.cgImage else {
        fputs("fail \(path)\n", stderr); continue
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    req.recognitionLanguages = ["la", "en", "el"]
    let handler = VNImageRequestHandler(cgImage: cg, options: [:])
    try! handler.perform([req])
    let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    let out = URL(fileURLWithPath: path).deletingPathExtension().lastPathComponent
    let dest = URL(fileURLWithPath: "vision_\(out.replacingOccurrences(of: "p-", with: "")).txt")
    try! (lines.joined(separator: "\n") + "\n").write(to: dest, atomically: true, encoding: .utf8)
    print("wrote \(dest.path) lines=\(lines.count)")
}
