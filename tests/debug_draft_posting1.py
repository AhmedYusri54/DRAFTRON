"""
Standalone diagnostic -- draft_generator_node on posting 1 only.
Run from the project root: uv run python tests/debug_draft_posting1.py
"""
from graph import PROJECT_ROOT
from graph.nodes.intake_node import intake_node
from graph.nodes.jd_extractor_node import jd_extractor_node
from graph.nodes.profile_matcher_node import profile_matcher_node
from graph.nodes.strategy_node import strategy_node
from graph.nodes.draft_generator_node import draft_generator_node

posting_path = PROJECT_ROOT / "tests" / "fixtures" / "postings" / "posting_1_clear_split.txt"
posting_text = posting_path.read_text(encoding="utf-8")

state = {"job_posting_raw": posting_text}
state.update(intake_node(state))
state.update(jd_extractor_node(state))
state.update(profile_matcher_node(state))
state.update(strategy_node(state))

print("== state going into draft_generator_node ==")
print("strategy:", state["strategy"])
print()

print("== calling draft_generator_node ==")
result = draft_generator_node(state)

print("== raw return value ==")
print(repr(result))
print()
print("== keys in returned dict ==")
print(list(result.keys()) if isinstance(result, dict) else "NOT A DICT")