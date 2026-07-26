from typing import TypedDict, Literal, Optional, Annotated
from pydantic import BaseModel, Field, field_validator
import operator

class CoverLetterState(TypedDict, total=False):
    job_posting_raw: str
    company_name: str
    role_title: str
    jd_structured: dict
    candidate_profile: dict
    matched_skills: list[str]
    skill_gaps: list[str]
    relevant_projects: list[str]
    strategy: dict
    strongest_angle: str
    draft: str
    critique: dict
    revision_count: int
    human_feedback: Optional[str]
    human_feedback_history: Annotated[list[str], operator.add]
    decision: Literal["approve", "edit", "regenerate", "reject"]
    final_letter: str

class JDExtraction(BaseModel):
    company_name: str
    role_title: str
    seniority: str
    required_skills: list[str]
    nice_to_have_skills: list[str] = Field(default_factory=list)
    culture_signals: list[str] = Field(default_factory=list)
    key_responsibilities: list[str]


class ProfileMatch(BaseModel):
    matched_skills: list[str]
    skill_gaps: list[str]
    relevant_projects: list[str]
    strongest_angle: str

    ## A Fix for writing a long story in skill_gaps field 
    @field_validator("skill_gaps")
    @classmethod
    def gaps_are_short_skill_names(cls, v: list[str]) -> list[str]:
        for entry in v:
            if len(entry.split()) > 6:
                raise ValueError(
                    f"skill_gaps entry too long/sentence-like: '{entry}' — "
                    "likely a decomposed explanation rather than a skill name"
                )
        return v


class Strategy(BaseModel):
    tone: str
    lead_project: Optional[str] = None
    opening_angle: str
    do_not_claim: list[str] = Field(default_factory=list)
    supporting_points: list[str]

class CritiqueResult(BaseModel):
    passes: bool
    overstatement_flags: list[str] = Field(default_factory=list)
    length_flag: bool
    tone_flag: bool
    education_mentions: list[str] = Field(default_factory=list)
    formulaic_phrases: list[str] = Field(default_factory=list)
    filler_flags: list[str] = Field(default_factory=list)
    notes: str

class CritiqueJudgment(BaseModel):
    tone_flag: bool
    tone_notes: str
    paraphrased_overstatement_flags: list[str] = Field(default_factory=list)
    filler_flags: list[str] = Field(default_factory=list)