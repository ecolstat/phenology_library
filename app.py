# -*- coding: utf-8 -*-
"""
Testing a Dash app based on the
- SONYC Dash App https://github.com/amyoshino/SONYC-Dash-App,
- Oil and Gas Dash sample app https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-oil-and-gas

NOTE: Just for testing, and many options (e.g., color ramps, components,
etc.) don't etc.) don't really make sense with the phenology data. This will
be expanded to more appropriate functionality in the future.
"""

import pickle
import copy
import pathlib
import math
import datetime as dt

import dash
from dash.dependencies import Input, Output, State  # , Event
# NOTE: Event was removed from dash. See https://community.plot.ly/t/dash-events-button/19791 if needed
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import plotly
from plotly import graph_objs as go
from plotly.graph_objs import *
from flask import Flask
import pandas as pd
import numpy as np
import os
import copy

# Multi-dropdown options
from controls import NLCD_2011, DOYLIST

# Get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()

# TODO: Verify this is the correct way to provide external stylesheets vs an asset folder
app = dash.Dash(__name__, external_stylesheets=['https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'])

server = app.server

# Load mapbox token
mapbox_token = os.getenv('MAPBOX_TOKEN')
if not mapbox_token:
    token = open(".mapbox_token").read()

# Load datasets
df = pd.read_csv(DATA_PATH.joinpath('lcDF.csv'), index_col=0, parse_dates=['variable'])
df.columns = ['PointID', 'LC_code', 'reference_date', 'ndvi', 'lon', 'lat']

layout = dict(
    autosize=True,
    height=500,
    font=dict(color="#191A1A"),
    titlefont=dict(color="#191A1A", size='14'),
    margin=dict(
        l=35,
        r=35,
        b=35,
        t=45
    ),
    hovermode="closest",
    plot_bgcolor='#fffcfc',
    paper_bgcolor='#fffcfc',
    legend=dict(font=dict(size=10), orientation='h'),
    title='Points represent center of sampling buffers',
    mapbox=dict(
        accesstoken=mapbox_token,
        style="light",
        center=dict(
            lon=-74.362539,  # manually copied from the csv lon
            lat=41.987256  # manually copied from the csv lat
        ),
        zoom=10,
    )
)

# Create controls
lc_options = [
    {"label": str(NLCD_2011[lc_class]), "value": str(lc_class)} for lc_class in NLCD_2011
]

doy_to_ref_date = dict(zip(DOYLIST, df.reference_date.unique()))

# TODO: if the previous variable works, delete this.
# # Controls (dropdowns)
# group = ['All']
# group = group + df.LC_code.unique()
# group_class = [{'label': str(item),
#                 'value': str(item)}
#                for item in group]


# Creating layouts for datatable
layout_right = copy.deepcopy(layout)
layout_right['height'] = 300
layout_right['margin-top'] = '20'
layout_right['font-size'] = '12'

# Define min and max LC codes for color mapping
lc_max = df['LC_code'].max()
lc_min = df['LC_code'].min()


# TODO: This should change to discrete color map for categorical LC classes
# Components style
def color_scale(df, selected_row_indices=[]):
    color = []
    max_class = lc_max
    min_class = lc_min
    for row in df['LC_code']:
        scale = (row - lc_min) / (lc_max - lc_min)
        if scale <= 0.06:
            color.append("#26EC04")
        elif scale <= 0.12:
            color.append("#8FDB44")
        elif scale <= 0.18:
            color.append("#A5D643")
        elif scale <= 0.24:
            color.append("#B8D343")
        elif scale <= 0.30:
            color.append("#B8D343")
        elif scale <= 0.36:
            color.append("#DBCD44")
        elif scale <= 0.42:
            color.append("#E1CD44")
        elif scale <= 0.48:
            color.append("#F0CB45")
        elif scale <= 0.54:
            color.append("#F3C644")
        elif scale <= 0.60:
            color.append("#F2BE41")
        elif scale <= 0.66:
            color.append("#F0AE3D")
        elif scale <= 0.72:
            color.append("#EFA73B")
        elif scale <= 0.78:
            color.append("#EE9F39")
        elif scale <= 0.84:
            color.append("#ED8934")
        elif scale <= 0.90:
            color.append("#E95729")
        else:
            color.append("#FD0101")
    for i in selected_row_indices:
        color[i] = '#1500FA'
    return color


def gen_map(df):
    # groupby returns a dictionary mapping the values of the first field
    # 'classification' onto a list of record dictionaries with that
    # classification value.
    return {
        "data": [
            {
                "type": "scattermapbox",
                "lat": list(df['lat']),
                "lon": list(df['lon']),
                "text": list(df['LC_code']),
                "mode": "markers",
                "name": list(df['PointID']),
                "marker": {
                    "size": 6,
                    "opacity": 0.7,
                    "color": color_scale(df)
                }
            }
        ],
        "layout": layout
    }

# Layout
app.layout = html.Div(
    [
    # Title - Row
    html.Div(
        [
            html.H1(
                'Phenology Library',
                style={'font-family': 'Helvetica',
                       "margin-top": "25",
                       "margin-bottom": "0"},
                className='eight columns',
            ),
            # html.Img(
            #     src="http://static1.squarespace.com/static/546fb494e4b08c59a7102fbc/t/591e105a6a496334b96b8e47/1497495757314/.png",
            #     className='two columns',
            #     style={
            #         'height': '9%',
            #         'width': '9%',
            #         'float': 'right',
            #         'position': 'relative',
            #         'padding-top': 10,
            #         'padding-right': 0
            #     },
            # ),
            html.P(
                'Interactive mapping of NDVI signatures by land cover class.',
                style={'font-family': 'Helvetica',
                       "font-size": "120%",
                       "width": "80%"},
                className='eight columns',
            ),
        ],
        className='row'
    ),
    # Selectors
    html.Div(
        [
            html.Div(
                [
                    html.P('Filter by Day Of Year (or select DOY in line plot):',
                        className = 'control_label',
                    ),
                    # TODO: This might not be the best since DOYs could change with different satellite data
                    dcc.Slider(
                        id='doy-slider',#  0,16,32,48,64,80,96,112,128,144,160,176,
                                        # 192,208,224,240,256,272,288,304,320,336,352
                        min=0,
                        max=352,
                        step=16,
                        value=176,
                        className='dcc_control',
                    ),
                ],
                className='six columns',
                style={'margin-top': '10'}
            ),
            html.Div(
                [
                    html.P('Filter by Land Cover Class:',
                        className='control_label',
                    ),
                    dcc.Dropdown(
                        id='lc_classes',
                        options=lc_options,
                        multi=True,
                        value=[lc_options[i]['value'] for i in [7, 8, 9, 11]],
                        placeholder="Select a land cover class",
                        className='dcc_control',
                    )
                ],
                className='six columns',
                style={'margin-top': '8'}
            ),
        ],
        className='row'
    ),

    # Table + Timeseries plot
    html.Div(
        [
            html.Div(
                [
                    dt.DataTable(
                        columns=[{'name': i, 'id': i, 'selectable': True} for i in df.columns],
                        data=df.to_dict('records'),
                        filter_action='native',
                        column_selectable='single',
                        row_selectable='multi',
                        sort_action='native',
                        sort_mode='multi',
                        selected_columns=[],
                        selected_rows=[],
                        page_action='native',
                        page_size=15,
                        id='datatable',
                    ),
                ],
                # style=layout_right,
                style={'margin-top': '20'},
                className="four columns"
            ),

            html.Div(
                [
                    dcc.Graph(id="timeplot",
                    ),
                ],
                style={'margin-top': '20'},
                # style=layout_right,
                className="four columns"
            ),

        ],
        className="row"
    ),

    # Map
     html.Div(
        [
            dcc.Graph(id='map-graph',
                        animate=True,
            ),
        ],
         className = "twelve columns"
    ),
],)# className='ten columns offset-by-one')

# Callbacks and functions
@app.callback(
    Output('map-graph', 'figure'),
    [Input('datatable', 'selected_rows'),
     Input('datatable', 'selected_row_ids')])
def map_selection(selected_rows, selected_row_ids):
    aux = pd.DataFrame(selected_rows)
    temp_df = aux.iloc[selected_row_ids, :]
    if len(selected_row_ids) == 0:
        return gen_map(aux)
    return gen_map(temp_df)


@app.callback(
    Output('datatable', 'style_data_conditional'),
    [Input('datatable', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]


@app.callback(
    Output('datatable', 'selected_rows'),
    [dash.dependencies.Input('doy-slider', 'value'),
    dash.dependencies.Input('lc_classes', 'value')])
def update_selected_row_indices(doy, lc_class):
    df_aux = df.copy()

    # # DOY filter
    # df_aux = df_aux[df_aux['']]


if __name__ == '__main__':
    app.run_server(debug = True)
