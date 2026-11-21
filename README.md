# Elysola Icon

Elysola 多项目品牌图标的源文件、生成器与多尺寸导出仓库，也是 [`icon-showcase`](../icon-showcase) 的资产上游。展示站通过 GitHub raw 读取本仓库提交的 `output/` 和 `output/manifest.json`，因此本地重新生成后还需提交并推送，线上才会更新。

## 真值与生成链

本仓库按图标类型使用两种真值链：

```text
Elysola 单色版 / 装饰版
geometry-kit/icon-geometry.json
  → projects/elysola/icon-mono.svg、icon-decorative.svg
  → output/elysola/*.png

Elysola 横排字标
projects/elysola/icon-mono.svg
  → projects/elysola/icon-text.svg
  → output/elysola/icon-text-*.png

Elysola 彩色主版 / 小尺寸版（手写）
projects/elysola/icon.svg、icon-small.svg
  → output/elysola/icon-*.png

Mailer / SleepyXposed / VectorLoom / WebHooker（手写）
projects/<project>/icon.svg、icon-small.svg、icon-mono.svg
  → output/<project>/*.png
```

`geometry-kit/icon-geometry.json` 是 Elysola 普通版与装饰版的唯一几何真值。由它生成的 SVG、横排字标 SVG 和 `output/` 下的全部文件都是派生产物，不应手工修改。

## 目录结构

```text
geometry-kit/              # Elysola 几何 JSON、生成器与说明
projects/<project>/        # 手写 SVG 或提交的派生 SVG
icons.json                 # 资产注册表、尺寸模式与验证开关
generate.py                # Elysola 专属 SVG 生成器
main.py / validate.py      # Vectorloom 兼容入口
output/<project>/          # 多尺寸 PNG 与 SVG 副本
output/manifest.json       # 展示站消费的资产清单
docs/                      # 统一方案与设计说明
```

当前注册的资产（每个项目都有彩色主版、小尺寸版和单色版；Elysola 另有装饰版与横排字标）：

| 项目 | 资产 | 真值类型 | 尺寸模式 |
| --- | --- | --- | --- |
| Elysola | `icon`、`icon-small`、`icon-mono` | 手写彩色主版 + 小尺寸版；单色版由 geometry kit 生成 | 正方形 |
| Elysola | `icon-decorative` | geometry | 正方形 |
| Elysola | `icon-text` | 派生字标 | 按宽度、保持比例 |
| Mailer / SleepyXposed / VectorLoom / WebHooker | `icon`、`icon-small`、`icon-mono` | 手写 SVG | 正方形 |

## 开发环境

推荐使用 Nix：

```bash
nix develop
```

开发 shell 通过 [VectorLoom](https://github.com/Elysola/VectorLoom) 提供通用声明式构建与验证，并提供 Python、uv、Ruff、Black、librsvg（`rsvg-convert`）、fontconfig、DejaVu 字体、ImageMagick 和 potrace。shellHook 会创建受控 fontconfig 配置，确保：

```text
DejaVu Sans Bold → DejaVuSans-Bold.ttf
```

这样横排字标不会被系统字体别名错误替换。构建脚本只使用 Python 标准库；SVG 渲染统一使用 `rsvg-convert`，不依赖 CairoSVG。

## 生成与验证

在 `nix develop` 中运行：

```bash
vectorloom build --config icons.json
vectorloom check --config icons.json
vectorloom validate --config icons.json
```

旧入口 `python3 main.py`、`python3 main.py --check` 和 `python3 validate.py` 仍保留兼容。

Vectorloom 读取 `icons.json`；`generate.py` 只保留 Elysola 专属几何与字标生成。统一流水线会：

1. 从 geometry JSON 生成 Elysola 普通版与装饰版 SVG；
2. 从当前普通版生成 `icon-text.svg`；
3. 用 `rsvg-convert` 生成 16、32、48、64、96、128、256、512 宽度的 PNG；
4. 保持 SVG 原始宽高比，非方形字标不会被拉伸成正方形；
5. 复制公开 SVG，并重写 `output/manifest.json`。

Vectorloom 会检查：

- DejaVu Sans Bold 精确字体匹配；
- 派生 SVG 重生成一致性；
- PNG 宽高、文件格式与画布透明度；
- Elysola 普通版的破晓镂空是真透明；
- SVG 不含不兼容的 `var(...)` 颜色；
- manifest 与 `icons.json` 完全一致；
- overlay 兼容版没有进入默认公开资产。

## 图标约定

- Elysola 的彩色主版与小尺寸版是手写 SVG：满版蓝色圆角底板 + 白色标志，小尺寸版做了光学校正；单色版与装饰版才来自 geometry kit。
- 五个项目的 `icon-mono.svg` 都是透明背景 + `currentColor`，不得内嵌固定 `color` 值，否则宿主主题化失效。
- 所有项目的彩色主版都是满版圆角底板 + 浅色标志 + 品牌强调色，与对应的小尺寸版结构一致，避免 32px 尺寸切换时图形突变。
- 镂空和负空间必须是真透明，不得用白色背景块冒充。
- geometry kit 的 overlay 版只适用于不支持 mask 的受限场景，不进入 `output/` 和 manifest。
- SVG 颜色不得使用 `var(...)`；需要主题色时使用 `currentColor`。
- 修改几何、字体、SVG 或注册表后必须全量重生成并运行验证。

## 新增项目或资产

1. 将手写 SVG 放入 `projects/<project>/`，或为生成型资产增加对应真值与生成逻辑；
2. 在 `icons.json` 登记项目、资产名、源路径、真值类型、尺寸模式和验证开关；
3. 根据图形特征补充专属验证（镂空、圆角、渐变或字体）；
4. 运行：

```bash
python3 main.py
python3 validate.py
```

5. 一并提交源、生成物与 `output/manifest.json`。
