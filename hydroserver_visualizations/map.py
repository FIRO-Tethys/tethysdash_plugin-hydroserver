from intake.source import base
from hydroserverpy import HydroServer
from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder


def thing_to_geojson_feature(thing):
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [thing.longitude, thing.latitude]
        },
        "properties": {
            "elevation_m": thing.elevation_m,
            "elevation_datum": thing.elevation_datum,
            "state": thing.state,
            "county": thing.county,
            "country": thing.country,
            "name": thing.name,
            "description": thing.description,
            "sampling_feature_type": thing.sampling_feature_type,
            "sampling_feature_code": thing.sampling_feature_code,
            "site_type": thing.site_type,
            # "tags": thing.tags,
            # "photos": thing.photos,
            "data_disclaimer": thing.data_disclaimer,
            "is_private": thing.is_private,
            "uid": str(thing.uid)
        }
    }


class Map(base.DataSource):
    container = "python"
    version = "0.0.1"
    name = "hydroserver_map"
    visualization_args = {
        "endpoint": "text"
    }  # TODO make hydroserver endpoint a text input
    visualization_tags = [
        "hydroserver",
        "map"
    ]
    visualization_description = ""
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Map"
    visualization_type = "map"
    _user_parameters = []

    def __init__(self, endpoint, metadata=None, **kwargs):
        self.endpoint = endpoint
        super(Map, self).__init__(metadata=metadata)

    def read(self):
        hs_api = HydroServer(host=self.endpoint)
        public_things = hs_api.things.list()
        features = [thing_to_geojson_feature(thing) for thing in public_things]
        geojson = {
            "type": "FeatureCollection",
            "name": "Hydroservers",
            "crs": {
                "type": "name",
                "properties": {
                    "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
                }
            },
            "features": features
        }
        builder = LayerConfigurationBuilder(name="Hydroservers", layer_source="GeoJSON")
        builder.set_geojson(geojson)
        builder.add_attribute_variable("uid", "thing_uid", "Hydroservers")
        map_config = {
            "baseMap": "https://server.arcgisonline.com/arcgis/rest/services/World_Topo_Map/MapServer",
            "layerControl": True,
            "layers": [builder.build()]
        }
        return map_config
