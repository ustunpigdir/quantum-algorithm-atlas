# Quantum Algorithm Atlas

A self-driven, build-in-public research project: harvest published quantum
algorithms from the literature and turn them into a clean, structured,
searchable dataset — then measure what the landscape looks like.

> Status: **Stage 0 — seed dataset.** Early days. Every step is published.

## Why
There is no single machine-readable catalog of quantum algorithms with their
problems, speedups, primitives, and assumptions laid out consistently. This
project builds one, with an auditable, reproducible pipeline — and uses it as a
vehicle for learning ML/data engineering in the open.

## Pipeline (high level)
0. **Seed** — scrape the Quantum Algorithm Zoo into a structured table.
1. **Harvest** — pull paper metadata (arXiv, OpenAlex, Semantic Scholar).
2. **Filter** — cheap metadata + embedding filter before downloading PDFs.
3. **Extract** — an LLM reads each paper, emits a structured record (schema in docs).
4. **Dedup + classify** — collapse duplicates, tag families.
5. **Store** — SQLite + a vector store.
6. **QA** — human spot-checks.

Full design, schema, tooling, keywords, and the model panel:
see [`pipeline-design.md`](./pipeline-design.md).
Working decisions + parked ideas: see [`project-log.md`](./project-log.md).

## Repo layout
```
.
├── README.md
├── project-log.md            # living decision log
├── pipeline-design.md        # full pipeline design
├── codex-stage0-prompt.md    # prompt used to generate the Stage 0 scraper
├── src/                      # code (Stage 0 scraper goes here)
├── data/                     # structured outputs (e.g. qaz_seed.csv)
└── raw/                      # raw fetched sources, for provenance
```

## Running Stage 0
Stage 0 fetches the public Quantum Algorithm Zoo page, saves the raw HTML for provenance, and turns the catalog into a deterministic CSV seed dataset at data/qaz_seed.csv. The scraper is defensive about irregular markup, writes stable rows sorted by category and name, and prints a short summary of how many algorithms and categories were recovered. Run it from the repository root with:
```
pip install -r requirements.txt
python src/scrape_qaz.py
```

## Constraints / ethos
Local-first, minimal spend, fully reproducible, every step inspectable.
Runs on a Mac mini (M4, 16 GB). No GPU required.

## License
MIT — see [`LICENSE`](./LICENSE).
