import AppKit
import Foundation

// Series cover for a Fathers Logos book. Same size, palette, and
// arrangement as the shelf painted in 2026-09: parchment ground,
// chi-rho, author, English title, original-language subtitle.
//
//   swiftc -o /tmp/logos_cover scripts/logos_cover.swift
//   /tmp/logos_cover jobs.json
//
// jobs.json is a list of {out, author, title, subtitle}.

struct Job: Decodable {
    let out: String
    let author: String
    let title: String
    let subtitle: String
}

let ink = NSColor(calibratedRed: 0.23, green: 0.18, blue: 0.14, alpha: 1)
let width = 900
let height = 1200

func chiRho(cx: CGFloat, cy: CGFloat) {
    ink.setStroke()
    let stem = NSBezierPath()
    stem.lineWidth = 3.4
    stem.lineCapStyle = .round
    stem.move(to: NSPoint(x: cx, y: cy - 86))
    stem.line(to: NSPoint(x: cx, y: cy + 86))
    stem.stroke()

    let chi = NSBezierPath()
    chi.lineWidth = 3.4
    chi.lineCapStyle = .round
    let y = cy - 6
    chi.move(to: NSPoint(x: cx - 58, y: y - 40))
    chi.line(to: NSPoint(x: cx + 58, y: y + 40))
    chi.move(to: NSPoint(x: cx - 58, y: y + 40))
    chi.line(to: NSPoint(x: cx + 58, y: y - 40))
    chi.stroke()

    let rho = NSBezierPath()
    rho.lineWidth = 3.4
    rho.lineCapStyle = .round
    rho.move(to: NSPoint(x: cx + 1, y: cy + 84))
    rho.curve(to: NSPoint(x: cx + 1, y: cy + 6),
              controlPoint1: NSPoint(x: cx + 78, y: cy + 86),
              controlPoint2: NSPoint(x: cx + 78, y: cy + 4))
    rho.stroke()
}

func font(_ name: String, _ size: CGFloat) -> NSFont {
    NSFont(name: name, size: size) ?? NSFont.systemFont(ofSize: size)
}

func drawCentered(_ text: String, fontName: String, size: CGFloat,
                  y: CGFloat, kern: CGFloat, maxWidth: CGFloat) -> CGFloat {
    let style = NSMutableParagraphStyle()
    style.alignment = .center
    style.lineBreakMode = .byWordWrapping
    let attrs: [NSAttributedString.Key: Any] = [
        .font: font(fontName, size),
        .foregroundColor: ink,
        .kern: kern,
        .paragraphStyle: style,
    ]
    let bounds = (text as NSString).boundingRect(
        with: NSSize(width: maxWidth, height: 800),
        options: [.usesLineFragmentOrigin, .usesFontLeading],
        attributes: attrs)
    let rect = NSRect(x: (CGFloat(width) - maxWidth) / 2, y: y - bounds.height,
                      width: maxWidth, height: bounds.height + 4)
    (text as NSString).draw(with: rect, options: [.usesLineFragmentOrigin], attributes: attrs)
    return bounds.height
}

func paint(_ job: Job) {
    let image = NSImage(size: NSSize(width: width, height: height))
    image.lockFocus()
    // Angle 90 paints the first color at the bottom. Lead with cream
    // so the shelf's dark band stays at the top.
    let ground = NSGradient(
        colors: [
            NSColor(calibratedRed: 0.97, green: 0.94, blue: 0.86, alpha: 1),
            NSColor(calibratedRed: 0.93, green: 0.86, blue: 0.74, alpha: 1),
            NSColor(calibratedRed: 0.55, green: 0.46, blue: 0.36, alpha: 1),
            NSColor(calibratedRed: 0.22, green: 0.18, blue: 0.15, alpha: 1),
        ],
        atLocations: [0.0, 0.42, 0.72, 1.0] as [CGFloat],
        colorSpace: .genericRGB)
    ground?.draw(in: NSRect(x: 0, y: 0, width: width, height: height), angle: 90)

    chiRho(cx: 450, cy: 860)

    var y: CGFloat = 760
    let author = job.author.uppercased()
    let authorSize: CGFloat = author.count > 32 ? 18 : 22
    y -= drawCentered(author, fontName: "TimesNewRomanPSMT", size: authorSize,
                      y: y, kern: 3.2, maxWidth: 760)
    y -= 28
    var titleSize: CGFloat = 54
    if job.title.count > 42 { titleSize = 40 }
    if job.title.count > 70 { titleSize = 32 }
    y -= drawCentered(job.title, fontName: "TimesNewRomanPS-BoldMT", size: titleSize,
                      y: y, kern: 0.2, maxWidth: 760)
    if !job.subtitle.isEmpty {
        y -= 16
        y -= drawCentered(job.subtitle, fontName: "TimesNewRomanPS-ItalicMT", size: 26,
                          y: y, kern: 0.4, maxWidth: 720)
    }
    y -= 22
    ink.setStroke()
    let rule = NSBezierPath()
    rule.lineWidth = 1.1
    rule.move(to: NSPoint(x: 330, y: y))
    rule.line(to: NSPoint(x: 570, y: y))
    rule.stroke()
    y -= 36
    _ = drawCentered("Private study edition", fontName: "TimesNewRomanPSMT", size: 18,
                     y: y, kern: 1.6, maxWidth: 760)
    image.unlockFocus()

    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let data = rep.representation(using: .jpeg, properties: [.compressionFactor: 0.9])
    else {
        fputs("could not encode \(job.out)\n", stderr)
        exit(1)
    }
    do {
        try data.write(to: URL(fileURLWithPath: job.out))
    } catch {
        fputs("write failed \(job.out): \(error)\n", stderr)
        exit(1)
    }
}

let args = CommandLine.arguments
guard args.count == 2 else {
    fputs("usage: logos_cover jobs.json\n", stderr)
    exit(2)
}
let url = URL(fileURLWithPath: args[1])
let jobs = try JSONDecoder().decode([Job].self, from: Data(contentsOf: url))
for job in jobs {
    paint(job)
}
fputs("covers \(jobs.count)\n", stderr)
