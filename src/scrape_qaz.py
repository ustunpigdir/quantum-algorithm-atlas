#!/usr/bin/env python3
"""Scrape the Quantum Algorithm Zoo into a structured seed dataset."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Dict, Optional

import httpx
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
RAW_HTML = ROOT / "raw" / "quantumalgorithmzoo.html"
OUTPUT_CSV = ROOT / "data" / "qaz_seed.csv"
SOURCE_URL = "https://quantumalgorithmzoo.org/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}
TIMEOUT = 20.0


def slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "algorithm"


def clean_text(value: str) -> str:
    if not value:
        return ""
    text = re.sub(r"\s+", " ", value)
    return text.strip()


def normalize_label(tag: object) -> str:
    if tag is None:
        return ""
    return clean_text(tag.get_text(" ", strip=True)).lower()


def extract_entry_anchor(html: str, start_index: int) -> str:
    if start_index <= 0:
        return ""
    anchor_match = re.search(r"<(?:a|span)\s+[^>]*(?:id|name)=['\"]([^'\"]+)['\"][^>]*>", html[:start_index], re.I)
    return anchor_match.group(1) if anchor_match else ""


def parse_entry(html: str, block: str, category: str, source_url: str, start_index: int) -> tuple[Optional[Dict[str, str]], str]:
    if not block:
        return None, "empty block"

    name = ""
    speedup = ""
    description = ""
    reference_urls: List[str] = []
    techniques: List[str] = []

    name_match = re.search(r"<b[^>]*>\s*Algorithm:\s*</b>\s*(.*?)\s*(?:<br>|$)", block, re.I | re.S)
    if name_match:
        name = clean_text(BeautifulSoup(name_match.group(1), "html.parser").get_text(" ", strip=True))

    speedup_match = re.search(r"<b[^>]*>\s*Speedup:\s*</b>\s*(.*?)\s*(?:<br>|$)", block, re.I | re.S)
    if speedup_match:
        speedup = clean_text(BeautifulSoup(speedup_match.group(1), "html.parser").get_text(" ", strip=True))

    description_match = re.search(r"<b[^>]*>\s*Description:\s*</b>\s*(.*?)(?=<br>\s*<br>|<br>\s*</?b>|</p>|$)", block, re.I | re.S)
    if description_match:
        description_html = description_match.group(1)
        description = clean_text(BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True))

    entry_soup = BeautifulSoup(block, "html.parser")
    for link in entry_soup.find_all("a", href=True):
        href = link.get("href", "")
        if href.startswith(("http://", "https://")):
            reference_urls.append(href)

    description_text = description.lower()
    technique_patterns = [
        "quantum Fourier transform",
        "grover search",
        "phase estimation",
        "quantum walk",
        "amplitude amplification",
        "hamiltonian simulation",
        "adiabatic",
        "variational",
        "matrix product",
        "tensor network",
        "semidefinite",
        "qft",
        "quantum annealing",
    ]
    for pattern in technique_patterns:
        if pattern in description_text:
            techniques.append(pattern)

    if not name:
        return None, "missing name"

    return {
        "id": slugify(name),
        "name": name,
        "category": category,
        "speedup": speedup,
        "techniques": "; ".join(techniques),
        "description": description,
        "reference_urls": "; ".join(dict.fromkeys(reference_urls)),
        "source_url": f"{source_url}#{anchor}" if (anchor := extract_entry_anchor(html, start_index)) else source_url,
    }, ""


def fetch_html() -> str:
    if RAW_HTML.exists():
        return RAW_HTML.read_text(encoding="utf-8")

    try:
        response = httpx.get(SOURCE_URL, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        response.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"Failed to fetch source page and no cached HTML exists: {exc}") from exc

    RAW_HTML.parent.mkdir(parents=True, exist_ok=True)
    RAW_HTML.write_text(response.text, encoding="utf-8")
    return response.text


def parse_algorithms(html: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    skipped: List[str] = []
    seen_ids: set[str] = set()

    marker_pattern = re.compile(r"<b[^>]*>\s*Algorithm:\s*</b>", re.I)
    markers = list(marker_pattern.finditer(html))
    print(f"Found {len(markers)} algorithm markers")

    for index, marker in enumerate(markers):
        start_index = marker.start()
        end_index = markers[index + 1].start() if index + 1 < len(markers) else len(html)
        block = html[start_index:end_index]

        category = ""
        heading_matches = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", html[:start_index], re.I | re.S))
        if heading_matches:
            category = clean_text(BeautifulSoup(heading_matches[-1].group(1), "html.parser").get_text(" ", strip=True))

        entry, reason = parse_entry(html, block, category, SOURCE_URL, start_index)
        if entry is None:
            skipped.append(f"entry {index + 1}: {reason}")
            continue

        if entry["id"] in seen_ids:
            skipped.append(f"entry {index + 1}: duplicate id {entry['id']}")
            continue

        seen_ids.add(entry["id"])
        rows.append(entry)

    rows.sort(key=lambda row: (row["category"].lower(), row["name"].lower()))
    print(f"Rows written: {len(rows)}")
    if skipped:
        print(f"Skipped entries with reasons: {len(skipped)}")
        for item in skipped:
            print(f"- {item}")
    else:
        print("Skipped entries with reasons: 0")
    return rows


def write_csv(rows: List[Dict[str, str]]) -> None:
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows, columns=[
        "id",
        "name",
        "category",
        "speedup",
        "techniques",
        "description",
        "reference_urls",
        "source_url",
    ])
    df.to_csv(OUTPUT_CSV, index=False)


def main() -> int:
    html = fetch_html()
    rows = parse_algorithms(html)
    write_csv(rows)

    print(f"Rows written: {len(rows)}")
    print(f"Categories: {len({row['category'] for row in rows if row['category']})}")
    print(f"Algorithms with non-empty speedup: {sum(1 for row in rows if row['speedup'])}")

    if len(rows) >= 40 and all(row["category"] for row in rows):
        print("PASS: dataset contains at least 40 algorithms with a non-empty category")
    else:
        print("FAIL: dataset does not meet the minimum size or category requirement")

    return 0


if __name__ == "__main__":
    sys.exit(main())
