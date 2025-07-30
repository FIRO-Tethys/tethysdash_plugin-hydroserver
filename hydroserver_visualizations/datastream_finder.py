from intake.source import base
from hydroserverpy import HydroServer


class DatastreamFinder(base.DataSource):
    container = "python"
    version = "0.0.4"
    name = "hydroserver_datastream_finder"
    visualization_tags = ["hydroserver", "datastreams", "variable input"]
    visualization_description = (
        "Provides all available datastreams for a selected hydroserver"
    )
    visualization_args = {
        "thing_uid": "text",
    }
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Datastreams Finder"
    visualization_type = "variable_input"

    def __init__(self, thing_uid, metadata=None):
        self.thing_uid = thing_uid
        super().__init__(metadata=metadata)

    def read(self):
        """
        Read the data for the datastream from the hydroserver service.
        """
        hs_api = HydroServer(host='https://playground.hydroserver.org')
        streams = hs_api.datastreams.list(thing=self.thing_uid)
        streams_dropdown = [
            {'label': str(stream.uid), 'value': str(stream.uid)}
            for stream in streams
        ]
        return {
            "variable_name": "Datastream",
            "initial_value": None,
            "variable_options_source": streams_dropdown,
        }
