from models.router import get_generation_model
from graph import PROJECT_ROOT
import json
from graph.nodes._shared import find_project
from graph.state import CoverLetterState
from langchain_core.messages import SystemMessage, HumanMessage

with open(PROJECT_ROOT / "prompts" / "revision.md", "r", encoding="utf-8") as f:
    REVISION_PROMPT = f.read()


_model = get_generation_model()


def revision_node(state: CoverLetterState) -> dict:
    role_context = {
    "company_name": state["company_name"],
    "role_title": state["role_title"],
    }

    strategy = state["strategy"]

    writing_brief = {
        "tone": strategy["tone"],
        "opening_angle": strategy["opening_angle"],
        "supporting_points": strategy["supporting_points"],
        "do_not_claim": strategy["do_not_claim"],
    }

    candidate_name = state["candidate_profile"]["name"]

    draft = state['draft']

    human_feedback = state['human_feedback']

    lead_project = find_project(state["candidate_profile"]["projects"], strategy["lead_project"])

    lead_project_text = json.dumps(lead_project, indent=2) if lead_project else "none — build the case from supporting_points instead"

    # Extract critique flags if available
    critique = state.get("critique", {})
    critique_flags = {
        "overstatement_flags": critique.get("overstatement_flags", []),
        "notes": critique.get("notes", ""),
    }

    messages = [
    SystemMessage(content=REVISION_PROMPT),
    HumanMessage(content=(
        f"Candidate name: {candidate_name}\n\n"
        f"Role:\n{json.dumps(role_context, indent=2)}\n\n"
        f"Writing brief:\n{json.dumps(writing_brief, indent=2)}\n\n"
        f"Current draft:\n{draft}\n\n"
        f"Lead project:\n{lead_project_text}\n\n"
        f"Latest feedback to address:\n{human_feedback}\n\n"
        f"Full feedback history so far (context only — don't undo earlier "
        f"requests while addressing the latest one):\n"
        f"{json.dumps(state.get('human_feedback_history', []), indent=2)}\n\n"
        f"Critique flags to fix (these are additional constraints):\n"
        f"{json.dumps(critique_flags, indent=2)}"
    )),
    ]

    result = _model.invoke(messages)

    return {
        "draft": result.content,
        "revision_count": state.get("revision_count", 0) + 1
    }

