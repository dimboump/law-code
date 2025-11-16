import json
from enum import Enum
from typing import Optional

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
# TERMINOLOGY ERRORS (Level 0: terminology)
# ============================================================================


class TerminologyLevel1(str, Enum):
    # """Level 1 terminology error types"""

    TERMBASE = "termbase"  # Inconsistent with terminology resource
    TERM_INCONSISTENCY = "term-inconsistency"  # Inconsistent use of terminology
    WRONG_TERM = "wrong-term"  # Wrong term


class TerminologyLevel2(str, Enum):
    # """Level 2 terminology error types"""

    # Under termbase
    TERMINOLOGY_COMPANY = "terminology-company"
    TERMINOLOGY_THIRD_PARTY = "terminology-third-party"
    # Under term-inconsistency
    MULTIPLE_TERMS_FOR_CONCEPT = "multiple-terms-for-concept"
    MULTIPLE_TRANSLATIONS_OF_TERM = "multiple-translations-of-term"
    INCONSISTENT_ABBREVIATIONS = "inconsistent-abbreviations"
    # Under wrong-term
    TERM_COLLOCATION = "term-collocation"


# ============================================================================
# ACCURACY ERRORS (Level 0: accuracy)
# ============================================================================


class AccuracyLevel1(str, Enum):
    # """Level 1 accuracy error types"""

    MISTRANSLATION = "mistranslation"
    OVER_TRANSLATION = "over-translation"
    UNDER_TRANSLATION = "under-translation"
    ADDITION = "addition"
    OMISSION = "omission"
    EUPHEMISM = "euphemism"
    NO_TRANSLATE = "no-translate"
    UNTRANSLATED = "untranslated"
    RETAINED_FACTUAL_ERROR = "retained-factual-error"
    COMPLETENESS = "completeness"


class AccuracyLevel2(str, Enum):
    # """Level 2 accuracy error types"""

    # Under mistranslation
    TECHNICAL_RELATIONSHIP = "technical-relationship"
    AMBIGUOUS_TARGET = "ambiguous-target"
    AMBIGUOUS_SOURCE = "ambiguous-source"
    FALSE_FRIEND = "false-friend"
    UNIT_CONVERSION = "unit-conversion"
    NUMBER = "number"
    DATE_TIME = "date-time"
    ENTITY = "entity"
    OVERLY_LITERAL = "overly-literal"
    MT_HALLUCINATION = "mt-hallucination"
    # Under omission
    OMITTED_VARIABLE = "omitted-variable"
    # Under untranslated
    UNTRANSLATED_GRAPHIC = "untranslated-graphic"
    # Under completeness
    INCOMPLETE_LIST = "incomplete-list"
    INCOMPLETE_PROCEDURE = "incomplete-procedure"


# ============================================================================
# FLUENCY ERRORS (Level 0: fluency)
# ============================================================================


class FluencyLevel1(str, Enum):
    # """Level 1 fluency error types"""

    GRAMMAR = "grammar"
    PUNCTUATION = "punctuation"
    WHITESPACE = "whitespace"
    SPELLING = "spelling"
    TITLE_STYLE = "title-style"
    CORPUS_CONFORMANCE = "corpus-conformance"
    PATTERN_PROBLEM = "pattern-problem"
    DUPLICATION = "duplication"
    SORTING = "sorting"
    UNCLEAR_REFERENCE = "unclear-reference"
    UNINTELLIGIBLE = "unintelligible"
    CHARACTER_ENCODING = "character-encoding"
    NONALLOWED_CHARACTERS = "nonallowed-characters"
    TEXTUAL_CONVENTIONS = "textual-conventions"


class FluencyLevel2(str, Enum):
    # """Level 2 fluency error types"""

    # Under grammar
    WORD_FORM = "word-form"
    WORD_ORDER = "word-order"
    FUNCTION_WORDS = "function-words"
    GENERAL_COLLOCATION = "general-collocation"
    # Under punctuation
    UNPAIRED_MARKS = "unpaired-marks"
    # Under spelling
    DIACRITICS = "diacritics"
    TRANSLITERATION = "transliteration"
    CAPITALIZATION = "capitalization"
    COMPOUNDING = "compounding"
    # Under textual-conventions
    INDEX_TOC = "index-toc"
    IMAGES_VS_TEXT = "images-vs-text"
    COHESION = "cohesion"
    COHERENCE = "coherence"


class FluencyLevel3(str, Enum):
    # """Level 3 fluency error types"""

    # Under word-form
    PART_OF_SPEECH = "part-of-speech"
    TENSE_MOOD_ASPECT = "tense-mood-aspect"
    AGREEMENT = "agreement"
    # Under index-toc
    MISSING_INCORRECT_TOC_ITEM = "missing-incorrect-toc-item"
    PAGE_REFERENCES = "page-references"
    INDEX_TOC_FORMAT = "index-toc-format"


# ============================================================================
# STYLE ERRORS (Level 0: style)
# ============================================================================


class StyleLevel1(str, Enum):
    # """Level 1 style error types"""

    COMPANY_STYLE = "company-style"
    THIRD_PARTY_STYLE = "third-party-style"
    INCONSISTENT_EXTERNAL_REFERENCE = "inconsistent-external-reference"
    REGISTER = "register"
    AWKWARD = "awkward"
    UNIDIOMATIC = "unidiomatic"
    INCONSISTENT_STYLE = "inconsistent-style"


class StyleLevel2(str, Enum):
    # """Level 2 style error types"""

    # Under register
    GRAMMATICAL_REGISTER = "grammatical-register"
    VARIANTS_SLANG = "variants-slang"


# ============================================================================
# LOCALE CONVENTION ERRORS (Level 0: locale-conventions)
# ============================================================================


class LocaleConventionLevel1(str, Enum):
    # """Level 1 locale convention error types"""

    NUMBER_FORMAT = "number-format"
    CURRENCY_FORMAT = "currency-format"
    MEASUREMENT_FORMAT = "measurement-format"
    TIME_FORMAT = "time-format"
    DATE_FORMAT = "date-format"
    CALENDAR_TYPE = "calendar-type"
    NAME_FORMAT = "name-format"
    ADDRESS_FORMAT = "address-format"
    POSTAL_CODE = "postal-code"
    TELEPHONE_FORMAT = "telephone-format"
    LOCALE_SPECIFIC_PUNCTUATION = "locale-specific-punctuation"
    NATIONAL_LANGUAGE_STANDARD = "national-language-standard"
    SHORTCUT_KEY = "shortcut-key"


class LocaleConventionLevel2(str, Enum):
    # """Level 2 locale convention error types"""

    # Under locale-specific-punctuation
    QUOTE_MARK_TYPE = "quote-mark-type"


# ============================================================================
# VERITY ERRORS (Level 0: verity)
# ============================================================================


class VerityLevel1(str, Enum):
    # """Level 1 verity error types"""

    CULTURE_SPECIFIC = "culture-specific"
    OFFENSIVE = "offensive"


class VerityLevel2(str, Enum):
    # """Level 2 verity error types"""

    # Under culture-specific
    END_USER_SUITABILITY = "end-user-suitability"
    LOCALE_SPECIFIC_CONTENT = "locale-specific-content"
    LANGUAGE_DEPENDENT_LOGIC = "language-dependent-logic"
    LEGAL_REQUIREMENTS = "legal-requirements"
    # Under offensive
    OBSCENITY = "obscenity"
    PROFANITY = "profanity"
    NON_INCLUSIVITY = "non-inclusivity"
    STEREOTYPE = "stereotype"
    INSULT = "insult"


# ============================================================================
# DESIGN ERRORS (Level 0: design)
# ============================================================================


class DesignLevel1(str, Enum):
    # """Level 1 design error types"""

    LOCAL_FORMATTING = "local-formatting"
    OVERALL_DESIGN = "overall-design"
    GRAPHICS_TABLES = "graphics-tables"
    MARKUP = "markup"
    TRUNCATION_TEXT_EXPANSION = "truncation-text-expansion"
    MISSING_TEXT = "missing-text"
    BROKEN_LINK = "broken-link"


class DesignLevel2(str, Enum):
    # """Level 2 design error types"""

    # Under local-formatting
    FONT = "font"
    KERNING = "kerning"
    # Under overall-design
    GLOBAL_FONT_CHOICE = "global-font-choice"
    COLOR = "color"
    MARGINS = "margins"
    PAGE_BREAKS = "page-breaks"
    FOOTNOTE_FORMAT = "footnote-format"
    HEADERS_AND_FOOTERS = "headers-and-footers"
    # Under graphics-tables
    GRAPHICS_TABLES_MISSING = "graphics-tables-missing"
    GRAPHICS_TABLES_POSITION = "graphics-tables-position"
    CALL_OUTS_CAPTIONS = "call-outs-captions"
    # Under markup
    QUESTIONABLE_MARKUP = "questionable-markup"
    MISSING_MARKUP = "missing-markup"
    ADDED_MARKUP = "added-markup"
    MISPLACED_MARKUP = "misplaced-markup"
    INCONSISTENT_MARKUP = "inconsistent-markup"
    # Under broken-link
    DOCUMENT_INTERNAL_LINK = "document-internal-link"
    DOCUMENT_EXTERNAL_LINK = "document-external-link"


class DesignLevel3(str, Enum):
    # """Level 3 design error types"""

    # Under font
    WRONG_FONT_SIZE = "wrong-font-size"
    BOLD_ITALIC = "bold-italic"
    SINGLE_DOUBLE_WIDTH = "single-double-width"


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

    # The MQM framework uses a 4-level hierarchy:
    # - Level 0: Main category (e.g., 'accuracy', 'fluency')
    # - Level 1: Primary subcategory (e.g., 'mistranslation', 'grammar')
    # - Level 2: Secondary subcategory (e.g., 'false-friend', 'word-form')
    # - Level 3: Tertiary subcategory (e.g., 'tense-mood-aspect')

    # Error classification
    category: ErrorCategory = Field()  # description="Top-level error category (Level 0)")

    # subcategory_level1: Optional[str] = Field(
    #     None, description="Primary subcategory (Level 1). Must be valid for the specified category."
    # )

    # subcategory_level2: Optional[str] = Field(
    #     None,
    #     description="Secondary subcategory (Level 2). Must be valid for the Level 1 subcategory.",
    # )

    # subcategory_level3: Optional[str] = Field(
    #     None,
    #     description="Tertiary subcategory (Level 3). Must be valid for the Level 2 subcategory.",
    # )

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

        # class CharacterSpan(BaseModel):
        #     character_start: Optional[int] = Field(
        #         ge=0,
        #         description="The start position of the token in text (character offset, 0-indexed)",
        #     )
        #     character_end: Optional[int] = Field(
        #         ge=0,
        #         description="The end position of the token in text (character offset, 0-indexed)",
        #     )

    in_source: TokenInfo
    in_target: TokenInfo

    # character_span: list[CharacterSpan] = Field(
    #     default_factory=list,
    #     description="List of start and end positions in text (character offsets, 0-indexed)",
    # )

    # source_end: Optional[int] = Field(
    #     None, ge=0, description="End position in source text (character offset, 0-indexed)"
    # )

    # target_start: int = Field(
    #     ge=0, description="Start position in target text (character offset, 0-indexed)"
    # )

    # target_end: int = Field(
    #     ge=0, description="End position in target text (character offset, 0-indexed)"
    # )

    # # Optional metadata
    # note: Optional[str] = Field(None, description="Annotator's explanation or note about the error")

    # corrected_text: Optional[str] = Field(None, description="Suggested correction for the error")


# ============================================================================
# DOCUMENT-LEVEL ANNOTATION MODEL
# ============================================================================


class MQMAnnotation(BaseModel):
    # """Complete MQM annotation for a translation segment or document."""

    # source_text: str = Field(description="Original source text")
    # target_text: str = Field(description="Translated target text")
    # reference_text: str | None = Field(None, description="Human reference text")
    errors: list[MQMError] = Field(
        default_factory=list, description="List of identified MQM errors"
    )

    model_config = {
        "json_schema_extra": {
            "additionalProperties": False,  # mandatory by OpenAI
        }
    }


def get_openai_schema(model_class: type[BaseModel]) -> dict:
    """
    Converts a Pydantic model (e.g., MQMAnnotation) into a fully OpenAI-compliant
    JSON Schema dictionary suitable for `response_format`:
      - Recursively adds additionalProperties: false
      - Ensures required contains all property keys
      - Moves descriptions inside definitions if needed
      - Cleans any $ref nodes for OpenAI validator
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
