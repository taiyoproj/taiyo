"""Solr Highlighting Configuration.

This module provides Pydantic models for Solr's highlighting functionality, including:
- Common highlighting parameters
- Unified Highlighter (recommended, most accurate)
- Original Highlighter (legacy, widely compatible)
- FastVector Highlighter (requires term vectors, fast for large texts)

Official Documentation:
    https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html
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
    """How to segment text into passages for highlighting.

    Controls where snippets begin and end:
    - SENTENCE: Break on sentence boundaries (recommended for natural-looking snippets)
    - WORD: Break on word boundaries
    - SEPARATOR: Break on a custom character
    - CHARACTER: Break anywhere
    - LINE: Break on line breaks
    - WHOLE: Treat entire field as one passage

    Reference: https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html
    """

    SEPARATOR = "SEPARATOR"  # Break on custom separator (define with bs_separator)
    SENTENCE = "SENTENCE"  # Break on sentence boundaries (default)
    WORD = "WORD"  # Break on word boundaries
    CHARACTER = "CHARACTER"  # Break on any character
    LINE = "LINE"  # Break on line breaks (\n)
    WHOLE = "WHOLE"  # Use entire field content


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
    """Configuration for Solr Highlighting.

    Highlighting allows you to show snippets of text from documents with query terms
    emphasized (usually wrapped in <em> tags). Common use cases include:
    - Search result snippets showing matched terms in context
    - Preview text with keywords highlighted
    - Showing relevant passages from long documents

    Official Documentation:
        https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html

    Example:
        ```python
        # Basic highlighting setup
        highlight_config = HighlightParamsConfig(
            method='unified',  # Use the recommended Unified Highlighter
            fields=['title', 'content'],  # Fields to highlight
            snippets_per_field=3,  # Show up to 3 snippets per field
            fragment_size=150,  # ~150 character snippets
            tag_before='<mark>',  # HTML tag before matched term
            tag_after='</mark>'  # HTML tag after matched term
        )
        ```

    Note:
        - Choose highlighter method based on your needs:
          - 'unified': Most accurate, recommended (default)
          - 'original': Works with any field configuration
          - 'fastVector': Fast for large documents (requires termVectors=true)
    """

    enable_key: str = "hl"

    method: Optional[HighlightMethod] = Field(
        default=None,
        alias="hl.method",
        description="""Highlighting implementation to use.
        
        - 'unified': Most accurate, recommended for most use cases (default)
        - 'original': Legacy highlighter, works with any field type
        - 'fastVector': Fastest for large documents (requires termVectors=true)
        
        Default: 'unified' (Solr 6.4+)""",
    )
    fields: Optional[Union[str, List[str]]] = Field(
        default=None,
        alias="hl.fl",
        description="""Fields to generate highlighted snippets for.
        
        Example: ['title', 'content'] highlights both title and content fields.
        Use '*' to highlight all fields (not recommended for performance).
        
        Fields must be stored (stored=true) to be highlighted.""",
    )
    query: Optional[str] = Field(
        default=None,
        alias="hl.q",
        description="""Query to use for highlighting (overrides main query).
        
        Example: Highlight 'python programming' even if main query is broader.
        
        Default: Uses the main query (q parameter).""",
    )
    query_parser: Optional[str] = Field(
        default=None,
        alias="hl.qparser",
        description="""Query parser to use for highlight_query.
        
        Example: 'edismax', 'lucene', 'dismax'
        
        Default: Uses the main query parser (defType parameter).""",
    )
    require_field_match: Optional[bool] = Field(
        default=None,
        alias="hl.requireFieldMatch",
        description="""If true, only highlight terms in the field they matched.
        
        Example: With query 'title:python', only highlights 'python' in title field,
        not in other fields.
        
        Set to false to highlight query terms in all requested fields.
        Default: false""",
    )
    query_field_pattern: Optional[str] = Field(
        default=None,
        alias="hl.queryFieldPattern",
        description="""Regular expression pattern for fields to consider for highlighting.
        
        Example: '.*_text$' matches all fields ending with '_text'.
        
        Works with require_field_match to control highlighting scope.""",
    )
    use_phrase_highlighter: Optional[bool] = Field(
        default=None,
        alias="hl.usePhraseHighlighter",
        description="""If true, highlights complete phrases accurately.
        
        Example: Query 'machine learning' only highlights when both words appear
        together, not 'machine' or 'learning' separately.
        
        Default: true (recommended)""",
    )
    multiterm: Optional[bool] = Field(
        default=None,
        alias="hl.highlightMultiTerm",
        description="""Enable highlighting for wildcard, fuzzy, and range queries.
        
        Example: Query 'progr*' highlights 'programming', 'program', 'progress'.
        
        Can impact performance for complex multi-term queries.
        Default: true""",
    )
    snippets_per_field: Optional[int] = Field(
        default=None,
        alias="hl.snippets",
        description="""Maximum number of snippets to return per field.
        
        Example: Set to 3 to show up to 3 relevant passages from each field.
        Higher values help users see more context but increase response size.
        
        Default: 1""",
    )
    fragment_size: Optional[int] = Field(
        default=None,
        alias="hl.fragsize",
        description="""Size of highlighted snippets in characters.
        
        Example: 150 creates ~150 character snippets around matched terms.
        Set to 0 to highlight the entire field content (not recommended for large fields).
        
        Default: 100""",
    )
    encoder: Optional[HighlightEncoder] = Field(
        default=None,
        alias="hl.encoder",
        description="""Text encoder for highlighted snippets.
        
        - 'html': Escape HTML special characters (<, >, &, etc.) - recommended for web display
        - '' (empty): No encoding
        
        Use 'html' to prevent XSS vulnerabilities when displaying highlights.""",
    )
    max_analyzed_chars: Optional[int] = Field(
        default=None,
        alias="hl.maxAnalyzedChars",
        description="""Maximum characters to analyze for highlighting per field.
        
        For large documents, only analyzes the first N characters to improve performance.
        Matches beyond this limit won't be highlighted.
        
        Example: 51200 (50KB) is a good balance for most use cases.
        Default: 51200""",
    )
    tag_before: Optional[str] = Field(
        default=None,
        alias="hl.tag.pre",
        description="""Text/tag to insert before each highlighted term.
        
        Example: '<mark class="highlight">' or '<strong>' or '**'
        
        Default: '<em>'""",
    )
    tag_after: Optional[str] = Field(
        default=None,
        alias="hl.tag.post",
        description="""Text/tag to insert after each highlighted term.
        
        Example: '</mark>' or '</strong>' or '**'
        
        Default: '</em>'""",
    )

    # Unified Highlighter specific parameters (most accurate, recommended)
    # Reference: https://solr.apache.org/guide/solr/latest/query-guide/highlighting.html#unified-highlighter

    offset_source: Optional[str] = Field(
        default=None,
        alias="hl.offsetSource",
        description="""How offsets are obtained (Unified Highlighter only).
        
        Options:
        - ANALYSIS: Analyze text on-the-fly (slower, smaller index)
        - POSTINGS: Use postings (fast, requires storeOffsetsWithPositions=true)
        - POSTINGS_WITH_TERM_VECTORS: Use postings with term vectors
        - TERM_VECTORS: Use term vectors (requires termVectors=true)
        
        Usually auto-detected. Set explicitly during index format migrations.""",
    )
    frag_align_ratio: Optional[float] = Field(
        default=None,
        alias="hl.fragAlignRatio",
        description="""Where to position the first match in the snippet (0.0-1.0).
        
        - 0.0: Align match to start (left)
        - 0.33: Align to left third (default, shows context before match)
        - 0.5: Center the match
        - 1.0: Align match to end (right)
        
        Lower values improve performance when highlighting lots of text.
        Default: 0.33""",
    )
    fragsize_is_minimum: Optional[bool] = Field(
        default=None,
        alias="hl.fragsizeIsMinimum",
        description="""How to interpret fragment_size.
        
        - true: Treat as minimum size (fragments at least this big)
        - false: Treat as target size (average fragment size)
        
        False is slower but gives more consistent snippet lengths.
        Default: true""",
    )
    tag_ellipsis: Optional[str] = Field(
        default=None,
        alias="hl.tag.ellipsis",
        description="""Text to display between multiple snippets.
        
        Example: '...' or ' [...] '
        
        By default, each snippet is returned separately.""",
    )
    default_summary: Optional[bool] = Field(
        default=None,
        alias="hl.defaultSummary",
        description="""If true, return leading text when no matches found.
        
        Useful to always show a preview even if search terms don't match.
        Default: false""",
    )
    score_k1: Optional[float] = Field(
        default=None,
        alias="hl.score.k1",
        description="""BM25 term frequency normalization parameter.
        
        Controls how term frequency affects passage scoring.
        Set to 0 to ignore term frequency (only count distinct terms).
        Default: 1.2""",
    )
    score_b: Optional[float] = Field(
        default=None,
        alias="hl.score.b",
        description="""BM25 length normalization parameter.
        
        Controls how passage length affects scoring.
        Set to 0 to ignore passage length completely.
        Default: 0.75""",
    )
    score_pivot: Optional[int] = Field(
        default=None,
        alias="hl.score.pivot",
        description="""BM25 average passage length in characters.
        
        Passages longer than this are penalized, shorter are boosted.
        Default: 87""",
    )
    bs_language: Optional[str] = Field(
        default=None,
        alias="hl.bs.language",
        description="""BreakIterator language for text segmentation.
        
        Example: 'en' for English, 'ja' for Japanese, 'de' for German.
        Used to intelligently break text at sentence/word boundaries.""",
    )
    bs_country: Optional[str] = Field(
        default=None,
        alias="hl.bs.country",
        description="""BreakIterator country code.
        
        Example: 'US', 'GB', 'JP'
        Used with bs_language for locale-specific text breaking.""",
    )
    bs_variant: Optional[str] = Field(
        default=None,
        alias="hl.bs.variant",
        description="BreakIterator variant for specialized locale rules.",
    )
    bs_type: Optional[BreakIteratorType] = Field(
        default=None,
        alias="hl.bs.type",
        description="""How to segment text into passages.
        
        - SENTENCE: Break on sentence boundaries (default, recommended)
        - WORD: Break on word boundaries
        - CHARACTER: Break on any character
        - LINE: Break on line breaks
        - SEPARATOR: Break on custom separator (use bs_separator)
        - WHOLE: Use entire field as one passage
        
        Default: SENTENCE""",
    )
    bs_separator: Optional[str] = Field(
        default=None,
        alias="hl.bs.separator",
        description="""Custom separator character when bs_type=SEPARATOR.
        
        Example: '\n' to break on newlines, '|' for pipe-separated text.""",
    )
    weight_matches: Optional[bool] = Field(
        default=None,
        alias="hl.weightMatches",
        description="""Use Lucene's Weight Matches API for most accurate highlighting.
        
        - Reflects query structure exactly
        - Highlights phrases as a whole
        - Currently slower for many fields
        
        Automatically disabled if usePhraseHighlighter=false or highlightMultiTerm=false.
        Default: varies""",
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
