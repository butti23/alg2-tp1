import dash
from dash import html, Output, Input, dash_table
import dash_leaflet as dl
import tp

points = tp.parse_csv('dados.csv')
tree = tp.KdTree(points)
center_x, center_y = (-19.9062135,-43.9650108)
points = []

def point_to_dict(p):
    return {
        "name": p.data.name,
        "date": p.data.date,
        "has_license": "Sim" if p.data.has_license else "Não" if p.data.has_license is not None else "",
        "addr": p.data.address
    }

app = dash.Dash(__name__)

def make_markers(data):
    return [
        dl.Marker(position=(p.y, p.x), children=dl.Tooltip(p.data.name))
        for p in data
    ]

app.layout = html.Div([
    dl.Map(center=(center_x, center_y), zoom=13, children=[
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
            {"name": "Nome", "id": "name"},
            {"name": "Data de início", "id": "date"},
            {"name": "Possui alvará", "id": "has_license"},
            {"name": "Endereço", "id": "addr"}
        ],
        data=[point_to_dict(p) for p in points],
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
    ll = tp.Point(None, lon_min, lat_min)
    ur = tp.Point(None, lon_max, lat_max)
    filtered = tree.search(tp.Rectangle(ll, ur))

    return [point_to_dict(p) for p in filtered], make_markers(filtered)

if __name__ == '__main__':
    app.run(debug=True)
