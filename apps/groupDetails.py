# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 19:04:59 2020

@author: tilan
"""

# -*- coding: utf-8 -*-
import math
import json
from datetime import date
import dateutil.parser
import numpy as np
import pandas as pd
from dateutil.parser import parse

import flask
import dash
import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.figure_factory as ff
import chart_studio.plotly as py
from plotly import graph_objs as go
import os

from app import app



from data import studentGrouped
import constants
import util





#fig = studentGroupedPerformance.figBar


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


hasFeatures =  studentGrouped.hasFeatures

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


dfPracticeTaskDetails                   = studentGrouped.dfPracticeTaskDetails
dfTheoryTaskDetails                     = studentGrouped.dfTheoryTaskDetails


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
getStudentsOfSchool                     =  studentGrouped.getStudentsOfSchool


getPracticeDescription                  =  studentGrouped.getPracticeDescription
getTheoryDescription                     =  studentGrouped.getTheoryDescription



def convert_list_column_tostr_NL(val) :
    separator = ',<br>'
    return separator.join(val)




#--------------------------- helper functions  END -----------------------


#------------------------------------

def plotSingleClass( titleTextAdd, school ):
     
    graphIndex = 1
    graphs = []
    
        
    try :
        groupOriginal = dfGroupedOriginal.get_group(school)
        
        try :
            groupOriginalTheory = dfGroupedPlayerStrategyTheory.get_group(school)
        except Exception as e: 
            print('plotSingleClass 1 ')
            print(e)
        
        
        
        
#        -------------------------------------------
#            Task wise information
        
        
        graphs.append(html.Div(id='Task-Information',
                               children = [html.H2('Task Information')], 
                               className = "c-container p_medium p-top_xx-large", 
                    ))        

#---------------------------        Datatable task wise success fail    ---------------------------
        dfTaskWiseSuccessFail = pd.DataFrame(index=np.arange(0, 1), columns=['Task', 'Success', 'Others', 'Type', 'TaskId'])
        
        
        pieDataTaskWisePractice = groupOriginal.groupby(['PracticeTaskId', 'StudentId'], as_index=False).sum()
        pieDataTaskWisePractice.loc[pieDataTaskWisePractice['Result'] > 0, 'Result'] = 1   
        pieDataTaskWisePracticeGrouped = pieDataTaskWisePractice.groupby(['PracticeTaskId'])
        
        
        index_dfTaskWiseSuccessFail = 0
        for groupKeyTaskId, groupTask in pieDataTaskWisePracticeGrouped:
            dfTaskWiseSuccessFail.loc[index_dfTaskWiseSuccessFail] =  getTaskWiseSuccessFail(groupTask, groupKeyTaskId,  dfPracticeTaskDetails, 'PracticeTaskId', 'Practice')
            index_dfTaskWiseSuccessFail += 1
                
        try :        
            pieDataTaskWiseTheory = groupOriginalTheory.groupby(['TheoryTaskId', 'StudentId'], as_index=False).sum()
            pieDataTaskWiseTheory.loc[pieDataTaskWiseTheory['Result'] > 0, 'Result'] = 1   
            pieDataTaskWiseTheoryGrouped = pieDataTaskWiseTheory.groupby(['TheoryTaskId'])
        
            for groupKeyTaskId, groupTask in pieDataTaskWiseTheoryGrouped:
                dfTaskWiseSuccessFail.loc[index_dfTaskWiseSuccessFail] =  getTaskWiseSuccessFail(groupTask, groupKeyTaskId,  dfTheoryTaskDetails, 'TheoryTaskId', 'Theory')
                index_dfTaskWiseSuccessFail += 1

        except Exception as e: 
                print('in the theory exception ')   
                print(e)   
        
        # convert column of DataFrame to Numeric Int
        dfTaskWiseSuccessFail["Success"] = pd.to_numeric(dfTaskWiseSuccessFail["Success"], downcast='integer')
        dfTaskWiseSuccessFail["Others"] = pd.to_numeric(dfTaskWiseSuccessFail["Others"], downcast='integer')
        
        figStudents =  dash_table.DataTable(
                id='datatable-taskwise-successfail',
                columns=[
                    {"name": i, "id": i, "deletable": True, "selectable": True} for i in dfTaskWiseSuccessFail.columns
                ],
                data            =   dfTaskWiseSuccessFail.to_dict('records'),
                editable        =   True,
                filter_action   =   "native",
                sort_action     =   "native",
                sort_mode       =   "multi",
                style_data_conditional = ([
                            {
                                'if': {'row_index': 'odd'},
                                'backgroundColor': constants.THEME_TABLE_ODDROW_COLOR_STYLE
                            },
                 ]) 
            )
            
        graphs.append(  
                html.Div([ figStudents ],
                         className = "c-table ")
        )
        graphIndex = graphIndex + 1
        

        
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
                        children = figStudents
                ))
            graphIndex = graphIndex + 1
        except Exception as e: 
                print('plotSingleClass 1 ')
                print(e)
                
        try :
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
                        children = figStudents
                ))
            graphIndex = graphIndex + 1
        
        except Exception as e: 
                print('plotSingleClass 2 ')
                print(e)
        
        
        
    #            CHECKED
    #            count of tasks completed by each student    
        graphTitle = '(Practice) Count of tasks completed by students'
        try: 
            studentWiseDataOriginalTaskPerformed = groupOriginal
            studentWiseDataOriginalTaskPerformed[featureTaskDesc] = studentWiseDataOriginalTaskPerformed['Title'] + ' (Id: ' + studentWiseDataOriginalTaskPerformed['PracticeTaskId'].astype(str) + ')' 
            studentWiseDataOriginalTaskPerformed = studentWiseDataOriginalTaskPerformed [ studentWiseDataOriginalTaskPerformed['Result'] == 1][['StudentId', 'PracticeTaskId'
                          , 'Result', 'Name', featureTaskDesc]].groupby(
                          ['StudentId', 'Name']).agg({'PracticeTaskId': ['nunique'], featureTaskDesc: ['unique']})
            studentWiseDataOriginalTaskPerformed = studentWiseDataOriginalTaskPerformed.reset_index()
            studentWiseDataOriginalTaskPerformed.rename(columns={'PracticeTaskId': countTaskCompletedByStudentFeature}, inplace=True)
            studentWiseDataOriginalTaskPerformed.columns = studentWiseDataOriginalTaskPerformed.columns.droplevel(1)
            
            studentWiseDataOriginalTaskPerformed[featureTaskDesc] = studentWiseDataOriginalTaskPerformed[featureTaskDesc].apply(convert_list_column_tostr_NL)
            studentWiseDataOriginalTaskPerformed[featureTaskType] = TaskTypePractice
            
            
            figStudents, graphQuantile = getFeaturePlot(studentWiseDataOriginalTaskPerformed, 
                           countTaskCompletedByStudentFeature, 
                           'Name', graphTitle, [featureTaskDesc], isColored = False, hasMeanStd = False)
                       
            
            graphs.append(
                    html.Div(
                        children = figStudents
                ))

            graphIndex = graphIndex + 1
        except Exception as e:             
            print( 'ERROR - ' + graphTitle )   
            print(e)
        
        graphTitle = '(Theory) Count of tasks completed by students'
        try: 
            studentWiseDataOriginalTaskPerformedTheory = groupOriginalTheory
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory.merge(right= dfTheoryTaskDetails
                                              , left_on='TheoryTaskId', right_on='TheoryTaskId'
                                                , left_index=False, right_index=False
                                                , how='inner')
            studentWiseDataOriginalTaskPerformedTheory[featureTaskDesc] = studentWiseDataOriginalTaskPerformedTheory['Title'] + ' (Id: ' + studentWiseDataOriginalTaskPerformedTheory['TheoryTaskId'].astype(str) + ')' 
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory [ studentWiseDataOriginalTaskPerformedTheory['Result'] == 1][['StudentId', 'TheoryTaskId'
                          , 'Result', 'Name', featureTaskDesc]].groupby(
                          ['StudentId', 'Name']).agg({'TheoryTaskId': ['nunique'], featureTaskDesc: ['unique']})
            studentWiseDataOriginalTaskPerformedTheory = studentWiseDataOriginalTaskPerformedTheory.reset_index()
            studentWiseDataOriginalTaskPerformedTheory.rename(columns={'TheoryTaskId': countTaskCompletedByStudentFeature}, inplace=True)
            studentWiseDataOriginalTaskPerformedTheory.columns = studentWiseDataOriginalTaskPerformedTheory.columns.droplevel(1)
            studentWiseDataOriginalTaskPerformedTheory[featureTaskDesc] = studentWiseDataOriginalTaskPerformedTheory[featureTaskDesc].apply(convert_list_column_tostr_NL)
            studentWiseDataOriginalTaskPerformedTheory[featureTaskType] = TaskTypeTheory
            
            figStudents, graphQuantile = getFeaturePlot(studentWiseDataOriginalTaskPerformedTheory, 
                           countTaskCompletedByStudentFeature, 
                           'Name', graphTitle, [featureTaskDesc], isColored = True, hasMeanStd = False)
                        
            
            graphs.append(
                    html.Div(
                        children = figStudents
                ))
            graphIndex = graphIndex + 1
            
            
        except Exception as e: 
            print( 'ERROR - ' + graphTitle )  
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
featureX = 'Count (no. of students used)'
featureY = 'Details'
featurePracticeTaskGroup = 'Task-Id'            

def plotGroupTaskWiseConcepts(groupId, isGrouped = True, taskId = 0 ) :
    
    graphs = []
    
    try :
        taskWiseConceptPracticeGrouped = dfGroupedPracticeTaskWise.get_group(groupId).groupby(['PracticeTaskId'])
        
        studentWiseTaskWiseConceptPractice = pd.DataFrame()
        
        
        
        if not taskId is None and  taskId > 0 and taskId in taskWiseConceptPracticeGrouped.groups.keys():
            
            groupTask = taskWiseConceptPracticeGrouped.get_group(taskId)
            
            studentWiseDataConceptsTask = groupTask.sum()
            
            colY = hasFeatures
           
            studentWiseDataConceptsTask = pd.DataFrame(studentWiseDataConceptsTask)
            studentWiseDataConceptsTask['PracticeTaskId'] = taskId
            studentWiseDataConceptsTask['Title'] = dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == taskId ]['Title'].astype(str).values[0]
            studentWiseDataConceptsTask[featurePracticeTaskGroup] = constants.TaskTypePractice + '-' + str(taskId)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask.index
            studentWiseDataConceptsTask = studentWiseDataConceptsTask.rename(columns={0: featureX})
            studentWiseDataConceptsTask.drop(studentWiseDataConceptsTask[~studentWiseDataConceptsTask[featureY].isin(colY)].index, inplace = True)
            
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].astype(str)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].replace(
                    feature2UserNamesDict, regex=True)
            
            taskTitle = str(taskId)
            try :
                taskTitle =  dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == taskId ]['Title'].astype(str).values[0]
            except Exception as e: 
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
                )) 
            
            return graphs
        
        
        for groupKeyTaskId, groupTask in taskWiseConceptPracticeGrouped:
            
            studentWiseDataConceptsTask = groupTask.sum()
            
            colY = hasFeatures
           
            studentWiseDataConceptsTask = pd.DataFrame(studentWiseDataConceptsTask)
            studentWiseDataConceptsTask['PracticeTaskId'] = groupKeyTaskId
            studentWiseDataConceptsTask['Title'] = dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == int(groupKeyTaskId) ]['Title'].astype(str).values[0]
            studentWiseDataConceptsTask[featurePracticeTaskGroup] = constants.TaskTypePractice + '-' + str(groupKeyTaskId)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask.index
            studentWiseDataConceptsTask = studentWiseDataConceptsTask.rename(columns={0: featureX})
            studentWiseDataConceptsTask.drop(studentWiseDataConceptsTask[~studentWiseDataConceptsTask[featureY].isin(colY)].index, inplace = True)
            
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].astype(str)
            studentWiseDataConceptsTask[featureY] = studentWiseDataConceptsTask[featureY].replace(
                    feature2UserNamesDict, regex=True)
            
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
                                , hover_data  =  [ 'Title', 'PracticeTaskId',  ]
                                , template      =   constants.graphTemplete   
                                , title         =   "(Practice) Concepts used by students in each task <br> (no. of students used a concept in code for a task)"
                                , labels        =   feature2UserNamesDict # customize axis label
                                , color         =   featurePracticeTaskGroup
                                , barmode       =   'group'
                )
            return figGroupedTaskConcepts
                
        return graphs
    except Exception as e: 
        print('plotGroupTaskWiseConcepts  last ')
        print(e)               


def getGroupPTaskDoneOptions(groupId) :
    options = []
    
    try :
        taskWiseConceptPracticeGrouped = dfGroupedPracticeTaskWise.get_group(groupId).groupby(['PracticeTaskId'])
        
        for groupKeyTaskId, groupTask in taskWiseConceptPracticeGrouped:            
            options.append({
                    'label' : '(TaskId ' + str(groupKeyTaskId) + ')' + dfPracticeTaskDetails[ dfPracticeTaskDetails['PracticeTaskId'] == int(groupKeyTaskId) ]['Title'].astype(str).values[0],
                    'value' : groupKeyTaskId
                    
            })
                    
        return options
    except Exception as e: 
        print('getGroupPTaskDoneOptions')
        print(e)    
    
    return options
        
        
def plotGroupConceptDetails(groupId):
    
    graphs = []
    
    graphs.append(html.Div(id='Concept-Information',
                           children = [html.H2('Concept Information')], 
                           className = "c-container p_medium p-top_xx-large", 
                ))
      
    try :
        groupPractice = dfGroupedPractice.get_group(groupId)
        
    #        sum - to get count of students who used the concept
        studentWiseDataConcepts = groupPractice.sum()
               
        colY = hasFeatures
       
        studentWiseDataConcepts = pd.DataFrame(studentWiseDataConcepts)
        studentWiseDataConcepts[featureY] = studentWiseDataConcepts.index
        studentWiseDataConcepts = studentWiseDataConcepts.rename(columns={0: featureX})
        studentWiseDataConcepts.drop(studentWiseDataConcepts[~studentWiseDataConcepts[featureY].isin(colY)].index, inplace = True)
        
        studentWiseDataConcepts[featureY] = studentWiseDataConcepts[featureY].astype(str)
        studentWiseDataConcepts[featureY] = studentWiseDataConcepts[featureY].replace(
                feature2UserNamesDict, regex=True)
        
        
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
            ))
        
#        Task wise concepts used - grouped together
        try :
            figBar = plotGroupTaskWiseConcepts(groupId, isGrouped = True, taskId = 0 )
            graphs.append(
                    dcc.Graph(
                        figure= figBar
                ))
        except Exception as e: 
                print('Task Concepts used')
                print(e)                
      
    except Exception as e: 
            print('Task Concepts used')
            print(e)  
            
    return graphs        


def getFeaturePlot(df, featureX, featureY, title, hoverData, isColored = False, hasMeanStd = True, hoverName = "Name", hasDistribution = False):
    graphs = []
    
    if isColored:
        try :
            fig = px.bar( df
                , x             =  featureX
                , y             =  featureY
                , title         = title
                , labels        = feature2UserNamesDict # customize axis label
                , template      = constants.graphTemplete                              
                , orientation   = 'h'
                , hover_name    =  hoverName
                , hover_data    =  hoverData
                , color         = constants.featureTaskType
                , color_discrete_map     =   {
                    constants.TaskTypeTheory    : constants.colorTheory,
                    constants.TaskTypePractice  : constants.colorPractice, },
            )
            graphs.append(
                    dcc.Graph(
                        figure = fig
                ))
        except Exception as e: 
            print('getFeaturePlot  1st  ')
            print('title  ' + title)
            print(e)
        
    else:    
        try :
            fig = px.bar( df
                , x             =  featureX
                , y             =  featureY
                , title         = title
                , labels        = feature2UserNamesDict # customize axis label
                , template      = constants.graphTemplete                              
                , orientation   = 'h'
                , hover_name    =  hoverName
                , hover_data    =  hoverData
            )
            graphs.append(
                    dcc.Graph(
                        figure = fig
                ))
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
                                 y                      = featureX, 
                                 points                 = "all",
                                 title                  = "Distribution  - " + title,
                                 hover_data             = ['Name'] + hoverData,
                                 labels                 = feature2UserNamesDict , # customize axis label
                                 height                 =   constants.graphHeightMin,
                                 template               = constants.graphTemplete ,     
                                 color                  = constants.featureTaskType ,
                                 color_discrete_map     =   {
                                    constants.TaskTypeTheory    : constants.colorTheory,
                                    constants.TaskTypePractice  : constants.colorPractice, 
                                    },
                )
                
            figQuantile.update_layout(constants.THEME_EXPRESS_LAYOUT)
            graphDistributions.append( html.Div( dcc.Graph(
                    figure =  figQuantile
            )))
    except Exception as e: 
        print('getFeaturePlot  hasDistribution ')
        print('title  ' + title)
        print(e)
        
        
        

    return graphs, graphDistributions


def plotSingleClassGeneral( titleTextAdd, school ):
    
    graphs = []
    
    graphs.append(html.Div(id='General-Information',
                       children = [html.H2('General Information')], 
                       className = "c-container p_medium p-top_xx-large", 
            ))
    
      
    featuresPractice            = dfPlayerStrategyPractice.columns
                             
    
        
    try :
        groupPractice = dfGroupedPractice.get_group(school)
        groupOriginal = dfGroupedOriginal.get_group(school)
        
        try :
            groupOriginalTheory = dfGroupedPlayerStrategyTheory.get_group(school)
        except Exception as e: 
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
            
        except Exception as e: 
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
                                                                   hasDistribution = True)
                            
                            graphs.append(
                                    html.Div(
                                            children = featurePlot
                                    )
                            )               
                            graphs.append(  html.Div( getPlotDistributionPlotChildrens(graphDistributions, quantileIndex) ,
                                className = "c-container"
                            ))
                            quantileIndex += 1
                            
                            
                            featurePlot, graphDistributions = getFeaturePlot(studentWiseDataTheory, featuresPractice[first], featuresPractice[second], 
                                                                   '(Theory) Details of students ' + titleFirst,
                                                                   hoverDataTheory, isColored = True,
                                                                   hasDistribution = True)
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
                                                                   hasDistribution = True)
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
                        
                    featurePlot, graphDistributions = getFeaturePlot(studentWiseDataTheory, rowTheory[0], rowTheory[1] , 
                                                                   '(Theory) Details of students ' + titleFirst,
                                                                   hoverDataTheory, isColored = True,
                                                                   hasDistribution = True)
                    
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
                    print(e)


    except Exception as e: 
        print(e)


    return graphs        


def getPlotDistributionPlotChildrens(graphDistributions, quantileIndex = 0):
    return [dbc.Button( [  html.I(className="fas fa-info m-right-small"),
        "Show Distribution" ],
        id          = "groupDetails-collapse-distribution-button-" + str(quantileIndex),
        color       = "light",
        n_clicks    = 0,
        className   = "m-bottom_medium"
    ),
    dbc.Collapse(
        children = graphDistributions ,
        id = "groupDetails-collapse-distribution-" + str(quantileIndex),
        is_open = True
    ),]


#Student Interaction with Game - TIMELINE
def plotClassOverview(schoolKey):
    
    graphs = []
    rows = []
    columns = []

    features2Plot = ['Name', 'SessionDuration', 'PracticeSessionDuration', 'TheorySessionDuration', 
                     'Attempts', 'Points' 
                     ]
        
    studentDataDf = studentGrouped.getStudentsOfSchoolDF(schoolKey)
    
    
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
    
    rows.append( dbc.Row( html.Div([
                html.H3('Overview'), 
            ]) ) )
    fig1Table = dash_table.DataTable(
        columns=[
            {"name": constants.feature2UserNamesDict.get(i) if i in constants.feature2UserNamesDict.keys() else i , "id": i, "deletable": True, "selectable": True} for i in studentDataDfSum[features2Plot].columns
        ],
        data            = studentDataDfSum[features2Plot].to_dict('records'),
        editable        = True,
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
                    fig1Table 
                    , align ="center"                    
                    , className = "c-table "
    ))
    rows.append( dbc.Row( columns ) )
    
#    ---------------------------------------------
        
    
    graphs.append(html.Div(  rows  ))
    
    return graphs


def plotGroupOverview(groupId):
    
    groupStudents     =  getStudentsOfSchool(groupId)
    studentDataDf     =  studentGrouped.getStudentsOfSchoolDF(groupId)
    plots               = []
    
#    if not studentDataDf is None and not studentDataDf.empty:
    plots = util.plotGroupOverview(groupId, groupStudents, studentDataDf)
    
    return plots


#-----------------------------------------
# Layout-------------------------
#-------------------------------------------

layout = [
        html.Div([
                   
    html.Div(id='groupDetails-Group-Overview-Container')
    , dbc.Row([
            dbc.Col( 
                    html.A(children=[html.I(className="fas fa-download font-size_medium p_small"),
                       "download data : Group",], id = "details_download_group_overview_link", className = "hidden" ,
                                               href="", target="_blank",
                                               download='group-overview.csv' )
      )])
    
    , dbc.Row([
            dbc.Col( 
                    html.Div(id='groupDetails-Group-Container', className = "c-table ")
        )])
    
    
    , dbc.Row([
            dbc.Col( 
                html.Div(id='groupDetails-Group-Concept-Container', className = "c-table ")
       )])
                    
    , dbc.Row([
            dbc.Col( 
                dcc.Dropdown(
                    id = "groupDetails-taskId-selector",
                    placeholder = "Select Task to see details",
                    options = [ {'label': 'Select a group', 'value' : '0'}  ]
                )
       )])
    , dbc.Row([
          dbc.Col( 
                  html.Div(id='groupDetails-taskId-container', className = "c-container ")
        )])
                
                    
    , dbc.Row([
            dbc.Col( 
                html.Div(id='groupDetails-Group-General-Container', className = "c-table ")
       )])
    
    
    ])    
]


#-----------------------------------------
# callback functions---------------------
#        ---------------------------------
@app.callback(Output('groupDetails-Group-Container', 'children'), [Input('group-selector-main', 'value')])
def display_graphs(schoolSelected):
    graphs = []
    
    if schoolSelected is None or not int(schoolSelected) >= 0 :
        return html.Div(graphs)
    
#    graphs = plotSingleClass('School', format(schoolSelected) )
    graphs = plotSingleClass('School', int(schoolSelected) )
    
    return html.Div(graphs)


@app.callback(Output('groupDetails-Group-General-Container', 'children'), [Input('group-selector-main', 'value')])
def display_class_general(schoolSelected):
    graphs = []
    
    if schoolSelected is None or not int(schoolSelected) >= 0 :
        return html.Div(graphs)
    
#    graphs = plotSingleClass('School', format(schoolSelected) )
    graphs = plotSingleClassGeneral('School', int(schoolSelected) )
    
    return html.Div(graphs)


@app.callback(Output('groupDetails-Group-Concept-Container', 'children'), [Input('group-selector-main', 'value')])
def display_class_concept(schoolSelected):
    graphs = []
    
    if schoolSelected is None or not int(schoolSelected) >= 0 :
        return html.Div(graphs)
    
    graphs = plotGroupConceptDetails(int(schoolSelected) )
    
    return html.Div(graphs)
#----------------------------------------

@app.callback(Output('groupDetails-Group-Overview-Container', 'children'), [Input('group-selector-main', 'value')])
def setClassOverview(groupMain):
    graphs = []

    if groupMain is None or not int(groupMain) >= 0:
        return html.Div(graphs)
    
    graphs =    plotGroupOverview(int(groupMain))  
    
    graphs =  graphs + plotClassOverview( int(groupMain) )    
    

    return  html.Div(graphs)
    


# **IMPORTANT - Quantile Count must be updated when Adding Distribution Quantile Plots !!!!
quantileCount = 9
@app.callback(
    [Output(f"groupDetails-collapse-distribution-{i}", "is_open") for i in range(quantileCount)],
    [Input(f"groupDetails-collapse-distribution-button-{i}", "n_clicks") for i in range(quantileCount)],
    [State(f"groupDetails-collapse-distribution-{i}", "is_open") for i in range(quantileCount)],
)
def onClickDistributionCollapseButton(*args):
    ctx = dash.callback_context
    
    newToggle = [False] * (quantileCount)
    
    if not ctx.triggered:
        return newToggle
    
    newToggle = [args[index] for index in range(quantileCount, len(args))]

    
    triggered_id = [p['prop_id'] for p in ctx.triggered][0]
    clickedButton_id = triggered_id.split('.')[0]
    
    clickedButton_id_split = clickedButton_id.split('-')

    clickedButton_index = int( clickedButton_id_split[  len(clickedButton_id_split) - 1 ] )
    
    if clickedButton_index >= 0  and  args[clickedButton_index] :
        newToggle[clickedButton_index] = not args[quantileCount + clickedButton_index ]   # add 1 for URL pathname param
        
    
    return newToggle




#On Select a Group - set Group Task Done Options - see task wise information             
@app.callback(
    [Output("groupDetails-taskId-selector", "options") 
     ],
    [Input("group-selector-main", "value")]
)
def onSelectGroupSetTaskOptions(groupId):
    if groupId is not None and int(groupId) >= 0:
        return [getGroupPTaskDoneOptions(groupId)]
    
    return [[{'label': 'Select a group', 'value' : '0'}]]
    

@app.callback(
    [Output("groupDetails-taskId-container", "children") 
     ],
    [Input("groupDetails-taskId-selector", "value")],
    [State('group-selector-main', 'value'),
     ],
)
def onSelectTaskShowTaskWiseConcept(taskId, groupId):
    graphs = []
    
    if not taskId is None and int(taskId) >= 0 and groupId is not None and int(groupId) >= 0:
        graphs = plotGroupTaskWiseConcepts( int(groupId), isGrouped = False, taskId = int(taskId) )  
        
    
    return  [html.Div(graphs)]






#--------------------- data download callbacks 
@app.callback(
    [ Output('details_download_group_overview_link', 'href'),
     Output('details_download_group_overview_link', 'className'),
     ],
    [ Input("group-selector-main", "value"), ])
def update_download_link__details_group(groupMain):
    if groupMain is None or not int(groupMain) >= 0 or groupMain == "":
        return "", "hidden"
    
    csv_string = util.get_download_link_data_uri( studentGrouped.getStudentsOfSchoolDF(int(groupMain)) )
    return csv_string, ""