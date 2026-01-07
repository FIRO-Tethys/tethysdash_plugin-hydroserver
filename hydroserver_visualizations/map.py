from intake.source import base
from tethysapp.tethysdash.plugin_helpers import LayerConfigurationBuilder
from .util import login_to_hydroserver


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
        "endpoint": "text",
        "api_key": "text"
    }
    visualization_tags = [
        "hydroserver",
        "map"
    ]
    visualization_description = ""
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Map"
    visualization_type = "map"
    visualization_attribution = "hydroserverpy"
    _user_parameters = []

    def __init__(self, endpoint, api_key=None, metadata=None, **kwargs):
        self.endpoint = endpoint
        self.api_key = api_key
        super(Map, self).__init__(metadata=metadata)

    def read(self):
        hs_api = login_to_hydroserver(self.endpoint, self.api_key)
        if self.api_key:
            workspaces = hs_api.workspaces.list(fetch_all=True)
            features = []
            for workspace in workspaces.items:
                features.extend([thing_to_geojson_feature(thing) for thing in workspace.things])
        else:
            public_things = hs_api.things.list(fetch_all=False)
            features = [thing_to_geojson_feature(thing) for thing in public_things.items]
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
