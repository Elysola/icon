"""生成 Elysola 主图标 SVG 到 projects/elysola/。

标志「A World Yet to Be」：椭圆扁拱门 + 实心梯形光束 + 底部开口的渐细圆环。
几何在 1024×1024 坐标系中定义，输出时用 viewBox 裁到标志周围。
"""

ICON_DIR = "projects/elysola"

CX = CY = 512
SHIFT_Y = -10.0  # 让标志的视觉外框在 1024 画布内上下居中
RING_CUT = 803.7  # 圆环在此 y 处水平截断，形成底部开口

# 门：内宽 156（半宽 78），顶 y=253，底 y=599；椭圆扁拱高 56
DOOR_HALF, DOOR_TOP, DOOR_BOTTOM = 78, 253, 599
DOOR_ARCH_RISE = 56
# 光束：y=621 → 886，顶部半宽等于门洞半宽，每向下 1 单位每侧外扩 0.30
BEAM_TOP, BEAM_BOTTOM, BEAM_SLOPE = 621, 886, 0.30

GRADIENT = (
    '<radialGradient id="g" cx="512" cy="640" r="470" gradientUnits="userSpaceOnUse">'
    '<stop offset="0" stop-color="#F2FCFF"/>'
    '<stop offset="0.38" stop-color="#BDEFFC"/>'
    '<stop offset="1" stop-color="#A99EF3"/>'
    "</radialGradient>"
)

VIEWBOX_MAIN = (112, 112, 800, 800)
VIEWBOX_SMALL = (136, 136, 752, 752)  # 小尺寸版裁得更紧


def gate(t):
    """等厚椭圆扁拱门：弧线在两侧以垂直切线接入门柱。"""
    outer_half = DOOR_HALF + t
    outer_join = DOOR_TOP + DOOR_ARCH_RISE
    inner_top = DOOR_TOP + t
    inner_rise = DOOR_ARCH_RISE - t
    return (
        f"M{CX - outer_half},{DOOR_BOTTOM}V{outer_join}"
        f"A{outer_half},{DOOR_ARCH_RISE} 0 0 1 {CX},{DOOR_TOP}"
        f"A{outer_half},{DOOR_ARCH_RISE} 0 0 1 {CX + outer_half},{outer_join}"
        f"V{DOOR_BOTTOM}H{CX + DOOR_HALF}V{outer_join}"
        f"A{DOOR_HALF},{inner_rise} 0 0 0 {CX},{inner_top}"
        f"A{DOOR_HALF},{inner_rise} 0 0 0 {CX - DOOR_HALF},{outer_join}"
        f"V{DOOR_BOTTOM}Z"
    )


def _half(y):
    return DOOR_HALF + (y - BEAM_TOP) * BEAM_SLOPE


def _trap(y0, y1):
    return (
        f"M{CX - _half(y0):.1f},{y0:.1f}H{CX + _half(y0):.1f}"
        f"L{CX + _half(y1):.1f},{y1:.1f}H{CX - _half(y1):.1f}Z"
    )


def beam(steps, gap):
    h = (BEAM_BOTTOM - BEAM_TOP - (steps - 1) * gap) / steps
    return "".join(
        _trap(BEAM_TOP + i * (h + gap), BEAM_TOP + i * (h + gap) + h)
        for i in range(steps)
    )


def ring(r_outer, r_inner, drop):
    """外圆与下移 drop 的内圆做 evenodd 差集：顶部最粗，向底部渐细。"""
    def circle(r, dy):
        return f"M{CX - r},{CY + dy}a{r},{r} 0 1 0 {2 * r},0a{r},{r} 0 1 0 {-2 * r},0Z"

    return circle(r_outer, 0) + circle(r_inner, drop)


# 主版本：门框 24，实心光束，圆环顶 20 / 两侧 15 / 开口约 11
MAIN = {"t": 24, "steps": 1, "gap": 0, "ring": (352.5, 337.5, 5), "viewbox": VIEWBOX_MAIN}
# 小尺寸版本（16–48px）：门框 40，圆环加粗
SMALL = {"t": 40, "steps": 1, "gap": 0, "ring": (364, 330, 4), "viewbox": VIEWBOX_SMALL}


def symbol_defs(gradient=True):
    """<defs> 内容；clipPath id=c，渐变 id=g。"""
    clip = f'<clipPath id="c"><rect width="1024" height="{RING_CUT}"/></clipPath>'
    return clip + (GRADIENT if gradient else "")


def symbol_body(fill, spec=MAIN):
    """标志本体（1024 坐标系），可嵌入其他 SVG。"""
    return (
        f'<g transform="translate(0 {SHIFT_Y})" fill="{fill}" fill-rule="evenodd">\n'
        f'<path d="{gate(spec["t"])}"/>\n'
        f'<path d="{beam(spec["steps"], spec["gap"])}"/>\n'
        f'<path d="{ring(*spec["ring"])}" clip-path="url(#c)"/>\n'
        "</g>"
    )


def build_svg(fill, spec=MAIN, title="Elysola"):
    x, y, w, h = spec["viewbox"]
    gradient = fill == "url(#g)"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"
 viewBox="{x} {y} {w} {h}" preserveAspectRatio="xMidYMid meet" role="img">
<title>{title}</title>
<defs>{symbol_defs(gradient)}</defs>
{symbol_body(fill, spec)}
</svg>
'''


OUTPUTS = {
    "icon": ("url(#g)", MAIN),
    "icon-white": ("#FFFFFF", MAIN),
    "icon-black": ("#000000", MAIN),
    "icon-small": ("url(#g)", SMALL),
}


def main():
    for name, (fill, spec) in OUTPUTS.items():
        path = f"{ICON_DIR}/{name}.svg"
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(build_svg(fill, spec))
        except OSError as exc:
            raise RuntimeError(f"Failed to write generated SVG: {path}") from exc
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
