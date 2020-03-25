"""
Testing out dash-bootstrap-components for layout and design.
"""
# -*- coding: utf-8 -*-

"""
Building up phenology library app component by component based on the Dash
tutorials rather than specifically a Dash example.

"""
import pathlib

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import os
import copy
import pandas as pd
import dash_bootstrap_components as dbc

# Multi-dropdown options
from controls import NLCD_2011, DOYLIST, DOYDICT, DOY2DATETIMEDICT

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# Load mapbox token
# mapboxAccessToken = os.getenv('MAPBOX_TOKEN')
# if not mapboxAccessToken:
mapboxAccessToken = open(".mapbox_token", 'r').read()
mapboxAccessToken = mapboxAccessToken.replace('"', '')

# Load datasets: Converted in external script from goeJSON to csv with x,y columns
df = pd.read_csv(DATA_PATH.joinpath('lcDF.csv'), index_col=0, parse_dates=['variable'])
df.columns = ['PointID', 'LC_code', 'reference_date', 'ndvi', 'lon', 'lat']

# Create controls
lc_options = [
    {"label": str(NLCD_2011[lc_class]), "value": str(lc_class)} for lc_class in NLCD_2011
]

controls = dbc.Row(
    [
        dbc.Col(
            dbc.FormGroup(
                [
                    dbc.Label('Select Landcover Class'),
                    dcc.Dropdown(
                        id='lc-class-dropdown',
                        options=lc_options,
                        value='41',
                        placeholder='Select a land cover class',
                    ),
                ]
            ),
            width = 6,
        ),
        dbc.Col(
            dbc.FormGroup(
                [
                    dbc.Label('Filter by Day Of Year (DOY), or select in lineplot'),
                    dcc.Slider(
                        id='doy-slider',
                        min=1, # See controls.py DOYLIST for values
                        max=353,
                        step=16,
                        value=177,
                        tooltip={'always_visible': True, 'placement':
                            'topLeft'},
                        updatemode='drag'
                    ),
                ]
            ),
            width=6,
        ),
    ],
    form=True,
)

layout = dict(
    autosize=True,
    height=600,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=0,
        r=0,
        b=35,
        t=45
    ),
    hovermode="closest",
    # plot_bgcolor='#fffcfc',
    # paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    title='Points represent center of sampling buffers',
    mapbox=dict(
        accesstoken=mapboxAccessToken,
        style="light",
        center=dict(
            lon=-74.296787,  # manually copied from the csv lon
            lat=41.12487  # manually copied from the csv lat
        ),
        zoom=6,
    )
)

def gen_map(map_data):
    return {
        "data": [
            {
                'type': 'scattermapbox',
                'lat': list(map_data['lat']),
                'lon': list(map_data['lon']),
                'text': list(map_data['ndvi']),
                'mode': 'markers',
                'name': map_data['PointID'],
                'marker': {
                    'size': 6,
                    'opacity': 0.7,
                    'color': map_data['ndvi']
                }
            }
        ],
        "layout": layout
    }

app.layout = dbc.Container(
    [
        html.H1('Phenology Library'),
        html.P('Interactive mapping of NDVI signatures by land cover class.'),
        # html.Hr(), #adds lines above and below the H1 and P
        dbc.Row(
            [
                dbc.Col(dcc.Graph(
                        id='map-graph',
                        # animate=True,
                    ),
                    md=12),
            ],
            align='center',
        ),
        controls,
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='ndvi-by-doy-scatter'), md=6),
            ],
            align='left',
        ),
    ],
    fluid=True,
)

#     # Scatterplot
#     html.Div(
#         [
#             html.Div(
#                 [
#                     dcc.Graph(
#                         id='ndvi-by-doy-scatter',
#                         figure={
#                             'data': [
#                                 dict(
#                                     type='scattergl',
#                                     x=df[df['LC_code'] == 41]['reference_date'],
#                                     y=df[df['LC_code'] == 41]['ndvi'],
#                                     text=df[df['LC_code'] == 41]['PointID'],
#                                     mode='markers',
#                                     opacity=0.7,
#                                     marker={
#                                         'size': 9,
#                                         'line': {'width': 0.5,
#                                                  'color': 'white'}
#                                     },
#                                     name=41
#                                 )  # for i in df.LC_code.unique()
#                             ],
#                             'layout': dict(
#                                 xaxis={'title': 'Day Of Year (DOY)'},
#                                 yaxis={'title': 'NDVI'},
#                                 # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#                                 legend={'x': 0, 'y': 1},
#                                 hovermode='closest'
#                             )
#                         }
#                     ),
#                 ],
#                 className='six columns',
#                 style={'margin-top': '30'}
#             )
#         ],
#         className='row'
#     ),
#     ],
#
# )

# TODO: see https://community.plotly.com/t/preserving-ui-state-like-zoom-in-dcc-graph-with-uirevision/15793
#   about preventing auto resetting map with input (e.g., slider) change.
@app.callback(
    Output('map-graph', 'figure'),
    [Input('lc-class-dropdown', 'value'),
     Input('doy-slider', 'value')]
)
def map_selection(lc_ID, doy):
    dff = df.copy()
    # Landcover class filter
    dff = dff[dff['LC_code'] == int(lc_ID)]
    # DOY filter
    dff = dff[dff['reference_date' ] == DOY2DATETIMEDICT[doy]]
    return gen_map(dff)

# @app.callback(
#     Output('ndvi-by-doy-scatter', 'figure'),
#     [Input('lc-class-dropdown', 'value'),
#      ]
# )

if __name__ == '__main__':
    app.run_server(debug=True)