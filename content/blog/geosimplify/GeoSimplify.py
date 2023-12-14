import requests
import geopandas as gpd
import topojson as tp


url = "https://www.geoboundaries.org/api/current/gbOpen/PHL/ADM1/"
url = "https://www.geoboundaries.org/api/current/gbOpen/DEU/ADM1/"
api_response = requests.get(url)

metadata = api_response.json()
DEUboundaries = gpd.read_file(metadata["gjDownloadURL"])


# Convert the GeoDataFrame to a TopoJSON format
topojson_data = tp.Topology(DEUboundaries,
                            prequantize = 1000000)

topojson_simplified_30m = topojson_data.toposimplify(
    epsilon = tolerance_degrees_30m, 
    simplify_algorithm   = 'vw', 
    simplify_with        = 'simplification', 
    prevent_oversimplify = True
)