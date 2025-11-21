from pydantic import Field

from taiyo.params import (
    FacetParamsConfig,
    HighlightParamsConfig,
    GroupParamsConfig,
    MoreLikeThisParamsConfig,
)
from taiyo.parsers.base import BaseQueryParser
from typing import Optional, Any
from typing_extensions import Self


class SparseQueryParser(BaseQueryParser):
    group: Optional[GroupParamsConfig] = Field(
        default=None,
        description="Configuration object for Grouping feature.",
    )
    facet: Optional[FacetParamsConfig] = Field(
        default=None,
        description="Configuration object for Faceting feature.",
    )
    highlight: Optional[HighlightParamsConfig] = Field(
        default=None,
        description="Configuration object for Highlighting feature.",
    )
    more_like_this: Optional[MoreLikeThisParamsConfig] = Field(
        default=None,
        description="Configuration object for MoreLikeThis feature.",
    )

    def facet(self, config: Optional[FacetParamsConfig] = None, **kwargs: Any) -> Self:
        """Set faceting configuration using either a config object or kwargs.

        Args:
            config: A FacetParamsConfig object (if provided, kwargs are ignored)
            **kwargs: Individual faceting parameters (queries, fields, prefix, etc.)

        Returns:
            A new parser instance with the facet configuration applied.

        Raises:
            ValidationError: If kwargs contain invalid parameter names or types

        Example:
            >>> parser.set_facet(fields=["genre", "director"], mincount=1, limit=10)
            >>> parser.set_facet(FacetParamsConfig(fields=["genre"], mincount=1))
        """
        if config is None:
            config = FacetParamsConfig(**kwargs)  # Pydantic validates kwargs
        return self.copy(facet=config)

    def group(self, config: Optional[GroupParamsConfig] = None, **kwargs: Any) -> Self:
        """Set grouping configuration using either a config object or kwargs.

        Args:
            config: A GroupParamsConfig object (if provided, kwargs are ignored)
            **kwargs: Individual grouping parameters (field, limit, offset, etc.)

        Returns:
            A new parser instance with the group configuration applied.

        Raises:
            ValidationError: If kwargs contain invalid parameter names or types

        Example:
            >>> parser.set_group(field="director", limit=2, ngroups=True)
            >>> parser.set_group(GroupParamsConfig(field="director", limit=2))
        """
        if config is None:
            config = GroupParamsConfig(**kwargs)  # Pydantic validates kwargs
        return self.copy(group=config)

    def highlight(
        self, config: Optional[HighlightParamsConfig] = None, **kwargs: Any
    ) -> Self:
        """Set highlighting configuration using either a config object or kwargs.

        Args:
            config: A HighlightParamsConfig object (if provided, kwargs are ignored)
            **kwargs: Individual highlighting parameters (fields, method, snippets, etc.)

        Returns:
            A new parser instance with the highlight configuration applied.

        Raises:
            ValidationError: If kwargs contain invalid parameter names or types

        Example:
            >>> parser.set_highlight(fields=["title"], method="unified", snippets=3)
            >>> parser.set_highlight(HighlightParamsConfig(fields=["title"]))
        """
        if config is None:
            config = HighlightParamsConfig(**kwargs)  # Pydantic validates kwargs
        return self.copy(highlight=config)

    def more_like_this(
        self, config: Optional[MoreLikeThisParamsConfig] = None, **kwargs: Any
    ) -> Self:
        """Set more-like-this configuration using either a config object or kwargs.

        Args:
            config: A MoreLikeThisParamsConfig object (if provided, kwargs are ignored)
            **kwargs: Individual MLT parameters (fields, min_term_freq, min_doc_freq, etc.)

        Returns:
            A new parser instance with the more_like_this configuration applied.

        Raises:
            ValidationError: If kwargs contain invalid parameter names or types

        Example:
            >>> parser.set_more_like_this(fields=["content"], min_term_freq=2)
            >>> parser.set_more_like_this(MoreLikeThisParamsConfig(fields=["content"]))
        """
        if config is None:
            config = MoreLikeThisParamsConfig(**kwargs)
        return self.copy(more_like_this=config)
