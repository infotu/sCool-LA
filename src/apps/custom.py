# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 10:34:38 2020

@author: tilan
"""
import numpy as np
import plotly.express as px

import pandas as pd
import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import chart_studio.plotly as py
from plotly import graph_objs as go

from app import app



from flask_login import current_user
from data import studentGrouped
import constants
import util
import subprocess



#--------------------- school selection START ----------------------
GroupSelector_options = studentGrouped.GroupSelector_options 
#--------------------- school selection END ----------------------



#--------------------------------- DataBase get data START ---------------------------
dfStudentDetails                        = studentGrouped.dfStudentDetails


dfPracticeTaskDetails                   = studentGrouped.dfPracticeTaskDetails
dfTheoryTaskDetails                     = studentGrouped.dfTheoryTaskDetails
dfSkillDetails                          = studentGrouped.dfSkillDetails
dfCourseDetails                          = studentGrouped.dfCourseDetails

dfGroupedPractice                       = studentGrouped.dfGroupedPractice
dfGroupedOriginal                       = studentGrouped.dfGroupedOriginal
dfPlayerStrategyPractice                = studentGrouped.dfPlayerStrategyPractice  
dfGroupedPracticeTaskWise               = studentGrouped.dfGroupedPracticeTaskWise
dfGroupedPracticeDB                     = studentGrouped.dfGroupedPracticeDB
dfRuns                                  = studentGrouped.dfRuns


dfPlayerStrategyTheory                  = studentGrouped.dfPlayerStrategyTheory
dfGroupedPlayerStrategyTheory           = studentGrouped.dfGroupedPlayerStrategyTheory

#--------------------------------- DataBase get data END ---------------------------

#--------------------------- helper functions START -----------------------    
getTaskWiseSuccessFail                  =  studentGrouped.getTaskWiseSuccessFail
getStudentsOfLearningActivity                     =  studentGrouped.getStudentsOfLearningActivity
getPracticeConceptsUsedDetailsStr          =  studentGrouped.getPracticeConceptsUsedDetailsStr
getStudentWiseData                      =  studentGrouped.getStudentWiseData


BuildOptions                            =  studentGrouped.BuildOptions

#--------------------------- helper functions END -----------------------  


getFigureTypesOptions                   = constants.getFigureTypesOptions



#-----------------------------------Functions START ----------------------------------------
FeaturesCustom          = constants.FeaturesCustom

FeaturesCustomPractice  = constants.FeaturesCustomPractice
FeaturesCustomTheory    = constants.FeaturesCustomTheory


FigureTypes             = constants.FigureTypes 


graphHeight         =  constants.graphHeight
graphHeight         =   graphHeight - 200


hoverData           =  constants.hoverData.copy()


Feature1            = "Student"
Feature3Size        = "SessionDuration"




featureGroupByOptions   = [constants.featureStudent, constants.featureTask, constants.featureSkill, constants.featureCourse, constants.featureTaskType]
#featureGroupBySubOptions   = featureGroupByOptions + [constants.featureTaskType]
featureGroupByDefault   = 'Student'



#Student Interaction with Game - TIMELINE
def plotClassOverview(schoolKey, feature1, selectedAxis, selectedFigureType, 
                      feature2              = '', 
                      feature3              = '',
                      plotClassName         = " col-12 col-xl-12 ", 
                      selectedDistribution  = [],
                      selectedFeatureMulti  = [],
                      groupBy               = constants.STUDENT_ID_FEATURE,
                      groupBySub            = [] ,
                      hoverData             = hoverData.copy()       ) :
    

    graphs = []
    rows = []
    
    if (None == schoolKey) :
        return graphs
    
    
    groupByAll = [ ]
    if groupBySub is None :
        groupBySub = []
    if selectedFeatureMulti is None:
        selectedFeatureMulti = []
    if selectedDistribution is None:
        selectedDistribution = []
    
    
    studentDataDf = studentGrouped.getStudentsOfLearningActivityDF(schoolKey, isOriginal = True)
    
    
    studentDataDf                                   = studentDataDf.merge(
               dfSkillDetails
               , how='inner', on=['SkillId'], left_index=False, right_index=False, suffixes = ['', 'Skill'])
    studentDataDf                                   = studentDataDf.merge(
               dfCourseDetails
               , how='inner', on=['CourseId'], left_index=False, right_index=False, suffixes = ['', 'Course'])
    
    
    studentDataDf[constants.featureStudent]     =    studentDataDf['Name'].astype(str)  + '-' + studentDataDf['StudentId'].astype(str)
#    studentDataDf[constants.featureGroup]       =    constants.TypeGroup + '-' + studentDataDf['GroupId'].astype(str)
    studentDataDf[constants.featureCourse]      =    constants.TypeCourse  + ' : ' + studentDataDf['TitleCourse'].astype(str) +  '-' +  studentDataDf['CourseId'].astype(str) 
    studentDataDf[constants.featureSkill]       =    constants.TypeSkill + ' : ' + studentDataDf['TitleSkill'].astype(str) + '-' + studentDataDf['SkillId'].astype(str) 
    studentDataDf[constants.featureTask]        =    studentDataDf[constants.featureTaskId].astype(str)
    
    
#    only the last successful task is taken into account for calculations !
    studentDataDf = studentDataDf.drop_duplicates(subset=[constants.featureStudent, constants.featureTask], keep='last')
    
    
    for hoverFeatureRemove in  featureGroupByOptions :
        if hoverFeatureRemove in hoverData:
            hoverData.remove( hoverFeatureRemove )
            

    if 'studentDataDf' in locals()     and    ( studentDataDf is not None  )  :
        
        if selectedFeatureMulti is not None:
            selectedFeatureMulti = [groupBy] + groupBySub + selectedFeatureMulti
        
        if   groupBy  in  featureGroupByOptions  :
            
            studentDataDfSum, hoverData, groupByAll = util.groupedBySelectedFeaturesDf(studentDataDf, 
                                                                   groupBy = groupBy  , 
                                                                   groupBySub = groupBySub  , 
                                                                   groupByAll = groupByAll  , 
                                                                   hoverData = hoverData.copy()   )
            hoverName   = groupBy
            
            
        else  :
            groupByAll = [ featureGroupByDefault ]
            studentDataDfSum = studentDataDf.groupby(groupByAll, as_index=False).sum()
            
            hoverName   = featureGroupByDefault
            groupBy     = featureGroupByDefault
            
                
                
        
#        TODO :- CHECK THIS   18.08.2020
        if not constants.featureStudent in  groupByAll:
            gameDataStudent = studentDataDf.groupby(groupByAll + [ constants.featureStudent ], as_index=False).sum().round(decimals=2)
        else :
            gameDataStudent = studentDataDf
            

        plotTitle   = ' Details of students ' 
        plotTitle   = plotTitle + str( constants.feature2UserNamesDict.get(feature1) if feature1 in constants.feature2UserNamesDict.keys() else feature1 )
        plotTitle   = plotTitle + ' vs ' + str( constants.feature2UserNamesDict.get(feature2) if feature2 in constants.feature2UserNamesDict.keys() else feature2 )
        

        marginalX   = ''
        marginalY   = ''
        
        
        rows = util.getCustomPlot(
                          df                    = studentDataDfSum, 
                          dfOriginal            = gameDataStudent, 
                          featureX              = feature1, 
                          featureY              = feature2, 
                          feature3              = feature3, 
                          selectedFigureType    = selectedFigureType, 
                          selectedAxis          = selectedAxis, 
                          plotTitle             = plotTitle,
                          marginalX             = marginalX,
                          marginalY             = marginalY,
                          hoverData             = hoverData,
                          hoverName             = hoverName,
                          groupBy               = groupBy,
                          selectedDistribution  = selectedDistribution,
                          selectedFeatureMulti  = selectedFeatureMulti,
                          isThemeSizePlot       = True,
            )
        
        
        if (constants.keyClassName in constants.FigureTypes.get(selectedFigureType)   ):
            plotClassName = constants.FigureTypes.get(selectedFigureType).get(constants.keyClassName)
        
       
        graphs.append( html.Div( rows ,
                                className = plotClassName ) )
        

    return graphs


def generateControlCardCustomPlotForm():
    
    return util.generateControlCardCustomPlotForm(
            idApp                   = "custom", 
            feature1Options         = FeaturesCustom + FeaturesCustomPractice + FeaturesCustomTheory , 
            feature2Options         = featureGroupByOptions + FeaturesCustom + FeaturesCustomPractice + FeaturesCustomTheory , 
            feature3Options         = FeaturesCustom + FeaturesCustomPractice + FeaturesCustomTheory , 
            feature1ValueDefault    = "" ,
            feature2ValueDefault    = "" ,
            feature3ValueDefault    = Feature3Size ,
            featureMultiOptions     = FeaturesCustom + FeaturesCustomPractice + FeaturesCustomTheory ,
            featureGroupByDefault   = featureGroupByDefault ,
            featureGroupByOptions   = featureGroupByOptions ,
    )


def generateLearningActivityControlCard():
    """
    :return: A Div containing Learning Analytics Selection.
    """
    return html.Div(
        id="custom-control-card-index",
        children=[
            html.P(constants.labelSelectLA),
            dcc.Dropdown(
                id = "custom-selector-main",
                className = "dropdown-main",
                placeholder = "Choose Class..."
            ),
        ]
    )


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


#------------------------------------------------------------------------------------------------
#---------------------------LAYOUT --------------------------------------------------------------


layout = [

    html.Div(html.H1('Custom Data Visualization', id = 'custom-heading', className = "align-center"), className = "stick-on-top-of-page"),

    html.Div(html.P("Welcome to the custom data visualizations tab! Here you can create your own graphs and tables based on your personal interest! Simply select the class you're interested in. Then, choose the data visualization type that fits your needs the best. The application will then present you with additional input options, tailored to your chosen visualization, allowing you to explore the data more extensively. Have fun!", className = "welcome-paragraph m-left-right-medium m-top_small")),

    html.Hr(id = 'custom-paragraph-hr', className = "hr_custom_style"),

    dbc.Row([
            dbc.Navbar(
                children = [
                        dbc.Row([
                                dbc.Col(
                                    # Left column
                                    html.Div(
                                        id="custom-row-control-main-index",
                                        className="",
                                        children=[ generateLearningActivityControlCard() ]
                                        + [
                                            html.Div(
                                                ["initial child"], id="custom-row-control-main-output-clientside-index", style={"display": "none"}
                                            )
                                        ],
                                    ),
                            ),
                        ],
                            className = "row w-100 selector-main-row"
                        ),                
                ],
                id="custom-page-topbar", 
                sticky          = "top" ,
                light           = False ,
                className       = "navbar-main p-bottom_medium m-left-right-small",
                style           = {'width': '100%'}
            ),
    ], className = "p-top_medium p-bottom_medium"),


    html.Div(id= "custom-row-control-main", className = "hidden", children=[generateControlCardCustomPlotForm()], style = {"border": "2px groove grey", "margin": "1rem", "padding-top": "0.5rem"}),

    html.Div(id = "custom-main-container", className = "row custom-main-container m-top_small hidden"),
    
    html.Div(
        html.A( children=[html.I(className="fas fa-download font-size_medium p_small"),
                "download data",], 
                id = "custom-download-main-link",
                className = "disabled",
                href="",
                target =  "_blank",
                download='data.csv'),
        id = "custom-download-div",
        className = "hidden"                                  
    )
]



#----------------------------------------------------------------------------------------------
#                    CALL BACK
#----------------------------------------------------------------------------------------------
    
    
@app.callback([Output("custom-row-control-main", "className"), Output("custom-main-container", "className"),
               Output("custom-download-div", "className")],
               Input("custom-selector-main", "value"))
def show_hide_custom_content(value):

    if value is not '':
        return ["m-left-right-small", "row custom-main-container m-top_small", ""]

    return ["m-left-right-small hidden", "row custom-main-container m-top_small hidden", "hidden"]


@app.callback([Output("custom-selector-main", "options"), Output("custom-selector-main", "value")], 
              [Input("url", "pathname")],
              state=[State(component_id = "custom-selector-main", component_property='options'),
                     State(component_id = "custom-selector-main", component_property='value')]
    )
def render_main_selector_content(pathname, selectorOptions, selectorValue ):
    
    if current_user and current_user.is_authenticated  :
        userOptions = getUserLAOptions()
        value = ''

        if selectorOptions and selectorValue:
           return selectorOptions, selectorValue
        
        if len(userOptions) == 1:
            value = userOptions[0]['value']
        
        return userOptions, value
    
    
    return [], ''


# Form Submission  - Update plot container with new selected plot
@app.callback(
    Output( "custom-main-container", "children"),
    [
        Input( "custom-form-submit-btn", "n_clicks")
    ],
     state=[ State(component_id  =  'custom-selector-main', component_property='value'),
                State(component_id = "custom-form-feature-1", component_property='value'),
                State(component_id = "custom-form-feature-2", component_property='value'),
                State(component_id = "custom-form-feature-3", component_property='value'),
                State(component_id = "custom-form-feature-axis", component_property='value'),
                State(component_id = "custom-form-figure-type", component_property='value'),
                State(component_id = "custom-form-feature-distribution", component_property='value'),
                State(component_id = "custom-form-feature-color-group", component_property='value'),
                State(component_id = "custom-form-feature-color-group-sub", component_property='value'),
                State(component_id = "custom-form-feature-multi", component_property='value'),
                State(component_id = "custom-main-container", component_property='children'),
                ]
)
def update_bar(n_clicks, groupMain, selectedFeature, selectedFeature1, selectedFeature3, selectedAxis, 
               selectedFigureType, 
               selectedDistribution,
               selectedFeatureColorGroupBy,
               selectedFeatureColorGroupBySub,
               selectedFeatureMulti,
               containerChildren 
               ):    
    graphs = []
    
    if n_clicks == 0 or  not util.isValidValueId(groupMain) :
        return html.Div(graphs)
    
    if   not ( selectedFeature1 ) :
        selectedFeature1 = ''
    
    if   not ( selectedFeature3 ) :
        selectedFeature3 = ''
        
    
    graphs = plotClassOverview( int(groupMain), selectedFeature, selectedAxis, selectedFigureType, selectedFeature1, selectedFeature3,
                               selectedDistribution         = selectedDistribution,
                               selectedFeatureMulti         = selectedFeatureMulti,
                               groupBy  = selectedFeatureColorGroupBy, 
                               groupBySub                   = selectedFeatureColorGroupBySub,   )
    
    if not(None is containerChildren):
        if isinstance(containerChildren, list):
            graphs = graphs + containerChildren 
        else :
            if isinstance(containerChildren, dict) and 'props' in containerChildren.keys():
                graphs = graphs + containerChildren.get('props').get('children')


    return   graphs 



# Form Submission  - Update plot container with new selected plot


@app.callback(
    Output("custom-data-based-on-selection", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-data-based-on-selection", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsDataBasedOn) 


@app.callback(
    Output("custom-graph-axis-data-label", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-graph-axis-data-label", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsAxisDataLabelEnabled) 


@app.callback(
    Output("custom-graph-axis-data-row", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-graph-axis-data-row", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsAxisDataRowEnabled) 


@app.callback(
    Output("custom-form-feature-axis", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-form-feature-axis", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsAxisEnabled) 


@app.callback(
    Output("custom-form-feature-3", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-form-feature-3", component_property='className') ]
)
def update_feature_size_disabled(selectedFigureType, initialClass):   
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsFeature3Enabled)


@app.callback(
    Output("custom-graph-orientation-label", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-graph-orientation-label", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsGraphOrientationLabelEnabled) 


@app.callback(
    Output("custom-distribution-label", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-distribution-label", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsDistributionLabelEnabled) 


@app.callback(
    Output("custom-form-feature-distribution", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-form-feature-distribution", component_property='className') ]
)
def update_feature_distribution_disabled(selectedFigureType, initialClass):   
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsDistributionEnabled)


@app.callback(
    Output("custom-table-columns-label", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-table-columns-label", component_property='className') ]
)
def update_axis_selector_disabled(selectedFigureType, initialClass):  
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsMultiFeatureLabelEnabled) 


@app.callback(
    Output("custom-form-feature-multi", "className"),
    [
        Input("custom-form-figure-type", "value")
    ],
    state=[ State(component_id = "custom-form-feature-multi", component_property='className') ]
)
def update_feature_multi_disabled(selectedFigureType, initialClass): 
    return util.updateSelectorDisabled(selectedFigureType, initialClass, constants.keyIsMultiFeatureEnabled)


@app.callback(
    [ Output("custom-download-main-link", 'href'),
     Output("custom-download-main-link", 'className'),
     ],
    [ Input("custom-selector-main", "value") ],
)
def update_download_link_custom_group(groupMain):
    if  not util.isValidValueId(groupMain) :
        return "", "disabled"
    
    csv_string = ""
    try:
        csv_string = util.get_download_link_data_uri( studentGrouped.getStudentsOfLearningActivityDF(int(groupMain)) )
    except Exception as e: 
        print('custom update_download_link_custom_group ')
        print(e)
    
    return csv_string, ""