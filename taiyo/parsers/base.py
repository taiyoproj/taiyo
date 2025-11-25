from typing import Any, Dict, List, Literal, Optional, Self, Union
from pydantic import ConfigDict
from taiyo.params.configs.base import ParamsConfig
from taiyo.params.configs.facet import (
    FacetParamsConfig,
)
from taiyo.params.configs.group import GroupParamsConfig
from taiyo.params.configs.highlight import (
    HighlightParamsConfig,
)
from taiyo.params.configs.more_like_this import MoreLikeThisParamsConfig
from taiyo.params.mixins.common import CommonParamsMixin


class BaseQueryParser(CommonParamsMixin):
    model_config = ConfigDict(validate_by_alias=False, extra="forbid")

    configs: list[ParamsConfig] = []

    def serialize_configs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize ParamsConfig objects as top level params."""
        updates: Dict[str, Any] = {}
        for config in self.configs:
            updates[config.enable_key] = True
            updates.update(
                config.model_dump(exclude_none=True, exclude_unset=True, by_alias=True)
            )
        params.update(updates)
        return params

    def build(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Serialize the parser configuration to Solr-compatible query parameters using Pydantic's model_dump.
        """
        params = self.model_dump(
            by_alias=True,
            exclude_none=True,
            exclude=["configs"],  # type: ignore[arg-type]
            exclude_unset=True,
            *args,
            **kwargs,
        )
        return self.serialize_configs(params)

    def facet(
        self,
        *,
        queries: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        prefix: Optional[str] = None,
        contains: Optional[str] = None,
        contains_ignore_case: Optional[bool] = None,
        matches: Optional[str] = None,
        sort: Optional[Literal["count", "index"]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        mincount: Optional[int] = None,
        missing: Optional[bool] = None,
        method: Optional[Literal["enum", "fc", "fcs"]] = None,
        enum_cache_min_df: Optional[int] = None,
        exists: Optional[bool] = None,
        exclude_terms: Optional[str] = None,
        overrequest_count: Optional[int] = None,
        overrequest_ratio: Optional[float] = None,
        threads: Optional[int] = None,
        range_field: Optional[List[str]] = None,
        range_start: Optional[Dict[str, str]] = None,
        range_end: Optional[Dict[str, str]] = None,
        range_gap: Optional[Dict[str, str]] = None,
        range_hardend: Optional[bool] = None,
        range_include: Optional[
            List[Literal["lower", "upper", "edge", "outer", "all"]]
        ] = None,
        range_other: Optional[
            List[Literal["before", "after", "between", "none", "all"]]
        ] = None,
        range_method: Optional[Literal["filter", "dv"]] = None,
        pivot_fields: Optional[List[str]] = None,
        pivot_mincount: Optional[int] = None,
    ) -> Self:
        """Enable faceting to categorize and count search results.

        Faceting breaks down search results into categories with counts, enabling
        drill-down navigation and data analysis.

        Args:
            queries: Arbitrary queries to generate facet counts for specific terms/expressions.
            fields: Fields to be treated as facets. Common for categories, brands, tags.
            prefix: Limits facet terms to those starting with the given prefix.
            contains: Limits facet terms to those containing the given substring.
            contains_ignore_case: If True, ignores case when matching the 'contains' parameter.
            matches: Only returns facets matching this regular expression.
            sort: Ordering of facet field terms. Use 'count' (by frequency) or 'index' (alphabetically).
            limit: Number of facet counts to return. Set to -1 for all.
            offset: Offset into the facet list for paging.
            mincount: Minimum count for facets to be included in response. Common to set to 1 to hide empty facets.
            missing: If True, include count of results with no facet value.
            method: Algorithm to use for faceting. Use 'enum' (enumerate all terms, good for low-cardinality),
                'fc' (field cache, good for high-cardinality), or 'fcs' (per-segment, good for frequent updates).
            enum_cache_min_df: Minimum document frequency for filterCache usage with enum method.
            exists: Cap facet counts by 1 (only for non-trie fields).
            exclude_terms: Terms to remove from facet counts.
            overrequest_count: Extra facets to request from each shard for better accuracy in distributed environments.
            overrequest_ratio: Ratio for overrequesting facets from shards.
            threads: Number of threads for parallel facet loading. Useful for multiple facets on large datasets.
            range_field: Fields for range faceting (e.g., price ranges, date ranges).
            range_start: Lower bound of ranges per field. Dict mapping field name to start value.
            range_end: Upper bound of ranges per field. Dict mapping field name to end value.
            range_gap: Size of each range span per field. E.g., {'price': '100'} for $100 increments.
            range_hardend: If True, uses exact range_end as upper bound even if it doesn't align with gap.
            range_include: Range bounds to include in faceting. List of: 'lower' (include lower bound),
                'upper' (include upper bound), 'edge' (first/last include edges), 'outer' (before/after inclusive), 'all'.
            range_other: Additional range counts to compute. List of: 'before' (below first range),
                'after' (above last range), 'between' (within bounds), 'none', or 'all'.
            range_method: Method to use for range faceting. Use 'filter' or 'dv' (for docValues).
            pivot_fields: Fields to use for pivot (hierarchical) faceting. E.g., ['category,brand'].
            pivot_mincount: Minimum count for pivot facet inclusion.

        Returns:
            A new parser instance with facet configuration applied.

        Examples:
            Basic field faceting:
            >>> parser.facet(fields=["genre", "director"], mincount=1, limit=10)

            Range faceting for prices:
            >>> parser.facet(
            ...     range_field=["price"],
            ...     range_start={"price": "0"},
            ...     range_end={"price": "1000"},
            ...     range_gap={"price": "100"}
            ... )

            Filtered facets:
            >>> parser.facet(fields=["color"], prefix="bl", mincount=5)
        """
        self.configs.append(
            FacetParamsConfig(
                queries=queries,
                fields=fields,
                prefix=prefix,
                contains=contains,
                contains_ignore_case=contains_ignore_case,
                matches=matches,
                sort=sort,
                limit=limit,
                offset=offset,
                mincount=mincount,
                missing=missing,
                method=method,
                enum_cache_min_df=enum_cache_min_df,
                exists=exists,
                exclude_terms=exclude_terms,
                overrequest_count=overrequest_count,
                overrequest_ratio=overrequest_ratio,
                threads=threads,
                range_field=range_field,
                range_start=range_start,
                range_end=range_end,
                range_gap=range_gap,
                range_hardend=range_hardend,
                range_include=range_include,
                range_other=range_other,
                range_method=range_method,
                pivot_fields=pivot_fields,
                pivot_mincount=pivot_mincount,
            )
        )
        return self

    def group(
        self,
        *,
        by: Optional[Union[str, List[str]]] = None,
        func: Optional[str] = None,
        query: Optional[Union[str, List[str]]] = None,
        limit: int = 1,
        offset: Optional[int] = None,
        sort: Optional[str] = None,
        format: str = "grouped",
        main: Optional[bool] = None,
        ngroups: bool = False,
        truncate: bool = False,
        facet: bool = False,
        cache_percent: int = 0,
    ) -> Self:
        """Enable result grouping to collapse results by common field values.

        Result grouping (also known as field collapsing) combines documents that share
        a common field value. Useful for showing one result per author, category, or domain.

        Args:
            by: Field(s) to group results by. Shows one representative doc per unique field value.
                Must be single-valued and indexed. Can specify multiple fields for separate groupings.
            func: Group by the result of a function query (e.g., 'floor(price)'). Not supported in SolrCloud/distributed searches.
            query: Create custom groups using arbitrary queries. Each query defines one group.
                Example: ['price:[0 TO 50]', 'price:[50 TO 100]'] creates price range groups.
            limit: Number of documents to return per group. Default: 1 (only top doc per group).
                Set higher to see more examples from each group.
            offset: Skip the first N documents within each group. Useful for pagination within groups.
            sort: How to sort documents within each group (e.g., 'date desc' for newest first).
                If not specified, uses the main sort parameter.
            format: Response structure format. 'grouped' (nested, default) or 'simple' (flat list).
            main: If True, returns first field grouping as main result list, flattening the response.
            ngroups: If True, include total number of unique groups in response.
                Useful for pagination. Requires co-location in SolrCloud.
            truncate: If True, base facet counts on one doc per group only.
            facet: If True, enable grouped faceting. Can be expensive on large result sets.
                Requires co-location in SolrCloud.
            cache_percent: Enable result grouping cache (0-100). Set to 0 to disable (default).
                Try 50-100 for complex queries to improve performance.

        Returns:
            A new parser instance with group configuration applied.

        Examples:
            Group by author:
            >>> parser.group(by="author", limit=3, sort="date desc", ngroups=True)

            Group by price range:
            >>> parser.group(
            ...     query=["price:[0 TO 50]", "price:[50 TO 100]", "price:[100 TO *]"],
            ...     limit=5
            ... )

            Multiple field groupings:
            >>> parser.group(by=["author", "category"], limit=2)
        """
        config = GroupParamsConfig(
            by=by,
            func=func,
            query=query,
            limit=limit,
            offset=offset,
            sort=sort,
            format=format,
            main=main,
            ngroups=ngroups,
            truncate=truncate,
            facet=facet,
            cache_percent=cache_percent,
        )
        self.configs.append(config)
        return self

    def highlight(
        self,
        *,
        # Common parameters
        method: Optional[Literal["unified", "original", "fastVector"]] = None,
        fields: Optional[Union[str, List[str]]] = None,
        query: Optional[str] = None,
        query_parser: Optional[str] = None,
        require_field_match: Optional[bool] = None,
        query_field_pattern: Optional[str] = None,
        use_phrase_highlighter: Optional[bool] = None,
        multiterm: Optional[bool] = None,
        snippets_per_field: Optional[int] = None,
        fragment_size: Optional[int] = None,
        encoder: Optional[Literal["", "html"]] = None,
        max_analyzed_chars: Optional[int] = None,
        tag_before: Optional[str] = None,
        tag_after: Optional[str] = None,
        # Unified Highlighter specific
        offset_source: Optional[str] = None,
        frag_align_ratio: Optional[float] = None,
        fragsize_is_minimum: Optional[bool] = None,
        tag_ellipsis: Optional[str] = None,
        default_summary: Optional[bool] = None,
        score_k1: Optional[float] = None,
        score_b: Optional[float] = None,
        score_pivot: Optional[int] = None,
        bs_language: Optional[str] = None,
        bs_country: Optional[str] = None,
        bs_variant: Optional[str] = None,
        bs_type: Optional[
            Literal["SEPARATOR", "SENTENCE", "WORD", "CHARACTER", "LINE", "WHOLE"]
        ] = None,
        bs_separator: Optional[str] = None,
        weight_matches: Optional[bool] = None,
        # Original Highlighter specific
        merge_contiguous: Optional[bool] = None,
        max_multivalued_to_examine: Optional[int] = None,
        max_multivalued_to_match: Optional[int] = None,
        alternate_field: Optional[str] = None,
        max_alternate_field_length: Optional[int] = None,
        alternate: Optional[bool] = None,
        formatter: Optional[Literal["simple"]] = None,
        simple_pre: Optional[str] = None,
        simple_post: Optional[str] = None,
        fragmenter: Optional[Literal["gap", "regex"]] = None,
        regex_slop: Optional[float] = None,
        regex_pattern: Optional[str] = None,
        regex_max_analyzed_chars: Optional[int] = None,
        preserve_multi: Optional[bool] = None,
        payloads: Optional[bool] = None,
        # FastVector Highlighter specific
        frag_list_builder: Optional[Literal["simple", "weighted", "single"]] = None,
        fragments_builder: Optional[Literal["default", "colored"]] = None,
        boundary_scanner: Optional[str] = None,
        phrase_limit: Optional[int] = None,
        multivalue_separator: Optional[str] = None,
    ) -> Self:
        """Enable highlighting to show snippets with query terms emphasized.

        Highlighting shows snippets of text from documents with query terms emphasized
        (usually wrapped in <em> tags). Common for search result snippets and previews.

        Args:
            method: Highlighting implementation to use. Use 'unified' (most accurate, recommended),
                'original' (legacy, widely compatible), or 'fastVector' (fast for large docs, requires term vectors).
            fields: Fields to generate highlighted snippets for. Must be stored fields.
                Example: ['title', 'content']. Use '*' for all fields (not recommended).
            query: Custom query to use for highlighting (overrides main query).
            query_parser: Query parser for the highlight query (e.g., 'edismax', 'lucene').
            require_field_match: If True, only highlight terms in the field they matched.
                Set to False to highlight query terms in all requested fields.
            query_field_pattern: Regular expression pattern for fields to consider for highlighting.
            use_phrase_highlighter: If True, highlights complete phrases accurately. Default: True.
            multiterm: Enable highlighting for wildcard, fuzzy, and range queries. Default: True.
            snippets_per_field: Maximum number of snippets to return per field. Default: 1.
                Set higher to show more context passages.
            fragment_size: Size of highlighted snippets in characters. Default: 100.
                Set to 0 to highlight entire field (not recommended for large fields).
            encoder: Text encoder for snippets. Use '' (empty string, default) or 'html' to escape HTML and prevent XSS.
            max_analyzed_chars: Maximum characters to analyze per field. Default: 51200 (50KB).
                For large documents, limits analysis to improve performance.
            tag_before: Text/tag to insert before each highlighted term. Default: '<em>'.
                Example: '<mark class="highlight">'.
            tag_after: Text/tag to insert after each highlighted term. Default: '</em>'.

            # Unified Highlighter specific (most accurate, recommended):
            offset_source: How offsets are obtained. Options: 'ANALYSIS', 'POSTINGS',
                'POSTINGS_WITH_TERM_VECTORS', 'TERM_VECTORS'. Usually auto-detected.
            frag_align_ratio: Where to position first match in snippet (0.0-1.0).
                Default: 0.33 (left third, shows context before match).
            fragsize_is_minimum: If True, treat fragment_size as minimum. Default: True.
            tag_ellipsis: Text between multiple snippets (e.g., '...' or ' [...] ').
            default_summary: If True, return leading text when no matches found.
            score_k1: BM25 term frequency normalization. Default: 1.2.
            score_b: BM25 length normalization. Default: 0.75.
            score_pivot: BM25 average passage length in characters. Default: 87.
            bs_language: BreakIterator language for text segmentation (e.g., 'en', 'ja').
            bs_country: BreakIterator country code (e.g., 'US', 'GB').
            bs_variant: BreakIterator variant for specialized locale rules.
            bs_type: How to segment text. Use 'SENTENCE' (default, recommended),
                'WORD', 'CHARACTER', 'LINE', 'SEPARATOR', or 'WHOLE'.
            bs_separator: Custom separator character when bs_type=SEPARATOR.
            weight_matches: Use Lucene's Weight Matches API for most accurate highlighting.

            # Original Highlighter specific (legacy):
            merge_contiguous: Merge adjacent fragments.
            max_multivalued_to_examine: Max entries to examine in multivalued field.
            max_multivalued_to_match: Max matches in multivalued field.
            alternate_field: Backup field for summary when no highlights found.
            max_alternate_field_length: Max length of alternate field.
            alternate: Highlight alternate field.
            formatter: Formatter for highlighted output. Use 'simple'.
            simple_pre: Text before term (simple formatter).
            simple_post: Text after term (simple formatter).
            fragmenter: Text snippet generator type. Use 'gap' or 'regex'.
            regex_slop: Deviation factor for regex fragmenter.
            regex_pattern: Pattern for regex fragmenter.
            regex_max_analyzed_chars: Char limit for regex fragmenter.
            preserve_multi: Preserve order in multivalued fields.
            payloads: Include payloads in highlighting.

            # FastVector Highlighter specific (requires term vectors):
            frag_list_builder: Snippet fragmenting algorithm. Use 'simple', 'weighted', or 'single'.
            fragments_builder: Fragment formatting implementation. Use 'default' or 'colored'.
            boundary_scanner: Boundary scanner implementation.
            phrase_limit: Max phrases to analyze for scoring.
            multivalue_separator: Separator for multivalued fields.

        Returns:
            A new parser instance with highlight configuration applied.

        Examples:
            Basic highlighting:
            >>> parser.highlight(fields=["title", "content"], snippets_per_field=3, fragment_size=150)

            Custom HTML tags:
            >>> parser.highlight(
            ...     fields=["title"],
            ...     tag_before='<mark class="highlight">',
            ...     tag_after='</mark>',
            ...     encoder="html"
            ... )

            Unified highlighter with sentence breaks:
            >>> parser.highlight(
            ...     fields=["content"],
            ...     method="unified",
            ...     bs_type="SENTENCE",
            ...     fragment_size=200
            ... )
        """
        config = HighlightParamsConfig(
            method=method,
            fields=fields,
            query=query,
            query_parser=query_parser,
            require_field_match=require_field_match,
            query_field_pattern=query_field_pattern,
            use_phrase_highlighter=use_phrase_highlighter,
            multiterm=multiterm,
            snippets_per_field=snippets_per_field,
            fragment_size=fragment_size,
            encoder=encoder,
            max_analyzed_chars=max_analyzed_chars,
            tag_before=tag_before,
            tag_after=tag_after,
            offset_source=offset_source,
            frag_align_ratio=frag_align_ratio,
            fragsize_is_minimum=fragsize_is_minimum,
            tag_ellipsis=tag_ellipsis,
            default_summary=default_summary,
            score_k1=score_k1,
            score_b=score_b,
            score_pivot=score_pivot,
            bs_language=bs_language,
            bs_country=bs_country,
            bs_variant=bs_variant,
            bs_type=bs_type,
            bs_separator=bs_separator,
            weight_matches=weight_matches,
            merge_contiguous=merge_contiguous,
            max_multivalued_to_examine=max_multivalued_to_examine,
            max_multivalued_to_match=max_multivalued_to_match,
            alternate_field=alternate_field,
            max_alternate_field_length=max_alternate_field_length,
            alternate=alternate,
            formatter=formatter,
            simple_pre=simple_pre,
            simple_post=simple_post,
            fragmenter=fragmenter,
            regex_slop=regex_slop,
            regex_pattern=regex_pattern,
            regex_max_analyzed_chars=regex_max_analyzed_chars,
            preserve_multi=preserve_multi,
            payloads=payloads,
            frag_list_builder=frag_list_builder,
            fragments_builder=fragments_builder,
            boundary_scanner=boundary_scanner,
            phrase_limit=phrase_limit,
            multivalue_separator=multivalue_separator,
        )
        self.configs.append(config)
        return self

    def more_like_this(
        self,
        *,
        fields: Optional[Union[str, List[str]]] = None,
        min_term_freq: Optional[int] = None,
        min_doc_freq: Optional[int] = None,
        max_doc_freq: Optional[int] = None,
        max_doc_freq_pct: Optional[int] = None,
        min_word_len: Optional[int] = None,
        max_word_len: Optional[int] = None,
        max_query_terms: Optional[int] = None,
        max_num_tokens_parsed: Optional[int] = None,
        boost: Optional[bool] = None,
        query_fields: Optional[str] = None,
        interesting_terms: Optional[str] = None,
        match_include: Optional[bool] = None,
        match_offset: Optional[int] = None,
    ) -> Self:
        """Enable MoreLikeThis to find documents similar to a given document.

        MoreLikeThis finds documents similar to a given document by analyzing the terms
        that make it unique. Common for "related articles", recommendations, and content discovery.

        Args:
            fields: Fields to analyze for similarity. Use fields with meaningful content (title, description, body).
                Can be a single field or list of fields. For best performance, enable term vectors on these fields.
            min_term_freq: Minimum times a term must appear in the source document to be considered. Default: 2.
                Lower values include more terms but may add noise.
            min_doc_freq: Minimum number of documents a term must appear in across the index. Default: 5.
                Filters out very rare terms that aren't useful for finding similar documents.
            max_doc_freq: Maximum number of documents a term can appear in. Filters out very common terms
                (like 'the', 'and'). Use this OR max_doc_freq_pct, not both.
            max_doc_freq_pct: Maximum document frequency as percentage (0-100).
                Example: 75 means ignore terms appearing in more than 75% of documents.
                Use instead of max_doc_freq for relative filtering.
            min_word_len: Minimum word length in characters. Words shorter than this are ignored.
                Example: 4 to skip 'the', 'and', 'or'.
            max_word_len: Maximum word length in characters. Words longer than this are ignored.
                Useful to filter out long tokens or URLs.
            max_query_terms: Maximum number of interesting terms to use in the MLT query. Default: 25.
                Higher values = more comprehensive but slower. Start with default and adjust as needed.
            max_num_tokens_parsed: Maximum tokens to analyze per field (for fields without term vectors). Default: 5000.
                Set lower for better performance on large documents.
            boost: If True, boost the query by each term's relevance/importance. Default: False.
                Enable for better relevance ranking of similar documents.
            query_fields: Query fields with optional boosts, like 'title^2.0 content^1.0'.
                Fields must also be in 'fields' parameter. Use to emphasize certain fields in similarity matching.
            interesting_terms: Controls what info about matched terms is returned.
                Options: 'none' (default), 'list' (term names), 'details' (terms with boost values).
                Use 'details' for debugging to see which terms were selected.
            match_include: If True, includes the source document in results (useful to compare).
                Default varies: true for MLT handler, depends on configuration for component.
            match_offset: When using with a query, specifies which result doc to use for similarity.
                0 = first result, 1 = second, etc. Default: 0.

        Returns:
            A new parser instance with more_like_this configuration applied.

        Examples:
            Basic similarity search:
            >>> parser.more_like_this(
            ...     fields=["title", "content"],
            ...     min_term_freq=2,
            ...     min_doc_freq=5,
            ...     max_query_terms=25
            ... )

            Advanced with filtering:
            >>> parser.more_like_this(
            ...     fields=["content"],
            ...     min_term_freq=1,
            ...     min_doc_freq=3,
            ...     min_word_len=4,
            ...     max_doc_freq_pct=80,
            ...     interesting_terms="details"
            ... )

            Boosted fields:
            >>> parser.more_like_this(
            ...     fields=["title", "content"],
            ...     query_fields="title^2.0 content^1.0",
            ...     boost=True
            ... )
        """
        config = MoreLikeThisParamsConfig(
            fields=fields,
            min_term_freq=min_term_freq,
            min_doc_freq=min_doc_freq,
            max_doc_freq=max_doc_freq,
            max_doc_freq_pct=max_doc_freq_pct,
            min_word_len=min_word_len,
            max_word_len=max_word_len,
            max_query_terms=max_query_terms,
            max_num_tokens_parsed=max_num_tokens_parsed,
            boost=boost,
            query_fields=query_fields,
            interesting_terms=interesting_terms,
            match_include=match_include,
            match_offset=match_offset,
        )
        self.configs.append(config)
        return self
