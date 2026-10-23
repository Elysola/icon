import glob
import subprocess

from main_symbol import MAIN, symbol_body, symbol_defs

ICON_DIR = "projects/elysola"
FONT_CANDIDATES = glob.glob("/nix/store/*dejavu-fonts*/share/fonts/truetype/DejaVuSans-Bold.ttf")
FONT = FONT_CANDIDATES[0] if FONT_CANDIDATES else "DejaVu Sans"

ICON_DISP = 256
GAP = 64
PAD = 28
F = 200

TEXT_FILL = "#A99EF3"  # 与标志渐变外圈的淡紫一致

VB_X, VB_Y, VB_W, _ = MAIN["viewbox"]
SCALE = ICON_DISP / VB_W


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
    icon = (
        f'<g transform="translate({PAD} {icon_y:.2f}) scale({SCALE:.6f}) '
        f'translate({-VB_X} {-VB_Y})">\n{symbol_body("url(#g)")}\n</g>'
    )
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w:.0f}" height="{canvas_h:.0f}"
 viewBox="0 0 {canvas_w:.0f} {canvas_h:.0f}" preserveAspectRatio="xMidYMid meet" role="img">
<title>{word}</title>
<defs>{symbol_defs()}</defs>
{icon}
<text x="{PAD + ICON_DISP + GAP:.0f}" y="{text_y:.0f}" font-family="DejaVu Sans" font-weight="bold"
 font-size="{F}" dominant-baseline="central" fill="{TEXT_FILL}">{word}</text>
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
