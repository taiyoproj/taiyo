"""Solr highlighting models.

This module provides Pydantic models for Solr's highlighting functionality, including:
- Common highlighting parameters
- Unified Highlighter specific parameters
- Original Highlighter specific parameters
- FastVector Highlighter specific parameters
"""

from enum import Enum
from typing import List, Optional, Union

from pydantic import Field
from taiyo.params.configs.base import ParamsConfig


class HighlightMethod(str, Enum):
    """Available highlighting methods."""

    UNIFIED = "unified"
    ORIGINAL = "original"
    FAST_VECTOR = "fastVector"


class BreakIteratorType(str, Enum):
    """Break iterator types for text segmentation."""

    SEPARATOR = "SEPARATOR"
    SENTENCE = "SENTENCE"
    WORD = "WORD"
    CHARACTER = "CHARACTER"
    LINE = "LINE"
    WHOLE = "WHOLE"


class FragListBuilder(str, Enum):
    """Fragment list builder types."""

    SIMPLE = "simple"
    WEIGHTED = "weighted"
    SINGLE = "single"


class FragmentsBuilder(str, Enum):
    """Fragments builder types."""

    DEFAULT = "default"
    COLORED = "colored"


class Fragmenter(str, Enum):
    """Text snippet generator types."""

    GAP = "gap"
    REGEX = "regex"


class Formatter(str, Enum):
    """Highlight formatter types."""

    SIMPLE = "simple"


class HighlightEncoder(str, Enum):
    """Highlight text encoding options."""

    EMPTY = ""
    HTML = "html"


class HighlightParamsConfig(ParamsConfig):
    """Comprehensive Solr highlighting parameters."""

    method: Optional[HighlightMethod] = Field(
        default=None,
        alias="hl.method",
        description="The highlighting implementation to use (unified, original, fastVector).",
    )
    fields: Optional[Union[str, List[str]]] = Field(
        default=None,
        alias="hl.fl",
        description="Fields to highlight (comma/space-delimited list).",
    )
    query: Optional[str] = Field(
        default=None,
        alias="hl.q",
        description="Query to use for highlighting (defaults to q param).",
    )
    query_parser: Optional[str] = Field(
        default=None,
        alias="hl.qparser",
        description="Query parser for hl.q (defaults to defType param).",
    )
    require_field_match: Optional[bool] = Field(
        default=None,
        alias="hl.requireFieldMatch",
        description="Only highlight fields that match the query.",
    )
    query_field_pattern: Optional[str] = Field(
        default=None,
        alias="hl.queryFieldPattern",
        description="Fields that can match for highlighting.",
    )
    use_phrase_highlighter: Optional[bool] = Field(
        default=None,
        alias="hl.usePhraseHighlighter",
        description="Accurately highlight phrase queries.",
    )
    multiterm: Optional[bool] = Field(
        default=None,
        alias="hl.highlightMultiTerm",
        description="Enable highlighting for wildcard queries.",
    )
    snippets: Optional[int] = Field(
        default=None,
        alias="hl.snippets",
        description="Maximum number of highlighted snippets per field.",
    )
    fragsize: Optional[int] = Field(
        default=None,
        alias="hl.fragsize",
        description="Size of fragments in characters (0 for whole field).",
    )
    encoder: Optional[HighlightEncoder] = Field(
        default=None,
        alias="hl.encoder",
        description="Encoder for highlighted text (html for special chars).",
    )
    max_analyzed_chars: Optional[int] = Field(
        default=None,
        alias="hl.maxAnalyzedChars",
        description="Character limit for highlighting analysis.",
    )
    pre: Optional[str] = Field(
        default=None, alias="hl.tag.pre", description="Tag before highlighted term."
    )
    post: Optional[str] = Field(
        default=None, alias="hl.tag.post", description="Tag after highlighted term."
    )

    # Unified Highlighter specific
    offset_source: Optional[str] = Field(
        default=None,
        alias="hl.offsetSource",
        description="Source for offset information (ANALYSIS, POSTINGS, etc).",
    )
    frag_align_ratio: Optional[float] = Field(
        default=None,
        alias="hl.fragAlignRatio",
        description="Position of first match in passage (0.0-1.0).",
    )
    fragsize_is_minimum: Optional[bool] = Field(
        default=None,
        alias="hl.fragsizeIsMinimum",
        description="Treat fragsize as minimum (true) or target (false).",
    )
    tag_ellipsis: Optional[str] = Field(
        default=None,
        alias="hl.tag.ellipsis",
        description="Text to use between fragments.",
    )
    default_summary: Optional[bool] = Field(
        default=None,
        alias="hl.defaultSummary",
        description="Use leading text if no proper snippet.",
    )
    score_k1: Optional[float] = Field(
        default=None, alias="hl.score.k1", description="BM25 term frequency parameter."
    )
    score_b: Optional[float] = Field(
        default=None,
        alias="hl.score.b",
        description="BM25 length normalization parameter.",
    )
    score_pivot: Optional[int] = Field(
        default=None, alias="hl.score.pivot", description="BM25 average passage length."
    )
    bs_language: Optional[str] = Field(
        default=None, alias="hl.bs.language", description="Break iterator language."
    )
    bs_country: Optional[str] = Field(
        default=None, alias="hl.bs.country", description="Break iterator country."
    )
    bs_variant: Optional[str] = Field(
        default=None, alias="hl.bs.variant", description="Break iterator variant."
    )
    bs_type: Optional[BreakIteratorType] = Field(
        default=None, alias="hl.bs.type", description="Break iterator type."
    )
    bs_separator: Optional[str] = Field(
        default=None, alias="hl.bs.separator", description="Custom separator character."
    )
    weight_matches: Optional[bool] = Field(
        default=None,
        alias="hl.weightMatches",
        description="Use Weight Matches API for accuracy.",
    )

    # Original Highlighter specific
    merge_contiguous: Optional[bool] = Field(
        default=None,
        alias="hl.mergeContiguous",
        description="Merge contiguous fragments.",
    )
    max_multivalued_to_examine: Optional[int] = Field(
        default=None,
        alias="hl.maxMultiValuedToExamine",
        description="Max entries to examine in multivalued field.",
    )
    max_multivalued_to_match: Optional[int] = Field(
        default=None,
        alias="hl.maxMultiValuedToMatch",
        description="Max matches in multivalued field.",
    )
    alternate_field: Optional[str] = Field(
        default=None, alias="hl.alternateField", description="Backup field for summary."
    )
    max_alternate_field_length: Optional[int] = Field(
        default=None,
        alias="hl.maxAlternateFieldLength",
        description="Max length of alternate field.",
    )
    alternate: Optional[bool] = Field(
        default=None,
        alias="hl.highlightAlternate",
        description="Highlight alternate field.",
    )
    formatter: Optional[Formatter] = Field(
        default=None,
        alias="hl.formatter",
        description="Formatter for highlighted output.",
    )
    simple_pre: Optional[str] = Field(
        default=None,
        alias="hl.simple.pre",
        description="Text before term (simple formatter).",
    )
    simple_post: Optional[str] = Field(
        default=None,
        alias="hl.simple.post",
        description="Text after term (simple formatter).",
    )
    fragmenter: Optional[Fragmenter] = Field(
        default=None, alias="hl.fragmenter", description="Text snippet generator type."
    )
    regex_slop: Optional[float] = Field(
        default=None,
        alias="hl.regex.slop",
        description="Deviation factor for regex fragmenter.",
    )
    regex_pattern: Optional[str] = Field(
        default=None,
        alias="hl.regex.pattern",
        description="Pattern for regex fragmenter.",
    )
    regex_max_analyzed_chars: Optional[int] = Field(
        default=None,
        alias="hl.regex.maxAnalyzedChars",
        description="Char limit for regex fragmenter.",
    )
    preserve_multi: Optional[bool] = Field(
        default=None,
        alias="hl.preserveMulti",
        description="Preserve order in multivalued fields.",
    )
    payloads: Optional[bool] = Field(
        default=None,
        alias="hl.payloads",
        description="Include payloads in highlighting.",
    )

    # FastVector Highlighter specific
    frag_list_builder: Optional[FragListBuilder] = Field(
        default=None,
        alias="hl.fragListBuilder",
        description="Snippet fragmenting algorithm.",
    )
    fragments_builder: Optional[FragmentsBuilder] = Field(
        default=None,
        alias="hl.fragmentsBuilder",
        description="Fragment formatting implementation.",
    )
    boundary_scanner: Optional[str] = Field(
        default=None,
        alias="hl.boundaryScanner",
        description="Boundary scanner implementation.",
    )
    phrase_limit: Optional[int] = Field(
        default=None,
        alias="hl.phraseLimit",
        description="Max phrases to analyze for scoring.",
    )
    multivalue_separator: Optional[str] = Field(
        default=None,
        alias="hl.multiValuedSeparatorChar",
        description="Separator for multivalued fields.",
    )
