#!/usr/bin/env python3
"""Download Langfuse screenshots from the source repo into data/langfuse_imgs/.

These images were originally produced while tracing the LangGraph pipeline.
Run once after clone (or whenever you need the PNGs locally):

    python scripts/extract_langfuse_imgs.py

Requires network access to GitHub.
"""

from __future__ import annotations

import urllib.request
from pathlib import Path

# Source: public raw URLs from the original project screenshots.
# Files are renamed to portfolio-friendly names.
SOURCES = {
    "trace_overview.png": (
        "https://raw.githubusercontent.com/yekta93/Generate-Query-Language/"
        "main/data/langfuse_imgs/image.png"
    ),
    "trace_detail_1.png": (
        "https://raw.githubusercontent.com/yekta93/Generate-Query-Language/"
        "main/data/langfuse_imgs/image%20(1).png"
    ),
    "trace_detail_2.png": (
        "https://raw.githubusercontent.com/yekta93/Generate-Query-Language/"
        "main/data/langfuse_imgs/image%20(2).png"
    ),
    "trace_detail_3.png": (
        "https://raw.githubusercontent.com/yekta93/Generate-Query-Language/"
        "main/data/langfuse_imgs/image%20(3).png"
    ),
    "trace_detail_4.png": (
        "https://raw.githubusercontent.com/yekta93/Generate-Query-Language/"
        "main/data/langfuse_imgs/image%20(4).png"
    ),
    "trace_detail_5.png": (
        "https://raw.githubusercontent.com/yekta93/Generate-Query-Language/"
        "main/data/langfuse_imgs/image%20(5).png"
    ),
}

DEST = Path(__file__).resolve().parents[1] / "data" / "langfuse_imgs"


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        path = DEST / name
        print(f"Downloading {name} ...")
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
        path.write_bytes(data)
        print(f"  → {path} ({len(data)} bytes)")
    print("Done. Images are in data/langfuse_imgs/")


if __name__ == "__main__":
    main()
