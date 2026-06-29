# Research Project — Log

*Living doc. Edit anything. This is our shared memory so nothing leaks out between sessions.*

---

## Next single step
**Pick the learning entry point** (or tell me to verify courses first). Full design lives in `pipeline-design.md`.

> See `pipeline-design.md` for the full pipeline: tools, schema, keywords, concepts, learning resources.

---

## Open decision
- What is the collection *for*? (dataset+tool artifact, vs. a research question built on top)

## Current direction
- Exploring the **algorithm-collection data pipeline** first. (RL circuit synthesis is parked, not dropped — see Parked.)

---

## Decided / things we already know
- **Hardware is not the bottleneck.** Don't buy anything. M4 Mac mini (16 GB) is fine for inference, simulation, and small RL. Rent a cloud GPU by the hour *only* if I ever fine-tune a model >~3B.
- **Verifier-driven search beats LLM generation** for circuit discovery, because small circuits are cheaply, exactly simulable (~20–30 qubits on the Mac). The verifier defines the project, not the model.
- **If RL:** write the *environment* myself (gate set, state, reward, sim loop); use a *vetted* RL library (Stable-Baselines3 or CleanRL) — do NOT hand-roll PPO. Simulation via Qiskit / PennyLane.
- **RL make-or-break parts:** (1) reward shaping, (2) baselines — must compare against random search + a simple evolutionary/greedy baseline, or results mean nothing.
- **De-risking move:** start with a *tiny target that has a known optimal* (Toffoli, or a fixed 2–3 qubit unitary), so I can verify the agent and get a result even if RL loses.

---

## Parked / Candidates (not lost — just not chosen yet)
1. **RL circuit synthesis** — higher ceiling, higher risk. Real, publishable framing. Feasibility ~3/5. Hardware fine; difficulty is RL's silent failures + reward design.
2. **Collect ~2000 quantum algorithms (data pipeline)** — harvest papers (arXiv/OpenAlex/Semantic Scholar) → parse (GROBID/Nougat) → LLM structured extraction (local, Ollama/MLX) → dedup (embeddings) → SQLite + vector store → human QA. A solid data-engineering portfolio artifact, but it's "LLM as a tool," not the RL learning I wanted. Note: "2000 algorithms" is really ~2000 *papers*; there are only ~60ish algorithm families.
3. **Evolutionary / genetic programming over circuits** — lowest risk, $0, CPU-only, fully transparent. Good fallback or baseline.

---

## Constraints & context
- **Goal:** genuine publication / workshop paper or preprint — but framed as an *entry-level, learning-in-public* project. Every step published to GitHub + portfolio site. (Tension to watch: "learning project" and "novel enough to publish" pull in different directions — don't try to be both and satisfy neither.)
- **Time:** ~10 hrs/week, 6–10 weeks. Part-time, solo.
- **Money:** minimal. Local-first.
- **Machine:** M4 Mac mini, 16 GB unified RAM (≈10–11 GB usable for ML). No GPU/CUDA → Apple MLX or llama.cpp for local models.
- **Background:** BSc Physics; ~7 yrs translation / linguistic QA / AI data annotation / freelance LLM eval. Prior project: PQS benchmark (LLM scientific-reasoning eval).

---

## How we work together
- One decision at a time. Answer first, detail after.
- I hold the thread; flag shiny tangents so I can park or chase them on purpose.
- Recommend a default rather than a menu.
- This log = external working memory.
