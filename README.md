# DRAFTRON

AI cover-letter agent. LangGraph pipeline with human-in-the-loop review. Groq for
structured extraction/matching/critique, OpenAI for draft generation. Streamlit frontend.

Architecture: intake → JD extraction → profile matching → strategy → draft generation →
self-critique → **human review** (`interrupt()`) → revision/finalize.

---

## Structure

```
draftron/
├── app.py                      # Streamlit entrypoint (WIP)
├── main.py                     # CLI stub
├── graph/
│   ├── state.py                # CoverLetterState + Pydantic schemas
│   ├── builder.py              # DraftronGraph — assembles & compiles StateGraph
│   ├── edges.py                # route_after_review() conditional routing
│   └── nodes/
│       ├── intake.py
│       ├── jd_extractor.py
│       ├── profile_matcher.py
│       ├── strategy.py
│       ├── draft_generator.py
│       ├── self_critique.py
│       ├── human_review.py     # interrupt() node
│       ├── revision.py
│       └── finalize.py
├── models/router.py            # Groq / OpenAI client factory
├── prompts/                    # Externalized system prompts
├── data/
│   ├── profile.json            # Your structured master profile
│   └── applications_log.jsonl  # Append-only application record (gitignored)
├── outputs/                    # Generated cover letters (gitignored)
├── tests/                      # Per-day node & graph tests
├── DRAFTRON_build_guide.md     # Day-by-day build guide
├── requirements.txt
└── pyproject.toml
```

---

## Setup

```bash
# 1. Clone & enter
cd draftron

# 2. Create venv (Python >=3.10)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install deps
pip install -r requirements.txt
```

---

## Environment

Copy `.env.example` → `.env` and fill in keys:

```bash
cp .env.example .env
```

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Extraction, matching, critique (cheap) |
| `OPENAI_API_KEY` | Draft generation & revision (quality) |
| `OPENROUTER_API_KEY` | Optional escape hatch for A/B testing |
| `DRAFTRON_GEN_MODEL` | Generator model, default: `gpt-4.1-mini` |

---

## Running

**Day-by-day node tests** (recommended while building):
```bash
python tests/verify_day1.py   # profile + state validation
python tests/test_day2.py     # intake + JD extraction
python tests/test_day3.py     # matching + strategy
python tests/test_day4.py     # draft + critique
```

**Full graph test** (interrupt/resume):
```bash
python tests/test_graph.py
```

**Streamlit UI** (work in progress):
```bash
streamlit run app.py
```

---

## Model Routing

| Task | Model | Why |
|------|-------|-----|
| JD extraction | `llama-3.3-70b-versatile` @ Groq | Structured output, zero temp |
| Profile matching | `llama-3.3-70b-versatile` @ Groq | Fast, honest gap-flagging |
| Draft generation | OpenAI (`gpt-4.1-mini` default) | Quality matters here |
| Self-critique | `llama-3.3-70b-versatile` @ Groq | Cheap rubric check |
| Revision | OpenAI (`gpt-4.1-mini` default) | Quality rewrite |

Swap the generator model without touching code:
```bash
DRAFTRON_GEN_MODEL=gpt-4o-mini streamlit run app.py
```

---

## Human Review Flow

`graph/nodes/human_review.py` uses `interrupt()` for Streamlit-safe
human-in-the-loop decisions:

- **Approve** → writes to `outputs/` + logs to `data/applications_log.jsonl`
- **Edit** → revision with your feedback → re-critique → review again
- **Regenerate** → back to `draft_generator` with same strategy
- **Reject** → pipeline ends, nothing saved

---

## Build Guide

For the day-by-day implementation plan, design decisions, and worked examples, see
`DRAFTRON_build_guide.md`.
