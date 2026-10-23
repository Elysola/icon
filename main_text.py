import glob
import subprocess

ICON_DIR = "projects/elysola"
ICON_SVG = f"{ICON_DIR}/icon.svg"
FONT_CANDIDATES = glob.glob("/nix/store/*dejavu-fonts*/share/fonts/truetype/DejaVuSans-Bold.ttf")
FONT = FONT_CANDIDATES[0] if FONT_CANDIDATES else "DejaVu Sans"

ICON_DISP = 256
GAP = 64
PAD = 28
F = 200

GRAD_TOP = "#C8E0FD"
GRAD_BOTTOM = "#3069C9"
TEXT_FILL = "#1E63CE"

ICON_PATHS = [
    "M 609.80 112.10 c -67.60 5.20 -128.60 42.30 -164.30 100.00 -10.60 17.10 -21.10 41.40 -25.10 57.90 l -1.80 7.50 -19.60 0.10 c -21.40 -0.00 -30.50 1.40 -49.20 7.40 -12.70 4.10 -33.30 14.60 -44.80 22.70 -12.10 8.70 -30.60 27.10 -39.30 39.30 -7.90 11.20 -19.30 33.70 -23.60 46.80 -6.10 18.30 -9.00 42.70 -7.20 59.90 5.50 53.20 34.30 95.80 82.10 121.60 16.20 8.70 33.80 14.90 72.00 25.60 11.80 3.30 26.00 7.70 31.50 9.60 26.80 9.60 52.30 22.20 69.40 34.30 9.70 6.80 10.50 6.80 9.60 -0.60 -1.20 -9.40 -0.70 -38.90 0.90 -50.70 11.10 -83.90 62.80 -157.00 137.60 -194.60 79.00 -39.70 169.40 -34.90 243.20 13.00 17.60 11.30 28.80 14.60 47.10 13.90 13.30 -0.60 22.20 -3.30 32.30 -9.80 14.60 -9.60 25.80 -27.30 29.00 -46.00 8.00 -47.00 -26.50 -103.70 -78.20 -128.60 -10.10 -4.80 -29.20 -10.90 -40.90 -13.00 -12.40 -2.10 -39.10 -2.30 -51.30 -0.20 l -8.20 1.50 -4.60 -8.60 c -30.30 -56.10 -84.90 -96.20 -145.40 -106.60 -8.40 -1.40 -33.10 -3.60 -38.00 -3.40 -1.40 0.10 -7.30 0.60 -13.20 1.00 z",
    "M 375.50 631.60 c -29.80 4.50 -49.80 12.20 -70.80 27.10 -18.50 13.10 -37.20 35.40 -48.20 57.30 -5.70 11.30 -12.60 31.80 -15.10 45.00 -2.70 14.30 -2.50 41.90 0.50 56.00 16.60 78.50 77.60 132.40 154.70 136.70 l 11.10 0.60 2.70 6.30 c 3.30 7.50 13.40 25.20 19.60 34.40 26.20 38.90 65.90 71.80 108.70 90.10 75.20 32.30 158.90 26.40 228.80 -16.30 25.30 -15.50 53.80 -41.10 71.00 -64.00 5.10 -6.80 8.50 -10.50 9.50 -10.30 0.80 0.20 7.40 0.90 14.50 1.60 28.80 2.50 56.20 -2.90 82.40 -16.20 36.80 -18.70 64.50 -53.30 74.50 -92.90 7.90 -31.30 1.80 -59.40 -16.90 -78.10 -17.40 -17.50 -41.60 -22.90 -66.20 -14.80 -8.90 2.90 -17.00 8.50 -29.70 20.70 -48.60 46.60 -109.10 70.40 -172.10 67.80 -34.50 -1.40 -63.90 -8.70 -94.00 -23.50 -58.30 -28.70 -99.10 -74.40 -122.50 -137.60 -12.20 -33.00 -26.10 -51.40 -51.70 -68.10 -21.50 -14.20 -45.20 -21.30 -72.80 -21.90 -8.20 -0.20 -16.30 -0.10 -18.00 0.10 z",
]

SCALE = ICON_DISP / 1254.0


def font_args():
    if FONT.endswith(".ttf"):
        return ["-font", FONT]
    return ["-font", "DejaVu Sans", "-weight", "bold"]


def measure(text):
    out = subprocess.check_output(
        ["magick", "-background", "none", "-fill", "white", *font_args(),
         "-pointsize", str(F), "label:" + text, "-trim", "-format", "%wx%h", "info:"]
    )
    w, h = out.decode().strip().split("x")
    return int(w), int(h)


def build_svg(word, tw, th, path):
    max_h = max(ICON_DISP, th)
    canvas_w = PAD * 2 + ICON_DISP + GAP + tw
    canvas_h = PAD * 2 + max_h
    icon_y = PAD + (max_h - ICON_DISP) / 2
    text_y = PAD + max_h / 2
    paths = "\n".join(
        f'  <path transform="translate({PAD} {icon_y:.2f}) scale({SCALE:.6f})" d="{d}"/>'
        for d in ICON_PATHS
    )
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.0f}" height="{canvas_h:.0f}"
 viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}" preserveAspectRatio="xMidYMid meet" role="img">
<title>{word}</title>
<defs>
<linearGradient id="g" gradientUnits="userSpaceOnUse"
 x1="{canvas_w / 2:.0f}" y1="{PAD:.0f}" x2="{canvas_w / 2:.0f}" y2="{canvas_h - PAD:.0f}">
<stop offset="0%" stop-color="{GRAD_TOP}"/><stop offset="100%" stop-color="{GRAD_BOTTOM}"/>
</linearGradient>
</defs>
<g fill="url(#g)">
{paths}
<text x="{PAD + ICON_DISP + GAP:.0f}" y="{text_y:.0f}" font-family="DejaVu Sans" font-weight="bold"
 font-size="{F}" dominant-baseline="central" fill="{TEXT_FILL}">{word}</text>
</g>
</svg>
'''
    try:
        with open(path, "w") as f:
            f.write(svg)
    except OSError as exc:
        raise RuntimeError(f"Failed to write generated SVG: {path}") from exc


def main():
    for word, prefix in [("Elysola", "icon-text")]:
        tw, th = measure(word)
        build_svg(word, tw, th, f"{ICON_DIR}/{prefix}.svg")
        print(f"{prefix}: text {tw}x{th}")


if __name__ == "__main__":
    main()
