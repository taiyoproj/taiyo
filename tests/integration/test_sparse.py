import random
import string
import time
from taiyo import SolrClient, SolrError, SolrDocument
from taiyo.schema import SolrField
from taiyo.parsers import StandardParser

SOLR_URL = "http://localhost:8983/solr"


class Article(SolrDocument):
    title: str
    content: str
    category: str


def test_standard():
    """End-to-end test for standard query parser with text analysis."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_taiyo_standard_{_rand}"

    with SolrClient(SOLR_URL) as client:
        # Create collection
        client.create_collection(collection, num_shards=1, replication_factor=1)
        time.sleep(1)

        client.set_collection(collection)

        # Define and add fields with text type for analysis
        fields = [
            SolrField(
                name="title",
                type="text_general",
                stored=True,
                indexed=True,
                multi_valued=False,
            ),
            SolrField(
                name="content",
                type="text_general",
                stored=True,
                indexed=True,
                multi_valued=False,
            ),
            SolrField(name="category", type="string", stored=True, indexed=True),
        ]

        for field in fields:
            try:
                client.add_field(field)
            except SolrError:
                pass  # Field may already exist

        time.sleep(1)

        # Add test documents with realistic content
        docs = [
            Article(
                title="Introduction to Machine Learning",
                content="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience.",
                category="technology",
            ),
            Article(
                title="Deep Learning Neural Networks",
                content="Deep learning uses neural networks with multiple layers to process data and make predictions.",
                category="technology",
            ),
            Article(
                title="Cooking Italian Pasta",
                content="Learn how to cook authentic Italian pasta with traditional recipes and techniques.",
                category="cooking",
            ),
            Article(
                title="Healthy Eating Guide",
                content="A comprehensive guide to healthy eating and nutrition for better lifestyle.",
                category="health",
            ),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Test standard query with field-specific search
        parser = StandardParser(query="title:learning", rows=10)
        res = client.search(parser, document_model=Article)
        assert res.status == 0
        assert res.num_found >= 1
        assert all(isinstance(doc, Article) for doc in res.docs)
        # Should find articles with "learning" in title
        assert any("learning" in d.title.lower() for d in res.docs)

        # Test boolean query
        parser2 = StandardParser(
            query="category:technology AND content:neural", rows=10
        )
        res2 = client.search(parser2, document_model=Article)
        assert res2.status == 0
        # Should find the deep learning article
        if res2.num_found > 0:
            assert all(doc.category == "technology" for doc in res2.docs)
            assert any("neural" in doc.content.lower() for doc in res2.docs)

        # Test phrase query
        parser3 = StandardParser(query='content:"machine learning"', rows=10)
        res3 = client.search(parser3, document_model=Article)
        assert res3.status == 0
        assert res3.num_found >= 1
        # Should find the machine learning article
        assert any("machine learning" in doc.content.lower() for doc in res3.docs)

        # Cleanup
        try:
            client.delete_collection(collection)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
