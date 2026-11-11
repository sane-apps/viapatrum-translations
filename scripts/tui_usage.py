#!/usr/bin/env python3
"""Read a terminal app's own usage panel without a person: open it in a pseudo-terminal, answer a "trust this
folder" prompt if one shows, type /usage, save what the screen showed, quit. No model turn is asked for.
usage: tui_usage.py OUTFILE -- command [args...]"""
import fcntl, os, pty, re, select, struct, sys, termios, time

ANSI = re.compile(r"\x1b\[[0-9;?<>=]*[A-Za-z~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b[()][A-Z0-9]|\x1b[=>78MDEHc]|\x1bP[^\x1b]*\x1b\\")


def clean(raw: bytes) -> list:
    text = ANSI.sub("\n", raw.decode("utf-8", "replace")).replace("\r", "\n")
    return list(dict.fromkeys(re.sub(r"\s+", " ", l).strip() for l in text.split("\n") if l.strip()))


def main() -> int:
    out = sys.argv[1]
    cmd = sys.argv[sys.argv.index("--") + 1:]
    pid, fd = pty.fork()
    if pid == 0:
        os.environ["TERM"] = "xterm-256color"
        os.execvp(cmd[0], cmd)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 60, 170, 0, 0))
    buf = bytearray()

    def pump(seconds):
        end = time.time() + seconds
        while time.time() < end:
            r, _, _ = select.select([fd], [], [], 0.2)
            if not r:
                continue
            try:
                d = os.read(fd, 65536)
            except OSError:
                return
            if not d:
                return
            buf.extend(d)
            if b"\x1b[6n" in d:                       # the queries a full-screen app waits on
                os.write(fd, b"\x1b[1;1R")
            if b"\x1b[c" in d or b"\x1b[0c" in d:
                os.write(fd, b"\x1b[?62;c")

    def send(keys: bytes, gap=0.06):
        for ch in keys:
            os.write(fd, bytes([ch])); time.sleep(gap)

    pump(12)
    stages = {"start": clean(bytes(buf))}
    if re.search(r"trust", " ".join(stages["start"]), re.I):
        send(b"\r"); pump(6)                          # accept the folder this lane always runs in
        stages["after_trust"] = clean(bytes(buf))
    mark = len(buf)
    send(b"/usage"); pump(1.5); send(b"\r"); pump(10)
    panel = clean(bytes(buf[mark:]))
    send(b"\x1b"); pump(0.7); send(b"\x03"); pump(0.7); send(b"\x03"); pump(0.7)
    try:
        os.kill(pid, 15)
    except OSError:
        pass
    with open(out, "w") as f:
        for name, lines in stages.items():
            f.write("##### %s\n%s\n" % (name, "\n".join(lines[-40:])))
        f.write("##### panel\n" + "\n".join(panel) + "\n")
    print("panel lines: %d" % len(panel))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
