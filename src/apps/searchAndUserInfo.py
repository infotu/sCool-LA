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
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from flask_login import current_user

from app import app
import constants
from data import studentGrouped

from apps import settings, classes
import subprocess

#----------------------------------------------------------------------------------------------------------------------
# global constants
dfStudentDetails                        = studentGrouped.dfStudentDetails


# ignore for now
def getUserRole():
    username = "brrr"

    print(current_user.get_id())

    return username


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
                                dbc.Col(dcc.Dropdown(id = "search-dropdown", options = [], placeholder = "", optionHeight = 48, style={"height": "48px", "font-size": "1.4em"})),
                                dbc.Col(dbc.Button("Search", color = "primary", className = "navbar-searchbutton"), width = "auto")
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
                options.append({"label": studentName, "value": ("student-" + str(studentId)), "title": "Student"})
        
        options.append({"label": "Classes",  "value": "tab-menu-link-3",  "title": "Tab"})
        options.append({"label": "Students", "value": "tab-menu-link-4",  "title": "Tab"})
        options.append({"label": "Custom",   "value": "tab-menu-link-5",  "title": "Tab"})

        return [x for x in options if searchInput in x["label"]]
    else:
        raise PreventUpdate
    
# dash.no_update
@app.callback(
    [Output("navbar-la-heading", "children"), Output("menu-link-3", "n_clicks"),
     Output("menu-link-4", "n_clicks"), Output("menu-link-5", "n_clicks")],
    Input("search-dropdown", "value"),
    State("menu-link-3", "n_clicks"), State("menu-link-4", "n_clicks"),
    State("menu-link-5", "n_clicks")
)
def update_content(newValue, n_clicks_classes, n_clicks_students, n_clicks_custom):

    if newValue:
        newValueSplitList = newValue.split('-')
        if(newValueSplitList[0] == "tab"):
            if(newValue == "tab-menu-link-3"): #click Classes Button
                subprocess.Popen(["echo", "PERFORM BUTTONCLICK CLASSES"])
                return [newValue, (n_clicks_classes + 1 if n_clicks_classes else 1), n_clicks_students, n_clicks_custom]
            elif(newValue == "tab-menu-link-4"): #click Students Button
                subprocess.Popen(["echo", "PERFORM BUTTONCLICK STUDENTS"])
                return [newValue, n_clicks_classes, (n_clicks_students + 1 if n_clicks_students else 1), n_clicks_custom]
            elif(newValue == "tab-menu-link-5"): #click Custom Button
                subprocess.Popen(["echo", "PERFORM BUTTONCLICK CUSTOM"])
                return [newValue, n_clicks_classes, n_clicks_students, (n_clicks_custom + 1 if n_clicks_custom else 1)]
            
        return [newValue, n_clicks_classes, n_clicks_students, n_clicks_custom]
    else:
        raise PreventUpdate
