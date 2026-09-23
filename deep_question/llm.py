"""LLM factory.

Supports:
* Amazon Bedrock  — via `langchain_aws.ChatBedrockConverse` using standalone Bedrock API key.
* Anthropic direct — plain `ChatAnthropic` with ANTHROPIC_API_KEY.

If credentials for both exist, Bedrock is primary and Anthropic is wired as an automatic fallback via
LangChain's `with_fallbacks`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrockConverse
from langchain_core.language_models import BaseChatModel


@dataclass(frozen=True)
class LLMSettings:
    provider: str = "auto"  # auto | bedrock | anthropic

    # AWS Bedrock settings (standalone API key)
    bedrock_api_key: str | None = None
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    # Anthropic direct settings
    anthropic_key: str | None = None
    anthropic_model: str = "claude-opus-5"

    effort: str = "high"
    # A 5-question Thai catalog with rationales is ~10-20k output tokens, and adaptive thinking also counts
    # against max_tokens. 16k truncated real runs.
    max_tokens: int = 48000
    timeout_s: float = 900.0

    @classmethod
    def from_env(cls) -> "LLMSettings":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "auto").lower(),
            bedrock_api_key=os.getenv("BEDROCK_API_KEY") or os.getenv("AWS_BEARER_TOKEN_BEDROCK") or None,
            aws_region=os.getenv("AWS_REGION") or "us-east-1",
            bedrock_model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
            anthropic_key=os.getenv("ANTHROPIC_API_KEY") or None,
            anthropic_model=os.getenv("ANTHROPIC_MODEL_ID", "claude-opus-5"),
            effort=os.getenv("LLM_EFFORT", "high"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "48000")),
        )


def _common_anthropic(s: LLMSettings) -> dict:
    return {
        "max_tokens": s.max_tokens,
        "thinking": {"type": "adaptive"},
        "effort": s.effort,
        "timeout": s.timeout_s,
        "max_retries": 2,
        "streaming": True,
    }


def bedrock_llm(s: LLMSettings) -> BaseChatModel:
    """Build Bedrock chat model via langchain_aws.ChatBedrockConverse with standalone Bedrock API key."""
    if not s.bedrock_api_key:
        raise RuntimeError(
            "BEDROCK_API_KEY is not set. Please add your standalone Bedrock API key to .env"
        )

    return ChatBedrockConverse(
        model=s.bedrock_model,
        region_name=s.aws_region,
        bedrock_api_key=s.bedrock_api_key,
        max_tokens=s.max_tokens,
        timeout=s.timeout_s,
        max_retries=2,
        supports_tool_choice_values=("auto",),
    )


def anthropic_llm(s: LLMSettings) -> ChatAnthropic:
    if not s.anthropic_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    return ChatAnthropic(model=s.anthropic_model, api_key=s.anthropic_key, **_common_anthropic(s))


def build_llm(s: LLMSettings | None = None) -> tuple[BaseChatModel, str]:
    """Return (model, description). `model` may already be a fallback chain."""
    s = s or LLMSettings.from_env()

    if s.provider == "bedrock":
        return bedrock_llm(s), f"bedrock:{s.bedrock_model} ({s.aws_region})"
    if s.provider == "anthropic":
        return anthropic_llm(s), f"anthropic:{s.anthropic_model}"

    # auto
    if s.bedrock_api_key and s.anthropic_key:
        primary, fallback = bedrock_llm(s), anthropic_llm(s)
        return (
            primary.with_fallbacks([fallback]),
            f"bedrock:{s.bedrock_model} ({s.aws_region}) -> fallback anthropic:{s.anthropic_model}",
        )
    if s.bedrock_api_key:
        return bedrock_llm(s), f"bedrock:{s.bedrock_model} ({s.aws_region})"
    if s.anthropic_key:
        return anthropic_llm(s), f"anthropic:{s.anthropic_model}"

    raise RuntimeError(
        "No credentials found. Set BEDROCK_API_KEY (Bedrock) and/or ANTHROPIC_API_KEY in .env"
    )



