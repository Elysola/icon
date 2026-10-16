# Elysola Icon

Elysola 多项目品牌图标的源文件与多尺寸导出聚合仓库。

## 目录结构

```
projects/<project>/     # 各项目图标源文件（SVG，可附原始位图）
output/<project>/       # 生成的多尺寸 PNG + SVG 副本
output/manifest.json    # 资产清单元数据
```

- `projects/elysola/`：Elysola 主品牌（`icon.svg` / `icon.png` / `icon-text.svg`）
- `projects/webhooker/`：WebHooker（`icon.svg`）
- `main.py`：遍历 `projects/`，将每个 `*.svg` 导出到 `output/<project>/` 并生成 `manifest.json`
- `main_text.py`：生成 Elysola 横排字标 SVG（`projects/elysola/icon-text*.svg`）
- `flake.nix` / `pyproject.toml`：Nix + uv 开发环境

## 环境

```bash
nix develop        # 提供 uv / cairo / librsvg / potrace / imagemagick
```

或直接使用已有的 `uv` 虚拟环境（含 `cairosvg`）。

## 生成全部项目资产

```bash
uv run main_text.py   # 先重新生成字标 SVG（仅 Elysola）
uv run main.py        # 导出所有项目到 output/，并写入 manifest.json
```

`main.py` 对每个 `projects/<project>/*.svg` 输出 `output/<project>/<name>-{16,32,48,64,96,128,256,512}.png`，PNG 宽度为尺寸值、保持比例，同时复制一份 `<name>.svg`。

## 重新生成 Elysola 主图标 SVG

矢量轮廓由 `potrace` 从位图提取，再替换为蓝渐变填充：

```bash
magick projects/elysola/icon.png -alpha extract -threshold 30% -negate shape.pbm
potrace shape.pbm -s --opaque --alphamax 1 --turdsize 2   # 得干净轮廓，替换 fill 为渐变
```

## 带文字图标（图标 + 字标）

Elysola 横排 logo lockup，字标为 `Elysola`，文字使用 DejaVu Sans Bold，填充品牌蓝 `#1E63CE`。

- `main_text.py`：用 `projects/elysola/icon.svg` 的轮廓配合 ImageMagick 生成
- `projects/elysola/icon-text.svg`：矢量 lockup
- `output/elysola/icon-text-{尺寸}.png`：由 `main.py` 导出

## 新增项目

1. 创建 `projects/<project>/icon.svg`
2. 运行 `uv run main.py`
