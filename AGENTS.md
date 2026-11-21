# Elysola 图标源仓库

本仓库存放 Elysola 各项目的品牌图标源文件与生成脚本，是多项目图标聚合存储，也是 `icon-showcase` 展示站的同步上游。展示站通过 GitHub raw 拉取本仓库的 `output/` 资产，因此本仓库的变更需推送后才对展示站可见。

## 目录结构

- `geometry-kit/`：Elysola 几何唯一真值（`icon-geometry.json`）及生成器；普通版与装饰版 SVG 不得手改。
- `projects/<project>/`：手写 SVG 或由统一构建生成的 SVG；Elysola 另含原始位图 `icon.png`。
- `icons.json`：全部资产的注册表、尺寸模式与专属断言开关。
- `output/<project>/`：由统一流水线生成的多尺寸 PNG + SVG 副本，被展示站 `scripts/sync.mjs` 拉取。
- `output/manifest.json`：资产清单元数据（项目 → 资产 → 文件列表）；overlay 版不进入 manifest。
- `generate.py`：仅负责 Elysola 专属几何 SVG 与横排字标生成。
- `main.py` / `validate.py`：兼容入口，实际调用独立项目 Vectorloom。
- VectorLoom：`https://github.com/Elysola/VectorLoom`，提供注册表解析、rsvg 渲染、PNG alpha 解码、manifest 和无副作用 check。

## 已有项目

- `projects/elysola/`：Elysola 单色图标（`currentColor`），含 geometry kit 生成的 `icon.svg` / `icon-decorative.svg`、派生的 `icon-text.svg`，以及 1254×1254 原始栅格 `icon.png`。旧脚本中的渐变常量从未生效，Elysola 图标没有渐变。
- `projects/mailer/`：Mailer 图标，SVG 内定义蓝色线性渐变。
- `projects/webhooker/`：WebHooker 图标，圆角矩形 + 白色 hook 符号（`#4f46e5`）。

## 真值与资产注册

- Elysola 普通版/装饰版：`geometry-kit/icon-geometry.json → projects/elysola/icon*.svg → output/elysola/*`。
- Elysola 横排字标：当前生成的 `icon.svg → icon-text.svg → output/elysola/icon-text-*`。
- Mailer/WebHooker：手写 `projects/<project>/icon.svg → output/<project>/icon-*`。
- 新增或删除公开资产必须同步修改 `icons.json`；不要依赖目录遍历自动公开文件。
- `sizeMode: square` 的 PNG 宽高相等；`sizeMode: by-width` 只固定宽度，高度按 viewBox 比例派生。

## 环境

- Nix：`nix develop`（flake 提供 uv/librsvg/fontconfig/DejaVu/Imagemagick 等），或 `direnv allow`。
- shellHook 生成受控 `FONTCONFIG_FILE`，确保 `DejaVu Sans:bold` 精确命中 `DejaVuSans-Bold.ttf`，而不是系统别名字体。
- Python 构建仅使用标准库；SVG 渲染统一调用 `rsvg-convert`，不允许重新引入 cairosvg。

## 常用命令

以下构建命令均在 `nix develop` 内运行：

- `vectorloom build --config icons.json`：运行项目生成器，导出全部 PNG，并写入 `output/manifest.json`。
- `vectorloom check --config icons.json`：在临时目录重建并逐字节比较，不修改 `output/`。
- `vectorloom validate --config icons.json`：执行字体、透明度、PNG 尺寸与 manifest 验收。
- `python3 main.py` / `python3 main.py --check` / `python3 validate.py`：兼容旧入口。
- `ruff check main.py main_text.py validate.py geometry-kit/generate.py`：Python 静态检查。
- `black --fast --check main.py validate.py geometry-kit/generate.py`：格式检查。
- `bun run sync`（在 icon-showcase 仓库）：从本仓库拉取最新资产。

## 约定

- 提交需 GPG 签名（`git commit -S`）。
- 修改几何、SVG、字体或注册表后须重新生成 `output/` 并推送，否则展示站同步到的仍是旧资产。
- 生成文件包括 `projects/elysola/icon.svg`、`icon-decorative.svg`、`icon-text.svg` 与全部 `output/`；不得手改。
- 修改 Elysola 图形只能改 `geometry-kit/icon-geometry.json` 或生成器；修改后运行统一流水线。
- 镂空必须保留真透明；禁止用背景色覆盖版作为默认产物。overlay 兼容版不得复制进 `output/`、不得写入 manifest。
- SVG 禁止使用 `var(...)` 颜色；主题化图标使用 `currentColor`。
- 字标字体必须由受控 fontconfig 解析为 `DejaVuSans-Bold.ttf`，不得依赖系统默认字体或 glob 猜路径。
- 新增项目：创建 `projects/<project>/icon.svg`、登记 `icons.json`、补相应声明式断言，再运行 Vectorloom build/check。
- 通用能力应提交到 Vectorloom；本仓库只保留品牌专属生成逻辑和配置。
- 发布前至少运行 `vectorloom check --config icons.json`、Ruff、Black 和 `git diff --check`。
