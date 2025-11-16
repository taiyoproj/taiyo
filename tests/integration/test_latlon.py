from taiyo import SolrClient, SolrError
import time
from .utils import create_collection_with_schema, COLLECTION, LatLonDoc, SOLR_URL
from taiyo.parsers import GeoFilterQueryParser, BoundingBoxQueryParser


def test_latlonpointspatialfield_geofilt_and_bbox():
    with SolrClient(SOLR_URL) as client:
        create_collection_with_schema(client)
        docs = [
            LatLonDoc(id="1", name="Alpha", latlon="35.0,139.0"),
            LatLonDoc(id="2", name="Beta", latlon="35.1,139.1"),
            LatLonDoc(id="3", name="Gamma", latlon="36.0,140.0"),
        ]
        client.set_collection(COLLECTION)
        client.add(docs)
        client.commit()
        time.sleep(1)

        geofilt = GeoFilterQueryParser(
            spatial_field="latlon",
            center_point=[35.05, 139.05],
            radial_distance=20.0,  # km
        )
        res = client.search(geofilt, document_model=LatLonDoc)
        assert res.status == 0
        names = {d.name for d in res.docs}
        assert "Alpha" in names and "Beta" in names

        bbox = BoundingBoxQueryParser(
            spatial_field="latlon",
            center_point=[35.05, 139.05],
            radial_distance=20.0,
        )
        res2 = client.search(bbox, document_model=LatLonDoc)
        assert res2.status == 0
        names2 = {d.name for d in res2.docs}
        assert "Alpha" in names2 and "Beta" in names2
        try:
            client.delete_collection(COLLECTION)
        except SolrError as e:
            if getattr(e, "status_code", None) == 404:
                pass
            else:
                raise
