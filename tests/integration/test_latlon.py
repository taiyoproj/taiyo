import random
import string
import time
from taiyo import SolrClient, SolrError, SolrDocument
from taiyo.schema import SolrFieldType, SolrField, SolrFieldClass
from taiyo.parsers import GeoFilterQueryParser

SOLR_URL = "http://localhost:8983/solr"
_rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
COLLECTION = f"test_taiyo_latlon_{_rand}"


class LatLonDoc(SolrDocument):
    name: str
    latlon: str


def test_latlonpointspatialfield_geofilt_and_bbox():
    """End-to-end test for spatial search with lat/lon field type."""
    with SolrClient(SOLR_URL) as client:
        # Create collection
        try:
            client.create_collection(COLLECTION, num_shards=1, replication_factor=1)
        except Exception:
            pass  # Collection may already exist

        time.sleep(1)
        client.set_collection(COLLECTION)

        # Define and add spatial field type
        latlon_field_type = SolrFieldType(
            name="latlon_point",
            solr_class=SolrFieldClass.LATLON_POINT_SPATIAL,
        )

        try:
            client.add_field_type(latlon_field_type)
        except Exception:
            pass  # Field type may already exist

        # Define and add fields
        fields = [
            SolrField(name="name", type="string", stored=True),
            SolrField(name="latlon", type="latlon_point", indexed=True, stored=True),
        ]

        for field in fields:
            try:
                client.add_field(field)
            except SolrError:
                pass  # Field may already exist

        time.sleep(1)

        # Add test documents
        docs = [
            LatLonDoc(name="Alpha", latlon="35.0,139.0"),
            LatLonDoc(name="Beta", latlon="35.1,139.1"),
            LatLonDoc(name="Gamma", latlon="36.0,140.0"),
        ]
        client.add(docs)
        client.commit()
        time.sleep(1)

        # Test geofilt query
        geofilt = GeoFilterQueryParser(
            spatial_field="latlon",
            center_point=[35.05, 139.05],
            radial_distance=20.0,  # km
        )
        res = client.search(geofilt, document_model=LatLonDoc)
        assert res.status == 0
        assert all(isinstance(doc, LatLonDoc) for doc in res.docs)
        names = {d.name for d in res.docs}
        assert "Alpha" in names and "Beta" in names

        # Test bbox query
        bbox = GeoFilterQueryParser(
            spatial_field="latlon",
            center_point=[35.05, 139.05],
            radial_distance=20.0,
            filter_type="bbox",
        )
        res2 = client.search(bbox, document_model=LatLonDoc)
        assert res2.status == 0
        assert all(isinstance(doc, LatLonDoc) for doc in res2.docs)
        names2 = {d.name for d in res2.docs}
        assert "Alpha" in names2 and "Beta" in names2

        # Cleanup
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
