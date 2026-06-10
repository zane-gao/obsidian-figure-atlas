# 来源优先级

采集论文事实、figures、tables 和 experiment settings 时，按以下顺序选择来源。

## 1. 官方论文来源

优先使用论文发表路径控制下的来源：

- arXiv abstract、PDF 和 e-print source tarball
- 官方 conference proceedings
- ICLR、NeurIPS、ICML 等 venue 的 OpenReview 页面
- publisher PDF 或 supplementary material

对 arXiv 论文，先检查 source tarball 是否暴露原始的 `figure`、`figures`、`images` 或 `assets` 文件。原始 source files 通常比截图更能保留 vector PDF 和干净的 PNG/JPG panel。

对 tables，优先寻找 source 中的原始表格图、编译产物或可稳定渲染的 table asset。最终 atlas 里必须保留 Table 原图 embed；Markdown 转写只能作为辅助摘录。

## 2. 官方 HTML 与项目页

使用 arXiv HTML、project pages 和 official lab pages 获取：

- direct image assets
- teaser images
- method diagrams
- qualitative result examples
- table images
- code 和 demo links

不要保存 ar5iv 或 arXiv HTML 的 missing-image placeholders。如果 HTML 图片缺失，切换到 source tarball 或 PDF rendering。

## 3. PDF 兜底

无法提取原始图片时，再使用 PDF rendering。优先工具：

- `pdfimages`：提取 embedded raster/vector-like assets
- `pdftoppm -r 220 -png -f PAGE -l PAGE`：生成 page-level figure/table crops 或 preview pages
- `pdftotext -layout`：提取 caption、table 和 experiment-setting clues

对 tables，如果 source 和 HTML 没有独立 table image，就从官方 PDF 做 table crop；无法稳定裁剪时，整页 render 也可接受，但要命名和备注为 PDF-rendered table/page asset。不要只转写表格内容，也不要用二手截图替代官方原图。

渲染页适合作为个人研究证据，不是干净的可复用 figure/table source。必须清楚标注为 PDF-rendered assets。

## 4. 二级来源

只有在以下条件满足时，才使用 blogs、slides、social posts 或 repository README images：

- 官方论文 assets 不可用
- 二级来源由同一团队发布
- 笔记明确标注来源和不确定性

除非官方来源已经过时，且更新的官方 venue 页面确认了变更，否则不要让二级来源覆盖官方 metadata。

## 证据日志字段

每个入选 asset 都要记录：

- `paper_key`
- `source_type`: `arxiv-source`, `arxiv-html`, `official-pdf`, `openreview`, `proceedings`, `project-page`, `secondary`
- `source_url`
- `local_path`
- `figure_or_table_id`
- `caption`
- `inferred_role`
- `confidence`: `high`, `medium`, or `low`
- `notes`

## 版权与引用

在 figure embeds 附近保留 source links。atlas 用于研究整理和 critique。不要把复制来的 figures 表述为新创作资产；未经权利核查，不要准备公开再分发。
