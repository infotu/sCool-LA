# -*- coding: utf-8 -*-

"""
Created on Thu Aug  6 21:24:40 2020
Reworked on  Mar 22 17:50:30 2023

@authors: tilan, zangl
"""


#----------------------------------------------------------------------------------------------------------------------
# imports
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction

from flask_login import current_user

from app import app
from data import studentGrouped
import constants


#----------------------------------------------------------------------------------------------------------------------
# global constants
THEME_COLOR_MAP     = constants.THEME_COLOR_MAP

keyLabel            = constants.keyLabel
keyHref             = constants.keyHref
keySubmenu          = constants.keySubmenu
keyValue            = constants.keyValue
keyScrollTo         = constants.keyScrollTo
keyClassName        = constants.keyClassName
keyColor            = constants.keyColor
keyBackgroundColor  = constants.keyBackgroundColor
keyIsDefault        = constants.keyIsDefault

iconNameHome        = constants.iconNameHome
iconNameGroups      = constants.iconNameGroups
iconNameDetails     = constants.iconNameDetails
iconNameStudents    = constants.iconNameStudents
iconNameCustom      = constants.iconNameCustom
iconNameTutorial    = constants.iconNameTutorial

themeOptionsButtonPre = "setting-customize-"


#----------------------------------------------------------------------------------------------------------------------
# global dataframes
dfUser                                                  = studentGrouped.dfUser
dfLearningActivityDetails                               = studentGrouped.dfLearningActivityDetails
dfEnrolledDetails                                       = studentGrouped.dfEnrolledDetails
dfStudentDetails                                        = studentGrouped.dfStudentDetails
dfCourseDetails                                         = studentGrouped.dfCourseDetails
dfSkillDetails                                          = studentGrouped.dfSkillDetails
dfPracticeTaskDetails                                   = studentGrouped.dfPracticeTaskDetails
dfTheoryTaskDetails                                     = studentGrouped.dfTheoryTaskDetails
dfTaskDetails                                           = studentGrouped.dfTaskDetails

dfPracticeTasks = dfPracticeTaskDetails.merge(
        dfSkillDetails[['SkillId', 'Title', 'Description']]
        , how='inner', on=['SkillId'], left_index=False, right_index=False,
        suffixes = ('', ' Skill')  )

dfPracticeTasks = dfPracticeTaskDetails.merge(
        dfCourseDetails[['CourseId', 'Title', 'Description']]
        , how='inner', on=['CourseId'], left_index=False, right_index=False,
        suffixes = ('', ' Course')  )


dfTheoryTasks = dfTheoryTaskDetails.merge(
        dfSkillDetails[['SkillId', 'Title', 'Description']]
        , how='inner', on=['SkillId'], left_index=False, right_index=False,
        suffixes = ('', ' Skill')  )

dfTheoryTasks = dfTheoryTaskDetails.merge(
        dfCourseDetails[['CourseId', 'Title', 'Description']]
        , how='inner', on=['CourseId'], left_index=False, right_index=False,
        suffixes = ('', ' Course')  )


#----------------------------------------------------------------------------------------------------------------------
# Function that sets the Theme of the app bases on parameter.
# params:   newTheme         (string) - new theme for app
# returns:  nothing
def setAppTheme(newTheme):
    
    constants.THEME = newTheme
    constants.THEME_COLOR, constants.THEME_BACKGROUND_COLOR, constants.THEME_COLOR_LIGHT, constants.THEME_EXPRESS_LAYOUT = constants.refreshThemeColor()


#----------------------------------------------------------------------------------------------------------------------
# Function that creates the content of the second tab of the settings page.
# params:   none
# returns:  list of html.Divs containing information about practice and theory tasks
def getCourseTask():
    
    layoutModalBodyCourseTask = []
    
    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated:
        currentUserId = current_user.id        
        userDB = studentGrouped.getUserFromUserId(currentUserId)        
        
        if  userDB is not None:        
            if userDB['IsAdmin']:
                layoutModalBodyCourseTask.append(                        
                        html.Div( 
                                children = [
                                    html.H5("Practice Tasks"),                  
                                    dbc.Table.from_dataframe(dfPracticeTaskDetails[[
                                            'PracticeTaskId','Title','Description','Difficulty','TitleSkill','TitleCourse']], 
                                                             striped=True, bordered=True, hover=True)
                                ]
                            )
                )
            
                layoutModalBodyCourseTask.append(                        
                        html.Div(      
                                children = [   
                                    html.H5("Theory Tasks"),                       
                                    dbc.Table.from_dataframe(dfTheoryTaskDetails[[
                                            'TheoryTaskId','Title','Description','Difficulty','TitleSkill','TitleCourse']], 
                                                             striped=True, bordered=True, hover=True)
                                ]
                            )
                )
            else:
                layoutModalBodyCourseTask.append(
                        html.Div(
                             children = [  
                                html.H5("Practice Tasks"),   
                                dbc.Table.from_dataframe(dfPracticeTaskDetails[  dfPracticeTaskDetails['User_Id'] ==  currentUserId][[
                                        'PracticeTaskId','Title','Description','Difficulty','TitleSkill','SkillId','TitleCourse','CourseId']], 
                                                         striped=True, bordered=True, hover=True)
                            ]
                        )
                )
                
                layoutModalBodyCourseTask.append(
                        html.Div(
                             children = [  
                                html.H5("Theory Tasks"),      
                                dbc.Table.from_dataframe(dfTheoryTaskDetails[  dfTheoryTaskDetails['User_Id'] ==  currentUserId][[
                                        'TheoryTaskId','Title','Description','Difficulty','TitleSkill','SkillId','TitleCourse','CourseId']], 
                                                         striped=True, bordered=True, hover=True)
                            ]
                        )
                )

    return layoutModalBodyCourseTask


#----------------------------------------------------------------------------------------------------------------------
# layout for the customize tab of the settings page
layoutModalBodyCustomize =[
    html.H5( children = [ html.I(className="fas fas fa-palette p-right_xx-small"),   "Customize theme"  ] ),
    html.P("Customize application theme"),
    
    html.Br()
    
    , dcc.Input(
                id              = "setting-customize-theme-color-input",
                type            = "text", 
                className       = "hidden",
                value           = "cyan"
            )
    , dcc.Input(
                id              = "setting-customize-theme-background-color-input",
                type            = "text", 
                className       = "hidden",
                value           = "cyan"
            )
    , html.Div(id='setting-customize-theme-color-output', className = "hidden"  )
]
layoutModalBodyCustomize = layoutModalBodyCustomize + [ html.Button(children=[
                                                            html.Span(  THEME_COLOR_MAP.get(i).get(keyLabel)  ) ],
                                                            id          = themeOptionsButtonPre + i, 
                                                            className   = "c-button button w3-btn w3-xlarge btn c-button-tile " + THEME_COLOR_MAP.get(i).get(keyClassName), 
                                                            n_clicks    = 0 )   for i in THEME_COLOR_MAP ]


#----------------------------------------------------------------------------------------------------------------------
# layout for the help center tab of the settings page
layoutModalBodyHelp = [
        
    html.Iframe( src  = "https://www.youtube.com/embed/70tjR3JYQ5A", width="420" , height="315" ),
        
    html.Br(),
    html.Br(),
    html.Hr(),
    html.Br(),
    
    html.H5( children = [ html.I(className="fas " + iconNameHome + " p-right_xx-small"),   "Game Data"  ] ),
    html.P("Only visible for admins!"),
    html.P("The Game Data tab serves as a comprehensive resource for global game data for admins only. This tab offers an in-depth analysis of game statistics, player demographics, and emerging global trends inside the sCool environment."),
    
    html.Hr(),
    html.Br(),
    
    html.H5( children = [ html.I(className="fas " + iconNameGroups + " p-right_xx-small"),   "Groups"  ] ),
    html.P("Only visible for admins!"),
    html.P("The Details tab empowers administrators with a powerful tool to compare classes and gain valuable insights into their performance. This tab offers a range of features that enable administrators to examine classes from different perspectives and make data-driven decisions for further development and other possible changes to the web application."),
    
    html.Hr(),
    html.Br(),

    html.H5( children = [ html.I(className="fas " + iconNameTutorial + " p-right_xx-small"),   "Tutorial"  ] ),
    html.P("Visible for admins and educators!"),
    html.P("The Tutorial serves as an introduction to the user interface (UI), ensuring a seamless and user-friendly experience right from the beginning. Designed for both new users and those seeking a refresher, this tab provides a concise overview of the key features and functionalities available. Users can quickly familiarize themselves with the layout, navigation options, and various interactive elements of the web app. "),
    
    html.Hr(),
    html.Br(),
    
    html.H5( children = [ html.I(className="fas " + iconNameDetails + " p-right_xx-small"),   "Classes"  ] ),
    html.P("Visible for admins and educators!"),
    html.P("The Classes tab offers users a convenient way to access and explore specific class-related information. With this tab, users can select a desired class from a list and gain access to high-value information and resources about the class. From class performances, current task assignments, and time spent in theory or practice, to granted points and much more."),
    
    html.Hr(),
    html.Br(),
    
    html.H5( children = [ html.I(className="fas " + iconNameStudents + " p-right_xx-small"),   "Students"  ] ),
    html.P("Visible for admins and educators!"),
    html.P("The Students tab provides users with the ability to select a specific class and then access individual student profiles within that class. This powerful feature allows users to gain detailed insights into each student's performance, progress, and engagement. Users can access a wealth of personalized information such as learned skills, task submissions, and participation levels via a timeline."),
    
    html.Hr(),
    html.Br(),
    
    html.H5( children = [ html.I(className="fas " + iconNameCustom + " p-right_xx-small"),   "Custom"  ] ),
    html.P("Visible for admins and educators!"),
    html.P("The Custom tab empowers users to create personalized and dynamic graphs that showcase information about the classes and/or students they have access. Users can create: "),
    html.P( children = [ html.I(className="fas fa-chart-bar font-size_medium p-right_xx-small"),   "Barcharts"  ]),
    html.P( children = [ html.I(className="fas fa-circle font-size_medium p-right_xx-small"),   "Scatterplots"  ] ),
    html.P( children = [ html.I(className="fas fa-ellipsis-h font-size_medium p-right_xx-small"),   "Bubblecharts" ] ),
    html.P( children = [ html.I(className="fas fa-chart-line font-size_medium p-right_xx-small"),   "Linecharts" ] ),
    html.P( children = [ html.I(className="fas fa-table font-size_medium p-right_xx-small"),   "Tables" ] ),
    
       
    html.Hr(),
    html.Br(),
        
    
    html.H5( children = [ html.I(className="fas fa-code p-right_xx-small"),   "Programming concepts"  ]  ),
      
    dcc.Link(children       = ['Python programming concepts']
             , href         = "https://docs.python.org/dev/library/ast.html"
             , className    = "c-link"
    ),
    
    html.P("Used Loop    =   used for, while loop in code"),
    html.P("Nested Loop    =   loop within a loop"),
    html.P("Condition    =   condition expression e.g. If"),
    html.P("Variable    =   a named variable e.g. a, x etc"),
    html.P("Arithematic Operators     =  viz Add, Div, Mult e.g. a + b, 1 * 2 etc "),
    html.P("Boolean = boolean operators = And, Or "),
    html.P("Logical Operators = e.g. Eq, Lt, Gt "),
    html.P("Unary Operators    =   e.g. Invert, Not, UAdd, USub"),
    html.P("Bitwise Operators    =  e.g.  LShift,  RShift,  BitOr,  BitXor,  BitAnd,  MatMult"),
    html.P("Dictionary Or Map     =   Dict"),
    html.P("Data Structure    =   e.g. Dict, List, Set"),
    html.P("Try Exception  =   Try exception "),
    html.P("Constants    =   e.g. 3 or 'a' or None "),
    html.P("Keyword = e.g. and, while, None "),
    html.P("function call = e.g. call('friend')  "),
    html.P("Statements = e.g. Assignment, Assert, Delete, AnnAssign, Raise, Pass, AugAssign, AnnAssign  "),
                                     
    html.P("The ast module helps Python applications to process trees of the Python abstract syntax grammar. The abstract syntax itself might change with each Python release; this module helps to find out programmatically what the current grammar looks like."),
    html.P("Expr   =   Expr,  UnaryOp, UAdd, USub,  Not, Invert, BinOp,  Add, Sub, Mult, Div, FloorDiv,  " +
           "Mod, Pow,  LShift, RShift,  BitOr, BitXor, BitAnd,  MatMult, BoolOp,  And, Or, " +
           "Compare,  Eq,  NotEq, Lt,  LtE, Gt, GtE,  Is, IsNot,  In, NotIn,  Call, keyword, IfExp, Attribute"),
    html.P("Operator    =   Add , Sub , Mult , MatMult , Div , Mod , Pow , LShift , RShift , BitOr , BitXor , BitAnd , FloorDiv"),
    html.P("Subscripting    =   Subscript , Slice"),
    html.P("Comprehensions    =   ListComp , SetComp, GeneratorExp, DictComp, comprehension"),
    html.P("Statements    =   Assign , AnnAssign, AugAssign, Raise, Assert, Delete, Pass"),
    html.P("imports    =   Import , ImportFrom, alias"),
    html.P("Control Flows    =   If, For, While, Break, Continue, Try, ExceptHandler, With, withitem"),
    html.P("Function Class    =   FunctionDef, Lambda,  arguments, arg, Return, Yield, YieldFrom, Global,  Nonlocal,  ClassDef"),
    html.P("Async    =   AsyncFunctionDef, Await,  AsyncFor, AsyncWith"),
       
    html.Hr(),
    html.Br(),
]


#----------------------------------------------------------------------------------------------------------------------
# main layout of the settings page
settingsLayout = [
        
    dbc.Tabs(
        [
            dbc.Tab( layoutModalBodyHelp , label="Help Center"),
            dbc.Tab( getCourseTask() , label="Course & Tasks" , id = "tabCourseSkillTask"),
            dbc.Tab( layoutModalBodyCustomize , label="Customize"),
        ]
    )
        
]


#----------------------------------------------------------------------------------------------------------------------
# Callback function to set custom theme background color
# params:   args         (tuple) - number of clicks on customize buttons (used as callback trigger)
# returns:  tuple of dicts with new theme color
@app.callback ( [ Output("setting-customize-theme-background-color-input", "value") ,
                    Output("setting-customize-theme-color-input", "value"), 
                 ], 
              [Input( themeOptionsButtonPre + f"{j}", "n_clicks")   for j in THEME_COLOR_MAP ])
def onChangeCustomizeAppTheme(*args):
    ctx = dash.callback_context
    newValue = "", ""

    if not ctx.triggered or not any(args):
        return newValue
    
    triggered_id = [p['prop_id'] for p in ctx.triggered][0]
    clickedButton_id = triggered_id.split('.')[0]
    
    if not clickedButton_id == ''  and clickedButton_id.split(themeOptionsButtonPre)[1] in THEME_COLOR_MAP :
        setAppTheme( clickedButton_id.split(themeOptionsButtonPre)[1] )
        
        return [
                THEME_COLOR_MAP.get( clickedButton_id.split(themeOptionsButtonPre)[1] ).get(keyBackgroundColor),
                THEME_COLOR_MAP.get( clickedButton_id.split(themeOptionsButtonPre)[1] ).get(keyColor),  ]
        
    return newValue  


#----------------------------------------------------------------------------------------------------------------------
# Callback function render task tab content if opened
# params:   pathname         (string) - containing current pathname (only used as trigger)
# returns:  empty html.Div or list of html.Divs
@app.callback(Output("tabCourseSkillTask", "children"), [Input("url", "pathname")],
    )
def render_tab_task_content(pathname):

    if current_user and current_user.is_authenticated  :
        return getCourseTask()
    
    return html.Div()


app.clientside_callback(
        # specifiy the callback with ClientsideFunction(<namespace>, <function name>)
        ClientsideFunction('ui', 'updateThemeColor'),
        # the Output, Input and State are passed in as with a regular callback
         Output('setting-customize-theme-color-output', 'children'),
        [ Input("setting-customize-theme-background-color-input", "value"),
            Input("setting-customize-theme-color-input", "value"),
            ]
    )