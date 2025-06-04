import dash
from dash import html, Output, Input, dash_table
import dash_leaflet as dl

# Exemplo
points = [
    {"name": "Point A", "lat": 40.7128, "lon": -74.0060, "info": "New York"},
    {"name": "Point B", "lat": 34.0522, "lon": -118.2437, "info": "Los Angeles"},
    {"name": "Point C", "lat": 41.8781, "lon": -87.6298, "info": "Chicago"},
    {"name": "Point D", "lat": 47.6062, "lon": -122.3321, "info": "Seattle"},
]

app = dash.Dash(__name__)

def make_markers(data):
    return [
        dl.Marker(position=(p["lat"], p["lon"]), children=dl.Tooltip(p["name"]))
        for p in data
    ]

app.layout = html.Div([
    dl.Map(center=(39, -98), zoom=4, children=[
        dl.TileLayer(),
        dl.LayerGroup(id="marker-layer", children=make_markers(points)),
        dl.FeatureGroup([
            dl.EditControl(
                id="edit-control",
                draw={"rectangle": True, "polyline": False, "polygon": False,
                      "circle": False, "marker": False, "circlemarker": False},
                edit={"edit": False}
            )
        ])
    ], style={'width': '100%', 'height': '500px'}),

    html.Hr(),

    dash_table.DataTable(
        id='points-table',
        columns=[
            {"name": "Name", "id": "name"},
            {"name": "Latitude", "id": "lat"},
            {"name": "Longitude", "id": "lon"},
            {"name": "Info", "id": "info"}
        ],
        data=points,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
    )
])

@app.callback(
    Output("points-table", "data"),
    Output("marker-layer", "children"),
    Input("edit-control", "geojson")
)
def filter_points(geojson):
    if not geojson or not geojson.get("features"):
        return points, make_markers(points)

    coords = geojson["features"][0]["geometry"]["coordinates"][0]
    lats = [pt[1] for pt in coords]
    lons = [pt[0] for pt in coords]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)

    # Trocar filtro abaixo - consultar kdtree
    filtered = [
        p for p in points
        if lat_min <= p["lat"] <= lat_max and lon_min <= p["lon"] <= lon_max
    ]

    return filtered, make_markers(filtered)

if __name__ == '__main__':
    app.run(debug=True)
