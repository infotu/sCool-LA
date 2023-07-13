# -*- coding: utf-8 -*-

"""
Created on   Jun 11 19:04:59 2020
Reworked on  Mar 14 10:25:00 2023

@authors: tilan, zangl
"""


#----------------------------------------------------------------------------------------------------------------------
# imports
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

from flask_login import logout_user, current_user

from app import app
import constants
from data import studentGrouped

from apps import settings
import util


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


#----------------------------------------------------------------------------------------------------------------------
# Function to create graphs for a single selected class.
# params:   titleTextAdd      (string)        - string with title text
#           school            (string)        - ID of selected class
#           filterByDate      (string)        - string containing possible filter option
# returns:  list of graphs representing a whole class
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
            print('plotSingleClass 1 ')
            print(e)
        
        
#        -------------------------------------------
#            Task wise information
        
        
        graphs.append(html.Div(id='Task-Information-Classes',
                               children = [html.H2('Task Information')], 
                               className = "c-container p_medium p-top_large", 
                    ))

#---------------------------        Datatable task wise success fail    ---------------------------
        
            #            CHECKED     
    #            count of students completing a task
    
    
    #       if a student passed a task once, then he is Successfull OR Result = 1    
    
        graphs.append(html.Div( "Practice Tasks",
                                className= "heading-sub practice"
                    )) 

        try :
            pieData = groupOriginal.groupby(['PracticeTaskId', 'StudentId'], as_index=False).sum()
            
            pieData.loc[pieData['Result'] > 0, 'Result'] = 1
        
            taskData = pieData.groupby(['PracticeTaskId'], as_index=False).sum()
            taskData = taskData.rename(columns={"Result": countStudentCompletingTaskFeature})
            taskData = taskData.merge(right= dfPracticeTaskDetails
                                                , left_on='PracticeTaskId', right_on='PracticeTaskId'
                                                , left_index=False, right_index=False
                                                , how='inner')

            taskData[featurePracticeTaskDesc] = taskData['Title'].astype(str) + ' (Id: ' + taskData['PracticeTaskId'].astype(str) + ")"
        
            figStudents, graphQuantile = getFeaturePlot(taskData, 
                           countStudentCompletingTaskFeature, 
                           featurePracticeTaskDesc ,
                           'Number of Students completing a Practice Task', 
                           ['Title'], 
                           isColored = False, hasMeanStd = False, hoverName = featurePracticeTaskDesc )
            
            graphs.append(html.Div(html.Div(figStudents, className = "p-top_medium")))
            
            graphIndex = graphIndex + 1
        except Exception as e:
                print('plotSingleClass 1 ')
                print(e)
        

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
        
        dfTaskWiseSuccessFailForUserPresentation = dfTaskWiseSuccessFail
        dfTaskWiseSuccessFailForUserPresentation.drop(columns=["Type"], inplace = True)

        for index, row in dfTaskWiseSuccessFailForUserPresentation.iterrows():
            timestamp = turnSecondsIntoFancyTimestamp(row["SessionDuration"])
            dfTaskWiseSuccessFailForUserPresentation.at[index,"SessionDuration"] = timestamp
        
        table_header = [
            html.Thead(html.Tr([html.Th("Task Name and Description"), html.Th("Number of Students who succeeded"), html.Th("Number of Students who failed"), html.Th('Students total Time spent on Task'), html.Th('Skill Category'), html.Th('Course'), html.Th('Task ID')]))
        ]
        rows = []
        for index, row in dfTaskWiseSuccessFailForUserPresentation.iterrows():

            tds = []
            for feature in dfTaskWiseSuccessFailForUserPresentation.columns:
                if not feature == constants.featureDescription :
                    tds.append(html.Td(str(row[feature])))

            rows.append(html.Tr(tds ,className = "type-practice"))
            rows.append(html.Tr([html.Td(row[constants.featureDescription], colSpan = len(dfTaskWiseSuccessFailForUserPresentation.columns) - 1)]))
            
        table_body = [html.Tbody(rows)]
        
        table = dbc.Table(table_header + table_body, bordered=True)
        
        graphs.append(html.Div(table,
                         className = "c-table c-table-oddeven font-size_small"
                    ))
        


    #            CHECKED
    #            count of tasks completed by each student    
        try: 

            graphs.append(html.Div( 'Student-related Practice Task Information',
                                   className= "heading-sub practice  p-top_large"
                        )) 
            
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
                html.Thead(html.Tr([html.Th("Student"), html.Th("Number of Tasks completed"), html.Th("Names of completed Practice Tasks", className="c-table-w-content-main")
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
#                                      className = (   "type-practice"  if row[featureTaskType] == constants.TaskTypePractice else "type-theory"  )
                                      ) )
            
            table_body = [html.Tbody(  rows   )]
            
            table = dbc.Table(table_header + table_body, bordered=True)
            

            graphs.append(html.Div(table ,className = "c-table c-table-oddeven font-size_small p-top_medium"))

        except Exception as e:     
            print( 'ERROR - practice')
            print(e)

        

                
        try :

            graphs.append(html.Div( 'Theory Tasks',
                                   className= "heading-sub theory p-top_large"
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

            taskDataTheory[featureTheoryTaskDesc] = taskDataTheory['Title'].astype(str) + ' (Id: ' + taskDataTheory['TheoryTaskId'].astype(str) + ")" 

            taskDataTheory[featureTaskType] = constants.TaskTypeTheory
            
        
            figStudents, graphQuantile = getFeaturePlot(taskDataTheory, 
                           countStudentCompletingTaskFeature, 
                           featureTheoryTaskDesc, 
                           'Number of Students completing a Theory Task', 
                           ['Title'], 
                           isColored = True, hasMeanStd = False, hoverName = featureTheoryTaskDesc )
                     
           
            graphs.append(html.Div(figStudents, className = "p-top_medium"))
                          
            graphIndex = graphIndex + 1


            dfTaskWiseSuccessFailTheory = pd.DataFrame(index=np.arange(0, 1), columns=['Task (Name and short Description)', constants.featureDescription, labelSuccess, labelFail, 'SessionDuration', 'Type',
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
                print('in the theory exception ')
                print(e)
            
            # convert column of DataFrame to Numeric Int
            dfTaskWiseSuccessFailTheory[labelSuccess] = pd.to_numeric(dfTaskWiseSuccessFailTheory[labelSuccess], downcast='integer')
            dfTaskWiseSuccessFailTheory[labelFail] = pd.to_numeric(dfTaskWiseSuccessFailTheory[labelFail], downcast='integer')
            
            dfTaskWiseSuccessFailForUserPresentationTheory = dfTaskWiseSuccessFailTheory
            dfTaskWiseSuccessFailForUserPresentationTheory.drop(columns=["Type"], inplace = True)

            for index, row in dfTaskWiseSuccessFailForUserPresentationTheory.iterrows():
                timestamp = turnSecondsIntoFancyTimestamp(row["SessionDuration"])
                dfTaskWiseSuccessFailForUserPresentationTheory.at[index,"SessionDuration"] = timestamp
            
            table_header = [
                html.Thead(html.Tr([html.Th("Task Name and Description"), html.Th("Number of Students who succeeded"), html.Th("Number of Students who failed"), html.Th('Students total Time spent on Task'), html.Th('Skill Category'), html.Th('Course'), html.Th('Task ID') ]))
            ]
            rows = []
            for index, row in dfTaskWiseSuccessFailForUserPresentationTheory.iterrows():

                tds = []
                for feature in dfTaskWiseSuccessFailForUserPresentationTheory.columns:
                    if not feature == constants.featureDescription:
                        tds.append(html.Td(str(row[feature])))

                rows.append(html.Tr(tds, className = ("type-theory")))
                rows.append(html.Tr([html.Td(row[constants.featureDescription], colSpan = len(dfTaskWiseSuccessFailForUserPresentationTheory.columns) - 1)]))
                
            
            table_body = [html.Tbody(rows)]
            
            table = dbc.Table(table_header + table_body, bordered=True)
            
            graphs.append(html.Div(table ,
                            className = "c-table c-table-oddeven font-size_small"
                        ))
            
        
        except Exception as e: 
                print('plotSingleClass 2 ')
                print(e)
        

        try: 

            graphs.append(html.Div('Student-related Theory Task Information',
                                   className= "heading-sub theory p-top_large"
            )) 

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
                html.Thead(html.Tr([html.Th("Student"), html.Th("Number of Tasks completed"), html.Th("Names of completed Theory Tasks", className="c-table-w-content-main")
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
            

            graphs.append(html.Div(table ,className = "c-table c-table-oddeven font-size_small p-top_medium"))        
            
        except Exception as e: 
            print( 'ERROR - theory')  
            print(e)
        
        

    except Exception as e: 
        print( 'ERROR - plotSingleClass ')
        print(e)

    return graphs        




    
    

    
#-------------------------------------------------
#GENERAL INFORMATION SECTION
#------------------------------------------------------

#        CHECKED
#            for concepts used
featureX = 'Students Count'
featureY = 'Details'
featurePracticeTaskGroup = 'Task-Id'            


#----------------------------------------------------------------------------------------------------------------------
# Function to create task related graphs for a single selected class.
# params:   groupId           (string)        - ID of selected class
#           isGrouped         (bool)          - bool indicating wether data is grouped
#           taskId            (int)           - integer holding the ID of the wanted task
#           filterByDate      (string)        - string containing possible filter option
# returns:  list of graphs representing task wise details of a class
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
        
        featureToPlotTask = ['Name', 'Code', 'SessionDuration', 'UsedConcepts']
        
        if not taskId is None and  taskId > 0 and taskId in taskWiseConceptPracticeGrouped.groups.keys():
            taskData = taskWiseConceptPracticeGrouped.get_group(taskId)

            table_header = [
                html.Thead(html.Tr([html.Th('Student'), html.Th('Submitted Code'), html.Th('Time spent writing Code'), html.Th("Used Code Concepts")]))
            ]

            for index, row in taskData.iterrows():
                timestamp = turnSecondsIntoFancyTimestamp(row["SessionDuration"])
                taskData.at[index, "SessionDuration"] = timestamp
            
            rows = []
            for index, row in taskData.iterrows():
    
                tds = []
                for feature in featureToPlotTask:
                    if feature == "Code":
                        codeWithBreaks = str(row[feature]).split('\n')
                        codeLined = []
                        for codeLine in codeWithBreaks:
                            codeLined.append(html.Pre(html.Span(codeLine),
                                                      className = "c-pre" 
                                            ))
                        tds.append(html.Td(codeLined))
                    elif feature == "UsedConcepts":
                        usedConcepts = []
                        for conceptKey in constants.codeConceptNameDict.keys():
                            if int(row[conceptKey]) > 0:
                                usedConcepts.append(conceptKey)
                        tds.append(html.Td(html.Div(children = [ 
                                html.Details(
                                            children = [
                                                html.Summary(constants.codeConceptNameDict[concept]),
                                                html.P(constants.codeConceptDescriptionDict[concept])
                                            ],
                                            className = " c-details practice"
                                        ) for concept in usedConcepts]), 
                                        className="c-table-w-content-main")
                        )
                    else:
                        tds.append(html.Td(str(row[feature])))
    
                rows.append(html.Tr(tds))

            table_body = [html.Tbody(rows)]            
            table = dbc.Table(table_header + table_body, bordered=True)
            
            graphs.append(html.Div(table ,
                             className = "c-table c-table-oddeven font-size_small m-top_small"
                        ))
            
            
            
              
            
    except Exception as e: 
                print('plotGroupTaskWiseConcepts 1 ')
                print(e)
            
    try:    
    #    Step 2 :- add the plot - concepts used by count of students
        graphs = graphs + plotGroupTaskWiseConcepts( groupId, isGrouped = isGrouped, taskId = taskId , filterByDate = filterByDate)    
    except Exception as e: 
        print('plotGroupTaskWiseConcepts 2 ')
        print(e)
    
    return graphs
    
    
#----------------------------------------------------------------------------------------------------------------------
# Function to create task related concept graphs for a single selected class.
# params:   groupId           (string)        - ID of selected class
#           isGrouped         (bool)          - bool indicating wether data is grouped
#           taskId            (int)           - integer holding the ID of the wanted task
#           filterByDate      (string)        - string containing possible filter option
# returns:  list of graphs representing task wise concepts of a class
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
                print('plotGroupTaskWiseConcepts 1 ')
                print(e)
                
            figBar = px.bar(studentWiseDataConceptsTask
                                , x             =  featureX
                                , y             =  featureY
                                , orientation   =  'h'
                                , height        =   constants.graphHeight - 100
                                , template      =   constants.graphTemplete   
                                , title         =   "Code Concepts used by Students in Task with Task ID " + str(taskId) + "<br>" + str(taskTitle)  +   " (Number of Students used a Concept in Code)"
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
                print('plotGroupTaskWiseConcepts 1 last ')
                print(e)
        
        if isGrouped:
            figGroupedTaskConcepts = px.bar(studentWiseTaskWiseConceptPractice
                                , x             =   featureY
                                , y             =   featureX
                                , height        =   constants.graphHeight - 100
                                , hover_data    =  [ 'Title', 'PracticeTaskId',  ]
                                , template      =   constants.graphTemplete   
                                , title         =   "Code Concepts used by Students in each Task <br> (Number of Students used a Concept in Code for a Task)"
                                , labels        =   feature2UserNamesDict # customize axis label
                                , color         =   featurePracticeTaskGroup
                                , barmode       =   'group'
                )
            return figGroupedTaskConcepts
                
        return graphs
    except Exception as e: 
        print('plotGroupTaskWiseConcepts  last ')
        print(e)               


#----------------------------------------------------------------------------------------------------------------------
# Function to get the done tasks options of a selected class.
# params:   groupId           (string)        - ID of selected class
#           filterByDate      (string)        - string containing possible filter option
# returns:  list of done task options
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
        print('getGroupPTaskDoneOptions')
        print(e)    
    
    return options



        
#----------------------------------------------------------------------------------------------------------------------
# Function to create concept details graphs.
# params:   groupId           (string)        - ID of selected class
#           filterByDate      (string)        - string containing possible filter option
# returns:  list of html.Div() holding various data visualizations
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
                            , title         =   "Code Concepts used by Students of this Class (Number of Students using a Concept in Code)"
                            , labels        =   feature2UserNamesDict # customize axis label
            )
        
        graphs.append(
                dcc.Graph(
                    figure= figBar
                )
        )
        
#       Task wise concepts used - grouped together
        try :
            figBar = plotGroupTaskWiseConcepts(groupId, isGrouped = True, taskId = 0, filterByDate = filterByDate )
            
            graphs.append(html.Div(
                dcc.Graph(figure= figBar), className = "c-container p-top_large p-bottom_large")
            )   

        except Exception as e: 
                print('Task Concepts used')
                print(e)                
      
    except Exception as e: 
            print('Task Concepts used')
            print(e)

    return graphs



#----------------------------------------------------------------------------------------------------------------------
# Function to create plot of a given feature.
# params:   df                  (DataFrame) - dataframe containing the data
#           featureX            (string)    - x axis information
#           featureY            (string)    - y axis information
#           title               (string)    - title string
#           hoverData           (string)    - string containing hover information for the user hovering over plot
#           isColored           (bool)      - bool stating wether plot is colored or not
#           hasMeanStd          (bool)      - bool stating wether plot has mean and standard derivation
#           hoverName           (string)    - string holding hover name info
#           hasDistribution     (bool)      - bool stating wether plot has distribution
#           isThemeSizePlot     (bool)      - bool stating wether the plot represents a theme size
# returns:  list of graphs of the given feature and their distributions
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
        print('getFeaturePlot  hasDistribution ')
        print('title  ' + title)
        print(e)
        
        
    return graphs, graphDistributions


#----------------------------------------------------------------------------------------------------------------------
# Function to create plot of a given feature.
# params:   df                  (DataFrame) - dataframe containing the data
#           featureX            (string)    - x axis information
#           featureY            (string)    - y axis information
#           title               (string)    - title string
#           hoverData           (string)    - string containing hover information for the user hovering over plot
#           isColored           (bool)      - bool stating wether plot is colored or not
#           hasMeanStd          (bool)      - bool stating wether plot has mean and standard derivation
#           hoverName           (string)    - string holding hover name info
#           hasDistribution     (bool)      - bool stating wether plot has distribution
#           isThemeSizePlot     (bool)      - bool stating wether the plot represents a theme size
# returns:  list of graphs of the given feature and their distributions
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
                                                                   'Students Practice ' + titleFirst,
                                                                   hoverDataPractice,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                            
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )

                            quantileIndex += 1
                            
                            
                            dfTheory2Plot = studentWiseDataTheory.groupby(['StudentId', 'Name', 'TaskType'], as_index=False).sum()
                            featurePlot, graphDistributions = getFeaturePlot(dfTheory2Plot, featuresPractice[first], featuresPractice[second], 
                                                                   'Students Theory ' + titleFirst,
                                                                   hoverDataTheory, 
                                                                   isColored = True,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )

                            quantileIndex += 1
                         
#    Graphs only for PRACTICE
                        if ([featuresPractice[first], featuresPractice[second]] not in  featurePairsToPlotTheory):    
                            featurePlot, graphDistributions = getFeaturePlot(studentWiseData, featuresPractice[first], featuresPractice[second], 
                                                                   'Students Practise ' + titleFirst,
                                                                   hoverDataPractice,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )

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
                                                                   'Students ' + titleFirst,
                                                                   hoverDataTheory, isColored = True,
                                                                   hasDistribution = True,
                                                                   isThemeSizePlot = False )
                    
                    graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                    )

                    quantileIndex += 1
                    
                except Exception as e: 
                    print(' plotSingleClassGeneral  rowTheory Theory plots ')
                    print(e)


    except Exception as e: 
        print(e)

    graphsMain.append(html.Div(html.Div(graphs, className = " p-top_medium "), className = "c-container "))
    
    return graphsMain      



#----------------------------------------------------------------------------------------------------------------------
# Function that turns a number (of seconds) into a fancy timestamp looking like xxh xxm xxs
# params:   totalSeconds      (int) - integer holding amount of seconds
# returns:  string - fancy timestamp
def turnSecondsIntoFancyTimestamp(totalSeconds):
    hours = totalSeconds // 3600
    minutes = (totalSeconds % 3600) // 60
    seconds = (totalSeconds % 3600) % 60
    
    timeString = f"{hours}h {minutes}m {seconds}s"
    return timeString


#----------------------------------------------------------------------------------------------------------------------
# Function that turns a fancy timestamp looking like xxh xxm xxs into a number (of seconds)
# params:   timeString      (string) - fancy timestamp
# returns:  integer holding amount of seconds
def turnFancyTimestampIntoSeconds(timeString):
    splitUpString = timeString.split()
    hours = int(splitUpString[0].rstrip('h'))
    minutes = int(splitUpString[1].rstrip('m'))
    seconds = int(splitUpString[2].rstrip('s'))

    totalSeconds = (hours * 3600) + (minutes * 60) + seconds
    return totalSeconds



#----------------------------------------------------------------------------------------------------------------------
# Function that plots the list of students of a selected class.
# params:   schoolKey         (string)        - ID of selected class
#           filterByDate      (string)        - string containing possible filter option
# returns:  Dash DataTable containing students in class
def plotStudentsList(schoolKey, filterByDate = '' ):
    
    graphs = []

    features2Plot = ['Name', 'SessionDuration', 'PracticeSessionDuration', 'TheorySessionDuration', 
                     'Attempts', 'Points']

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
        
        for index, row in studentDataDfSum.iterrows():
            timestamp = turnSecondsIntoFancyTimestamp(row["PracticeSessionDuration"])
            studentDataDfSum.at[index,"PracticeSessionDuration"] = timestamp
            timestamp = turnSecondsIntoFancyTimestamp(row["TheorySessionDuration"])
            studentDataDfSum.at[index,"TheorySessionDuration"] = timestamp
            timestamp = turnSecondsIntoFancyTimestamp(row["SessionDuration"])
            studentDataDfSum.at[index,"SessionDuration"] = timestamp

        fig1Table = dash_table.DataTable(
            id = "students-list-table",
            columns=[
                {"name": constants.feature2UserNamesDict.get(i) if i in constants.feature2UserNamesDict.keys() else i , "id": i, "selectable": True} for i in studentDataDfSum[features2Plot].columns
            ],
            data         = studentDataDfSum[features2Plot].to_dict('records'),
            sort_action  = "custom",
            sort_mode    = "single",
            sort_by      = [],
            style_header = {
                'border': '1px solid black',
                'textAlign': 'center',
                'backgroundColor': 'rgb(210, 210, 210)',
                'color': 'black',
                'fontWeight': 'bold'
            },
            style_data = {
                'border': '1px solid black',
                'textAlign': 'left',
                'backgroundColor': 'white',
                'color': 'black'
            },
            style_data_conditional = [
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(230, 230, 230)',
                }
            ],
        )
        
#    ---------------------------------------------
            
        graphs.append(html.Div(children = [html.H2("Students in this Class", className = "p-left_medium"), fig1Table], className = "p-top_medium"))

    except Exception as e: 
        print('plotStudentsList 2 ')
        print(e)

    return graphs



#----------------------------------------------------------------------------------------------------------------------
# Function that plots the class overview.
# params:   groupId           (string)        - ID of selected class
#           filterByDate      (string)        - string containing possible filter option
# returns:  list of html.Div() containing plots.
def plotClassOverview(groupId, filterByDate = '' ):
    plots               = []
    try:    
        groupStudents     =  getStudentsOfLearningActivity(groupId)
        studentDataDf     =  studentGrouped.getStudentsOfLearningActivityDF(groupId)
        
        if filterByDate:
            dateGroup = studentDataDf.groupby(  [ studentDataDf['CreatedAt'].dt.date ] )
            studentDataDf = dateGroup.get_group(filterByDate)

    #    if not studentDataDf is None and not studentDataDf.empty:
        plots = util.plotClassOverview(groupId, groupStudents, studentDataDf, classes = "c-card-medium")
    except Exception as e: 
        print('plotClassOverview ')
        print(e)

    return plots


#----------------------------------------------------------------------------------------------------------------------
# Function to retrieve the classes the current user has access to.
# params:   none
# returns:  The unique values of classes ids.
def getUserLA():
    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated:
        currentUserId = current_user.id
        
        if  current_user.isAdmin : 
            return studentGrouped.dfLearningActivityDetails[constants.GROUPBY_FEATURE].unique().astype(str)
        else:
            return studentGrouped.dfLearningActivityDetails[studentGrouped.dfLearningActivityDetails['User_Id'] == 
                                                            currentUserId][constants.GROUPBY_FEATURE].unique().astype(str)


    return studentGrouped.dfLearningActivityDetails[constants.GROUPBY_FEATURE].unique()


#----------------------------------------------------------------------------------------------------------------------
# Function to call the BuildOptionsLA() function with the right classes.
# params:   none
# returns:  List of dictionaries containing the classes the user has access to.
def getUserLAOptions():
    userLA = getUserLA()
    
    if current_user and current_user is not None   and   not isinstance(current_user, type(None))  and    current_user.is_authenticated:
        return studentGrouped.BuildOptionsLA( [ groupId for groupId in  userLA  ] , isAdmin =  current_user.isAdmin ) 
    
    return studentGrouped.BuildOptionsLA( [ groupId for groupId in  userLA  ] , isAdmin = True  )


#----------------------------------------------------------------------------------------------------------------------
# Function to generate the learning activity buttons (class buttons)
# params:   none
# returns:  list containing the class buttons the user has access to
def createUserLAOptionsButtons():
    buttons_list = []

    user_LA_options = getUserLAOptions()
    for option in user_LA_options:
        button_label = option["label"]
        button_value = int(option["value"])
        buttons_list.append(html.Button(button_label, id = {"button-type": "select-classes-button", "class-id": button_value}))

    return buttons_list


#----------------------------------------------------------------------------------------------------------------------
# Function to get a button Label.
# params:   class_id   (int) - integer holding class id
# returns:  Button label for selected class.
def getButtonLabel(class_id):
    user_LA_options = getUserLAOptions()
    for option in user_LA_options:
        if(int(option["value"]) == class_id):
            return option["label"]
    return "Heading Error"
        

clicked_button = {}


#----------------------------------------------------------------------------------------------------------------------
# classes tab layout - used in main layout (located in index.py)
layout = html.Div(
    [
    html.Div(html.H1('Select a Class', id = 'select-a-class-heading', className = "align-center"),
                         id = "select-a-class-heading-div", className="stick-on-top-of-page"),

    html.Div(createUserLAOptionsButtons(), id = 'learning-activity-selection-div',
             className = 'm-top_small m-left-right-small choose-learning-activity-buttons'),

    html.Div(html.Button('Select other Class', id = {"button-type": "select-other-classes-button"}),
             id = "button-select-other-la-div", className = 'm-top_small m-left-right-small choose-learning-activity-buttons hidden'),
      
    html.Hr(id = 'classes-overview-hr', className = "hr_custom_style hidden"),

    html.Div(id='classes-overview-container', className = "c-table m-left-right-medium"),

    html.A(children=[html.I(className="fas fa-download font-size_medium p_small"),
                       "download class data",], id = "classes_download_overview_link", className = "m-left-right-medium hidden" ,
                                               href="", target="_blank",
                                               download='group-overview.csv' ),

    html.Hr(id = 'classes-task-information-hr', className = "hr_custom_style hidden"),

    html.Div(id='classes-task-information-container', className = "c-table m-left-right-medium"),
    
    html.Hr(id = 'classes-code-submission-hr', className = "hr_custom_style hidden"),

    html.Div(children=[
            html.Div('Task code submissions',
                     id = 'classes-taskId-selector-heading',
                     className= "heading-sub practice  p-bottom_small m-top_small"
            ),
            html.Div(constants.codeSubmissionParagraph,
                     className = "normal-paragraph m-bottom_small"),
            dcc.Dropdown(id = "classes-taskId-selector",
                         placeholder = "Select Task to see details",
                         options = [ {'label': 'Select a group', 'value' : '0'}  ],
                         className = "m-top_small"
            )
        ],
        id = "classes-taskid-selector-div",
        className = "p-top_large p-bottom_large m-left-right-medium hidden"
    ),

    html.Div(id='classes-taskId-container', className = "c-container m-left-right-medium"),

    html.Hr(id = 'classes-concept-hr', className = "hr_custom_style hidden"),

    html.Div(id='classes-concept-container', className = "c-table m-left-right-medium"),

    html.Hr(id = 'classes-stats-hr', className = "hr_custom_style hidden"),
                     
    html.Div(id='classes-general-container', className = "c-table m-left-right-medium")
    ]
)


#----------------------------------------------------------------------------------------------------------------------
# Callback function to manipulate the generated class buttons.
# params:   pathname         (string) - string containing the pathname (used only as trigger)
# returns:  newly generated class buttons.
@app.callback(Output("learning-activity-selection-div", "children"), 
              [Input("url", "pathname")],
)
def create_class_selection_buttons(pathname):
    
    return createUserLAOptionsButtons()


#----------------------------------------------------------------------------------------------------------------------
# Callback function to manipulate the content of the classes tab. (if it should be visible or not)
# params:   *args     (tuple) - tuple containing info on how often select-classes-button or select-other-classes-button was pressed (used only as trigger)
# returns:  list of newly set styling strings for className property
@app.callback([Output('learning-activity-selection-div', 'className'), Output('select-a-class-heading', 'children'),
               Output('button-select-other-la-div', 'className'), Output('classes-overview-container', 'className'),
               Output('classes-task-information-container', 'className'), Output('classes-general-container', 'className'),
               Output('classes-concept-container', 'className'), Output("classes-taskid-selector-div", "className"),
               Output("classes-taskId-container", "className"),
               
               Output('classes-overview-hr', 'className'), Output('classes-task-information-hr', 'className'),
               Output('classes-code-submission-hr', 'className'), Output('classes-concept-hr', 'className'),
               Output('classes-stats-hr', 'className')],
              [Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"), Input({"button-type": "select-other-classes-button"}, "n_clicks")])
def show_hide_classes_tab_content(*args):

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']             # example string for triggered_id: {"button-type":"select-classes-button","class-id":1}.n_clicks

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        someButtonWasPressed = False
        for clickinfo in args[0]:
            if clickinfo is not None:
                someButtonWasPressed = True
        if args[1] is not None:
            someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            return ["m-top_small m-left-right-small choose-learning-activity-buttons hidden", getButtonLabel(class_id),
                    "m-top_small m-left-right-small choose-learning-activity-buttons", "c-table m-left-right-medium",
                    "c-table m-left-right-medium", "c-table m-left-right-medium",
                    "c-table m-left-right-medium", "p-top_large p-bottom_large m-left-right-medium",
                    "c-container m-left-right-medium",
                    "hr_custom_style", "hr_custom_style",
                    "hr_custom_style", "hr_custom_style",
                    "hr_custom_style"]

    return ["m-top_small m-left-right-small choose-learning-activity-buttons", "Select a Class",
            "m-top_small m-left-right-small choose-learning-activity-buttons hidden", "c-table m-left-right-medium hidden",
            "c-table m-left-right-medium hidden", "c-table m-left-right-medium hidden",
            "c-table m-left-right-medium hidden", "p-top_large p-bottom_large m-left-right-medium hidden",
            "c-container m-left-right-medium hidden",
            "hr_custom_style hidden", "hr_custom_style hidden",
            "hr_custom_style hidden", "hr_custom_style hidden",
            "hr_custom_style hidden"]


#----------------------------------------------------------------------------------------------------------------------
# Callback function to change the children of the classes-overview-container based on user actions.
# params:   n_clicks     (int) - integer holding information on how often button was clicked (used as trigger)
# returns:  list of newly created children
@app.callback(Output('classes-overview-container', 'children'), 
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def set_class_overview(n_clicks):

    graphs = []
    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        someButtonWasPressed = False
        for clickinfo in n_clicks:
            if clickinfo is not None:
                someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            graphs = plotClassOverview(class_id, '')
            graphs = graphs + plotStudentsList(class_id, '')

    return html.Div(graphs)


#----------------------------------------------------------------------------------------------------------------------
# Callback function to change the children of the classes-task-information-container based on user actions.
# params:   n_clicks     (int) - integer holding information on how often button was clicked (used as trigger)
# returns:  list of newly created children
@app.callback(Output('classes-task-information-container', 'children'), 
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

        someButtonWasPressed = False
        for clickinfo in n_clicks:
            if clickinfo is not None:
                someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            graphs = plotSingleClass('School', class_id, '')

    return html.Div(graphs)


#----------------------------------------------------------------------------------------------------------------------
# Callback function to change the children of the classes-general-container based on user actions.
# params:   n_clicks     (int) - integer holding information on how often button was clicked (used as trigger)
# returns:  list of newly created children
@app.callback(Output('classes-general-container', 'children'), 
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

        someButtonWasPressed = False
        for clickinfo in n_clicks:
            if clickinfo is not None:
                someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            graphs = plotSingleClassGeneral('School', class_id, '')

    return html.Div(graphs)


#----------------------------------------------------------------------------------------------------------------------
# Callback function to change the children of the classes-concept-container based on user actions.
# params:   n_clicks     (int) - integer holding information on how often button was clicked (used as trigger)
# returns:  list of newly created children
@app.callback(Output('classes-concept-container', 'children'), 
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

        someButtonWasPressed = False
        for clickinfo in n_clicks:
            if clickinfo is not None:
                someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            graphs = plotGroupConceptDetails(class_id, '')

    return html.Div(graphs)
    

#----------------------------------------------------------------------------------------------------------------------
# Callback function to set Group Task Done Options - see task wise information.
# params:   n_clicks     (int) - integer holding information on how often button was clicked (used as trigger)
# returns:  list of newly created options          
@app.callback([Output("classes-taskId-selector", "options")],
              Input({"button-type": "select-classes-button", "class-id": ALL}, "n_clicks"))
def on_select_group_set_task_options(n_clicks):

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']

        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        someButtonWasPressed = False
        for clickinfo in n_clicks:
            if clickinfo is not None:
                someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            clicked_button['buttonID'] = class_id
            return [getGroupPTaskDoneOptions(class_id , '')]
    
    return [[{'label': 'Select a group', 'value' : '0'}]]
    

#----------------------------------------------------------------------------------------------------------------------
# Callback function to change the children of the classes-taskId-container based on user actions.
# params:   taskId     (int) - integer holding task id
# returns:  list of newly created children
@app.callback([Output("classes-taskId-container", "children")],
              [Input("classes-taskId-selector", "value")])
def on_select_task_show_task_wise_concept(taskId):

    graphs = []
    
    if util.isValidValueId(taskId) and util.isValidValueId(clicked_button["buttonID"]):
        graphs = getGroupTaskWiseDetails(clicked_button["buttonID"], isGrouped = False, taskId = int(taskId), filterByDate = '')
    
    return [html.Div(graphs)]


#----------------------------------------------------------------------------------------------------------------------
# Callback function to change the classes download link and visibility of this download link.
# params:   *args     (tuple) - tuple containing info on how often select-classes-button or select-other-classes-button was pressed (used only as trigger)
# returns:  new classes download link and string representing visibility of this download link
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

        someButtonWasPressed = False
        for clickinfo in args[0]:
            if clickinfo is not None:
                someButtonWasPressed = True
        if args[1] is not None:
            someButtonWasPressed = True

        if triggered_id_dict["button-type"] == "select-classes-button" and someButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            csv_string = ""
            try:
                csv_string = util.get_download_link_data_uri( studentGrouped.getStudentsOfLearningActivityDF(class_id))
            except Exception as e: 
                print('update_download_link__details_group ')
                print(e)
    
            return csv_string, "m-left-right-medium"

    return "", "m-left-right-medium hidden"


#----------------------------------------------------------------------------------------------------------------------
# Callback function that sorts the data displayed in the table based on the sorting parameters received.
# params:   sortBy     (string)    - sorting information
#           data       (DataFrame) - students-list-table data
# returns:  sorted data as dictionary
@app.callback(Output('students-list-table', 'data'),
              Input('students-list-table', 'sort_by'),
              State('students-list-table', 'data')
)
def custom_sort_students_table(sortBy, data):
    
    if sortBy:
        df = pd.DataFrame(data)
        if sortBy[0]['column_id'] == "Name":
            df_sorted = df.sort_values(by = 'Name', ascending = (sortBy[0]['direction'] == 'asc'))
            return df_sorted.to_dict('records')
    
        elif sortBy[0]['column_id'] == "SessionDuration":
            for index, row in df.iterrows():
                seconds = turnFancyTimestampIntoSeconds(row["SessionDuration"])
                df.at[index,"SessionDuration"] = seconds
            df_sorted = df.sort_values(by = 'SessionDuration', ascending = (sortBy[0]['direction'] == 'asc'))
            for index, row in df_sorted.iterrows():
                timestamp = turnSecondsIntoFancyTimestamp(row["SessionDuration"])
                df_sorted.at[index,"SessionDuration"] = timestamp
            return df_sorted.to_dict('records')
    
        elif sortBy[0]['column_id'] == "PracticeSessionDuration":
            for index, row in df.iterrows():
                seconds = turnFancyTimestampIntoSeconds(row["PracticeSessionDuration"])
                df.at[index,"PracticeSessionDuration"] = seconds
            df_sorted = df.sort_values(by = 'PracticeSessionDuration', ascending = (sortBy[0]['direction'] == 'asc'))
            for index, row in df_sorted.iterrows():
                timestamp = turnSecondsIntoFancyTimestamp(row["PracticeSessionDuration"])
                df_sorted.at[index,"PracticeSessionDuration"] = timestamp
            return df_sorted.to_dict('records')
    
        elif sortBy[0]['column_id'] == "TheorySessionDuration":
            for index, row in df.iterrows():
                seconds = turnFancyTimestampIntoSeconds(row["TheorySessionDuration"])
                df.at[index,"TheorySessionDuration"] = seconds
            df_sorted = df.sort_values(by = 'TheorySessionDuration', ascending = (sortBy[0]['direction'] == 'asc'))
            for index, row in df_sorted.iterrows():
                timestamp = turnSecondsIntoFancyTimestamp(row["TheorySessionDuration"])
                df_sorted.at[index,"TheorySessionDuration"] = timestamp
            return df_sorted.to_dict('records')
    
        elif sortBy[0]['column_id'] == "Attempts":
            df_sorted = df.sort_values(by = 'Attempts', ascending = (sortBy[0]['direction'] == 'asc'))
            return df_sorted.to_dict('records')
    
        elif sortBy[0]['column_id'] == "Points":
            df_sorted = df.sort_values(by = 'Points', ascending = (sortBy[0]['direction'] == 'asc'))
            return df_sorted.to_dict('records')
    
    return data