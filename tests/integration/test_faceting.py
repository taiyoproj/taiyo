import random
import string
import time
from pydantic import Field
from taiyo import SolrClient, SolrError, SolrDocument
from taiyo.schema import SolrField
from taiyo.parsers import StandardParser

SOLR_URL = "http://localhost:8983/solr"


class Movie(SolrDocument):
    title: str
    genre: str
    director: str
    year: int
    vector: list[float] = Field(
        default_factory=list, description="Dense vector for KNN search"
    )


def test_faceting_and_highlighting():
    """End-to-end test for faceting and highlighting."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_taiyo_faceting_{_rand}"

    with SolrClient(SOLR_URL) as client:
        client.create_collection(collection, num_shards=1, replication_factor=1)

        client.set_collection(collection)

        fields = [
            SolrField(name="title", type="string", stored=True),
            SolrField(name="genre", type="string", stored=True),
            SolrField(name="director", type="string", stored=True),
            SolrField(name="year", type="pint", stored=True),
        ]

        for field in fields:
            client.add_field(field)

        docs = [
            Movie(
                title="The Shawshank Redemption",
                genre="Drama",
                director="Frank Darabont",
                year=1994,
                vector=[0.12, 0.34],
            ),
            Movie(
                title="The Godfather",
                genre="Drama",
                director="Francis Ford Coppola",
                year=1972,
                vector=[0.15, 0.32],
            ),
            Movie(
                title="The Dark Knight",
                genre="Action",
                director="Christopher Nolan",
                year=2008,
                vector=[0.89, 0.67],
            ),
            Movie(
                title="Pulp Fiction",
                genre="Crime",
                director="Quentin Tarantino",
                year=1994,
                vector=[0.45, 0.78],
            ),
            Movie(
                title="Inception",
                genre="Sci-Fi",
                director="Christopher Nolan",
                year=2010,
                vector=[0.23, 0.56],
            ),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        parser = StandardParser(query='director:"Christopher Nolan"', rows=10)
        res = client.search(parser, document_model=Movie)
        assert res.status == 0
        assert res.num_found >= 1
        assert all(isinstance(doc, Movie) for doc in res.docs)
        extra = getattr(res, "extra", {})
        assert "facet_counts" in extra or "facets" in extra
        params = extra.get("responseHeader", {}).get("params", {})
        assert params.get("highlight") == "true"
        assert "title" in params.get("hl.fl", "") or "director" in params.get(
            "hl.fl", ""
        )

        try:
            client.delete_collection(collection)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
