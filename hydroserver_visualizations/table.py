from intake.source import base
import pandas as pd
import plotly.graph_objects as go
import json
from .util import login_to_hydroserver


class Table(base.DataSource):
    container = "python"
    version = "0.0.1"
    name = "hydroserver_table"
    visualization_description = ("Hydroserver datastreams table")
    visualization_tags = ["hydroserver", "datastreams", "table"]
    visualization_args = {
        "endpoint": "text",
        "api_key": "text",
        "thing_uid": "text"
    }
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Datastreams Table"
    visualization_type = "plotly"
    visualization_attribution = "hydroserverpy"
    _user_parameters = []

    def __init__(self, endpoint, thing_uid, api_key=None, metadata=None):
        self.endpoint = endpoint
        self.thing_uid = thing_uid
        self.api_key = api_key
        super(Table, self).__init__(metadata=metadata)

    def read(self):
        columns = ['uid', 'name', 'is_private', 'is_visible']
        hs_api = login_to_hydroserver(endpoint=self.endpoint, api_key=self.api_key)
        streams = hs_api.datastreams.list(thing=self.thing_uid)
        streams_dict = [{col: stream.__getattribute__(col) for col in columns} for stream in streams.items]

        def estimate_col_width(series, min_width=50, scale=7):
            max_len = max(len(str(v)) for v in series)
            return max(min_width, max_len * scale)

        df = pd.DataFrame(streams_dict)
        plot = go.Figure(data=[go.Table(
                header=dict(
                    values=columns,
                ),
                cells=dict(
                    values=[df[col] for col in df.columns],
                ),
                columnwidth=[estimate_col_width(df[col]) for col in df.columns],
            ),
        ])
        plot.update_layout(
            margin=dict(l=20, r=20, t=20, b=20)
        )
        return json.loads(plot.to_json())
