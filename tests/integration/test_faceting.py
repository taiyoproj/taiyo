from taiyo import SolrClient, SolrError
import time
from .utils import Store, create_collection_with_schema, COLLECTION, SOLR_URL
from taiyo.params.configs.facet import FacetParamsConfig
from taiyo.params.configs.highlight import HighlightMethod
from taiyo.parsers import StandardParser


def test_faceting_and_highlighting():
    with SolrClient(SOLR_URL) as client:
        create_collection_with_schema(client)
        docs = [
            Store(id="1", name="Alpha", vector=[0.0, 0.0]),
            Store(id="2", name="Alpha", vector=[1.0, 1.0]),
            Store(id="3", name="Beta", vector=[2.0, 2.0]),
        ]
        client.set_collection(COLLECTION)
        client.add(docs)
        client.commit()
        time.sleep(1)

        parser = StandardParser(query="name:Alpha", rows=10)
        parser.facet = FacetParamsConfig(fields=["name"])
        from taiyo.params.configs.highlight import HighlightParamsConfig

        parser.highlight = HighlightParamsConfig(
            method=HighlightMethod.UNIFIED,
            fields=["name"],
        )
        res = client.search(parser, document_model=Store)
        assert res.status == 0
        assert res.num_found >= 1
        extra = getattr(res, "extra", {})
        assert "facet_counts" in extra or "facets" in extra
        params = extra.get("responseHeader", {}).get("params", {})
        assert params.get("highlight") == "true"
        assert "name" in params.get("hl.fl", "")
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
