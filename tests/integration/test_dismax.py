import random
import string
import time
from taiyo import SolrClient, SolrError, SolrDocument
from taiyo.schema import SolrField
from taiyo.parsers import DisMaxQueryParser, ExtendedDisMaxQueryParser

SOLR_URL = "http://localhost:8983/solr"

class Product(SolrDocument):
    name: str
    description: str


def test_dismax_and_edismax_queries():
    """End-to-end test for DisMax and eDisMax query parsers with text analysis."""
    _rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    with SolrClient(SOLR_URL) as client:
        collection_name = f"test_taiyo_dismax_{_rand}"

        client.create_collection(collection_name, num_shards=1, replication_factor=1)

        time.sleep(1)

        client.set_collection(collection_name)

        # Define and add fields with text type for proper analysis
        fields = [
            SolrField(name="name", type="text_general", stored=True, indexed=True, multi_valued=False),
            SolrField(name="description", type="text_general", stored=True, indexed=True, multi_valued=False),
        ]

        for field in fields:
            client.add_field(field)

        time.sleep(1)

        # Add test documents with realistic content
        docs = [
            Product(
                name="Apple MacBook Pro",
                description="Powerful laptop with M2 chip for professional work"
            ),
            Product(
                name="Dell XPS 15",
                description="High performance laptop with Intel processor"
            ),
            Product(
                name="Apple iPhone 15",
                description="Latest smartphone with advanced camera features"
            ),
            Product(
                name="Samsung Galaxy S24",
                description="Android smartphone with powerful performance"
            ),
            Product(
                name="Sony Headphones",
                description="Wireless noise cancelling headphones for music"
            ),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Test DisMax query for Apple products
        dismax = DisMaxQueryParser(
            query="Apple laptop",
            query_fields={"name": 3.0, "description": 1.0},
            min_match="50%",
        )
        res = client.search(dismax, document_model=Product)
        assert res.status == 0
        assert res.num_found >= 1
        assert all(isinstance(doc, Product) for doc in res.docs)
        # Should find Apple MacBook Pro as it matches both terms
        assert any("Apple" in doc.name for doc in res.docs)

        # Test eDisMax with phrase query and boost
        edismax = ExtendedDisMaxQueryParser(
            query="smartphone camera",
            query_fields={"name": 2.0, "description": 1.5},
            phrase_fields={"description": 3.0},
            split_on_whitespace=True,
            min_match="1",
        )
        res2 = client.search(edismax, document_model=Product)
        assert res2.status == 0
        assert res2.num_found >= 1
        assert all(isinstance(doc, Product) for doc in res2.docs)
        # Should find smartphones
        matching_docs = [doc for doc in res2.docs if "smartphone" in doc.description.lower()]
        assert len(matching_docs) >= 1

        # Test eDisMax with boolean operators
        edismax2 = ExtendedDisMaxQueryParser(
            query="laptop -Apple",
            query_fields={"name": 2.0, "description": 1.0},
            min_match="1",
        )
        res3 = client.search(edismax2, document_model=Product)
        assert res3.status == 0
        # Should find Dell but not Apple laptops
        if res3.num_found > 0:
            assert all("Apple" not in doc.name for doc in res3.docs)

        # Cleanup
        try:
            client.delete_collection(collection_name)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
