# Algorithm-Collection Pipeline — Design

*Reference doc. Skim the headers, ignore what you don't need yet. Edit freely.*

---

## TL;DR — the shape of it
Seed from a known catalog → harvest paper metadata → cheap filter → fetch full text → AI extracts structured fields → dedup → store → you spot-check. Local-first, ~$0, runs on the Mac.

**One honest correction up front:** you don't need an "AI agent framework" (LangChain/AutoGPT-style). Those are opaque and fight your "control everything" goal. What you need is a **single local LLM used as an extractor + a yes/no classifier**, with a strict output schema. Simpler, cheaper, fully inspectable, and you'll actually learn what's happening.

---

## The pipeline, stage by stage

**Stage 0 — Seed.** Quantum Algorithm Zoo (the canonical catalog, ~60 families). Gives you a trusted backbone + reference list to snowball from.

**Stage 1 — Harvest metadata.** Pull paper records (title, abstract, authors, year, IDs).
- Tools: `arxiv` (Python), `pyalex` (OpenAlex), Semantic Scholar API. All free.
- Strategy: prefer **citation snowballing** from the Zoo's references over raw keyword search — much higher precision. Keyword search is the noisy fallback.

**Stage 2 — Cheap filter (before downloading anything).** Decide "is this plausibly a quantum-algorithm paper?" using only title+abstract.
- Tools: `rapidfuzz` (fuzzy title match for dedup), `sentence-transformers` (embed abstracts, keep ones close to your seed set).
- Only send *borderline* cases to the LLM. Saves huge compute.

**Stage 3 — Fetch full text.** Mostly arXiv (open). 
- Parse: **GROBID** (PDF → structured sections/refs, robust) or **Nougat** (PDF → markdown, good with math). `PyMuPDF` for quick raw text.

**Stage 4 — AI extraction (the core).** An LLM reads the paper, emits one structured JSON record (schema below).
- **Two ways to run the model — use both for different jobs:**
  - **OpenRouter (recommended for extraction):** one API key → many models (GPT, Claude, Gemini, plus open models like Qwen/Llama/DeepSeek). Lets you (a) use a stronger model than a local 7B for higher-quality extraction, (b) **A/B compare models cheaply** on the same papers, (c) sidestep the 16 GB limit. Cost for ~2000 papers on cheap models is low (cents-to-low-dollars range with small models; verify current per-token prices before a big run). Keeps "minimal spend" honest if you pick cheap models.
  - **Local (Ollama / MLX) as the $0 baseline:** Qwen2.5-7B-Instruct or Llama-3.1-8B, quantized (Q4/Q5), fits 16 GB. Free, fully private, slower. Good default for bulk runs once a prompt is dialed in.
- **Smart split:** prototype + pick the best extractor via OpenRouter on a small sample → run the bulk locally for free, OR keep using a cheap OpenRouter model if quality matters more than cost. The model comparison itself is a nice publishable/portfolio detail.
- Structured output: **Instructor** or **Outlines** with a Pydantic schema → forces consistent fields, no free-text mess. Works the same against OpenRouter or local.

**Model access I actually have (use in the comparison):**
- **OpenRouter** — broad menu, one key, for A/B testing many models.
- **DeepSeek API** (direct) — very cheap, strong reasoning; good cheap-but-capable extractor.
- **Mistral API** (direct) — solid, cheap; another comparison point.
- **Local (Ollama/MLX)** — Qwen2.5-7B / Llama-3.1-8B, $0 bulk baseline.
→ This is a ready-made **model panel**: run the same extraction prompt across DeepSeek, Mistral, a local 7B, and 1–2 OpenRouter models on a small labeled sample, measure agreement vs your human checks, then pick the winner for the bulk run. The eval *is* a portfolio asset.

**Stage 5 — Dedup + classify.** Collapse duplicates/variants (embeddings + fuzzy match). Tag family/category.

**Stage 6 — Store.** **SQLite** for structured records + **Chroma** or **LanceDB** for semantic search. Both local, free, inspectable.

**Stage 7 — Human QA.** You spot-check a sample against sources. This is your edge (annotation/eval background) and what makes the dataset trustworthy enough to publish.

**Orchestration:** plain Python scripts + a `Makefile` or simple runner. Do NOT add Airflow/Prefect — overkill, and you want to *see* every step.

---

## What to look for while extracting (the schema)
This is the heart of the project — decide these fields and the rest follows.

| Field | What it captures |
|---|---|
| `name` / `aliases` | Algorithm name + other names used |
| `problem` | The task it solves |
| `family` | search / factoring / simulation / optimization / linear algebra / QML / … |
| `primitives` | QFT, amplitude amplification, phase estimation, quantum walk, … |
| `speedup_type` | none / quadratic (Grover) / polynomial / exponential / heuristic |
| `complexity` | quantum vs classical cost, as stated |
| `inputs_outputs` | what goes in / comes out |
| `assumptions` | oracle access, QRAM, fault-tolerance, etc. |
| `hardware_regime` | NISQ vs fault-tolerant |
| `novelty` | new algorithm / variant / application of an existing one |
| `source` | arXiv id, DOI, year, authors |
| `provenance` | which section the LLM pulled each claim from + confidence |

`provenance` matters: it lets you audit the AI and is a credibility point in a paper.

---

## Keywords & search strategy
**Primary category:** `quant-ph`. **Also sweep:** `cs.DS`, `cs.CC`, `cs.ET`, `cs.LG` (for QML).

**Seed terms:** quantum algorithm, quantum speedup, amplitude amplification, quantum walk, phase estimation, Hamiltonian simulation, linear systems / HHL, Grover, Shor, QAOA, variational quantum, quantum optimization, query complexity, oracle, fault-tolerant algorithm, near-term algorithm, quantum machine learning.

**Method, ranked by precision:**
1. Snowball from Zoo references (best signal).
2. Citation expansion via OpenAlex/Semantic Scholar.
3. Keyword search (broadest, noisiest — filter hard in Stage 2).

---

## Concepts to learn (paired to the stage that needs them)
You don't need all of this before starting — learn each just-in-time, as its stage comes up.

**Engineering / ML track**
- Python data wrangling (`pandas` or `polars`) — Stages 1–6
- Calling REST APIs: pagination, rate limits — Stage 1
- Embeddings & cosine similarity (what a vector *is*) — Stages 2, 5
- Structured LLM prompting / output schemas — Stage 4
- Dedup: fuzzy matching vs embedding similarity — Stage 5
- SQLite + simple schema design — Stage 6
- Reproducibility: git, virtual envs, logging — throughout

**Quantum-domain track (only enough to label correctly — you have the physics base)**
- Speedup types & query complexity
- The core primitives (QFT, amplitude amplification, phase estimation, walks)
- Algorithm-family taxonomy
- NISQ vs fault-tolerant regimes

---

## AuDHD-friendly learning approach
Format matters more than the specific course. What tends to work: **short modular lessons** (finish one in a sitting → dopamine), **project-first** (learn by doing the actual pipeline, not abstract theory upfront), **captioned/self-paced**, and **interactive notebooks** over long lecture videos.

Resources that fit those criteria (well-known, stable — *I'll verify current links/availability before you commit*):
- **Kaggle Learn** — bite-sized, hands-on micro-courses (Python, Pandas, Intro to ML, embeddings). Hours, not weeks.
- **fast.ai** — top-down, build-first; good for ADHD because you ship something early.
- **IBM Quantum Learning / Qiskit textbook** — interactive, for the quantum-concepts track.
- **freeCodeCamp** — project-based Python/data.

> Next-step option: I can run a proper search and build a *verified* shortlist matched to each concept above (current, free, AuDHD-friendly). Say the word.

---

## Reality checks to keep in view
- "2000 algorithms" ≈ ~2000 *papers*; real distinct algorithm families number in the dozens-to-low-hundreds. The dataset's value is in structure + dedup, not raw count.
- The hard part is **schema design + extraction QA**, not the tools. Budget your energy there.
- The collection is the artifact; the *publishable* part is what you measure on top of it (parked decision — don't forget it).
