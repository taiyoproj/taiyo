from taiyo.parsers import (
    KNNQueryParser,
    KNNTextToVectorQueryParser,
    VectorSimilarityParser,
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
    parser = VectorSimilarityParser(
        field="vector", min_return=0.7, min_traverse=0.2, vector=[0.1, 2.0, 3.9]
    )
    params = parser.build()
    assert len(params) == 1
    assert (
        params["q"]
        == "{!vectorSimilarity minTraverse=0.2 minReturn=0.7 f=vector}[0.1, 2.0, 3.9]"
    )
