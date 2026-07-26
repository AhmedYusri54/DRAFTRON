from langgraph.graph import StateGraph, START, END  # type: ignore
from langgraph.checkpoint.memory import InMemorySaver # type: ignore
from langgraph.types import Command  # type: ignore
from graph.nodes.intake_node import intake_node
from graph.nodes.jd_extractor_node import jd_extractor_node
from graph.nodes.profile_matcher_node import profile_matcher_node
from graph.nodes.strategy_node import strategy_node
from graph.nodes.draft_generator_node import draft_generator_node
from graph.nodes.self_critique_node import self_critique_node
from graph.nodes.human_review_node import human_review_node
from graph.nodes.revision_node import revision_node
from graph.nodes.finalize_node import finalize_node
from graph.edges import route_after_review
from graph.state import CoverLetterState


class DraftronGraph:
       def __init__(self, checkpointer=None):
           self.checkpointer = checkpointer or InMemorySaver()
           self.graph = self._build().compile(checkpointer=self.checkpointer)

       def _build(self) -> StateGraph:
           # Init the graph 
           g = StateGraph(CoverLetterState)

           # Add the nodes 
           g.add_node("intake", intake_node)
           g.add_node("jd_extractor", jd_extractor_node)
           g.add_node("profile_matcher", profile_matcher_node)
           g.add_node("strategy", strategy_node)
           g.add_node("draft_generator", draft_generator_node)
           g.add_node("self_critique", self_critique_node)
           g.add_node("human_review", human_review_node)
           g.add_node("revision", revision_node)
           g.add_node("finalize", finalize_node)

           # Add the edges
           g.add_edge(START, "intake")
           g.add_edge("intake", "jd_extractor")
           g.add_edge("jd_extractor", "profile_matcher")
           g.add_edge("profile_matcher", "strategy")
           g.add_edge("strategy", "draft_generator")
           g.add_edge("draft_generator", "self_critique")
           g.add_edge("self_critique", "human_review")
           g.add_conditional_edges(
            "human_review",
            route_after_review,
            {
                "finalize": "finalize",
                "revision": "revision",
                "draft_generator": "draft_generator",
                "__end__": END,
            }
           )
           g.add_edge("revision", "self_critique")
           g.add_edge("finalize", END)

           return g


       def start(self, job_posting: str, thread_id: str):
           # First invocation — kicks off the pipeline
           config = {"configurable": {"thread_id": thread_id}}
           return self.graph.invoke({"job_posting_raw": job_posting}, config=config)

       def resume(self, resume_value: dict, thread_id: str):
           # Resume after interrupt — picks up where it left off
           config = {"configurable": {"thread_id": thread_id}}
           return self.graph.invoke(Command(resume=resume_value), config=config)
