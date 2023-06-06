# -*- coding: utf-8 -*-

"""
Created on   May 18 14:30:00 2023

@authors: zangl
"""

#----------------------------------------------------------------------------------------------------------------------
# imports
import dash
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
import constants


#----------------------------------------------------------------------------------------------------------------------
# welcome tab layout - used in main layout (located in index.py)
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


#----------------------------------------------------------------------------------------------------------------------
# Callback function to show/hide a red highlight border on certain components based on user interaction. (clicking on headlines)
# params:   searchBarClicks         (int) - number of clicks on a button with id = "search-bar-heading-button"
#           userInformationClicks   (int) - number of clicks on a button with id = "user-information-heading-button"
#           websiteTabClicks        (int) - number of clicks on a button with id = "website-tabs-heading-button"
#           infoIconClicks          (int) - number of clicks on a button with id = "info-icon-heading-button"
#           otherClicks             (int) - number of clicks on a html.Div with id = "welcome-div"
# returns:  list containing classNames (CSS styling) of various web app components
@app.callback(
    [Output("search-bar-row", "className"), Output("user-info-name-role", "className"), Output("user-info-icon", "className"),
    Output("menu-main-nav", "className"), Output("menu-modal-help-div", "className")],
    [Input("search-bar-heading-button", "n_clicks"), Input("user-information-heading-button", "n_clicks"),
    Input("website-tabs-heading-button", "n_clicks"), Input("info-icon-heading-button", "n_clicks"),
    Input("welcome-div", "n_clicks")]
)
def show_hide_red_highlights(searchBarClicks, userInformationClicks, websiteTabClicks, infoIconClicks, otherClicks):

    ctx = dash.callback_context
    if ctx.triggered:
        triggeredId = ctx.triggered[0]['prop_id']

        if searchBarClicks and "search-bar-heading-button" in triggeredId:
            return ["welcome-highlight", "", "", "", "menu-modal-help"]
        elif userInformationClicks and "user-information-heading-button" in triggeredId:
            return ["", "welcome-highlight", "welcome-highlight", "", "menu-modal-help"]
        elif websiteTabClicks and "website-tabs-heading-button" in triggeredId:
            return ["", "", "", "welcome-highlight", "menu-modal-help"]
        elif infoIconClicks and "info-icon-heading-button" in triggeredId:
            return ["", "", "", "", "welcome-highlight menu-modal-help"]
    return ["", "", "", "", "menu-modal-help"]


#----------------------------------------------------------------------------------------------------------------------
# Callback function to make sure red highlights are not visible when user chooses other tabs then welcome tab.
# params:   pathname         (str) - string containing current pathname
# returns:  list containing style properties of various web app components
@app.callback(
    [Output("search-bar-row", "style"), Output("user-info-name-role", "style"), Output("user-info-icon", "style"),
    Output("menu-main-nav", "style"), Output("menu-modal-help-div", "style")],
    [Input("url", "pathname")]
)
def hide_red_highlights(pathname):

    if pathname != "/Welcome":
        return [{"border": "0px"}, {"border": "0px"}, {"border": "0px"}, {"border": "0px"}, {"border": "0px"}]
    else:
        return [{}, {}, {}, {}, {}]
