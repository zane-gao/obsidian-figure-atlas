#!/usr/bin/env python3
"""Collect candidate arXiv figure assets for a paper figure atlas."""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import shutil
import subprocess
import sys
import tarfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ARXIV_ID_RE = re.compile(
    r"(?P<id>(?:\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?)",
    re.IGNORECASE,
)


@dataclass
class PaperInfo:
    raw_input: str
    arxiv_id: str
    slug: str
    abs_url: str
    html_url: str
    pdf_url: str
    source_url: str
    title: str = ""
    authors: list[str] | None = None
    year: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download candidate figures from arXiv HTML and optionally extract PDF assets.",
    )
    parser.add_argument(
        "--paper",
        action="append",
        required=True,
        help="arXiv ID or arXiv abs/html/pdf URL. Repeat for multiple papers.",
    )
    parser.add_argument("--out", required=True, help="Output directory.")
    parser.add_argument(
        "--limit-assets",
        type=int,
        default=0,
        help="Maximum downloaded HTML image assets per paper. 0 means no limit.",
    )
    parser.add_argument(
        "--skip-source",
        action="store_true",
        help="Skip arXiv e-print source archive extraction.",
    )
    parser.add_argument(
        "--extract-pdf-images",
        action="store_true",
        help="Download the PDF and run pdfimages when available.",
    )
    parser.add_argument(
        "--render-pages",
        default="",
        help="Comma-separated PDF pages to render with pdftoppm, for example 1,2,5.",
    )
    parser.add_argument(
        "--extract-text",
        action="store_true",
        help="Download the PDF and run pdftotext -layout for caption/table clues.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Network timeout in seconds.",
    )
    return parser.parse_args()


def normalize_arxiv(raw: str) -> tuple[str, str]:
    match = ARXIV_ID_RE.search(raw)
    if not match:
        raise ValueError(f"Cannot find an arXiv ID in: {raw}")
    arxiv_id = match.group("id")
    if raw.endswith(".pdf") and arxiv_id.endswith(".pdf"):
        arxiv_id = arxiv_id[:-4]
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", arxiv_id)
    return arxiv_id, slug


def get_soup(url: str, timeout: int) -> BeautifulSoup:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "paper-figure-atlas/1.0"})
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def parse_abs_metadata(info: PaperInfo, timeout: int) -> PaperInfo:
    try:
        soup = get_soup(info.abs_url, timeout)
    except Exception as exc:  # noqa: BLE001 - report and continue with URL-only metadata
        print(f"[WARN] Failed to fetch abs metadata for {info.arxiv_id}: {exc}", file=sys.stderr)
        return info

    title = soup.select_one("h1.title")
    if title:
        info.title = clean_text(title.get_text(" ")).removeprefix("Title:").strip()

    authors = [clean_text(a.get_text(" ")) for a in soup.select(".authors a")]
    info.authors = authors

    citation_date = soup.find("meta", attrs={"name": "citation_date"})
    if citation_date and citation_date.get("content"):
        info.year = str(citation_date["content"])[:4]
    if not info.year:
        dateline = soup.select_one(".dateline")
        if dateline:
            year_match = re.search(r"\b(19|20)\d{2}\b", dateline.get_text(" "))
            if year_match:
                info.year = year_match.group(0)

    return info


def infer_role(text: str) -> tuple[str, str]:
    lower = text.lower()
    rules = [
        ("experiment-setup", ["setup", "protocol", "benchmark", "dataset", "environment"]),
        ("ablation", ["ablation", "variant", "without", "component", "sensitivity"]),
        ("analysis", ["analysis", "diagnostic", "attention", "error", "visualization", "t-sne", "failure"]),
        ("result", ["result", "performance", "comparison", "sota", "qualitative", "quantitative"]),
        ("method", ["method", "framework", "architecture", "pipeline", "model", "algorithm"]),
        ("infographic", ["task", "overview", "illustration", "problem", "concept"]),
        ("table", ["table", "hyperparameter", "statistics", "settings"]),
        ("hero", ["teaser", "main", "overview", "fig. 1", "figure 1"]),
    ]
    for role, keywords in rules:
        if any(keyword in lower for keyword in keywords):
            return role, "medium"
    return "candidate", "low"


def extension_from_response(url: str, response: requests.Response) -> str:
    path_suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    if path_suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".svg"}:
        return path_suffix
    content_type = response.headers.get("content-type", "").split(";", 1)[0].strip()
    guessed = mimetypes.guess_extension(content_type)
    if guessed:
        return guessed
    return ".bin"


def safe_caption_for_image(img: Any) -> str:
    candidates: list[str] = []
    alt = img.get("alt")
    if alt:
        candidates.append(str(alt))
    title = img.get("title")
    if title:
        candidates.append(str(title))

    parent = img.find_parent(["figure", "table", "div", "p"])
    if parent:
        caption = parent.find(["figcaption", "caption"])
        if caption:
            candidates.append(caption.get_text(" "))
        else:
            candidates.append(parent.get_text(" "))

    text = clean_text(" ".join(candidates))
    return text[:800]


def collect_html_assets(info: PaperInfo, paper_dir: Path, timeout: int, limit_assets: int) -> list[dict[str, Any]]:
    try:
        soup = get_soup(info.html_url, timeout)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Failed to fetch arXiv HTML for {info.arxiv_id}: {exc}", file=sys.stderr)
        return []

    html_dir = paper_dir / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    assets: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    image_tags = soup.find_all("img")

    for img in image_tags:
        src = img.get("src")
        if not src:
            continue
        src_text = str(src)
        if src_text.startswith("data:") or "missing" in src_text.lower():
            continue

        asset_url = urljoin(info.html_url, src_text)
        if asset_url in seen_urls:
            continue
        seen_urls.add(asset_url)

        if limit_assets and len(assets) >= limit_assets:
            break

        try:
            response = requests.get(
                asset_url,
                timeout=timeout,
                headers={"User-Agent": "paper-figure-atlas/1.0"},
            )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] Failed to download {asset_url}: {exc}", file=sys.stderr)
            continue

        caption = safe_caption_for_image(img)
        role, confidence = infer_role(" ".join([caption, asset_url]))
        ext = extension_from_response(asset_url, response)
        asset_index = len(assets) + 1
        filename = f"fig{asset_index:02d}_{role}{ext}"
        local_path = html_dir / filename
        local_path.write_bytes(response.content)

        assets.append(
            {
                "paper_key": info.slug,
                "asset_id": f"{info.slug}:html:{asset_index:02d}",
                "source_type": "arxiv-html",
                "source_url": asset_url,
                "local_path": str(local_path.relative_to(paper_dir.parent)),
                "figure_or_table_id": guess_figure_id(caption, asset_index),
                "caption": caption,
                "inferred_role": role,
                "confidence": confidence,
                "notes": "Downloaded from arXiv HTML. Inspect manually before final selection.",
            }
        )

    return assets


def allowed_source_asset(path: str) -> bool:
    suffix = Path(path).suffix.lower()
    return suffix in {".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg"}


def safe_archive_name(name: str) -> str:
    path = Path(name)
    parts = [part for part in path.parts if part not in {"", ".", ".."}]
    return "_".join(parts) if parts else path.name


def write_source_asset(
    *,
    data: bytes,
    original_name: str,
    info: PaperInfo,
    source_dir: Path,
    output_root: Path,
    asset_index: int,
) -> dict[str, Any]:
    role, confidence = infer_role(original_name)
    suffix = Path(original_name).suffix.lower() or ".bin"
    filename = f"source{asset_index:02d}_{role}{suffix}"
    local_path = source_dir / filename
    local_path.write_bytes(data)
    return {
        "paper_key": info.slug,
        "asset_id": f"{info.slug}:arxiv-source:{asset_index:02d}",
        "source_type": "arxiv-source",
        "source_url": info.source_url,
        "local_path": str(local_path.relative_to(output_root)),
        "figure_or_table_id": Path(original_name).stem,
        "caption": "",
        "inferred_role": role,
        "confidence": confidence,
        "notes": f"Extracted from arXiv source archive member: {original_name}",
    }


def collect_source_assets(
    info: PaperInfo,
    paper_dir: Path,
    timeout: int,
    limit_assets: int,
    existing_count: int,
) -> list[dict[str, Any]]:
    source_dir = paper_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    archive_path = source_dir / f"{info.slug}_eprint"
    try:
        response = requests.get(info.source_url, timeout=timeout, headers={"User-Agent": "paper-figure-atlas/1.0"})
        response.raise_for_status()
        archive_path.write_bytes(response.content)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Failed to download arXiv source for {info.arxiv_id}: {exc}", file=sys.stderr)
        return []

    remaining = None if not limit_assets else max(0, limit_assets - existing_count)
    if remaining == 0:
        return []

    assets: list[dict[str, Any]] = []
    max_member_size = 50 * 1024 * 1024

    def maybe_add_asset(original_name: str, data: bytes) -> None:
        if not allowed_source_asset(original_name):
            return
        if remaining is not None and len(assets) >= remaining:
            return
        if not data:
            return
        assets.append(
            write_source_asset(
                data=data,
                original_name=safe_archive_name(original_name),
                info=info,
                source_dir=source_dir,
                output_root=paper_dir.parent,
                asset_index=len(assets) + 1,
            )
        )

    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path, "r:*") as archive:
            members = sorted(
                (member for member in archive.getmembers() if member.isfile()),
                key=lambda member: member.name.lower(),
            )
            for member in members:
                if remaining is not None and len(assets) >= remaining:
                    break
                if member.size > max_member_size or not allowed_source_asset(member.name):
                    continue
                file_obj = archive.extractfile(member)
                if file_obj:
                    maybe_add_asset(member.name, file_obj.read())
        return assets

    if zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as archive:
            names = sorted(archive.namelist(), key=str.lower)
            for name in names:
                if remaining is not None and len(assets) >= remaining:
                    break
                info_obj = archive.getinfo(name)
                if info_obj.file_size > max_member_size or not allowed_source_asset(name):
                    continue
                maybe_add_asset(name, archive.read(name))
        return assets

    # Some arXiv e-prints are single TeX files. Keep the archive for inspection,
    # but there are no safe image members to emit in that case.
    print(f"[WARN] arXiv source for {info.arxiv_id} is not a tar/zip archive with extractable images", file=sys.stderr)
    return assets


def guess_figure_id(caption: str, fallback_index: int) -> str:
    match = re.search(r"\b(?:fig(?:ure)?\.?|table)\s*([A-Za-z0-9]+)", caption, re.IGNORECASE)
    if match:
        prefix = "Table" if "table" in match.group(0).lower() else "Fig."
        return f"{prefix} {match.group(1)}"
    return f"candidate-{fallback_index:02d}"


def download_pdf(info: PaperInfo, paper_dir: Path, timeout: int) -> Path | None:
    pdf_dir = paper_dir / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = pdf_dir / f"{info.slug}.pdf"
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        return pdf_path
    try:
        response = requests.get(info.pdf_url, timeout=timeout, headers={"User-Agent": "paper-figure-atlas/1.0"})
        response.raise_for_status()
        pdf_path.write_bytes(response.content)
        return pdf_path
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Failed to download PDF for {info.arxiv_id}: {exc}", file=sys.stderr)
        return None


def run_checked(command: list[str]) -> bool:
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] Command failed: {' '.join(command)} :: {exc}", file=sys.stderr)
        return False


def extract_pdf_text(pdf_path: Path, paper_dir: Path, source_url: str) -> dict[str, Any] | None:
    if not shutil.which("pdftotext"):
        print("[WARN] pdftotext not found; skipping text extraction", file=sys.stderr)
        return None
    text_dir = paper_dir / "pdf_text"
    text_dir.mkdir(parents=True, exist_ok=True)
    text_path = text_dir / f"{pdf_path.stem}.txt"
    if run_checked(["pdftotext", "-layout", str(pdf_path), str(text_path)]):
        return {
            "source_type": "official-pdf-text",
            "source_url": source_url,
            "local_path": str(text_path.relative_to(paper_dir.parent)),
            "notes": "Extracted with pdftotext -layout for caption/table clues.",
        }
    return None


def extract_pdf_images(
    pdf_path: Path,
    paper_dir: Path,
    limit_assets: int,
    existing_count: int,
    source_url: str,
) -> list[dict[str, Any]]:
    if not shutil.which("pdfimages"):
        print("[WARN] pdfimages not found; skipping PDF image extraction", file=sys.stderr)
        return []
    image_dir = paper_dir / "pdf_images"
    image_dir.mkdir(parents=True, exist_ok=True)
    prefix = image_dir / "pdfimg"
    if not run_checked(["pdfimages", "-png", str(pdf_path), str(prefix)]):
        return []

    files = sorted(image_dir.glob("pdfimg-*"))
    if limit_assets:
        files = files[: max(0, limit_assets - existing_count)]

    assets: list[dict[str, Any]] = []
    for index, path in enumerate(files, start=1):
        if path.is_dir():
            continue
        role, confidence = infer_role(path.name)
        assets.append(
            {
                "paper_key": paper_dir.name,
                "asset_id": f"{paper_dir.name}:pdf-image:{index:02d}",
                "source_type": "official-pdf",
                "source_url": source_url,
                "local_path": str(path.relative_to(paper_dir.parent)),
                "figure_or_table_id": f"pdf-image-{index:02d}",
                "caption": "",
                "inferred_role": role,
                "confidence": confidence,
                "notes": "Extracted from PDF with pdfimages. Match against captions manually.",
            }
        )
    return assets


def parse_pages(raw_pages: str) -> list[int]:
    pages: list[int] = []
    for part in raw_pages.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit() or int(part) < 1:
            raise ValueError(f"Invalid page number: {part}")
        pages.append(int(part))
    return pages


def render_pdf_pages(pdf_path: Path, paper_dir: Path, pages: list[int], source_url: str) -> list[dict[str, Any]]:
    if not pages:
        return []
    if not shutil.which("pdftoppm"):
        print("[WARN] pdftoppm not found; skipping PDF page rendering", file=sys.stderr)
        return []
    render_dir = paper_dir / "pdf_pages"
    render_dir.mkdir(parents=True, exist_ok=True)
    assets: list[dict[str, Any]] = []
    for page in pages:
        prefix = render_dir / f"page{page:03d}"
        if run_checked(["pdftoppm", "-r", "220", "-png", "-f", str(page), "-l", str(page), str(pdf_path), str(prefix)]):
            output = render_dir / f"page{page:03d}-{page}.png"
            if not output.exists():
                matches = sorted(render_dir.glob(f"page{page:03d}-*.png"))
                output = matches[0] if matches else output
            if output.exists():
                assets.append(
                    {
                        "paper_key": paper_dir.name,
                        "asset_id": f"{paper_dir.name}:pdf-page:{page:03d}",
                        "source_type": "official-pdf-rendered-page",
                        "source_url": source_url,
                        "local_path": str(output.relative_to(paper_dir.parent)),
                        "figure_or_table_id": f"pdf-page-{page}",
                        "caption": "",
                        "inferred_role": "candidate",
                        "confidence": "low",
                        "notes": "Rendered full PDF page. Crop or inspect manually before embedding.",
                    }
                )
    return assets


def collect_one(raw_paper: str, output_dir: Path, args: argparse.Namespace) -> dict[str, Any]:
    arxiv_id, slug = normalize_arxiv(raw_paper)
    info = PaperInfo(
        raw_input=raw_paper,
        arxiv_id=arxiv_id,
        slug=slug,
        abs_url=f"https://arxiv.org/abs/{arxiv_id}",
        html_url=f"https://arxiv.org/html/{arxiv_id}",
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        source_url=f"https://arxiv.org/e-print/{arxiv_id}",
    )
    info = parse_abs_metadata(info, args.timeout)

    paper_dir = output_dir / slug
    paper_dir.mkdir(parents=True, exist_ok=True)

    assets: list[dict[str, Any]] = []
    if not args.skip_source:
        assets.extend(collect_source_assets(info, paper_dir, args.timeout, args.limit_assets, len(assets)))
    if not args.limit_assets or len(assets) < args.limit_assets:
        assets.extend(collect_html_assets(info, paper_dir, args.timeout, args.limit_assets - len(assets) if args.limit_assets else 0))
    text_artifacts: list[dict[str, Any]] = []

    pages = parse_pages(args.render_pages)
    needs_pdf = args.extract_pdf_images or args.extract_text or bool(pages)
    if needs_pdf:
        pdf_path = download_pdf(info, paper_dir, args.timeout)
        if pdf_path:
            if args.extract_text:
                text_artifact = extract_pdf_text(pdf_path, paper_dir, info.pdf_url)
                if text_artifact:
                    text_artifacts.append(text_artifact)
            if args.extract_pdf_images:
                assets.extend(extract_pdf_images(pdf_path, paper_dir, args.limit_assets, len(assets), info.pdf_url))
            if pages:
                assets.extend(render_pdf_pages(pdf_path, paper_dir, pages, info.pdf_url))

    return {
        "paper_key": slug,
        "input": raw_paper,
        "arxiv_id": arxiv_id,
        "title": info.title,
        "year": info.year,
        "authors": info.authors or [],
        "links": {
            "abs": info.abs_url,
            "html": info.html_url,
            "pdf": info.pdf_url,
            "source": info.source_url,
        },
        "assets": assets,
        "text_artifacts": text_artifacts,
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.out).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "paper-figure-atlas/scripts/collect_arxiv_assets.py",
        "papers": [],
    }

    failures = 0
    for raw_paper in args.paper:
        try:
            manifest["papers"].append(collect_one(raw_paper, output_dir, args))
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"[ERROR] Failed to collect {raw_paper}: {exc}", file=sys.stderr)

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Wrote manifest: {manifest_path}")
    for paper in manifest["papers"]:
        print(f"[OK] {paper['paper_key']}: {len(paper['assets'])} assets")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
