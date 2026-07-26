from models.router import get_matching_model
from graph import PROJECT_ROOT
import json
from graph.state import ProfileMatch, CoverLetterState
from langchain_core.messages import SystemMessage, HumanMessage

with open(PROJECT_ROOT / "prompts" / "profile_matching.md", "r", encoding="utf-8") as f:
    PROFILE_MATCHER_PROMPT = f.read()


_model = get_matching_model().with_structured_output(ProfileMatch)


def _drop_invalid_gaps(result: ProfileMatch, posting_skills: list[str]) -> ProfileMatch:
    """
    Deterministic backstop: skill_gaps must only contain entries traceable to
    this posting's own required/nice-to-have skills. Drops anything invented
    that isn't an actual posting skill (e.g. inferring a broader category like
    "deep learning frameworks" around an already-matched skill like "PyTorch").
    """
    posting_lower = [s.lower() for s in posting_skills]

    def _is_valid_gap(entry: str) -> bool:
        entry_l = entry.lower()
        return any(entry_l in p or p in entry_l for p in posting_lower)

    result.skill_gaps = [g for g in result.skill_gaps if _is_valid_gap(g)]
    return result


def _enforce_unverified_skills(result: ProfileMatch, posting_skills: list[str], unverified_skills: list[str]) -> ProfileMatch:
    """
    Deterministic backstop: any posting skill (required or nice-to-have)
    that's also in the candidate's unverified_skills list must end up in
    skill_gaps -- regardless of what the model decided or omitted.
    """
    unverified_lower = {s.lower() for s in unverified_skills}

    matched = [s for s in result.matched_skills if s.lower() not in unverified_lower]
    gaps = set(result.skill_gaps)
    for skill in posting_skills:
        if skill.lower() in unverified_lower:
            gaps.add(skill)

    result.matched_skills = matched
    result.skill_gaps = list(gaps)
    return result

def _collect_exact_evidence_terms(profile: dict) -> set[str]:
    """All skill/tag strings that literally appear somewhere in the
    candidate's projects or skills categories -- lowercased for
    case-insensitive exact matching."""
    terms = set()
    for project in profile.get("projects", []):
        for tag in project.get("tags", []):
            terms.add(tag.lower())
    for category_skills in profile.get("skills", {}).values():
        for skill in category_skills:
            terms.add(skill.lower())
    return terms

def _enforce_exact_matches(result: ProfileMatch, posting_skills: list[str], evidence_terms: set[str]) -> ProfileMatch:
    """
    Deterministic backstop: if a posting skill is an exact (case-insensitive)
    match against something literally present in the candidate's project tags
    or skills list, it must be matched. Exhaustive exact-string matching is a
    known LLM weak spot -- this node has missed the same literal tag match
    multiple times, including at temperature=0.
    """
    matched = set(result.matched_skills)
    gaps = set(result.skill_gaps)

    for skill in posting_skills:
        if skill.lower() in evidence_terms and skill not in matched:
            matched.add(skill)
            gaps.discard(skill)

    result.matched_skills = list(matched)
    result.skill_gaps = list(gaps)
    return result

def profile_matcher_node(state: CoverLetterState) -> dict:
    # 1. Build the JD requirements the model needs to see
    job_requirements = {
        "role_title": state["role_title"],
        "company_name": state["company_name"],
        "required_skills": state["jd_structured"]["required_skills"],
        "nice_to_have_skills": state["jd_structured"]["nice_to_have_skills"],
        "key_responsibilities": state["jd_structured"]["key_responsibilities"],
    }

    # 2. Strip contact info before it goes into the profile
    profile_for_matching = {k: v for k, v in state["candidate_profile"].items() if k != "contact"}

    # 3. Build the system and human messages
    messages = [
        SystemMessage(content=PROFILE_MATCHER_PROMPT),
        HumanMessage(content=(
            f"Job requirements:\n{json.dumps(job_requirements, indent=2)}\n\n"
            f"Candidate profile:\n{json.dumps(profile_for_matching, indent=2)}"
        )),
    ]

    # 4. Run it through the matcher model
    result = _model.invoke(messages)

    posting_skills = job_requirements["required_skills"] + job_requirements["nice_to_have_skills"]

    evidence_terms = _collect_exact_evidence_terms(state["candidate_profile"])
    result = _enforce_exact_matches(result, posting_skills, evidence_terms)

    unverified = state["candidate_profile"]["letter_generation_notes"]["unverified_skills"]
    result = _enforce_unverified_skills(result, posting_skills, unverified)

    result = _drop_invalid_gaps(result, posting_skills)

    return {
        "matched_skills": result.matched_skills,
        "skill_gaps": result.skill_gaps,
        "relevant_projects": result.relevant_projects,
        "strongest_angle": result.strongest_angle,

    }
