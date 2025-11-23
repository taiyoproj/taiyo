import random
import string
import time

from taiyo import SolrClient, SolrDocument, SolrError
from taiyo.schema import SolrField
from taiyo.parsers import StandardParser

SOLR_URL = "http://localhost:8983/solr"


class Article(SolrDocument):
    id: str
    title: str
    content: str


def _setup_mlt_collection(client: SolrClient) -> tuple[str, list[Article]]:
    """Create a disposable collection seeded with documents for MLT tests."""
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    collection = f"test_taiyo_mlt_{suffix}"

    client.create_collection(collection, num_shards=1, replication_factor=1)
    time.sleep(1)

    client.set_collection(collection)

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
    ]

    for field in fields:
        client.add_field(field)

    time.sleep(1)

    docs = [
        Article(
            id=f"mlt-article-{suffix}-1",
            title="Understanding Solr relevance for related articles",
            content=(
                "Solr more like this uses TF-IDF similarity to recommend related "
                "articles about search relevance tuning and boosting strategies."
            ),
        ),
        Article(
            id=f"mlt-article-{suffix}-2",
            title="Designing recommendation widgets with Solr",
            content=(
                "Building recommendation widgets with Solr more like this similarity "
                "analysis to recommend related content, tune relevance feedback, and "
                "apply boosting controls for discovery experiences."
            ),
        ),
        Article(
            id=f"mlt-article-{suffix}-3",
            title="Exploring coastal hiking destinations",
            content=(
                "Plan coastal hiking adventures with trail safety tips, wildlife "
                "sightings, and packing guidance for beachside excursions."
            ),
        ),
        Article(
            id=f"mlt-article-{suffix}-4",
            title="Deploying Solr more like this for news portals",
            content=(
                "News portals rely on Solr more like this similarity scoring to "
                "recommend related stories, encourage exploration, and guide user "
                "journeys through curated collections."
            ),
        ),
    ]

    client.add(docs)
    client.commit()
    time.sleep(1)

    return collection, docs


def test_more_like_this_returns_related_articles():
    """Exercise MoreLikeThis configuration against a live Solr collection."""
    with SolrClient(SOLR_URL) as client:
        collection = ""
        try:
            collection, docs = _setup_mlt_collection(client)
            target_id = docs[0].id

            parser = StandardParser(query=f"id:{target_id}", rows=1).more_like_this(
                fields=["title", "content"],
                min_term_freq=1,
                min_doc_freq=1,
                max_query_terms=20,
                boost=True,
                match_include=False,
            )

            response = client.search(parser, document_model=Article)
            assert response.status == 0

            extra = response.extra or {}

            assert response.more_like_this is not None
            assert target_id in response.more_like_this

            similar_docs = response.more_like_this[target_id].docs
            assert similar_docs

            similar_ids = {doc.id for doc in similar_docs}
            expected_ids = {docs[1].id, docs[3].id}

            assert similar_ids & expected_ids
            assert docs[2].id not in similar_ids
            assert docs[0].id not in similar_ids

            params = (extra.get("responseHeader") or {}).get("params", {})
            assert params.get("mlt") == "true"

            mlt_fields_raw = params.get("mlt.fl")
            if isinstance(mlt_fields_raw, str):
                tokens = {
                    token.strip()
                    for token in mlt_fields_raw.replace(",", " ").split()
                    if token.strip()
                }
            elif isinstance(mlt_fields_raw, list):
                tokens = {str(token) for token in mlt_fields_raw}
            else:
                tokens = set()
            assert {"title", "content"}.issubset(tokens)
        finally:
            if collection:
                try:
                    client.delete_collection(collection)
                except SolrError as exc:
                    if getattr(exc, "status_code", None) != 404:
                        raise


def test_more_like_this_interesting_terms_details():
    """Ensure interesting terms are returned when requesting detailed output."""
    with SolrClient(SOLR_URL) as client:
        collection = ""
        try:
            collection, docs = _setup_mlt_collection(client)
            target_id = docs[0].id

            parser = StandardParser(query=f"id:{target_id}", rows=1).more_like_this(
                fields=["content"],
                min_term_freq=1,
                min_doc_freq=1,
                max_query_terms=10,
                interesting_terms="details",
                match_include=False,
            )

            response = client.search(parser, document_model=Article)
            assert response.status == 0

            result = response.more_like_this[target_id]
            interesting_terms = result.interesting_terms
            assert interesting_terms

            tokens: set[str] = set()
            if isinstance(interesting_terms, dict):
                for term in interesting_terms:
                    _, _, keyword = term.partition(":")
                    tokens.add(keyword or term)
            elif isinstance(interesting_terms, list):
                for term in interesting_terms:
                    if isinstance(term, str):
                        _, _, keyword = term.partition(":")
                        tokens.add(keyword or term)
                    elif isinstance(term, dict):
                        for key in term:
                            _, _, keyword = key.partition(":")
                            tokens.add(keyword or key)

            assert tokens & {"similarity", "recommend", "search", "related"}

            assert response.more_like_this is not None
            assert target_id in response.more_like_this
            similar_docs = result.docs
            assert similar_docs

            similar_ids = {doc.id for doc in similar_docs}
            assert docs[0].id not in similar_ids
        finally:
            if collection:
                try:
                    client.delete_collection(collection)
                except SolrError as exc:
                    if getattr(exc, "status_code", None) != 404:
                        raise
