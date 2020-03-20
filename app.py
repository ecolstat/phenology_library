# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output, State #, Event
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


app = dash.Dash(__name__)
server = app.server

# Load mapbox token
mapbox_token = os.getenv('MAPBOX_TOKEN')
if not mapbox_token:
    token = open(".mapbox_token").read()

# Load datasets



# if __name__ == '__main__':
#     app.run_server(debug = True)