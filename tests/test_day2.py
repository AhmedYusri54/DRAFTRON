"""
Day 2 manual test harness for DRAFTRON.
Run from the project root: uv run python tests/test_day2.py
"""
import json

from graph import PROJECT_ROOT
from models.router import (
    get_extraction_model,
    get_matching_model,
    get_generation_model,
    get_critique_model,
)
from graph.nodes.intake_node import intake_node
from graph.nodes.jd_extractor_node import jd_extractor_node

POSTINGS_DIR = PROJECT_ROOT / "tests" / "fixtures" / "postings"


def test_router():
    print("== Router sanity check ==")
    for name, getter in [
        ("extraction (Groq)", get_extraction_model),
        ("matching (Groq)", get_matching_model),
        ("generation (OpenAI)", get_generation_model),
        ("critique (Groq)", get_critique_model),
    ]:
        try:
            client = getter()
            response = client.invoke("Say hello in exactly 3 words.")
            print(f"  OK   {name}: {response.content}")
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    print()


def test_intake():
    print("== intake_node ==")
    posting_text = (POSTINGS_DIR / "posting_1_clear_split.txt").read_text(encoding="utf-8")
    result = intake_node({"job_posting_raw": posting_text})
    profile = result["candidate_profile"]
    print(f"  Loaded profile for: {profile.get('name')}")
    print(f"  Skill categories: {list(profile.get('skills', {}).keys())}")
    print(f"  Projects: {[p['name'] for p in profile.get('projects', [])]}")
    print()


def test_jd_extractor():
    print("== jd_extractor_node ==")
    for posting_file in sorted(POSTINGS_DIR.glob("*.txt")):
        print(f"--- {posting_file.name} ---")
        posting_text = posting_file.read_text(encoding="utf-8")
        result = jd_extractor_node({"job_posting_raw": posting_text})
        print(json.dumps(result["jd_structured"], indent=2))
        print()


if __name__ == "__main__":
    test_router()
    test_intake()
    test_jd_extractor()