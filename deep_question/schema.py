"""Data contracts.

Two halves:
  * INPUT  — the fixed base questionnaire loaded from Excel (`BaseQuestion`, `ProductQuestionnaire`) and
             the targeting `Factors`.
  * OUTPUT — the personalized `Catalog` the LLM must return. This is also the JSON schema handed to the
             model for structured output, so field docstrings double as instructions to the model.
"""

from __future__ import annotations

from typing import Literal, get_args

from pydantic import BaseModel, Field, computed_field

# --------------------------------------------------------------------------- INPUT

QuestionRole = Literal["default", "core", "uw", "spare"]
Channel = Literal["facebook", "tiktok", "instagram", "google"]
# Age of the INSURED (the person the policy is for), not necessarily the visitor.
AgeBracket = Literal["0-22", "23-45", "46-60", "60+"]
Gender = Literal["male", "female"]
# Who the visitor is applying for. "other" = buying for a parent, child, spouse, sibling...
Applicant = Literal["me", "other"]

SELF_APPLY_MIN_AGE = 20  # youngest insured age that can realistically apply for themselves


def bracket_bounds(bracket: str) -> tuple[int, int]:
    """'0-22' -> (0, 22); '60+' -> (60, 200)."""
    if bracket.endswith("+"):
        return int(bracket[:-1]), 200
    lo, hi = bracket.split("-")
    return int(lo), int(hi)


class BaseQuestion(BaseModel):
    key: str = Field(description="Stable machine key, e.g. reason_why, budget.")
    role: QuestionRole
    order: int = Field(description="Business order within the product (1..n). 0 for defaults.")
    text: str = Field(description="Original question text (Thai).")
    options: list[str] = Field(default_factory=list, description="Empty list means free text / numeric.")


class ProductQuestionnaire(BaseModel):
    product: str
    product_line: Literal["Non-Life", "Life"]
    description: str = ""
    entry_age_min: int | None = Field(default=None, description="Youngest insured age the product accepts.")
    entry_age_max: int | None = Field(default=None, description="Oldest insured age the product accepts.")
    questions: list[BaseQuestion]

    def core_questions(self) -> list[BaseQuestion]:
        return [q for q in self.questions if q.role == "core"]

    def eligible_age_brackets(self, applicant: str, self_apply_min_age: int = SELF_APPLY_MIN_AGE) -> list[str]:
        """Brackets that overlap the product's entry-age window; for 'me', the insured must be old enough to apply."""
        lo_p = self.entry_age_min if self.entry_age_min is not None else 0
        hi_p = self.entry_age_max if self.entry_age_max is not None else 200
        out: list[str] = []
        for b in get_args(AgeBracket):
            lo, hi = bracket_bounds(b)
            if hi < lo_p or lo > hi_p:
                continue
            if applicant == "me" and min(hi, hi_p) < self_apply_min_age:
                continue
            out.append(b)
        return out


class Factors(BaseModel):
    channel: Channel
    applicant: Applicant = Field(description="'me' = visitor is the insured; 'other' = visitor buys for someone else.")
    age_bracket: AgeBracket = Field(description="Age bracket of the INSURED.")
    gender: Gender = Field(description="Gender of the INSURED.")
    copy_language: str = Field(default="th", description="BCP-47-ish code for customer-facing copy.")
    n_steps: int = Field(default=5, ge=3, le=7)


# --------------------------------------------------------------------------- OUTPUT

StepPhase = Literal["hook", "pain", "gap", "profile", "emotion"]
SpinStage = Literal["Situation", "Problem", "Implication", "Fact-Check", "Need-Payoff"]
InputType = Literal["single_select", "multi_select", "free_text", "number"]


class Option(BaseModel):
    option_id: str = Field(description="Stable id, e.g. Q1_A, Q1_B.")
    label: str = Field(description="Customer-facing option text, phrased as the visitor's own inner voice.")
    source_question_key: str = Field(description="The base question `key` this option belongs to.")
    source_option: str = Field(
        description="Verbatim base option text this maps to. Use 'FREE_TEXT' if the base field has no options."
    )
    underlying_intent: str = Field(description="3-8 English words a TSR can scan, e.g. 'loss aversion via proximity'.")
    micro_reflection: str = Field(description="1-2 sentences shown instantly on selection. Validate, reframe, bridge.")
    reflection_technique: str = Field(
        description="Named technique: Feel-Felt-Found | Reframing | Normalising | Social proof | FAB translation | Anchoring | Permission"
    )
    risk_weight: int = Field(
        default=0,
        ge=0,
        le=30,
        description="Risk score points (0-30) contributed if this option is chosen. Higher = greater exposure/vulnerability.",
    )
    gap_statement: str = Field(
        default="",
        description="Specific 1-sentence customer vulnerability statement if this option reveals an unaddressed risk or gap.",
    )


class BiasCard(BaseModel):
    bias: str = Field(description="Cognitive bias name, e.g. Loss aversion. Strictly internal for TSR/Reviewer.")
    text: str = Field(
        description="1-2 sentences in natural Thai. Empathetic priming quote and narrative bridge toward the next question. NEVER prefix with bias name or category."
    )
    why_this_bias: str = Field(description="English: why this bias fits this segment and how it bridges step N to N+1.")
    needs_fact_check: bool = Field(description="True if the copy contains any number or claim not given in the input.")


class Question(BaseModel):
    question_id: str = Field(description="Q1..Qn in display order.")
    step_phase: StepPhase
    spin_stage: SpinStage
    source_question_key: str = Field(description="Which base question this step covers.")
    headline: str = Field(description="The question as an advisor would ask it. One sentence, second person.")
    sub_headline: str = Field(description="One short line giving a reason to answer or a normalising primer.")
    input_type: InputType
    options: list[Option]
    bias_card: BiasCard
    design_rationale: str = Field(
        description="English, 2-4 sentences: principle used, why it fits this person, what the TSR learns."
    )


class DeferredQuestion(BaseModel):
    source_question_key: str
    handled_by: Literal["tsr_call", "post_submit_form", "dropped"]
    reason: str


class PrincipleNote(BaseModel):
    principle: str = Field(description="e.g. SPIN - Implication, GAP analysis, Maslow - Safety, Anchoring")
    where_applied: str = Field(description="Which question/option/reflection ids.")
    explanation: str = Field(description="Plain-English explanation a marketing manager can repeat.")


class CatalogMetadata(BaseModel):
    product: str
    product_line: str
    channel: str
    applicant: str = Field(description="me | other")
    age_bracket: str = Field(description="Insured's age bracket.")
    gender: str = Field(description="Insured's gender.")
    copy_language: str
    primary_archetype: str
    secondary_archetype: str | None = None
    maslow_level: str
    tone: str = Field(description="3-6 words describing the voice, e.g. 'calm, protective, family-first'.")


class Catalog(BaseModel):
    """The complete personalized questionnaire for one segment."""

    catalog_id: str = Field(
        description=(
            "UPPER_SNAKE: PRODUCT_CHANNEL_APPLICANT_AGE_GENDER_V1. Channel codes: FB, TT, IG, GG. "
            "Applicant: ME, OTH. Age codes: 0022, 2345, 4660, 60P. Gender: M, F. "
            "e.g. CANCER_FB_ME_2345_F_V1, SENIOR55_FB_OTH_60P_F_V1"
        )
    )
    metadata: CatalogMetadata
    persona_read: str = Field(description="English. Who this person is at the moment of the click; specific, not generic.")
    strategy: str = Field(description="English. The conversation arc in plain language, step by step.")

    # Screen 1: Diagnostic Hook (Frames 2, 3, 4, 5 - ALL DYNAMIC)
    hook_headline: str = Field(description="Frame 2: Bold emotional hook question tailored to segment")
    anchor_label: str = Field(description="Frame 3: Contextual stat label e.g. ค่าห้องเดี่ยวมาตรฐาน รพ.เอกชน ต่อคืน หรือ ค่ารักษาเฉลี่ยโรคมะเร็ง")
    anchor_number: str = Field(description="Frame 3: Prominent stat or cost figure e.g. ฿8,000 หรือ ฿1,500,000")
    anchor_sub_caption: str = Field(description="Frame 3: Sobering caveat e.g. ยังไม่รวมค่าหมอ ค่ายา และค่าผ่าตัด")
    diagnostic_promise: str = Field(description="Frame 4: Clear reason to complete questionnaire e.g. ตอบไม่กี่คำถาม รู้ว่าคุณต้องมีวงเงินเท่าไหร่...")
    hook_cta_text: str = Field(description="Frame 5: Action-oriented CTA button tailored to segment")

    # Screen 2: Pre-Submit Landing Bridge
    social_proof: str = Field(description="Screen 2: Peer group adoption stat tailored to demographic.")
    insight_message: str = Field(description="Screen 2: Personalized framing message connecting medical inflation, product, and peace of mind.")
    pre_submit_cta: str = Field(description="Screen 2: Reassuring action CTA button text with microcopy.")

    # Screen 3: Result Evaluation Matrix
    base_risk_score: int = Field(default=15, ge=0, le=50, description="Baseline risk score (0-50) derived from age/gender/product.")
    default_gap_statement: str = Field(description="Screen 3: Fallback 1-sentence vulnerability gap statement.")

    questions: list[Question]
    deferred_questions: list[DeferredQuestion] = Field(default_factory=list)
    principles_applied: list[PrincipleNote]
    tsr_brief_notes: str = Field(description="English. How a TSR should read the combination of answers before dialing.")
    claims_to_verify: list[str] = Field(
        default_factory=list,
        description="Every number or factual claim in the copy that the business must verify before shipping.",
    )

    @computed_field
    def landing_hook(self) -> dict:
        return {
            "headline": self.hook_headline,
            "anchor_card": {
                "label": self.anchor_label,
                "highlight_number": self.anchor_number,
                "sub_caption": self.anchor_sub_caption,
            },
            "diagnostic_promise": self.diagnostic_promise,
            "cta_text": self.hook_cta_text,
        }

    @computed_field
    def pre_submit_landing(self) -> dict:
        return {
            "social_proof": self.social_proof,
            "insight_card": {
                "title": "ข้อความถึงคุณโดยเฉพาะ",
                "message": self.insight_message,
            },
            "cta_label": self.pre_submit_cta,
            "cta_subtext": "ไม่มีข้อผูกมัด ผู้เชี่ยวชาญโทรอธิบายภายใน 24 ชม.",
        }

    @computed_field
    def result_matrix(self) -> dict:
        return {
            "base_risk_score": self.base_risk_score,
            "default_gap_statement": self.default_gap_statement,
        }

