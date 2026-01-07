from intake.source import base
import pandas as pd
import json
import plotly.graph_objects as go
from .util import login_to_hydroserver


class Plot(base.DataSource):
    container = "python"
    version = "0.0.1"
    name = "hydroserver_plot"
    visualization_tags = [
        "hydroserver",
        "plots"
    ]
    visualization_description = (
        "The plot of timeseries for the selected datastream"
    )
    visualization_args = {
        "endpoint": "text",
        "datastream_uid": "text",
        "api_key": "text"
    }
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Plot"
    visualization_type = "plotly"
    visualization_attribution = "hydroserverpy"
    _user_parameters = []

    def __init__(self, endpoint, datastream_uid, api_key=None, metadata=None):
        self.endpoint = endpoint
        self.datastream_uid = datastream_uid
        self.api_key = api_key
        super(Plot, self).__init__(metadata=metadata)

    def read(self):
        hs_api = login_to_hydroserver(endpoint=self.endpoint, api_key=self.api_key)
        datastream = hs_api.datastreams.get(uid=self.datastream_uid)
        # Get observations of a datastream
        observation = datastream.get_observations(fetch_all=True)
        df_full_observation = observation.dataframe
        df_full_observation['date'] = pd.to_datetime(df_full_observation['phenomenon_time'])
        df_full_observation['date'] = df_full_observation['date'].dt.tz_convert(None)
        df_full_observation['value'] = df_full_observation['result'].clip(lower=0)

        plot = go.Figure()
        plot.add_trace(go.Scatter(
            x=df_full_observation['date'].to_list(),
            y=df_full_observation['value'],
            mode='lines',
            name='Observations',
        ))
        plot.update_layout(
            xaxis_title='Date',
            yaxis_title='Value',
            xaxis=dict(tickformat='%Y-%m-%d', tickangle=45)
        )

        return json.loads(plot.to_json())
