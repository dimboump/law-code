import enum
from collections.abc import Sequence
from typing import Any

import pandas as pd
import tiktoken
from pydantic import BaseModel


class ModelMeta(BaseModel):
    api_name: str
    tokenizer_model: str
    input_tokens_cost: float  # USD per 1m tokens
    output_tokens_cost: float  # USD per 1m tokens
    latency: str  # e.g. "low", "medium", "high"
    input_types: tuple[str, ...]
    output_types: tuple[str, ...]

    class Config:
        model_config = {"frozen": True}


class GPT(enum.Enum):
    _4_1 = ModelMeta(
        api_name="gpt-4.1-2025-04-14",
        tokenizer_model="o200k_base",
        input_tokens_cost=2,
        output_tokens_cost=0.5,
        latency="high",
        input_types=("text", "image"),
        output_types=("text",),
    )
    _4o_default = ModelMeta(
        api_name="gpt-4o-2024-08-06",
        tokenizer_model="o200k_base",
        input_tokens_cost=2.5,
        output_tokens_cost=10,
        latency="medium",
        input_types=("text",),
        output_types=("text",),
    )
    _4o_latest = ModelMeta(
        api_name="gpt-4o-2024-11-20",
        tokenizer_model="o200k_base",
        input_tokens_cost=2.5,
        output_tokens_cost=10,
        latency="low",
        input_types=("text", "code"),
        output_types=("text", "code"),
    )


def gpt_models_to_df() -> pd.DataFrame:
    def sanitize_values(model_metadata: ModelMeta) -> dict[str, Any]:
        sanitized = {}

        for k, v in model_metadata.model_dump().items():
            sanitized_k = k.replace("_", " ").title()
            if "Cost" in sanitized_k:
                sanitized_k += " (USD per 1 million)"

            if isinstance(v, Sequence) and not isinstance(v, (str, bytes)):
                sanitized_v = ", ".join(v)
                sanitized[sanitized_k] = sanitized_v
            else:
                sanitized[sanitized_k] = v

        return sanitized

    data = {model.name: sanitize_values(model.value) for model in GPT}
    df = pd.DataFrame(data)
    return df


def count_tokens(text: str, model: GPT) -> int:
    enc = tiktoken.get_encoding(model.value.tokenizer_model)
    tokens = enc.encode(text=text)
    return len(tokens)
