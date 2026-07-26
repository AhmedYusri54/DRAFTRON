import json
import re
from datetime import datetime
from pathlib import Path
from graph import PROJECT_ROOT
from graph.state import CoverLetterState
from models.router import DRAFT_MODEL


def _sanitize_filename(text: str) -> str:
    """Convert 'AI Agent Engineer' -> 'ai_agent_engineer'"""
    text = re.sub(r'[^\w\s-]', '', text).strip()
    return text.replace(' ', '_').lower()


def _build_letter(draft: str, candidate_name: str, company_name: str) -> str:
    """
    Wrap the model-generated body paragraphs with a salutation and sign-off.
    Deliberately not draft_generator's job -- draft_generation.md explicitly
    bans a salutation/sign-off from its output, since this is fixed,
    deterministic template formatting, same reasoning as everywhere else this
    week for not delegating mechanical structure to model judgment.
    """
    salutation = f"Dear {company_name} Hiring Team,"
    sign_off = f"Sincerely,\n{candidate_name}"
    return f"{salutation}\n\n{draft}\n\n{sign_off}"


def _unique_output_path(outputs_dir: Path, base_filename: str) -> Path:
    """
    Avoid silently overwriting an existing file. Same company + role + date
    happens more often than it sounds -- rerunning a test, or genuinely
    re-applying to the same posting twice in one day.
    """
    candidate = outputs_dir / base_filename
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    n = 2
    while True:
        candidate = outputs_dir / f"{stem}_v{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def finalize_node(state: CoverLetterState) -> dict:
    company_name = state.get("company_name", "unknown_company")
    role_title = state.get("role_title", "unknown_role")
    candidate_name = state["candidate_profile"]["name"]
    draft = state["draft"]
    revision_count = state.get("revision_count", 0)

    final_letter = _build_letter(draft, candidate_name, company_name)

    # --- Side effect 1: Save the letter to outputs/ ---
    outputs_dir = PROJECT_ROOT / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    company_slug = _sanitize_filename(company_name)
    role_slug = _sanitize_filename(role_title)
    base_filename = f"{company_slug}_{role_slug}_{date_str}.md"

    output_path = _unique_output_path(outputs_dir, base_filename)
    output_path.write_text(final_letter, encoding="utf-8")

    # --- Side effect 2: Append to applications_log.jsonl ---
    log_path = PROJECT_ROOT / "data" / "applications_log.jsonl"
    log_entry = {
        "date": date_str,
        "company": company_name,
        "role": role_title,
        "decision": "approve",
        "revision_count": revision_count,
        "model_used": DRAFT_MODEL,
        "output_path": str(output_path.relative_to(PROJECT_ROOT)),
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"== Saved: {output_path.relative_to(PROJECT_ROOT)} ==")
    print(f"== Logged to: {log_path.relative_to(PROJECT_ROOT)} ==")

    return {"final_letter": final_letter}