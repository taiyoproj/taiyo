from taiyo.params import GroupParamsConfig, FacetParamsConfig
from taiyo.parsers import StandardParser, DisMaxQueryParser


def test_lucene():
    group = GroupParamsConfig(field=["title", "description"])
    parser = StandardParser(
        query="foo bar",
        query_operator="AND",
        default_field="title",
        split_on_whitespace=True,
        group=group,
    )
    params = parser.build()
    assert params["q"] == "foo bar"
    assert params["q.op"] == "AND"
    assert params["df"] == "title"
    assert params["sow"]
    assert params["group"]
    assert params["group.field"] == ["title", "description"]


def test_dismax():
    parser = DisMaxQueryParser(
        query="foo bar",
        query_fields={"title": 2.0, "body": 1.0},
        query_slop=1,
        phrase_fields={"title": 3.0},
        phrase_slop=2,
        min_match="75%",
        tie_breaker=0.1,
        boost_queries=["cat:electronics^5.0"],
        boost_functons=["recip(rord(myfield),1,2,3)"],
        facet=FacetParamsConfig(queries=["facet true"]),
    )
    params = parser.build()
    assert params["defType"] == "dismax"
    assert params["q"] == "foo bar"
    assert params["qf"] == "title^2.0 body^1.0"
    assert params["mm"] == "75%"
    assert params["pf"] == "title^3.0"
    assert params["ps"] == 2
    assert params["qs"] == 1
    assert params["tie"] == 0.1
    assert params["bq"] == ["cat:electronics^5.0"]
    assert params["bf"] == ["recip(rord(myfield),1,2,3)"]
    assert params["facet"]
    assert params["facet.query"] == ["facet true"]
