from models.router import get_matching_model
from graph import PROJECT_ROOT
import json
from graph.state import Strategy, CoverLetterState
from langchain_core.messages import SystemMessage, HumanMessage

with open(PROJECT_ROOT / "prompts" / "strategy.md", "r", encoding="utf-8") as f:
    STRATEGY_PROMPT = f.read()

_model = get_matching_model().with_structured_output(Strategy)


def strategy_node(state: CoverLetterState) -> dict:
    posting_context = {
    "culture_signals": state["jd_structured"]["culture_signals"],
    "key_responsibilities": state["jd_structured"]["key_responsibilities"],
    }

    match_summary = {
        "matched_skills": state["matched_skills"],
        "relevant_projects": state["relevant_projects"],
        "strongest_angle": state["strongest_angle"],
    }

    messages = [
    SystemMessage(content=STRATEGY_PROMPT),
    HumanMessage(content=(
        f"Job posting context:\n{json.dumps(posting_context, indent=2)}\n\n"
        f"Match summary:\n{json.dumps(match_summary, indent=2)}"
    )),
    ]

    result = _model.invoke(messages)

    return {
    "strategy": {
        "tone": result.tone,
        "lead_project": result.lead_project,
        "opening_angle": result.opening_angle,
        "do_not_claim": state["skill_gaps"],   
        "supporting_points": result.supporting_points,
    }
    }
