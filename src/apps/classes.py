# -*- coding: utf-8 -*-

"""
Created on   Jun 11 19:04:59 2020
Reworked on  Mar 14 10:25:00 2023

@authors: tilan, zangl
"""

import math
import json
from datetime import date
import dateutil.parser
from dateutil.parser import parse

import flask
import dash_table
from dash.exceptions import PreventUpdate
import plotly.figure_factory as ff
import chart_studio.plotly as py
from plotly import graph_objs as go
import os
import util
import numpy as np
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL

from flask_login import logout_user, current_user, LoginManager, UserMixin

from app import app, login_manager, User
import constants
from data import studentGrouped

from apps import settings
import util
import subprocess


#--------------------------------- Const values START ----------------------------

feature2UserNamesDict               = constants.feature2UserNamesDict
countStudentCompletingTaskFeature   = constants.countStudentCompletingTaskFeature
countTaskCompletedByStudentFeature  = constants.countTaskCompletedByStudentFeature
featurePracticeTaskDesc             = constants.featurePracticeTaskDesc
featureTheoryTaskDesc               = constants.featureTheoryTaskDesc
featureTaskDesc                     = constants.featureTaskDesc
featureTaskType                     = constants.featureTaskType
featureDescription                  = constants.featureDescription

TaskTypePractice                    = constants.TaskTypePractice
TaskTypeTheory                      = constants.TaskTypeTheory


hasFeatures                         =  studentGrouped.hasFeatures

labelSuccess                        = constants.labelSuccess
labelFail                           = constants.labelFail

#    [  X ,  Y   ]
featurePairsToPlotSingle = [
        ['Attempts', 'Name']
        , ['Points', 'Name']
        , ['robotCollisionsBoxCount', 'Name']
        , ['CollectedCoins', 'Name']
        , ['SessionDuration', 'Name']    
        ]

featurePairsToPlotTheory = [
        ['playerShootEndEnemyHitCount', 'Name']
        , ['Points', 'Name']  
        , ['SessionDuration', 'Name']  
        , ['Attempts', 'Name']  
        ]
#--------------------------------- Const values END ----------------------------


#--------------------------------- DataBase get data START ---------------------------

dfStudentDetails                        = studentGrouped.dfStudentDetails


dfCourseDetails                         = studentGrouped.dfCourseDetails
dfSkillDetails                          = studentGrouped.dfSkillDetails
dfPracticeTaskDetails                   = studentGrouped.dfPracticeTaskDetails
dfTheoryTaskDetails                     = studentGrouped.dfTheoryTaskDetails
dfTaskDetails                           = studentGrouped.dfTaskDetails


dfGroupedPractice                       = studentGrouped.dfGroupedPractice
dfGroupedOriginal                       = studentGrouped.dfGroupedOriginal
dfPlayerStrategyPractice                = studentGrouped.dfPlayerStrategyPractice  
dfGroupedPracticeTaskWise               = studentGrouped.dfGroupedPracticeTaskWise
dfGroupedPracticeDB                     = studentGrouped.dfGroupedPracticeDB
dfRuns                                  = studentGrouped.dfRuns


dfPlayerStrategyTheory                  = studentGrouped.dfPlayerStrategyTheory
dfGroupedPlayerStrategyTheory           = studentGrouped.dfGroupedPlayerStrategyTheory

#--------------------------------- DataBase get data END ---------------------------


#---------------------------------
# school selection
SchoolSelector_options                  = studentGrouped.GroupSelector_options 

StudentSelector_students = list()

#-----------------------------------


#--------------------------- helper functions -----------------------    
getTaskWiseSuccessFail                  =  studentGrouped.getTaskWiseSuccessFail
getStudentsOfLearningActivity                     =  studentGrouped.getStudentsOfLearningActivity


getPracticeDescription                  =  studentGrouped.getPracticeDescription
getTheoryDescription                     =  studentGrouped.getTheoryDescription



def convert_list_column_tostr_NL(val) :
    separator = ',<br>'
    return separator.join(val)




#--------------------------- helper functions  END -----------------------


#------------------------------------

def plotSingleClass( titleTextAdd, school, filterByDate = '' ):
     
    graphIndex = 1
    graphs = []
    
    
        
        
        
    try :
        groupOriginal = dfGroupedOriginal.get_group(school)
        groupOriginal['CreatedAt'] = pd.to_datetime(groupOriginal['CreatedAt'])
        groupOriginal['CreatedAtDate'] = groupOriginal['CreatedAt'].dt.date
        
        if filterByDate:
            dateGroup = groupOriginal.groupby(  [ groupOriginal['CreatedAt'].dt.date ] )
            groupOriginal = dateGroup.get_group(filterByDate)
        
        try :
            groupOriginalTheory = dfGroupedPlayerStrategyTheory.get_group(school)
            groupOriginalTheory['CreatedAtDate'] = groupOriginalTheory['CreatedAt'].dt.date
            
            if filterByDate :
                dateGroup = groupOriginalTheory.groupby(  [ groupOriginalTheory['CreatedAt'].dt.date ] )
                groupOriginalTheory = dateGroup.get_group(filterByDate)
            
        except Exception as e: 
            subprocess.Popen(['echo', 'plotSingleClass 1 '])
            subprocess.Popen(['echo', str(e)])
            print('plotSingleClass 1 ')
            print(e)
        
        
        
        
#        -------------------------------------------
#            Task wise information
        
        
        graphs.append(html.Div(id='Task-Information-Classes',
                               children = [html.H2('Task Information')], 
                               className = "c-container p_medium p-top_large", 
                    ))

#---------------------------        Datatable task wise success fail    ---------------------------
        
        
        graphTitle = '(Practice)  No. of students completing a Task '
        dfTaskWiseSuccessFail = pd.DataFrame(index=np.arange(0, 1), columns=['Task', constants.featureDescription, labelSuccess, labelFail, 'SessionDuration', 'Type',
                                             'Skill', 'Course', constants.featureTaskId])
        
        
        pieDataTaskWisePractice = groupOriginal.groupby(['PracticeTaskId', 'StudentId'], as_index=False).sum()
        pieDataTaskWisePractice.loc[pieDataTaskWisePractice['Result'] > 0, 'Result'] = 1   
        pieDataTaskWisePracticeGrouped = pieDataTaskWisePractice.groupby(['PracticeTaskId'])
        
        
        index_dfTaskWiseSuccessFail = 0
        for groupKeyTaskId, groupTask in pieDataTaskWisePracticeGrouped:
            dfTaskWiseSuccessFail.loc[index_dfTaskWiseSuccessFail] =  getTaskWiseSuccessFail(groupTask, groupKeyTaskId,  dfPracticeTaskDetails, 'PracticeTaskId', 'Practice')
            index_dfTaskWiseSuccessFail += 1


        # convert column of DataFrame to Numeric Int
        dfTaskWiseSuccessFail[labelSuccess] = pd.to_numeric(dfTaskWiseSuccessFail[labelSuccess], downcast='integer')
        dfTaskWiseSuccessFail[labelFail] = pd.to_numeric(dfTaskWiseSuccessFail[labelFail], downcast='integer')
        
        
        
        table_header = [
            html.Thead(html.Tr([html.Th("Task"), html.Th(labelSuccess), html.Th(labelFail), html.Th('Session Duration(s)'), html.Th('Type'), html.Th('Skill'), html.Th('Course'), html.Th('TaskId') ]))
        ]
        rows = []
        for index, row in dfTaskWiseSuccessFail.iterrows():

            tds = []
            for feature in dfTaskWiseSuccessFail.columns:
                if not feature == constants.featureDescription :
                    tds.append( html.Td(  str(  row[feature]  )  ) )

            rows.append(  html.Tr(  tds ,
                                  className =  (   "type-practice"  if row['Type'] == constants.TaskTypePractice else "type-theory"  )
                                  ) )
            rows.append( html.Tr([ html.Td(  row[constants.featureDescription]  , colSpan  = len(dfTaskWiseSuccessFail.columns) - 1   )  ]) )
            
        
        table_body = [html.Tbody(  rows   )]
        
        table = dbc.Table(table_header + table_body, bordered=True)
        
        graphs.append(html.Div( graphTitle,
                                className= "heading-sub practice"
                    )) 
        graphs.append(html.Div(table ,
                         className = "c-table c-table-oddeven font-size_small"
                    ))
        
        
    #            CHECKED     
    #            count of students completing a task
    
    
    #       if a student passed a task once, then he is Successfull OR Result = 1    
    
        try :
            pieData = groupOriginal.groupby(['PracticeTaskId', 'StudentId'], as_index=False).sum()
            
            pieData.loc[pieData['Result'] > 0, 'Result'] = 1
        
            taskData = pieData.groupby(['PracticeTaskId'], as_index=False).sum()
            taskData = taskData.rename(columns={"Result": countStudentCompletingTaskFeature})
            taskData = taskData.merge(right= dfPracticeTaskDetails
                                              , left_on='PracticeTaskId', right_on='PracticeTaskId'
                                                , left_index=False, right_index=False
                                                , how='inner')
#            taskData[featurePracticeTaskDesc] = taskData['Title'].astype(str).str[10] + '... (Id: ' + taskData['PracticeTaskId'].astype(str) + ')' 
            taskData[featurePracticeTaskDesc] = 'Id: ' + taskData['PracticeTaskId'].astype(str) 
        
            figStudents, graphQuantile = getFeaturePlot(taskData, 
                           countStudentCompletingTaskFeature, 
                           featurePracticeTaskDesc ,
                           "(Practice)" +  ' No. of students completing a Task ', 
                           ['Title', 'PracticeTaskId'], 
                           isColored = False, hasMeanStd = False, hoverName = featurePracticeTaskDesc )
            
            graphs.append(
                    html.Div(
                        children = html.Details(
                                    children = [
                                            html.Summary([  html.I(className="fas fa-info m-right-small"),
                                            "Plot of (Practice) No. of students completing a Task " ]),
                                            html.Div(figStudents ,
                                            className = " p-top_medium "),
                                        ],
                                            className = " c-container "
                                )
                ))
            graphIndex = graphIndex + 1
        except Exception as e: 
                subprocess.Popen(['echo', 'plotSingleClass 1 '])
                subprocess.Popen(['echo', str(e)])
                print('plotSingleClass 1 ')
                print(e)
                
        try :
            
            graphTitle = '(Theory)  No. of students completing a Task '

            dfTaskWiseSuccessFailTheory = pd.DataFrame(index=np.arange(0, 1), columns=['Task', constants.featureDescription, labelSuccess, labelFail, 'SessionDuration', 'Type',
                                                'Skill', 'Course', constants.featureTaskId])
            
            index_dfTaskWiseSuccessFailTheory = 0
                    
            try :        
                pieDataTaskWiseTheory = groupOriginalTheory.groupby(['TheoryTaskId', 'StudentId'], as_index=False).sum()
                pieDataTaskWiseTheory.loc[pieDataTaskWiseTheory['Result'] > 0, 'Result'] = 1   
                pieDataTaskWiseTheoryGrouped = pieDataTaskWiseTheory.groupby(['TheoryTaskId'])
            
                for groupKeyTaskId, groupTask in pieDataTaskWiseTheoryGrouped:
                    dfTaskWiseSuccessFailTheory.loc[index_dfTaskWiseSuccessFailTheory] =  getTaskWiseSuccessFail(groupTask, groupKeyTaskId,  dfTheoryTaskDetails, 'TheoryTaskId', 'Theory')
                    index_dfTaskWiseSuccessFailTheory += 1

            except Exception as e: 
                subprocess.Popen(['echo', 'in the theory exception '])
                subprocess.Popen(['echo', str(e)])
                print('in the theory exception ')
                print(e)
            
            # convert column of DataFrame to Numeric Int
            dfTaskWiseSuccessFailTheory[labelSuccess] = pd.to_numeric(dfTaskWiseSuccessFailTheory[labelSuccess], downcast='integer')
            dfTaskWiseSuccessFailTheory[labelFail] = pd.to_numeric(dfTaskWiseSuccessFailTheory[labelFail], downcast='integer')
            
            
            
            table_header = [
                html.Thead(html.Tr([html.Th("Task"), html.Th(labelSuccess), html.Th(labelFail), html.Th('Session Duration(s)'), html.Th('Type'), html.Th('Skill'), html.Th('Course'), html.Th('TaskId') ]))
            ]
            rows = []
            for index, row in dfTaskWiseSuccessFailTheory.iterrows():

                tds = []
                for feature in dfTaskWiseSuccessFailTheory.columns:
                    if not feature == constants.featureDescription :
                        tds.append( html.Td(  str(  row[feature]  )  ) )

                rows.append(  html.Tr(  tds ,
                                    className =  (   "type-practice"  if row['Type'] == constants.TaskTypePractice else "type-theory"  )
                                    ) )
                rows.append( html.Tr([ html.Td(  row[constants.featureDescription]  , colSpan  = len(dfTaskWiseSuccessFailTheory.columns) - 1   )  ]) )
                
            
            table_body = [html.Tbody(  rows   )]
            
            table = dbc.Table(table_header + table_body, bordered=True)
            
            graphs.append(html.Div( graphTitle,
                                   className= "heading-sub theory p-top_large"
                        )) 
            graphs.append(html.Div(table ,
                            className = "c-table c-table-oddeven font-size_small"
                        ))
            


#       Plot 

            pieDataTheory = groupOriginalTheory.groupby(['TheoryTaskId', 'StudentId'], as_index=False).sum()
        
            pieDataTheory.loc[pieDataTheory['Result'] > 0, 'Result'] = 1
        
            taskDataTheory = pieDataTheory.groupby(['TheoryTaskId'], as_index=False).sum()
            taskDataTheory = taskDataTheory.rename(columns={"Result": countStudentCompletingTaskFeature})
            taskDataTheory = taskDataTheory.merge(right= dfTheoryTaskDetails
                                              , left_on='TheoryTaskId', right_on='TheoryTaskId'
                                                , left_index=False, right_index=False
                                                , how='inner')
#            taskDataTheory[featureTheoryTaskDesc] = taskDataTheory['Title'].astype(str).str[10] + '... (Id: ' + taskDataTheory['TheoryTaskId'].astype(str) + ')' 
            taskDataTheory[featureTheoryTaskDesc] = 'Id: ' + taskDataTheory['TheoryTaskId'].astype(str) 
            taskDataTheory[featureTaskType] = constants.TaskTypeTheory
            
        
            figStudents, graphQuantile = getFeaturePlot(taskDataTheory, 
                           countStudentCompletingTaskFeature, 
                           featureTheoryTaskDesc, 
                           "(Theory)" + ' No. of students completing a Task ', 
                           ['Title', 'TheoryTaskId'], 
                           isColored = True, hasMeanStd = False, hoverName = featureTheoryTaskDesc )
                     
           
            graphs.append(
                    html.Div(
                        children = html.Details(
                                    children = [
                                            html.Summary([  html.I(className="fas fa-info m-right-small"),
                                            "Plot of (Theory) no. of students completing a Task " ]),
                                            html.Div(figStudents,
                                                    className = " p-top_medium "),
                                        ],
                                            className = " c-container "
                                ) 
                ))
            graphIndex = graphIndex + 1
        
        except Exception as e: 
                subprocess.Popen(['echo', 'plotSingleClass 2 '])
                subprocess.Popen(['echo', str(e)])
                print('plotSingleClass 2 ')
                print(e)
        
        
        
    #            CHECKED
    #            count of tasks completed by each student    
        graphTitle = '(Practice) Count of tasks completed by students'
        try: 
            studentWiseDataOriginalTaskPerformed = groupOriginal
            studentWiseDataOriginalTaskPerformed[featureTaskDesc] = studentWiseDataOriginalTaskPerformed['Title'] + '-' + studentWiseDataOriginalTaskPerformed['PracticeTaskId'].astype(str)  
            studentWiseDataOriginalTaskPerformed[constants.featureTask] = constants.TaskTypePractice + '-' + studentWiseDataOriginalTaskPerformed['PracticeTaskId'].astype(str) 
            studentWiseDataOriginalTaskPerformed = studentWiseDataOriginalTaskPerformed [ studentWiseDataOriginalTaskPerformed['Result'] == 1][['StudentId', 'PracticeTaskId'
                          , 'Result', 'Name', featureTaskDesc, constants.featureTask]].groupby(
                          ['StudentId', 'Name']).agg({'PracticeTaskId': ['nunique'], featureTaskDesc: ['unique'], constants.featureTask : ['unique']})
            studentWiseDataOriginalTaskPerformed = studentWiseDataOriginalTaskPerformed.reset_index()
            studentWiseDataOriginalTaskPerformed.rename(columns={'PracticeTaskId': countTaskCompletedByStudentFeature}, inplace=True)
            studentWiseDataOriginalTaskPerformed.columns = studentWiseDataOriginalTaskPerformed.columns.droplevel(1)
            
            studentWiseDataOriginalTaskPerformed[featureTaskDesc] = studentWiseDataOriginalTaskPerformed[featureTaskDesc].apply(convert_list_column_tostr_NL)
            studentWiseDataOriginalTaskPerformed[featureTaskType] = TaskTypePractice
            
            studentWiseDataOriginalTaskPerformed = studentWiseDataOriginalTaskPerformed.sort_values(by=[ countTaskCompletedByStudentFeature ], ascending=False)
            
            table_header = [
                html.Thead(html.Tr([html.Th("Student"), html.Th("No of Tasks completed"), html.Th("Practice Tasks", className="c-table-w-content-main")
                                    ]))
            ]
            rows = []
            for index, row in studentWiseDataOriginalTaskPerformed.iterrows():
    
                tds = []
                for feature in studentWiseDataOriginalTaskPerformed[['Name',countTaskCompletedByStudentFeature, constants.featureTask, ]].columns:
                    if feature == constants.featureTask:
                        
                        tds.append( html.Td( html.Div(children = [ 
                                html.Details(
                                        children = [
                                                html.Summary(dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['Title']),
                                                html.P('Description: '  + dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['Description'] + '; Task:' + str(taskId) ),
                                                html.P('Skill: '  + dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['TitleSkill']),
                                                html.P('Course: '  + dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['TitleCourse']),
                                            ],
                                            className = " c-details practice "
                                    )
                                  for taskId in 
                                                                  list(row[feature]) ] ), 
                                        className="c-table-w-content-main"  ) )
                    else:
                        tds.append( html.Td(  str(  row[feature]  )  ) )
                        
    
                rows.append(  html.Tr(  tds ,
#                                      className =  (   "type-practice"  if row[featureTaskType] == constants.TaskTypePractice else "type-theory"  )
                                      ) )
            
            table_body = [html.Tbody(  rows   )]
            
            table = dbc.Table(table_header + table_body, bordered=True)
            
            
            graphs.append(html.Div( graphTitle,
                                   className= "heading-sub practice  p-top_large"
                        )) 
            '''
            graphs.append(html.Div(table ,
                             className = "c-table c-table-oddeven font-size_small"
                        ))
            '''

            graphs.append(
                html.Div(
                        html.Details(
                            children = [
                                    html.Summary([  html.I(className="fas fa-info m-right-small"),
                                    "Data : " + graphTitle ]),
                                    html.Div(table ,
                                            className = "c-table c-table-oddeven font-size_small p-top_medium"
                                        ),
                                ],
                                className = "  c-container  "
                        ),
                    className = " p-top_small "))  

        except Exception as e:   
            subprocess.Popen(['echo', 'ERROR - ' + graphTitle])
            subprocess.Popen(['echo', str(e)])          
            print( 'ERROR - ' + graphTitle )
            print(e)
        
        graphTitle = '(Theory) Count of tasks completed by students'
        try: 
            studentWiseDataOriginalTaskPerformedTheory = groupOriginalTheory
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory.merge(right= dfTheoryTaskDetails
                                              , left_on='TheoryTaskId', right_on='TheoryTaskId'
                                                , left_index=False, right_index=False
                                                , how='inner')
            studentWiseDataOriginalTaskPerformedTheory[featureTaskDesc] = studentWiseDataOriginalTaskPerformedTheory['Title'] + '-' +  studentWiseDataOriginalTaskPerformedTheory['TheoryTaskId'].astype(str)
            studentWiseDataOriginalTaskPerformedTheory[constants.featureTask] = constants.TaskTypeTheory + '-' +  studentWiseDataOriginalTaskPerformedTheory['TheoryTaskId'].astype(str)
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory [ studentWiseDataOriginalTaskPerformedTheory['Result'] == 1][['StudentId', 'TheoryTaskId'
                          , 'Result', 'Name', featureTaskDesc, constants.featureTask]].groupby(
                          ['StudentId', 'Name']).agg({'TheoryTaskId': ['nunique'], featureTaskDesc: ['unique'], constants.featureTask : ['unique'], })
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory.reset_index()
            studentWiseDataOriginalTaskPerformedTheory.rename(columns={'TheoryTaskId': countTaskCompletedByStudentFeature}, inplace=True)
            studentWiseDataOriginalTaskPerformedTheory.columns = studentWiseDataOriginalTaskPerformedTheory.columns.droplevel(1)
            studentWiseDataOriginalTaskPerformedTheory[featureTaskDesc] = studentWiseDataOriginalTaskPerformedTheory[featureTaskDesc].apply(convert_list_column_tostr_NL)
            studentWiseDataOriginalTaskPerformedTheory[featureTaskType] = TaskTypeTheory
            
            
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory.sort_values(by=[ countTaskCompletedByStudentFeature ], ascending=False)
            
            table_header = [
                html.Thead(html.Tr([html.Th("Student"), html.Th("No of Tasks completed"), html.Th("Theory Tasks", className="c-table-w-content-main")
                                    ]))
            ]
            rows = []
            for index, row in studentWiseDataOriginalTaskPerformedTheory.iterrows():
    
                tds = []
                for feature in studentWiseDataOriginalTaskPerformedTheory[['Name',countTaskCompletedByStudentFeature, constants.featureTask, ]].columns:
                    if feature == constants.featureTask:                        
                        tds.append( html.Td( html.Div(children = [ 
                                        html.Details(
                                                children = [
                                                        html.Summary(dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['Title']),
                                                        html.P( ' Description: '  + dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['Description'] + '; Task:' + str(taskId)  ),
                                                        html.P('Skill: '  + dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]['TitleSkill']),
                                                    ],
                                                    className = " c-details theory "
                                            )
                                          for taskId in 
                                                                  list(row[feature]) ] ), 
                                        className="c-table-w-content-main"  ) )
                    else:
                        tds.append( html.Td(  str(  row[feature]  )  ) )
                        
    
                rows.append(  html.Tr(  tds ,
#                                      className =  (   "type-practice"  if row[featureTaskType] == constants.TaskTypePractice else "type-theory"  )
                                      ) )
            
            table_body = [html.Tbody(  rows   )]
            
            table = dbc.Table(table_header + table_body, bordered=True)
            
            
            graphs.append(html.Div( graphTitle,
                                   className= "heading-sub theory p-top_large"
                        )) 

            graphs.append(html.Div(html.Details(
                        children = [
                                html.Summary([  html.I(className="fas fa-info m-right-small"),
                                "Data : " + graphTitle ]),
                                html.Div(table ,
                                        className = "c-table c-table-oddeven font-size_small p-top_medium"
                                ),
                            ],
                            className = " c-container  "
                    ),
                    className = " p-top_small  p-bottom_x-large "))           
            
        except Exception as e: 
            subprocess.Popen(['echo', 'ERROR - ' + graphTitle ])
            subprocess.Popen(['echo', str(e)])
            print( 'ERROR - ' + graphTitle )  
            print(e)
        
        

    except Exception as e: 
        subprocess.Popen(['echo', 'ERROR - plotSingleClass '])
        subprocess.Popen(['echo', str(e)])
        print( 'ERROR - plotSingleClass ')
        print(e)

    return graphs        




    
    

    
#-------------------------------------------------
#GENERAL INFORMATION SECTION
#------------------------------------------------------

#        CHECKED
#            for concepts used
featureX = 'Count (no. of students used)'
featureY = 'Details'
featurePracticeTaskGroup = 'Task-Id'            

def getGroupTaskWiseDetails(groupId, isGrouped = True, taskId = 0 , filterByDate = '' ) :
    
    graphs = []
    
#   Step 1 : add the code of each student in table
    try :
        currentGroupData = dfGroupedOriginal.get_group(groupId)
        
        if filterByDate:
            dateGroup = currentGroupData.groupby(  [ currentGroupData['CreatedAt'].dt.date ] )
            currentGroupData = dateGroup.get_group(filterByDate)
        
        
        currentGroupDataNoDup = currentGroupData.drop_duplicates(subset=['PracticeTaskId', 'StudentId'], keep='last')
        
        taskWiseConceptPracticeGrouped = currentGroupDataNoDup.groupby(['PracticeTaskId'])
        
        featureToPlotTask = ['Name', 'Code', 'SessionDuration']
        
        if not taskId is None and  taskId > 0 and taskId in taskWiseConceptPracticeGrouped.groups.keys():
            taskData = taskWiseConceptPracticeGrouped.get_group(taskId)
            
            headThs = []
            for feat in featureToPlotTask:
                headThs.append(html.Th(feat))
            
            table_header = [
                html.Thead(html.Tr( headThs  ))
            ]
            
            rows = []
            for index, row in taskData.iterrows():
    
                tds = []
                for feature in featureToPlotTask:
                    if feature == "Code":
                        codeWithBreaks = str(  row[feature]  ).split('\n')
                        codeLined = []
                        for codeLine in codeWithBreaks:
                            codeLined.append( html.Pre( html.Span(codeLine) ,
                                                       className = "c-pre" 
                                                ))
                        
                        tds.append( html.Td(  codeLined  ) )
                    else :
                        tds.append( html.Td(  str(  row[feature]  )  ) )
    
                rows.append(  html.Tr(  tds 
                                      ) )

            table_body = [html.Tbody(  rows   )]            
            table = dbc.Table(table_header + table_body, bordered=True)
            
            graphs.append(html.Div(table ,
                             className = "c-table c-table-oddeven font-size_small m-top_small"
                        ))
            
            
            
              
            
    except Exception as e: 
                subprocess.Popen(['echo', 'plotGroupTaskWiseConcepts 1 '])
                subprocess.Popen(['echo', str(e)])
                print('plotGroupTaskWiseConcepts 1 ')
                print(e)
            
    try:    
    #    Step 2 :- add the plot - concepts used by count of students
        graphs = graphs + plotGroupTaskWiseConcepts( groupId, isGrouped = isGrouped, taskId = taskId , filterByDate = filterByDate)    
    except Exception as e: 
        subprocess.Popen(['echo', 'plotGroupTaskWiseConcepts 2 '])
        subprocess.Popen(['echo', str(e)])
        print('plotGroupTaskWiseConcepts 2 ')
        print(e)
    
    return graphs
    
    
def plotGroupTaskWiseConcepts(groupId, isGrouped = True, taskId = 0 , filterByDate = '' ) :
    
    graphs = []
    
    try :
        currentGroupData = dfGroupedOriginal.get_group(groupId)
        
        if filterByDate:
            dateGroup = currentGroupData.groupby(  [ currentGroupData['CreatedAt'].dt.date ] )
            currentGroupData = dateGroup.get_group(filterByDate)


        currentGroupDataNoDup = currentGroupData.drop_duplicates(subset=['PracticeTaskId', 'StudentId'], keep='last')

        taskWiseConceptPracticeGrouped = currentGroupDataNoDup.groupby(['PracticeTaskId'])
        
        
        studentWiseTaskWiseConceptPractice = pd.DataFrame()
        
        
        if not taskId is None and  taskId > 0 and taskId in taskWiseConceptPracticeGrouped.groups.keys():
            
            groupTask = taskWiseConceptPracticeGrouped.get_group(taskId)
        
            studentWiseDataConceptsTask = groupTask.sum()
            
            colY = hasFeatures
           
            studentWiseDataConceptsTask = pd.DataFrame(studentWiseDataConceptsTask)
            studentWiseDataConceptsTask['PracticeTaskId'] = taskId
            studentWiseDataConceptsTask['Title'] = dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == taskId ]['Title'].astype(str).values[0]
            studentWiseDataConceptsTask[featurePracticeTaskGroup] = constants.TaskTypePractice + '-' +  str(taskId)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask.index
            studentWiseDataConceptsTask = studentWiseDataConceptsTask.rename(columns={0: featureX})
            studentWiseDataConceptsTask.drop(studentWiseDataConceptsTask[~studentWiseDataConceptsTask[featureY].isin(colY)].index, inplace = True)
            
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].astype(str)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].replace(
                    {r'\b{}\b'.format(k):v for k, v in feature2UserNamesDict.items()} , regex=True  )
            
            taskTitle = str(taskId)
            try :
                taskTitle =  dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == taskId ]['Title'].astype(str).values[0]
            except Exception as e: 
                subprocess.Popen(['echo', 'plotGroupTaskWiseConcepts 1 '])
                subprocess.Popen(['echo', str(e)])
                print('plotGroupTaskWiseConcepts 1 ')
                print(e)
                
            figBar = px.bar(studentWiseDataConceptsTask
                                , x             =   featureX
                                , y             =   featureY
                                , orientation   =  'h'
                                , height        =   constants.graphHeight - 100
                                , template      =   constants.graphTemplete   
                                , title         =   "(Practice) Concepts used by students in task " + str(taskId) + '(TaskId)'+ "<br>" + str(taskTitle)  +   " (no. of students used a concept in code)"
                                , labels        =   feature2UserNamesDict # customize axis label
                )
            
            graphs.append(
            
                dcc.Graph(
                    figure= figBar
                )
            
                if  constants.languageLocal  != 'en' else
            
                dcc.Graph(
                    figure= figBar
                     
                    , config  =  dict (locale   =  constants.languageLocal   ) 
                )
                    
            ) 
            
            return graphs


#  for Grouped data !!!
        for groupKeyTaskId, groupTask in taskWiseConceptPracticeGrouped:
            
            studentWiseDataConceptsTask = groupTask.sum()
            
            colY = hasFeatures
           
            studentWiseDataConceptsTask = pd.DataFrame(studentWiseDataConceptsTask)
            studentWiseDataConceptsTask['PracticeTaskId'] = groupKeyTaskId
            studentWiseDataConceptsTask['Title'] = dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == int(groupKeyTaskId) ]['Title'].astype(str).values[0]
            studentWiseDataConceptsTask[featurePracticeTaskGroup] = constants.TaskTypePractice + '-' +  str(groupKeyTaskId)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask.index
            studentWiseDataConceptsTask = studentWiseDataConceptsTask.rename(columns={0: featureX})
            studentWiseDataConceptsTask.drop(studentWiseDataConceptsTask[~studentWiseDataConceptsTask[featureY].isin(colY)].index, inplace = True)
            
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].astype(str)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].replace(
                    {r'\b{}\b'.format(k):v for k, v in feature2UserNamesDict.items()} , regex=True  )
            
            if studentWiseTaskWiseConceptPractice is None or studentWiseTaskWiseConceptPractice.empty:
                studentWiseTaskWiseConceptPractice = studentWiseDataConceptsTask
            else:
                studentWiseTaskWiseConceptPractice = pd.concat([studentWiseTaskWiseConceptPractice, studentWiseDataConceptsTask], ignore_index=True)


            taskTitle = str(groupKeyTaskId)
            try :
                taskTitle =  dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == int(groupKeyTaskId) ]['Title'].astype(str).values[0]
            except Exception as e: 
                subprocess.Popen(['echo', 'plotGroupTaskWiseConcepts 1 last '])
                subprocess.Popen(['echo', str(e)])
                print('plotGroupTaskWiseConcepts 1 last ')
                print(e)
        
        if isGrouped:
            figGroupedTaskConcepts = px.bar(studentWiseTaskWiseConceptPractice
                                , x             =   featureY
                                , y             =   featureX
                                , height        =   constants.graphHeight - 100
                                , hover_data    =  [ 'Title', 'PracticeTaskId',  ]
                                , template      =   constants.graphTemplete   
                                , title         =   "(Practice) Concepts used by students in each task <br> (no. of students used a concept in code for a task)"
                                , labels        =   feature2UserNamesDict # customize axis label
                                , color         =   featurePracticeTaskGroup
                                , barmode       =   'group'
                )
            return figGroupedTaskConcepts
                
        return graphs
    except Exception as e: 
        subprocess.Popen(['echo', 'plotGroupTaskWiseConcepts  last '])
        subprocess.Popen(['echo', str(e)])
        print('plotGroupTaskWiseConcepts  last ')
        print(e)               


def getGroupPTaskDoneOptions(groupId , filterByDate = '' ) :
    options = []
    
    try :
        currentGroupData = dfGroupedOriginal.get_group(groupId)
        
        if filterByDate:
            dateGroup = currentGroupData.groupby(  [ currentGroupData['CreatedAt'].dt.date ] )
            currentGroupData = dateGroup.get_group(filterByDate)

        
        
        currentGroupDataNoDup = currentGroupData.drop_duplicates(subset=['PracticeTaskId', 'StudentId'], keep='last')
        
        taskWiseConceptPracticeGrouped = currentGroupDataNoDup.groupby(['PracticeTaskId']) 
        
        
        for groupKeyTaskId, groupTask in taskWiseConceptPracticeGrouped:            
            options.append({
                    'label' : dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == int(groupKeyTaskId) ]['Title'].astype(str).values[0] + ' (TaskId ' + str(groupKeyTaskId) + ')',
                    'value' : groupKeyTaskId
                    
            })
                    
        return options
    except Exception as e: 
        subprocess.Popen(['echo', 'getGroupPTaskDoneOptions'])
        subprocess.Popen(['echo', str(e)])
        print('getGroupPTaskDoneOptions')
        print(e)    
    
    return options



        
        
        
def plotGroupConceptDetails(groupId, filterByDate = '' ):
    
    graphs = []
    
    graphs.append(html.Div(id='Concept-Information-Classes',
                           children = [html.H2('Concept Information')], 
                           className = "c-container p_medium p-top_large", 
                ))
      
    try :
        groupPractice = dfGroupedPractice.get_group(groupId)
        
        if filterByDate:
            dateGroup = groupPractice.groupby(  [ groupPractice['CreatedAt'].dt.date ] )
            groupPractice = dateGroup.get_group(filterByDate)
        
        
        
#       sum - to get count of students who used the concept
        studentWiseDataConcepts = groupPractice.sum()
               
        colY = hasFeatures
       
        studentWiseDataConcepts = pd.DataFrame(studentWiseDataConcepts)
        studentWiseDataConcepts[featureY] = studentWiseDataConcepts.index
        studentWiseDataConcepts = studentWiseDataConcepts.rename(columns={0: featureX})
        studentWiseDataConcepts.drop(studentWiseDataConcepts[~studentWiseDataConcepts[featureY].isin(colY)].index, inplace = True)
        
        studentWiseDataConcepts[featureY] = studentWiseDataConcepts[featureY].astype(str)
        studentWiseDataConcepts[featureY] = studentWiseDataConcepts[featureY].replace(
                    {r'\b{}\b'.format(k):v for k, v in feature2UserNamesDict.items()} , regex=True  )
        
        
        figBar = px.bar(studentWiseDataConcepts
                            , x             =   featureX
                            , y             =   featureY
                            , orientation   =  'h'
                            , height        =   constants.graphHeight - 100
                            , template      =   constants.graphTemplete   
                            , title         =   "(Practice) Concepts used by students of this class (no. of students using a concept in code)"
                            , labels        =   feature2UserNamesDict # customize axis label
            )
        graphs.append(
            
                dcc.Graph(
                    figure= figBar
                )
            
                if  constants.languageLocal  != 'en' else
            
                dcc.Graph(
                    figure= figBar
                     
                    , config  =  dict (locale   =  constants.languageLocal   ) 
                )
        )
        
#       Task wise concepts used - grouped together
        try :
            figBar = plotGroupTaskWiseConcepts(groupId, isGrouped = True, taskId = 0, filterByDate = filterByDate )
            
            graphs.append(
                html.Div(html.Details(
                            children = [
                                    html.Summary([  html.I(className="fas fa-info m-right-small"),
                                    "Concepts used by students in each task"  ]),
                                    html.Div(
                                        dcc.Graph(
                                            figure= figBar
                                        )
                                    
                                        if  constants.languageLocal  != 'en' else
                                    
                                        dcc.Graph(
                                            figure= figBar
                                            
                                            , config  =  dict (locale   =  constants.languageLocal   ) 
                                        )
                                    ),
                            ],
                            className = "c-container p-top_large p-bottom_large"
            )))     

        except Exception as e: 
                subprocess.Popen(['echo', 'Task Concepts used'])
                subprocess.Popen(['echo', str(e)])
                print('Task Concepts used')
                print(e)                
      
    except Exception as e: 
            subprocess.Popen(['echo', 'Task Concepts used'])
            subprocess.Popen(['echo', str(e)])
            print('Task Concepts used')
            print(e)

    return graphs


def getFeaturePlot(df, featureX, featureY, title, hoverData, isColored = False, hasMeanStd = True, hoverName = "Name", hasDistribution = False, isThemeSizePlot = False):
    graphs = []
    
    graphHeightD = df.shape[0] * 20
    graphHeightD = 400 if (graphHeightD < 400) else (constants.graphHeight if (graphHeightD < (constants.graphHeight + 200) ) else graphHeightD )
    
    if isColored:
        try :
            
            df = df.sort_values(    by  =   [ featureX ]    )
            
            
            if isThemeSizePlot : 
                 fig = px.bar( df
                    , x             =   featureX
                    , y             =   featureY
                    , title         =   title
                    , labels        =   feature2UserNamesDict # customize axis label
                    , template      =   constants.graphTemplete                              
                    , orientation   =   'h'
                    , hover_name    =   hoverName
                    , hover_data    =   hoverData
                    , color         =   constants.featureTaskType
                    , height        =   constants.graphHeight
                    , color_discrete_map     =   {
                        constants.TaskTypeTheory    : constants.colorTheory,
                        constants.TaskTypePractice  : constants.colorPractice, },
                )
                    
            else:
                fig = px.bar( df
                    , x             =   featureX
                    , y             =   featureY
                    , title         =   title
                    , labels        =   feature2UserNamesDict # customize axis label
                    , template      =   constants.graphTemplete                              
                    , orientation   =   'h'
                    , hover_name    =   hoverName
                    , hover_data    =   hoverData
                    , height        =   graphHeightD
                    , color         =   constants.featureTaskType
                    , color_discrete_map     =   {
                        constants.TaskTypeTheory    : constants.colorTheory,
                        constants.TaskTypePractice  : constants.colorPractice, },
                )
            
            graphs.append(
            
                dcc.Graph(
                    figure= fig
                )
            
                if  constants.languageLocal  != 'en' else
            
                dcc.Graph(
                    figure= fig
                     
                    , config  =  dict (locale   =  constants.languageLocal   ) 
                )
            )
        except Exception as e: 
            subprocess.Popen(['echo', 'getFeaturePlot  1st  '])
            subprocess.Popen(['echo', 'title  ' + title])
            subprocess.Popen(['echo', str(e)])
            print('getFeaturePlot  1st  ')
            print('title  ' + title)
            print(e)
        
    else:    
        try :
            
            df = df.sort_values(by=[ featureX ])
            
            
            if isThemeSizePlot : 
                fig = px.bar( df
                    , x             =  featureX
                    , y             =  featureY
                    , title         = title
                    , labels        = feature2UserNamesDict # customize axis label
                    , template      = constants.graphTemplete                              
                    , orientation   = 'h'
                    , hover_name    =  hoverName
                    , hover_data    =  hoverData
                    , height        =   constants.graphHeight
                )
                    
            else:
                fig = px.bar( df
                    , x             =  featureX
                    , y             =  featureY
                    , title         = title
                    , labels        = feature2UserNamesDict # customize axis label
                    , template      = constants.graphTemplete                              
                    , orientation   = 'h'
                    , hover_name    =  hoverName
                    , hover_data    =  hoverData
                    , height        =  graphHeightD
                )
                
            graphs.append(
                dcc.Graph(
                    figure= fig
                )
            
                if  constants.languageLocal  != 'en' else
            
                dcc.Graph(
                    figure= fig
                     
                    , config  =  dict (locale   =  constants.languageLocal   ) 
                )
            )
        except Exception as e: 
            subprocess.Popen(['echo', 'getFeaturePlot  2nd  '])
            subprocess.Popen(['echo', 'title  ' + title])
            subprocess.Popen(['echo', str(e)])
            print('getFeaturePlot  2nd  ')
            print('title  ' + title)
            print(e)
                    
    
    
                    
                    
                    
                
                    
                    
                    
    graphDistributions = []
      
    try :
        if hasDistribution :
            if hasMeanStd :
                figMean = df.mean().round(decimals=2)[featureX]
                figStd = df.std().round(decimals=2)[featureX]
                graphDistributions.append(
                        html.Div(children=[
                                html.P('Mean ' + ((constants.feature2UserNamesDict.get(featureX)) if featureX in constants.feature2UserNamesDict.keys() else featureX )  + ' = ' + str(figMean) ),
                                html.P('Std. ' + ((constants.feature2UserNamesDict.get(featureX)) if featureX in constants.feature2UserNamesDict.keys() else featureX )  + ' = ' + str(figStd) ),
                                ])
                )
                         
            figQuantile = px.box(df, 
                                 y                      =   featureX, 
                                 points                 =   "all",
                                 title                  =   "Distribution  - " + title,
                                 hover_data             =   ['Name'] + hoverData,
                                 labels                 =   feature2UserNamesDict , # customize axis label
                                 height                 =   constants.graphHeightMin,
                                 template               =   constants.graphTemplete ,     
                                 color                  =   constants.featureTaskType ,
                                 color_discrete_map     =   {
                                    constants.TaskTypeTheory    : constants.colorTheory,
                                    constants.TaskTypePractice  : constants.colorPractice, 
                                    },
                )
                
            figQuantile.update_layout(constants.THEME_EXPRESS_LAYOUT)
            graphDistributions.append( html.Div( 
                    
                    
                dcc.Graph(
                    figure= figQuantile
                )
            
                if  constants.languageLocal  != 'en' else
            
                dcc.Graph(
                    figure= figQuantile
                     
                    , config  =  dict (locale   =  constants.languageLocal   ) 
                )
                
            ))
    except Exception as e: 
        subprocess.Popen(['echo', 'getFeaturePlot  hasDistribution '])
        subprocess.Popen(['echo', str(e)])
        print('getFeaturePlot  hasDistribution ')
        print('title  ' + title)
        print(e)
        
        
    return graphs, graphDistributions


def plotSingleClassGeneral( titleTextAdd, school, filterByDate = '' ):
    
    graphs = []
    graphsMain = []
    
    graphsMain.append(html.Div(id='General-Information-Classes',
                       children = [html.H2('Class Statistics')], 
                       className = "c-container p_medium p-top_large", 
            ))
    
      
    featuresPractice            = dfPlayerStrategyPractice.columns
                             
    
    
        
     
        
    try :
        groupPractice = dfGroupedPractice.get_group(school)
        groupOriginal = dfGroupedOriginal.get_group(school)
        
        if filterByDate:
            dateGroup = groupPractice.groupby(  [ groupPractice['CreatedAt'].dt.date ] )
            groupPractice = dateGroup.get_group(filterByDate)
            dateGroup = groupOriginal.groupby(  [ groupOriginal['CreatedAt'].dt.date ] )
            groupOriginal = dateGroup.get_group(filterByDate)

        
        
        try :
            groupOriginalTheory = dfGroupedPlayerStrategyTheory.get_group(school)
            
            if filterByDate :
                dateGroup = groupOriginalTheory.groupby(  [ groupOriginalTheory['CreatedAt'].dt.date ] )
                groupOriginalTheory = dateGroup.get_group(filterByDate)
        except Exception as e: 
            subprocess.Popen(['echo', ' plotSingleClassGeneral  groupOriginalTheory value set error '])
            subprocess.Popen(['echo', str(e)])
            print(' plotSingleClassGeneral  groupOriginalTheory value set error ')
            print(e)
        
        
        #            2. other features    
        #   Combined Plots         
        
#              Practice Data
        studentWiseData = groupPractice.groupby(['StudentId'], as_index=False).sum()
        
        studentWiseData = studentWiseData.merge(right= dfPlayerStrategyPractice[['StudentId', "Result", 'ConceptsUsed', 'ConceptsUsedDetails', 'Name', "lineOfCodeCount", "Code"]]
                                                , left_index=False, right_index=False
                                                , how='inner')
        
#        studentWiseData['ConceptsUsedDetailsStr']= studentWiseData['ConceptsUsedDetails'].apply(lambda x: x[1:-1])
        studentWiseData['ConceptsUsedDetailsStr']= studentWiseData['ConceptsUsedDetails']
        
        studentWiseData.reset_index(drop=True, inplace=True)
        
        studentWiseData[countTaskCompletedByStudentFeature] = studentWiseData['Result']
        
        del studentWiseData['Attempts']
        del studentWiseData['SessionDuration']
        del studentWiseData['Result']
        
        studentWiseDataOriginal = groupOriginal.groupby(['StudentId'], as_index=False).sum()
        studentWiseData = studentWiseData.merge(right= studentWiseDataOriginal[['StudentId', "Attempts", 'SessionDuration', 'Result']]
                                                , left_on='StudentId', right_on='StudentId'
                                                , left_index=False, right_index=False
                                                , how='inner')  
        
        
        studentWiseData[featureDescription] = getPracticeDescription(studentWiseData)
        studentWiseData[constants.featureTaskType] = constants.TaskTypePractice
        
        
        
        try :
            studentWiseDataTheory =  groupOriginalTheory.groupby(['StudentId'], as_index=False).sum()
            studentWiseDataTheory.reset_index(drop=True, inplace=True)
            
            studentWiseDataTheory[countTaskCompletedByStudentFeature] = studentWiseDataTheory['Result']
            
            studentWiseDataTheory = studentWiseDataTheory.merge(right= dfStudentDetails[['StudentId', 'Name']]
                                            , left_on='StudentId', right_on='StudentId'
                                            , left_index=False, right_index=False
                                            , how='inner')
            
#            if need to add a MEAN column values
#            studentWiseDataTheoryMean =  groupOriginalTheory.groupby(['StudentId'], as_index=False).sum()
#            studentWiseDataTheory['Attempts'] = studentWiseDataTheory['StudentId'].map(studentWiseDataTheoryMean.set_index('StudentId')['Attempts'])
            
            studentWiseDataTheory[featureDescription] = getTheoryDescription(studentWiseDataTheory)
            studentWiseDataTheory[constants.featureTaskType] = constants.TaskTypeTheory
            
            #Drop duplicates keeping only the first row for Student and Task
            studentWiseDataTheory = studentWiseDataTheory.drop_duplicates(subset=['StudentId'], keep='first')
            
            
        except Exception as e: 
            subprocess.Popen(['echo', ' plotSingleClassGeneral  studentWiseDataTheory value set error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! '])
            subprocess.Popen(['echo', str(e)])
            print(' plotSingleClassGeneral  studentWiseDataTheory value set error !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ')
            print(e)
        
    #            2. other features        
    
        hoverDataPractice   = ["SessionDuration", "Points", "Attempts", "Result", "CollectedCoins", "robotCollisionsBoxCount", "ConceptsUsedDetailsStr", "lineOfCodeCount", 'StudentId']
        hoverDataTheory     = ["SessionDuration", "Points", "Attempts", "Result", "itemsCollectedCount", "playerShootEndEnemyHitCount", 'StudentId']
                

        quantileIndex = 0
                          
        for first in range(featuresPractice.size):
                
            for second in  range(featuresPractice.size):
                if ([featuresPractice[first], featuresPractice[second]] in featurePairsToPlotSingle):                
            
                    if featuresPractice[first] != featuresPractice[second] :            
    
    #                           for setting title        
                        titleFirst = featuresPractice[first]
                        if featuresPractice[first] in feature2UserNamesDict:
                            titleFirst = feature2UserNamesDict.get(featuresPractice[first])
                        
                        #    Graphs for both THEORY & PRACTICE                        
                        if ([featuresPractice[first], featuresPractice[second]] in  featurePairsToPlotTheory):  
                            
                            
                            featurePlot, graphDistributions = getFeaturePlot(studentWiseData, featuresPractice[first], featuresPractice[second], 
                                                                   '(Practice) Details of students ' + titleFirst,
                                                                   hoverDataPractice,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                            
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )
                            graphs.append(  html.Div( getPlotDistributionPlotChildrens(graphDistributions, quantileIndex) ,
                                className = "c-container"
                            ))
                            quantileIndex += 1
                            
                            
                            dfTheory2Plot = studentWiseDataTheory.groupby(['StudentId', 'Name', 'TaskType'], as_index=False).sum()
                            featurePlot, graphDistributions = getFeaturePlot(dfTheory2Plot, featuresPractice[first], featuresPractice[second], 
                                                                   '(Theory) Details of students ' + titleFirst,
                                                                   hoverDataTheory, 
                                                                   isColored = True,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )
                            graphs.append(  html.Div( getPlotDistributionPlotChildrens(graphDistributions, quantileIndex) ,
                                className = "c-container"
                            ))
                            quantileIndex += 1
                         
#    Graphs only for PRACTICE
                        if ([featuresPractice[first], featuresPractice[second]] not in  featurePairsToPlotTheory):    
                            featurePlot, graphDistributions = getFeaturePlot(studentWiseData, featuresPractice[first], featuresPractice[second], 
                                                                   '(Practice) Details of students ' + titleFirst,
                                                                   hoverDataPractice,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )
                            graphs.append(  html.Div( getPlotDistributionPlotChildrens(graphDistributions, quantileIndex) ,
                                className = "c-container"
                            ))
                            quantileIndex += 1
    
#    Graphs only for THEORY
        for rowTheory in featurePairsToPlotTheory : 
            if (rowTheory not in featurePairsToPlotSingle) :
                
                try :
                    #                           for setting title  
                    titleFirst = rowTheory[0]
                    if rowTheory[0] in feature2UserNamesDict:
                        titleFirst = feature2UserNamesDict.get(rowTheory[0])  
                        
                    dfTheory2Plot = studentWiseDataTheory.groupby(['StudentId', 'Name', 'TaskType'], as_index=False).sum()
                    featurePlot, graphDistributions = getFeaturePlot(dfTheory2Plot, rowTheory[0], rowTheory[1] , 
                                                                   '(Theory) Details of students ' + titleFirst,
                                                                   hoverDataTheory, isColored = True,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                    
                    graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                    )
                    graphs.append(  html.Div(getPlotDistributionPlotChildrens(graphDistributions, quantileIndex) ,
                        className = "c-container"
                    ))
                    quantileIndex += 1
                    
                except Exception as e: 
                    subprocess.Popen(['echo', ' plotSingleClassGeneral  rowTheory Theory plots '])
                    subprocess.Popen(['echo', str(e)])
                    print(' plotSingleClassGeneral  rowTheory Theory plots ')
                    print(e)


    except Exception as e: 
        subprocess.Popen(['echo', str(e)])
        print(e)

    graphsMain.append(
        html.Div(html.Details(
                    children = [
                            html.Summary([  html.I(className="fas fa-info m-right-small"),
                            "General Information "  ]),
                            html.Div(
                                graphs,
                                className = " p-top_medium "
                            ),
                    ],
                    className = "c-container "
    )))     
    
    return graphsMain      


def getPlotDistributionPlotChildrens(graphDistributions, quantileIndex = 0):
    return [
        html.Details(
            children = [
                    html.Summary([  html.I(className="fas fa-info m-right-small"),
                    "Distribution" ]),
                    html.Div(graphDistributions),
                ],
        ),
    ]


#Student Interaction with Game - TIMELINE
def plotClassOverview(schoolKey, filterByDate = '' ):
    
    graphs = []
    rows = []
    columns = []

    features2Plot = ['Name', 'SessionDuration', 'PracticeSessionDuration', 'TheorySessionDuration', 
                     'Attempts', 'Points' 
                     ]

    try:    
        studentDataDf = studentGrouped.getStudentsOfLearningActivityDF(schoolKey)
        
        if filterByDate:
            dateGroup = studentDataDf.groupby(  [ studentDataDf['CreatedAt'].dt.date ] )
            studentDataDf = dateGroup.get_group(filterByDate)

        
        if studentDataDf is None    or   studentDataDf.empty :
            graphs.append(
                    util.getNoDataMsg()
            )
            return graphs
        
        
        studentDataDfSum = studentDataDf.groupby(['StudentId', 'Name'], as_index=False).sum()
        
        studentDataDfSumTask = studentDataDf.groupby(['StudentId', 'Name', constants.TASK_TYPE_FEATURE
                                                ], as_index=False)

        studentDataDfFeaturesInterpreted = pd.DataFrame(columns = ['StudentId', 'PracticeSessionDuration', 'TheorySessionDuration']) 
        for groupKey, group in studentDataDfSumTask :        
            practiceSessionDuration = group[group[constants.TASK_TYPE_FEATURE] ==  constants.TaskTypePractice ]['SessionDuration'].sum()        
            theorySessionDuration =  group[group[constants.TASK_TYPE_FEATURE] == constants.TaskTypeTheory ]['SessionDuration'].sum()            
            studentDataDfFeaturesInterpreted = studentDataDfFeaturesInterpreted.append({'StudentId' : groupKey[0], 
                                                                                        'PracticeSessionDuration' : practiceSessionDuration, 
                                                                                        'TheorySessionDuration' : theorySessionDuration},  
                                                                                ignore_index = True)       
        studentDataDfFeaturesInterpreted = studentDataDfFeaturesInterpreted.groupby(['StudentId'],  as_index=False).sum()
            
        studentDataDfSum = studentDataDfSum.merge(right= studentDataDfFeaturesInterpreted
                                        , left_on='StudentId', right_on='StudentId'
                                            , left_index=False, right_index=False
                                            , how='inner')
        
        fig1Table = dash_table.DataTable(
            columns=[
                {"name": constants.feature2UserNamesDict.get(i) if i in constants.feature2UserNamesDict.keys() else i , "id": i, "selectable": True} for i in studentDataDfSum[features2Plot].columns
            ],
            data            = studentDataDfSum[features2Plot].to_dict('records'),
            filter_action       = "native",
            sort_action         = "native",
            sort_mode           = "multi",
            style_data_conditional = ([ 
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': constants.THEME_TABLE_ODDROW_COLOR_STYLE
                    },
            ]) 
        )

        columns.append(dbc.Col(
                        html.Details(
                                    children = [
                                            html.Summary([  html.I(className="fas fa-info m-right-small"),
                                            "Overview data " ]),
                                            html.Div(fig1Table, 
                                                    className = " p-top_medium  "),
                                        ],
                                            className = " c-container  p-top_medium  p-bottom_medium  "
                                )  
                        , align ="center"                    
                        , className = "c-table "
        ))
        rows.append( dbc.Row( columns ) )
        
#    ---------------------------------------------
            
        graphs.append(html.Div(  rows  ))
    except Exception as e: 
        subprocess.Popen(['echo', 'plotClassOverview 2 '])
        subprocess.Popen(['echo', str(e)])
        print('plotClassOverview 2 ')
        print(e)

    return graphs


def plotGroupOverview(groupId, filterByDate = '' ):
    plots               = []
    try:    
        groupStudents     =  getStudentsOfLearningActivity(groupId)
        studentDataDf     =  studentGrouped.getStudentsOfLearningActivityDF(groupId)
        
        if filterByDate:
            dateGroup = studentDataDf.groupby(  [ studentDataDf['CreatedAt'].dt.date ] )
            studentDataDf = dateGroup.get_group(filterByDate)

    #    if not studentDataDf is None and not studentDataDf.empty:
        plots = util.plotGroupOverview(groupId, groupStudents, studentDataDf, classes = "c-card-medium")
    except Exception as e: 
        subprocess.Popen(['echo', 'plotGroupOverview '])
        subprocess.Popen(['echo', str(e)])
        print('plotGroupOverview ')
        print(e)


    return plots

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


def createUserLAOptionsButtons():
    buttons_list = []

    user_LA_options = getUserLAOptions()
    for option in user_LA_options:
        button_label = option["label"]
        button_value = int(option["value"])
        buttons_list.append(html.Button(button_label, id = {"button-type": "select-classes-button", "class-id": button_value}))

    return buttons_list


def getButtonLabel(class_id):
    user_LA_options = getUserLAOptions()
    for option in user_LA_options:
        if(int(option["value"]) == class_id):
            return option["label"]
    return "Heading Error"
        

user_LA_option_buttons = createUserLAOptionsButtons()
clicked_button = {}


layout = html.Div(
    [
    html.H1('Select a Class', id = 'select-a-class-heading', style = {'text-align': 'center'}),

    html.Div(user_LA_option_buttons, className = 'choose-learning-activity-buttons', id = 'learning-activity-selection-div'),

    html.Div(html.Button('Select other Class', id = {"button-type": "select-other-classes-button"}), className = 'choose-learning-activity-buttons hidden', id = "button-select-other-la-div"),
      
    html.Div(id='Classes-Overview-Container'),

    dbc.Row([
            dbc.Col( 
                    html.A(children=[html.I(className="fas fa-download font-size_medium p_small"),
                       "download data : Group",], id = "classes_download_overview_link", className = "hidden" ,
                                               href="", target="_blank",
                                               download='group-overview.csv' )
       )]),

    dbc.Row([
            dbc.Col( 
                    html.Div(id='Classes-Task-Information-Container', className = "c-table ")
       )]),
                    
    dbc.Row([
            dbc.Col( 
                html.Div(children=[
                        html.Div( 'Task code submissions',
                                  id = 'Classes-taskId-selector-heading',
                                  className= "heading-sub practice  p-bottom_small hidden"
                        ),
                        dcc.Dropdown(
                            id = "Classes-taskId-selector",
                            placeholder = "Select Task to see details",
                            options = [ {'label': 'Select a group', 'value' : '0'}  ],
                            className = " "
                        )
                    ],
                    className = "p-top_large p-bottom_large"
                )
       )]),

    dbc.Row([
            dbc.Col( 
                html.Div(id='Classes-taskId-container', className = "c-container ")
        )]),

    dbc.Row([
            dbc.Col( 
                html.Div(id='Classes-Concept-Container', className = "c-table ")
        )]),
                     
    dbc.Row([
            dbc.Col( 
                html.Div(id='Classes-General-Container', className = "c-table ")
       )])
    ],
    style = {'margin': '30px'}
)


#----------------------------------------------------------------------------------------------------------------------
@app.callback([Output('learning-activity-selection-div', 'className'), Output('select-a-class-heading', 'children'),
               Output('button-select-other-la-div', 'className'), Output('Classes-Overview-Container', 'className'),
               Output('Classes-Task-Information-Container', 'className'), Output('Classes-General-Container', 'className'),
               Output('Classes-Concept-Container', 'className'), Output("Classes-taskId-selector", "className"),
               Output("Classes-taskId-container", "className"), Output("Classes-taskId-selector-heading", "className")],
              [Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"), Input({"button-type": "select-other-classes-button"}, "n_clicks")])
def showHideLearningActivitySelectionButtons(*args):

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']             # example string for triggered_id: {"button-type":"select-classes-button","class-id":1}.n_clicks

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            return ["choose-learning-activity-buttons hidden", getButtonLabel(class_id),
                    "choose-learning-activity-buttons", "",
                    "c-table ", "c-table ",
                    "c-table ", " ",
                    "c-container ", "heading-sub practice  p-bottom_small"]

    return ["choose-learning-activity-buttons", "Select a Class",
            "choose-learning-activity-buttons hidden", "hidden",
            "c-table hidden", "c-table hidden",
            "c-table hidden", "hidden",
            "c-container hidden", "heading-sub practice  p-bottom_small hidden"]

#----------------------------------------------------------------------------------------------------------------------
@app.callback(Output('Classes-Overview-Container', 'children'), 
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def setClassOverview(n_clicks):

    graphs = []
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            graphs = plotGroupOverview(class_id, '')
            graphs = [html.Hr(id = 'classes-overview-hr', className = "hr_custom_style")] + graphs + plotClassOverview(class_id, '')

    return html.Div(graphs)


#----------------------------------------------------------------------------------------------------------------------
@app.callback(Output('Classes-Task-Information-Container', 'children'), 
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def display_graphs(n_clicks):

    graphs = []
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            graphs = plotSingleClass('School', class_id, '')
            graphs = [html.Hr(id = 'classes-task-information-hr', className = "hr_custom_style")] + graphs + [html.Hr(id = 'classes-code-submission-hr', className = "hr_custom_style")]

    return html.Div(graphs)


#----------------------------------------------------------------------------------------------------------------------
@app.callback(Output('Classes-General-Container', 'children'), 
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def display_class_general(n_clicks):

    graphs = []
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            graphs = plotSingleClassGeneral('School', class_id, '')
            graphs = graphs + [html.Hr(className = "hr_custom_style")]

    return html.Div(graphs)


#----------------------------------------------------------------------------------------------------------------------
@app.callback(Output('Classes-Concept-Container', 'children'), 
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def display_class_concept(n_clicks):

    graphs = []
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            graphs = plotGroupConceptDetails(class_id, '')
            graphs = graphs + [html.Hr(id = 'classes-stats-hr', className = "hr_custom_style")]

    return html.Div(graphs)
    

#----------------------------------------------------------------------------------------------------------------------
#On Select a Group - set Group Task Done Options - see task wise information             
@app.callback([Output("Classes-taskId-selector", "options")],
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def onSelectGroupSetTaskOptions(n_clicks):

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            clicked_button['buttonID'] = class_id
            return [getGroupPTaskDoneOptions(class_id , '')]
    
    return [[{'label': 'Select a group', 'value' : '0'}]]
    

#----------------------------------------------------------------------------------------------------------------------
@app.callback([Output("Classes-taskId-container", "children")],
              [Input("Classes-taskId-selector", "value")])
def onSelectTaskShowTaskWiseConcept(taskId):

    graphs = []
    
    if util.isValidValueId(taskId) and util.isValidValueId(clicked_button["buttonID"]):
        graphs = getGroupTaskWiseDetails(clicked_button["buttonID"], isGrouped = False, taskId = int(taskId), filterByDate = '')
        
    graphs = graphs + [html.Hr(id = 'classes-concept-hr', className = "hr_custom_style")]
    
    return [html.Div(graphs)]


#----------------------------------------------------------------------------------------------------------------------
#--------------------- data download callback
@app.callback([Output('classes_download_overview_link', 'href'), Output('classes_download_overview_link', 'className')],
              [Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"), Input({"button-type": "select-other-classes-button"}, "n_clicks")])
def update_download_link__details_group(*args):

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "select-classes-button":
            class_id = triggered_id_dict["class-id"]
            csv_string = ""
            try:
                csv_string = util.get_download_link_data_uri( studentGrouped.getStudentsOfLearningActivityDF(class_id))
            except Exception as e: 
                subprocess.Popen(['echo', 'update_download_link__details_group '])
                subprocess.Popen(['echo', str(e)])
                print('update_download_link__details_group ')
                print(e)
    
            return csv_string, ""

    return "", "hidden"