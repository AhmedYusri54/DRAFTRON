from models.router import get_generation_model
from graph import PROJECT_ROOT
import json
from graph.nodes._shared import find_project
from graph.state import CoverLetterState
from langchain_core.messages import SystemMessage, HumanMessage

with open(PROJECT_ROOT / "prompts" / "draft_generation.md", "r", encoding="utf-8") as f:
    DRAFT_GENERATION_PROMPT = f.read()


_model = get_generation_model()



def draft_generator_node(state: CoverLetterState) -> dict: 
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

    lead_project = find_project(state["candidate_profile"]["projects"], strategy["lead_project"])

    lead_project_text = json.dumps(lead_project, indent=2) if lead_project else "none — build the case from supporting_points instead"

    candidate_name = state["candidate_profile"]["name"]

    messages = [
    SystemMessage(content=DRAFT_GENERATION_PROMPT),
    HumanMessage(content=(
        f"Candidate name: {candidate_name}\n\n"
        f"Role:\n{json.dumps(role_context, indent=2)}\n\n"
        f"Writing brief:\n{json.dumps(writing_brief, indent=2)}\n\n"
        f"Lead project:\n{lead_project_text}"
    )),
    ]

    result = _model.invoke(messages).content

    return {"draft": result}