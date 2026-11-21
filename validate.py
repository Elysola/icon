import json
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
REGISTRY = ROOT / "icons.json"
OUT = ROOT / "output"


def fail(message: str) -> None:
    raise RuntimeError(message)


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise RuntimeError(f"{name} not found")
    return executable


def controlled_environment() -> dict[str, str]:
    environment = os.environ.copy()
    config = environment.get("ELY_FONTCONFIG_FILE")
    if config is None or not config:
        fail("ELY_FONTCONFIG_FILE is unset; run inside `nix develop`")
    environment["FONTCONFIG_FILE"] = str(config)
    return environment


def load_registry() -> dict[str, Any]:
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read icon registry: {error}") from error


def assert_no_forbidden_constructs(registry: dict[str, Any]) -> None:
    checked_code = [
        ROOT / "main.py",
        ROOT / "validate.py",
        ROOT / "pyproject.toml",
        ROOT / "flake.nix",
    ]
    forbidden_renderer = "cairo" + "svg"
    for path in checked_code:
        if forbidden_renderer in path.read_text(encoding="utf-8").lower():
            fail(f"Forbidden legacy renderer reference in {path.relative_to(ROOT)}")
    for asset in registry["assets"]:
        source = ROOT / asset["source"]
        if "var(" in source.read_text(encoding="utf-8"):
            fail(f"CSS var() is forbidden in {source.relative_to(ROOT)}")


def assert_font(environment: dict[str, str]) -> None:
    fc_match = require_executable("fc-match")
    match = subprocess.check_output(
        [fc_match, "-f", "%{file}\n", "DejaVu Sans:style=Bold"],
        text=True,
        env=environment,
    ).strip()
    if Path(match).name != "DejaVuSans-Bold.ttf":
        fail(f"Wrong font selected: {match}")


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"Invalid PNG signature: {path.relative_to(ROOT)}")
    return struct.unpack(">II", data[16:24])


def alpha_plane(path: Path, environment: dict[str, str]) -> tuple[int, int, bytes]:
    magick = require_executable("magick")
    width, height = png_size(path)
    alpha = subprocess.check_output(
        [magick, str(path), "-alpha", "extract", "-depth", "8", "gray:-"],
        env=environment,
    )
    if len(alpha) != width * height:
        fail(f"Unexpected alpha byte count for {path.relative_to(ROOT)}")
    return width, height, alpha


def assert_pngs(registry: dict[str, Any], environment: dict[str, str]) -> None:
    for asset in registry["assets"]:
        project, name = asset["project"], asset["name"]
        for width in registry["sizes"]:
            path = OUT / project / f"{name}-{width}.png"
            actual_width, actual_height = png_size(path)
            if actual_width != width:
                fail(f"Wrong width for {path.relative_to(ROOT)}: {actual_width}")
            if asset["sizeMode"] == "square" and actual_height != width:
                fail(f"Square asset has wrong height: {path.relative_to(ROOT)}")
        path512 = OUT / project / f"{name}-512.png"
        width, height, alpha = alpha_plane(path512, environment)
        if asset.get("checkCorners"):
            corners = (
                alpha[0],
                alpha[width - 1],
                alpha[(height - 1) * width],
                alpha[-1],
            )
            if any(value != 0 for value in corners):
                fail(f"Opaque canvas corner in {path512.relative_to(ROOT)}: {corners}")
        if asset.get("checkCutout"):
            if alpha[250 * width + 192] != 0:
                fail("Elysola cutout sample (192,250) is not transparent")
            segments = []
            start = None
            for y in range(230, 270):
                opaque = alpha[y * width + 192] >= 128
                if opaque and start is None:
                    start = y
                elif not opaque and start is not None:
                    segments.append((start, y - 1))
                    start = None
            if start is not None:
                segments.append((start, 269))
            expected = [(234, 246), (255, 264)]
            if len(segments) != 2 or any(
                abs(actual - reference) > 1
                for segment, expected_segment in zip(segments, expected, strict=True)
                for actual, reference in zip(segment, expected_segment, strict=True)
            ):
                fail(f"Unexpected Elysola cutout segments: {segments}")


def assert_manifest(registry: dict[str, Any]) -> None:
    try:
        manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot read manifest: {error}") from error
    assets = {
        (project, name)
        for project, entry in manifest["projects"].items()
        for name in entry["assets"]
    }
    expected = {(asset["project"], asset["name"]) for asset in registry["assets"]}
    if assets != expected:
        fail(f"Manifest assets differ: expected {expected}, got {assets}")
    if any("overlay" in name for _, name in assets):
        fail("Overlay asset must not appear in manifest")


def main() -> None:
    registry = load_registry()
    environment = controlled_environment()
    assert_font(environment)
    assert_no_forbidden_constructs(registry)
    assert_manifest(registry)
    assert_pngs(registry, environment)
    subprocess.run(
        [sys.executable, str(ROOT / "main.py"), "--check"],
        check=True,
        env=environment,
        stdout=subprocess.DEVNULL,
    )
    print(
        "Validation passed: generated sources, renderer, font, PNG alpha, and manifest are consistent."
    )


if __name__ == "__main__":
    main()
