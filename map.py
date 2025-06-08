import dash
from dash import html, Output, Input, dash_table
import dash_leaflet as dl
import kdtree

CENTER_COORDS = (-19.9062135, -43.9650108)
ZOOM_LEVEL = 13
MAP_HEIGHT = '500px'

points = kdtree.parse_csv('dados.csv')
tree = kdtree.KdTree(points)
bares_info = kdtree.parse_bares_completos_csv('bares.csv')
points = []

def point_to_dict(p: kdtree.Point) -> dict:
    return {
        "name": p.data.name,
        "date": p.data.date,
        "has_license": "Sim" if p.data.has_license else "Não" if p.data.has_license is not None else "",
        "addr": p.data.address
    }

def get_bar_extra_info(point: kdtree.Point) -> str:
    bar_id = getattr(point.data, "id_ativ_econ_estabelecimento", None)
    info = bares_info.get(bar_id)
    if info:
        return (
            f"<b>{info['Nome']}</b><br>"
            f"<a href=\"{info['Link Detalhes']}\" target=\"_blank\">Ver detalhes</a><br>"
            f"<b>Prato:</b> {info['Nome Petisco']}<br>"
            f"<b>Descrição:</b> {info['Descricao']}<br>"
            f"<b>Endereço:</b> {info['Endereco']}<br>"
            f"<img src=\"{info['Link Imagem']}\" width=\"150\">"
        )
    return point.data.name

def make_markers(data: list) -> list:
    return [
        dl.Marker(
            position=(p.y, p.x),
            children=dl.Tooltip(content=get_bar_extra_info(p), direction="top", permanent=False)
        )
        for p in data
    ]

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Buscador de bares e restaurantes BH"),

    dl.Map(
        center=CENTER_COORDS,
        zoom=ZOOM_LEVEL,
        children=[
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
        ],
        style={'width': '100%', 'height': MAP_HEIGHT}
    ),

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
        return [point_to_dict(p) for p in points], make_markers(points)

    coords = geojson["features"][0]["geometry"]["coordinates"][0]
    lats = [pt[1] for pt in coords]
    lons = [pt[0] for pt in coords]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)

    ll = kdtree.Point(None, lon_min, lat_min)
    ur = kdtree.Point(None, lon_max, lat_max)
    filtered = tree.search(kdtree.Rectangle(ll, ur))

    return [point_to_dict(p) for p in filtered], make_markers(filtered)

if __name__ == '__main__':
    app.run()