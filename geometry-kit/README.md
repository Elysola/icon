# Elysola 通用几何数据与生成器

一份数据，生成全部产物。图标只存一份几何中间数据 `icon-geometry.json`，
SVG、Canvas、CSS 都由 `generate.py` 从这份数据机械生成，不存在第二份手写轮廓。

## 包内容

| 文件 | 说明 |
| --- | --- |
| `icon-geometry.json` | 唯一数据源：双版本（standard / decorative）的坐标系、映射、共用参数与全部模块几何 |
| `generate.py` | 生成器（纯 Python 标准库）：读 JSON，产出 `dist/` 下全部文件 |
| `validate.py` | 验收脚本（需 Pillow + rsvg-convert 或 cairosvg）：用外部渲染器渲染生成版与内嵌原稿 SVG 做像素比对（IoU、边界 chamfer、切槽 alpha、E 圆角采样、cairosvg 崩溃检查），生成 `VALIDATION.md` |
| `VALIDATION.md` | 本次生成的实测验收报告 |
| `dist/elysola-standard.svg` | 512×512 SVG（仅 M / L / A / Z + 一个 `<mask>`）：**mask 版为默认版**，切槽是真透明、与背景无关，且不含 CSS `var()`，cairosvg / rsvg 均可渲染 |
| `dist/elysola-standard-overlay.svg` | 旧的背景色覆盖版，仅供禁止 `<mask>` 的场景（部分打印 / 邮件管线）；切槽为显式 `#ffffff` 不透明覆盖，只在白底上正确，不要放进 cairosvg 驱动的 PNG 流水线当透明图用 |
| `dist/elysola-decorative.svg` | 512×512 SVG（仅 M / L / A / Z，无 mask、无贝塞尔） |
| `dist/elysola-canvas.js` | 原生 Canvas 2D 实现：`drawElysola(ctx, variant, color)`（局部坐标）与 `setupElysolaCanvas(canvas, variant, color, cssSize)`（含 DPR 适配） |
| `dist/elysola.css` + `elysola-css.html` | 纯 CSS 实现（零 svg）与引用片段 |
| `dist/preview.html` | 三种渲染并排预览页 |

## 数据格式

- 每个版本有自己的局部坐标系（standard 280×140、decorative 360×140）与到 512 画布的映射
  `mapTo512 = {translate, scale}`：standard 为 translate(32, 136.8) scale(1.6)，
  decorative 为 translate(36.3, 169.3) scale(1.22)。
- 共用参数：`t=18, r=9, r0=6, g=6, R_sun=38`。
- 图元只有四类：`e-letter`（脊柱圆角矩形 + 胶囊横画）、`outline`（由 `line` / `arc`
  元素首尾相接的闭合轮廓）、以及带 `role` 的透镜轮廓（地平线、切槽）。
- **每段圆弧统一存 `from / through / to` 三点**，圆心、半径 `R`、圆心角 `thetaDeg`
  由三点定圆公式派生，只作标注记录；所有生成器都从三点作弧，
  因此 SVG 的 `A` 命令、Canvas 的 `arc`、CSS 的采样多边形天然同源。
- S 每版 22 个轮廓元素：直线端面 + 10 段圆弧 + 直线端面 + 10 段圆弧，
  起点、顺序、闭合与 nonzero 填充在数据中写死。
- E：横画分开存直线段终点 `chordEnd` 与端帽半径 `endR`，视觉末端为
  `chordEnd + endR`（与原稿 `H … A r` 的语义一致：直线到 chordEnd，半圆
  端帽再向外鼓出 endR），E 的组合宽度为 `(chordEnd + endR) − spine.x`。
  standard 三横 chordEnd 124/114/124、组合宽 91/81/91、视觉末端 133/123/133；
  decorative chordEnd 104/86/104、组合宽 87/68/87、视觉末端 113/94/113
  （中横高 16、端半径 8）。
- E 横画起点（v1.2 修正）：`bars[].x = spine.x + cornerRadii.tl`
  （standard 48、decorative 32），**不得从 spine.x 起画**。横画左端是直角，
  若从脊柱最左缘起画，会把脊柱左上 / 左下 r6 圆角填成直角（原稿是单一
  轮廓，顶横上缘从 x=48 起、底横下缘回到 x=48，圆角归脊柱）。内缩后
  x=spine.x..bars.x 一段由脊柱自身供给，横画自身的宽为
  `chordEnd − bars.x + endR`（standard 85/75/85、decorative 81/62/81），
  末端与组合宽不变。
- 切槽（standard）：按原稿遮罩重算。原稿遮罩黑形为 Q 透镜（端点 (24,96)/(256,96)，
  上顶点 (140,69)、下顶点 (140,73.5)）加 `stroke-width: 6` 描边；等效轮廓即该透镜
  按半宽 3 法向外扩：上弧过 (22.73,93.28)/(140,66)/(257.27,93.28)，R=265.7、
  圆心 (140,331.7)；下弧过 (254.91,98.8)/(140,76.5)/(25.09,98.8)，R=307.3、
  圆心 (140,383.8)；两端以直线段连接。切槽中心跨 y 66–76.5，与前景透镜
  （上缘 y=71）之间的可见白带为 y 66–71（高 5）。

## 重新生成与验收

```bash
python3 generate.py            # 读 ./icon-geometry.json，写 ./dist/
python3 validate.py            # 写 ./VALIDATION.md，全部通过时退出码为 0
```

改图标只改 `icon-geometry.json`，然后重跑这两条命令；验收不过（退出码非 0）不要发布。

## 各端如何消费同一份数据

- **SVG**：`outline` 逐元素翻译为 `M/L/A/Z`；E 翻译为圆角矩形与胶囊子路径。
- **Canvas**：同一元素列表用三点定圆调用 `arc` / `lineTo` / `roundRect`；
  standard 的切槽在离屏画布上以 `destination-out` 擦除，不需要背景色。
- **iOS / Android / Flutter**：按同一元素列表调用各自 Path API 的 arcTo/addArc 即可，数据无需改动。
- **CSS**：E 为定位 div + border-radius；S / 太阳 / 地平线为沿圆弧采样（3° 步长）的
  `clip-path` 多边形；standard 切槽为背景色同形覆盖层，颜色取 `--elysola-bg`（默认 #fff），
  放在 ES 层与地平线层之间。

## 保真度说明

- SVG 与 Canvas 为精确渲染（同一组圆弧）。
- CSS 版 S / 透镜为采样多边形近似：3° 采样下与精确轮廓的偏差在亚像素量级，
  但 CSS 无原生路径填充，仍按近似还原对待，品牌正式场合优先用 SVG 或 Canvas。
- SVG 版 standard 切槽自 v1.2 起默认用真 `<mask>`（`dist/elysola-standard.svg`）：
  切槽在任何背景上都是真透明（512 采样点 (192,250) 的 alpha 为 0，与原稿一致），
  且文件不含 CSS `var()`，cairosvg 不会再崩。背景色覆盖版保留为
  `dist/elysola-standard-overlay.svg`，仅供禁止 mask 的场景，颜色已改为显式
  `#ffffff`（不再用 `var()`），但它在透明背景上是不透明白块，只适用于白底。
  CSS 版切槽仍为背景色覆盖层（CSS 无 mask 等价物），颜色取 `--elysola-bg`（默认 #fff）；
  Canvas 版用 destination-out，与背景无关。

## 数据来源说明

标量参数（坐标系、映射、t/r/r0/g、地平线、太阳的 R 与圆心）取自
《Elysola 品牌图标几何标准化设计规范》（唯一确定版）。E 横画口径与切槽参数
于 v1.1 按原稿 SVG 逐项重算修正：早期版本把 E 的直线段终点误作含帽末端
（三横短 9 单位），且切槽为估算的加宽透镜（白带高约 7）；v1.1 起 E 按
chordEnd + endR 还原原稿端帽，切槽按原稿 Q 透镜加描边外扩重算（白带高 5）。
v1.2 起 validate.py 换成外部渲染器方法：优先 subprocess 调 rsvg-convert
渲染 dist SVG 与内嵌的原稿 SVG（cairosvg 为回退），比 IoU、边界 chamfer
最大偏差、切槽采样点 alpha、E 圆角采样点 alpha，并实际用 cairosvg 渲染
每个 dist SVG 检查不再崩溃；旧版自绘原稿（ImageDraw + MaxFilter 膨胀）的
方法已废弃，它对 A/B/C 三类缺陷（圆角被填、切槽不透明、cairosvg 崩溃）
全无检出能力。v1.2 同时修正 E 横画起点（见上）与 standard SVG 的切槽
实现（mask 版为默认，见保真度说明）。S 的端面、段数结构与绘制
顺序按该规范；每段弧的圆心/R/θ 按规范 1.3 的三点定圆公式由端点与过点算出——
规范 S 明细表中个别段的圆心/R 与其自身端点不满足 |P−C|=R（如普通版第 5 段
端点到圆心距离约 7.4 而表中 R 为 24.9），无法按字面作图，故以公式派生值为准，
端点与结构未作任何改动。验收数值见 `VALIDATION.md`。
