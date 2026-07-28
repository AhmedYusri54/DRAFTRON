# models/router.py
import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


GROQ_MODEL = "llama-3.3-70b-versatile"

GEN_PROVIDER = os.getenv("DRAFTRON_GEN_PROVIDER", "openai")  # "openai" or "groq"
DRAFT_MODEL = os.getenv(
    "DRAFTRON_GEN_MODEL",
    "gpt-4o-mini" if GEN_PROVIDER == "openai" else GROQ_MODEL,
)


def get_extraction_model():
    return ChatGroq(model=GROQ_MODEL, temperature=0)


def get_matching_model():
    return ChatGroq(model=GROQ_MODEL, temperature=0)


def get_generation_model():
    if GEN_PROVIDER == "groq":
        return ChatGroq(model=DRAFT_MODEL, temperature=0.7)
    return ChatOpenAI(model=DRAFT_MODEL, temperature=0.7)


def get_critique_model():
    return ChatGroq(model=GROQ_MODEL, temperature=0)
