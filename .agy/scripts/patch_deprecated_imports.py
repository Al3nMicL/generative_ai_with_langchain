#!/usr/bin/env -S uv run
"""
Patch deprecated imports in chapter7/software_development.ipynb.

Replaces:
  from langchain.llms import HuggingFacePipeline
with:
  from langchain_huggingface import HuggingFacePipeline

Run from the project root:
  uv run .agy/scripts/patch_deprecated_imports.py
"""
import json
import sys
from pathlib import Path


PATCHES = [
    {
        "file": "chapter7/software_development.ipynb",
        "old": "from langchain.llms import HuggingFacePipeline",
        "new": "from langchain_huggingface import HuggingFacePipeline",
        "description": "HuggingFacePipeline moved to langchain_huggingface in LangChain 1.x",
    },
]


def patch_notebook(path: Path, old: str, new: str) -> int:
    """Patch all occurrences of `old` → `new` in notebook source cells.

    Returns the number of cells changed.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        new_source = []
        cell_changed = False
        for line in cell.get("source", []):
            if old in line:
                new_source.append(line.replace(old, new))
                cell_changed = True
            else:
                new_source.append(line)
        if cell_changed:
            cell["source"] = new_source
            changed += 1
    if changed:
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    return changed


def main() -> None:
    root = Path(__file__).parent.parent.parent  # project root
    total = 0
    for patch in PATCHES:
        nb_path = root / patch["file"]
        if not nb_path.exists():
            print(f"[SKIP] {patch['file']} not found")
            continue
        n = patch_notebook(nb_path, patch["old"], patch["new"])
        if n:
            print(f"[PATCHED] {patch['file']}: {n} cell(s) — {patch['description']}")
        else:
            print(f"[OK]     {patch['file']}: pattern not found (already patched?)")
        total += n

    if total:
        print(f"\nDone. {total} cell(s) patched.")
    else:
        print("\nDone. No changes needed.")


if __name__ == "__main__":
    main()
