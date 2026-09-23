"""The generation engine: prompt assembly + one structured LLM call.

    catalog = generate(product_questionnaire, factors, llm)

Prompt layout (stable -> volatile, so the static part is prompt-cacheable):
    system  = prompts/system.md + prompts/frameworks.md + prompts/segments.md
    user    = JSON {product, factors, base_questionnaire}
"""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableWithFallbacks

from deep_question.schema import Catalog, Factors, ProductQuestionnaire

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
PROMPT_FILES = ["system.md", "frameworks.md", "segments.md"]


def load_system_prompt(prompts_dir: Path = PROMPTS_DIR) -> str:
    parts = [(prompts_dir / name).read_text(encoding="utf-8").strip() for name in PROMPT_FILES]
    return "\n\n---\n\n".join(parts)


def build_user_payload(base: ProductQuestionnaire, factors: Factors) -> dict:
    return {
        "product": {
            "name": base.product,
            "product_line": base.product_line,
            "description": base.description,
            "entry_age": {"min": base.entry_age_min, "max": base.entry_age_max},
        },
        "factors": factors.model_dump(),
        "base_questionnaire": [q.model_dump() for q in base.questions],
    }


def build_messages(
    base: ProductQuestionnaire,
    factors: Factors,
    prompts_dir: Path = PROMPTS_DIR,
    use_anthropic_cache: bool = True,
) -> list[BaseMessage]:
    system_text = load_system_prompt(prompts_dir)
    payload = build_user_payload(base, factors)
    user_text = (
        f"Design the personalized questionnaire for this segment. "
        f"Produce exactly {factors.n_steps} questions.\n\n"
        f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
    )
    if use_anthropic_cache:
        sys_msg = SystemMessage(
            content=[{"type": "text", "text": system_text, "cache_control": {"type": "ephemeral"}}]
        )
    else:
        sys_msg = SystemMessage(content=system_text)
    return [
        sys_msg,
        HumanMessage(content=user_text),
    ]


def _structured(llm: BaseChatModel):
    """Attach the Catalog schema. Works for ChatBedrockConverse, ChatAnthropic, and fallback chains."""
    def _bind(model: BaseChatModel):
        model_cls_name = model.__class__.__name__
        if "Bedrock" in model_cls_name:
            # Bedrock models may reject tool_choice="tool" and "any", only supporting "auto"
            if hasattr(model, "supports_tool_choice_values"):
                model.supports_tool_choice_values = ("auto",)
            return model.with_structured_output(Catalog, method="function_calling", include_raw=True)
        try:
            return model.with_structured_output(Catalog, method="json_schema", include_raw=True)
        except Exception:
            return model.with_structured_output(Catalog, include_raw=True)

    if isinstance(llm, RunnableWithFallbacks):
        primary = _bind(llm.runnable)
        fallbacks = [_bind(f) for f in llm.fallbacks]
        return primary.with_fallbacks(fallbacks)
    return _bind(llm)


class OutputTruncated(RuntimeError):
    """The model hit max_tokens before finishing the catalog JSON."""


def generate(base: ProductQuestionnaire, factors: Factors, llm: BaseChatModel, prompts_dir: Path = PROMPTS_DIR) -> Catalog:
    primary_model = getattr(llm, "runnable", llm)
    is_bedrock = "Bedrock" in primary_model.__class__.__name__
    messages = build_messages(base, factors, prompts_dir, use_anthropic_cache=not is_bedrock)
    result = _structured(llm).invoke(messages)  # {"raw": AIMessage, "parsed": Catalog | None, "parsing_error": ...}

    raw = result["raw"]
    stop_reason = raw.response_metadata.get("stop_reason")
    usage = raw.usage_metadata or {}
    if stop_reason == "max_tokens":
        raise OutputTruncated(
            f"model stopped at max_tokens after {usage.get('output_tokens', '?')} output tokens "
            f"(thinking counts too). Raise LLM_MAX_TOKENS in .env or lower LLM_EFFORT."
        )
    if stop_reason == "refusal":
        raise RuntimeError(f"model refused: {raw.response_metadata.get('stop_details')}")
    if result.get("parsing_error") is not None:
        raise result["parsing_error"]

    catalog = result["parsed"]
    if not isinstance(catalog, Catalog):  # dict when schema given as JSON; keep type stable
        catalog = Catalog.model_validate(catalog)
    catalog.__dict__["usage"] = usage  # attach for the CLI without changing the schema
    validate_contract(catalog, base)
    return catalog


def validate_contract(catalog: Catalog, base: ProductQuestionnaire) -> list[str]:
    """Cheap, deterministic checks of the data contract. Returns warnings (also attached for the CLI to print)."""
    warnings: list[str] = []
    by_key = {q.key: q for q in base.questions}

    covered = [q.source_question_key for q in catalog.questions]
    for q in base.core_questions():
        deferred = {d.source_question_key for d in catalog.deferred_questions}
        if q.key not in covered and q.key not in deferred:
            warnings.append(f"core question '{q.key}' is neither covered nor deferred")

    for q in catalog.questions:
        src = by_key.get(q.source_question_key)
        if src is None:
            warnings.append(f"{q.question_id}: unknown source_question_key '{q.source_question_key}'")
            continue
        for o in q.options:
            if o.source_question_key != q.source_question_key:
                warnings.append(f"{q.question_id}/{o.option_id}: option maps to a different question than its step")
            if src.options and o.source_option not in src.options and o.source_option != "FREE_TEXT":
                warnings.append(f"{q.question_id}/{o.option_id}: source_option '{o.source_option}' not in base options")
        if src.options:
            mapped = {o.source_option for o in q.options}
            missing = [b for b in src.options if b not in mapped and "อื่นๆ" not in b]
            if missing:
                warnings.append(f"{q.question_id}: base options not represented: {missing}")

    catalog.__dict__["contract_warnings"] = warnings  # attach without changing schema
    return warnings
