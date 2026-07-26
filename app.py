"""
DRAFTRON — AI Cover Letter Agent
Streamlit UI with human-in-the-loop review via LangGraph interrupt().
Dynamic Pipeline Graph & Live Execution Trace.
"""

import uuid
import json
import streamlit as st
from pathlib import Path
from datetime import datetime
from graph.builder import DraftronGraph
from graph import PROJECT_ROOT
from graph.nodes.self_critique_node import MIN_WORDS, MAX_WORDS
from models.router import DRAFT_MODEL

missing = [k for k in ("GROQ_API_KEY",) if not os.getenv(k)]
if missing:
    st.error(f"Missing required secret(s): {', '.join(missing)}. Set them in App settings → Secrets.")
    st.stop()
# ═══════════════════════════════════════════
# Page Config
# ═══════════════════════════════════════════

st.set_page_config(
    page_title="DRAFTRON — AI Cover Letter Agent",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════
# Load & Inject Custom CSS Design System
# ═══════════════════════════════════════════

_css_path = Path(__file__).parent / "styles" / "main.css"
if _css_path.exists():
    st.markdown(f"<style>{_css_path.read_text()}</style>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# Graph — cached so InMemorySaver survives reruns
# ═══════════════════════════════════════════

@st.cache_resource
def get_app():
    return DraftronGraph()

app = get_app()

# ═══════════════════════════════════════════
# Session State Defaults
# ═══════════════════════════════════════════

_DEFAULTS = {
    "thread_id": str(uuid.uuid4()),
    "result": None,
    "current_step": "input",         # input | review | finalized | rejected | history_detail
    "active_step_before_history": "input",
    "selected_history_item": None,
    "active_node": "input",
    "node_execution_trace": [],
    "draft": "",
    "critique": {},
    "revision_count": 0,
    "company_name": "",
    "role_title": "",
    "final_letter": "",
    "feedback_history": [],
    "error_message": "",
    "approve_override_ack": False,
    "feedback_input": "",
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ═══════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════

def _load_history() -> list[dict]:
    """Read the append-only applications log."""
    path = PROJECT_ROOT / "data" / "applications_log.jsonl"
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _reset_session():
    """Clear all state for a fresh generation."""
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.result = None
    st.session_state.current_step = "input"
    st.session_state.active_step_before_history = "input"
    st.session_state.selected_history_item = None
    st.session_state.active_node = "input"
    st.session_state.node_execution_trace = []
    st.session_state.draft = ""
    st.session_state.critique = {}
    st.session_state.revision_count = 0
    st.session_state.company_name = ""
    st.session_state.role_title = ""
    st.session_state.final_letter = ""
    st.session_state.feedback_history = []
    st.session_state.error_message = ""
    st.session_state.approve_override_ack = False
    st.session_state.feedback_input = ""


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _build_suggested_feedback(critique: dict, draft: str) -> str:
    """
    Translate self_critique's flags into a plain-language edit instruction,
    pre-filled into the feedback box. This is a starting point, not a
    replacement for the human's judgment -- they can accept it as-is, edit
    it, or clear it and write their own. Deliberately plain string assembly,
    not another LLM call: turning three known lists into a sentence doesn't
    need judgment, same reasoning behind every deterministic check this
    project already uses (word counts, literal-leak matching, etc).
    """
    if critique.get("passes", True):
        return ""

    lines = []

    overstatement = critique.get("overstatement_flags", [])
    if overstatement:
        items = "; ".join(overstatement)
        lines.append(
            f"Remove or rephrase these overstated claims, which aren't fully "
            f"supported: {items}."
        )

    if critique.get("length_flag"):
        wc = _word_count(draft)
        if wc > MAX_WORDS:
            lines.append(f"Shorten the letter — it's currently {wc} words, target is under {MAX_WORDS}.")
        elif wc < MIN_WORDS:
            lines.append(f"Expand the letter — it's currently {wc} words, target is at least {MIN_WORDS}.")

    if critique.get("tone_flag"):
        lines.append("Adjust the tone so it better matches the letter's intended tone.")

    generic_phrases = critique.get("formulaic_phrases", []) + critique.get("filler_flags", [])
    if generic_phrases:
        items = "; ".join(generic_phrases)
        lines.append(f"Rewrite these generic or formulaic phrases in more specific language: {items}.")

    if critique.get("education_mentions"):
        lines.append("Remove the mention of education or university details — these should never appear in the letter.")

    return " ".join(lines)


def _is_rate_limit_error(e: Exception) -> bool:
    """
    Duck-typed check rather than importing OpenAI/Groq's specific exception
    classes -- both providers use HTTP 429 for rate limits, and checking for
    that status code (with a string fallback) works regardless of which SDK
    raised it or how its exception hierarchy is versioned.
    """
    status_code = getattr(e, "status_code", None)
    if status_code == 429:
        return True
    message = str(e).lower()
    return "rate limit" in message or "429" in message


def _handle_pipeline_error(e: Exception) -> str:
    """
    Turn any exception raised inside the graph into a message safe to show a
    stranger. Rate limits get an honest "try later" message -- that's the
    only case where it's actually true. Everything else (our own deliberate
    raises like a bad profile.json or a bad lead_project id, or a genuine
    bug) gets logged in full server-side and a generic message shown --
    never a false "you hit a limit" claim, and never a raw exception string
    that could leak internals without actually helping the user.
    """
    if _is_rate_limit_error(e):
        return "We've hit today's usage limit with the model provider. Please try again later."

    print(f"[DRAFTRON ERROR] {type(e).__name__}: {e}")

    return (
        "Something went wrong while processing your request. This has been "
        "logged and is on us, not something you did — please try again in a "
        "moment."
    )



    """Pull draft/critique/revision_count from interrupt payload & fetch metadata."""
    payload = result["__interrupt__"][0].value
    st.session_state.draft = payload["draft"]
    st.session_state.critique = payload["critique"]
    st.session_state.revision_count = payload.get("revision_count", 0)
    # Every new draft needs its own acknowledgment -- don't let checking this
    # for one flagged draft silently carry over to a later, different one.
    st.session_state.approve_override_ack = False
    # Same reasoning for the suggested feedback: always regenerated fresh for
    # THIS draft's actual flags, never left over from a previous round.
    st.session_state.feedback_input = _build_suggested_feedback(
        payload["critique"], payload["draft"]
    )

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    try:
        state = app.graph.get_state(config)
        st.session_state.company_name = state.values.get("company_name", "")
        st.session_state.role_title = state.values.get("role_title", "")
    except Exception:
        pass

    st.session_state.current_step = "review"


# ═══════════════════════════════════════════
# Pipeline Step Config & Dynamic Logic
# ═══════════════════════════════════════════

PIPELINE_STEPS = [
    ("1", "Job Posting Input"),
    ("2", "Profile Matching"),
    ("3", "Draft Generation"),
    ("4", "Self-Critique"),
    ("5", "Human Review"),
    ("6", "Finalization"),
]

NODE_TO_STEP = {
    "input": 0,
    "intake": 0,
    "jd_extractor": 0,
    "profile_matcher": 1,
    "strategy": 1,
    "draft_generator": 2,
    "self_critique": 3,
    "human_review": 4,
    "revision": 3,
    "finalize": 5,
}


def _step_status(idx: int) -> str:
    """Return 'completed', 'active', or 'pending' for a pipeline step."""
    step = st.session_state.current_step
    if step == "history_detail":
        step = st.session_state.get("active_step_before_history", "input")

    if step == "input":
        return "active" if idx == 0 else "pending"

    if step == "finalized":
        return "completed"

    if step == "rejected":
        if idx < 4:
            return "completed"
        elif idx == 4:
            return "rejected"
        return "pending"

    if step == "review":
        active_node = st.session_state.get("active_node", "human_review")
        active_step_idx = NODE_TO_STEP.get(active_node, 4)

        if idx < active_step_idx:
            return "completed"
        elif idx == active_step_idx:
            return "active"
        else:
            return "pending"

    return "pending"


def _step_icon(status: str) -> str:
    if status == "completed":
        return "✅"
    if status == "active":
        return "🔵"
    if status == "rejected":
        return "❌"
    return "⚪"


# ═══════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════

def render_header():
    st.markdown(
        """
        <div class="header-banner">
            <div class="header-left">
                <div class="header-logo-icon">📝</div>
                <div class="header-title-group">
                    <span class="header-logo">DRAFTRON</span>
                    <span class="header-tagline">Autonomous AI Cover Letter Agent</span>
                </div>
            </div>
            <div class="status-badge">
                <span class="status-dot"></span> System Connected
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════

def render_sidebar():
    with st.sidebar:
        st.markdown("#### Created by [Ahmed Yusri](https://www.linkedin.com/in/ahmed-yusri)")
        st.markdown("#### ⚡ Pipeline Progress")
        for idx, (num, label) in enumerate(PIPELINE_STEPS):
            status = _step_status(idx)
            icon = _step_icon(status)
            st.markdown(
                f'<div class="pipeline-step {status}">'
                f'<span class="step-icon">{icon}</span> {num}. {label}</div>',
                unsafe_allow_html=True,
            )

        # ── Agent Execution Path Trace ──
        render_execution_trace()

        st.markdown("---")

        # ── Approved Applications History Only ──
        st.markdown("#### 🏆 Approved Applications")
        history = [e for e in _load_history() if e.get("decision") == "approve"]
        if not history:
            st.markdown(
                '<div class="empty-state">'
                '<div class="empty-icon">📄</div>'
                "No approved letters yet</div>",
                unsafe_allow_html=True,
            )
        else:
            for idx, entry in enumerate(reversed(history[-15:])):
                comp = entry.get("company", "—")
                role = entry.get("role", "—")
                dt = entry.get("date", "")

                label = f"✨ {comp}\n{role} • {dt}"
                btn_key = f"hist_item_btn_{idx}_{abs(hash(comp + role + dt))}"

                if st.button(label, key=btn_key, use_container_width=True):
                    if st.session_state.current_step != "history_detail":
                        st.session_state.active_step_before_history = st.session_state.current_step
                    st.session_state.selected_history_item = entry
                    st.session_state.current_step = "history_detail"
                    st.rerun()

        st.markdown("---")
        st.caption(f"🤖 LLM Engine: `{DRAFT_MODEL}`")


def render_execution_trace():
    trace = st.session_state.get("node_execution_trace", [])
    if not trace:
        return

    st.markdown("---")
    st.markdown("#### 📍 Agent Execution Path")

    html = ['<div class="agent-trace-card">']
    for item in trace:
        status = item.get("status", "")
        label = item.get("label", item.get("node", ""))

        if status == "loop":
            html.append(f'<div class="trace-loop-divider">{label}</div>')
        elif status == "active":
            html.append(
                f'<div class="agent-trace-item active">'
                f'<span>{label}</span>'
                f'<span class="trace-badge active">Active 🔵</span></div>'
            )
        else:
            html.append(
                f'<div class="agent-trace-item">'
                f'<span>{label}</span>'
                f'<span class="trace-badge completed">Done ✅</span></div>'
            )
    html.append("</div>")

    st.markdown("".join(html), unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  INPUT SECTION
# ═══════════════════════════════════════════

def render_input():
    st.markdown(
        '<div class="card">'
        '<div class="card-header">📄 Paste Job Posting</div>'
        '<div class="card-subtitle">Provide target job description to initialize AI extraction & profile alignment</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    job_posting = st.text_area(
        "Job Posting",
        placeholder="Paste full job description, role requirements, qualifications, and company information here…",
        height=230,
        label_visibility="collapsed",
        key="job_input",
    )

    char_count = len(job_posting) if job_posting else 0
    st.markdown(
        f'<div class="word-count-pill">📊 {char_count:,} characters input</div>',
        unsafe_allow_html=True,
    )

    with st.expander("💡 Pro Tips for Best Cover Letter Results"):
        st.markdown(
            '<div class="tips-box">'
            "<strong>For optimal AI tailoring:</strong>"
            "<ul>"
            "<li>Include the <strong>complete</strong> job posting details</li>"
            "<li>Ensure company name & exact role title are included</li>"
            "<li>Include specific tech stack requirements or qualifications</li>"
            "</ul></div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    generate_disabled = not job_posting or not job_posting.strip()
    if st.button(
        "✨ Generate Cover Letter",
        type="primary",
        disabled=generate_disabled,
        use_container_width=True,
        key="generate_btn",
    ):
        st.session_state.error_message = ""
        
        # Initialize Execution Path Trace
        st.session_state.node_execution_trace = [
            {"node": "intake", "label": "1. Job Intake", "status": "completed"},
            {"node": "jd_extractor", "label": "2. JD Extraction", "status": "completed"},
            {"node": "profile_matcher", "label": "3. Profile Matcher", "status": "completed"},
            {"node": "strategy", "label": "4. Strategy Planner", "status": "completed"},
            {"node": "draft_generator", "label": "5. Draft Generator (#0)", "status": "completed"},
            {"node": "self_critique", "label": "6. Self-Critique", "status": "completed"},
            {"node": "human_review", "label": "7. Human Review", "status": "active"},
        ]
        st.session_state.active_node = "human_review"

        with st.spinner("🚀 Extracting JD requirements & drafting tailored letter…"):
            try:
                result = app.start(job_posting.strip(), st.session_state.thread_id)
                st.session_state.result = result
                if "__interrupt__" in result:
                    _extract_interrupt(result)
                else:
                    st.session_state.final_letter = result.get("final_letter", "")
                    st.session_state.current_step = "finalized"
                st.rerun()
            except Exception as e:
                st.session_state.error_message = _handle_pipeline_error(e)

    if st.session_state.error_message:
        st.error(f"❌ {st.session_state.error_message}")


# ═══════════════════════════════════════════
#  REVIEW SECTION
# ═══════════════════════════════════════════

def render_review():
    draft = st.session_state.draft
    critique = st.session_state.critique
    revision_count = st.session_state.revision_count
    company = st.session_state.company_name
    role = st.session_state.role_title

    if company or role:
        st.info(f"🎯 **Target Application:** {company} — *{role}*")

    st.markdown(
        '<div class="card">'
        '<div class="card-header">✍️ Draft Cover Letter</div>'
        f'<div class="card-subtitle">Revision #{revision_count} • Human-in-the-Loop Verification</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="draft-text">{draft}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="word-count-pill">📏 {_word_count(draft)} words</div>',
        unsafe_allow_html=True,
    )

    with st.expander("📋 Copy Raw Draft Text"):
        st.code(draft, language=None)

    # ── Critique Section ──
    passes = critique.get("passes", True)
    badge_cls = "pass" if passes else "fail"
    badge_txt = "✅ All quality checks passed" if passes else "⚠️ Potential issues flagged"

    with st.expander(f"🔍 Automated Self-Critique Report — {'Pass' if passes else 'Flags Detected'}", expanded=not passes):
        st.markdown(
            f'<div class="critique-badge {badge_cls}">{badge_txt}</div>',
            unsafe_allow_html=True,
        )

        flags = critique.get("overstatement_flags", [])
        if flags:
            st.markdown("**Overstatement flags:**")
            for f in flags:
                st.markdown(f'<div class="flag-item">⚠️ {f}</div>', unsafe_allow_html=True)

        if critique.get("length_flag"):
            st.markdown(f'<div class="flag-item">📏 Length outside target word range</div>', unsafe_allow_html=True)

        if critique.get("tone_flag"):
            st.markdown(f'<div class="flag-item">🎭 Tone mismatch detected</div>', unsafe_allow_html=True)

        notes = critique.get("notes", "")
        if notes:
            st.info(f"📝 {notes}")

    st.markdown("---")

    # ── Action Buttons ──
    st.markdown("#### 🎯 Human Review Decision")

    # When the automated critique flagged something, don't silently let
    # Approve carry the same visual weight as a clean draft. The human still
    # makes the final call -- interrupt() still fires every time, nothing is
    # auto-routed -- but approving a flagged draft should take a deliberate
    # extra step, not a habitual click on the button that's always primary.
    approval_blocked = False
    if not passes:
        st.warning(
            "⚠️ This draft has flagged issues — see the Self-Critique report "
            "above. Edit or Regenerate is recommended. You can still approve "
            "it as-is, but you'll need to confirm you've seen the flags first."
        )
        acknowledge = st.checkbox(
            "I've read the flagged issues above and want to approve this draft anyway.",
            key="approve_override_ack",
        )
        approval_blocked = not acknowledge

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        approve_clicked = st.button(
            "✅ Approve & Finalize",
            use_container_width=True,
            key="approve_btn",
            type="primary" if passes else "secondary",
            disabled=approval_blocked,
        )

    with col2:
        edit_clicked = st.button(
            "✏️ Request Edit",
            use_container_width=True,
            key="edit_btn",
            type="secondary" if passes else "primary",
        )

    with col3:
        regen_clicked = st.button(
            "🔄 Regenerate Draft",
            use_container_width=True,
            key="regen_btn",
        )

    with col4:
        reject_clicked = st.button(
            "❌ Reject Application",
            use_container_width=True,
            key="reject_btn",
        )

    # ── Feedback Area ──
    st.markdown("---")

    if not passes and st.session_state.feedback_input:
        st.caption(
            "💡 The box below is pre-filled from the flags above, as a starting "
            "point — not something you have to use as-is. Edit it, add your own "
            "notes, or clear it and write your own instructions instead."
        )
        if st.button("🧹 Clear suggestion, write my own", key="clear_suggestion_btn"):
            st.session_state.feedback_input = ""
            st.rerun()

    feedback = st.text_area(
        "Feedback (Required for Requesting Edit)",
        placeholder="Specify desired adjustments, e.g., 'Emphasize cloud architecture experience and add a stronger closing line.'",
        height=100,
        key="feedback_input",
    )

    if st.session_state.feedback_history:
        with st.expander("📜 Feedback Revision Log"):
            for i, fb in enumerate(st.session_state.feedback_history, 1):
                st.markdown(
                    f'<div class="fb-history-item">'
                    f'<div class="fb-round">Revision Round {i}</div>'
                    f'<div class="fb-text">{fb}</div></div>',
                    unsafe_allow_html=True,
                )

    if approve_clicked:
        _handle_resume({"decision": "approve"})

    if edit_clicked:
        if not feedback or not feedback.strip():
            st.warning("⚠️ Please provide feedback instructions before requesting an edit.")
        else:
            st.session_state.feedback_history.append(feedback.strip())
            _handle_resume({"decision": "edit", "feedback": feedback.strip()})

    if regen_clicked:
        _handle_resume({"decision": "regenerate"})

    if reject_clicked:
        _handle_resume({"decision": "reject"})


def _handle_resume(resume_value: dict):
    """Resume the graph with human review decision & update dynamic pipeline state."""
    decision = resume_value["decision"]
    st.session_state.error_message = ""

    action_labels = {
        "approve": "Finalizing & saving approved letter…",
        "edit": "Revising letter with user feedback…",
        "regenerate": "Generating fresh cover letter draft…",
        "reject": "Terminating workflow…",
    }

    # Update Active Node & Trace dynamically BEFORE and DURING resume
    rev = st.session_state.revision_count + 1

    # Mark existing active trace items as completed
    for item in st.session_state.node_execution_trace:
        if item.get("status") == "active":
            item["status"] = "completed"

    if decision == "edit":
        # Loop back through Revision -> Self-Critique -> Human Review
        st.session_state.active_node = "revision"
        st.session_state.node_execution_trace.append(
            {"node": "loop_marker", "label": f"🔄 Loop #{rev}: Requested Edit", "status": "loop"}
        )
        st.session_state.node_execution_trace.append(
            {"node": "revision", "label": f"Revision Node (Rev #{rev})", "status": "completed"}
        )
        st.session_state.node_execution_trace.append(
            {"node": "self_critique", "label": "Self-Critique Engine", "status": "completed"}
        )
        st.session_state.node_execution_trace.append(
            {"node": "human_review", "label": f"Human Review (Rev #{rev})", "status": "active"}
        )

    elif decision == "regenerate":
        # Loop back through Draft Generator -> Self-Critique -> Human Review
        st.session_state.active_node = "draft_generator"
        st.session_state.node_execution_trace.append(
            {"node": "loop_marker", "label": f"🔄 Loop #{rev}: Full Regeneration", "status": "loop"}
        )
        st.session_state.node_execution_trace.append(
            {"node": "draft_generator", "label": f"Draft Generator (Rev #{rev})", "status": "completed"}
        )
        st.session_state.node_execution_trace.append(
            {"node": "self_critique", "label": "Self-Critique Engine", "status": "completed"}
        )
        st.session_state.node_execution_trace.append(
            {"node": "human_review", "label": f"Human Review (Rev #{rev})", "status": "active"}
        )

    elif decision == "approve":
        st.session_state.active_node = "finalize"
        st.session_state.node_execution_trace.append(
            {"node": "finalize", "label": "Finalization & Output Save", "status": "completed"}
        )

    with st.spinner(f"🔄 {action_labels.get(decision, 'Processing…')}"):
        try:
            result = app.resume(resume_value, st.session_state.thread_id)
            st.session_state.result = result

            if "__interrupt__" in result:
                _extract_interrupt(result)
                st.session_state.active_node = "human_review"
            elif decision == "approve":
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                state = app.graph.get_state(config)
                st.session_state.final_letter = state.values.get("final_letter", "")
                st.session_state.company_name = state.values.get("company_name", "")
                st.session_state.role_title = state.values.get("role_title", "")
                st.session_state.revision_count = state.values.get("revision_count", 0)
                st.session_state.active_node = "finalize"
                st.session_state.current_step = "finalized"
            elif decision == "reject":
                st.session_state.active_node = "human_review"
                st.session_state.current_step = "rejected"

            st.rerun()
        except Exception as e:
            st.session_state.error_message = _handle_pipeline_error(e)
            st.error(f"❌ {st.session_state.error_message}")


# ═══════════════════════════════════════════
#  FINALIZED SECTION
# ═══════════════════════════════════════════

def render_finalized():
    st.markdown(
        '<div class="success-banner">🎉 Cover letter approved and saved to output directory!</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="final-letter-card">'
        '<div class="card-header">✨ Your Finalized Cover Letter</div>'
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="letter-content">{st.session_state.final_letter}</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️ Download as Markdown (.md)",
            data=st.session_state.final_letter,
            file_name=f"{st.session_state.company_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        with st.expander("📋 Copy Raw Markdown"):
            st.code(st.session_state.final_letter, language=None)

    # ── Metadata Grid ──
    st.markdown(
        f'<div class="meta-grid">'
        f'<div><div class="meta-item-label">Company</div><div class="meta-item-value">{st.session_state.company_name or "—"}</div></div>'
        f'<div><div class="meta-item-label">Role Title</div><div class="meta-item-value">{st.session_state.role_title or "—"}</div></div>'
        f'<div><div class="meta-item-label">Saved Date</div><div class="meta-item-value">{datetime.now().strftime("%b %d, %Y")}</div></div>'
        f'<div><div class="meta-item-label">Revisions</div><div class="meta-item-value">{st.session_state.revision_count}</div></div>'
        f'<div><div class="meta-item-label">LLM Engine</div><div class="meta-item-value">{DRAFT_MODEL}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("")
    if st.button("✨ Create Another Cover Letter", type="primary", use_container_width=True, key="new_btn"):
        _reset_session()
        st.rerun()


# ═══════════════════════════════════════════
#  REJECTED SECTION
# ═══════════════════════════════════════════

def render_rejected():
    st.info("❌ Application draft was rejected. No cover letter was saved.")
    if st.button("🔄 Start New Application", type="primary", use_container_width=True, key="restart_btn"):
        _reset_session()
        st.rerun()


# ═══════════════════════════════════════════
#  HISTORY DETAIL SECTION
# ═══════════════════════════════════════════

def render_history_detail():
    entry = st.session_state.get("selected_history_item")
    if not entry:
        st.session_state.current_step = "input"
        st.rerun()
        return

    company = entry.get("company", "—")
    role = entry.get("role", "—")
    date = entry.get("date", "—")
    decision = entry.get("decision", "approve")
    revision_count = entry.get("revision_count", 0)
    model_used = entry.get("model_used", DRAFT_MODEL)
    output_path = entry.get("output_path", "")

    st.markdown(
        f'<div class="card">'
        f'<div class="card-header">🏆 Saved Approved Letter: {company}</div>'
        f'<div class="card-subtitle">{role} • Saved on {date}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    letter_content = ""
    file_exists = False
    if output_path:
        full_file = PROJECT_ROOT / output_path
        if full_file.exists():
            try:
                letter_content = full_file.read_text(encoding="utf-8")
                file_exists = True
            except Exception as e:
                letter_content = f"Error reading file: {e}"

    if file_exists and letter_content:
        st.markdown(
            f'<div class="letter-content">{letter_content}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning(f"⚠️ Cover letter file not found at `{output_path}`.")

    st.markdown(
        f'<div class="meta-grid">'
        f'<div><div class="meta-item-label">Company</div><div class="meta-item-value">{company}</div></div>'
        f'<div><div class="meta-item-label">Role Title</div><div class="meta-item-value">{role}</div></div>'
        f'<div><div class="meta-item-label">Date</div><div class="meta-item-value">{date}</div></div>'
        f'<div><div class="meta-item-label">Status</div><div class="meta-item-value">Approved</div></div>'
        f'<div><div class="meta-item-label">Revisions</div><div class="meta-item-value">{revision_count}</div></div>'
        f'<div><div class="meta-item-label">Model Engine</div><div class="meta-item-value">{model_used}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("")

    col1, col2, col3 = st.columns(3)

    with col1:
        prev_step = st.session_state.get("active_step_before_history", "input")
        btn_text = "⬅️ Back to Active Flow" if prev_step != "input" else "⬅️ Back to Input"
        if st.button(btn_text, type="primary", use_container_width=True, key="back_from_hist_btn"):
            st.session_state.current_step = prev_step
            st.session_state.selected_history_item = None
            st.rerun()

    with col2:
        if file_exists and letter_content:
            file_name = Path(output_path).name if output_path else "cover_letter.md"
            st.download_button(
                "⬇️ Download Letter",
                data=letter_content,
                file_name=file_name,
                mime="text/markdown",
                use_container_width=True,
                key="hist_download_btn",
            )

    with col3:
        if file_exists and letter_content:
            with st.expander("📋 Copy Raw Text"):
                st.code(letter_content, language=None)


# ═══════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════

def render_footer():
    st.markdown(
        '<div class="app-footer">'
        '<span>© 2026 DRAFTRON Agentic AI</span>'
        '<span>v0.1.0 • Built with LangGraph & Streamlit</span>'
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════
#  MAIN DISPATCHER
# ═══════════════════════════════════════════

render_header()
render_sidebar()

step = st.session_state.current_step

if step == "input":
    render_input()
elif step == "review":
    render_review()
elif step == "finalized":
    render_finalized()
elif step == "rejected":
    render_rejected()
elif step == "history_detail":
    render_history_detail()

render_footer()
