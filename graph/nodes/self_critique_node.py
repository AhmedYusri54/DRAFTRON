from models.router import get_critique_model
from graph import PROJECT_ROOT
import json
import re
from graph.state import CritiqueJudgment, CoverLetterState, CritiqueResult
from langchain_core.messages import SystemMessage, HumanMessage

with open(PROJECT_ROOT / "prompts" / "self_critique.md", "r", encoding="utf-8") as f:
    SELF_CRITIQUE_PROMPT = f.read()

_model = get_critique_model().with_structured_output(CritiqueJudgment)

EDUCATION_TERMS = ["university", "gpa", "b.sc", "bachelor", "degree", "college"]

# Exposed as named constants so app.py's suggested-feedback builder can say
# "shorten to under 400 words" without duplicating these numbers separately.
MIN_WORDS = 120
MAX_WORDS = 400

FORMULAIC_OPENER_PATTERN = re.compile(
    r"\bi(?:'m| am) (?:particularly |genuinely |truly )?"
    r"(?:excited|eager|keen|drawn|ready|prepared|thrilled|delighted|honored)\b",
    re.IGNORECASE,
)

def _normalize_quotes(text: str) -> str:
    """
    Normalize typographic quotes to straight ASCII ones before any
    deterministic check runs. Generation isn't consistent about which style
    it uses draft to draft, and a regex anchored on a straight apostrophe
    silently fails to match the same contraction written with a curly one.
    Normalize once, here, rather than fixing every check's pattern separately.
    """
    return (
        text.replace("\u2019", "'").replace("\u2018", "'")
            .replace("\u201c", '"').replace("\u201d", '"')
    )

def _term_variants(term: str) -> set[str]:
    """A compound restricted term like 'model deployment (Docker, FastAPI)'
    should also flag on its base phrase alone."""
    base = re.sub(r"\s*\([^)]*\)", "", term).strip()
    return {v.lower() for v in {term, base} if v}


def _find_literal_leaks(draft: str, do_not_claim: list[str]) -> list[str]:
    """Deterministic, exact/near-exact check: which do_not_claim terms are
    literally present in the draft, including their base phrase. A lookup,
    not a judgment call -- kept in Python rather than asked of the LLM."""
    lower = draft.lower()
    return [term for term in do_not_claim if any(v in lower for v in _term_variants(term))]


def _find_education_mentions(draft: str) -> list[str]:
    """Deterministic check: any known education term appearing in the draft,
    regardless of context. Standing rule -- education never appears in
    generated letters, so presence alone is enough to flag."""
    lower = draft.lower()
    return [term for term in EDUCATION_TERMS if term in lower]


def _find_formulaic_phrases(draft: str) -> list[str]:
    """Deterministic check for the 'I am [feeling adjective] to...' pattern --
    recurred under a new synonym every round despite explicit prompt bans, and
    the LLM's own filler_flags catch it inconsistently even at temperature=0.
    Catch the grammatical shape, not a word list."""
    return [m.group(0) for m in FORMULAIC_OPENER_PATTERN.finditer(draft)]


def _check_length(draft: str) -> bool:
    """Mechanical word count against the target range -- never ask an LLM to
    count words, same reasoning as every exact-match check this week."""
    word_count = len(draft.split())
    return word_count < MIN_WORDS or word_count > MAX_WORDS


def self_critique_node(state: CoverLetterState) -> dict:
    draft = _normalize_quotes(state["draft"])
    do_not_claim = state["strategy"]["do_not_claim"]
    tone = state["strategy"]["tone"]

    # deterministic pass first -- certain, no model involved
    literal_leaks = _find_literal_leaks(draft, do_not_claim)
    education_mentions = _find_education_mentions(draft)
    formulaic_phrases = _find_formulaic_phrases(draft)
    length_flag = _check_length(draft)

    review_context = {
        "target_tone": tone,
        "do_not_claim_full_list": do_not_claim,
        "already_flagged_literal_mentions": literal_leaks,
    }

    messages = [
        SystemMessage(content=SELF_CRITIQUE_PROMPT),
        HumanMessage(content=(
            f"Draft:\n{draft}\n\n"
            f"Review context:\n{json.dumps(review_context, indent=2)}"
        )),
    ]

    # LLM pass second -- only for what actually needs judgment
    judgment = _model.invoke(messages)

    overstatement_flags = literal_leaks + judgment.paraphrased_overstatement_flags

    notes_parts = [judgment.tone_notes]
    if education_mentions:
        notes_parts.append(f"Education mentions found: {', '.join(education_mentions)}")
    if judgment.filler_flags:
        notes_parts.append(f"Filler/cliche flags: {', '.join(judgment.filler_flags)}")
    if formulaic_phrases:
        notes_parts.append(f"Formulaic phrasing found: {', '.join(formulaic_phrases)}")
    notes = " | ".join(notes_parts)

    passes = not (
        overstatement_flags
        or length_flag
        or judgment.tone_flag
        or education_mentions
        or judgment.filler_flags
        or formulaic_phrases
    )

    critique = CritiqueResult(
        passes=passes,
        overstatement_flags=overstatement_flags,
        length_flag=length_flag,
        tone_flag=judgment.tone_flag,
        education_mentions=education_mentions,
        formulaic_phrases=formulaic_phrases,
        filler_flags=judgment.filler_flags,
        notes=notes,
    )

    return {"critique": critique.model_dump()}