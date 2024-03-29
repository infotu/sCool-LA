# -*- coding: utf-8 -*-

"""
Created on   Jun 14 15:45:09 2020
Reworked on  Mar 14 10:25:00 2023

@authors: tilan, zangl
"""


#----------------------------------------------------------------------------------------------------------------------
# imports
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


#----------------------------------------------------------------------------------------------------------------------
# global constants
keyLabel            = constants.keyLabel
keyHref             = constants.keyHref
keySubmenu          = constants.keySubmenu
keyValue            = constants.keyValue
keyScrollTo         = constants.keyScrollTo
keyClassName        = constants.keyClassName
keyOnlyForAdmin     = constants.keyOnlyForAdmin

iconNameHome        = constants.iconNameHome
iconNameGroups      = constants.iconNameGroups
iconNameClasses     = constants.iconNameClasses
iconNameStudents    = constants.iconNameStudents
iconNameCustom      = constants.iconNameCustom
iconNameTutorial    = constants.iconNameTutorial


#----------------------------------------------------------------------------------------------------------------------
# Used to generate left side navbar buttons
# provide href, where navigate to on click on the Menu Section
menuLink = {
    "menu-link-0" : { keyLabel : 'Game Data', keyHref : '/Home',
                  keySubmenu : [],  keyClassName : 'fas ' + iconNameHome + ' m-right-small',
                          keyOnlyForAdmin : True },

    "menu-link-1" : { keyLabel : 'Groups', keyHref : '/Groups',
                  keySubmenu : [
                          "menu-sub-link-0", "menu-sub-link-1", "menu-sub-link-2"
                          ],  keyClassName : 'fas ' + iconNameGroups + ' m-right-small',
                          keyOnlyForAdmin : True    },

    "menu-link-2" : { keyLabel : 'Tutorial', keyHref : '/Welcome' ,
                  keySubmenu : [],  keyClassName : 'fas ' + iconNameTutorial + ' m-right-small',
                          keyOnlyForAdmin : False    },

    "menu-link-3" : { keyLabel : 'Classes', keyHref : '/Classes' ,
                  keySubmenu : [
                          "menu-sub-link-4", "menu-sub-link-5", "menu-sub-link-6", "menu-sub-link-7", "menu-sub-link-8"
                          ],  keyClassName : 'fas ' + iconNameClasses + ' m-right-small',
                          keyOnlyForAdmin : False    },

    "menu-link-4" : { keyLabel : 'Students', keyHref : '/Students' ,
                  keySubmenu : [ "menu-sub-link-9", "menu-sub-link-10", "menu-sub-link-11"
                          ],  keyClassName : 'fas ' + iconNameStudents + ' m-right-small',
                          keyOnlyForAdmin : False    },  

    "menu-link-5" : { keyLabel : 'Custom', keyHref : '/Custom' ,
                  keySubmenu : [],  keyClassName : 'fas ' + iconNameCustom + ' m-right-small',
                          keyOnlyForAdmin : False    }
}


#----------------------------------------------------------------------------------------------------------------------
# Used to generate left side navbar sub-buttons
# provide Scroll to domElementId -> scroll to this domElement on click
menuSubLink2Scroll = {
    "menu-sub-link-0"  :  {keyLabel : "Overview", keyScrollTo: ''}
    ,"menu-sub-link-1" :  {keyLabel : "Compare Groups", keyScrollTo: 'row-control-main-overview'}
    ,"menu-sub-link-2" :  {keyLabel : "Distribution", keyScrollTo: "Group-Distribution-Information"}
    ,"menu-sub-link-4" :  {keyLabel : "Class Overview", keyScrollTo: 'classes-overview-hr'}
    ,"menu-sub-link-5" :  {keyLabel : "Task Information", keyScrollTo: 'classes-task-information-hr'}
    ,"menu-sub-link-6" :  {keyLabel : "Task Code Submissions", keyScrollTo: 'classes-code-submission-hr'}
    ,"menu-sub-link-7" :  {keyLabel : "Concept Information", keyScrollTo: 'classes-concept-hr'}
    ,"menu-sub-link-8" :  {keyLabel : "Class Statistics", keyScrollTo: 'classes-stats-hr'}
    ,"menu-sub-link-9" :  {keyLabel : "Student Overview", keyScrollTo: 'students-overview-hr'}
    ,"menu-sub-link-10" :  {keyLabel : "Courses Progress Tracker", keyScrollTo: 'students-progress-tracker-hr'}
    ,"menu-sub-link-11" :  {keyLabel : "Game Interactions/Timeline", keyScrollTo: 'students-game-interactions-hr'}
}


spacer = [html.Div(className = "  m-bottom_x-small ")]


#----------------------------------------------------------------------------------------------------------------------
# Function that generates the sidebar menu buttons (Game Data, Groups, Tutorial, Classes, Students, Custom) and their sub-buttons
# params:   none
# returns:  list containing sidebar menu buttons
def getMenu():
    menus = []
    
    countMenuLink = 0
    countMenuSubLink = 0
    
    isUserAdmin = False  

    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated:
        userDB = studentGrouped.getUserFromUserId(current_user.id)
        
        print(userDB)
        if  userDB is not None:        
            if userDB['IsAdmin']:
                isUserAdmin = True

    for menuKey in menuLink.keys():
        currentMenu = menuLink.get(menuKey)
        
        contentClass = ""
        if len(currentMenu.get(keySubmenu)) > 0  :
            contentClass = " c-button-nav-content-hover-items "
        
        menus.append(
            html.Li(
                # use Row and Col components to position the chevrons
                        dbc.Button(html.Span([
                                                html.Span(children = [
                                                            html.I(className=  currentMenu.get(keyClassName)),
                                                            html.Span(currentMenu.get(keyLabel), className = "c-button-nav-text")
                                                    ], 
                                                    className = contentClass)
                                                ]
                                        ,
                                        className = " c-button-nav-content " ), 
                                    href= currentMenu.get(keyHref) , 
                                    size="lg", 
                                    className=" c-button-nav ", 
                                    outline=True, color="primary", 
                                    id= menuKey, 
                                    block=True),
                className = "hidden-v "  if    not isUserAdmin   and   currentMenu.get(keyOnlyForAdmin)   else   "m-top_x-small",
                id = menuKey + '-li-container' 
            )
        )
        # we use the Collapse component to hide and reveal the menu links
        subMenuButtons = []
        
        for submenuKey in currentMenu.get(keySubmenu):
            subMenuButtons.append(
                    dbc.Button(menuSubLink2Scroll.get(submenuKey).get('label'), 
                                       id=  submenuKey , 
                                       outline=True, color="primary", 
                                       className="m_x-small", 
                                       block=True),
            )
            countMenuSubLink += 1
            
        
        menus.append( 
                dbc.Collapse(
                    subMenuButtons,
                    id= menuKey + "-collapse",
                    className=" p-left_small ",
                )
        )
                
        countMenuLink += 1
        menus = menus + spacer

    return menus


#----------------------------------------------------------------------------------------------------------------------
# Function to get the help center layout from settings.py
# params:   none
# returns:  layout of the settings tab
def getModalHelpBody():
    return settings.settingsLayout


#----------------------------------------------------------------------------------------------------------------------
# sidebar manu layout - used in main layout (located in index.py)
sidebar = html.Div(
    [

        html.H2(
                html.Img(src=app.get_asset_url('sCool-Logo.png'), className="img-fit" ), className="display-4"),

        html.P(
            "Student perfomance in sCool", className="lead"
        ),

        html.Hr(),

        dbc.Nav( children = getMenu(), 
                id = "menu-main-nav",
                vertical=True),
                
#        for menu link click output
        html.Div(id='menu-link-output-hidden', style={'display':'none'}),

        html.Div(id='menu-link-output-prevent-default', style={'display':'none'}),

        dcc.Input(
                id="menu-link-input",
                type="text", 
                style={'display':'none'},
                value="Groups"
            ),

        html.Div(id='menu-sub-link-output-hidden', style={'display':'none'}),

        dcc.Input(
                id="menu-sub-link-input",
                type="text", 
                style={'display':'none'},
                value="Groups"
            ),
        
        html.Div(
            [
                html.Button(html.I(className="fas fa-info font-size_medium p-right_xx-small"),
                                   id='menu-modal-setting-open', 
                                   className="c-button button w3-btn w3-xlarge menu-modal-help-button btn btn-outline-info ",
                                   n_clicks=0),
                dbc.Modal(
                    [
                        dbc.ModalHeader("sCool Data Analysis Tool Help Center & Settings"),
                        dbc.ModalBody(children = getModalHelpBody()),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="menu-modal-setting-close", className="ml-auto")
                        ),
                    ],
                    id="menu-modal-setting",
                    className = "c-modal-large"
                ),
            ],
            id = "menu-modal-help-div",
            className = "menu-modal-help"
        ), 
    ],
    className = " page-sidebar p-bottom_x-large hidden",
    id="page-sidebar",
)


#----------------------------------------------------------------------------------------------------------------------
# Callback function to show/hide a red highlight border on certain components based on user interaction. (clicking on headlines)
# params:   args         (tuple) - id of main sidebar menu buttons / current url / state of buttons (if they are currently selected or not)
# returns:  new state of buttons (if they are currently selected or not)
@app.callback(
    [Output(f"{i}-collapse", "is_open") for i in menuLink],
    ([Input(f"{i}", "n_clicks") for i in menuLink ] + [ Input("url", "pathname")]),
    [State(f"{i}-collapse", "is_open") for i in menuLink],
)
def toggle_accordion(*args):
    menuLinksCount      =   len(menuLink.keys())
    ctx = dash.callback_context
    
    newToggle = [False] * (menuLinksCount)
    
    if not ctx.triggered:
        
        for index, menuLinkKey in enumerate(list(menuLink.keys())):
                if  (   ( args[ menuLinksCount ] is not None  ) 
                        and   args[ menuLinksCount ].lower()   in  menuLink.get(menuLinkKey).get(keyHref).lower()):
                    newToggle[index] = True
                    
        return newToggle

    triggered_id = [p['prop_id'] for p in ctx.triggered][0]
    clickedButton_id = triggered_id.split('.')[0]
            
#    on INIT url changes is the clickedButton_id
    if len(clickedButton_id.split('-')) == 1 :
        if args[menuLinksCount ] in ["/"]:
            for index, menuLinkKey in enumerate(list(menuLink.keys())):
                if (   menuLink.get(menuLinkKey).get(keyHref) == constants.loginRedirect  ) :
                    newToggle[index] = True
        else :
            for index, menuLinkKey in enumerate(list(menuLink.keys())):
                if (  ( args[ menuLinksCount ] is not None  ) 
                        and  args[ menuLinksCount ].lower()   in  menuLink.get(menuLinkKey).get(keyHref).lower()  ) :
                    newToggle[index] = True   
        
        return newToggle

    clickedButton_index = int(clickedButton_id.split('-')[2])
    
    if clickedButton_index >= 0  and  args[clickedButton_index] :
        newToggle[clickedButton_index] = not args[menuLinksCount + 1 + clickedButton_index ]   # add 1 for URL pathname param
        
    return newToggle


#----------------------------------------------------------------------------------------------------------------------
# Callback function to manipulate the className property of the menu buttons list container based on wether the current user is a admin or not.
# params:   pathname         (string) - string containing the pathname (used only as trigger)
# returns:  list containing classNames (CSS styling) of the sidebar menu buttons list container
@app.callback(  [  Output(f"{i}-li-container", "className") for i in menuLink   ], 
                [  Input("url", "pathname")   ],
)
def set_menu_class_on_login(pathname):   

    menuLinksCount = len(menuLink.keys())
    newClasses = ['m-top_x-small'] * menuLinksCount

    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated  :

        isUserAdmin = False    
        
        userDB = studentGrouped.getUserFromUserId(current_user.id)
        
        if  userDB is not None:        
            if userDB['IsAdmin']:
                isUserAdmin = True

        for index, menuKey in enumerate(menuLink):
            currentMenu = menuLink.get(menuKey)
            newClasses[index] = "hidden-v "  if    not isUserAdmin   and   currentMenu.get(keyOnlyForAdmin)   else   "m-top_x-small"
            
    return newClasses


#----------------------------------------------------------------------------------------------------------------------
# Callback function to manipulate the className property of the menu buttons. (highlight setter)
# params:   args         (tuple) - states of main sidebar menu button collapses (indicating if they are currently open or not)
# returns:  new className of buttons (if they are currently selected or not)
@app.callback(  [ Output(f"{i}", "className") for i in menuLink ], 
                 [Input(f"{i}-collapse", "is_open") for i in menuLink] )
def set_menu_class_on_change_open(*args):   
    return  np.where(args,"open highlight",'').tolist()


#----------------------------------------------------------------------------------------------------------------------
# Callback function to set the value of the Imput field with the id menu-sub-link-input.
# params:   args         (tuple) - click information of all sub-menu buttons
# returns:  new value of button with id menu-sub-link-input (indicating wehter button is pressed)
@app.callback ( Output("menu-sub-link-input", "value") , 
              [Input(f"{j}", "n_clicks")   for j in menuSubLink2Scroll ])
def change_menu_set_input(*args):
    ctx = dash.callback_context
    newValue = ""

    if not ctx.triggered or not any(args):
        return newValue
    
    triggered_id = [p['prop_id'] for p in ctx.triggered][0]
    clickedButton_id = triggered_id.split('.')[0]

    
    if clickedButton_id     and   clickedButton_id in menuSubLink2Scroll :
         return menuSubLink2Scroll.get(clickedButton_id).get('scrollTo')
        
    return newValue    


#----------------------------------------------------------------------------------------------------------------------
# Callback function to update the property "is_open" of the menu-modal-setting component.
# params:   n1              (int)  - number of clicks on component menu-modal-setting-open
#           n2              (int)  - number of clicks on component menu-modal-setting-close
#           is_open         (bool) - indicating wether the menu-modal-setting component is currently open or not
# returns:  new state of property "is_open" of the menu-modal-setting component
@app.callback(
    Output("menu-modal-setting", "is_open"),
    [Input("menu-modal-setting-open", "n_clicks"), Input("menu-modal-setting-close", "n_clicks")],
    [State("menu-modal-setting", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


#----------------------------------------------------------------------------------------------------------------------
# Clientside callback function to update the children of menu-sub-link-output-hidden (with javascript code in /src/assets/app.js)
# params:   elmntId         (string)  - menu-sub-link-input value
# returns:  nothing
app.clientside_callback(
        # specifiy the callback with ClientsideFunction(<namespace>, <function name>)
        ClientsideFunction('ui', 'jsFunction'),
        # the Output, Input and State are passed in as with a regular callback
         Output('menu-sub-link-output-hidden', 'children'),
        [Input("menu-sub-link-input", "value")]
    )