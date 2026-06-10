# Obsidian 模板

本地 figures/tables 使用 Obsidian embeds；外部来源使用 Markdown links。正文不写“图表 Manifest”小节；如需 provenance，可在 assets 目录旁单独保存 `manifest.json`。

## 写作原则

- “总览 / 基本信息 / 一页结论”合并为 `论文速览`，保持短。
- `Tables` 原图要全部进入正文：优先嵌入官方原始 table image；没有独立原图时，用官方 PDF 的 table crop 或 page render。Markdown 表格、关键数字摘录和 table note 只能补充，不能替代原图。
- 研究哲学、实验设置、图表美学、图表 taste 都贴在对应 figure/table 下讲，不单独堆成很长的总结章。
- 每张图/表下面写 3-5 条短 bullets；用简单话讲清楚“它证明什么、设置是什么、好在哪里、能借鉴什么”。

## Single atlas 模式

论文列表不超过 8 篇时使用，除非用户明确要求 card mode。

```markdown
---
title: <Paper Title> 图表图谱
date: <YYYY-MM-DD>
paper_id: <stable id>
year: <year>
venue: <venue>
tags:
  - paper/figure-atlas
  - research/visual-design
status: draft
---

# <Paper Title>

## 论文速览

- **一句话**：<这篇论文最重要的问题、方法或结论。>
- **作者 / Venue**：<authors/team>；<venue/year>
- **方向**：<field/direction>
- **Source**：[paper](url), [PDF](url), [code](url), [project](url)
- **图表主线**：<用一句话说明图表证据链，比如“现象图 -> 机制图 -> 消融表 -> 结果表”。>

## 图表精读

### Fig. <id> - <role>

![[<asset_path>|800]]

- **证明什么**：<这张图要让读者一眼看懂的核心 claim。>
- **设置口径**：<dataset / model / metric / supervision / protocol，只写和图有关的要点。>
- **图表 taste**：<panel、颜色、对比或视觉语法为什么有效。>
- **可借鉴**：<未来写论文或做 slides 可复用的一个做法。>

### Table <id> - <role>

![[<table_original_asset>|800]]

可选关键数字摘录：

| Setting | Metric | Main result |
| --- | --- | --- |
| <row> | <metric> | <short result> |

- **证明什么**：<这张表服务的结论。>
- **设置口径**：<benchmark / baseline / metric。>
- **表格 taste**：<增量、分组、灰底、高亮或对照结构为什么清楚。>
- **可借鉴**：<表格组织方式给未来工作的启发。>
```

## Index and cards 模式

论文列表超过 8 篇，或用户希望长期维护时使用。

索引页保持轻量，只做导航和跨论文一眼比较：

```markdown
---
title: 图表图谱索引 - <topic>
tags:
  - paper/figure-atlas
---

# 图表图谱索引 - <topic>

| 论文 | Year | Venue | Card | 图表主线 |
| --- | --- | --- | --- | --- |
| <title> | <year> | <venue> | [[papers/<paper_slug>]] | <one-line evidence chain> |
```

单篇论文 card 使用和 single-atlas 相同的结构：

```markdown
---
title: <Paper Title>
paper_id: <stable id>
year: <year>
venue: <venue>
tags:
  - paper/figure-atlas
---

# <Paper Title>

## 论文速览

- **一句话**：...
- **作者 / Venue**：...
- **Source**：...
- **图表主线**：...

## 图表精读

### Fig. <id> - <role>

![[<asset_path>|800]]

- **证明什么**：...
- **设置口径**：...
- **图表 taste**：...
- **可借鉴**：...

### Table <id> - <role>

![[<table_original_asset>|800]]

可选关键数字摘录：

| Setting | Metric | Main result |
| --- | --- | --- |
| ... | ... | ... |

- **证明什么**：...
- **设置口径**：...
- **表格 taste**：...
- **可借鉴**：...
```
