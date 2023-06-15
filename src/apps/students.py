# -*- coding: utf-8 -*-

"""
Created on   Aug  1 10:55:10 2020
Reworked on  Mar 14 10:25:00 2023

@authors: tilan, zangl
"""


#----------------------------------------------------------------------------------------------------------------------
# imports
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
from dash.dependencies import Input, Output, State, ALL
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.figure_factory as ff
import chart_studio.plotly as py
from plotly import graph_objs as go
import os

from app import app
from apps import classes

from data import studentGrouped
import constants
import util
import subprocess
import traceback
import datetime


#----------------------------------------------------------------------------------------------------------------------
# global constants
feature2UserNamesDict               = constants.feature2UserNamesDict
countStudentCompletingTaskFeature   = constants.countStudentCompletingTaskFeature
countTaskCompletedByStudentFeature  = constants.countTaskCompletedByStudentFeature
featurePracticeTaskDesc             = constants.featurePracticeTaskDesc
featureTheoryTaskDesc               = constants.featureTheoryTaskDesc
featureTaskDesc                     = constants.featureTaskDesc
featureTaskType                     = constants.featureTaskType
featureDescription                  = constants.featureDescription
featureSessionDuration              = constants.featureSessionDuration

TaskTypePractice                    = constants.TaskTypePractice
TaskTypeTheory                      = constants.TaskTypeTheory

sortOrderDescending                 = constants.sortOrderDescending
sortOrderAscending                  = constants.sortOrderAscending

hasFeatures                         =  studentGrouped.hasFeatures

studentOverviewFeaturesDefault =   {
        constants.featureCollectedCoins : {
                constants.keyClassName : 'fas fa-coins ',
                constants.keyHasMeanStd : False,                
        }
        , constants.featureItemsCollectedCount : {
                constants.keyClassName : 'fas fa-memory ',
                constants.keyHasMeanStd : False,                
        }
        , constants.featureLineOfCodeCount : {
                constants.keyClassName : 'fas list-ol ',
                constants.keyHasMeanStd : False,                
        }
}

currentClassGlobal = -1
currentStudentGlobal = -1

#----------------------------------------------------------------------------------------------------------------------
# global database constants
dfStudentDetails                        = studentGrouped.dfStudentDetails

dfCourseDetails                         = studentGrouped.dfCourseDetails
dfSkillDetails                          = studentGrouped.dfSkillDetails
dfPracticeTaskDetails                   = studentGrouped.dfPracticeTaskDetails
dfTheoryTaskDetails                     = studentGrouped.dfTheoryTaskDetails
dfTaskDetails                           = studentGrouped.dfTaskDetails

dfGroupedOriginal                       = studentGrouped.dfGroupedOriginal
dfPlayerStrategyPractice                = studentGrouped.dfPlayerStrategyPractice  
dfGroupedPracticeTaskWise               = studentGrouped.dfGroupedPracticeTaskWise
dfGroupedPracticeDB                     = studentGrouped.dfGroupedPracticeDB
dfRuns                                  = studentGrouped.dfRuns

dfPlayerStrategyTheory                  = studentGrouped.dfPlayerStrategyTheory
dfGroupedPlayerStrategyTheory           = studentGrouped.dfGroupedPlayerStrategyTheory


#----------------------------------------------------------------------------------------------------------------------
# helper functions
getTaskWiseSuccessFail                  =  studentGrouped.getTaskWiseSuccessFail
getStudentsOfLearningActivity           =  studentGrouped.getStudentsOfLearningActivity


getPracticeDescription                  =  studentGrouped.getPracticeDescription
getTheoryDescription                    =  studentGrouped.getTheoryDescription


#----------------------------------------------------------------------------------------------------------------------
# Function to get data of student by serving student id, class id (and optional filter date)
# params:   studentId       (int) - integer containing student ID
#           schoolKey       (int) - integer containing class ID
#           selectedDate    (string) - string containing date of which the data is filtered by
# returns:  Dataframe with all important data of a student from a certain class
def getStudentData(studentId, schoolKey, selectedDate = '' ):
    
    print('getStudentData')
    
    studentData = pd.DataFrame()
    
    try :
        school                            = dfGroupedOriginal.get_group(schoolKey)
        studentData                       = school[school['StudentId'] == studentId]
        studentData['Finish']             = studentData['CreatedAt'] 
        studentData['Start']              = studentData['Finish'] - pd.to_timedelta(studentData[featureSessionDuration], unit='s')
        
        studentData['CodeDesc']           = studentData['Code'].str.replace('\n','<br>')
        
        studentData[featureDescription]   = getPracticeDescription(studentData, False)   
        studentData[featureDescription]   = '<b>Title</b>:' + studentData['Title'].astype(str)  + '<br>'+ studentData[featureDescription].astype(str)
        studentData[featureDescription]   = studentData[featureDescription].astype(str) + '<br><b>Code</b>:' + studentData['CodeDesc'].astype(str) 
        
        studentData = studentData.sort_values(by='Start')
        
        studentData['GroupBy']              = constants.TaskTypePractice + '-' + studentData['PracticeTaskId'].astype(str)  
        studentData['Task']                 = constants.TaskTypePractice  + '-' + studentData['PracticeTaskId'].astype(str)  
        studentData['IndexCol']             = studentData['Task'] + '-' +  studentData['Result'].astype('Int64').astype(str)   
        
        studentData['Finish']               = np.where(studentData['Finish'].isnull(), studentData['Start'].shift(-1), studentData['Finish'])
        
        studentData['Difference']           = (studentData['Finish'] - studentData['Start']).astype('timedelta64[s]')
        
        studentData[constants.featureTaskType] = constants.TaskTypePractice
    except Exception as e: 
        subprocess.Popen(['echo', 'getStudentData first Exception'])
        subprocess.Popen(['echo', str(e)])
        print(e)


    try :
        schoolTheory = dfGroupedPlayerStrategyTheory.get_group(schoolKey)
        schoolTheoryStudent = schoolTheory[schoolTheory['StudentId'] == studentId]
        
        schoolTheoryStudent['Finish']       =   schoolTheoryStudent['CreatedAt']
        schoolTheoryStudent['Start']        =   schoolTheoryStudent['Finish'] - pd.to_timedelta(schoolTheoryStudent[featureSessionDuration], unit='s')
        schoolTheoryStudent                 =   schoolTheoryStudent.sort_values(by='Start')
        
        schoolTheoryStudent['Difference']   =   (schoolTheoryStudent['Finish'] - schoolTheoryStudent['Start']).astype('timedelta64[s]')
        
        schoolTheoryStudent.loc[schoolTheoryStudent['Difference'] > schoolTheoryStudent[featureSessionDuration], 'Difference'] = schoolTheoryStudent[
                schoolTheoryStudent['Difference'] > schoolTheoryStudent[featureSessionDuration]][featureSessionDuration]        
        
        schoolTheoryStudent                 = schoolTheoryStudent.merge(right= dfTheoryTaskDetails[['TheoryTaskId', 'Title', 'Description']]
                                                  , left_on='TheoryTaskId', right_on='TheoryTaskId'
                                                  , left_index=False, right_index=False
                                                  , how='inner')
        schoolTheoryStudent.rename(columns={'Description': 'TheoryTaskDescription'}, inplace=True)
        
        schoolTheoryStudent[featureDescription] = getTheoryDescription(schoolTheoryStudent, False)  
        schoolTheoryStudent[featureDescription] = '<b>Title</b>:' + schoolTheoryStudent['Title'].astype(str) + '<br>'+ schoolTheoryStudent[featureDescription].astype(str) 
    
        schoolTheoryStudent['GroupBy']    = constants.TaskTypeTheory    + '-' +  schoolTheoryStudent['TheoryTaskId'].astype(str) 
        schoolTheoryStudent['Task']       = constants.TaskTypeTheory    + '-' +  schoolTheoryStudent['TheoryTaskId'].astype(str)  
        schoolTheoryStudent['IndexCol']   = schoolTheoryStudent['Task'] + '-' +  schoolTheoryStudent['Result'].astype(str) 
        
        schoolTheoryStudent[constants.featureTaskType] = constants.TaskTypeTheory
        
        if schoolTheoryStudent is not None and schoolTheoryStudent.empty == False:
            studentData = pd.concat([studentData, schoolTheoryStudent], ignore_index=True)
    except Exception as e:
        subprocess.Popen(['echo', 'getStudentData second Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)

    if studentData is None         or     studentData.empty   :
        return studentData
    
    if     None is not selectedDate         and         not selectedDate == ''     and   util.is_valid_date(selectedDate) :
        selectedDate = datetime.datetime.strptime(selectedDate, '%Y-%m-%d').date()
        studentDataGroupedDate     =   studentData.groupby([studentData['Start'].dt.date])
        studentData                =   studentDataGroupedDate.get_group(selectedDate)
    
    studentData['StartStr'] = '@' + studentData['Start'].dt.strftime('%Y-%m-%d %H:%M:%S') + '-' + studentData['IndexCol'].astype(str)

    return studentData


#----------------------------------------------------------------------------------------------------------------------
# Function to check wether student is in a class
# params:   StudentId       (int) - integer containing student ID
#           schoolKey       (int) - integer containing class ID
# returns:  Boolean stating if student is in class or not
def isStudentInClass(studentId, classId) :
    try:
        groupStudents = getStudentsOfLearningActivity(classId)
        if not studentId in groupStudents:
            return False
        return True

    except Exception as e:
        subprocess.Popen(['echo', 'isStudentInClass Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)


#----------------------------------------------------------------------------------------------------------------------
# Function to plot the Student Overview subsection
# params:   studentId       (int) - integer containing student ID
#           classId         (int) - integer containing class ID
# returns:  List containing html and dbc components with relevant graphs
def plotStudentOverview(studentId, classId):
    
    graphs = []
    
    try:
    #    the student is not in the group
        if not isStudentInClass(studentId, classId) :
            return graphs
        
        studentDataDf                     = getStudentData(studentId, classId)
        
        if studentDataDf is None or studentDataDf.empty == True :
            graphs.append(
                    util.getNoDataMsg()
            )
            return graphs
        
        studentDataDf.fillna(0, inplace=True)
        graphs = util.plotStudentOverview(studentDataDf , classes = "c-card-small" )
        
        plotRow = []
    
        groupOriginal                           = dfGroupedOriginal.get_group(classId)
        
        groupOriginal['ConceptsUsed']           = groupOriginal['Code'].apply( studentGrouped.getAllNodeTypesUsefull )
        groupOriginal["ConceptsUsedDetails"]    = groupOriginal['ConceptsUsed'].replace(
                                                        constants.ProgramConceptsUsefull2UserNames, regex=True )
        
        studentWiseData                         = groupOriginal.groupby(['StudentId'], as_index=False).sum()
        studentDataDfPractice                   = studentWiseData[studentWiseData['StudentId'] == studentId]
        
        studentDataDfSuccess                    =     studentDataDf[studentDataDf['Result'].astype('Int64') > 0 ]
        
        if studentDataDfSuccess is not None and studentDataDfSuccess.empty is False  and 'Task' in studentDataDfSuccess.columns:        
            plotRow.append( html.Div([  
                                        util.generateCardDetail([html.I(className="fas fa-cubes m-right-small"),   'No. of Tasks completed'], 
                                            '' + util.millify(len(studentDataDfSuccess['Task'].unique())), 
                                            '' + str(  len(studentDataDfSuccess[studentDataDfSuccess[constants.featureTaskType] == constants.TaskTypePractice ]['Task'].unique()) ), 
                                            '' + str(  len(studentDataDfSuccess[studentDataDfSuccess[constants.featureTaskType] == constants.TaskTypeTheory ]['Task'].unique()) ), 
                                            constants.labelTotal  ,
                                            constants.TaskTypePractice,
                                            constants.TaskTypeTheory ,
                                            classes = "c-card-small" 
                                            )
                                    ],
                                    className="col-sm-4",
                            ))
            
        for feature2OKey in studentOverviewFeaturesDefault.keys():
            currentFeatureO = studentOverviewFeaturesDefault.get(feature2OKey)
            
            if constants.keyHasMeanStd in currentFeatureO.keys() and currentFeatureO.get(constants.keyHasMeanStd):
                plotRow.append( html.Div([
                                        util.generateCardDetail(
                                                    [html.I(className =  html.I(className=  currentFeatureO.get(constants.keyClassName)) +  " m-right-small"), 
                                                    ((constants.feature2UserNamesDict.get(feature2OKey)) if feature2OKey in constants.feature2UserNamesDict.keys() else feature2OKey ) ], 
                                                    studentDataDf[feature2OKey].sum().round(decimals=2) ,
                                                    studentDataDf[feature2OKey].mean().round(decimals=2) , 
                                                    studentDataDf[feature2OKey].std().round(decimals=2) , 
                                                    constants.labelTotal  ,
                                                    constants.labelMean ,
                                                    constants.labelStd ,
                                                    classes = "c-card-small" )
                                        ],
                                        className="col-sm-4",
                                ))
            else:
                if feature2OKey in studentDataDfPractice.columns:
                    plotRow.append( html.Div([
                                                util.generateCardBase(
                                                        [   html.I(className=  currentFeatureO.get(constants.keyClassName) +  " m-right-small"), 
                                                            ((constants.feature2UserNamesDict.get(feature2OKey)) if feature2OKey in constants.feature2UserNamesDict.keys() else feature2OKey ) ], 
                                                        studentDataDfPractice[feature2OKey].sum() ,
                                                        classes = "c-card-small" )
                                            ],
                                            className="col-sm-4",
                                    ))
                elif feature2OKey in studentDataDf.columns:
                    plotRow.append( html.Div([
                                                util.generateCardBase(
                                                        [   html.I(className=  currentFeatureO.get(constants.keyClassName) +  " m-right-small"), 
                                                            ((constants.feature2UserNamesDict.get(feature2OKey)) if feature2OKey in constants.feature2UserNamesDict.keys() else feature2OKey ) ], 
                                                        studentDataDf[feature2OKey].sum() ,
                                                        classes = "c-card-small" )
                                            ],
                                            className="col-sm-4",
                                    ))
        
        if groupOriginal[groupOriginal['StudentId'] == studentId] is not None and groupOriginal[groupOriginal['StudentId'] == studentId]['ConceptsUsedDetails'].shape[0] > 0 :        
            try :
                ConceptsUsedUnique = util.get_unique_list_feature_items(groupOriginal[groupOriginal['StudentId'] == studentId], 'ConceptsUsedDetails')
                
                if     ConceptsUsedUnique is not None  :        
                    
                    ConceptsUsedUniqueUserReadable = set()
                    for conceptUsed in ConceptsUsedUnique:
                        ConceptsUsedUniqueUserReadable.add( constants.ProgramConceptsUsefull2UserNames.get(conceptUsed) if 
                                                            conceptUsed in constants.ProgramConceptsUsefull2UserNames 
                                                            else 
                                                            conceptUsed)
                    
                    plotRow.append( html.Div([
                                                util.generateCardBase(
                                                        [html.I(className="fas fa-code m-right-small"), 'Concepts Used'], 
                                                        ', '.join(ConceptsUsedUniqueUserReadable) ,
                                                        classes = "c-card-small" )
                                            ],
                                            className="col-sm-6",
                                    ))
            except Exception as e:
                subprocess.Popen(['echo', 'student overview Concepts Used Error'])
                subprocess.Popen(['echo', str(e)]) 
                print(' student overview Concepts Used Error ')
                print(e)
        
        graphs.append(
                html.Div(children  = plotRow,                
                        className = "row")
        )
    
    except Exception as e:
        subprocess.Popen(['echo', 'plotStudentOverview big Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)

    return graphs


#----------------------------------------------------------------------------------------------------------------------
# Function to plot the Student Courses Progress Tracker
# params:   studentId       (int) - integer containing student ID
#           classId         (int) - integer containing class ID
# returns:  List containing html and dbc components with relevant graphs
def createProgressChildren(studentId, classId):
    
    graphs = []

    try:
        if not isStudentInClass(studentId, classId):
            return graphs

        studentDataDf = getStudentData(studentId, classId)
        
        if studentDataDf is None or studentDataDf.empty == True:
            graphs.append(util.getNoDataMsg())
            return graphs

        studentDataDf.fillna(0, inplace=True)
        studentDataDfSuccess = studentDataDf[studentDataDf['Result'].astype('Int64') > 0]

        if studentDataDfSuccess is not None and studentDataDfSuccess.empty is False  and 'Task' in studentDataDfSuccess.columns:        
            
            print('skill studentdatadf')

            tasksCompleted = studentDataDfSuccess['Task'].unique()
            dfTasksCompleted = dfTaskDetails[dfTaskDetails['Task'].isin(tasksCompleted)]

            graphs.append(html.H3("Student Courses Progress Tracker", className = "p-bottom_medium p-top_large"))       

            for courseIdAttempt in dfTasksCompleted['CourseId'].unique():
                graphs.append( getCourseProgressCard(courseIdAttempt, dfTasksCompleted))

    except Exception as e:
        subprocess.Popen(['echo', 'createProgressChildren Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)

    return graphs


#----------------------------------------------------------------------------------------------------------------------
# Function to generate the Student Courses Progress Tracker Cards (each course gets one card)
# params:   courseId            (int)       - integer containing course ID
#           dfTasksCompleted    (Dataframe) - pandas Dataframe containing completed Tasks
# returns:  html Div component with course and skill progress data
def getCourseProgressCard(courseId, dfTasksCompleted):
    try:

        completeCourseTasks = dfTaskDetails[dfTaskDetails["CourseId"] == courseId]
        courseSkillIdAttempt = completeCourseTasks[completeCourseTasks['CourseId'] == courseId]['SkillId'].unique()
                
        skillsDiv = []
        for skillIdAttempt in courseSkillIdAttempt:

            totalTasksOfSkillUniqueList = dfTaskDetails[dfTaskDetails['SkillId'] == skillIdAttempt]['Task'].unique()
            totalCompletedTasksOfSkillUniqueList = dfTasksCompleted[dfTasksCompleted['SkillId'] == skillIdAttempt]['Task'].unique()
            totalNotCompletedTasksOfSkillUniqueList = [x for x in totalTasksOfSkillUniqueList if x not in totalCompletedTasksOfSkillUniqueList]

            skillTitle = dfTaskDetails[dfTaskDetails['SkillId'] == skillIdAttempt]['TitleSkill'].unique()
            progressSkill = math.ceil(len(totalCompletedTasksOfSkillUniqueList) * 100 / len(totalTasksOfSkillUniqueList))
            tasksCompletedDetails =  []
            tasksNotCompletedDetails = []

            for taskId in totalCompletedTasksOfSkillUniqueList:
                currentTask = dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]
                classNameAddOn = ""
                if(currentTask["TaskType"].iloc[0] == "Practice"):
                    classNameAddOn = "rgb(76, 114, 176)"
                elif(currentTask["TaskType"].iloc[0] == "Theory"):
                    classNameAddOn = "rgb(214, 12, 140)"

                tasksCompletedDetails.append(html.Details(
                            children = [
                                    html.Summary(currentTask['Title']),
                                    html.P('Task: ' + str(taskId) + 
                                        ';   Description: '  + currentTask['Description'] + ' \n'),
                                ],
                                className = "c-details",
                                style = {"color": classNameAddOn}
                        ))
                
            for taskId in totalNotCompletedTasksOfSkillUniqueList:
                currentTask = dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]
                classNameAddOn = ""
                if(currentTask["TaskType"].iloc[0] == "Practice"):
                    classNameAddOn = "rgb(76, 114, 176)"
                elif(currentTask["TaskType"].iloc[0] == "Theory"):
                    classNameAddOn = "rgb(214, 12, 140)"
                tasksNotCompletedDetails.append(html.Details(
                            children = [
                                    html.Summary(currentTask['Title']),
                                    html.P('Task: ' + str(taskId) + 
                                        ';   Description: '  + currentTask['Description'] + ' \n'),
                                ],
                                className = " c-details ",
                                style = {"color": classNameAddOn}
                        ))
            
            skillsDiv.append(html.Div(children= [
                html.Div(
                        children = [
                                    html.Div( skillTitle + '-' +  str(skillIdAttempt) ),
                                    dbc.Progress(str(progressSkill) + "%", value = progressSkill, className= " c-progress ",
                                                color = "success" if progressSkill == 100 else "primary", ), 
                                    html.Div(
                                            children = [ 'Skill' ],
                                            className="card_value_label"
                                        ) ],
                        className=" card_value_details  col-2  "
                    ),
                html.Div(
                        children =[ html.Div(
                                            children = [ 'Completed Tasks: ' ],
                                            className="card_value_label"
                                        ),
                                    ] + tasksCompletedDetails,
                        className=" card_value_details  col-10  align-left "
                    ),
                html.Div(
                        children = [],
                        className=" card_value_details  col-2  "
                    ),    
                html.Div(
                        children =[ html.Div(
                                            children = [ 'Not Completed Tasks: ' ],
                                            className="card_value_label"
                                        ),
                                    ] + tasksNotCompletedDetails,
                        className=" card_value_details  col-10  align-left "
                    ),
            ], className = "row m-bottom_small p_small", style = {"border": "2px groove grey"}))
        

        totalTasksOfCourseUniqueList = dfTaskDetails[dfTaskDetails['CourseId'] == courseId]['Task'].unique()
        totalCompletedTasksOfCourseUniqueList = dfTasksCompleted[dfTasksCompleted['CourseId'] == courseId]['Task'].unique()
        totalNotCompletedTasksOfCourseUniqueList = [x for x in totalTasksOfCourseUniqueList if x not in totalCompletedTasksOfCourseUniqueList]

        courseTitle = dfTaskDetails[dfTaskDetails['CourseId'] == courseId]['TitleCourse'].unique()
        progressCourse = math.ceil(len(totalCompletedTasksOfCourseUniqueList) * 100 / len(totalTasksOfCourseUniqueList)) 

        return html.Div( html.Div(
            [
                html.Div(
                    children = [
                                html.Div( courseTitle + '-' +  str(courseId)  , className = "m-bottom_small"),
                                dbc.Progress(str(progressCourse) + "%", value = progressCourse, className= " c-progress ",
                                                color = "success" if progressCourse == 100 else "primary", ), 
                                html.Div(
                                        getCurrentSelectedStudentName() + ' completed ' + str(len(totalCompletedTasksOfCourseUniqueList)) + ' of ' + str(len(totalTasksOfCourseUniqueList)) + ' tasks in this course.',
                                        className="card_value_label m-top_x-small"
                                    ),  ],
                    className="card_value_title col-12 m-top_small"
                ),
                html.Div(children = skillsDiv, className = "col-12"),
            ],
            className="c-card  c-card-small   row",
        ),
        className = "col-sm-12 m-bottom_medium" )
    
    except Exception as e:
        subprocess.Popen(['echo', 'getCoursePProgressCard Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)
        

#----------------------------------------------------------------------------------------------------------------------
# Function to generate the graphs of Student interactions with the tasks and the timeline
# params:   studentId               (int)    - integer containing student ID
#           schoolKey               (int)    - integer containing class ID
#           studentSelectedDate     (string) - string containing date of which the data is filtered by 
#           studentGraphDirection   (string) - string containing info about data is sorted desc or asc
# returns:  list containing relevant graphs (student interactions and timeline)
def plotStudent(studentId, schoolKey, studentSelectedDate = '', studentGraphDirection = sortOrderDescending):
    
    graphs = []
    
    try:    
    #    the student is not in the group
        if not isStudentInClass(studentId, schoolKey):
            return graphs
        
        studentData = getStudentData(studentId, schoolKey, studentSelectedDate)

        if studentData is None or studentData.empty == True :
            graphs.append(
                    util.getNoDataMsg()
            )
            return graphs
        
    #    studentData                     = studentData.sort_values(by='Start')
            
        isAscending = True
        if None is not studentGraphDirection and not studentGraphDirection == '' and studentGraphDirection == sortOrderDescending :
            isAscending = False
            
        studentData.sort_values(by = 'Start', inplace=True, ascending = isAscending )
        
        studentData.loc[studentData[constants.featureTaskType]   == constants.TaskTypePractice, 'color']     =   constants.colorPractice
        studentData.loc[studentData[constants.featureTaskType]   == constants.TaskTypeTheory, 'color']       =   constants.colorTheory
        studentData.loc[(studentData[constants.featureTaskType]  == constants.TaskTypePractice) & 
                        (studentData['Result']  == 0), 'color']                                              =   constants.colorPracticeError
        studentData.loc[(studentData[constants.featureTaskType]  == constants.TaskTypeTheory) & 
                        (studentData['Result']  == 0), 'color']                                              =   constants.colorTheoryError

        studentData['Task'] = studentData['IndexCol']
        studentData['Text'] = studentData['Difference'].astype(str) + 's for ' + studentData[constants.featureTaskType].astype(str) + ' Task : ' +  studentData['Title' ]  + ' Result : ' +  studentData['Result'].astype(str)

        colors = {
            constants.TaskTypePractice            : constants.colorPractice,
            constants.TaskTypeTheory              : constants.colorTheory,
            constants.TaskTypePractice   + '-1'   : constants.colorPractice,
            constants.TaskTypeTheory     + '-1'   : constants.colorTheory,
            constants.TaskTypePractice   + '-0'   : constants.colorPracticeError,
            constants.TaskTypeTheory     + '-0'   : constants.colorTheoryError
        }
        
        studentData['IndexSuccFail'] = studentData[constants.featureTaskType] + '-' +  studentData['Result'].astype(str)
        
        graphHeightRows = (studentData.shape[0] * 40)
        graphHeightRows = graphHeightRows if (graphHeightRows > (constants.graphHeightMin + 100)) else (constants.graphHeightMin + 100)
        
        #type 2 
        fig = go.Figure()
        fig.add_traces(go.Bar(
                        x               =  studentData['Difference'],
                        y               = studentData['StartStr'] ,
                        text            = studentData['Text'] , 
                        textposition    = 'auto'  ,    
                        orientation     = 'h',
                        marker          =  dict( color = studentData['color']   ) ,
                        customdata      = np.stack(( studentData['Title'],
                                                studentData['Description'] 
                                ), axis=-1) ,
                        hovertemplate   = "<br>" +
                                    "%{customdata[1]}<br>"     
                                    
                        )
        )
        fig.update_layout(
                                    height        =  graphHeightRows, 
                                    title_text    = 'Details of Student\'s Game Interactions',
                                    yaxis = dict(
                                        title = 'Time',
                                        titlefont_size = 16,
                                        tickfont_size = 14,),
                                    xaxis = dict(
                                        title = 'Duration (s)',
                                        titlefont_size = 16,
                                        tickfont_size = 14)                   
        )
        graphs.append(
                    dcc.Graph(
                        figure= fig
                    )
                
                if  constants.languageLocal  != 'en' else
                
                    dcc.Graph(
                        figure= fig,
                        config = dict (locale = constants.languageLocal) 
                    )
            )
        
    #    gantt chart for timeline 
    #    if studentData is not None and studentData.empty == False :    
        studentData['Task'] = studentData['GroupBy']
        
        graphHeightRows = (len(studentData['Task'].unique()) * 40)
        graphHeightRows = graphHeightRows if (graphHeightRows > (constants.graphHeightMin + 100)) else (constants.graphHeightMin + 100)

        fig = ff.create_gantt(studentData, 
                            title             =   constants.labelStudentTimeline , 
                            colors            =   colors ,
                            index_col         =   'IndexSuccFail' , 
                            group_tasks       =   True ,
                            show_colorbar     =   True , 
                            bar_width         =   0.8 , 
                            showgrid_x        =   True , 
                            showgrid_y        =   True ,
                            show_hover_fill   =   True ,
                            height            =   graphHeightRows ,
                            )
        
        graphs.append(
                    dcc.Graph(
                        figure= fig
                    )

                if  constants.languageLocal  != 'en' else

                    dcc.Graph(
                        figure= fig,
                        config = dict (locale = constants.languageLocal) 
                    )
        )
    
    except Exception as e:
        subprocess.Popen(['echo', 'plotStudent Exception'])
        subprocess.Popen(['echo', str(e)])
        subprocess.Popen(['echo', str(traceback.format_exc())])
        print(e)

    return graphs


#----------------------------------------------------------------------------------------------------------------------
# Function to generate the learning activity buttons (class buttons)
# params:   none
# returns:  list containing the class buttons the user has access to
def createUserLAOptionsButtons():
    buttonsList = []

    userLAOptions = classes.getUserLAOptions()
    for option in userLAOptions:
        buttonLabel = option["label"]
        buttonValue = int(option["value"])
        buttonsList.append(html.Button(buttonLabel, id = {"button-type": "students-select-classes-button", "class-id": buttonValue}))

    return buttonsList


#----------------------------------------------------------------------------------------------------------------------
# Function to create button label (Student name)
# params:   buttonId        (int) - integer containing the button id (here it is also the student id)
# returns:  string containing the name of the student with right id (buttonId)
def getButtonLabel(buttonId):
    dfstudents = dfStudentDetails[dfStudentDetails[constants.STUDENT_ID_FEATURE].isin([buttonId])][['StudentId', 'Name']].drop_duplicates(subset=['StudentId'], keep='first')

    for index, row in dfstudents.iterrows():
        studentId = row['StudentId']
        studentName = row['Name']

        if(studentId == buttonId):
            return studentName
        
    return "something went wrong with button label function"


#----------------------------------------------------------------------------------------------------------------------
# Function to create student selection buttons
# params:   classId        (int) - integer containing the class id
# returns:  list of html buttons whcih are the student slection buttons
def createStudentButtonsFromClassId(classId):

    studentButtonsList = []
    studentsIdList = getStudentsOfLearningActivity(classId)
    dfstudents = dfStudentDetails[dfStudentDetails[constants.STUDENT_ID_FEATURE].isin(studentsIdList)][['StudentId', 'Name']].drop_duplicates(subset=['StudentId'], keep='first')

    for index, row in dfstudents.iterrows():
        studentId = row['StudentId']
        studentName = row['Name']
        studentButtonsList.append(html.Button(studentName, id = {"button-type": "students-select-student-button", "student-id": studentId}))

    return studentButtonsList


#----------------------------------------------------------------------------------------------------------------------
# Function to get current selected student name
# params:   none
# returns:  string containing the name of the student that is currently selected
def getCurrentSelectedStudentName():

    studentName = ""

    try :
        school                            = dfGroupedOriginal.get_group(currentClassGlobal)
        studentData                       = school[school['StudentId'] == currentStudentGlobal]
        studentName                       = studentData["Name"].iloc[0]
        
    except Exception as e: 
        subprocess.Popen(['echo', 'getSelectedStudent exception'])
        subprocess.Popen(['echo', str(e)])
        print(e)

    return studentName


#----------------------------------------------------------------------------------------------------------------------
# students tab layout - used in main layout (located in index.py)
layout = [
    html.Div([

        html.Div(html.H1('Select a Class', id = 'students-select-a-class-heading', className = "align-center"), className = "custom-heading-select-a-class"),

        html.Div(createUserLAOptionsButtons(), className = 'm-top_small m-left-right-small choose-learning-activity-buttons', id = 'students-learning-activity-selection-div'),

        html.Div(html.Button('Select other Class', id = {"button-type": "students-select-classes-button", "class-id": -1}), className = 'm-top_small m-left-right-small choose-learning-activity-buttons hidden', id = "students-button-select-other-la-div"),

        html.Hr(id = 'students-select-student-hr', className = "hr_custom_style hidden"),

        html.Div(html.H1('Select a Student', id = 'students-select-a-student-heading', className = "align-center"), id = 'students-select-a-student-heading-div', className = 'stick-on-top-of-page hidden'),

        html.Div(children = [], className = 'm-top_small m-left-right-small choose-students-buttons hidden', id = 'students-selection-div'),

        html.Div(html.Button('Select other Student', id = {"button-type": "students-select-student-button", "student-id": -1}), className = 'm-top_small m-left-right-small choose-students-buttons hidden', id = "students-button-select-other-student-div"),

        html.Hr(id = 'students-overview-hr', className = "hr_custom_style hidden"),

        html.Div(html.H3('Student Overview', className = "p-bottom_medium p-top_large"), id = 'students-overview', className = "c-container m-left-right-medium hidden"),

        html.Div(id = 'students-overview-container', className = "c-container m-left-right-medium m-bottom_medium hidden"),

        html.Hr(id = 'students-progress-tracker-hr', className = "hr_custom_style hidden"),

        html.Div(id = 'students-progress-tracker-container', className = "c-container m-left-right-medium m-bottom_medium hidden"),

        html.Hr(id = 'students-game-interactions-hr', className = "hr_custom_style hidden"),

        html.Div(children = [
            html.H3("Student Game Interactions and Timeline", className = "p-bottom_small p-top_large"),
            html.P(constants.studentsGameInteractionParagraph, className = "normal-paragraph m-bottom_small")
        ], id = "students-game-interactions-header-div", className = "c-container m-left-right-medium hidden"),

        html.Div(
            dbc.Row([
                dbc.Col(html.Div([dcc.Dropdown(id = 'students-date-dropdown', placeholder = "Select Date")], id = "students-date-dropdown-div", className = "c-container hidden"), width = 6),

                dbc.Col(
                    html.Div([
                        dcc.Dropdown(
                                id = 'students-sort-order-dropdown',
                                options = [{'label': sortOrderAscending, 'value': sortOrderAscending}, {'label': sortOrderDescending, 'value': sortOrderDescending}],
                                value = sortOrderAscending , 
                                placeholder = "Order",
                        )
                    ], 
                    id = "students-sort-order-dropdown-div",
                    className = "c-container hidden", 
                    ),
                    width =  6
                )
            ]), className = "m-left-right-medium m-top_large"
        ),
     
        html.Div(id = 'Students-Container', className = "c-container p-bottom_15 m-left-right-medium hidden"),

        html.Div(html.A(children=[html.I(className="fas fa-download font-size_medium p_small"),"download data : Student",],
                           id = "students_details_download_link", className = "hidden", href = "", target = "_blank", download = 'student.csv'), id = "students_details_download_link-A", className = "m-left-right-medium hidden")
    ])
]


#----------------------------------------------------------------------------------------------------------------------
# Callback function to control the content of the whole students tab (based on user actions)
# params:   classes_n_clicks         (int)    - integer containing number of clicks on classes selection buttons
#           students_n_clicks        (int)    - integer containing number of clicks on students selection buttons
#           studentSelectedDate      (string) - string containing date dropdown value
#           studentGraphDirection    (string) - string containing sort order dropdown value
#           initialClassDate         (string) - string containing date dropdown className
#           initialClassDir          (string) - string containing sort order dropdown value
# returns:  list of classNames and childrens of various components
@app.callback([Output('students-learning-activity-selection-div', 'className'), Output('students-learning-activity-selection-div', 'children'),
               Output('students-select-a-class-heading', 'children'),           Output('students-button-select-other-la-div', 'className'),
               Output('students-select-a-student-heading-div', 'className'),    Output('students-selection-div', 'children'),
               Output('students-selection-div', 'className'),                   Output('students-select-a-student-heading', 'children'),
               Output('students-button-select-other-student-div', 'className'), Output('students-overview', 'className'),
               Output('students-date-dropdown-div', 'className'),               Output('students-sort-order-dropdown-div', 'className'),
               Output('students_details_download_link-A', 'className'),         Output('Students-Container', 'className'),

               Output('students-overview-container', 'children'),               Output('students-overview-container', 'className'),
               Output('students-progress-tracker-container', 'children'),       Output('students-progress-tracker-container', 'className'),
               Output("students-date-dropdown", "className"),                   Output("students-sort-order-dropdown", "className"),
               Output('Students-Container', 'children'),                        Output('students-date-dropdown', 'options'),
               Output('students_details_download_link', 'href'),                Output('students_details_download_link', 'className'),
               Output("students-game-interactions-header-div", "className"),
               
               Output("students-select-student-hr", "className"),               Output("students-overview-hr", "className"),
               Output("students-progress-tracker-hr", "className"),             Output("students-game-interactions-hr", "className")],

               Input({"button-type": "students-select-classes-button", "class-id": ALL}, "n_clicks"),
               Input({"button-type": "students-select-student-button", "student-id": ALL}, "n_clicks"),
               Input('students-date-dropdown', 'value'),
               Input('students-sort-order-dropdown', 'value'),
               State(component_id = 'students-date-dropdown', component_property = 'className'),
               State(component_id = 'students-sort-order-dropdown', component_property = 'className')
)
def ClassesAndStudentsSelectionButtonsControls(classes_n_clicks, students_n_clicks, studentSelectedDate, studentGraphDirection, initialClassDate, initialClassDir):

    global currentClassGlobal
    global currentStudentGlobal

    initialClassDateS = set()
    initialClassDirS = set()

    if not None is initialClassDate:
        initialClassDateS = set(initialClassDate.split(' ')) 
    if not None is initialClassDir:
        initialClassDirS = set(initialClassDir.split(' ')) 

    initialClassDateS.add('disabled') 
    initialClassDirS.add('disabled') 

    ctx = dash.callback_context
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']        # triggered_id can be: {"button-type":"students-select-classes-button","class-id":1}.n_clicks OR 'students-date-dropdown.value' OR 'students-sort-order-dropdown.value'

        if triggered_id == 'students-date-dropdown.value' or triggered_id == 'students-sort-order-dropdown.value':
            student_overview_graphs = []
            student_container_graphs = []
            student_date_dropdown_options = []

            if studentSelectedDate is None  or  studentSelectedDate == '':
                studentSelectedDate = ''

            if isStudentInClass(currentStudentGlobal, currentClassGlobal):
                student_overview_graphs = plotStudentOverview(currentStudentGlobal, currentClassGlobal)
                student_container_graphs = plotStudent(currentStudentGlobal, currentClassGlobal, format(studentSelectedDate), studentGraphDirection)
                student_progress_tracker_graphs = createProgressChildren(currentStudentGlobal, currentClassGlobal)
                dfStudentData = getStudentData(currentStudentGlobal, currentClassGlobal)

                if not (dfStudentData is None or dfStudentData.empty == True):
                    student_date_dropdown_options = [{'label': d, 'value': d} for d in dfStudentData['Start'].dt.date.unique()]
                csv_string = ""

                try:    
                    csv_string = util.get_download_link_data_uri(getStudentData(currentStudentGlobal, currentClassGlobal, format(studentSelectedDate)))
                except Exception as e:
                    subprocess.Popen(['echo', 'download - callback Exception 1'])
                    subprocess.Popen(['echo', str(e)]) 
                    subprocess.Popen(['echo', str(traceback.format_exc())])
                    print('groupStudents update_download_link__details_student ')
                    print(e)

            initialClassDateS.discard('disabled')
            initialClassDirS.discard('disabled')

            return ["m-top_small m-left-right-small choose-learning-activity-buttons hidden", dash.no_update,
                    dash.no_update, "m-top_small m-left-right-small choose-learning-activity-buttons",
                    "stick-on-top-of-page", [],
                    "m-top_small m-left-right-small choose-students-buttons hidden", getButtonLabel(currentStudentGlobal),
                    "m-top_small m-left-right-small choose-students-buttons", "c-container m-left-right-medium",
                    "c-container", "c-container",
                    "m-left-right-medium", "c-container p-bottom_15 m-left-right-medium",
                    student_overview_graphs, "c-container m-left-right-medium m-bottom_medium",
                    student_progress_tracker_graphs, "c-container m-left-right-medium m-bottom_medium",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS),
                    student_container_graphs, student_date_dropdown_options,
                    csv_string, "",
                    "c-container m-left-right-medium",
                    "hr_custom_style", "hr_custom_style",
                    "hr_custom_style", "hr_custom_style"]
        
        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        someClassesButtonWasPressed = False
        for clickinfo in classes_n_clicks:
            if clickinfo is not None:
                someClassesButtonWasPressed = True

        if triggered_id_dict["button-type"] == "students-select-classes-button" and triggered_id_dict["class-id"] >= 0 and someClassesButtonWasPressed:
            class_id = triggered_id_dict["class-id"]
            currentClassGlobal = class_id

            return ["m-top_small m-left-right-small choose-learning-activity-buttons hidden", createUserLAOptionsButtons(),
                    classes.getButtonLabel(class_id), "m-top_small m-left-right-small choose-learning-activity-buttons",
                    "stick-on-top-of-page", createStudentButtonsFromClassId(class_id),
                    "m-top_small m-left-right-small choose-students-buttons", "Select a Student",
                    "m-top_small m-left-right-small choose-students-buttons hidden", "c-container m-left-right-medium hidden",
                    "c-container hidden", "c-container hidden",
                    "m-left-right-medium hidden", "c-container p-bottom_15 m-left-right-medium hidden",
                    [], "c-container m-left-right-medium m-bottom_medium hidden",
                    [], "c-container m-left-right-medium m-bottom_medium hidden",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS),
                    [], [],
                    "", "disabled",
                    "c-container m-left-right-medium hidden",
                    "hr_custom_style", "hr_custom_style hidden",
                    "hr_custom_style hidden", "hr_custom_style hidden"]
        
        elif triggered_id_dict["button-type"] == "students-select-student-button" and triggered_id_dict["student-id"] >= 0:
            student_id = triggered_id_dict["student-id"]
            currentStudentGlobal = student_id

            student_overview_graphs = []
            student_container_graphs = []
            student_date_dropdown_options = []

            if studentSelectedDate is None  or  studentSelectedDate == '':
                studentSelectedDate = ''

            if isStudentInClass(student_id, currentClassGlobal):
                student_overview_graphs = plotStudentOverview(student_id, currentClassGlobal)
                student_container_graphs = plotStudent(student_id, currentClassGlobal, format(studentSelectedDate), studentGraphDirection)
                student_progress_tracker_graphs = createProgressChildren(currentStudentGlobal, currentClassGlobal)
                dfStudentData                   = getStudentData(student_id, currentClassGlobal)

                if not (dfStudentData is None or dfStudentData.empty == True):
                    student_date_dropdown_options = [{'label': d, 'value': d} for d  in dfStudentData['Start'].dt.date.unique()]
                csv_string = ""

                try:    
                    csv_string = util.get_download_link_data_uri(getStudentData(student_id, currentClassGlobal, format(studentSelectedDate)))
                except Exception as e:
                    subprocess.Popen(['echo', 'download - callback Exception 2'])
                    subprocess.Popen(['echo', str(e)]) 
                    subprocess.Popen(['echo', str(traceback.format_exc())])
                    print('groupStudents update_download_link__details_student ')
                    print(e)

            initialClassDateS.discard('disabled')
            initialClassDirS.discard('disabled')

            return ["m-top_small m-left-right-small choose-learning-activity-buttons hidden", dash.no_update,
                    dash.no_update, "m-top_small m-left-right-small choose-learning-activity-buttons",
                    "stick-on-top-of-page", [],
                    "m-top_small m-left-right-small choose-students-buttons hidden", getButtonLabel(student_id),
                    "m-top_small m-left-right-small choose-students-buttons", "c-container m-left-right-medium",
                    "c-container", "c-container",
                    "m-left-right-medium", "c-container p-bottom_15 m-left-right-medium",
                    student_overview_graphs, "c-container m-left-right-medium m-bottom_medium",
                    student_progress_tracker_graphs, "c-container m-left-right-medium m-bottom_medium",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS),
                    student_container_graphs, student_date_dropdown_options,
                    csv_string, "",
                    "c-container m-left-right-medium",
                    "hr_custom_style", "hr_custom_style",
                    "hr_custom_style", "hr_custom_style"]
        
        elif triggered_id_dict["button-type"] == "students-select-student-button" and triggered_id_dict["student-id"] == -1:
            currentStudentGlobal = -1

            return ["m-top_small m-left-right-small choose-learning-activity-buttons hidden", dash.no_update,
                    dash.no_update, "m-top_small m-left-right-small choose-learning-activity-buttons",
                    "stick-on-top-of-page", createStudentButtonsFromClassId(currentClassGlobal),
                    "m-top_small m-left-right-small choose-students-buttons", "Select a Student",
                    "m-top_small m-left-right-small choose-students-buttons hidden", "c-container m-left-right-medium hidden",
                    "c-container hidden", "c-container hidden",
                    "m-left-right-medium hidden", "c-container p-bottom_15 m-left-right-medium hidden",
                    [], "c-container m-left-right-medium m-bottom_medium hidden",
                    [], "c-container m-left-right-medium m-bottom_medium hidden",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS),
                    [], [],
                    "", "disabled",
                    "c-container m-left-right-medium hidden",
                    "hr_custom_style", "hr_custom_style hidden",
                    "hr_custom_style hidden", "hr_custom_style hidden"]

    currentClassGlobal = -1
    currentStudentGlobal = -1

    return ["m-top_small m-left-right-small choose-learning-activity-buttons", createUserLAOptionsButtons(),
            "Select a Class", "m-top_small m-left-right-small choose-learning-activity-buttons hidden",
            "stick-on-top-of-page hidden", [],
            "m-top_small m-left-right-small choose-students-buttons hidden", "Select a Student",
            "m-top_small m-left-right-small choose-students-buttons hidden", "c-container m-left-right-medium hidden",
            "c-container hidden", "c-container hidden",
            "m-left-right-medium hidden", "c-container p-bottom_15 m-left-right-medium hidden",
            [], "c-container m-left-right-medium m-bottom_medium hidden",
            [], "c-container m-left-right-medium m-bottom_medium hidden",
            ' '.join(initialClassDateS), ' '.join(initialClassDirS),
            [], [],
            "", "disabled",
            "c-container m-left-right-medium hidden",
            "hr_custom_style hidden", "hr_custom_style hidden",
            "hr_custom_style hidden", "hr_custom_style hidden"]