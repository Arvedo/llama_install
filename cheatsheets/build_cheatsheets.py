"""
Generator für die llama.cpp Download-Cheat-Sheets.

Erzeugt:
  - download_windows.svg / .png
  - download_linux.svg   / .png
  - download_apple_mobile.svg / .png
  - handout.html  (alle Sheets, A4 quer)  ->  handout.pdf

Aufruf:  python build_cheatsheets.py
PNG/PDF werden per Edge/Chrome headless gerendert (falls vorhanden).

Stand der Dateinamen: Release b11377 (Okt 2026). Bei neuen CUDA/ROCm-Versionen
einfach die Strings in WINDOWS / LINUX unten anpassen.
"""
import html
import os
import pathlib
import shutil
import subprocess

OUT = pathlib.Path(__file__).resolve().parent
W, H = 1920, 1080

FONT = "'Segoe UI', 'Inter', 'Helvetica Neue', Arial, sans-serif"
MONO = "'Cascadia Mono', Consolas, Menlo, 'DejaVu Sans Mono', monospace"

C = dict(
    bg="#F6F7F9", ink="#0F172A", muted="#64748B", soft="#94A3B8", line="#A3AFC2",
    card="#FFFFFF", border="#E2E8F0", q="#1E293B", qsub="#CBD5E1",
    nvidia="#5E9400", amd="#D7191F", intel="#0068B5", cpu="#475569", apple="#111827",
    android="#2E7D32", warn="#92400E", warnbg="#FEF3C7", warnline="#F59E0B",
    accent="#7C3AED",
)

RELEASES_URL = "github.com/ggml-org/llama.cpp/releases"


# ---------------------------------------------------------------- primitives
def esc(s: str) -> str:
    return html.escape(s, quote=False)


def text(x, y, s, size=20, weight=400, fill=None, family=FONT, anchor="start", italic=False):
    fill = fill or C["ink"]
    style = ' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{style}>{esc(s)}</text>')


def rich(x, y, parts, size=20, family=FONT, anchor="start"):
    """parts = [(text, dict(fill=..., weight=..., family=...)), ...]"""
    spans = []
    for s, a in parts:
        attrs = []
        if "fill" in a:
            attrs.append(f'fill="{a["fill"]}"')
        if "weight" in a:
            attrs.append(f'font-weight="{a["weight"]}"')
        if "family" in a:
            attrs.append(f'font-family="{a["family"]}"')
        if "size" in a:
            attrs.append(f'font-size="{a["size"]}"')
        spans.append(f'<tspan {" ".join(attrs)}>{esc(s)}</tspan>')
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'fill="{C["ink"]}" text-anchor="{anchor}">{"".join(spans)}</text>')


def rect(x, y, w, h, fill, rx=14, stroke=None, sw=1.5, shadow=False, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    f = ' filter="url(#sh)"' if shadow else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{f} {extra}/>'


def pill(cx, cy, label, color, size=17, pad=14, bg="#FFFFFF"):
    w = len(label) * size * 0.56 + pad * 2
    h = size + 14
    return (rect(cx - w / 2, cy - h / 2, w, h, bg, rx=h / 2, stroke=color, sw=2)
            + text(cx, cy + size * 0.36, label, size, 700, color, anchor="middle"))


def edge(x1, y1, x2, y2, label=None, color=None, lsize=17):
    dx = (x2 - x1) / 2
    d = f"M{x1},{y1} C{x1 + dx},{y1} {x2 - dx},{y2} {x2 - 4},{y2}"
    out = f'<path d="{d}" fill="none" stroke="{C["line"]}" stroke-width="3" marker-end="url(#arr)"/>'
    if label:
        out += pill((x1 + x2) / 2, (y1 + y2) / 2, label, color or C["q"], lsize)
    return out


def qnode(x, y, w, h, lines, sub=None, sub_mono=False):
    out = [rect(x, y, w, h, C["q"], rx=20, shadow=True)]
    lh = 32
    total = len(lines) * lh + (30 if sub else 0)
    y0 = y + h / 2 - total / 2 + 24
    for i, l in enumerate(lines):
        out.append(text(x + w / 2, y0 + i * lh, l, 27, 700, "#FFFFFF", anchor="middle"))
    if sub:
        out.append(text(x + w / 2, y0 + len(lines) * lh + 8, sub, 16, 400, C["qsub"],
                        MONO if sub_mono else FONT, "middle"))
    return "\n".join(out)


def leaf(x, y, w, h, color, title, tag, file_suffix, prefix="llama-bXXXX-bin-", lib=None):
    out = [
        rect(x, y, w, h, color, rx=14, shadow=True),
        rect(x + 9, y, w - 9, h, C["card"], rx=12),
        rect(x, y, w, h, "none", rx=14, stroke=C["border"]),
        text(x + 30, y + 36, title, 23, 700, color),
        text(x + w - 22, y + 36, tag, 16, 500, C["muted"], anchor="end"),
        rich(x + 30, y + 72, [(prefix, dict(fill=C["soft"])),
                              (file_suffix, dict(fill=C["ink"], weight=700))],
             size=19, family=MONO),
    ]
    if lib:
        by = y + h - 44
        out.append(rect(x + 26, by, w - 50, 32, C["warnbg"], rx=8, stroke=C["warnline"], sw=1.5))
        out.append(rich(x + 38, by + 22, [("+ mitladen: ", dict(fill=C["warn"], weight=700, family=FONT)),
                                          (lib, dict(fill=C["warn"], family=MONO))], size=14.5))
    return "\n".join(out)


def step(x, y, w, h, n, title, body_parts, body_mono=False):
    out = [rect(x, y, w, h, C["card"], rx=14, stroke=C["border"], shadow=True),
           f'<circle cx="{x + 36}" cy="{y + h / 2}" r="20" fill="{C["accent"]}"/>',
           text(x + 36, y + h / 2 + 7, str(n), 21, 700, "#FFFFFF", anchor="middle"),
           text(x + 70, y + 36, title, 20, 700, C["ink"])]
    out.append(rich(x + 70, y + 68, body_parts, size=16.5, family=MONO if body_mono else FONT))
    return "\n".join(out)


def svg_doc(body: str, title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<title>{esc(title)}</title>
<defs>
  <filter id="sh" x="-10%" y="-10%" width="120%" height="130%">
    <feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#0F172A" flood-opacity="0.10"/>
  </filter>
  <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="{C['line']}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="{C['bg']}"/>
{body}
</svg>
"""


def header(title, os_label, os_color, legend_parts):
    return "\n".join([
        rect(0, 0, W, 8, C["accent"], rx=0),
        text(60, 78, title, 46, 800, C["ink"]),
        rich(60, 116, [("Quelle: ", dict(fill=C["muted"])),
                       (RELEASES_URL, dict(fill=C["accent"], weight=700)),
                       ("  →  neuestes Release  →  „Assets“ aufklappen", dict(fill=C["muted"]))], size=21),
        rect(W - 330, 36, 270, 60, os_color, rx=30),
        text(W - 195, 75, os_label, 24, 800, "#FFFFFF", anchor="middle"),
        rich(60, 152, legend_parts, size=17),
    ])


# ---------------------------------------------------------------- PC tree
WINDOWS = dict(
    key="windows", title="llama.cpp Download-Kompass", os_label="WINDOWS", os_color="#0078D4",
    vendor_sub="Task-Manager → Leistung → GPU", vendor_mono=False,
    arch_sub="$env:PROCESSOR_ARCHITECTURE", arch_hint="AMD64 = x64 · ARM64 = arm64",
    cuda13=("win-cuda-13.4-x64.zip", "cudart-llama-bin-win-cuda-13.4-x64.zip"),
    cuda12=("win-cuda-12.4-x64.zip", "cudart-llama-bin-win-cuda-12.4-x64.zip"),
    rocm="win-rocm-10.0-x64.zip",
    sycl="win-sycl-x64.zip", sycl_tag="Arc A/B-Serie · Core Ultra iGPU",
    cpu_x64="win-cpu-x64.zip", cpu_arm="win-cpu-arm64.zip",
    arm_label="arm64 · z. B. Snapdragon X",
    run="./llama-server.exe -m modell.gguf", unpack=".zip entpacken (Rechtsklick → Alle extrahieren)",
    foot=("Bewusst weggelassen: Vulkan (Universal-Fallback, z. B. ältere AMD-Karten / iGPU), OpenVINO, "
          "OpenCL-Adreno, NVIDIA auf arm64 (win-cuda-13.4-arm64). ROCm/SYCL: aktuellen GPU-Treiber installieren."),
)

LINUX = dict(
    key="linux", title="llama.cpp Download-Kompass", os_label="LINUX · UBUNTU", os_color="#E95420",
    vendor_sub="lspci | grep -iE 'vga|3d'", vendor_mono=True,
    arch_sub="uname -m", arch_hint="x86_64 = x64 · aarch64 = arm64",
    cuda13=("ubuntu-cuda-13.4-x64.tar.gz", "cudart-llama-bXXXX-bin-ubuntu-cuda-13.4-x64.tar.gz"),
    cuda12=("ubuntu-cuda-12.8-x64.tar.gz", "cudart-llama-bXXXX-bin-ubuntu-cuda-12.8-x64.tar.gz"),
    rocm="ubuntu-rocm-10.0-x64.tar.gz",
    sycl="ubuntu-sycl-fp16-x64.tar.gz", sycl_tag="FP16 · bei Problemen: sycl-fp32",
    cpu_x64="ubuntu-x64.tar.gz", cpu_arm="ubuntu-arm64.tar.gz",
    arm_label="arm64 · z. B. Raspberry Pi 5, Graviton",
    run="./llama-server -m modell.gguf", unpack="je Archiv: tar -xzf <datei>.tar.gz  (cudart ebenso)",
    foot=("Bewusst weggelassen: Vulkan (Universal-Fallback), OpenVINO, s390x, Snapdragon. "
          "NVIDIA auf arm64 (DGX Spark, Jetson Thor): ubuntu-cuda-13.4-arm64 + passende cudart. "
          "ROCm/SYCL: Treiber bzw. Runtime installiert haben."),
)


def build_pc(cfg) -> str:
    b = []
    b.append(header(cfg["title"], cfg["os_label"], cfg["os_color"], [
        ("Alle Dateien heißen  ", dict(fill=C["muted"])),
        ("llama-bXXXX-bin-", dict(fill=C["ink"], family=MONO, weight=700)),
        ("…   (XXXX = aktuelle Build-Nr., z. B. b11377)      ", dict(fill=C["muted"])),
        ("■ ", dict(fill=C["warnline"], size=20)),
        ("Gelb = zweites Archiv (CUDA-Runtime) laden & in DENSELBEN Ordner entpacken", dict(fill=C["warn"], weight=700)),
    ]))

    # question nodes
    b.append(qnode(60, 430, 320, 160, ["Dedizierte", "Grafikkarte?"], "Nur Onboard/iGPU = Nein"))
    b.append(qnode(480, 290, 310, 140, ["Welcher", "Hersteller?"], cfg["vendor_sub"], cfg["vendor_mono"]))
    b.append(qnode(480, 750, 310, 140, ["CPU-", "Architektur?"], cfg["arch_sub"], True))
    b.append(text(635, 915, cfg["arch_hint"], 15, 600, C["muted"], anchor="middle"))
    b.append(qnode(880, 175, 300, 170, ["Blackwell-", "Generation?"], "RTX 50xx & neuer"))
    b.append(text(1030, 368, "Modell prüfen: nvidia-smi", 15, 600, C["muted"], MONO, "middle"))

    # edges (drawn before leaves so they sit underneath)
    b.append(edge(380, 510, 480, 360, "Ja", C["q"]))
    b.append(edge(380, 510, 480, 820, "Nein", C["q"]))
    b.append(edge(790, 325, 880, 260, "NVIDIA", C["nvidia"]))
    b.append(edge(790, 375, 1290, 510, "AMD", C["amd"]))
    b.append(edge(790, 410, 1290, 620, "Intel", C["intel"]))
    b.append(edge(1180, 240, 1290, 235, "Ja", C["nvidia"], 15))
    b.append(edge(1180, 290, 1290, 380, "Nein", C["nvidia"], 15))
    b.append(edge(790, 795, 1290, 770, "x64 · Intel / AMD", C["cpu"]))
    b.append(edge(790, 850, 1290, 880, cfg["arm_label"], C["cpu"]))

    # leaves
    lx, lw = 1290, 590
    b.append(leaf(lx, 170, lw, 130, C["nvidia"], "NVIDIA · CUDA 13", "RTX 50xx · Blackwell",
                  cfg["cuda13"][0], lib=cfg["cuda13"][1]))
    b.append(leaf(lx, 315, lw, 130, C["nvidia"], "NVIDIA · CUDA 12", "RTX 20/30/40 · GTX 10/16",
                  cfg["cuda12"][0], lib=cfg["cuda12"][1]))
    b.append(leaf(lx, 462, lw, 96, C["amd"], "AMD · ROCm", "Radeon RX 6000/7000/9000", cfg["rocm"]))
    b.append(leaf(lx, 572, lw, 96, C["intel"], "Intel · SYCL", cfg["sycl_tag"], cfg["sycl"]))
    b.append(leaf(lx, 722, lw, 96, C["cpu"], "Nur CPU · x64", "Intel Core / AMD Ryzen", cfg["cpu_x64"]))
    b.append(leaf(lx, 832, lw, 96, C["cpu"], "Nur CPU · arm64", "ARM-Prozessor", cfg["cpu_arm"]))

    # steps
    sy, sh_, sw = 950, 92, 586
    b.append(step(60, sy, sw, sh_, 1, "Herunterladen",
                  [("Datei(en) aus dem Baum oben laden", dict(fill=C["muted"]))]))
    b.append(step(60 + sw + 31, sy, sw, sh_, 2, "Entpacken – alles in EINEN Ordner",
                  [(cfg["unpack"], dict(fill=C["muted"]))]))
    b.append(step(60 + 2 * (sw + 31), sy, sw, sh_, 3, "Modell (.gguf) dazu → Terminal → starten",
                  [(cfg["run"], dict(fill=C["ink"], weight=700, family=MONO)),
                   ("   → localhost:8080", dict(fill=C["muted"]))]))
    b.append(text(60, 1066, cfg["foot"], 14, 400, C["muted"]))
    return svg_doc("\n".join(b), f"llama.cpp Download-Kompass – {cfg['os_label']}")


# ---------------------------------------------------------------- Apple & Mobile
def bullet_list(x, y, items, size=19, gap=34, color=None):
    out = []
    for i, s in enumerate(items):
        yy = y + i * gap
        out.append(f'<circle cx="{x + 6}" cy="{yy - size * 0.33}" r="4.5" fill="{color or C["accent"]}"/>')
        out.append(text(x + 22, yy, s, size, 400, C["ink"]))
    return "\n".join(out)


def card(x, y, w, h, color, title, subtitle):
    return "\n".join([
        rect(x, y, w, h, C["card"], rx=20, stroke=C["border"], shadow=True),
        f'<path d="M{x},{y + 20} a20,20 0 0 1 20,-20 h{w - 40} a20,20 0 0 1 20,20 v52 h-{w} z" fill="{color}"/>',
        text(x + 28, y + 50, title, 30, 800, "#FFFFFF"),
        text(x + w - 26, y + 48, subtitle, 18, 600, "#E5E7EB", anchor="end"),
    ])


def app_box(x, y, w, name, store, color):
    return "\n".join([
        rect(x, y, w, 96, "#F8FAFC", rx=16, stroke=color, sw=2.5),
        text(x + 26, y + 32, "EMPFEHLUNG · Wrapper-App", 14, 800, color),
        text(x + 26, y + 70, name, 32, 800, C["ink"]),
        text(x + w - 22, y + 70, store, 16, 600, C["muted"], anchor="end"),
    ])


def dev_box(x, y, w, lines):
    out = [rect(x, y, w, 30 + 30 * len(lines), "#F1F5F9", rx=12, stroke=C["border"]),
           text(x + 20, y + 26, "NUR FÜR ENTWICKLER / BASTLER", 13, 800, C["muted"])]
    for i, (pre, mono) in enumerate(lines):
        out.append(rich(x + 20, y + 56 + i * 30, [(pre, dict(fill=C["muted"])),
                                                   (mono, dict(fill=C["ink"], weight=700, family=MONO))], size=16))
    return "\n".join(out)


def build_apple_mobile() -> str:
    b = [header("llama.cpp Download-Kompass", "APPLE & MOBILE", C["apple"], [
        ("Desktop = Terminal-Weg mit Release-Dateien  ·  Smartphone = ", dict(fill=C["muted"])),
        ("fertige Wrapper-App nehmen", dict(fill=C["ink"], weight=700)),
        (" (laufen unter der Haube auf llama.cpp / GGUF)", dict(fill=C["muted"])),
    ])]

    # ---- macOS card
    x, y, w, h = 60, 190, 900, 700
    b.append(card(x, y, w, h, C["apple"], "macOS", "Terminal-Weg"))
    b.append(qnode(x + 30, y + 130, 270, 170, ["Welcher", "Chip?"], " → Über diesen Mac"))
    b.append(edge(x + 300, y + 215, x + 380, y + 160, "M1 – M5", C["apple"], 15))
    b.append(edge(x + 300, y + 215, x + 380, y + 300, "Intel", C["cpu"], 15))
    lx, lw = x + 380, 490
    b.append(leaf(lx, y + 100, lw, 120, C["apple"], "Apple Silicon", "empfohlen", "macos-arm64.tar.gz"))
    b.append(text(lx + 30, y + 202, "Metal-GPU automatisch aktiv · RAM = VRAM", 16, 500, C["muted"]))
    b.append(leaf(lx, y + 245, lw, 120, C["cpu"], "Intel-Mac", "primär CPU", "macos-x64.tar.gz"))
    b.append(text(lx + 30, y + 347, "eher kleine Modelle (≤ 8B, Q4)", 16, 500, C["muted"]))

    # mac tips
    ty = y + 400
    b.append(rect(x + 30, ty, w - 60, 86, C["warnbg"], rx=12, stroke=C["warnline"]))
    b.append(text(x + 52, ty + 32, "„Kann nicht geöffnet werden“? Gatekeeper-Sperre im Ordner lösen:", 17, 700, C["warn"]))
    b.append(text(x + 52, ty + 66, "xattr -dr com.apple.quarantine .", 19, 700, C["ink"], MONO))
    b.append(step(x + 30, ty + 108, (w - 80) / 2, 92, 1, "Bequemer: Homebrew",
                  [("brew install llama.cpp", dict(fill=C["ink"], weight=700, family=MONO))]))
    b.append(step(x + 50 + (w - 80) / 2, ty + 108, (w - 80) / 2, 92, 2, "Starten",
                  [("./llama-server -m modell.gguf", dict(fill=C["ink"], weight=700, family=MONO))]))
    b.append(text(x + 30, y + h - 22, "Gibt es auch: macos-arm64 „KleidiAI“ – aktuell deaktiviert, ignorieren.",
                  14, 400, C["muted"], italic=True))

    # ---- iOS card
    x, w = 1000, 420
    b.append(card(x, y, w, h, "#0A84FF", "iOS / iPadOS", "App-Weg"))
    b.append(app_box(x + 24, y + 100, w - 48, "Pocket AI Lab", "App Store", "#0A84FF"))
    b.append(text(x + 30, y + 222, "im App Store suchen", 17, 700, "#0A84FF"))
    b.append(bullet_list(x + 30, y + 275, [
        "Kein Terminal, keine Binaries",
        "App lädt & verwaltet Modelle",
        "Läuft komplett offline",
        "Realistisch: 1–4B in Q4",
        "Geräte mit 8 GB+ RAM ideal",
    ], 20, 42, "#0A84FF"))
    b.append(dev_box(x + 24, y + h - 150, w - 48, [
        ("Eigene App bauen: ", "…-xcframework.zip"),
        ("→ ", "in Xcode einbinden"),
    ]))

    # ---- Android card
    x = 1460
    b.append(card(x, y, w, h, C["android"], "Android", "App-Weg"))
    b.append(app_box(x + 24, y + 100, w - 48, "LM Playground", "", C["android"]))
    b.append(rich(x + 30, y + 222, [("lmplayground.app", dict(fill=C["android"], weight=700, family=MONO)),
                                    ("  · kostenlos · Open Source", dict(fill=C["muted"], weight=600))], size=17))
    b.append(bullet_list(x + 30, y + 275, [
        "Kein Terminal, keine Binaries",
        "App lädt & verwaltet Modelle",
        "Läuft komplett offline",
        "Realistisch: 1–4B in Q4",
        "Geräte mit 8 GB+ RAM ideal",
    ], 20, 42, C["android"]))
    b.append(dev_box(x + 24, y + h - 180, w - 48, [
        ("Termux / adb: ", "android-arm64"),
        ("Snapdragon: ", "…-arm64-snapdragon"),
        ("  ", "(Adreno GPU + Hexagon NPU)"),
    ]))

    # ---- bottom banner
    by = 920
    b.append(rect(60, by, W - 120, 120, C["q"], rx=20, shadow=True))
    b.append(text(100, by + 50, "Warum auf dem Smartphone eine Wrapper-App?", 26, 800, "#FFFFFF"))
    b.append(text(100, by + 90,
                  "iOS/Android haben kein offenes Terminal & sandboxen Apps  ·  App übernimmt Download, Speicher & Thermik  ·  "
                  "gleiche GGUF-Modelle wie am PC", 19, 500, C["qsub"]))
    return svg_doc("\n".join(b), "llama.cpp Download-Kompass – Apple & Mobile")


# ---------------------------------------------------------------- handout + render
HANDOUT = """<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8"><title>llama.cpp Download-Kompass – Handout</title>
<style>
  @page {{ size: A4 landscape; margin: 8mm; }}
  html, body {{ margin: 0; background: #fff; }}
  .page {{ page-break-after: always; display: flex; align-items: center; justify-content: center;
          height: 190mm; }}
  .page:last-child {{ page-break-after: auto; }}
  img {{ width: 100%; height: auto; max-height: 190mm; object-fit: contain; }}
</style></head><body>
{pages}
</body></html>
"""


def find_browser():
    for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
        if os.path.exists(p):
            return p
    return shutil.which("msedge") or shutil.which("chrome") or shutil.which("chromium")


def render(browser, args):
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", *args],
                   check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)


def main():
    sheets = {
        "download_windows": build_pc(WINDOWS),
        "download_linux": build_pc(LINUX),
        "download_apple_mobile": build_apple_mobile(),
    }
    for name, svg in sheets.items():
        (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
        print("SVG ", name)

    pages = "\n".join(f'<div class="page"><img src="{n}.svg"></div>' for n in sheets)
    (OUT / "handout.html").write_text(HANDOUT.format(pages=pages), encoding="utf-8")

    browser = find_browser()
    if not browser:
        print("Kein Edge/Chrome gefunden – PNG/PDF übersprungen.")
        return
    for name in sheets:
        render(browser, [f"--window-size={W},{H}", f"--screenshot={OUT / (name + '.png')}",
                         (OUT / f"{name}.svg").as_uri()])
        print("PNG ", name)
    render(browser, [f"--print-to-pdf={OUT / 'handout.pdf'}", "--no-pdf-header-footer",
                     (OUT / "handout.html").as_uri()])
    print("PDF  handout")


if __name__ == "__main__":
    main()
