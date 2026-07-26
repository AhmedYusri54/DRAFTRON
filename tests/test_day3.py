"""
Day 3 manual test harness for DRAFTRON.
Run from the project root: uv run python tests/test_day3.py
"""
from graph import PROJECT_ROOT
from graph.nodes.intake_node import intake_node
from graph.nodes.jd_extractor_node import jd_extractor_node
from graph.nodes.profile_matcher_node import profile_matcher_node
from graph.nodes.strategy_node import strategy_node

POSTINGS_DIR = PROJECT_ROOT / "tests" / "fixtures" / "postings"

# what to actually check per posting, not just "did it run"
WATCH_FOR = {
    "posting_1_clear_split.txt": (
        "Matching: Chemistry Voice Tutor should appear in relevant_projects. "
        "CrewAI should land in skill_gaps, not matched_skills. "
        "Strategy: tone should read direct/energetic given the culture signals; "
        "lead_project should be Chemistry Voice Tutor."
    ),
    "posting_2_sparse.txt": (
        "Matching: honesty check — thin matched_skills, empty gaps/projects is fine. "
        "Strategy: with relevant_projects empty, lead_project should be None/empty "
        "and opening_angle should stay skills-forward, NOT a confident 'strong fit' "
        "framing. This is the real test — strategy shouldn't oversell what matching "
        "was honest about."
    ),
    "posting_3_mixed.txt": (
        "Matching: Predictive Attrition Modeling Pipeline should surface. "
        "Strategy: lead_project should be Predictive Attrition Modeling Pipeline; "
        "tone likely more plain/technical since this posting's culture_signals are sparse."
    ),
}


def run_pipeline(posting_text: str) -> dict:
    """Chains the nodes the way LangGraph will once builder.py exists."""
    state = {"job_posting_raw": posting_text}
    state.update(intake_node(state))
    state.update(jd_extractor_node(state))
    state.update(profile_matcher_node(state))
    state.update(strategy_node(state))
    return state


def test_pipeline():
    for posting_file in sorted(POSTINGS_DIR.glob("*.txt")):
        print(f"=== {posting_file.name} ===")
        print(f"Watch for: {WATCH_FOR.get(posting_file.name, '(no specific check)')}\n")

        posting_text = posting_file.read_text(encoding="utf-8")
        state = run_pipeline(posting_text)

        print("-- profile_matcher --")
        print(f"  matched_skills:     {state['matched_skills']}")
        print(f"  skill_gaps:         {state['skill_gaps']}")
        print(f"  relevant_projects:  {state['relevant_projects']}")
        print(f"  strongest_angle:    {state['strongest_angle']}")

        print("-- strategy --")
        strategy = state["strategy"]
        print(f"  tone:               {strategy['tone']}")
        print(f"  lead_project:       {strategy['lead_project']}")
        print(f"  opening_angle:      {strategy['opening_angle']}")
        print(f"  do_not_claim:       {strategy['do_not_claim']}")
        print(f"  supporting_points:  {strategy['supporting_points']}")
        print()


if __name__ == "__main__":
    test_pipeline()