# Elysola Icon

Elysola 多项目品牌图标的源文件与多尺寸导出聚合仓库。

## 目录结构

```
projects/<project>/     # 各项目图标源文件（SVG，可附原始位图）
output/<project>/       # 生成的多尺寸 PNG + SVG 副本
output/manifest.json    # 资产清单元数据
```

- `projects/elysola/`：Elysola 主品牌（`icon.svg` / `icon-white.svg` / `icon-black.svg` / `icon-small.svg` / `icon-text.svg`）
- `projects/webhooker/`：WebHooker（`icon.svg`）
- `main.py`：遍历 `projects/`，将每个 `*.svg` 导出到 `output/<project>/` 并生成 `manifest.json`
- `main_symbol.py`：生成 Elysola 标志 SVG（`projects/elysola/icon*.svg`）
- `main_text.py`：生成 Elysola 横排字标 SVG（`projects/elysola/icon-text*.svg`）
- `flake.nix` / `pyproject.toml`：Nix + uv 开发环境

## 环境

```bash
nix develop        # 提供 uv / cairo / librsvg / potrace / imagemagick
```

或直接使用已有的 `uv` 虚拟环境（含 `cairosvg`）。

## 生成全部项目资产

```bash
uv run main_symbol.py # 先重新生成标志 SVG（仅 Elysola）
uv run main_text.py   # 再生成字标 SVG（仅 Elysola）
uv run main.py        # 导出所有项目到 output/，并写入 manifest.json
```

`main.py` 对每个 `projects/<project>/*.svg` 输出 `output/<project>/<name>-{16,32,48,64,96,128,256,512}.png`，PNG 宽度为尺寸值、保持比例，同时复制一份 `<name>.svg`。

## Elysola 标志

「A World Yet to Be」：椭圆扁拱门、从门口投出的实心梯形光束、底部开口的渐细圆环。门顶采用弧高 56 的对称椭圆弧，并以垂直切线接入门柱。几何与配色全部在 `main_symbol.py` 中参数化定义（1024 坐标系），输出透明底 SVG：

| 文件 | 用途 |
|---|---|
| `icon.svg` | 主版本，径向渐变 `#F2FCFF` → `#BDEFFC` → `#A99EF3`，适合深色底（设计底色 `#0A1130`） |
| `icon-white.svg` / `icon-black.svg` | 单色版本 |
| `icon-small.svg` | 16–48px 专用：裁切更紧、门框和圆环加粗 |

## 带文字图标（图标 + 字标）

Elysola 横排 logo lockup，字标为 `Elysola`，文字使用 DejaVu Sans Bold，填充淡紫 `#A99EF3`。

- `main_text.py`：从 `main_symbol.py` 导入标志，配合 ImageMagick 测量文字生成
- `projects/elysola/icon-text.svg`：矢量 lockup
- `output/elysola/icon-text-{尺寸}.png`：由 `main.py` 导出

## 新增项目

1. 创建 `projects/<project>/icon.svg`
2. 运行 `uv run main.py`
