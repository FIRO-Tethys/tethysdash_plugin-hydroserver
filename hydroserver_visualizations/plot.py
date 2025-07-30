from intake.source import base
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from hydroserverpy import HydroServer


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
        "datastream_uid": "text"
    }
    visualization_group = "Hydroserver"
    visualization_label = "Hydroserver Plot"
    visualization_type = "plotly"
    _user_parameters = []

    def __init__(self, datastream_uid, metadata=None):
        self.datastream_uid = datastream_uid
        super(Plot, self).__init__(metadata=metadata)

    def read(self):
        # Get a datastream
        hs_api = HydroServer(host='https://playground.hydroserver.org')
        datastream = hs_api.datastreams.get(uid=self.datastream_uid)

        # Get observations of a datastream between two timestamps
        # observations_df = datastream.get_observations(
        #     start_time=datetime(year=2023, month=1, day=1),
        #     end_time=datetime(year=2023, month=12, day=31)
        # )

        # Get observations all observations of a datastream
        df_full_observation = datastream.get_observations(fetch_all=True)
        df_full_observation['date'] = pd.to_datetime(df_full_observation['timestamp'])
        df_full_observation['date'] = df_full_observation['date'].dt.tz_convert(None)
        df_full_observation['value'] = df_full_observation['value'].clip(lower=0)
        print("type: ", df_full_observation['date'].dtype)
        print("date: ", df_full_observation['date'].head())
        plot = go.Figure()
        plot.add_trace(go.Scatter(
            x=df_full_observation['date'].to_list(),
            y=df_full_observation['value'],
            mode='lines',
            name='Observations',
            # marker=dict(color='rgb(0, 166, 255)')
        ))
        plot.update_layout(
            xaxis_title='Date',
            yaxis_title='Value',
            xaxis=dict(tickformat='%Y-%m-%d', tickangle=45)
        )
        data = []
        for trace in plot.data:
            trace_json = trace.to_plotly_json()
            if "x" in trace_json and isinstance(trace_json["x"], np.ndarray):
                trace_json["x"] = trace_json["x"].tolist()
            if "y" in trace_json and isinstance(trace_json["y"], np.ndarray):
                trace_json["y"] = trace_json["y"].tolist()
            data.append(trace_json)
        layout = plot.to_plotly_json()["layout"]
        config = {"autosizable": True, "responsive": True}
        return {"data": data, "layout": layout, "config": config}
