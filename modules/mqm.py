import json
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# SEVERITY LEVELS
# ============================================================================
class Severity(str, Enum):
    NEUTRAL = "neutral"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


# ============================================================================
# MAIN ERROR TYPE (Level 0)
# ============================================================================
class ErrorCategory(str, Enum):
    # """Top-level MQM error categories"""

    TERMINOLOGY = "terminology"
    ACCURACY = "accuracy"
    FLUENCY = "fluency"
    STYLE = "style"
    LOCALE_CONVENTIONS = "locale-conventions"
    VERITY = "verity"
    DESIGN = "design"


# ============================================================================
# MQM ERROR MODEL
# ============================================================================
class MQMError(BaseModel):
    # Represents a single MQM error annotation with hierarchical error taxonomy.

    # Error classification
    category: ErrorCategory = Field()  # description="Top-level error category (Level 0)")

    # Severity
    severity: Severity = Field()  # description="Error severity: neutral/minor/major/critical")

    class TokenInfo(BaseModel):
        token_index: Optional[list[int]] = Field(
            None,
            ge=0,
            description="The position of a single or adjacent words in the text (word offset, 0-indexed)",
        )
        character_span: Optional[list[int]] = Field(
            default_factory=lambda: [],
            description="List of start and end positions in text (character offsets, 0-indexed)",
        )
        token: Optional[str] = Field(
            None, description="The token(s) (single or adjacent full words) in question in the text"
        )

    in_source: TokenInfo
    in_target: TokenInfo


# ============================================================================
# DOCUMENT-LEVEL ANNOTATION MODEL
# ============================================================================
class MQMAnnotation(BaseModel):
    # """Complete MQM annotation for a translation segment or document."""

    errors: list[MQMError] = Field(
        default_factory=list, description="List of identified MQM errors"
    )

    model_config = {
        "json_schema_extra": {
            "additionalProperties": False,  # mandatory by OpenAI
        }
    }


def get_openai_schema(model_class: type[BaseModel]) -> dict[str, Any]:
    """
    Convert a Pydantic model into a OpenAI-compliant JSON Schema suitable for `response_format` by:

    - Recursively adding additionalProperties: false
    - Ensuring required contains all property keys
    - Moving descriptions inside definitions if needed
    - Cleaning any $ref nodes for OpenAI validator.

    Args:
        model_class (type[BaseModel]): The Pydantic model to be converted.

    Returns:
        dict[str, Any]: The OpenAI-compliant JSON schema for an LLM's response format.
    """
    schema = model_class.model_json_schema(ref_template="#/definitions/{model}")

    def fix_node(node: dict):
        if not isinstance(node, dict):
            return

        # Objects must have additionalProperties: false
        if node.get("type") == "object":
            node.setdefault("additionalProperties", False)
            props = node.get("properties")
            if isinstance(props, dict):
                node["required"] = list(props.keys())

        # Recurse into standard keys
        for key in ("properties", "$defs", "definitions"):
            if key in node and isinstance(node[key], dict):
                for child in node[key].values():
                    fix_node(child)

        # Recurse into array items
        if "items" in node:
            fix_node(node["items"])

        # Recurse into combinators
        for combo in ("oneOf", "anyOf", "allOf"):
            if combo in node and isinstance(node[combo], list):
                for child in node[combo]:
                    fix_node(child)

    fix_node(schema)
    return schema


if __name__ == "__main__":
    mqm = MQMAnnotation()
    print(json.dumps(get_openai_schema(MQMAnnotation), ensure_ascii=False, indent=2))
