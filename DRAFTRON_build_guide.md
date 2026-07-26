# DRAFTRON — Build Guide (Week 1 of the Agent Challenge)

Cover letter agent. LangGraph + human-in-the-loop via `interrupt()`. Groq for the
cheap/structured work, OpenAI for the one node where quality actually matters, Streamlit
as the front end.

---

## 1. Directory structure

```
draftron/
├── .env                          # API keys — gitignored
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── app.py                        # Streamlit entrypoint

├── graph/
│   ├── __init__.py
│   ├── state.py                  # CoverLetterState TypedDict + Pydantic schemas
│   ├── builder.py                # DraftronGraph class — assembles + compiles the StateGraph
│   ├── edges.py                  # route_after_review() conditional routing
│   └── nodes/
│       ├── __init__.py
│       ├── intake.py
│       ├── jd_extractor.py
│       ├── profile_matcher.py
│       ├── strategy.py
│       ├── draft_generator.py
│       ├── self_critique.py
│       ├── human_review.py
│       ├── revision.py
│       └── finalize.py

├── models/
│   ├── __init__.py
│   └── router.py                 # Groq / OpenAI / OpenRouter client factory

├── prompts/                      # externalized system prompts, not buried in code
│   ├── jd_extraction.md
│   ├── profile_matching.md
│   ├── strategy.md
│   ├── draft_generation.md
│   ├── self_critique.md
│   └── revision.md

├── data/
│   ├── profile.json               # your structured master profile — CV, skills, projects
│   └── applications_log.jsonl     # append-only record of every generated application

├── outputs/                       # generated cover letters land here — gitignored

└── tests/
    ├── test_nodes.py               # standalone node tests (Day 2–4)
    └── test_graph.py               # full graph + interrupt/resume tests (Day 5)
```

`requirements.txt`:

```
langgraph>=1.2
langchain>=1.0
langchain-openai
langchain-groq
langgraph-checkpoint-sqlite
streamlit
pydantic>=2
python-dotenv
```

---



## 2. State and schemas — `graph/state.py`

```python
from typing import TypedDict, Literal, Optional
from pydantic import BaseModel, Field

class CoverLetterState(TypedDict, total=False):
    job_posting_raw: str
    company_name: str
    role_title: str
    jd_structured: dict
    candidate_profile: dict
    matched_skills: list[str]
    skill_gaps: list[str]
    relevant_projects: list[str]
    strategy: dict
    draft: str
    critique: dict
    revision_count: int
    human_feedback: Optional[str]
    decision: Literal["approve", "edit", "regenerate", "reject"]
    final_letter: str

class JDExtraction(BaseModel):
    company_name: str
    role_title: str
    seniority: str
    required_skills: list[str]
    nice_to_have_skills: list[str] = Field(default_factory=list)
    culture_signals: list[str] = Field(default_factory=list)
    key_responsibilities: list[str]

class ProfileMatch(BaseModel):
    matched_skills: list[str]
    skill_gaps: list[str]
    relevant_projects: list[str]
    strongest_angle: str

class CritiqueResult(BaseModel):
    passes: bool
    overstatement_flags: list[str] = Field(default_factory=list)
    length_flag: bool
    tone_flag: bool
    notes: str
```

`data/profile.json` is the ground truth the matcher checks the JD against — your real
skills, real projects (LAPIS V2, DRAFTRON itself, the CV certs), and honest experience
tenure. This is what keeps `profile_matcher` from ever inventing a skill gap doesn't exist.

---



## 3. Model router — `models/router.py`

```python
import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

GROQ_MODEL = "llama-3.3-70b-versatile"
DRAFT_MODEL = os.getenv("DRAFTRON_GEN_MODEL", "gpt-4o-mini")

def get_extraction_model():
    return ChatGroq(model=GROQ_MODEL, temperature=0)

def get_matching_model():
    return ChatGroq(model=GROQ_MODEL, temperature=0.2)

def get_generation_model():
    return ChatOpenAI(model=DRAFT_MODEL, temperature=0.7)

def get_critique_model():
    return ChatGroq(model=GROQ_MODEL, temperature=0)

def get_openrouter_model(model_name: str):
    # escape hatch for A/B testing generation quality — same interface,
    # this is also the pattern NEXARA will reuse in Week 6
    return ChatOpenAI(
        model=model_name,
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
```

Swapping the generator model later (e.g. to `gpt-5.4-mini` for a quality bump) is a one-line
env var change — nothing in the graph touches this.

---



## 4. Nodes

Each node is a plain function: takes `CoverLetterState`, returns a partial-state dict
(LangGraph's convention — not classes; classes are reserved for the schemas and the graph
wrapper below).

```python
# graph/nodes/jd_extractor.py
from graph.state import JDExtraction
from models.router import get_extraction_model

def jd_extractor_node(state: CoverLetterState) -> dict:
    model = get_extraction_model().with_structured_output(JDExtraction)
    result = model.invoke(f"Extract structured data from this job posting:\n\n{state['job_posting_raw']}")
    return {
        "company_name": result.company_name,
        "role_title": result.role_title,
        "jd_structured": result.model_dump(),
    }
```

```python
# graph/nodes/human_review.py
from langgraph.types import interrupt

def human_review_node(state: CoverLetterState) -> dict:
    response = interrupt({
        "draft": state["draft"],
        "critique": state["critique"],
        "revision_count": state.get("revision_count", 0),
    })
    # response shape from the UI: {"decision": "approve"|"edit"|"regenerate"|"reject", "feedback": str|None}
    return {
        "decision": response["decision"],
        "human_feedback": response.get("feedback"),
    }
```

```python
# graph/edges.py
from typing import Literal
from graph.state import CoverLetterState

def route_after_review(state: CoverLetterState) -> Literal["approve", "edit", "regenerate", "reject"]:
    return state["decision"]
```


| Node              | Job                                        | Model      | Reads                                | Writes                                              |
| ----------------- | ------------------------------------------ | ---------- | ------------------------------------ | --------------------------------------------------- |
| `intake`          | Load posting + profile.json                | none       | `job_posting_raw`                    | `candidate_profile`                                 |
| `jd_extractor`    | Structured JD parse                        | Groq       | `job_posting_raw`                    | `jd_structured`, `company_name`, `role_title`       |
| `profile_matcher` | Match skills/projects, flag gaps           | Groq       | `jd_structured`, `candidate_profile` | `matched_skills`, `skill_gaps`, `relevant_projects` |
| `strategy`        | Pick angle, tone, lead project             | Groq       | matcher output                       | `strategy`                                          |
| `draft_generator` | Write the letter                           | **OpenAI** | `strategy`, matcher output           | `draft`                                             |
| `self_critique`   | Rubric check (overstatement, length, tone) | Groq       | `draft`, `skill_gaps`                | `critique`                                          |
| `human_review`    | `interrupt()` — you decide                 | none       | `draft`, `critique`                  | `decision`, `human_feedback`                        |
| `revision`        | Regenerate using your feedback             | **OpenAI** | `human_feedback`, `draft`            | `draft` (+`revision_count`)                         |
| `finalize`        | Save file + log the application            | none       | `draft`                              | `final_letter`                                      |


---



## 5. Graph assembly — `graph/builder.py`

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from graph.state import CoverLetterState
from graph.edges import route_after_review
from graph.nodes.intake import intake_node
from graph.nodes.jd_extractor import jd_extractor_node
from graph.nodes.profile_matcher import profile_matcher_node
from graph.nodes.strategy import strategy_node
from graph.nodes.draft_generator import draft_generator_node
from graph.nodes.self_critique import self_critique_node
from graph.nodes.human_review import human_review_node
from graph.nodes.revision import revision_node
from graph.nodes.finalize import finalize_node

class DraftronGraph:
    def __init__(self, checkpointer=None):
        self.checkpointer = checkpointer or InMemorySaver()
        self.graph = self._build().compile(checkpointer=self.checkpointer)

    def _build(self) -> StateGraph:
        g = StateGraph(CoverLetterState)
        g.add_node("intake", intake_node)
        g.add_node("jd_extractor", jd_extractor_node)
        g.add_node("profile_matcher", profile_matcher_node)
        g.add_node("strategy", strategy_node)
        g.add_node("draft_generator", draft_generator_node)
        g.add_node("self_critique", self_critique_node)
        g.add_node("human_review", human_review_node)
        g.add_node("revision", revision_node)
        g.add_node("finalize", finalize_node)

        g.add_edge(START, "intake")
        g.add_edge("intake", "jd_extractor")
        g.add_edge("jd_extractor", "profile_matcher")
        g.add_edge("profile_matcher", "strategy")
        g.add_edge("strategy", "draft_generator")
        g.add_edge("draft_generator", "self_critique")
        g.add_edge("self_critique", "human_review")
        g.add_conditional_edges("human_review", route_after_review, {
            "approve": "finalize",
            "edit": "revision",
            "regenerate": "draft_generator",
            "reject": END,
        })
        g.add_edge("revision", "self_critique")   # re-checked before you see it again
        g.add_edge("finalize", END)
        return g

    def start(self, job_posting: str, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke({"job_posting_raw": job_posting}, config=config)

    def resume(self, resume_value: dict, thread_id: str):
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(Command(resume=resume_value), config=config)
```

Wrapping the graph in a class (rather than a loose `compile()` call in `app.py`) is
deliberate — Week 6's NEXARA will need to call DRAFTRON as a sub-agent, and `.start()` /
`.resume()` is the interface that makes that a clean handoff instead of a rewrite.

---



## 6. Streamlit wiring — the one gotcha

Streamlit reruns the **entire script** on every interaction. If you build the graph fresh
each rerun, your checkpointer's memory resets and the interrupted thread is lost. Fix:
cache the graph and keep the thread id in session state.

```python
# app.py
import uuid, streamlit as st
from graph.builder import DraftronGraph

@st.cache_resource
def get_app():
    return DraftronGraph()

app = get_app()
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

job_posting = st.text_area("Paste job posting")

if st.button("Generate") and job_posting:
    st.session_state.result = app.start(job_posting, st.session_state.thread_id)

result = st.session_state.get("result")
if result and "__interrupt__" in result:
    payload = result["__interrupt__"][0].value
    st.markdown(payload["draft"])
    st.caption(f"Critique: {payload['critique']}")

    c1, c2, c3, c4 = st.columns(4)
    feedback = st.text_area("Feedback (for Edit)")
    if c1.button("Approve"):
        st.session_state.result = app.resume({"decision": "approve"}, st.session_state.thread_id)
    if c2.button("Edit"):
        st.session_state.result = app.resume({"decision": "edit", "feedback": feedback}, st.session_state.thread_id)
    if c3.button("Regenerate"):
        st.session_state.result = app.resume({"decision": "regenerate"}, st.session_state.thread_id)
    if c4.button("Reject"):
        st.session_state.result = app.resume({"decision": "reject"}, st.session_state.thread_id)
```

Use `InMemorySaver` for local dev — it survives reruns because it lives inside the cached
`DraftronGraph` instance. Switch to `SqliteSaver` only if you need a review to survive
closing the browser entirely.

---



## 7. Day-by-day (7 days)

**Day 1 — Skeleton + data model**
Scaffold the folder structure above, set up the venv, install `requirements.txt`. Get
OpenAI and Groq API keys into `.env`. Build `data/profile.json` — your real skills,
projects (including LAPIS V2 and DRAFTRON itself), and certifications, structured so
`profile_matcher` can query it. Write `graph/state.py` in full. *Done when:* `profile.json`
validates and you can print it.

**Day 2 — Router + first two nodes**
Write `models/router.py`. Write `intake_node` and `jd_extractor_node`. Test each function
standalone with a hardcoded fake job posting — no graph yet, just call the function and
print the output. *Done when:* `jd_extractor_node` reliably returns clean structured JSON
from three different pasted postings.

**Day 3 — Matching and strategy**
Write `profile_matcher_node` and `strategy_node`. Run them against 2–3 different fake
postings (one EdTech/virtual-lab flavored, one generic AI Engineer) and check that LAPIS
surfaces when relevant and doesn't when it isn't. *Done when:* the gap-flagging is honest —
it should flag things you haven't actually used, not smooth them over.

**Day 4 — Draft generation and critique**
Write `prompts/draft_generation.md` (see below) and `draft_generator_node`. Write the
critique rubric and `self_critique_node`. Chain all five nodes manually (no graph) and
read the output critically — this is the day quality either clicks or doesn't. *Done when:*
you'd actually send one of these letters.

**Day 5 — Wire the graph**
Build `graph/builder.py`, `human_review_node`, `edges.py`. Test purely in a Python script
with `InMemorySaver` and a fixed `thread_id`: call `.start()`, catch the interrupt, print
the payload, then call `.resume()` four times in four separate runs — one per decision
branch — to confirm routing actually works before touching the UI. *Done when:* all four
branches (approve/edit/regenerate/reject) resolve correctly.

**Day 6 — Streamlit + finalize**
Build `app.py` per the wiring above. Write `finalize_node` — save the letter to
`outputs/` and append a row to `data/applications_log.jsonl`. Full browser test: paste a
real posting, walk approve, then a separate run walk edit, then regenerate. *Done when:*
you can go end-to-end in the browser without touching the terminal.

**Day 7 — Real run, polish, deploy**
Run it against 2–3 job postings you're actually planning to apply to. Try swapping
`DRAFTRON_GEN_MODEL` to compare `gpt-4o-mini` vs a stronger model on one of them. Deploy
to Streamlit Community Cloud for the live URL the roadmap calls for. Write `README.md`,
push to GitHub.

---



## 8. Worked example — what you should actually see

Say you paste in a posting like: *"AI Agent Engineer, EdTech company building virtual
lab simulations, remote/Cairo. Requirements: Python, agent frameworks (LangGraph or
similar), RAG, 2+ years experience."* (This is a stand-in shape — use whatever real
posting you're working on.)

**After** `jd_extractor`**:**

```json
{"company_name": "Example EdTech Co", "role_title": "AI Agent Engineer",
 "required_skills": ["Python", "LangGraph", "RAG", "multi-agent systems"],
 "seniority": "mid", "culture_signals": ["remote-friendly", "product-focused"]}
```

**After** `profile_matcher`**:**

```json
{"matched_skills": ["Python", "LangGraph", "RAG", "multi-agent systems"],
 "skill_gaps": [], "relevant_projects": ["LAPIS V2", "DRAFTRON"],
 "strongest_angle": "LAPIS V2 is a direct domain match — a virtual lab with a real three-agent backend"}
```

**After** `self_critique`**:**

```json
{"passes": true, "overstatement_flags": [], "length_flag": false,
 "tone_flag": false, "notes": "No unclaimed tools, three short paragraphs, direct close."}
```

**What you see on the human-review screen:** the draft letter, the critique summary above,
and four buttons — Approve / Edit / Regenerate / Reject. If you hit Edit with feedback like
"mention the RPC protocol work," it goes to `revision`, comes back through `self_critique`,
and you review it again — same thread, same screen.

**On Approve,** `finalize` **writes:**

```
outputs/example_edtech_ai_agent_engineer_2026-07-09.md
```

and appends to `data/applications_log.jsonl`:

```json
{"date": "2026-07-09", "company": "Example EdTech Co", "role": "AI Agent Engineer",
 "decision": "approve", "revision_count": 0, "model_used": "gpt-4o-mini",
 "output_path": "outputs/example_edtech_ai_agent_engineer_2026-07-09.md"}
```

That log file is the thing worth noticing — by the time you're job-hunting at volume, it's
a running record of every company you've applied to, which draft went out, and how many
revisions it took. Useful on its own, and it's exactly the kind of structured history
PATHRA (Week 5) will eventually read from.