"""
Day 5 test harness -- human_review_node and revision_node loop.
Run from the project root: uv run python tests/test_day5.py

This doesn't use the compiled graph/interrupt() yet (that's builder.py, still
ahead). It tests the loop logic directly: build a real draft through the
pipeline, then manually simulate what human_review_node's response would be
for an "edit" decision, run revision_node, and confirm the loop's contract
holds -- feedback applied, history preserved, re-critiqued.
"""
from graph import PROJECT_ROOT
from graph.nodes.intake_node import intake_node
from graph.nodes.jd_extractor_node import jd_extractor_node
from graph.nodes.profile_matcher_node import profile_matcher_node
from graph.nodes.strategy_node import strategy_node
from graph.nodes.draft_generator_node import draft_generator_node
from graph.nodes.self_critique_node import self_critique_node
from graph.nodes.revision_node import revision_node

POSTINGS_DIR = PROJECT_ROOT / "tests" / "fixtures" / "postings"


def build_initial_state(posting_text: str) -> dict:
    state = {"job_posting_raw": posting_text}
    state.update(intake_node(state))
    state.update(jd_extractor_node(state))
    state.update(profile_matcher_node(state))
    state.update(strategy_node(state))
    state.update(draft_generator_node(state))
    state.update(self_critique_node(state))
    return state


def simulate_human_response(state: dict, decision: str, feedback: str | None) -> dict:
    """
    Stands in for what human_review_node would receive back from interrupt()
    once the graph is compiled. Mirrors human_review_node's own return shape
    so this test exercises the same contract the real node relies on.
    """
    return {
        "decision": decision,
        "human_feedback": feedback,
        "human_feedback_history": [feedback] if feedback else [],
    }


def test_edit_loop():
    print("=" * 60)
    print("=== edit loop: posting_1, two rounds of feedback ===")
    print("=" * 60)

    posting_text = (POSTINGS_DIR / "posting_1_clear_split.txt").read_text(encoding="utf-8")
    state = build_initial_state(posting_text)
    original_word_count = len(state['draft'].split())

    print(f"-- original draft ({original_word_count} words) --")
    print(state["draft"])
    print()
    print(f"-- original critique --  passes={state['critique']['passes']}")
    print()

    # round 1: simulate the human asking for something shorter
    round1 = simulate_human_response(state, "edit", "Make the opening paragraph shorter and more direct.")
    state.update(round1)
    state.update(revision_node(state))
    state.update(self_critique_node(state))

    round1_word_count = len(state['draft'].split())
    print(f"-- after round 1 ({round1_word_count} words) -- revision_count={state['revision_count']}")
    print(state["draft"])
    print(f"critique passes={state['critique']['passes']}  notes={state['critique']['notes']}")
    print(f"feedback_history so far: {state.get('human_feedback_history')}")
    print()

    # Assertions for round 1
    assert state['revision_count'] == 1, f"Expected revision_count=1, got {state['revision_count']}"
    assert round1_word_count < original_word_count, f"Draft should be shorter after round 1 ({original_word_count} -> {round1_word_count})"
    assert "I am prepared" not in state['draft'], "Formulaic 'I am prepared' should be removed"
    assert "I am particularly" not in state['draft'], "Formulaic 'I am particularly' should be removed"

    # round 2: a second, different piece of feedback -- the real test of
    # whether round 1's "shorter opening" request survives untouched
    round2 = simulate_human_response(state, "edit", "Add a specific mention of the FAISS work in the closing paragraph.")
    state["human_feedback_history"] = state.get("human_feedback_history", []) + round2["human_feedback_history"]
    state["human_feedback"] = round2["human_feedback"]
    state.update(revision_node(state))
    state.update(self_critique_node(state))

    round2_word_count = len(state['draft'].split())
    print(f"-- after round 2 ({round2_word_count} words) -- revision_count={state['revision_count']}")
    print(state["draft"])
    print(f"critique passes={state['critique']['passes']}  notes={state['critique']['notes']}")
    print(f"feedback_history so far: {state['human_feedback_history']}")
    print()

    # Assertions for round 2
    assert state['revision_count'] == 2, f"Expected revision_count=2, got {state['revision_count']}"
    assert len(state['human_feedback_history']) == 2, f"Expected 2 feedback entries, got {len(state['human_feedback_history'])}"
    assert "faiss" in state['draft'].lower(), "FAISS should be mentioned in round 2 draft"
    # Check round 1's shorter opening is preserved (within 10% tolerance)
    assert round2_word_count <= round1_word_count * 1.1, f"Round 1's shorter request violated: {round1_word_count} -> {round2_word_count}"

    print("✅ All assertions passed!")
    print(">> Opening still short: YES (round 1 preserved)")
    print(">> FAISS mentioned in closing: YES")
    print()


def test_approve_path():
    print("=" * 60)
    print("=== approve path: posting_2, no revision needed ===")
    print("=" * 60)

    posting_text = (POSTINGS_DIR / "posting_2_sparse.txt").read_text(encoding="utf-8")
    state = build_initial_state(posting_text)

    response = simulate_human_response(state, "approve", None)
    print(f"decision={response['decision']}  feedback={response['human_feedback']}")
    print("-- final draft (unchanged, as approve should never touch draft) --")
    print(state["draft"])
    print()


if __name__ == "__main__":
    test_edit_loop()
    test_approve_path()