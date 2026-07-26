from graph.state import CoverLetterState
from typing import Literal


def route_after_review(state: CoverLetterState) -> Literal["finalize", "revision", "draft_generator", "__end__"]:
    decision = state["decision"]

    if decision == "approve":
        return "finalize"
    elif decision == "edit":
        return "revision"
    elif decision == "regenerate":
        return "draft_generator"
    elif decision == "reject":
        return "__end__"
    else:
        raise ValueError(f"Unexpected decision: {decision!r}")
