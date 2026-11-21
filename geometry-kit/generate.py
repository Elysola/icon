"""Elysola icon generator: icon-geometry.json -> SVG / Canvas JS / CSS.

Single source of truth: every output below is computed from the same
from/through/to arc data. No hand-written path data anywhere.
Usage: python3 generate.py [geometry.json] [outdir]   (defaults: ./icon-geometry.json ./dist)
Only Python standard library is used.
"""

import json
import math
import os
import sys


def circle3(p0, p1, p2):
    d = 2 * ((p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1]))
    a = p0[0] ** 2 + p0[1] ** 2
    b = p1[0] ** 2 + p1[1] ** 2
    e = p2[0] ** 2 + p2[1] ** 2
    ux = ((p2[1] - p0[1]) * (b - a) - (p1[1] - p0[1]) * (e - a)) / d
    uy = ((p1[0] - p0[0]) * (e - a) - (p2[0] - p0[0]) * (b - a)) / d
    return (ux, uy), math.hypot(p0[0] - ux, p0[1] - uy)


def arc_flags(p0, p1, p2):
    """Return (R, largeArc, sweep) for an SVG A command from->to through p1."""
    (cx, cy), r = circle3(p0, p1, p2)
    a0 = math.atan2(p0[1] - cy, p0[0] - cx)
    am = math.atan2(p1[1] - cy, p1[0] - cx)
    a2 = math.atan2(p2[1] - cy, p2[0] - cx)
    span_cw = (a2 - a0) % (2 * math.pi)
    mid_cw = (am - a0) % (2 * math.pi)
    if mid_cw <= span_cw:
        return r, (1 if span_cw > math.pi else 0), 1
    return r, (1 if (2 * math.pi - span_cw) > math.pi else 0), 0


def arc_points(p0, p1, p2, step_deg=3.0):
    """Sample the arc from->through->to as polyline points (excluding p0)."""
    (cx, cy), r = circle3(p0, p1, p2)
    a0 = math.atan2(p0[1] - cy, p0[0] - cx)
    am = math.atan2(p1[1] - cy, p1[0] - cx)
    a2 = math.atan2(p2[1] - cy, p2[0] - cx)
    span_cw = (a2 - a0) % (2 * math.pi)
    mid_cw = (am - a0) % (2 * math.pi)
    span = span_cw if mid_cw <= span_cw else span_cw - 2 * math.pi
    n = max(2, math.ceil(abs(math.degrees(span)) / step_deg))
    return [
        (cx + r * math.cos(a0 + span * i / n), cy + r * math.sin(a0 + span * i / n))
        for i in range(1, n + 1)
    ]


def outline_points(elements, step_deg=3.0):
    pts = [tuple(elements[0]["from"])]
    for e in elements:
        if e["type"] == "line":
            pts.append(tuple(e["to"]))
        else:
            pts.extend(arc_points(e["from"], e["through"], e["to"], step_deg))
    return pts


def f1(x):
    return f"{x:.1f}"


# ---------- SVG ----------
def svg_outline_d(elements):
    parts = [f"M {f1(elements[0]['from'][0])} {f1(elements[0]['from'][1])}"]
    for e in elements:
        if e["type"] == "line":
            parts.append(f"L {f1(e['to'][0])} {f1(e['to'][1])}")
        else:
            r, la, sw = arc_flags(e["from"], e["through"], e["to"])
            parts.append(
                f"A {f1(r)} {f1(r)} 0 {la} {sw} {f1(e['to'][0])} {f1(e['to'][1])}"
            )
    parts.append("Z")
    return " ".join(parts)


def svg_e_d(mod):
    s = mod["spine"]
    cr = s["cornerRadii"]
    x, y, w, h = s["x"], s["y"], s["w"], s["h"]
    d = (
        f"M {f1(x)} {f1(y+cr['tl'])} A {cr['tl']} {cr['tl']} 0 0 1 {f1(x+cr['tl'])} {f1(y)} "
        f"L {f1(x+w)} {f1(y)} L {f1(x+w)} {f1(y+h)} L {f1(x+cr['bl'])} {f1(y+h)} "
        f"A {cr['bl']} {cr['bl']} 0 0 1 {f1(x)} {f1(y+h-cr['bl'])} Z"
    )
    for b in mod["bars"]:
        cx = b["chordEnd"]
        d += (
            f" M {f1(b['x'])} {f1(b['y'])} L {f1(cx)} {f1(b['y'])} "
            f"A {b['endR']} {b['endR']} 0 0 1 {f1(cx)} {f1(b['y']+b['h'])} "
            f"L {f1(b['x'])} {f1(b['y']+b['h'])} Z"
        )
    return d


def render_svg(geo, variant, mode="mask"):
    """mode='mask' (default, standard only): real <mask> cutout - the cutout
    is genuinely transparent on any background and the file contains no
    CSS var(), so cairosvg / rsvg-convert both render it.
    mode='overlay': legacy background-colour cover, kept only for contexts
    that forbid <mask> (some print / mail pipelines). It paints an opaque
    #ffffff lens, so it is only correct on a white background. The colour
    is an explicit hex value - never var() - so cairosvg does not crash."""
    var = geo["variants"][variant]
    mp = var["mapTo512"]
    tx, ty = mp["translate"]
    sc = mp["scale"]
    mods = {m["id"]: m for m in var["modules"]}

    def path_of(mid):
        m = mods[mid]
        d = svg_e_d(m) if m["type"] == "e-letter" else svg_outline_d(m["elements"])
        return f'<path d="{d}"/>'

    body = []
    if variant == "decorative":
        for mid in ["E", "S", "sun", "horizon"]:
            body.append("  " + path_of(mid))
    elif mode == "mask":
        fw, fh = var["frame"]["width"], var["frame"]["height"]
        cut_d = svg_outline_d(mods["cutout"]["elements"])
        body.append(
            f'  <defs><mask id="elysola-cutout" maskUnits="userSpaceOnUse" x="0" y="0" width="{fw}" height="{fh}">'
            f'<rect x="0" y="0" width="{fw}" height="{fh}" fill="#ffffff"/>'
            f'<path d="{cut_d}" fill="#000000"/></mask></defs>'
        )
        body.append('  <g mask="url(#elysola-cutout)">')
        body.append("    " + path_of("E"))
        body.append("    " + path_of("S"))
        body.append("  </g>")
        body.append("  " + path_of("horizon"))
    else:  # overlay
        body.append("  " + path_of("E"))
        body.append("  " + path_of("S"))
        body.append(
            f'  <path class="elysola-cutout" fill="#ffffff" d="{svg_outline_d(mods["cutout"]["elements"])}"/>'
        )
        body.append("  " + path_of("horizon"))
    paths = "\n".join(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512" '
        f'fill="currentColor" role="img" aria-label="Elysola">\n'
        f'<g transform="translate({tx}, {ty}) scale({sc})">\n{paths}\n</g>\n</svg>\n'
    )


# ---------- Canvas JS ----------
CANVAS_JS_TEMPLATE = r"""// Generated by generate.py from icon-geometry.json - do not edit by hand.
// Pure Canvas 2D: only arc / lineTo / roundRect / clip-free basic geometry.
const ELYSOLA_GEOMETRY = __GEO_JSON__;

function _elysolaCircle(c, p0, p1, p2) {
  const d = 2*((p1[0]-p0[0])*(p2[1]-p0[1]) - (p2[0]-p0[0])*(p1[1]-p0[1]));
  const a = p0[0]*p0[0]+p0[1]*p0[1], b = p1[0]*p1[0]+p1[1]*p1[1], e = p2[0]*p2[0]+p2[1]*p2[1];
  const ux = ((p2[1]-p0[1])*(b-a) - (p1[1]-p0[1])*(e-a)) / d;
  const uy = ((p1[0]-p0[0])*(e-a) - (p2[0]-p0[0])*(b-a)) / d;
  const r = Math.hypot(p0[0]-ux, p0[1]-uy);
  const cross = (p1[0]-p0[0])*(p2[1]-p0[1]) - (p1[1]-p0[1])*(p2[0]-p0[0]);
  c.arc(ux, uy, r, Math.atan2(p0[1]-uy, p0[0]-ux), Math.atan2(p2[1]-uy, p2[0]-ux), cross < 0);
}
function _elysolaTrace(c, elements) {
  c.beginPath();
  c.moveTo(elements[0].from[0], elements[0].from[1]);
  for (const e of elements) {
    if (e.type === 'line') c.lineTo(e.to[0], e.to[1]);
    else _elysolaCircle(c, e.from, e.through, e.to);
  }
  c.closePath();
}
function _elysolaE(c, mod) {
  const s = mod.spine, cr = s.cornerRadii;
  c.beginPath();
  c.roundRect(s.x, s.y, s.w, s.h, [cr.tl, cr.tr, cr.br, cr.bl]);
  c.fill();
  for (const b of mod.bars) {
    c.beginPath();
    c.roundRect(b.x, b.y, b.chordEnd - b.x + b.endR, b.h, [0, b.endR, b.endR, 0]); // total width incl. cap
    c.fill();
  }
}
// Draws in LOCAL coordinates. Caller sets transform (mapTo512 or any scale)
// and fillStyle. variant: 'standard' | 'decorative'.
function drawElysola(c, variant, color) {
  const geo = ELYSOLA_GEOMETRY.variants[variant];
  const mods = {}; for (const m of geo.modules) mods[m.id] = m;
  c.fillStyle = color;
  if (variant === 'standard') {
    const off = document.createElement('canvas');
    off.width = geo.frame.width; off.height = geo.frame.height;
    const o = off.getContext('2d'); o.fillStyle = color;
    _elysolaE(o, mods.E); _elysolaTrace(o, mods.S.elements); o.fill();
    o.globalCompositeOperation = 'destination-out';
    _elysolaTrace(o, mods.cutout.elements); o.fill();
    o.globalCompositeOperation = 'source-over';
    c.drawImage(off, 0, 0); // under caller's current transform (local space)
    c.fillStyle = color;
    _elysolaTrace(c, mods.horizon.elements); c.fill();
  } else {
    _elysolaE(c, mods.E);
    _elysolaTrace(c, mods.sun.elements); c.fill();
    _elysolaTrace(c, mods.horizon.elements); c.fill();
    _elysolaTrace(c, mods.S.elements); c.fill();
  }
}
// Convenience: fit a canvas element to the 512 viewBox with DPR scaling.
function setupElysolaCanvas(canvas, variant, color, cssSize) {
  const dpr = window.devicePixelRatio || 1;
  canvas.style.width = cssSize + 'px'; canvas.style.height = cssSize + 'px';
  canvas.width = cssSize * dpr; canvas.height = cssSize * dpr;
  const c = canvas.getContext('2d');
  const mp = ELYSOLA_GEOMETRY.variants[variant].mapTo512;
  const k = (cssSize / 512) * dpr;
  c.setTransform(k, 0, 0, k, 0, 0);
  c.translate(mp.translate[0], mp.translate[1]); c.scale(mp.scale, mp.scale);
  drawElysola(c, variant, color);
}
"""


def render_canvas_js(geo):
    return CANVAS_JS_TEMPLATE.replace(
        "__GEO_JSON__", json.dumps(geo, ensure_ascii=False)
    )


# ---------- CSS ----------
def css_pct_polygon(elements, bbox, step_deg=3.0):
    x0, y0, x1, y1 = bbox
    pts = outline_points(elements, step_deg)
    return ", ".join(
        f"{(px-x0)/(x1-x0)*100:.2f}% {(py-y0)/(y1-y0)*100:.2f}%" for px, py in pts
    )


def module_bbox(elements):
    pts = outline_points(elements, 6.0)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def render_css(geo):
    out = [
        "/* Generated by generate.py from icon-geometry.json - do not edit by hand.",
        "   Pure CSS: no <svg>. S / horizon / sun use clip-path polygons sampled",
        "   from the same arc data (approximate - see README fidelity note).",
        "   Set --elysola-bg to your page background for the standard cutout. */",
    ]
    for variant, var in geo["variants"].items():
        W, H = var["frame"]["width"], var["frame"]["height"]
        mods = {m["id"]: m for m in var["modules"]}
        out.append(
            f".elysola-{variant} {{ position: relative; width: {W}px; height: {H}px; color: inherit; }}"
        )
        out.append(f".elysola-{variant} > * {{ position: absolute; }}")
        # E parts
        e = mods["E"]
        s = e["spine"]
        cr = s["cornerRadii"]
        out.append(
            f".elysola-{variant} .e-spine {{ left:{s['x']}px; top:{s['y']}px; width:{s['w']}px; height:{s['h']}px; "
            f"background: currentColor; border-radius: {cr['tl']}px {cr['tr']}px {cr['br']}px {cr['bl']}px; }}"
        )
        for i, b in enumerate(e["bars"]):
            tot = b["chordEnd"] - b["x"] + b["endR"]
            out.append(
                f".elysola-{variant} .e-bar{i} {{ left:{b['x']}px; top:{b['y']}px; width:{tot}px; height:{b['h']}px; "
                f"background: currentColor; border-radius: 0 {b['endR']}px {b['endR']}px 0; }}"
            )
        for mid in ["S", "sun", "horizon", "cutout"]:
            if mid not in mods:
                continue
            m = mods[mid]
            bx = module_bbox(m["elements"])
            bg = "var(--elysola-bg, #ffffff)" if mid == "cutout" else "currentColor"
            z = {"S": 1, "sun": 1, "cutout": 2, "horizon": 3}[mid]
            out.append(
                f".elysola-{variant} .m-{mid.lower()} {{ left:{bx[0]:.1f}px; top:{bx[1]:.1f}px; "
                f"width:{bx[2]-bx[0]:.1f}px; height:{bx[3]-bx[1]:.1f}px; background: {bg}; z-index: {z}; "
                f"clip-path: polygon({css_pct_polygon(m['elements'], bx)}); }}"
            )
    return "\n".join(out) + "\n"


def render_css_html(geo):
    parts = ['<link rel="stylesheet" href="elysola.css">']
    for variant in geo["variants"]:
        var = geo["variants"][variant]
        mods = {m["id"]: m for m in var["modules"]}
        inner = ['<div class="e-spine"></div>'] + [
            f'<div class="e-bar{i}"></div>' for i in range(len(mods["E"]["bars"]))
        ]
        for mid in ["S", "sun", "cutout", "horizon"]:
            if mid in mods:
                inner.append(f'<div class="m-{mid.lower()}"></div>')
        parts.append(f'<div class="elysola-{variant}">' + "".join(inner) + "</div>")
    return "\n".join(parts) + "\n"


def render_preview(geo):
    return (
        '<!DOCTYPE html>\n<html lang="zh"><head><meta charset="utf-8">'
        "<title>Elysola geometry kit preview</title>"
        '<link rel="stylesheet" href="elysola.css">'
        "<style>body{font-family:system-ui;background:#0B2A4A;color:#fff}section{margin:24px}img,canvas{background:#fff}</style>"
        "</head><body><h1>Elysola - one geometry, three renderers</h1>"
        '<section><h2>SVG</h2><img src="elysola-standard.svg" width="256"> <img src="elysola-decorative.svg" width="256"></section>'
        '<section><h2>Canvas</h2><canvas id="cs"></canvas> <canvas id="cd"></canvas></section>'
        '<section><h2>CSS</h2><div style="background:#fff;color:#0B2A4A;padding:8px">'
        + render_css_html(geo).replace('<link rel="stylesheet" href="elysola.css">', "")
        + "</div></section>"
        '<script src="elysola-canvas.js"></script>'
        "<script>setupElysolaCanvas(document.getElementById('cs'),'standard','#0B2A4A',256);"
        "setupElysolaCanvas(document.getElementById('cd'),'decorative','#0B2A4A',256);</script>"
        "</body></html>\n"
    )


def main():
    src = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "icon-geometry.json"
        )
    )
    outdir = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
    )
    try:
        with open(src, encoding="utf-8") as source_file:
            geo = json.load(source_file)
        os.makedirs(outdir, exist_ok=True)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Cannot prepare geometry generation: {error}") from error
    files = {
        "elysola-standard.svg": render_svg(geo, "standard", "mask"),
        "elysola-standard-overlay.svg": render_svg(geo, "standard", "overlay"),
        "elysola-decorative.svg": render_svg(geo, "decorative"),
        "elysola-canvas.js": render_canvas_js(geo),
        "elysola.css": render_css(geo),
        "elysola-css.html": render_css_html(geo),
        "preview.html": render_preview(geo),
    }
    for name, content in files.items():
        path = os.path.join(outdir, name)
        try:
            with open(path, "w", encoding="utf-8") as output_file:
                output_file.write(content)
        except OSError as error:
            raise RuntimeError(
                f"Cannot write generated file {path}: {error}"
            ) from error
        print("generated", path)


if __name__ == "__main__":
    main()
