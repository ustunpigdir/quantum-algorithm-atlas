# Codex Prompt — Stage 0 scraper

Paste the block below to Codex.

---

Build a small, reproducible Python scraper that turns the Quantum Algorithm Zoo
into a structured seed dataset. This is Stage 0 of a research data pipeline, so
correctness, reproducibility, and provenance matter more than cleverness.

SOURCE
- https://quantumalgorithmzoo.org/  (single public HTML page; no API, no auth)
- Inspect the actual page structure before writing parsing logic. Entries are
  grouped under problem/topic headings; each algorithm entry typically has a
  name, a "Speedup" line, a prose description, and a list of references with
  hyperlinks. The HTML is somewhat irregular — parse defensively.

OUTPUT — write a CSV named `data/qaz_seed.csv` with these columns:
- id            (stable slug derived from the algorithm name)
- name          (algorithm name)
- category       (the problem/topic heading it falls under)
- speedup        (the stated speedup, e.g. "superpolynomial", "polynomial",
                  "quadratic"; empty string if not stated)
- techniques     (semicolon-separated primitives/techniques if mentioned,
                  else empty)
- description    (the entry's prose description, cleaned of HTML)
- reference_urls (semicolon-separated list of hyperlink URLs in the entry)
- source_url     (the page URL, with the entry anchor if one exists)

REQUIREMENTS
- Python 3.11+. Dependencies: httpx, beautifulsoup4, pandas. Pin them in a
  requirements.txt.
- Be polite: one request, set a descriptive User-Agent, add a short timeout.
- Save the raw fetched HTML to `raw/quantumalgorithmzoo.html` for provenance
  and reproducibility (so the parse can be re-run offline).
- Deterministic output: stable row order (sort by category, then name).
- Deduplicate by id.
- Robust parsing: never crash on a missing field — emit empty string instead.
- Light logging to stdout: total entries found, rows written, any entries
  skipped and why.
- At the end, print a summary: number of categories, number of algorithms,
  and how many have a non-empty speedup.

DELIVERABLES
- src/scrape_qaz.py    (the script; clear functions, brief comments)
- requirements.txt
- Update README.md with a one-paragraph "Stage 0" section: what it does + how to run.
- It must run on macOS (Apple Silicon) with: pip install -r requirements.txt
  then python src/scrape_qaz.py

ACCEPTANCE CHECK
- Running it produces data/qaz_seed.csv with at least ~40 algorithm rows and a
  non-empty category for each row. Print a clear PASS/FAIL line based on that.

Do not use any paid API or LLM call. Pure scraping + parsing only.
