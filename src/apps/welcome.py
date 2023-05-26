# -*- coding: utf-8 -*-

"""
Created on   May 18 14:30:00 2023

@authors: zangl
"""

import math
import json
from datetime import date
import dateutil.parser
from dateutil.parser import parse

import flask
import dash_table
from dash.exceptions import PreventUpdate
import plotly.figure_factory as ff
import chart_studio.plotly as py
from plotly import graph_objs as go
import os
import util
import numpy as np
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL

from flask_login import logout_user, current_user, LoginManager, UserMixin

from app import app, login_manager, User
import constants
from data import studentGrouped

from apps import settings
import util
import subprocess


search_bar_clicks_old = 0
user_information_clicks_old = 0
website_tab_clicks_old = 0
info_icon_clicks_old = 0


layout = html.Div([

    html.H1(constants.welcomeHeading, className = "welcome-heading"),
    html.P(constants.welcomeText, className = "welcome-paragraph"),

    html.H2(constants.tutorialHeading, className = "welcome-heading-tutorial"),
    html.P(constants.tutorialText, className = "welcome-paragraph"),

    html.Button(html.H3(constants.searchBarHeading, className = "welcome-heading-smaller"), id = "search-bar-heading-button", className = "welcome-button"),
    html.P(constants.searchBarText, id = "search-bar-text", className = "welcome-paragraph"),

    html.Button(html.H3(constants.userInformationHeading, className = "welcome-heading-smaller"), id = "user-information-heading-button", className = "welcome-button"),
    html.P(constants.userInformationText, className = "welcome-paragraph"),

    html.Button(html.H3(constants.websiteTabsHeading, className = "welcome-heading-smaller"), id = "website-tabs-heading-button", className = "welcome-button"),
    html.P(constants.websiteTabsText, className = "welcome-paragraph"),
    html.P(constants.tutorialTabText, className = "welcome-paragraph"),
    html.P(constants.classesTabText, className = "welcome-paragraph"),
    html.P(constants.studentsTabText, className = "welcome-paragraph"),
    html.P(constants.customTabText, className = "welcome-paragraph"),

    html.Button(html.H3(constants.infoIconHeading, className = "welcome-heading-smaller"), id = "info-icon-heading-button", className = "welcome-button"),
    html.P(constants.infoIconText, className = "welcome-paragraph")

    ], id = "welcome-div", className = "m_medium"
)


@app.callback(
    [Output("search-bar-row", "className"), Output("user-info-name-role", "className"), Output("user-info-icon", "className"),
     Output("menu-main-nav", "className"), Output("menu-modal-help-div", "className"), Output("welcome-div", "className")],
    [Input("search-bar-heading-button", "n_clicks"), Input("user-information-heading-button", "n_clicks"),
     Input("website-tabs-heading-button", "n_clicks"), Input("info-icon-heading-button", "n_clicks"),
     Input("welcome-div", "n_clicks")]
)
def update_highlighted_div(search_bar_clicks, user_information_clicks, website_tab_clicks, info_icon_clicks, other_clicks):
    
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']
    
    if search_bar_clicks and "search-bar-heading-button" in triggered_id:
        return ["welcome-highlight", "", "", "", "menu-modal-help", "m_medium"]
    elif user_information_clicks and "user-information-heading-button" in triggered_id:
        return ["", "welcome-highlight", "welcome-highlight", "", "menu-modal-help", "m_medium"]
    elif website_tab_clicks and "website-tabs-heading-button" in triggered_id:
        return ["", "", "", "welcome-highlight", "menu-modal-help", "m_medium"]
    elif info_icon_clicks and "info-icon-heading-button" in triggered_id:
        return ["", "", "", "", "welcome-highlight menu-modal-help", "m_medium"]
    return ["", "", "", "", "menu-modal-help", "m_medium"]
