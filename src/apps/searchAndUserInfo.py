# -*- coding: utf-8 -*-
"""
Created on Feb 23 08:10:00 2023

@author: zangl
"""
import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction


from flask_login import current_user

from app import app
import constants
from data import studentGrouped

from apps import settings

# in this file the top bar, where user information is displayed, is managed
# also users are able to open their own detail menu where information about the user is displayed
# and the users can change their username, password and so on

# ignore for now
def getUserRole():
    username = "brrr"

    print(current_user.get_id())

    return username

navbar = html.Div(
    html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Learning Analytics Web Application", className="navbar-heading"),
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(dbc.Input(type="text", placeholder="Search...", className="navbar-searchinput")),
                                dbc.Col(dbc.Button("Search", color="primary", className="navbar-searchbutton"), width="auto")
                            ],
                            align="center"
                        ),
                        width=4,
                    ),
                    dbc.Col([html.Div(constants.navbarTestUsername, className="navbar-username"), html.Div(constants.navbarTestRole, className="navbar-userrole")], width=3),
                    dbc.Col(html.Img(src="/assets/user-icon.png", height="50px"), width=1),
                ],
                align="center"
            )
        ],
        className="page-navbar-margin-top"
    ),
    className="page-navbar"
)