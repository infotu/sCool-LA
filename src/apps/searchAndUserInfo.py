# -*- coding: utf-8 -*-

"""
Created on Feb 23 08:10:00 2023

@author: zangl
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
# global constants
dfStudentDetails                      = studentGrouped.dfStudentDetails
getStudentsOfLearningActivity         = studentGrouped.getStudentsOfLearningActivity



def getUserInfoLayout():
    return advancedUserInfo.layout

#----------------------------------------------------------------------------------------------------------------------
# top navbar layout - used in main layout (located in index.py)
navbar = html.Div(
    html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Learning Analytics Web Application", id = "navbar-la-heading", className="navbar-heading"),
                        ],
                        width = 4,
                    ),
                    dbc.Col(
                        dbc.Row(
                            [
                                dbc.Col(dcc.Dropdown(id = "search-dropdown", options = [], placeholder = "Search...", optionHeight = 38, style={"font-size": "1.1em", "z-index": 15})),
                                dbc.Col(dbc.Button("Search", id = "navbar-search-button", color = "primary", className = "navbar-searchbutton"), width = "auto")
                            ],
                            id = "search-bar-row",
                            align = "center"
                        ),
                        width = 4,
                    ),
                    dbc.Col([html.Div(constants.navbarTestUsername, id = "navbar-username", className="navbar-username"), html.Div(constants.navbarTestRole, id = "navbar-userrole", className="navbar-userrole")], id = "user-info-name-role", width = 3),
                    dbc.Col(html.Button(html.Img(src="/assets/user-icon.png", height="50px"), id = "user-info-button", className = "welcome-button"), id = "user-info-icon", width = 1),
                ],
                align="center"
            ),
            dbc.Modal(
                    [
                        dbc.ModalHeader("User Information"),
                        dbc.ModalBody(children = getUserInfoLayout()),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="user-info-button-close", className="ml-auto")
                        ),
                    ],
                    id="user-info-modal",
                    className = "c-modal-large"
            )
        ],
        className="page-navbar-margin-top"
    ),
    className="page-navbar"
)


@app.callback(
    Output("user-info-modal", "is_open"),
    [Input("user-info-button", "n_clicks"), Input("user-info-button-close", "n_clicks")],
    [State("user-info-modal", "is_open")],
)
def toggle_user_info_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



@app.callback(
    Output("search-dropdown", "options"),
    Input("search-dropdown", "search_value")
)
def update_options(searchInput):

    if searchInput:
        options = []
        classesUserHasAccessTo = classes.getUserLAOptions()
        for entry in classesUserHasAccessTo:
            className = entry["label"]
            classId = entry["value"]
            options.append({"label": className, "value": ("class-" + str(classId)), "title": "Class"})

            studentsUserHasAccessTo = studentGrouped.getStudentsOfLearningActivity(classId)
            dfstudents = dfStudentDetails[dfStudentDetails["StudentId"].isin(studentsUserHasAccessTo)][['StudentId', 'Name']].drop_duplicates(subset=['StudentId'], keep='first')
            for index, row in dfstudents.iterrows():
                studentName = row['Name']
                studentId = row['StudentId']

                options.append({"label": studentName, "value": ("student-" + str(classId) + "-" + str(studentId)), "title": "Student - " + className})
        
        options.append({"label": "Tutorial", "value": "tab-menu-link-2",  "title": "Tab"})
        options.append({"label": "Classes",  "value": "tab-menu-link-3",  "title": "Tab"})
        options.append({"label": "Students", "value": "tab-menu-link-4",  "title": "Tab"})
        options.append({"label": "Custom",   "value": "tab-menu-link-5",  "title": "Tab"})

        return [x for x in options if searchInput in x["label"]]
    else:
        raise PreventUpdate


@app.callback(
    Output("search-dropdown", "value"),
    Input("navbar-search-button", "n_clicks"),
    State("search-dropdown", "search_value")
)
def update_options(n_clicks, searchValue):

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        if triggered_id == 'navbar-search-button.n_clicks':
            return searchValue
    return dash.no_update


#----------------------------------------------------------------------------------------------------------------------
# Callback function to manipulate 
# params:   pathname         (string) - string containing the pathname (used only as trigger)
# returns:  
@app.callback([Output("navbar-username", "children"), Output("navbar-userrole", "children")], 
              [Input("url", "pathname")],
)
def setMenuClassOnLogin(pathname):   
    
    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated  :

        isUserAdmin = False    
        
        userDB = studentGrouped.getUserFromUserId(current_user.id)
        
        if  userDB is not None:        
            if userDB['IsAdmin']:
                isUserAdmin = True

        if isUserAdmin:
            return [userDB['UserName'], constants.navbarAdmin]
        else:
            return [userDB['UserName'], constants.navbarEducator]
            
    return [dash.no_update, dash.no_update]


app.clientside_callback(
    ClientsideFunction('ui', 'executeSearchRequest'),
    Output("navbar-la-heading", "children"),
    Input("search-dropdown", "value")
)