from models.router import get_extraction_model
from graph import PROJECT_ROOT
from graph.state import JDExtraction, CoverLetterState
from langchain_core.messages import SystemMessage, HumanMessage

with open(PROJECT_ROOT / "prompts" / "jd_extraction.md", "r", encoding="utf-8") as f:
    JD_EXTRACTION_PROMPT = f.read()

_model = get_extraction_model().with_structured_output(JDExtraction)


def jd_extractor_node(state: CoverLetterState) -> dict:
    job_posting = state["job_posting_raw"]

    messages = [
        SystemMessage(content=JD_EXTRACTION_PROMPT),
        HumanMessage(content=job_posting),
    ]

    result = _model.invoke(messages)
    

    return {
        "company_name": result.company_name,
        "role_title": result.role_title,
        "jd_structured": result.model_dump(),
    }
