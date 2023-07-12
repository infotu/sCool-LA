# -*- coding: utf-8 -*-

"""
Created on Thu May 10:25:00 2023

@authors: zangl
"""


#----------------------------------------------------------------------------------------------------------------------
# imports
import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate

from flask_login import current_user

from app import app
import constants
from data import studentGrouped

from apps import settings, classes, advancedUserInfo
import subprocess


#----------------------------------------------------------------------------------------------------------------------
# advancedUserInfo tab layout - used in main layout (located in index.py)
layout = [
    html.Div(children = [], id = "user-info-div")
]


#----------------------------------------------------------------------------------------------------------------------
# Callback function to update user info if user info gets opened.
# params:   is_open     (bool) - bool indicaating wether user info is open or not
# returns:  html.Div() containing user info
@app.callback(Output("user-info-div", "children"),
              Input("user-info-modal", "is_open")
)
def update_user_info(is_open):
    if is_open:
        if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and  current_user.is_authenticated:
            
            role_string = ""
            if current_user.isAdmin:
                role_string = "Admin"
            else:
                role_string = "Educator"

            dfUserInfo = studentGrouped.getUserDetails(current_user.id)

            email = ""

            for index, row in dfUserInfo.iterrows():
                email = row["Email"]

            userInfo = html.Div(
                children = [
                    html.Div("Username: " + f"{current_user.name}", style = {"font-size": "1.5em"}),
                    html.Div("Userrole: " + f"{role_string}",       style = {"font-size": "1.5em"}),
                    html.Div("E-Mail: "   + f"{email}",             style = {"font-size": "1.5em"})
                ]
            )

            return userInfo

    return [html.Div("No Data Found")]