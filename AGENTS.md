# Elysola 图标源仓库

本仓库存放 Elysola 各项目的品牌图标源文件与生成脚本，是多项目图标聚合存储，也是 `icon-showcase` 展示站的同步上游。展示站通过 GitHub raw 拉取本仓库的 `output/` 资产，因此本仓库的变更需推送后才对展示站可见。

## 目录结构

- `projects/<project>/`：各项目图标源文件（`*.svg`）。
- `output/<project>/`：生成的多尺寸 PNG + SVG 副本，被展示站 `scripts/sync.mjs` 拉取。
- `output/manifest.json`：资产清单元数据（项目 → 资产 → 文件列表）。
- `main.py`：遍历 `projects/`，把每个 `*.svg` 导出为 `output/<project>/<name>-{16,32,48,64,96,128,256,512}.png`，并复制 SVG、生成 `manifest.json`。
- `main_symbol.py`：参数化生成 Elysola 标志 SVG（`projects/elysola/icon{,-white,-black,-small}.svg`），几何与配色的唯一来源。
- `main_text.py`：生成 Elysola 横排字标 SVG（`projects/elysola/icon-text*.svg`），标志从 `main_symbol.py` 导入，ImageMagick + DejaVuSans-Bold。

## 已有项目

- `projects/elysola/`：Elysola 标志「A World Yet to Be」：椭圆扁拱门 + 实心梯形光束 + 底部开口的渐细圆环，透明底。含 `icon.svg`（渐变主版）/ `icon-white.svg` / `icon-black.svg`（单色）/ `icon-small.svg`（16–48px 用，线条加粗）/ `icon-text.svg`。均由脚本生成，不要手改。
- `projects/webhooker/`：WebHooker 图标，圆角矩形 + 白色 hook 符号（`#4f46e5`）。

## 环境

- Nix：`nix develop`（flake 提供 uv/cairo/librsvg/potrace/imagemagick），或 `direnv allow`。
- Python 依赖：cairosvg（`uv sync` 生成 `.venv`）。
- cairosvg 依赖 libcairo，运行前需 `export LD_LIBRARY_PATH=/nix/store/...cairo.../lib`；直接使用 `uv run main.py` 时 flake shellHook 已设置。

## 常用命令

- `uv run main_symbol.py`：重新生成 Elysola 标志 SVG 到 `projects/elysola/`。
- `uv run main_text.py`：重新生成 Elysola 字标 SVG 到 `projects/elysola/`（标志改动后也要重跑）。
- `uv run main.py`：导出所有项目到 `output/`，并写入 `output/manifest.json`。
- `bun run sync`（在 icon-showcase 仓库）：从本仓库拉取最新资产。

## 约定

- 提交需 GPG 签名（`git commit -S`）。
- 修改渐变/形状后须重新导出 `output/` 并推送，否则展示站同步到的仍是旧资产。
- Elysola 标志使用单一径向渐变（`radialGradient id=g`，中心在门口 `512,640`：`#F2FCFF` → `#BDEFFC` → `#A99EF3`），门框、光束、圆环共用同一渐变，不要拆成各自的渐变。设计底色为午夜深蓝 `#0A1130`。
- 门使用对称椭圆扁拱，弧高 56，弧线以垂直切线接入两侧门柱；不要改成标准半圆拱、普通圆角矩形或尖拱。光束是几何梯形（不是射线或三角聚光）；圆环开口水平截断。
- 新增项目：创建 `projects/<project>/icon.svg`，运行 `uv run main.py`。
