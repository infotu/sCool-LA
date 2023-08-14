# -*- coding: utf-8 -*-
"""
Created on   Jun 11 18:04:10 2020
Reworked on  Mar 14 10:25:00 2023

@authors: tilan, zangl
"""

# -*- coding: utf-8 -*-
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from flask_login import logout_user, current_user

from app import app, server, login_manager, User
from apps import groups, custom, home, sidebar, login, searchAndUserInfo, classes, students, tutorial
from data import studentGrouped

import constants
import subprocess



#--------------------- school selection START ----------------------
GroupSelector_options   = studentGrouped.GroupSelector_options 
dfUser                  =  studentGrouped.dfUser
#--------------------- school selection END ----------------------



@login_manager.user_loader
def load_user(usernameOrId):
    userDB = studentGrouped.getUserFromUserId(usernameOrId)
    
    if  userDB is not None:
        subprocess.Popen(["echo", "____________SHIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIT_______________"])
        subprocess.Popen(["echo", f"str({usernameOrId})"])
        return User(userDB['UserName'], userDB['Id'], active = True, isAdmin = userDB['IsAdmin'], securityStamp = userDB['SecurityStamp'])


content = html.Div(
        children=[
            # Page content
            html.Div(id="page-content", className="page-content ")],   
    id="page-main", 
    className = "  page-main "
)
   

app.layout = html.Div([dcc.Location(id="url"), searchAndUserInfo.navbar, sidebar.sidebar, content,
                       ],
                       className = constants.THEME
                       )


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    
    if pathname == '/login':
        if current_user and not current_user.is_authenticated:
            return login.layout
    elif pathname == '/logout':
        if current_user and current_user.is_authenticated:
            logout_user()
        

    if current_user and current_user.is_authenticated:
        if pathname in ["/Home"]:
            return home.layout
        if pathname in ["/Groups"]:
            return groups.layout
        elif pathname  in ["/", "/Welcome"]:
            return tutorial.layout
        elif pathname  in ["/Classes"]:
            return classes.layout
        elif pathname == "/Custom":
            return custom.layout
        elif pathname == "/Students":
            return students.layout

        return tutorial.layout

    
    # DEFAULT NOT LOGGED IN: /login
    return login.layout



@app.callback(
    Output("page-sidebar", "className"),
    [
        Input("url", "pathname")
    ],
     state=[ State(component_id='page-sidebar', component_property='className')
                ]
)
def show_hide_sidebar(pathname, currentClasses):
    currentClassesS = set()
    
    if not (None is currentClasses) and not ('' == currentClasses) :
        currentClassesS = set(currentClasses.split(' '))

    currentClassesS.discard('hidden')
    
    if  pathname in  ["/login"]    or   not  ( current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated) :
        currentClassesS.add('hidden')
        
    return  ' '.join(currentClassesS) 



@app.callback(
    Output("page-navbar-searchengine-userinfo", "className"),
    [
        Input("url", "pathname")
    ],
     state=[ State(component_id='page-navbar-searchengine-userinfo', component_property='className')
                ]
)
def show_hide_sidebar(pathname, currentClasses):
    currentClassesS = set()
    
    if not (None is currentClasses) and not ('' == currentClasses) :
        currentClassesS = set(currentClasses.split(' '))

    currentClassesS.discard('hidden')
    
    if  pathname in  ["/login"]    or   not  ( current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated) :
        currentClassesS.add('hidden')
        
    return  ' '.join(currentClassesS) 



# For Debug Mode
#if __name__ == "__main__":
#    app.run_server(port=8080, debug=True)

# For deployment
if __name__ == "__main__":
    app.run_server(port=8080, host="0.0.0.0", debug=False)