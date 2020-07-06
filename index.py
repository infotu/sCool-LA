# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 18:04:10 2020

@author: tilan
"""

# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import flask
import chart_studio.plotly as py
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly import graph_objs as go
import math

from app import app
from apps import overview, groupDetails

from sidebar import sidebar


import constants

import studentGroupedGeneral



#--------------------- school selection START ----------------------
GroupSelector_options = studentGroupedGeneral.GroupSelector_options 
#--------------------- school selection END ----------------------




def generateControlCard():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card-index",
        children=[
            html.P("Select Group"),
            dcc.Dropdown(
                id = "group-selector-main-index",
                options = GroupSelector_options,
            ),
        ],
    )


content = html.Div(
        children=[
        
    dbc.Navbar(
        children = [
                dbc.Row([
                        dbc.Col(
                            # Left column
                            html.Div(
                                id="row-control-main-index",
                                className="",
                                children=[ generateControlCard() ]
                                + [
                                    html.Div(
                                        ["initial child"], id="row-control-main-output-clientside-index", style={"display": "none"}
                                    )
                                ],
                            ),
                    ),
                ],
                    className = "row w-100" ),
                
#                dbc.Row(
#                    [
#                        dbc.Col(  html.Div([
#                            html.H1("sCool Data Analysis")
#                            ,  html.Div('Student perfomance in sCool.')
#                        ]),  
#                            width = { "size" : 12} ,
#                            style = {'background-color' : '#3aaab2',
#                                     'font-size' : 'initial'   }
#                        ),
#                    ],
#                    className = "row w-100" )
        ],
        id="page-topbar", 
        sticky          = "top" ,
        light           = True ,
        style           = {
                 'background-color' : '#3aaab2',
                 'font-size' : 'initial',
                 'color'  : 'white'  }
    ),

    # Page content
    html.Div(id="page-content", className="", style={"marginTop": "5rem"}),
    
    ],
        
    id="page-main", style =  constants.CONTENT_STYLE )


app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/Overview"]:
        return overview.layout
    elif pathname == "/Details":
        return groupDetails.layout
    elif pathname == "/page-2/1":
        return html.P("Oh cool, this is page 2.1!")
    elif pathname == "/page-2/2":
        return html.P("No way! This is page 2.2!")
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )



#if __name__ == "__main__":
#    app.run_server(port=8888, debug=True)

if __name__ == "__main__":
    app.run_server(debug=True)