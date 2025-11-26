"""Unit tests for TermsQueryParser."""

import pytest
from taiyo.parsers import TermsQueryParser


class TestTermsQueryParserBasic:
    """Test basic TermsQueryParser functionality."""

    def test_basic_terms_query(self):
        """Test basic terms query with default parameters."""
        parser = TermsQueryParser(
            field="tags", terms=["software", "apache", "solr", "lucene"]
        )
        params = parser.build()

        assert params["q"] == "*:*"
        assert params["fq"] == "{!terms f=tags}software,apache,solr,lucene"

    def test_single_term(self):
        """Test with a single term."""
        parser = TermsQueryParser(field="category", terms=["electronics"])
        params = parser.build()

        assert params["fq"] == "{!terms f=category}electronics"

    def test_many_terms(self):
        """Test with many terms (100+)."""
        terms = [f"id_{i}" for i in range(150)]
        parser = TermsQueryParser(field="product_id", terms=terms)
        params = parser.build()

        expected_terms = ",".join(terms)
        assert params["fq"] == f"{{!terms f=product_id}}{expected_terms}"


class TestTermsQueryParserQueryField:
    """Test optional query field parameter."""

    def test_default_query(self):
        """Test that default query is *:*."""
        parser = TermsQueryParser(field="tags", terms=["tag1", "tag2"])
        params = parser.build()

        assert params["q"] == "*:*"

    def test_custom_query(self):
        """Test with custom query field."""
        parser = TermsQueryParser(
            field="tags", terms=["python", "java"], query="status:active"
        )
        params = parser.build()

        assert params["q"] == "status:active"
        assert params["fq"] == "{!terms f=tags}python,java"

    def test_complex_query(self):
        """Test with complex query expression."""
        parser = TermsQueryParser(
            field="tags",
            terms=["tag1", "tag2"],
            query="status:active AND inStock:true AND price:[10 TO 100]",
        )
        params = parser.build()

        assert params["q"] == "status:active AND inStock:true AND price:[10 TO 100]"


class TestTermsQueryParserSeparator:
    """Test separator parameter."""

    def test_default_comma_separator(self):
        """Test default comma separator."""
        parser = TermsQueryParser(field="tags", terms=["a", "b", "c"])
        params = parser.build()

        assert params["fq"] == "{!terms f=tags}a,b,c"

    def test_space_separator(self):
        """Test space separator."""
        parser = TermsQueryParser(
            field="categoryId", terms=["8", "6", "7", "5309"], separator=" "
        )
        params = parser.build()

        assert params["fq"] == "{!terms f=categoryId}8 6 7 5309"

    def test_custom_separator(self):
        """Test custom separator."""
        parser = TermsQueryParser(
            field="ids", terms=["id1", "id2", "id3"], separator="|"
        )
        params = parser.build()

        assert params["fq"] == "{!terms f=ids}id1|id2|id3"

    def test_pipe_separator(self):
        """Test pipe separator."""
        parser = TermsQueryParser(
            field="codes", terms=["ABC", "DEF", "GHI"], separator="|"
        )
        params = parser.build()

        assert params["fq"] == "{!terms f=codes}ABC|DEF|GHI"


class TestTermsQueryParserMethod:
    """Test method parameter."""

    def test_default_method_not_in_params(self):
        """Test that default method (termsFilter) is not explicitly set."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"])
        params = parser.build()

        assert "method" not in params
        assert "{!terms f=tags}a,b" == params["fq"]

    def test_boolean_query_method(self):
        """Test booleanQuery method."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"], method="booleanQuery")
        params = parser.build()

        assert params["method"] == "booleanQuery"
        assert params["fq"] == "{!terms f=tags method=booleanQuery}a,b"

    def test_automaton_method(self):
        """Test automaton method."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"], method="automaton")
        params = parser.build()

        assert params["method"] == "automaton"
        assert params["fq"] == "{!terms f=tags method=automaton}a,b"

    def test_docvalues_filter_method(self):
        """Test docValuesTermsFilter method."""
        parser = TermsQueryParser(
            field="author_id",
            terms=["author1", "author2"],
            method="docValuesTermsFilter",
        )
        params = parser.build()

        assert params["method"] == "docValuesTermsFilter"
        assert (
            params["fq"]
            == "{!terms f=author_id method=docValuesTermsFilter}author1,author2"
        )

    def test_docvalues_per_segment_method(self):
        """Test docValuesTermsFilterPerSegment method."""
        parser = TermsQueryParser(
            field="tags", terms=["a"], method="docValuesTermsFilterPerSegment"
        )
        params = parser.build()

        assert params["method"] == "docValuesTermsFilterPerSegment"

    def test_docvalues_top_level_method(self):
        """Test docValuesTermsFilterTopLevel method."""
        parser = TermsQueryParser(
            field="tags", terms=["a"], method="docValuesTermsFilterTopLevel"
        )
        params = parser.build()

        assert params["method"] == "docValuesTermsFilterTopLevel"


class TestTermsQueryParserCommonParams:
    """Test common query parameters."""

    def test_with_rows(self):
        """Test with rows parameter."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"], rows=20)
        params = parser.build()

        assert params["rows"] == 20

    def test_with_start(self):
        """Test with start parameter."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"], start=10)
        params = parser.build()

        assert params["start"] == 10

    def test_with_filters(self):
        """Test with additional filter queries."""
        parser = TermsQueryParser(
            field="product_id",
            terms=["P123", "P456"],
            filters=["status:active", "inStock:true"],
        )
        params = parser.build()

        # fq should be a list: all filters + terms filter
        assert params["fq"] == ["status:active", "inStock:true", "{!terms f=product_id}P123,P456"]

    def test_with_field_list(self):
        """Test with field list."""
        parser = TermsQueryParser(
            field="tags", terms=["a", "b"], field_list=["id", "title", "score"]
        )
        params = parser.build()

        assert params["fl"] == ["id", "title", "score"]

    def test_with_sort(self):
        """Test with sort parameter."""
        parser = TermsQueryParser(
            field="tags", terms=["a", "b"], sort="price asc, score desc"
        )
        params = parser.build()

        assert params["sort"] == "price asc, score desc"


class TestTermsQueryParserConfigs:
    """Test with configuration objects."""

    def test_with_facet_config(self):
        """Test with facet configuration."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"]).facet(
            fields=["category", "brand"], mincount=1
        )
        params = parser.build()

        assert params["facet"] is True
        assert params["facet.field"] == ["category", "brand"]
        assert params["facet.mincount"] == 1

    def test_with_group_config(self):
        """Test with group configuration."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"]).group(
            by="category", limit=5
        )
        params = parser.build()

        assert params["group"] is True
        assert params["group.field"] == "category"
        assert params["group.limit"] == 5

    def test_with_highlight_config(self):
        """Test with highlight configuration."""
        parser = TermsQueryParser(field="tags", terms=["a", "b"]).highlight(
            fields=["title", "description"], fragment_size=150
        )
        params = parser.build()

        assert params["hl"] is True
        assert params["hl.fl"] == ["title", "description"]
        assert params["hl.fragsize"] == 150

    def test_chained_configs(self):
        """Test chaining multiple configs."""
        parser = (
            TermsQueryParser(field="tags", terms=["python", "java"])
            .facet(fields=["category"], mincount=1)
            .group(by="brand", limit=3)
            .highlight(fields=["title"], fragment_size=100)
        )
        params = parser.build()

        assert params["facet"] is True
        assert params["group"] is True
        assert params["hl"] is True


class TestTermsQueryParserEdgeCases:
    """Test edge cases and special scenarios."""

    def test_terms_with_special_characters(self):
        """Test terms containing special characters."""
        parser = TermsQueryParser(field="tags", terms=["C++", "C#", "F#", ".NET"])
        params = parser.build()

        assert params["fq"] == "{!terms f=tags}C++,C#,F#,.NET"

    def test_terms_with_spaces(self):
        """Test terms containing spaces."""
        parser = TermsQueryParser(
            field="category", terms=["Science Fiction", "Action Adventure"]
        )
        params = parser.build()

        assert params["fq"] == "{!terms f=category}Science Fiction,Action Adventure"

    def test_terms_with_unicode(self):
        """Test terms with unicode characters."""
        parser = TermsQueryParser(
            field="tags", terms=["日本語", "中文", "한국어", "العربية"]
        )
        params = parser.build()

        assert params["fq"] == "{!terms f=tags}日本語,中文,한국어,العربية"

    def test_empty_terms_list(self):
        """Test with empty terms list - should still be valid."""
        parser = TermsQueryParser(field="tags", terms=[])
        params = parser.build()

        assert params["fq"] == "{!terms f=tags}"

    def test_numeric_terms(self):
        """Test with numeric terms (as strings)."""
        parser = TermsQueryParser(field="product_id", terms=["123", "456", "789"])
        params = parser.build()

        assert params["fq"] == "{!terms f=product_id}123,456,789"


class TestTermsQueryParserCombinations:
    """Test complex combinations of parameters."""

    def test_all_parameters(self):
        """Test with all parameters combined."""
        parser = TermsQueryParser(
            field="tags",
            terms=["tag1", "tag2", "tag3"],
            query="status:active",
            separator=",",
            method="booleanQuery",
            rows=50,
            start=10,
            filters=["inStock:true"],
            field_list=["id", "title"],
            sort="score desc",
        )
        params = parser.build()

        assert params["q"] == "status:active"
        assert params["fq"] == ["inStock:true", "{!terms f=tags method=booleanQuery}tag1,tag2,tag3"]
        # field 'f' is excluded from top-level params (only in fq local params)
        assert params["method"] == "booleanQuery"
        assert params["rows"] == 50
        assert params["start"] == 10
        assert params["fl"] == ["id", "title"]
        assert params["sort"] == "score desc"

    def test_space_separator_with_method(self):
        """Test space separator combined with method."""
        parser = TermsQueryParser(
            field="categoryId",
            terms=["8", "6", "7"],
            separator=" ",
            method="booleanQuery",
        )
        params = parser.build()

        assert params["fq"] == "{!terms f=categoryId method=booleanQuery}8 6 7"
        assert params["method"] == "booleanQuery"

    def test_custom_query_with_configs(self):
        """Test custom query with faceting and grouping."""
        parser = (
            TermsQueryParser(
                field="tags",
                terms=["python", "java"],
                query="status:active AND year:[2020 TO *]",
            )
            .facet(fields=["language", "framework"])
            .group(by="author")
        )
        params = parser.build()

        assert params["q"] == "status:active AND year:[2020 TO *]"
        assert params["fq"] == "{!terms f=tags}python,java"
        assert params["facet"] is True
        assert params["group"] is True


class TestTermsQueryParserValidation:
    """Test parameter validation."""

    def test_invalid_method_raises_error(self):
        """Test that invalid method raises validation error."""
        with pytest.raises(Exception):  # Pydantic validation error
            TermsQueryParser(
                field="tags",
                terms=["a", "b"],
                method="invalidMethod",  # type: ignore
            )

    def test_field_required(self):
        """Test that field is required."""
        with pytest.raises(Exception):  # Pydantic validation error
            TermsQueryParser(terms=["a", "b"])  # type: ignore

    def test_terms_required(self):
        """Test that terms is required."""
        with pytest.raises(Exception):  # Pydantic validation error
            TermsQueryParser(field="tags")  # type: ignore
