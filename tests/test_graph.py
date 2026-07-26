"""
Day 6 test harness -- full graph with interrupt/resume via InMemorySaver.
Run from the project root: uv run python tests/test_graph.py

Tests the compiled DraftronGraph end-to-end: start -> interrupt -> resume.
No mocking -- this exercises the real graph, real nodes, real checkpointer.
"""
from graph import PROJECT_ROOT
from graph.builder import DraftronGraph

POSTINGS_DIR = PROJECT_ROOT / "tests" / "fixtures" / "postings"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"


def _count_output_files() -> int:
    if not OUTPUTS_DIR.exists():
        return 0
    return len(list(OUTPUTS_DIR.glob("*.md")))


def _print_full_critique(result: dict, interrupt_payload: dict) -> None:
    """
    Full diagnostic dump -- do_not_claim, every critique field, and the full
    draft text. Not truncated: we need to actually read the whole thing to
    check for paraphrased leaks the deterministic check can't catch.
    """
    do_not_claim = result.get("strategy", {}).get("do_not_claim")
    print(f"\n  do_not_claim: {do_not_claim}")

    critique = interrupt_payload.get("critique", {})
    print(f"  critique.passes:              {critique.get('passes')}")
    print(f"  critique.overstatement_flags: {critique.get('overstatement_flags')}")
    print(f"  critique.length_flag:         {critique.get('length_flag')}")
    print(f"  critique.tone_flag:           {critique.get('tone_flag')}")
    print(f"  critique.notes:               {critique.get('notes')}")

    draft = interrupt_payload.get("draft", "")
    print(f"\n  -- full draft ({len(draft.split())} words) --")
    print(f"  {draft}")

    if do_not_claim:
        lower = draft.lower()
        for term in do_not_claim:
            head_word = term.split()[0].lower()
            if head_word in lower:
                print(f"\n  !! MANUAL CHECK: '{head_word}' (from do_not_claim term '{term}') "
                      f"appears literally in the draft -- read the surrounding sentence "
                      f"to confirm whether this is an actual leak.")


def test_approve_path():
    """Test the happy path: start -> interrupt -> approve -> finalize."""
    print("=" * 60)
    print("=== approve path: full graph interrupt/resume ===")
    print("=" * 60)

    app = DraftronGraph()
    thread_id = "test-approve-001"
    posting_text = (POSTINGS_DIR / "posting_1_clear_split.txt").read_text(encoding="utf-8")

    files_before = _count_output_files()

    print("\n-- Step 1: start() --")
    result = app.start(posting_text, thread_id)

    assert "__interrupt__" in result, "Expected __interrupt__ in result -- graph didn't pause at human_review"
    interrupt_payload = result["__interrupt__"][0].value

    print("  Interrupt received!")
    _print_full_critique(result, interrupt_payload)

    print("\n-- Step 2: resume(decision='approve') --")
    result = app.resume({"decision": "approve"}, thread_id)

    assert "final_letter" in result, "Expected final_letter in result after approve"
    print(f"  final_letter present: True")
    print(f"  Letter length: {len(result['final_letter'].split())} words")

    files_after = _count_output_files()
    assert files_after == files_before + 1, f"Expected 1 new file in outputs/, found {files_after - files_before} new files"
    print(f"  New file saved to outputs/: YES ({files_before} -> {files_after})")

    log_path = PROJECT_ROOT / "data" / "applications_log.jsonl"
    assert log_path.exists(), "applications_log.jsonl should exist"
    last_line = log_path.read_text(encoding="utf-8").strip().split("\n")[-1]
    print(f"  Last log entry: {last_line}")

    print("\n[OK] Approve path passed!")


def test_reject_path():
    """Test the reject path: start -> interrupt -> reject -> END (no save)."""
    print("\n" + "=" * 60)
    print("=== reject path: full graph interrupt/resume ===")
    print("=" * 60)

    app = DraftronGraph()
    thread_id = "test-reject-001"
    posting_text = (POSTINGS_DIR / "posting_2_sparse.txt").read_text(encoding="utf-8")

    files_before = _count_output_files()

    print("\n-- Step 1: start() --")
    result = app.start(posting_text, thread_id)

    assert "__interrupt__" in result, "Expected __interrupt__ in result"
    print("  Interrupt received!")

    print("\n-- Step 2: resume(decision='reject') --")
    result = app.resume({"decision": "reject"}, thread_id)

    has_final = "final_letter" in result and result["final_letter"]
    print(f"  final_letter present: {has_final}")

    files_after = _count_output_files()
    assert files_after == files_before, f"Expected no new file after reject, but found {files_after - files_before} new files"
    print(f"  New file saved to outputs/: NO (correct)")

    print("\n[OK] Reject path passed!")


def test_edit_then_approve():
    """Test the edit loop: start -> interrupt -> edit -> revision -> critique -> interrupt -> approve."""
    print("\n" + "=" * 60)
    print("=== edit loop: start -> edit -> revision -> approve ===")
    print("=" * 60)

    app = DraftronGraph()
    thread_id = "test-edit-001"
    posting_text = (POSTINGS_DIR / "posting_3_mixed.txt").read_text(encoding="utf-8")

    files_before = _count_output_files()

    print("\n-- Step 1: start() --")
    result = app.start(posting_text, thread_id)

    assert "__interrupt__" in result, "Expected __interrupt__ in result"
    draft_v1 = result["__interrupt__"][0].value["draft"]
    print(f"  Draft v1 ({len(draft_v1.split())} words)")

    print("\n-- Step 2: resume(decision='edit', feedback='Make it shorter') --")
    result = app.resume({"decision": "edit", "feedback": "Make it shorter"}, thread_id)

    assert "__interrupt__" in result, "Expected __interrupt__ after edit -- graph should pause again"
    draft_v2 = result["__interrupt__"][0].value["draft"]
    revision_count = result["__interrupt__"][0].value["revision_count"]

    print(f"  Draft v2 ({len(draft_v2.split())} words)")
    print(f"  Revision count: {revision_count}")

    print("\n-- Step 3: resume(decision='approve') --")
    result = app.resume({"decision": "approve"}, thread_id)

    assert "final_letter" in result, "Expected final_letter after approve"
    print(f"  final_letter present: True")

    files_after = _count_output_files()
    print(f"  Outputs directory: {files_after} files")

    print("\n[OK] Edit -> Approve path passed!")


if __name__ == "__main__":
    test_approve_path()
    test_reject_path()
    test_edit_then_approve()
    print("\n" + "=" * 60)
    print("=== ALL DAY 6 TESTS PASSED ===")
    print("=" * 60)