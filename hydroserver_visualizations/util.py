from hydroserverpy import HydroServer
from tethysapp.tethysdash.exceptions import VisualizationError


def login_to_hydroserver(endpoint, api_key=None):
    try:
        hs_api = HydroServer(host=endpoint, apikey=api_key)
    except Exception as e:
        raise VisualizationError("Error connecting to HydroServer: ", e)
    return hs_api
