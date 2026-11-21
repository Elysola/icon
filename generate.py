import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / "projects"
GEOMETRY_KIT = ROOT / "geometry-kit"
GENERATED = (
    PROJECTS / "elysola" / "icon-mono.svg",
    PROJECTS / "elysola" / "icon-decorative.svg",
    PROJECTS / "elysola" / "icon-text.svg",
)


def require(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise RuntimeError(f"{name} not found; run inside `nix develop`")
    return executable


def environment() -> dict[str, str]:
    result = os.environ.copy()
    config = result.get("ELY_FONTCONFIG_FILE")
    if not config:
        raise RuntimeError("ELY_FONTCONFIG_FILE is unset; run inside `nix develop`")
    result["FONTCONFIG_FILE"] = config
    return result


def geometry(destination: Path) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        subprocess.run(
            [
                require("python3"),
                str(GEOMETRY_KIT / "generate.py"),
                str(GEOMETRY_KIT / "icon-geometry.json"),
                temporary,
            ],
            check=True,
        )
        generated = {
            Path(temporary) / "elysola-standard.svg": destination / "icon-mono.svg",
            Path(temporary)
            / "elysola-decorative.svg": destination
            / "icon-decorative.svg",
        }
        for source, target in generated.items():
            target.write_bytes(source.read_bytes())


def icon_markup(source: Path) -> str:
    text = source.read_text(encoding="utf-8")
    start, end = text.find(">") + 1, text.rfind("</svg>")
    if start <= 0 or end < start:
        raise RuntimeError(f"Invalid SVG: {source}")
    return text[start:end].strip()


def text_icon(destination: Path, env: dict[str, str]) -> None:
    font_file = subprocess.check_output(
        [require("fc-match"), "-f", "%{file}\n", "DejaVu Sans:style=Bold"],
        text=True,
        env=env,
    ).strip()
    measured = subprocess.check_output(
        [
            require("magick"),
            "-background",
            "none",
            "-fill",
            "white",
            "-font",
            font_file,
            "-pointsize",
            "200",
            "label:Elysola",
            "-trim",
            "-format",
            "%wx%h",
            "info:",
        ],
        text=True,
        env=env,
    ).strip()
    text_width, text_height = (int(value) for value in measured.split("x"))
    pad, icon_size, gap, font_size = 28, 256, 64, 200
    max_height = max(icon_size, text_height)
    canvas_width = pad * 3 + icon_size + gap + text_width + 120
    canvas_height = pad * 2 + max_height
    icon_y = pad + (max_height - icon_size) / 2
    text_y = pad + max_height / 2
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_width}" height="{canvas_height}"
 viewBox="0 0 {canvas_width} {canvas_height}" preserveAspectRatio="xMidYMid meet" role="img">
<title>Elysola</title>
<g fill="#000000">
<svg x="{pad}" y="{icon_y:.2f}" width="{icon_size}" height="{icon_size}" viewBox="0 0 512 512">
{icon_markup(destination / 'icon-mono.svg')}
</svg>
<text x="{pad + icon_size + gap}" y="{text_y:.0f}" font-family="DejaVu Sans" font-weight="bold"
 font-size="{font_size}" dominant-baseline="central" fill="#000000">Elysola</text>
</g>
</svg>
"""
    (destination / "icon-text.svg").write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Elysola project-specific SVGs"
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    env = environment()
    before = {path: path.read_bytes() for path in GENERATED if path.exists()}
    destination = PROJECTS / "elysola"
    geometry(destination)
    text_icon(destination, env)
    if args.check:
        changed = [path for path in GENERATED if before.get(path) != path.read_bytes()]
        if changed:
            names = ", ".join(str(path.relative_to(ROOT)) for path in changed)
            raise RuntimeError(f"Generated SVGs are stale: {names}")


if __name__ == "__main__":
    main()
