"""LLM factory.

One class does everything: `ChatAnthropic` from langchain-anthropic.

* Amazon Bedrock  — Bedrock exposes the native Anthropic Messages API at
                    https://bedrock-mantle.<region>.api.aws/anthropic and accepts a Bedrock API key as a
                    bearer token. So we point ChatAnthropic at that base URL and add an Authorization header.
                    No boto3, no SigV4.
* Anthropic direct — plain ChatAnthropic with ANTHROPIC_API_KEY.

If both credentials exist, Bedrock is primary and Anthropic is wired in as an automatic fallback via
LangChain's `with_fallbacks`, so a Bedrock outage or quota error transparently retries on Anthropic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from anthropic import Omit
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel


@dataclass(frozen=True)
class LLMSettings:
    provider: str = "auto"  # auto | bedrock | anthropic
    bedrock_token: str | None = None
    aws_region: str = "us-east-1"
    bedrock_model: str = "anthropic.claude-opus-5"
    anthropic_key: str | None = None
    anthropic_model: str = "claude-opus-5"
    effort: str = "high"
    # A 5-question Thai catalog with rationales is ~10-20k output tokens, and adaptive thinking also counts
    # against max_tokens. 16k truncated real runs. Streaming is on so the SDK allows large values.
    max_tokens: int = 48000
    timeout_s: float = 900.0

    @classmethod
    def from_env(cls) -> "LLMSettings":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "auto").lower(),
            bedrock_token=os.getenv("AWS_BEARER_TOKEN_BEDROCK") or None,
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            bedrock_model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-opus-5"),
            anthropic_key=os.getenv("ANTHROPIC_API_KEY") or None,
            anthropic_model=os.getenv("ANTHROPIC_MODEL_ID", "claude-opus-5"),
            effort=os.getenv("LLM_EFFORT", "high"),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "48000")),
        )


def _common(s: LLMSettings) -> dict:
    return {
        "max_tokens": s.max_tokens,
        "thinking": {"type": "adaptive"},
        "effort": s.effort,
        "timeout": s.timeout_s,
        "max_retries": 2,
        # Stream under the hood (invoke() still returns one message). Required by the Anthropic SDK for
        # max_tokens above ~21k, and it avoids HTTP timeouts on long Thai outputs.
        "streaming": True,
    }


def bedrock_llm(s: LLMSettings) -> ChatAnthropic:
    if not s.bedrock_token:
        raise RuntimeError("AWS_BEARER_TOKEN_BEDROCK is not set.")
    llm = ChatAnthropic(
        model=s.bedrock_model,
        base_url=f"https://bedrock-mantle.{s.aws_region}.api.aws/anthropic",
        api_key="",  # do not pick up ANTHROPIC_API_KEY from the environment
        default_headers={"Authorization": f"Bearer {s.bedrock_token}"},
        **_common(s),
    )
    # ChatAnthropic always adds an X-Api-Key header; Bedrock wants only the bearer token.
    # The Anthropic SDK's documented way to drop a default header is the `Omit` sentinel.
    for client in (llm._client, llm._async_client):
        client._custom_headers["X-Api-Key"] = Omit()
    return llm


def anthropic_llm(s: LLMSettings) -> ChatAnthropic:
    if not s.anthropic_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    return ChatAnthropic(model=s.anthropic_model, api_key=s.anthropic_key, **_common(s))


def build_llm(s: LLMSettings | None = None) -> tuple[BaseChatModel, str]:
    """Return (model, description). `model` may already be a fallback chain."""
    s = s or LLMSettings.from_env()

    if s.provider == "bedrock":
        return bedrock_llm(s), f"bedrock:{s.bedrock_model} ({s.aws_region})"
    if s.provider == "anthropic":
        return anthropic_llm(s), f"anthropic:{s.anthropic_model}"

    # auto
    if s.bedrock_token and s.anthropic_key:
        primary, fallback = bedrock_llm(s), anthropic_llm(s)
        return (
            primary.with_fallbacks([fallback]),
            f"bedrock:{s.bedrock_model} ({s.aws_region}) -> fallback anthropic:{s.anthropic_model}",
        )
    if s.bedrock_token:
        return bedrock_llm(s), f"bedrock:{s.bedrock_model} ({s.aws_region})"
    if s.anthropic_key:
        return anthropic_llm(s), f"anthropic:{s.anthropic_model}"
    raise RuntimeError(
        "No credentials found. Set AWS_BEARER_TOKEN_BEDROCK (Bedrock) and/or ANTHROPIC_API_KEY in .env"
    )
