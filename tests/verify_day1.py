"""
Day 1 sanity check for DRAFTRON.
Run from the project root: python tests/verify_day1.py
"""
import json
import os
import sys
from pathlib import Path

passed, failed = [], []

def check(name, condition, hint=""):
    if condition:
        passed.append(name)
        print(f"  PASS  {name}")
    else:
        failed.append(name)
        print(f"  FAIL  {name}" + (f"  -> {hint}" if hint else ""))

print("== 1. Folder structure ==")
for d in ["graph", "graph/nodes", "models", "prompts", "data", "outputs", "tests"]:
    check(f"{d}/ exists", Path(d).is_dir(), f"mkdir -p {d}")
for f in ["requirements.txt", ".env.example", "graph/state.py", "data/profile.json"]:
    check(f"{f} exists", Path(f).is_file())

print("\n== 2. .env keys present ==")
check(".env exists", Path(".env").is_file(), "cp .env.example .env and fill it in")
if Path(".env").is_file():
    from dotenv import load_dotenv
    load_dotenv()
    check("OPENAI_API_KEY set", bool(os.getenv("OPENAI_API_KEY")))
    check("GROQ_API_KEY set", bool(os.getenv("GROQ_API_KEY")))

print("\n== 3. Dependencies importable ==")
for pkg in ["langgraph", "langchain", "langchain_openai", "langchain_groq", "streamlit", "pydantic", "dotenv"]:
    try:
        __import__(pkg)
        check(f"import {pkg}", True)
    except ImportError as e:
        check(f"import {pkg}", False, str(e))

print("\n== 4. profile.json is valid and populated ==")
try:
    data = json.loads(Path("data/profile.json").read_text())
    check("profile.json is valid JSON", True)
    for key in ["name", "skills", "projects", "certifications", "education"]:
        check(f"profile.json has '{key}'", key in data)
    check("at least 1 project listed", len(data.get("projects", [])) > 0)
    check("at least 1 skill category", len(data.get("skills", {})) > 0)
except Exception as e:
    check("profile.json is valid JSON", False, str(e))

print("\n== 5. graph/state.py defines the right shapes ==")
sys.path.insert(0, ".")
try:
    from graph.state import CoverLetterState, JDExtraction, ProfileMatch, CritiqueResult
    check("CoverLetterState importable", True)
    check("JDExtraction importable", True)
    check("ProfileMatch importable", True)
    check("CritiqueResult importable", True)
    JDExtraction(company_name="Test Co", role_title="AI Engineer", seniority="mid",
                 required_skills=["Python"], key_responsibilities=["build things"])
    check("JDExtraction validates a sample payload", True)
except Exception as e:
    check("graph/state.py imports and validates cleanly", False, str(e))

print(f"\n{len(passed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)