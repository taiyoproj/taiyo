from taiyo.parsers import (
    KNNQueryParser,
    KNNTextToVectorQueryParser,
    VectorSimilarityQueryParser,
)


def test_knn():
    parser = KNNQueryParser(
        field="vector",
        top_k=5,
        pre_filter=["inStock:true"],
        include_tags=["tag1"],
        exclude_tags=["tag2"],
        vector=[1.0, 2.0, 4.0],
        debug="INFO",
    )
    params = parser.build()
    assert len(params) == 2
    assert (
        params["q"]
        == "{!knn topK=5 f=vector preFilter=inStock:true includeTags=tag1 excludeTags=tag2}[1.0, 2.0, 4.0]"
    )
    assert params["debug"] == "INFO"


def test_knn_text_to_vector():
    parser = KNNTextToVectorQueryParser(
        field="vector", text="query text to search for", model="emb_model", top_k=5
    )
    params = parser.build()
    assert len(params) == 1
    assert (
        params["q"]
        == "{!knn_text_to_vector model=emb_model topK=5 f=vector}query text to search for"
    )


def test_vector_similarity():
    parser = VectorSimilarityQueryParser(
        field="vector", min_return=0.7, min_traverse=0.2, vector=[0.1, 2.0, 3.9]
    )
    params = parser.build()
    assert len(params) == 1
    assert (
        params["q"]
        == "{!vectorSimilarity minTraverse=0.2 minReturn=0.7 f=vector}[0.1, 2.0, 3.9]"
    )


def test_knn_with_facet_config():
    """Test that KNN parser properly includes facet configuration."""
    parser = KNNQueryParser(
        field="product_vector",
        vector=[0.1, 0.2, 0.3, 0.4],
        top_k=10
    )
    parser.facet(fields=["category", "brand"], mincount=1)
    
    result = parser.build()
    
    # Check that both KNN params and facet params are present
    assert "q" in result
    assert "{!knn" in result["q"]
    assert result["facet"] is True
    assert result["facet.field"] == ["category", "brand"]
    assert result["facet.mincount"] == 1


def test_vector_similarity_with_group_config():
    """Test that VectorSimilarity parser properly includes group configuration."""
    parser = VectorSimilarityQueryParser(
        field="doc_vector",
        vector=[1.0, 2.0, 3.0],
        min_return=0.7
    )
    parser.group(by="author", limit=5)
    
    result = parser.build()
    
    # Check that both vector similarity params and group params are present
    assert "q" in result
    assert "{!vectorSimilarity" in result["q"]
    assert result["group"] is True
    assert result["group.field"] == "author"
    assert result["group.limit"] == 5


def test_knn_with_multiple_configs():
    """Test that KNN parser can handle multiple configs at once."""
    parser = KNNQueryParser(
        field="embedding",
        vector=[0.5] * 384,
        top_k=20
    )
    parser.facet(fields=["category"], mincount=1)
    parser.group(by="product_id", limit=3)
    parser.highlight(fields=["title"], snippets_per_field=1)
    
    result = parser.build()
    
    # Check that all configs are present
    assert "q" in result
    assert result["facet"] is True
    assert result["group"] is True
    assert result["hl"] is True
    assert result["facet.field"] == ["category"]
    assert result["group.field"] == "product_id"
    assert result["hl.fl"] == ["title"]
