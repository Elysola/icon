# Elysola 图标源仓库

本仓库存放 Elysola 各项目的品牌图标源文件与生成脚本，是多项目图标聚合存储，也是 `icon-showcase` 展示站的同步上游。展示站通过 GitHub raw 拉取本仓库的 `output/` 资产，因此本仓库的变更需推送后才对展示站可见。

## 目录结构

- `projects/<project>/`：各项目图标源文件（`*.svg`，Elysola 另含原始位图 `icon.png`）。
- `output/<project>/`：生成的多尺寸 PNG + SVG 副本，被展示站 `scripts/sync.mjs` 拉取。
- `output/manifest.json`：资产清单元数据（项目 → 资产 → 文件列表）。
- `main.py`：遍历 `projects/`，把每个 `*.svg` 导出为 `output/<project>/<name>-{16,32,48,64,96,128,256,512}.png`，并复制 SVG、生成 `manifest.json`。
- `main_text.py`：生成 Elysola 横排字标 SVG（`projects/elysola/icon-text*.svg`），ImageMagick + DejaVuSans-Bold。

## 已有项目

- `projects/elysola/`：Elysola 主图标，potrace 提取轮廓 + 手动垂直蓝渐变（`linearGradient id=g`，顶浅底深）。含 `icon.svg` / `icon.png`（1254×1254 原始栅格源）/ `icon-text.svg`。
- `projects/webhooker/`：WebHooker 图标，圆角矩形 + 白色 hook 符号（`#4f46e5`）。

## 环境

- Nix：`nix develop`（flake 提供 uv/cairo/librsvg/potrace/imagemagick），或 `direnv allow`。
- Python 依赖：cairosvg（`uv sync` 生成 `.venv`）。
- cairosvg 依赖 libcairo，运行前需 `export LD_LIBRARY_PATH=/nix/store/...cairo.../lib`；直接使用 `uv run main.py` 时 flake shellHook 已设置。

## 常用命令

- `uv run main_text.py`：重新生成 Elysola 字标 SVG 到 `projects/elysola/`。
- `uv run main.py`：导出所有项目到 `output/`，并写入 `output/manifest.json`。
- `bun run sync`（在 icon-showcase 仓库）：从本仓库拉取最新资产。

## 约定

- 提交需 GPG 签名（`git commit -S`）。
- 修改渐变/形状后须重新导出 `output/` 并推送，否则展示站同步到的仍是旧资产。
- 渐变方向保持垂直单调（顶 `#C8E0FD` → 底 `#3069C9`），不要引入环形或对角线分段。
- 新增项目：创建 `projects/<project>/icon.svg`，运行 `uv run main.py`。
