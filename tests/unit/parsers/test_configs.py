"""Tests for different ways to configure parser results with ParamsConfig objects."""

from taiyo.params import (
    FacetParamsConfig,
    GroupParamsConfig,
    HighlightParamsConfig,
    MoreLikeThisParamsConfig,
)
from taiyo.parsers import StandardParser, DisMaxQueryParser


class TestConfigViaConstructor:
    """Test passing configs as a list during parser construction."""

    def test_single_facet_config_in_constructor(self):
        """Test parser with a single facet config passed in constructor."""
        facet_config = FacetParamsConfig(
            fields=["category", "brand"],
            mincount=5,
            limit=10,
            sort="count",
        )
        parser = StandardParser(
            query="laptop",
            configs=[facet_config],
        )
        params = parser.build()

        assert params["q"] == "laptop"
        assert params["facet"] is True
        assert params["facet.field"] == ["category", "brand"]
        assert params["facet.mincount"] == 5
        assert params["facet.limit"] == 10
        assert params["facet.sort"] == "count"

    def test_single_group_config_in_constructor(self):
        """Test parser with a single group config passed in constructor."""
        group_config = GroupParamsConfig(
            by="author",
            limit=3,
            sort="date desc",
            ngroups=True,
        )
        parser = StandardParser(
            query="python programming",
            configs=[group_config],
        )
        params = parser.build()

        assert params["q"] == "python programming"
        assert params["group"] is True
        assert params["group.field"] == "author"
        assert params["group.limit"] == 3
        assert params["group.sort"] == "date desc"
        assert params["group.ngroups"] is True

    def test_single_highlight_config_in_constructor(self):
        """Test parser with a single highlight config passed in constructor."""
        highlight_config = HighlightParamsConfig(
            fields=["title", "content"],
            snippets_per_field=3,
            fragment_size=150,
            simple_pre="<mark>",
            simple_post="</mark>",
        )
        parser = StandardParser(
            query="search term",
            configs=[highlight_config],
        )
        params = parser.build()

        assert params["q"] == "search term"
        assert params["hl"] is True
        assert params["hl.fl"] == ["title", "content"]
        assert params["hl.snippets"] == 3
        assert params["hl.fragsize"] == 150
        assert params["hl.simple.pre"] == "<mark>"
        assert params["hl.simple.post"] == "</mark>"

    def test_single_more_like_this_config_in_constructor(self):
        """Test parser with a single more_like_this config passed in constructor."""
        mlt_config = MoreLikeThisParamsConfig(
            fields=["title", "description"],
            min_term_freq=2,
            min_doc_freq=5,
            max_query_terms=25,
            boost=True,
        )
        parser = StandardParser(
            query="id:123",
            configs=[mlt_config],
        )
        params = parser.build()

        assert params["q"] == "id:123"
        assert params["mlt"] is True
        assert params["mlt.fl"] == ["title", "description"]
        assert params["mlt.mintf"] == 2
        assert params["mlt.mindf"] == 5
        assert params["mlt.maxqt"] == 25
        assert params["mlt.boost"] is True

    def test_multiple_configs_in_constructor(self):
        """Test parser with multiple configs passed in constructor."""
        facet_config = FacetParamsConfig(
            fields=["category"],
            mincount=1,
        )
        group_config = GroupParamsConfig(
            by="brand",
            limit=2,
        )
        highlight_config = HighlightParamsConfig(
            fields=["description"],
            fragment_size=100,
        )

        parser = StandardParser(
            query="electronics",
            configs=[facet_config, group_config, highlight_config],
        )
        params = parser.build()

        # Check basic query param
        assert params["q"] == "electronics"

        # Check facet config
        assert params["facet"] is True
        assert params["facet.field"] == ["category"]
        assert params["facet.mincount"] == 1

        # Check group config
        assert params["group"] is True
        assert params["group.field"] == "brand"
        assert params["group.limit"] == 2

        # Check highlight config
        assert params["hl"] is True
        assert params["hl.fl"] == ["description"]
        assert params["hl.fragsize"] == 100

    def test_dismax_with_configs_in_constructor(self):
        """Test DisMaxQueryParser with configs in constructor."""
        facet_config = FacetParamsConfig(
            queries=["inStock:true", "price:[0 TO 100]"],
        )

        parser = DisMaxQueryParser(
            query="laptop",
            query_fields={"title": 2.0, "description": 1.0},
            min_match="75%",
            configs=[facet_config],
        )
        params = parser.build()

        assert params["defType"] == "dismax"
        assert params["q"] == "laptop"
        assert params["qf"] == "title^2.0 description^1.0"
        assert params["mm"] == "75%"
        assert params["facet"] is True
        assert params["facet.query"] == ["inStock:true", "price:[0 TO 100]"]


class TestConfigViaChaining:
    """Test adding configs via chaining methods."""

    def test_single_facet_via_chaining(self):
        """Test adding a facet config via chaining method."""
        parser = StandardParser(query="laptop").facet(
            fields=["category", "brand"],
            mincount=5,
            limit=10,
            sort="count",
        )
        params = parser.build()

        assert params["q"] == "laptop"
        assert params["facet"] is True
        assert params["facet.field"] == ["category", "brand"]
        assert params["facet.mincount"] == 5
        assert params["facet.limit"] == 10
        assert params["facet.sort"] == "count"

    def test_single_group_via_chaining(self):
        """Test adding a group config via chaining method."""
        parser = StandardParser(query="python programming").group(
            by="author",
            limit=3,
            sort="date desc",
            ngroups=True,
        )
        params = parser.build()

        assert params["q"] == "python programming"
        assert params["group"] is True
        assert params["group.field"] == "author"
        assert params["group.limit"] == 3
        assert params["group.sort"] == "date desc"
        assert params["group.ngroups"] is True

    def test_single_highlight_via_chaining(self):
        """Test adding a highlight config via chaining method."""
        parser = StandardParser(query="search term").highlight(
            fields=["title", "content"],
            snippets_per_field=3,
            fragment_size=150,
            simple_pre="<mark>",
            simple_post="</mark>",
        )
        params = parser.build()

        assert params["q"] == "search term"
        assert params["hl"] is True
        assert params["hl.fl"] == ["title", "content"]
        assert params["hl.snippets"] == 3
        assert params["hl.fragsize"] == 150
        assert params["hl.simple.pre"] == "<mark>"
        assert params["hl.simple.post"] == "</mark>"

    def test_single_more_like_this_via_chaining(self):
        """Test adding a more_like_this config via chaining method."""
        parser = StandardParser(query="id:123").more_like_this(
            fields=["title", "description"],
            min_term_freq=2,
            min_doc_freq=5,
            max_query_terms=25,
            boost=True,
        )
        params = parser.build()

        assert params["q"] == "id:123"
        assert params["mlt"] is True
        assert params["mlt.fl"] == ["title", "description"]
        assert params["mlt.mintf"] == 2
        assert params["mlt.mindf"] == 5
        assert params["mlt.maxqt"] == 25
        assert params["mlt.boost"] is True

    def test_multiple_configs_via_chaining(self):
        """Test adding multiple configs via chaining methods."""
        parser = (
            StandardParser(query="electronics")
            .facet(
                fields=["category"],
                mincount=1,
            )
            .group(
                by="brand",
                limit=2,
            )
            .highlight(
                fields=["description"],
                fragment_size=100,
            )
        )
        params = parser.build()

        # Check basic query param
        assert params["q"] == "electronics"

        # Check facet config
        assert params["facet"] is True
        assert params["facet.field"] == ["category"]
        assert params["facet.mincount"] == 1

        # Check group config
        assert params["group"] is True
        assert params["group.field"] == "brand"
        assert params["group.limit"] == 2

        # Check highlight config
        assert params["hl"] is True
        assert params["hl.fl"] == ["description"]
        assert params["hl.fragsize"] == 100

    def test_dismax_with_chaining(self):
        """Test DisMaxQueryParser with chaining methods."""
        parser = DisMaxQueryParser(
            query="laptop",
            query_fields={"title": 2.0, "description": 1.0},
            min_match="75%",
        ).facet(queries=["inStock:true", "price:[0 TO 100]"])

        params = parser.build()

        assert params["defType"] == "dismax"
        assert params["q"] == "laptop"
        assert params["qf"] == "title^2.0 description^1.0"
        assert params["mm"] == "75%"
        assert params["facet"] is True
        assert params["facet.query"] == ["inStock:true", "price:[0 TO 100]"]


class TestMixedConfigApproaches:
    """Test mixing configs in constructor with chaining methods."""

    def test_constructor_config_plus_chaining(self):
        """Test parser with config in constructor and additional config via chaining."""
        facet_config = FacetParamsConfig(
            fields=["category"],
            mincount=1,
        )

        parser = StandardParser(
            query="laptop",
            configs=[facet_config],
        ).group(
            by="brand",
            limit=2,
        )
        params = parser.build()

        assert params["q"] == "laptop"

        # Check facet config from constructor
        assert params["facet"] is True
        assert params["facet.field"] == ["category"]
        assert params["facet.mincount"] == 1

        # Check group config from chaining
        assert params["group"] is True
        assert params["group.field"] == "brand"
        assert params["group.limit"] == 2

    def test_constructor_multiple_configs_plus_chaining(self):
        """Test parser with multiple configs in constructor and additional chaining."""
        facet_config = FacetParamsConfig(
            fields=["category", "brand"],
            limit=20,
        )
        highlight_config = HighlightParamsConfig(
            fields=["title"],
            fragment_size=200,
        )

        parser = (
            StandardParser(
                query="search query",
                configs=[facet_config, highlight_config],
            )
            .group(
                by="author",
                limit=5,
            )
            .more_like_this(
                fields=["content"],
                min_term_freq=1,
            )
        )
        params = parser.build()

        assert params["q"] == "search query"

        # Check facet config from constructor
        assert params["facet"] is True
        assert params["facet.field"] == ["category", "brand"]
        assert params["facet.limit"] == 20

        # Check highlight config from constructor
        assert params["hl"] is True
        assert params["hl.fl"] == ["title"]
        assert params["hl.fragsize"] == 200

        # Check group config from chaining
        assert params["group"] is True
        assert params["group.field"] == "author"
        assert params["group.limit"] == 5

        # Check more_like_this config from chaining
        assert params["mlt"] is True
        assert params["mlt.fl"] == ["content"]
        assert params["mlt.mintf"] == 1


class TestRangeFaceting:
    """Test range faceting configurations."""

    def test_range_facet_via_constructor(self):
        """Test range faceting config passed in constructor."""
        facet_config = FacetParamsConfig(
            range_field=["price"],
            range_start={"price": "0"},
            range_end={"price": "1000"},
            range_gap={"price": "100"},
        )
        parser = StandardParser(
            query="*:*",
            configs=[facet_config],
        )
        params = parser.build()

        assert params["facet"] is True
        assert params["facet.range"] == ["price"]
        assert params["facet.range.start"] == {"price": "0"}
        assert params["facet.range.end"] == {"price": "1000"}
        assert params["facet.range.gap"] == {"price": "100"}

    def test_range_facet_via_chaining(self):
        """Test range faceting config via chaining method."""
        parser = StandardParser(query="*:*").facet(
            range_field=["price"],
            range_start={"price": "0"},
            range_end={"price": "1000"},
            range_gap={"price": "100"},
        )
        params = parser.build()

        assert params["facet"] is True
        assert params["facet.range"] == ["price"]
        assert params["facet.range.start"] == {"price": "0"}
        assert params["facet.range.end"] == {"price": "1000"}
        assert params["facet.range.gap"] == {"price": "100"}


class TestGroupByQuery:
    """Test group-by-query configurations."""

    def test_group_by_query_via_constructor(self):
        """Test group by query config passed in constructor."""
        group_config = GroupParamsConfig(
            query=["price:[0 TO 50]", "price:[50 TO 100]", "price:[100 TO *]"],
            limit=5,
        )
        parser = StandardParser(
            query="electronics",
            configs=[group_config],
        )
        params = parser.build()

        assert params["group"] is True
        assert params["group.query"] == [
            "price:[0 TO 50]",
            "price:[50 TO 100]",
            "price:[100 TO *]",
        ]
        assert params["group.limit"] == 5

    def test_group_by_query_via_chaining(self):
        """Test group by query config via chaining method."""
        parser = StandardParser(query="electronics").group(
            query=["price:[0 TO 50]", "price:[50 TO 100]", "price:[100 TO *]"],
            limit=5,
        )
        params = parser.build()

        assert params["group"] is True
        assert params["group.query"] == [
            "price:[0 TO 50]",
            "price:[50 TO 100]",
            "price:[100 TO *]",
        ]
        assert params["group.limit"] == 5


class TestAdvancedHighlighting:
    """Test advanced highlighting configurations."""

    def test_unified_highlighter_via_constructor(self):
        """Test unified highlighter config in constructor."""
        highlight_config = HighlightParamsConfig(
            fields=["content"],
            method="unified",
            offset_source="POSTINGS",
            tag_before="<em class='highlight'>",
            tag_after="</em>",
            max_analyzed_chars=500000,
        )
        parser = StandardParser(
            query="search term",
            configs=[highlight_config],
        )
        params = parser.build()

        assert params["hl"] is True
        assert params["hl.fl"] == ["content"]
        # method is returned as enum, convert to string for comparison
        assert str(params["hl.method"]).split(".")[-1] == "UNIFIED"
        assert params["hl.offsetSource"] == "POSTINGS"
        assert params["hl.tag.pre"] == "<em class='highlight'>"
        assert params["hl.tag.post"] == "</em>"
        assert params["hl.maxAnalyzedChars"] == 500000

    def test_unified_highlighter_via_chaining(self):
        """Test unified highlighter config via chaining."""
        parser = StandardParser(query="search term").highlight(
            fields=["content"],
            method="unified",
            offset_source="POSTINGS",
            tag_before="<em class='highlight'>",
            tag_after="</em>",
            max_analyzed_chars=500000,
        )
        params = parser.build()

        assert params["hl"] is True
        assert params["hl.fl"] == ["content"]
        # method is returned as enum, convert to string for comparison
        assert str(params["hl.method"]).split(".")[-1] == "UNIFIED"
        assert params["hl.offsetSource"] == "POSTINGS"
        assert params["hl.tag.pre"] == "<em class='highlight'>"
        assert params["hl.tag.post"] == "</em>"
        assert params["hl.maxAnalyzedChars"] == 500000
