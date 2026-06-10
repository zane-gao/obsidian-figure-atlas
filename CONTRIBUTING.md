# Contributing / 贡献指南

Thanks for improving Obsidian Figure Atlas.

感谢你一起改进这个论文图表图谱 skill。

## Development Setup / 开发环境

```bash
git clone https://github.com/zane-gao/obsidian-figure-atlas.git
cd obsidian-figure-atlas
python -m pip install -r requirements.txt
```

Optional PDF fallback commands require Poppler:

```bash
brew install poppler
```

## Local Checks / 本地检查

Run these before opening a pull request:

```bash
python -m py_compile scripts/collect_arxiv_assets.py scripts/validate_obsidian_atlas.py
python scripts/collect_arxiv_assets.py --help
python scripts/validate_obsidian_atlas.py examples/demo_atlas.md --manifest examples/manifest.json
```

If you are developing inside Codex on the original machine, also run:

```bash
/Users/zane/.codex/venvs/codex311/bin/python /Users/zane/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
```

## Contribution Rules / 贡献规则

- Keep `SKILL.md` as the source of truth for agent behavior.
- Preserve the public skill name: `paper-figure-atlas`.
- Do not commit real copyrighted paper figures as examples.
- Use synthetic assets, tiny fixtures, or generated placeholders in tests.
- Keep scripts lightweight; avoid heavy ML dependencies for basic collection and validation.
- Prefer official paper sources over secondary screenshots.

## Pull Request Checklist / PR 检查表

- [ ] The skill still validates locally.
- [ ] Script entrypoints still support `--help`.
- [ ] Demo atlas validation passes.
- [ ] README or references are updated when behavior changes.
- [ ] No real paper figure assets are committed without a clear license.
