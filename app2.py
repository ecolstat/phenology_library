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

# Multi-dropdown options
from controls import NLCD_2011, DOYLIST

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

# Load datasets: Converted in external script from goeJSON to csv with x,y columns
df = pd.read_csv(DATA_PATH.joinpath('lcDF.csv'), index_col=0, parse_dates=['variable'])
df.columns = ['PointID', 'LC_code', 'reference_date', 'ndvi', 'lon', 'lat']

# Create controls
lc_options = [
    {"label": str(NLCD_2011[lc_class]), "value": str(lc_class)} for lc_class in NLCD_2011
]


# Load mapbox token
mapboxAccessToken = open(".mapbox_token", 'r').read()
mapboxAccessToken = mapboxAccessToken.replace('"', '')

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

def gen_map(df):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.
    return {
        "data": [
            {
                "type": "scattermapbox",
                "lat": list(df[df['LC_code'] == 41]['lat']),
                "lon": list(df[df['LC_code'] == 41]['lon']),
                "text": list(df[df['LC_code'] == 41]['ndvi']),
                "mode": "markers",
                "name": 41,
                "marker": {
                    # "size": 6,
                    "opacity": 0.7,
                    "color": df[df['LC_code'] == 41]['ndvi']
                }
            }
        ],
        "layout": layout
    }


app.layout = html.Div(
    [
    html.Div(
        [
            html.H1(
                'Phenology Library',
                style={'font-family': 'Helvetica',
                       "margin-top": "25",
                       "margin-bottom": "0"},
                className='eight columns',
                # This is an html 'class' in Dash
            ),

            html.P(
                'Interactive mapping of NDVI signatures by land cover class.',
                style={'font-family': 'Helvetica',
                       "font-size": "120%"},
                      # "width": "230%"},
                className='eight columns',
            ),
        ],
        className='row'
    ),

    html.Div(
        [
            # Map
            html.Div(
                [
                    dcc.Graph(
                        id='map-graph',
                        animate=True,
                        figure=gen_map(df)
                    ),
                ]
            )
        ],
        className='row'
    ),

    # Selectors
    html.Div(
        [
            html.Div(
                [
                    html.P('Select land cover class:',
                           className='control_label',
                           ),
                    dcc.Dropdown(
                        id='lc_classes',
                        options=lc_options,
                        value='41',
                        placeholder='Select a land cover class',
                        className='dcc_control',
                    ),
                ],
                className='six columns',
                style={'margin-top': '8'}
            ),

            html.Div(
                [
                    html.P('Filter by Day Of Year (or select DOY in line plot):',
                        className='control_label',
                    ),
                    # TODO: This might not be the best since DOYs could change with different satellite data
                    dcc.Slider(
                        id='doy-slider',
                        # 0,16,32,48,64,80,96,112,128,144,160,176,
                        # 192,208,224,240,256,272,288,304,320,336,352
                        min=0,
                        max=352,
                        step=16,
                        value=176,
                        className='dcc_control',
                    ),
                    html.Div(id='slider-output-container'),
                ],
                className='six columns',
                style={'margin-top': '10'}
            ),
        ],
        className='row'
    ),
    # Scatterplot
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id='ndvi-by-doy-scatter',
                        figure={
                            'data': [
                                dict(
                                    type='scattergl',
                                    x=df[df['LC_code'] == 41]['reference_date'],
                                    y=df[df['LC_code'] == 41]['ndvi'],
                                    text=df[df['LC_code'] == 41]['PointID'],
                                    mode='markers',
                                    opacity=0.7,
                                    marker={
                                        'size': 9,
                                        'line': {'width': 0.5,
                                                 'color': 'white'}
                                    },
                                    name=41
                                )  # for i in df.LC_code.unique()
                            ],
                            'layout': dict(
                                xaxis={'title': 'Day Of Year (DOY)'},
                                yaxis={'title': 'NDVI'},
                                # margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                                legend={'x': 0, 'y': 1},
                                hovermode='closest'
                            )
                        }
                    ),
                ],
                className='six columns',
                style={'margin-top': '30'}
            )
        ],
        className='row'
    ),
    ],

)

# Slider display callback
@app.callback(
    Output('slider-output-container', 'children'),
    [Input('doy-slider', 'value')])
def update_output(value):
    # TODO: Look into formatting this with markdown
    return 'You have selected "{}"'.format(value)


if __name__ == '__main__':
    app.run_server(debug=True)