# 图表分类体系

按照每个候选 visual 在论文中的证据角色进行分类。好的 atlas 要覆盖论文的 evidence logic，而不只是收集好看的图片。

| Role | 展示内容 | 常见线索 |
| --- | --- | --- |
| `hero` | 论文的核心主张、teaser 或任务框定 | teaser, overview, pipeline, main result, Fig. 1 |
| `method` | architecture、algorithm、pipeline、training 或 inference flow | method, framework, architecture, model, pipeline |
| `infographic` | 概念解释或问题设定 | illustration, overview, task, dataset construction |
| `experiment-setup` | benchmark、data collection、protocol、environment、metrics | setup, benchmark, dataset, protocol, evaluation |
| `result` | 主要 quantitative 或 qualitative evidence | results, performance, comparison, SOTA, qualitative |
| `analysis` | diagnostic、attribution、error analysis、sensitivity、scaling | analysis, visualization, t-SNE, attention, error |
| `ablation` | 组件贡献或设计选择证据 | ablation, variant, component, without, sensitivity |
| `table` | 结构化数值证据或设置 | Table, hyperparameter, dataset statistics, metrics |
| `supplement` | appendix-only、但有助于解释正文的细节 | appendix, supplementary, additional |

## 选择规则

- 总是尽量包含一个 `hero` 或 overview visual。
- 当论文提出 model、algorithm、data pipeline 或 system 时，至少包含一个 `method` visual。
- 当论文提出 empirical claims 时，至少包含一个 `result` visual 或 key table。
- 当贡献依赖 benchmark design、data construction、human study、robotics setup 或 protocol choices 时，包含 `experiment-setup`。
- 当 `analysis` 和 `ablation` 能揭示方法为什么有效或在哪里失败时，应纳入。
- 跳过冗余 panels，除非它们展示了不同 evidence type。

## 命名

使用稳定文件名：

```text
fig01_hero_overview.png
fig02_method_pipeline.png
fig03_result_main_table.png
fig04_analysis_failure_cases.png
table01_experiment_settings.md
```

当原始 asset 已经有稳定 source filename 时，即使本地文件名做了规范化，也要在 manifest 中保留原始文件名信息。
