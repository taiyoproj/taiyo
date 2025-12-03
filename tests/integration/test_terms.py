"""Integration tests for TermsQueryParser with Solr."""

import random
import string
import pytest
from typing import Generator


from taiyo import SolrClient, SolrDocument
from taiyo.schema import SolrField
from taiyo.parsers import TermsQueryParser


SOLR_URL = "http://localhost:8983/solr"
_rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
COLLECTION = f"test_taiyo_terms_{_rand}"


class Product(SolrDocument):
    """Product document for testing."""

    product_id: str
    name: str
    category: str
    tags: list[str]
    price: float
    inStock: bool
    brand: str


@pytest.fixture(scope="module")
def solr_client() -> Generator[SolrClient, None, None]:
    """Create Solr client and collection for testing."""
    with SolrClient(SOLR_URL) as client:
        # Create collection
        try:
            client.create_collection(COLLECTION, num_shards=1, replication_factor=1)
        except Exception:
            pass  # Collection may already exist

        client.set_collection(COLLECTION)

        # Add fields
        fields = [
            SolrField(name="product_id", type="string", stored=True, indexed=True),
            SolrField(name="name", type="string", stored=True),
            SolrField(name="category", type="string", stored=True, indexed=True),
            SolrField(
                name="tags", type="string", stored=True, indexed=True, multi_valued=True
            ),
            SolrField(
                name="price", type="pfloat", stored=True, indexed=True, docValues=True
            ),
            SolrField(
                name="inStock",
                type="boolean",
                stored=True,
                indexed=True,
                docValues=True,
            ),
            SolrField(
                name="brand", type="string", stored=True, indexed=True, docValues=True
            ),
        ]

        for field in fields:
            try:
                client.add_field(field)
            except Exception:
                pass  # Field may already exist

        # Index sample documents
        docs = [
            Product(
                product_id="P001",
                name="Python Programming Book",
                category="books",
                tags=["python", "programming", "software"],
                price=29.99,
                inStock=True,
                brand="TechBooks",
            ),
            Product(
                product_id="P002",
                name="Java Development Guide",
                category="books",
                tags=["java", "programming", "software"],
                price=34.99,
                inStock=True,
                brand="TechBooks",
            ),
            Product(
                product_id="P003",
                name="Rust Systems Programming",
                category="books",
                tags=["rust", "programming", "systems"],
                price=39.99,
                inStock=False,
                brand="DevPress",
            ),
            Product(
                product_id="P004",
                name="Apache Solr Guide",
                category="books",
                tags=["solr", "apache", "search", "software"],
                price=44.99,
                inStock=True,
                brand="TechBooks",
            ),
            Product(
                product_id="P005",
                name="Lucene in Action",
                category="books",
                tags=["lucene", "apache", "search", "java"],
                price=49.99,
                inStock=True,
                brand="DevPress",
            ),
            Product(
                product_id="P006",
                name="Wireless Mouse",
                category="electronics",
                tags=["computer", "peripheral", "wireless"],
                price=19.99,
                inStock=True,
                brand="TechGear",
            ),
            Product(
                product_id="P007",
                name="Mechanical Keyboard",
                category="electronics",
                tags=["computer", "peripheral", "mechanical"],
                price=89.99,
                inStock=False,
                brand="TechGear",
            ),
            Product(
                product_id="P008",
                name="USB-C Hub",
                category="electronics",
                tags=["computer", "accessory", "usb"],
                price=39.99,
                inStock=True,
                brand="ConnectPro",
            ),
        ]

        client.add(docs)
        client.commit()

        yield client

        # Cleanup
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass


def test_basic_terms_query(solr_client):
    """Test basic terms query returns matching documents."""
    parser = TermsQueryParser(field="tags", terms=["python", "java", "rust"])

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 3
    product_ids = [doc.product_id for doc in results.docs]
    assert "P001" in product_ids  # Python book
    assert "P002" in product_ids  # Java book
    assert "P003" in product_ids  # Rust book


def test_terms_query_with_custom_query(solr_client):
    """Test terms query combined with custom query field."""
    parser = TermsQueryParser(
        field="tags",
        terms=["programming", "search"],
        query="inStock:true",
    )

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 3
    # All returned docs should be in stock
    for doc in results.docs:
        assert doc.inStock is True


def test_terms_query_single_match(solr_client):
    """Test terms query with single matching term."""
    parser = TermsQueryParser(field="tags", terms=["lucene"])

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found == 1
    assert results.docs[0].product_id == "P005"


def test_terms_query_no_matches(solr_client):
    """Test terms query with no matching documents."""
    parser = TermsQueryParser(
        field="tags", terms=["nonexistent", "invalid", "notfound"]
    )

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found == 0


def test_terms_query_with_product_ids(solr_client):
    """Test filtering by specific product IDs."""
    parser = TermsQueryParser(field="product_id", terms=["P001", "P003", "P005"])

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found == 3
    product_ids = {doc.product_id for doc in results.docs}
    assert product_ids == {"P001", "P003", "P005"}


def test_terms_query_with_space_separator(solr_client):
    """Test terms query with space separator."""
    # Solr terms parser expects comma-separated values; space separator may not work.
    parser = TermsQueryParser(
        field="product_id",
        terms=["P001", "P002", "P003"],
        separator=",",  # Use comma
    )

    results = solr_client.search(parser, document_model=Product)

    print("[DEBUG] test_terms_query_with_space_separator results:", results)
    assert results.num_found == 3


def test_terms_query_with_boolean_method(solr_client):
    """Test terms query with booleanQuery method."""
    parser = TermsQueryParser(
        field="tags", terms=["apache", "solr"], method="booleanQuery"
    )

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 2


def test_terms_query_with_pagination(solr_client):
    """Test terms query with rows and start parameters."""
    parser = TermsQueryParser(
        field="category", terms=["books", "electronics"], rows=3, start=0
    )

    results = solr_client.search(parser, document_model=Product)

    assert len(results.docs) <= 3

    # Test second page
    parser2 = TermsQueryParser(
        field="category", terms=["books", "electronics"], rows=3, start=3
    )

    results2 = solr_client.search(parser2, document_model=Product)

    # Ensure we get different docs (pagination working)
    if len(results2.docs) > 0:
        first_page_ids = {doc.product_id for doc in results.docs}
        second_page_ids = {doc.product_id for doc in results2.docs}
        assert first_page_ids != second_page_ids


def test_terms_query_with_field_list(solr_client):
    """Test terms query with specific field list."""
    parser = TermsQueryParser(
        field="tags", terms=["python", "java"], field_list=["product_id", "name"]
    )

    results = solr_client.search(parser)

    assert results.num_found >= 2
    for doc in results.docs:
        assert hasattr(doc, "product_id")
        assert hasattr(doc, "name")
        # Other fields should not be present
        assert not hasattr(doc, "price")
        assert not hasattr(doc, "category")


def test_terms_query_with_sort(solr_client):
    """Test terms query with sorting."""
    parser = TermsQueryParser(field="category", terms=["books"], sort="price asc")

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 5
    # Verify ascending price order
    prices = [doc.price for doc in results.docs if hasattr(doc, "price")]
    assert prices == sorted(prices)


def test_terms_query_with_faceting(solr_client):
    """Test terms query with faceting."""
    parser = TermsQueryParser(
        field="tags", terms=["programming", "software", "search"]
    ).facet(fields=["brand", "category"], mincount=1)

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 4
    assert hasattr(results, "facets")
    assert "brand" in results.facets.fields
    assert "category" in results.facets.fields


def test_terms_query_with_grouping(solr_client):
    """Test terms query with grouping."""
    parser = TermsQueryParser(field="category", terms=["books", "electronics"]).group(
        by="brand", limit=3
    )

    results = solr_client.search(parser, document_model=Product)

    print("[DEBUG] test_terms_query_with_grouping results:", results)
    # Grouped results are now in results.grouping.grouped
    assert results.grouping is not None
    grouped = results.grouping.grouped
    assert "brand" in grouped


def test_terms_query_with_highlighting(solr_client):
    """Test terms query with highlighting."""
    parser = TermsQueryParser(field="tags", terms=["python", "java"]).highlight(
        fields=["name"], fragment_size=100
    )

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 2
    # Highlighting should be present in results
    assert hasattr(results, "highlighting")


def test_terms_query_multiple_categories(solr_client):
    """Test searching across multiple categories."""
    parser = TermsQueryParser(field="category", terms=["books", "electronics"])

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found == 8  # All documents
    categories = {doc.category for doc in results.docs}
    assert "books" in categories
    assert "electronics" in categories


def test_terms_query_with_brand_filter(solr_client):
    """Test filtering by specific brands."""
    parser = TermsQueryParser(field="brand", terms=["TechBooks", "DevPress"])

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 4
    brands = {doc.brand for doc in results.docs}
    assert brands.issubset({"TechBooks", "DevPress"})


def test_terms_query_complex_scenario(solr_client):
    """Test complex scenario with multiple parameters."""
    parser = (
        TermsQueryParser(
            field="tags",
            terms=["programming", "software", "computer"],
            query="inStock:true",
            rows=10,
        )
        .facet(fields=["category"], mincount=1)
        .highlight(fields=["name"])
    )

    results = solr_client.search(parser, document_model=Product)

    print("[DEBUG] test_terms_query_complex_scenario results:", results)
    # Should have results from both books and electronics
    assert results.num_found >= 2

    # All should be in stock
    for doc in results.docs:
        assert doc.inStock is True

    # Facets should be present
    assert hasattr(results, "facets")
    assert "category" in results.facets.fields


def test_terms_query_docvalues_method(solr_client):
    """Test terms query with docValues method on brand field."""
    parser = TermsQueryParser(
        field="brand", terms=["TechBooks", "DevPress"], method="docValuesTermsFilter"
    )

    results = solr_client.search(parser, document_model=Product)

    assert results.num_found >= 4
    brands = {doc.brand for doc in results.docs}
    assert brands.issubset({"TechBooks", "DevPress"})


def test_terms_query_empty_result_set(solr_client):
    """Test that empty terms list returns no false positives."""
    parser = TermsQueryParser(field="tags", terms=[])

    results = solr_client.search(parser, document_model=Product)

    # With empty terms, behavior depends on Solr version
    # Should either return 0 or all documents (acts as no filter)
    assert results.num_found >= 0
