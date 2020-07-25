# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 15:45:09 2020

@author: tilan
"""
import numpy as np
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import visdcc
import dash_dangerously_set_inner_html


from app import app



# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "backgroundColor": "#f8f9fa",
}


MENU_BUTTON_STYLE = {     
    'width': '100%'
}


submenu_1 = [
    html.Li(
        # use Row and Col components to position the chevrons
        dbc.Row(
            [
                dbc.Col([
                        
                        dbc.Button(html.Span(["Overview", html.I(className="fas fa-chevron-right mr-3", style= {'float': 'right'})]), 
                                   href="/Overview", size="lg", className="mr-1", outline=True, color="primary", id="menu-link-0", block=True),
                        ]),
            ],
            className="my-1",
        ),
        id="menu-0",
    ),
    # we use the Collapse component to hide and reveal the navigation links
    dbc.Collapse(
        [

            dbc.Button("Groups", id="menu-sub-link-0", outline=True, color="primary", className="mr-2 w-100", block=True),
            dbc.Button("Overview", id="menu-sub-link-1", outline=True, color="primary", className="mr-2 w-100", block=True),
            dbc.Button("Distribution", id="menu-sub-link-2", outline=True, color="primary", className="mr-2 w-100", block=True),
        ],
        id="menu-link-0-collapse",
        className="p-left_medium",
    ),
]

submenu_2 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col( [
                        dbc.Button(html.Span(["Details", html.I(className="fas fa-chevron-right mr-3", style= {'float': 'right'})]), 
                                   href="/Details", size="lg", className="mr-1", outline=True, color="primary", id="menu-link-1", block=True),                        
                        ]),
            ],
            className="my-1",
        ),
    ),
    dbc.Collapse(
        [
            dbc.Button("Tasks Info", id="menu-sub-link-3", outline=True, color="primary", className="mr-1 w-100", block=True),
            dbc.Button("General Info", id="menu-sub-link-4", outline=True, color="primary", className="mr-1 w-100", block=True),
            dbc.Button("Student Info", id="menu-sub-link-5", outline=True, color="primary", className="mr-1 w-100", block=True),
        ],
        id="menu-link-1-collapse",
        className="p-left_medium",
    ),
]

submenu_3 = [
    html.Li(
        dbc.Row(
            [
                dbc.Col( [
                        dbc.Button(html.Span(["Custom", html.I(className="fas fa-chevron-right mr-3", style= {'float': 'right'})]), 
                                   href="/Custom", size="lg", className="mr-1", outline=True, color="primary", id="menu-link-2", block=True),                            
                        ]),
            ],
            className="my-1",
        ),
        id="menu-5",
    ),
    dbc.Collapse(
        [
            dbc.Button("Custom", id="menu-sub-link-6", outline=True, color="primary", className="mr-1 w-100", block=True),
        ],
        id="menu-link-2-collapse",
        className="p-left_medium",
    ),
]



br = [html.Br()]


sidebar = html.Div(
    [
        html.H2("sCool", className="display-4"),
        html.P(
            "Student perfomance in sCool", className="lead"
        ),
        html.Hr(),
        dbc.Nav(submenu_1 + br + submenu_2 + submenu_3, vertical=True),
        
        
        visdcc.Run_js(id = 'javascript'),
        
        
        
#        for menu link click output
        html.Div(id='menu-link-output-hidden', style={'display':'none'}),
        html.Div(id='menu-link-output-prevent-default', style={'display':'none'}),
        dcc.Input(
                id="menu-link-input",
                type="text", 
                style={'display':'none'},
                value="Overview"
            ),
        html.Div(id='menu-sub-link-output-hidden', style={'display':'none'}),
        dcc.Input(
                id="menu-sub-link-input",
                type="text", 
                style={'display':'none'},
                value="Overview"
            )
    
    
    ],
    style=SIDEBAR_STYLE,
    id="sidebar",
)



menuLinksCount = 3
menuSubLinksCount = 7
initUrl0 = "/Overview"
initUrl1 = "/Details"
initUrl2 = "/Custom"
@app.callback(
    [Output(f"menu-link-{i}-collapse", "is_open") for i in range(menuLinksCount)],
    ([Input(f"menu-link-{i}", "n_clicks") for i in range(menuLinksCount) ] + [ Input("url", "pathname")]),
    [State(f"menu-link-{i}-collapse", "is_open") for i in range(menuLinksCount)],
)
def toggle_accordion(*args):
    ctx = dash.callback_context

    print('toggle_accordion')    
    print(args)
    
    newToggle = [False] * (menuLinksCount)
    
    if not ctx.triggered:
        return newToggle

    triggered_id = [p['prop_id'] for p in ctx.triggered][0]
    clickedButton_id = triggered_id.split('.')[0]
     
    print(triggered_id)
    print(clickedButton_id)
    
    
#    on INIT url changes is the clickedButton_id
    if len(clickedButton_id.split('-')) == 1 :
        print('Init buttons')
        print(args[menuLinksCount ])
        print(args[menuLinksCount ] == initUrl0)
        if args[menuLinksCount ] in ["/", initUrl0]:
            newToggle[0] = True 
        elif args[menuLinksCount ] == initUrl1:
            newToggle[1] = True
        print(newToggle)
        return newToggle

    clickedButton_index = int(clickedButton_id.split('-')[2])
    
    print('args value = ')
    print(args[menuLinksCount + clickedButton_index])
    print(args[clickedButton_index])
    print( args[menuLinksCount + 1] )
        
    if clickedButton_index >= 0  and  args[clickedButton_index] :
        newToggle[clickedButton_index] = not args[menuLinksCount + 1 + clickedButton_index ]   # add 1 for URL pathname param
        
    
    return newToggle





@app.callback(  [ Output(f"menu-link-{i}", "className") for i in range(menuLinksCount) ], 
                 [Input(f"menu-link-{i}-collapse", "is_open") for i in range(menuLinksCount)] )
def setMenuClassOnChangeOpen(*args):   
    return  np.where(args,"open highlight",'').tolist()

       
                        
menuLink2Scroll = {
		"menu-sub-link-0" : ''
		,"menu-sub-link-1" : 'row-control-main-overview'
		,"menu-sub-link-2" : "Group-Distribution-Information"
		,"menu-sub-link-3" : 'Task-Information'
		,"menu-sub-link-4" : 'General-Information'
		,"menu-sub-link-5" : 'Student-Information'
		,"menu-sub-link-6" : ''
	}



@app.callback ( Output("menu-sub-link-input", "value") , 
              [Input(f"menu-sub-link-{j}", "n_clicks")   for j in range(menuSubLinksCount) ])
def changeMenuSetInput(*args):
    ctx = dash.callback_context
    newValue = ""

    
    if not ctx.triggered or not any(args):
        return newValue
    
    triggered_id = [p['prop_id'] for p in ctx.triggered][0]
    clickedButton_id = triggered_id.split('.')[0]

    print(clickedButton_id)
    
    if clickedButton_id     and   clickedButton_id in menuLink2Scroll :
         return menuLink2Scroll.get(clickedButton_id)
        
    return newValue    
    


app.clientside_callback(
        # specifiy the callback with ClientsideFunction(<namespace>, <function name>)
        ClientsideFunction('ui', 'jsFunction'),
        # the Output, Input and State are passed in as with a regular callback
         Output('menu-sub-link-output-hidden', 'children'),
        [Input("menu-sub-link-input", "value")]
    )