# 审美与洞察 Rubric

把 visual design 当作 evidence design 来分析。除非笔记能说明是哪一个具体设计选择造成了这种效果，否则避免只写 “clean” 或 “beautiful” 这类泛泛评价。

## 分析维度

这些维度用于思考，不要求每张图机械展开全部项目。最终输出要贴在具体 figure/table 下，挑最关键的 3-5 点讲清楚。

1. Core visual thesis
   - 这张图试图让读者一眼看懂什么？
   - 哪个视觉元素承载了核心主张？

2. Evidence chain
   - panels 如何从 problem setup 推进到 method 再到 result？
   - 这张图展示的是 causality、comparison、mechanism，还是 evidence accumulation？

3. Panel hierarchy
   - 哪个 panel 是 anchor？
   - 支撑 panels 是按逻辑、时间、尺度，还是 metric family 排列？

4. Visual grammar
   - 箭头、颜色、图标、坐标轴、空间布局和 annotations 分别表示什么？
   - 这些 grammar 是否在多个 panels 中一致复用？

5. Comparison design
   - 图中比较的是 methods、datasets、conditions、time、failure modes，还是 mechanisms？
   - baselines 和 uncertainty 是否足够可见？

6. Color, typography, and density
   - color 是语义性的还是装饰性的？
   - typography 是在引导阅读，还是增加噪声？
   - information density 是否与该图要证明的 claim 相匹配？

7. Scientific philosophy
   - 论文更偏向 mechanism、benchmark dominance、diagnostic transparency、system engineering、scaling behavior，还是 qualitative intuition？
   - figure design 如何暴露这种立场？

8. Reusable taste and insight
   - 未来写论文或做 slides 时，哪些 pattern 值得借鉴？
   - 哪些做法应避免？
   - 这张图会让 reviewer 追问什么问题？

## 输出模式

每张 figure/table 下使用短小、绑定证据的 bullets。优先说人话，少写抽象大词：

```markdown
- **证明什么**：...
- **设置口径**：...
- **图表 taste**：...
- **可借鉴**：...
```

可按图表类型替换 bullet 名称：

- 方法图：强调 pipeline、信息流、模块关系。
- 结果图：强调 baseline、metric、增量和不确定性。
- 分析图：强调诊断指标、因果 probe、failure mode。
- 表格：强调 benchmark 分组、核心数字、增量标注和对照结构。

避免写法：

- 不要把“研究哲学 / 实验设置 / 图表美学 / taste 总结”集中成远离图表的大段文字。
- 不要写“很清晰、很漂亮”但不说明是哪一个视觉选择有效。
- 不要为了覆盖 rubric 把单张图写得很长；宁可短，但每条都指向可见证据。

对 cross-paper atlas，只在索引或开头保留 1-3 条跨论文 visual pattern，不写长篇 synthesis。
