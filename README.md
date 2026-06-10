# Obsidian Figure Atlas / 论文图表图谱

[![CI](https://github.com/zane-gao/obsidian-figure-atlas/actions/workflows/ci.yml/badge.svg)](https://github.com/zane-gao/obsidian-figure-atlas/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Turn scientific papers into Obsidian-ready figure and table atlases.

把论文里的主图、方法图、结果图、分析图、实验设置和关键表格，整理成可直接放入 Obsidian 的图表精读笔记。

This repository packages the Codex skill `$paper-figure-atlas`. It helps an agent collect official figure/table candidates from arXiv source, arXiv HTML, official PDFs, project pages, or proceedings, then write compact notes about visual evidence, figure design taste, and reusable research insight.

这个仓库提供一个 skill：`$paper-figure-atlas`。它面向科研阅读和论文写作训练：优先从官方来源采集图表候选资源，再把每张图表放回论文证据链中解读，而不是只把图片无脑堆进笔记。

## Why Use It / 为什么值得用

- **Official-source first**: prefers arXiv source tarballs, official PDFs, venue pages, OpenReview, and project pages before secondary screenshots.
- **Obsidian-native output**: writes local embeds, card/index layouts, and manifests that are easy to keep inside a vault.
- **Figure taste, not just figure dumps**: explains what each visual proves, how the experiment is framed, and what design pattern is worth reusing.
- **Tables stay visual**: key tables must be embedded as official images, PDF crops, or rendered pages; Markdown summaries are only supplements.
- **Built-in validation**: checks Markdown image embeds and `manifest.json` local paths before handoff.

- **官方来源优先**：优先使用 arXiv source、官方 PDF、venue 页面、OpenReview 和项目页，避免二手截图污染事实。
- **适配 Obsidian**：输出本地 embed、单篇 atlas 或索引 + card 结构，并保留资源 manifest 方便追踪。
- **不只是扒图**：每张图表下面都会解释它证明什么、实验口径是什么、图表设计为什么有效、未来写论文能借鉴什么。
- **表格必须有原图**：关键表格不能只转写成 Markdown 表格，必须嵌入官方表格图、PDF 裁图或页面渲染图。
- **带验证脚本**：交付前检查 Markdown 图片引用和 manifest 本地路径，降低 broken link 风险。

## Install / 安装

Install it as a Codex skill by cloning this repository into the skill folder named `paper-figure-atlas`:

```bash
git clone https://github.com/zane-gao/obsidian-figure-atlas.git ~/.codex/skills/paper-figure-atlas
```

The repository name is `obsidian-figure-atlas`, but the skill name remains:

```text
$paper-figure-atlas
```

Python helpers use a small dependency set:

```bash
cd ~/.codex/skills/paper-figure-atlas
python -m pip install -r requirements.txt
```

Optional PDF fallback features use Poppler command-line tools:

```bash
# macOS
brew install poppler

# Ubuntu / Debian
sudo apt-get install poppler-utils
```

## Quick Start / 快速开始

Ask Codex:

```text
使用 $paper-figure-atlas，根据这份论文列表构建 Obsidian figure atlas：
- 2003.08934
- https://openreview.net/forum?id=...
输出到 /path/to/my/obsidian/vault/figure_atlas/
```

Run the arXiv asset collector manually:

```bash
python scripts/collect_arxiv_assets.py \
  --paper 2003.08934 \
  --out /tmp/paper-figure-atlas-smoke \
  --limit-assets 2
```

Validate an atlas:

```bash
python scripts/validate_obsidian_atlas.py examples/demo_atlas.md \
  --manifest examples/manifest.json
```

## Workflow / 工作流

```text
paper list
  -> verify paper facts
  -> collect official visual candidates
  -> classify figure/table roles
  -> select evidence-bearing visuals
  -> write Obsidian atlas
  -> validate embeds and manifest paths
```

The skill uses these source priorities:

1. arXiv source tarball, official PDF, proceedings, OpenReview, publisher pages.
2. Official HTML and project pages.
3. PDF extraction, page rendering, or table crops.
4. Secondary sources only when official assets are unavailable and clearly marked.

## Repository Layout / 目录结构

```text
.
├── SKILL.md                         # Codex skill entrypoint
├── agents/openai.yaml               # Skill display metadata
├── references/
│   ├── source-priority.md           # Official-source policy
│   ├── figure-taxonomy.md           # Figure/table role taxonomy
│   ├── aesthetic-rubric.md          # Visual evidence analysis rubric
│   └── obsidian-template.md         # Obsidian output templates
├── scripts/
│   ├── collect_arxiv_assets.py      # arXiv source/HTML/PDF asset collector
│   └── validate_obsidian_atlas.py   # Obsidian embed + manifest validator
└── examples/
    ├── demo_atlas.md                # Synthetic example atlas
    └── manifest.json                # Example provenance manifest
```

## Example / 示例

See [`examples/demo_atlas.md`](examples/demo_atlas.md). The example uses synthetic SVG placeholders so the repository stays safe to redistribute. Real atlas outputs should keep source links near figure embeds and remain mindful of paper figure copyrights.

示例文件只使用虚构论文和自绘 SVG，不包含真实论文图表。实际使用时，请在图表附近保留 source links，并在公开再分发前确认版权和使用场景。


## Contributing / 贡献

Issues and pull requests are welcome. Useful contributions include:

- better arXiv / publisher extraction fallbacks
- more robust Obsidian link validation
- examples for new research domains
- improved figure taxonomy and visual evidence rubrics
- tests that avoid downloading copyrighted assets

欢迎提 issue 或 PR。尤其欢迎补充更稳的图表抽取 fallback、更好的 Obsidian 链接校验、新领域示例、图表 taxonomy 和不依赖真实论文图的测试。

## License / 许可证

MIT. See [`LICENSE`](LICENSE).
