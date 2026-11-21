import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / "projects"
OUT = ROOT / "output"
REGISTRY = ROOT / "icons.json"
GEOMETRY_KIT = ROOT / "geometry-kit"


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, check=True, env=env)


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise RuntimeError(f"{name} not found; run inside `nix develop`")
    return executable


def controlled_environment() -> dict[str, str]:
    environment = os.environ.copy()
    fontconfig_file = environment.get("ELY_FONTCONFIG_FILE")
    if not fontconfig_file:
        raise RuntimeError("ELY_FONTCONFIG_FILE is unset; run inside `nix develop`")
    environment["FONTCONFIG_FILE"] = fontconfig_file
    return environment


def assert_font(environment: dict[str, str]) -> None:
    fc_match = require_executable("fc-match")
    match = subprocess.check_output(
        [fc_match, "-f", "%{file}\n", "DejaVu Sans:style=Bold"],
        text=True,
        env=environment,
    ).strip()
    if Path(match).name != "DejaVuSans-Bold.ttf":
        raise RuntimeError(f"DejaVu Sans Bold resolved to the wrong font: {match}")


def generate_geometry() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        out = Path(temporary)
        run(
            [
                require_executable("python3"),
                str(GEOMETRY_KIT / "generate.py"),
                str(GEOMETRY_KIT / "icon-geometry.json"),
                str(out),
            ]
        )
        generated = {
            out / "elysola-standard.svg": PROJECTS / "elysola" / "icon.svg",
            out
            / "elysola-decorative.svg": PROJECTS
            / "elysola"
            / "icon-decorative.svg",
        }
        for source, destination in generated.items():
            destination.write_bytes(source.read_bytes())


def text_icon_markup() -> str:
    source = (PROJECTS / "elysola" / "icon.svg").read_text(encoding="utf-8")
    start = source.find(">") + 1
    end = source.rfind("</svg>")
    if start <= 0 or end < start:
        raise RuntimeError("Invalid Elysola icon SVG")
    return source[start:end].strip()


def generate_text_icon(environment: dict[str, str]) -> None:
    magick = require_executable("magick")
    font_file = subprocess.check_output(
        [require_executable("fc-match"), "-f", "%{file}\n", "DejaVu Sans:style=Bold"],
        text=True,
        env=environment,
    ).strip()
    measured = subprocess.check_output(
        [
            magick,
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
        env=environment,
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
{text_icon_markup()}
</svg>
<text x="{pad + icon_size + gap}" y="{text_y:.0f}" font-family="DejaVu Sans" font-weight="bold"
 font-size="{font_size}" dominant-baseline="central" fill="#000000">Elysola</text>
</g>
</svg>
"""
    (PROJECTS / "elysola" / "icon-text.svg").write_text(content, encoding="utf-8")


def render_png(
    renderer: str,
    source: Path,
    destination: Path,
    width: int,
    environment: dict[str, str],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run(
        [renderer, "-w", str(width), "-o", str(destination), str(source)],
        env=environment,
    )


def build_outputs(
    registry: dict[str, Any], environment: dict[str, str]
) -> dict[str, Any]:
    renderer = require_executable("rsvg-convert")
    sizes = registry["sizes"]
    manifest: dict[str, Any] = {"projects": {}}
    for asset in registry["assets"]:
        source = ROOT / asset["source"]
        project = asset["project"]
        name = asset["name"]
        out_dir = OUT / project
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{name}.svg").write_bytes(source.read_bytes())
        pngs = []
        for width in sizes:
            filename = f"{name}-{width}.png"
            render_png(renderer, source, out_dir / filename, width, environment)
            pngs.append(filename)
        projects = manifest["projects"]
        project_entry = projects.setdefault(project, {"assets": {}})
        project_entry["assets"][name] = {"svg": f"{name}.svg", "png": pngs}
        print(f"  {project}/{name}: {len(pngs)} PNGs")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate and render all icon assets")
    parser.add_argument(
        "--check", action="store_true", help="fail if generation changes tracked assets"
    )
    args = parser.parse_args()
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read icon registry: {error}") from error
    environment = controlled_environment()
    assert_font(environment)

    tracked = [
        PROJECTS / "elysola" / "icon.svg",
        PROJECTS / "elysola" / "icon-decorative.svg",
        PROJECTS / "elysola" / "icon-text.svg",
    ]
    before = {path: path.read_bytes() for path in tracked if path.exists()}
    generate_geometry()
    generate_text_icon(environment)
    if args.check:
        changed = [path for path in tracked if before.get(path) != path.read_bytes()]
        if changed:
            names = ", ".join(str(path.relative_to(ROOT)) for path in changed)
            raise RuntimeError(f"generated SVGs are stale: {names}")

    OUT.mkdir(parents=True, exist_ok=True)
    manifest = build_outputs(registry, environment)
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nExported {len(manifest['projects'])} project(s) to {OUT}/")


if __name__ == "__main__":
    main()
