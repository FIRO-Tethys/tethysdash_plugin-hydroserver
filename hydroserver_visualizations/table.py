from intake.source import base
import pandas as pd
import plotly.graph_objects as go
import json
from hydroserverpy import HydroServer


class Table(base.DataSource):
    container = "python"
    version = "0.0.1"
    name = "hydroserver_table"
    visualization_description = ("Hydroserver datastreams table")
    visualization_tags = ["hydroserver", "datastreams", "table"]
    visualization_args = {
        "thing_uid": "text"
    }
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Datastreams Table"
    visualization_type = "plotly"
    visualization_attribution = "hydroserverpy"
    _user_parameters = []

    def __init__(self, thing_uid, metadata=None):
        self.thing_uid = thing_uid
        super(Table, self).__init__(metadata=metadata)

    def read(self):
        columns = ['uid', 'is_private', 'is_visible']
        hs_api = HydroServer(host='https://playground.hydroserver.org')
        streams = hs_api.datastreams.list(thing=self.thing_uid)
        streams_dict = [{col: stream.__getattribute__(col) for col in columns} for stream in streams.items]
        df = pd.DataFrame(streams_dict)
        plot = go.Figure(data=[go.Table(
            header=dict(
                values=columns,
                # fill_color='rgba(0, 0, 0, 0)'
            ),
            cells=dict(
                values=[df[col] for col in df.columns],
            ))
        ])
        return json.loads(plot.to_json())
