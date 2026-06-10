#!/usr/bin/env python3
"""Validate local image embeds and manifest paths in an Obsidian figure atlas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


WIKILINK_EMBED_RE = re.compile(r"!\[\[([^\]\|#]+)(?:[|#][^\]]*)?\]\]")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


@dataclass
class MissingRef:
    markdown: Path
    reference: str
    kind: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that Obsidian image embeds and manifest local paths exist.",
    )
    parser.add_argument("markdown", nargs="+", help="Markdown file(s) to validate.")
    parser.add_argument(
        "--vault-root",
        default="",
        help="Optional vault root for vault-root-relative wikilinks.",
    )
    parser.add_argument(
        "--manifest",
        action="append",
        default=[],
        help="Optional manifest.json path. Repeat for multiple manifests.",
    )
    return parser.parse_args()


def is_external(path_text: str) -> bool:
    parsed = urlparse(path_text)
    return parsed.scheme in {"http", "https", "mailto", "obsidian"}


def normalize_markdown_path(path_text: str) -> str:
    text = path_text.strip().strip("<>")
    if " " in text and text.startswith("./"):
        return unquote(text)
    return unquote(text)


def candidate_paths(reference: str, markdown_path: Path, vault_root: Path | None) -> list[Path]:
    ref = normalize_markdown_path(reference)
    path = Path(ref)
    if path.is_absolute():
        return [path]

    candidates = [markdown_path.parent / path]
    if vault_root:
        candidates.append(vault_root / path)

    # Obsidian wikilinks often omit folders. Searching by basename keeps validation useful
    # without pretending the link is definitely correct.
    search_roots = [markdown_path.parent]
    if vault_root and vault_root not in search_roots:
        search_roots.append(vault_root)
    for root in search_roots:
        if root.exists():
            candidates.extend(root.rglob(path.name))

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.expanduser()
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def exists(reference: str, markdown_path: Path, vault_root: Path | None) -> bool:
    if is_external(reference):
        return True
    return any(path.exists() for path in candidate_paths(reference, markdown_path, vault_root))


def validate_markdown(markdown_path: Path, vault_root: Path | None) -> tuple[int, list[MissingRef]]:
    text = markdown_path.read_text(encoding="utf-8")
    total = 0
    missing: list[MissingRef] = []

    for match in WIKILINK_EMBED_RE.finditer(text):
        ref = match.group(1).strip()
        total += 1
        if not exists(ref, markdown_path, vault_root):
            missing.append(MissingRef(markdown_path, ref, "wikilink-embed"))

    for match in MARKDOWN_IMAGE_RE.finditer(text):
        ref = normalize_markdown_path(match.group(1))
        total += 1
        if not exists(ref, markdown_path, vault_root):
            missing.append(MissingRef(markdown_path, ref, "markdown-image"))

    return total, missing


def iter_manifest_asset_paths(manifest_path: Path) -> list[str]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths: list[str] = []
    for paper in data.get("papers", []):
        for asset in paper.get("assets", []):
            local_path = asset.get("local_path")
            if isinstance(local_path, str) and local_path:
                paths.append(local_path)
        for artifact in paper.get("text_artifacts", []):
            local_path = artifact.get("local_path")
            if isinstance(local_path, str) and local_path:
                paths.append(local_path)
    return paths


def validate_manifest(manifest_path: Path) -> tuple[int, list[str]]:
    missing: list[str] = []
    paths = iter_manifest_asset_paths(manifest_path)
    for local_path in paths:
        candidate = (manifest_path.parent / local_path).expanduser()
        if not candidate.exists():
            missing.append(local_path)
    return len(paths), missing


def main() -> int:
    args = parse_args()
    vault_root = Path(args.vault_root).expanduser().resolve() if args.vault_root else None

    total_refs = 0
    missing_refs: list[MissingRef] = []
    for raw_markdown in args.markdown:
        markdown_path = Path(raw_markdown).expanduser().resolve()
        if not markdown_path.exists():
            print(f"[ERROR] Markdown not found: {markdown_path}", file=sys.stderr)
            return 1
        count, missing = validate_markdown(markdown_path, vault_root)
        total_refs += count
        missing_refs.extend(missing)

    total_manifest_paths = 0
    missing_manifest_paths: list[tuple[Path, str]] = []
    for raw_manifest in args.manifest:
        manifest_path = Path(raw_manifest).expanduser().resolve()
        if not manifest_path.exists():
            print(f"[ERROR] Manifest not found: {manifest_path}", file=sys.stderr)
            return 1
        count, missing = validate_manifest(manifest_path)
        total_manifest_paths += count
        missing_manifest_paths.extend((manifest_path, path) for path in missing)

    print(f"[OK] Checked markdown image refs: {total_refs}")
    if args.manifest:
        print(f"[OK] Checked manifest local paths: {total_manifest_paths}")

    if missing_refs or missing_manifest_paths:
        for item in missing_refs:
            print(f"[MISSING] {item.markdown}: {item.kind}: {item.reference}", file=sys.stderr)
        for manifest_path, local_path in missing_manifest_paths:
            print(f"[MISSING] {manifest_path}: manifest local_path: {local_path}", file=sys.stderr)
        return 1

    print("[OK] No missing local assets found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
