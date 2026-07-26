"""
Day 4 test harness -- draft_generator_node and self_critique_node.
Run from the project root: uv run python tests/test_day4.py
"""
from graph import PROJECT_ROOT
from graph.nodes.intake_node import intake_node
from graph.nodes.jd_extractor_node import jd_extractor_node
from graph.nodes.profile_matcher_node import profile_matcher_node
from graph.nodes.strategy_node import strategy_node
from graph.nodes.draft_generator_node import draft_generator_node
from graph.nodes.self_critique_node import self_critique_node

POSTINGS_DIR = PROJECT_ROOT / "tests" / "fixtures" / "postings"

EDUCATION_TERMS = ["university", "gpa", "b.sc", "bachelor", "degree", "college"]
BOILERPLATE_PHRASES = [
    "i am excited to apply",
    "i am writing to express",
    "i believe i would be a great fit",
    "i look forward to hearing from you soon",
]


def run_pipeline(posting_text: str) -> dict:
    state = {"job_posting_raw": posting_text}
    state.update(intake_node(state))
    state.update(jd_extractor_node(state))
    state.update(profile_matcher_node(state))
    state.update(strategy_node(state))
    state.update(draft_generator_node(state))
    state.update(self_critique_node(state))
    return state


def sanity_check(draft: str) -> list[str]:
    """Quick eyeball flags for reading the printed output -- not the same as
    self_critique_node itself, just a second pair of eyes on the raw text."""
    flags = []
    lower = draft.lower()
    word_count = len(draft.split())
    if word_count < 120 or word_count > 400:
        flags.append(f"length off: {word_count} words")
    for term in EDUCATION_TERMS:
        if term in lower:
            flags.append(f"possible education mention: '{term}'")
    for phrase in BOILERPLATE_PHRASES:
        if phrase in lower:
            flags.append(f"boilerplate phrase: '{phrase}'")
    return flags


def test_full_pipeline():
    for posting_file in sorted(POSTINGS_DIR.glob("*.txt")):
        print("=" * 60)
        print(f"=== {posting_file.name} ===")
        print("=" * 60)

        posting_text = posting_file.read_text(encoding="utf-8")
        state = run_pipeline(posting_text)

        strategy = state["strategy"]
        print(f"[strategy] tone={strategy['tone']!r} lead_project={strategy['lead_project']!r}")
        print(f"[strategy] do_not_claim={strategy['do_not_claim']}")
        print()
        print(state["draft"])
        print()

        print("-- self_critique --")
        critique = state["critique"]
        print(f"  passes:              {critique['passes']}")
        print(f"  overstatement_flags: {critique['overstatement_flags']}")
        print(f"  length_flag:         {critique['length_flag']}")
        print(f"  tone_flag:           {critique['tone_flag']}")
        print(f"  notes:               {critique['notes']}")

        flags = sanity_check(state["draft"])
        if flags:
            print("  !! manual sanity flags (cross-check against critique above):")
            for f in flags:
                print(f"     - {f}")
        print()


def test_self_critique_catches_bad_draft():
    """
    Adversarial test: hand-construct a draft that violates do_not_claim
    directly, and confirm self_critique_node actually catches it.
    A critique node that's only ever reviewed clean drafts hasn't been
    tested -- it's only been run.
    """
    print("=" * 60)
    print("=== adversarial test: deliberately bad draft ===")
    print("=" * 60)

    bad_state = {
        "strategy": {
            "tone": "direct",
            "do_not_claim": ["edge deployment", "CrewAI"],
        },
        "draft": (
            "I bring hands-on experience with edge deployment, having shipped "
            "production models to resource-constrained edge hardware. I'm also "
            "excited to apply my CrewAI expertise to multi-agent orchestration "
            "challenges. I am eager to bring these skills to your team and look "
            "forward to hearing from you soon."
        ),
    }

    result = self_critique_node(bad_state)
    critique = result["critique"]

    print(f"  passes:              {critique['passes']}  (expected: False)")
    print(f"  overstatement_flags: {critique['overstatement_flags']}  (expected: contains 'edge deployment' and 'CrewAI')")
    print(f"  notes:               {critique['notes']}")

    if critique["passes"]:
        print("  !! FAILURE: self_critique_node did not catch an obvious violation")
    else:
        print("  OK: correctly flagged as not passing")
    print()


if __name__ == "__main__":
    test_full_pipeline()
    test_self_critique_catches_bad_draft()