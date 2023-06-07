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

from apps import settings, classes
import subprocess

external_scripts = [
    {
        'src': '/assets/clickClassesButton.js'
    }
]

#----------------------------------------------------------------------------------------------------------------------
# global constants
dfStudentDetails                      = studentGrouped.dfStudentDetails
getStudentsOfLearningActivity         = studentGrouped.getStudentsOfLearningActivity


"""
#----------------------------------------------------------------------------------------------------------------------
# Function to check wether student is in a class
# params:   StudentId       (int) - integer containing student ID
#           schoolKey       (int) - integer containing class ID
# returns:  Boolean stating if student is in class or not
def isStudentInClass(studentId, classId) :
    try:
        groupStudents = getStudentsOfLearningActivity(classId)
        if not studentId in groupStudents:
            return False
        return True

    except Exception as e:
        subprocess.Popen(['echo', 'isStudentInClass Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)
"""


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
                    dbc.Col([html.Div(constants.navbarTestUsername, className="navbar-username"), html.Div(constants.navbarTestRole, className="navbar-userrole")], id = "user-info-name-role", width = 3),
                    dbc.Col(html.Img(src="/assets/user-icon.png", height="50px"), id = "user-info-icon", width = 1),
                ],
                align="center"
            )
        ],
        className="page-navbar-margin-top"
    ),
    className="page-navbar"
)


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

                options.append({"label": studentName, "value": ("student-" + str(classId) + "-" + str(studentId)), "title": "Student"})
        
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


app.clientside_callback(
    ClientsideFunction('ui', 'executeSearchRequest'),
    Output("navbar-la-heading", "children"),
    Input("search-dropdown", "value")
)