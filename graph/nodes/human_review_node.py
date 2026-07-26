from langgraph.types import interrupt
from graph.state import  CoverLetterState


def human_review_node(state: CoverLetterState) -> dict: 
    response = interrupt({
          "draft": state["draft"],
          "critique": state["critique"],
          "revision_count": state.get("revision_count", 0),
      })

    feedback = response.get("feedback")

    return {
          "decision": response["decision"],
          "human_feedback": feedback,
          "human_feedback_history": [feedback] if feedback else [],
      }


