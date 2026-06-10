---
name: paper-figure-atlas
description: "从指定论文列表构建 Obsidian paper figure atlas，采集官方 figures、tables、实验设置与 metadata，并综合分析 figure design aesthetics、research taste 和 insight。用于用户要求爬取、收集、整理或分析 scientific-paper 主图、方法图、结果图、分析图、实验图、表格、visual resources、figure inspiration，或生成 Obsidian 论文图表学习文档时。"
---

# Paper Figure Atlas

## 用途

使用这个 skill，把用户指定的论文列表整理成可直接放入 Obsidian 的 figure atlas。产物需要保留可靠的论文事实，在可行时收集官方图表资源，并在每张 figure/table 下用简短、说人话的文字解释它的 evidence design、scientific taste 和可复用研究洞察。

默认用中文写面向用户的内容。英文论文标题、方法名、指标、venue、数据集名、figure/table label 保持原文。

## 输入

接受混合形式的论文标识：

- arXiv ID 或 URL
- DOI、OpenReview、publisher、project 或 PDF URL
- 本地 PDF
- 没有稳定标识时的论文标题

如果用户没有指定交付形态，默认使用：

- `single-atlas`：论文数量不超过 8 篇时使用
- `index-and-cards`：论文数量超过 8 篇时使用

如果缺少目标 Obsidian 路径，且当前环境中没有明显的 vault 上下文，在写文件前只问一次目标 note 或 folder。

## 工作流

1. 检查目标上下文。
   - 先查看附近的 Obsidian 笔记，再决定 frontmatter 字段、附件路径、wikilink 风格和标题层级。
   - 当现有 vault 约定与本 skill 模板冲突时，优先遵守现有 vault 约定。

2. 先核准论文事实，再采集图表资源。
   - 按需使用 `paper-search`、`paper-analyze`、`research-lookup`、OpenAlex、OpenReview、arXiv、官方项目页和 publisher 页面。
   - 记录 title、year、venue、author team、field/direction、arXiv/DOI/PDF/project/code links 和 source confidence。
   - 当用户把 `Venue` 误写成 `Veuve` 等拼写时，仍按必填的 `Venue` 字段理解。

3. 遵守官方来源优先级。
   - 来源选择不明显时，阅读 `references/source-priority.md`。
   - 优先使用 arXiv source tarball 中的原始文件和官方 PDF，而不是截图。
   - 不要把 ar5iv 或 arXiv HTML 的缺图占位图当作有效 figure。

4. 采集候选图表资源。
   - 对 arXiv 论文，运行 `scripts/collect_arxiv_assets.py` 下载 HTML 图片、提取 caption clues，并按需渲染 PDF 页面。
   - 对非 arXiv 论文，手动使用官方 PDF、项目页或 proceedings 页面，再用相同 manifest 形态记录资源。
   - 只收集有助于理解论文的 figures 和 tables，不要把所有装饰性或重复 panel 都塞进笔记。

5. 分类并筛选图表。
   - 选择 figure roles 时阅读 `references/figure-taxonomy.md`。
   - 条件允许时，至少覆盖 main/overview figure，以及一个 method 或 result figure。
   - 对图表丰富的论文，也纳入 analysis、ablation、experiment setup、qualitative examples 和 key tables。

6. 分析图表设计和 research taste。
   - 阅读 `references/aesthetic-rubric.md` 获取分析维度。
   - 解释 evidence logic、panel hierarchy、visual grammar、comparison structure、color/typography 选择，以及图表体现出的作者 scientific philosophy。
   - 避免泛泛夸奖。每个 taste 或 insight 判断都要绑定到可见的 figure/table 证据。

7. 写出 Obsidian 交付物。
   - 写作前阅读 `references/obsidian-template.md`。
   - Single atlas 模式使用 `<note_stem>.md` 和 `<note_stem>_assets/<paper_slug>/...`。
   - Index/card 模式使用 `00_figure_atlas_index.md`、`papers/<paper_slug>.md` 和 `assets/<paper_slug>/...`。
   - 本地资源使用 Obsidian embeds，外部来源使用 Markdown links。
   - 正文不要生成“图表 Manifest”小节；如需资源追踪，可单独保留 `manifest.json` 给验证和 provenance 使用。
   - 将“总览 / 基本信息 / 一页结论”合并为一个简短的“论文速览”部分。
   - Tables 原图必须全部嵌入在文档中：优先使用 arXiv source 原始表格图或编译产物，其次使用 arXiv HTML table image，最后使用官方 PDF table crop 或 page render；Markdown 表格、关键数字摘要和 table note 只能作为补充，不可替代原图 embed。
   - 研究哲学、实验设置、图表美学、图表 taste 总结等内容，放在对应 figure/table 下就地说明，不要集中堆成长篇总述。
   - 每张图/表下面控制在 3-5 条短 bullets，尽量凝练、简单易懂、有启发性。

8. 收尾前验证。
   - 对生成的 Markdown 运行 `scripts/validate_obsidian_atlas.py`。
   - 下载或渲染过资源时，用 `file` 抽查文件类型。
   - 搜索未解决的占位符，如 `待补`、`TODO`、broken links 或缺失的 local assets。只有在证据确实不可得时，才保留 `待补`。

## 辅助脚本

可用时使用 Codex Python 环境：

```bash
/Users/zane/.codex/venvs/codex311/bin/python scripts/collect_arxiv_assets.py \
  --paper 2003.08934 \
  --out /tmp/paper-figure-atlas-smoke \
  --limit-assets 2
```

验证 atlas：

```bash
/Users/zane/.codex/venvs/codex311/bin/python scripts/validate_obsidian_atlas.py \
  path/to/atlas.md
```

脚本只是辅助工具，不是 source of truth。决定哪些内容进入最终 atlas 之前，必须人工检查下载到的 assets 和 captions。

## 输出契约

每篇论文的 section 或 card 必须包含：

- 论文速览：title、year、venue、authors/team、field/direction、links、source confidence 和一句话结论
- selected figure/table embeds；所有 key tables 都要以官方原图或官方 PDF 渲染裁图的本地图片形式嵌入正文
- 每个 figure/table 下的短解读：它在证明什么、对应实验/设置口径、图表设计 taste、可借鉴启发
- Table 的 Markdown 摘录或关键数字摘要只作为辅助阅读材料，不能替代 Table 原图 embed
- 可选独立 `manifest.json`：source、local path、figure/table id、inferred role、caption clue；用于资源追踪和验证，不在正文展开成 Manifest 表格

## 禁止事项

- 不要编造 venues、author teams、experiment settings、figure captions 或 table numbers。
- 官方来源可用时，不要使用博客截图或二手总结替代。
- 不要把所有提取出的 asset 不经筛选和解释地倒进笔记。
- 不要在最终正文里生成单独的“图表 Manifest”资源清单。
- 不要把研究哲学、实验设置和图表 taste 写成远离图表的大段集中总结；应贴着具体图表讲。
- 不要让单张图下面的解释过长；优先短句、短 bullets、可直接复用的启发。
- 不要把受版权保护的 figures 当作公开素材再分发；始终保留 source links 和 citations。
