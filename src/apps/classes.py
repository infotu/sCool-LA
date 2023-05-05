# -*- coding: utf-8 -*-
"""
Created on Mar 14 10:25:00 2023

@author: zangl
"""

import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


from flask_login import logout_user, current_user, LoginManager, UserMixin

from app import app, login_manager, User
import constants
from data import studentGrouped

from apps import settings


@login_manager.user_loader
def load_user(usernameOrId):
    userDB = studentGrouped.getUserFromUserId(usernameOrId)
    
    if  userDB is not None:        
        return User(userDB['UserName'], userDB['Id'], active = True, isAdmin = userDB['IsAdmin'], securityStamp = userDB['SecurityStamp'] )


def getUserLA():
    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated:
        currentUserId = current_user.id
        
        if  current_user.isAdmin : 
            return studentGrouped.dfLearningActivityDetails[constants.GROUPBY_FEATURE].unique().astype(str)
        else:
            return studentGrouped.dfLearningActivityDetails[studentGrouped.dfLearningActivityDetails['User_Id'] == 
                                                            currentUserId][constants.GROUPBY_FEATURE].unique().astype(str)


    return studentGrouped.dfLearningActivityDetails[constants.GROUPBY_FEATURE].unique()


def getUserLAOptions():
    userLA = getUserLA()
    
    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated:
        return studentGrouped.BuildOptionsLA( [ groupId for groupId in  userLA  ] , isAdmin =  current_user.isAdmin ) 
    
    return studentGrouped.BuildOptionsLA( [ groupId for groupId in  userLA  ] , isAdmin = True  )


def getUserLAOptionsStrings():
    options_strings = []
    
    for option in user_LA_options:
        options_strings.append(option["label"])

    return options_strings


user_LA_options = getUserLAOptions()
user_LA_options_strings = getUserLAOptionsStrings()
user_LA_buttons = [html.Button(option, id = f"button-{i}") for i, option in enumerate(user_LA_options_strings)]

layout = html.Div(
    [
        html.H1('Select a Class'),
        html.Div(user_LA_buttons, className='option-buttons'),
        html.H1(id="test-text")
    ],
    style = {'margin': '30px'}
)

@app.callback(
    Output("test-text", "children"),
    [Input(f"button-{i}", 'n_clicks') for i in range(len(user_LA_options_strings))]
)
def update_output(*args):
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('-')[1]
        button_index = int(button_id.split('.')[0])
        button_label = user_LA_options_strings[button_index]
        return button_label
    return "nothing pressed"

