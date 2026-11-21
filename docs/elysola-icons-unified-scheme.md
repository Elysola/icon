# Elysola 图标规范与统一流水线

## 资产体系

Elysola 不再用一份透明单色 SVG 覆盖所有场景。不同尺寸、背景和版式应选择对应资产：

| 资产 | 文件 | 用途 |
| --- | --- | --- |
| 默认主图标 | `projects/elysola/icon.svg` | 网站卡片、应用图标、社交头像、48px 及以上的常规展示 |
| 小尺寸图标 | `projects/elysola/icon-small.svg` | 16px、32px、favicon、紧凑导航和小型状态区域 |
| 单色标志 | `projects/elysola/icon-mono.svg` | 内联 SVG、单色印刷、由宿主明确控制前景色的界面 |
| 装饰标志 | `projects/elysola/icon-decorative.svg` | 大尺寸品牌装饰、海报和非功能性视觉，不用作应用图标 |
| 横排字标 | `projects/elysola/icon-text.svg` | 页眉、品牌署名和空间充足的横向版式 |

## 选择规则

### 默认使用 `icon`

没有特殊要求时使用彩色 `icon.svg` 或对应 PNG。它使用蓝色圆角底板和白色标志，在浅色、深色及复杂背景上都有稳定对比度。

适用场景：

- 产品卡片和项目列表；
- GitHub、社交平台和聊天机器人头像；
- PWA、桌面应用和移动应用图标；
- Open Graph 图片中的品牌图标；
- 48px 及以上的独立图标展示。

不要通过 CSS 给该资产重新着色，也不要移除其底板。

### 16px 和 32px 改用 `icon-small`

小尺寸版经过光学校正，放大并加粗了 ES，简化了容易被抗锯齿吞掉的细节。以下场景必须使用它：

- 16px、32px PNG；
- 浏览器 favicon；
- 紧凑导航、菜单、标签和小按钮；
- 图标实际显示尺寸不超过 32 CSS px 的位置。

VectorLoom 已自动执行尺寸切换：正式 `output/elysola/icon-16.png` 和 `icon-32.png` 来自 `icon-small.svg`；48px 及以上来自 `icon.svg`。使用仓库生成的 PNG 时无需手动选择源文件。

SVG 消费方不会自动按显示尺寸切换。若直接引用 SVG，应用应通过 `<picture>`、媒体条件或组件逻辑在不超过 32px 时选择 `icon-small.svg`。

### 需要主题着色时改用 `icon-mono`

单色版透明且使用 `currentColor`，只适用于宿主明确控制颜色的场景：

- 内联到 HTML/组件中的 SVG；
- 浅色背景上的深色单色标志；
- 深色背景上的白色或浅色标志；
- 单色印刷、压印、激光雕刻和水印。

推荐颜色：

```css
.elysola-mark { color: #172033; }
.dark .elysola-mark { color: #f5f7fb; }
```

`currentColor` 只有内联 SVG 或组件化 SVG 才能可靠继承。不要用普通 `<img src="icon-mono.svg">` 指望它继承父元素颜色；这种用法通常会回退为黑色。无法内联时，应使用彩色默认图标，或由消费方生成固定颜色版本。

单色版不适合 favicon、头像或无法控制背景的外部平台。

### 横向空间充足时使用 `icon-text`

横排字标用于需要同时表达图形与名称的场景：

- 网站页眉和品牌导航；
- 合作伙伴页与赞助署名；
- 文档首页和演示文稿标题；
- 横向品牌锁定组合。

字标是按宽度驱动的非正方形资产。只设置目标宽度，高度必须由 viewBox 比例派生；禁止同时强制相同宽高。显示空间狭窄或高度低于约 32px 时，优先使用方形主图标或小尺寸图标。

### `icon-decorative` 只用于大尺寸装饰

装饰版保留更舒展的几何关系，适合 Hero、海报、背景图形和品牌展示。它不具备统一底板，也未针对小尺寸优化，因此不得用于 favicon、应用图标、头像、按钮或紧凑导航。

## 网站使用建议

- 页眉：空间充足时使用 `icon-text`；移动端或紧凑页眉使用彩色 `icon`。
- favicon：使用仓库生成的 `icon-16.png`、`icon-32.png` 和更高分辨率彩色 PNG。
- 深色模式：默认彩色图标无需切换；单色版必须切换为浅色前景。
- Hero：可使用大尺寸 `icon`；需要弱化、铺底或动态着色时才使用 `icon-mono` 或 `icon-decorative`。
- 外部平台：默认上传彩色 PNG，不上传依赖 `currentColor` 的 SVG。

## 真值链

- Elysola 单色普通版与装饰版：`geometry-kit/icon-geometry.json → icon-mono.svg / icon-decorative.svg`。
- Elysola 彩色主版和小尺寸版：品牌专属手写 SVG，分别为 `icon.svg` 与 `icon-small.svg`。
- Elysola 横排字标：由 `icon-mono.svg` 与锁定字体派生，避免把彩色方形底板嵌入字标。
- 其他产品：各自的手写主版、小尺寸版和单色版 SVG。
- `output/` 中的 SVG 副本、PNG 和 manifest 均为生成物，不得手改。

## 统一流水线

- `icons.json` 登记全部资产、尺寸模式、尺寸特定源和断言。
- `generate.py` 运行 geometry kit，并从单色普通版生成横排字标。
- VectorLoom 使用 `rsvg-convert` 渲染，主图标在 16/32px 自动改用小尺寸源。
- 渲染只传目标宽度，高度由 viewBox 比例派生；text 版不得拉伸成正方形。
- overlay 版只留在 kit 的临时产物中，不复制到 `output/`，不写入 manifest。

## 字体锁定

受控 fontconfig 必须将 `DejaVu Sans:style=Bold` 精确解析为 `DejaVuSans-Bold.ttf`。仅安装 DejaVu 不足以保证命中正确字体。

## 验证与回归

同一受控环境重跑必须逐字节一致。升级 librsvg、字体、几何或尺寸选择规则时，需重新评审视觉差异并全量生成。

核心验收包括：

- 字体精确命中 `DejaVuSans-Bold.ttf`；
- `icon-16.png` 和 `icon-32.png` 来自小尺寸 SVG；
- `icon-48.png` 及以上来自默认主 SVG；
- 彩色主图标和小尺寸图标的圆角外部保持透明；
- 单色版和装饰版的负空间保持真透明；
- text 版保持原始宽高比；
- SVG 不出现 `var(...)`；
- overlay 不进入 manifest；
- `vectorloom check --config icons.json` 与 `vectorloom validate --config icons.json` 全部通过。
