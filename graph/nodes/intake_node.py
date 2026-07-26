import json
from graph import PROJECT_ROOT
from graph.state import CoverLetterState


def intake_node(state: CoverLetterState) -> dict:
    job_posting = state["job_posting_raw"].strip()
    if not job_posting:
        raise ValueError("job_posting_raw is empty — nothing to extract from.")

    profile_path = PROJECT_ROOT / "data" / "profile.json"
    try:
        with open(profile_path, "r") as f:
            profile = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"{profile_path} not found — add your profile.json to the data folder."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"{profile_path} is not valid JSON: {e}")

    required_keys = {"name", "skills", "projects"}
    missing = required_keys - profile.keys()
    if missing:
        raise ValueError(f"profile.json is missing required keys: {missing}")

    print("== Profile loaded successfully ==")
    return {
        "job_posting_raw": job_posting,
        "candidate_profile": profile,
    }