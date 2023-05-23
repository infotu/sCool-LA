# -*- coding: utf-8 -*-
"""
Created on   Aug  1 10:55:10 2020
Reworked on  Mar 14 10:25:00 2023

@authors: tilan, zangl
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
featureSessionDuration              = constants.featureSessionDuration

TaskTypePractice                    = constants.TaskTypePractice
TaskTypeTheory                      = constants.TaskTypeTheory



sortOrderDescending                 = constants.sortOrderDescending
sortOrderAscending                  = constants.sortOrderAscending

hasFeatures                         =  studentGrouped.hasFeatures

#--------------------------------- Const values END ----------------------------


#--------------------------------- DataBase get data START ---------------------------

dfStudentDetails                        = studentGrouped.dfStudentDetails

dfCourseDetails                         = studentGrouped.dfCourseDetails
dfSkillDetails                          = studentGrouped.dfSkillDetails
dfPracticeTaskDetails                   = studentGrouped.dfPracticeTaskDetails
dfTheoryTaskDetails                     = studentGrouped.dfTheoryTaskDetails
dfTaskDetails                           = studentGrouped.dfTaskDetails

#dfGroupedPractice                       = studentGrouped.dfGroupedPractice
dfGroupedOriginal                       = studentGrouped.dfGroupedOriginal
dfPlayerStrategyPractice                = studentGrouped.dfPlayerStrategyPractice  
dfGroupedPracticeTaskWise               = studentGrouped.dfGroupedPracticeTaskWise
dfGroupedPracticeDB                     = studentGrouped.dfGroupedPracticeDB
dfRuns                                  = studentGrouped.dfRuns


dfPlayerStrategyTheory                  = studentGrouped.dfPlayerStrategyTheory
dfGroupedPlayerStrategyTheory           = studentGrouped.dfGroupedPlayerStrategyTheory

#--------------------------------- DataBase get data END ---------------------------


#--------------------------- helper functions -----------------------    
getTaskWiseSuccessFail                  =  studentGrouped.getTaskWiseSuccessFail
getStudentsOfLearningActivity           =  studentGrouped.getStudentsOfLearningActivity


getPracticeDescription                  =  studentGrouped.getPracticeDescription
getTheoryDescription                    =  studentGrouped.getTheoryDescription



def convert_list_column_tostr_NL(val) :
    separator = ',<br>'
    return separator.join(val)



#--------------------------- helper functions  END -----------------------


#------------------------------------
def getStudentData(StudentId, schoolKey, selectedDate = '' ):
    
    print('getStudentData')
    
    studentData = pd.DataFrame()
    
    try :
        school                            = dfGroupedOriginal.get_group(schoolKey)
        studentData                       = school[school['StudentId'] == StudentId]
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
        schoolTheoryStudent = schoolTheory[schoolTheory['StudentId'] == StudentId]
        
        
        schoolTheoryStudent['Finish']       =   schoolTheoryStudent['CreatedAt']
        schoolTheoryStudent['Start']        =   schoolTheoryStudent['Finish'] - pd.to_timedelta(schoolTheoryStudent[featureSessionDuration], unit='s')
        schoolTheoryStudent                 =   schoolTheoryStudent.sort_values(by='Start')
        
        
        schoolTheoryStudent['Difference']   = (schoolTheoryStudent['Finish'] - schoolTheoryStudent['Start']).astype('timedelta64[s]')
        
        schoolTheoryStudent.loc[schoolTheoryStudent['Difference'] > schoolTheoryStudent[featureSessionDuration], 'Difference'] =  schoolTheoryStudent[
                schoolTheoryStudent['Difference'] > schoolTheoryStudent[featureSessionDuration] ][featureSessionDuration]        
        
        
        schoolTheoryStudent                 = schoolTheoryStudent.merge(right= dfTheoryTaskDetails[ ['TheoryTaskId', 'Title', 'Description' ] ]
                                                  , left_on='TheoryTaskId', right_on='TheoryTaskId'
                                                  , left_index=False, right_index=False
                                                  , how='inner')
        schoolTheoryStudent.rename(columns={'Description': 'TheoryTaskDescription'}, inplace=True)
        
        schoolTheoryStudent[featureDescription] = getTheoryDescription(schoolTheoryStudent, False)  
        schoolTheoryStudent[featureDescription] = '<b>Title</b>:' + schoolTheoryStudent['Title'].astype(str)  + '<br>'+ schoolTheoryStudent[featureDescription].astype(str) 
    
        schoolTheoryStudent['GroupBy']      = constants.TaskTypeTheory + '-' + schoolTheoryStudent['TheoryTaskId'].astype(str) 
        schoolTheoryStudent['Task']         = constants.TaskTypeTheory + '-' +  schoolTheoryStudent['TheoryTaskId'].astype(str)  
        schoolTheoryStudent['IndexCol']     = schoolTheoryStudent['Task'] + '-' +  schoolTheoryStudent['Result'].astype(str) 
        
        schoolTheoryStudent[constants.featureTaskType] = constants.TaskTypeTheory
        
        
        if schoolTheoryStudent is not None and schoolTheoryStudent.empty == False :
            studentData = pd.concat([studentData, schoolTheoryStudent], ignore_index=True)
    except Exception as e:
        subprocess.Popen(['echo', 'getStudentData second Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)
        
    
    if studentData is None         or     studentData.empty   :
        return studentData
    
    
    if     None is not selectedDate         and         not selectedDate == ''     and   util.is_valid_date(selectedDate) :
        studentDataGroupedDate      = studentData.groupby(  [studentData['Start'].dt.date] )
        studentData                 = studentDataGroupedDate.get_group(selectedDate)
    
    
    studentData['StartStr']         = '@' + studentData['Start'].dt.strftime('%Y-%m-%d %H:%M:%S') + '-' + studentData['IndexCol'].astype(str)
        
    return studentData


#Check if Student is in a Group
def isStudentInGroup(StudentId, groupId) :
    try:
        groupStudents = getStudentsOfLearningActivity(groupId)
        
        if  not StudentId in groupStudents:
            return False
        
        return True

    except Exception as e:
        subprocess.Popen(['echo', 'isStudentInGroup Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)


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


def plotStudentOverview(StudentId, groupId):
    
    graphs = []
    
    try:

    #    the student is not in the group
        if not isStudentInGroup(StudentId, groupId) :
            return graphs
        
        

        studentDataDf                     = getStudentData(StudentId, groupId)
        
        if studentDataDf is None or studentDataDf.empty == True :
            graphs.append(
                    util.getNoDataMsg()
            )
            return graphs

        
        studentDataDf.fillna(0, inplace=True)
        graphs = util.plotStudentOverview(studentDataDf , classes = "c-card-small" )
        
        
        
        plotRow = []
        
        
        
        groupOriginal                           = dfGroupedOriginal.get_group(groupId)
        
        groupOriginal['ConceptsUsed']           = groupOriginal['Code'].apply( studentGrouped.getAllNodeTypesUsefull )
        groupOriginal["ConceptsUsedDetails"]    = groupOriginal['ConceptsUsed'].replace(
                                                        constants.ProgramConceptsUsefull2UserNames, regex=True )
        
        
        studentWiseData                         = groupOriginal.groupby(['StudentId'], as_index=False).sum()
        studentDataDfPractice                   = studentWiseData[studentWiseData['StudentId'] == StudentId]
        
        
        
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
    #        plotRow.append( html.Div([  
    #                                    util.generateCardBase([html.I(className="fas fa-cubes m-right-small"),   'Tasks completed'], 
    #                                                           
    #                                                           ', '.join(studentDataDfSuccess['Task'].unique()), 
    #                                                           
    #                                                           classes = "c-card-small"),
    #                                ],
    #                                className="col-sm-8",
    #                        ))
            
        for feature2OKey in studentOverviewFeaturesDefault.keys():
            currentFeatureO = studentOverviewFeaturesDefault.get(feature2OKey)
            
            if constants.keyHasMeanStd in currentFeatureO.keys() and   currentFeatureO.get(constants.keyHasMeanStd):
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


                
            else :
                if feature2OKey in studentDataDfPractice.columns :
                    plotRow.append( html.Div([
                                                util.generateCardBase(
                                                        [   html.I(className=  currentFeatureO.get(constants.keyClassName) +  " m-right-small"), 
                                                            ((constants.feature2UserNamesDict.get(feature2OKey)) if feature2OKey in constants.feature2UserNamesDict.keys() else feature2OKey ) ], 
                                                        studentDataDfPractice[feature2OKey].sum() ,
                                                        classes = "c-card-small" )
                                            ],
                                            className="col-sm-4",
                                    ))
                elif feature2OKey in studentDataDf.columns :
                    plotRow.append( html.Div([
                                                util.generateCardBase(
                                                        [   html.I(className=  currentFeatureO.get(constants.keyClassName) +  " m-right-small"), 
                                                            ((constants.feature2UserNamesDict.get(feature2OKey)) if feature2OKey in constants.feature2UserNamesDict.keys() else feature2OKey ) ], 
                                                        studentDataDf[feature2OKey].sum() ,
                                                        classes = "c-card-small" )
                                            ],
                                            className="col-sm-4",
                                    ))
        
            
        if groupOriginal[groupOriginal['StudentId'] == StudentId] is not None  and groupOriginal[groupOriginal['StudentId'] == StudentId]['ConceptsUsedDetails'].shape[0] > 0 :        
            try :
                ConceptsUsedUnique                      = util.get_unique_list_feature_items(groupOriginal[groupOriginal['StudentId'] == StudentId], 'ConceptsUsedDetails')
                
                if     ConceptsUsedUnique is not None  :        
                    
                    ConceptsUsedUniqueUserReadable = set()
                    for conceptUsed in ConceptsUsedUnique:
                        ConceptsUsedUniqueUserReadable.add(  constants.ProgramConceptsUsefull2UserNames.get(conceptUsed) if 
                                                            conceptUsed in constants.ProgramConceptsUsefull2UserNames 
                                                            else 
                                                            conceptUsed  )
                    
                    plotRow.append( html.Div([
                                                util.generateCardBase(
                                                        [html.I(className="fas fa-code m-right-small"),   'Concepts Used', ], 
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
        
        if studentDataDfSuccess is not None and studentDataDfSuccess.empty is False  and 'Task' in studentDataDfSuccess.columns:        
    #        get tasks unique and courses
            
            print('skill studentdatadf')

            tasksCompleted = studentDataDfSuccess['Task'].unique()
            dfTasksCompleted = dfTaskDetails[dfTaskDetails['Task'].isin(tasksCompleted)]        
            
            for courseIdAttempt in dfTasksCompleted['CourseId'].unique():
                plotRow.append( getCourseProgressCard(courseIdAttempt, dfTasksCompleted )  )

        


        graphs.append(
                html.Div(children  = plotRow,                
                        className = "row")
        )

    
    except Exception as e:
        subprocess.Popen(['echo', 'plotStudentOverview big Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)



    return graphs


def getCourseProgressCard(courseId, dfTasksCompleted ):
    try:
        courseSkillIdAttempt = dfTasksCompleted[dfTasksCompleted['CourseId'] == courseId]['SkillId'].unique()
                
        skillsDiv = []
        for skillIdAttempt in courseSkillIdAttempt:
            skillTitle = dfTaskDetails[dfTaskDetails['SkillId'] == skillIdAttempt]['TitleSkill'].unique()
            
            dfSkillTaskCompleted = dfTasksCompleted[dfTasksCompleted['SkillId'] == skillIdAttempt]
            skillTaskCount = len(dfTaskDetails[dfTaskDetails['SkillId'] == skillIdAttempt][constants.featureTask].unique())
            progressSkill = math.ceil(  len(dfSkillTaskCompleted[constants.featureTask].unique()) * 100 / skillTaskCount  )
            
            
            tasksCompletedDetails =  []
            
            for taskId in dfSkillTaskCompleted[constants.featureTask].unique() :
                currentTask = dfTaskDetails[dfTaskDetails[constants.featureTask] == taskId]
                tasksCompletedDetails.append(html.Details(
                            children = [
                                    html.Summary(currentTask['Title']),
                                    html.P('Task:' + str(taskId) + 
                                        ';   Description: '  + currentTask['Description']),
                                ],
                                className = " c-details " + (   "type-practice"  if currentTask[constants.featureTaskType].iloc[0] == constants.TaskTypePractice else "type-theory"  )
                        ))
            
            skillsDiv.append(html.Div(children= [
                html.Div(
                        children = [
                                    dbc.Progress(str(progressSkill) + "%", value = progressSkill, className= " c-progress ",
                                                color = "success" if progressSkill == 100 else "primary", ), 
                                    html.Div( skillTitle + '-' +  str(skillIdAttempt) ),
                                    html.Div(
                                            children = [ 'Skill' ],
                                            className="card_value_label"
                                        ) ],
                        className=" card_value_details  col-2  "
                    ),
                html.Div(
                        children =[ html.Div(
                                            children = [ 'Tasks' ],
                                            className="card_value_label"
                                        ), 
    #                    ', '.join(dfSkillTaskCompleted['Task'].unique()),
                                    ] + tasksCompletedDetails,
                        className=" card_value_details  col-10  align-left "
                    ),
            ], className= "  row  "))
        
        courseTitle = dfTaskDetails[dfTaskDetails['CourseId'] == courseId]['TitleCourse'].unique()
        courseTasksCount = len(dfTaskDetails[dfTaskDetails['CourseId'] == courseId]['Task'].unique())
        courseTasksCompletedCount = len(dfTasksCompleted[dfTasksCompleted['CourseId'] == courseId]['Task'].unique())
        progressCourse = math.ceil(  courseTasksCompletedCount * 100 / courseTasksCount  ) 

        return html.Div( html.Div(
            [
                html.Div(
                    children = [
                                dbc.Progress(str(progressCourse) + "%", value = progressCourse, className= " c-progress ",
                                                color = "success" if progressCourse == 100 else "primary", ), 
                                html.Div( courseTitle + '-' +  str(courseId)  ),
                                html.Div(
                                        children = [ 'Course' ],
                                        className="card_value_label"
                                    ),  ],
                    className="card_value_title col-12"
                ),
                html.Div(children = skillsDiv,
                        className = "  col-12  "),
            ],
            className="c-card  c-card-small   row",
        ),
        className = "col-sm-12" )
    
    except Exception as e:
        subprocess.Popen(['echo', 'getCoursePProgressCard Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)


def plotStudentOverviewFeatures( StudentId, groupId, features2Overview ):
    if (None == groupId) :
        return html.Div()
    
    if (None == features2Overview) :
        features2Overview = [] 
        
    
    graphs = []
    plotRow = []    

    try:    
    #    the student is not in the group
        if not isStudentInGroup(StudentId, groupId) :
            return graphs
        
        

        studentDataDf                     = getStudentData(StudentId, groupId)
        
        if studentDataDf is None or studentDataDf.empty == True :
            graphs.append(
                    util.getNoDataMsg()
            )
            return graphs
        
        
    #    studentDataDf = studentDataDf.drop_duplicates(subset=['StudentId', 'Task'], keep='last')
        studentDataDf.fillna(0, inplace=True)
    
    
        try:
    #        For Mean and STD cards !!!
    #        studentDataDfMean           = studentDataDf.mean().round(decimals=2)
    #        studentDataDfStd            = studentDataDf.std().round(decimals=2)
    #        
    #        studentDataDfMean.fillna(0, inplace=True)
    #        studentDataDfStd.fillna(0, inplace=True)
        
            for feature2O in features2Overview :
                
                plotRow.append(
                    html.Div([
                            
                            util.generateCardBase( 
                                ((constants.feature2UserNamesDict.get(feature2O)) if feature2O in constants.feature2UserNamesDict.keys() else feature2O ) 
                                    , 
                                                '' + util.millify( studentDataDf[ feature2O ].sum().round(decimals=2) ), 
                                                classes = "c-card-small"
                                                )
                            
    #        For Mean and STD cards !!!
    #                       util.generateCardDetail( 
    #                               ((constants.feature2UserNamesDict.get(feature2O)) if feature2O in constants.feature2UserNamesDict.keys() else feature2O ) 
    #                                , 
    #                                            '' + util.millify( studentDataDf[ feature2O ].sum().round(decimals=2) ), 
    #                                            '' + str( studentDataDfMean[ feature2O ] ), 
    #                                            '' + str( studentDataDfStd[ feature2O ] ), 
    #                                            'total',
    #                                            'mean',
    #                                            'std',
    #                                            classes = "c-card-small"
    #                                            )
                        ],            
                        className="col-sm-4",
                    ))
        except Exception as e:
            subprocess.Popen(['echo', 'plotStudentOverviewFeatures Exception 1'])
            subprocess.Popen(['echo', str(e)]) 
            print(e)
            
        
        graphs.append(
                html.Div(children  = plotRow,                
                        className = "row")
        )    
    except Exception as e:
        subprocess.Popen(['echo', 'plotStudentOverviewFeatures Exception 2'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)


    return graphs
        

#Student Interaction with Game - TIMELINE
def plotStudent(StudentId, schoolKey, studentSelectedDate = '', studentGraphDirection = sortOrderDescending ):
    
    graphs = []
    
    try:    
    #    the student is not in the group
        if not isStudentInGroup(StudentId, schoolKey) :
            return graphs
        

        studentData                     = getStudentData(StudentId, schoolKey, studentSelectedDate)

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
        
        studentData.loc[studentData[constants.featureTaskType]  == constants.TaskTypePractice, 'color']      =   constants.colorPractice
        studentData.loc[studentData[constants.featureTaskType]  == constants.TaskTypeTheory, 'color']        =   constants.colorTheory
        studentData.loc[(studentData[constants.featureTaskType]  == constants.TaskTypePractice ) & 
                        (studentData['Result']  == 0), 'color']                                              =   constants.colorPracticeError
        studentData.loc[(studentData[constants.featureTaskType]  == constants.TaskTypeTheory ) & 
                        (studentData['Result']  == 0), 'color']                                              =   constants.colorTheoryError

        studentData['Task'] = studentData['IndexCol']
        studentData['Text'] = studentData['Difference'].astype(str) + 's for ' + studentData[constants.featureTaskType].astype(str) + ' Task : ' +  studentData['Title' ]  + ' Result : ' +  studentData['Result'].astype(str)

        colors  = {
                constants.TaskTypePractice  : constants.colorPractice,
                constants.TaskTypeTheory : constants.colorTheory,
                constants.TaskTypePractice + '-1' : constants.colorPractice,
                constants.TaskTypeTheory + '-1' : constants.colorTheory,
                constants.TaskTypePractice + '-0' : constants.colorPracticeError,
                constants.TaskTypeTheory + '-0' : constants.colorTheoryError,
        }
        
        studentData['IndexSuccFail'] = studentData[constants.featureTaskType] + '-' +  studentData['Result'].astype(str)
        
        
        graphHeightRows =  ( studentData.shape[0] * 40 )
        graphHeightRows = graphHeightRows if (graphHeightRows > (constants.graphHeightMin + 100) ) else (constants.graphHeightMin + 100)
        
        
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
                                            height          =   graphHeightRows , 
                                            title_text      = 'Details of student\'s game interactions'
                                                , yaxis = dict(
                                                    title = 'Time',
                                                    titlefont_size = 16,
                                                    tickfont_size = 14,
                                                ), xaxis = dict(
                                                    title = 'Duration (s)',
                                                    titlefont_size = 16,
                                                    tickfont_size = 14,
                                )                   
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
        
        
    #    gantt chart for timeline 
    #    if studentData is not None and studentData.empty == False :    
        studentData['Task'] = studentData['GroupBy']
        
        graphHeightRows =  ( len(studentData['Task'].unique()) * 40 )
        graphHeightRows = graphHeightRows if (graphHeightRows > (constants.graphHeightMin + 100) ) else (constants.graphHeightMin + 100)

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
                        figure= fig
                        
                        , config  =  dict (locale   =  constants.languageLocal   ) 
                    )
        )

# **** IMPORTANT - ff.create_gantt is deprecated -> moved to px.timeline 
#    studentData['StartStr'] = studentData['Start'].dt.strftime('%Y-%m-%d %H:%M:%S')
#    studentData['FinishStr'] = studentData['Finish'].dt.strftime('%Y-%m-%d %H:%M:%S')
#    
#    fig = px.timeline(studentData, x_start="StartStr", x_end="FinishStr", y="Task"
#                      , color = constants.featureTaskType,   
#                        hover_data    = ['Description', 'Start', 'StartStr', 'Finish', 'FinishStr'] ,                   
#                        height =   graphHeightRows 
#    )
#    graphs.append(
#            dcc.Graph(
#                figure= fig
#        ))
    
    
    except Exception as e:
        subprocess.Popen(['echo', 'plotStudent Exception'])
        subprocess.Popen(['echo', str(e)]) 
        print(e)

    
    return graphs


featuresToExclude = [
             'PracticeTaskId',
             'EnrolledId', 
             'SkillId', 
             'CourseId', 
             'StudentId', 
             'LearningActivity_LearningActivityId',  
             'Difficulty', 
             'PracticeStatisticsId', 
             'TheoryStatisticsId',  
             'EnrolledId', 'SkillId', 'TheoryTaskId', 
             'LearningActivityId', 'CourseId', 'studentAttemptsTotal'
             

             # because complicated to explain
             ,'runsHasVariablesNamedCount' , 'runsHasVariablesCount'
             ,'hasVariablesNamed', 'hasVariables', 'hasVariable'
]


def getFeatureOptions():
    
    numericFeaturesPracticeS = set(util.getNumericFeatures(dfGroupedOriginal.median()))
    numericFeaturesTheoryS = set(util.getNumericFeatures(dfPlayerStrategyTheory))
    
    mergedList = numericFeaturesPracticeS.union(numericFeaturesTheoryS)
    
    newFeatureOptionsList = list(set(mergedList) - set(featuresToExclude))
   
    return util.BuildOptionsFeatures( newFeatureOptionsList )
    

def createUserLAOptionsButtons():
    buttons_list = []

    user_LA_options = classes.getUserLAOptions()
    for option in user_LA_options:
        button_label = option["label"]
        button_value = int(option["value"])
        buttons_list.append(html.Button(button_label, id = {"button-type": "students-select-classes-button", "class-id": button_value}))

    return buttons_list


def getButtonLabel(button_id):
    dfstudents = dfStudentDetails[dfStudentDetails[constants.STUDENT_ID_FEATURE].isin([button_id])][['StudentId', 'Name']].drop_duplicates(subset=['StudentId'], keep='first')

    for index, row in dfstudents.iterrows():
        student_id = row['StudentId']
        student_name = row['Name']

        if(student_id == button_id):
            return student_name
        
    return "something went wrong with button label function"


def createStudentButtonsFromClassId(class_id):

    student_buttons_list = []
    students_id_list = getStudentsOfLearningActivity(class_id)
    dfstudents = dfStudentDetails[dfStudentDetails[constants.STUDENT_ID_FEATURE].isin(students_id_list)][['StudentId', 'Name']].drop_duplicates(subset=['StudentId'], keep='first')

    for index, row in dfstudents.iterrows():
        student_id = row['StudentId']
        student_name = row['Name']
        student_buttons_list.append(html.Button(student_name, id = {"button-type": "students-select-student-button", "student-id": student_id}))

    return student_buttons_list


current_class = -1
current_student = -1


#-----------------------------------------
# Layout-------------------------
#-------------------------------------------

layout = [
    html.Div([

        html.H1('Select a Class', id = 'students-select-a-class-heading', style = {'text-align': 'center', 'margin-top': '10px'}),

        html.Div(createUserLAOptionsButtons(), className = 'choose-learning-activity-buttons', id = 'students-learning-activity-selection-div'),

        html.Div(html.Button('Select other Class', id = {"button-type": "students-select-classes-button", "class-id": -1}), className = 'choose-learning-activity-buttons hidden', id = "students-button-select-other-la-div"),

        html.H1('Select a Student', id = 'students-select-a-student-heading', style = {'text-align': 'center', 'margin-top': '10px'}, className = 'hidden'),

        html.Div(children = [], className = 'choose-students-buttons hidden', id = 'students-selection-div'),

        html.Div(html.Button('Select other Student', id = {"button-type": "students-select-student-button", "student-id": -1}), className = 'choose-students-buttons hidden', id = "students-button-select-other-student-div"),

        dbc.Row([
            dbc.Col(html.Div(id = 'students-information', children = [html.H3('Student Information')], className = "c-container hidden"))
        ]),

        dbc.Row([
            dbc.Col(html.Div(id = 'students-overview-container', className = "c-container m_small hidden"))
        ]),
             
        dbc.Row([
            dbc.Col(
                html.Div([
                    dcc.Dropdown(id = 'students-feature-overview-dropdown', placeholder = "Select Overview Features", options = [], multi = True)
                    ],
                    id = 'students-feature-overview-dropdown-div',
                    className = "hidden"
                )
                , width = 12
            ),
        ]),
                
        dbc.Row([
            dbc.Col(html.Div(id = 'students-features-overview-container', className = "c-container m_small hidden"))
        ]),
             
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
                )
                , width  =  6
            )
        ]),
                    
        dbc.Row([
            dbc.Col(html.A(children=[html.I(className="fas fa-download font-size_medium p_small"),"download data : Student",],
                           id = "students_details_download_link", className = "hidden", href = "", target = "_blank", download = 'student.csv'), id = "students_details_download_link-A", className = "hidden")
        ]),    
     
        dbc.Row([
            dbc.Col(html.Div(id = 'Students-Container', className = "c-container p-bottom_15 hidden"))
        ])
    ], style = {'margin': '30px'})
]


#-----------------------------------------
# callback functions---------------------
#        ---------------------------------
#----------------------------------------------------------------------------------------------------------------------
@app.callback([Output('students-learning-activity-selection-div', 'className'), Output('students-select-a-class-heading', 'children'),
               Output('students-button-select-other-la-div', 'className'),      Output('students-select-a-student-heading', 'className'),
               Output('students-selection-div', 'children'),                    Output('students-selection-div', 'className'),
               Output('students-select-a-student-heading', 'children'),         Output('students-button-select-other-student-div', 'className'),
               Output('students-information', 'className'),                     Output('students-feature-overview-dropdown', 'options'),
               Output('students-feature-overview-dropdown-div', 'className'),   Output('students-features-overview-container', 'className'),
               Output('students-date-dropdown-div', 'className'),               Output('students-sort-order-dropdown-div', 'className'),
               Output('students_details_download_link-A', 'className'),         Output('Students-Container', 'className'),

               Output('students-overview-container', 'children'),               Output('students-overview-container', 'className'),
               Output("students-date-dropdown", "className"),                   Output("students-sort-order-dropdown", "className"),
               Output("students-feature-overview-dropdown", "className"),
               Output('Students-Container', 'children'),                        Output('students-date-dropdown', 'options'),
               Output('students_details_download_link', 'href'),                Output('students_details_download_link', 'className')],

               Input({"button-type": "students-select-classes-button", "class-id": ALL}, "n_clicks"),
               Input({"button-type": "students-select-student-button", "student-id": ALL}, "n_clicks"),
               Input('students-date-dropdown', 'value'),
               Input('students-sort-order-dropdown', 'value'),
               State(component_id = 'students-date-dropdown', component_property = 'className'),
               State(component_id = 'students-sort-order-dropdown', component_property = 'className'),
               State(component_id = 'students-feature-overview-dropdown', component_property = 'className')
)
def ClassesAndStudentsSelectionButtonsControls(classes_n_clicks, students_n_clicks, studentSelectedDate, studentGraphDirection, initialClassDate, initialClassDir, initialClassFeatures):

    global current_class
    global current_student
    initialClassDateS = set()
    initialClassDirS = set()
    initialClassFeaturesS = set()

    if not None is initialClassDate:
        initialClassDateS = set(initialClassDate.split(' ')) 
    if not None is initialClassDir:
        initialClassDirS = set(initialClassDir.split(' ')) 
    if not None is initialClassFeatures:
        initialClassFeaturesS = set(initialClassFeatures.split(' '))

    initialClassDateS.add('disabled') 
    initialClassDirS.add('disabled') 
    initialClassFeaturesS.add('disabled')

    ctx = dash.callback_context
    subprocess.Popen(['echo', 'callback - initial trigger ' + str(ctx.triggered[0]['prop_id'])])
    if ctx.triggered:
        triggered_id = ctx.triggered[0]['prop_id']        # triggered_id can be: {"button-type":"students-select-classes-button","class-id":1}.n_clicks OR 'students-date-dropdown.value' OR 'students-sort-order-dropdown.value'

        subprocess.Popen(['echo', 'callback - ' + 'ctx triggered'])
        subprocess.Popen(['echo', 'callback - ' + str(triggered_id)])

        if triggered_id == 'students-date-dropdown.value' or triggered_id == 'students-sort-order-dropdown.value':
            student_overview_graphs = []
            student_container_graphs = []
            student_date_dropdown_options = []
            if studentSelectedDate is None  or  studentSelectedDate == '':
                studentSelectedDate = ''
            if isStudentInGroup(current_student, current_class):
                student_overview_graphs = plotStudentOverview(current_student, current_class)
                student_container_graphs = plotStudent(current_student, current_class, format(studentSelectedDate), studentGraphDirection)
                dfStudentData = getStudentData(current_student, current_class)
                if not (dfStudentData is None or dfStudentData.empty == True):
                    student_date_dropdown_options = [{'label': d, 'value': d} for d in dfStudentData['Start'].dt.date.unique()]

                csv_string = ""
                try:    
                    csv_string = util.get_download_link_data_uri(getStudentData(student_id, current_class, format(studentSelectedDate)))
                except Exception as e:
                    subprocess.Popen(['echo', 'download - callback Exception'])
                    subprocess.Popen(['echo', str(e)]) 
                    print('groupStudents update_download_link__details_student ')
                    print(e)

            initialClassDateS.discard('disabled')
            initialClassDirS.discard('disabled')
            initialClassFeaturesS.discard('disabled')

            return ["choose-learning-activity-buttons hidden", dash.no_update,
                    "choose-learning-activity-buttons", "",
                    [], "choose-students-buttons hidden",
                    getButtonLabel(current_student), "choose-students-buttons", 
                    "c-container", getFeatureOptions(),
                    "", "c-container m_small",
                    "c-container", "c-container",
                    "", "c-container p-bottom_15",
                    student_overview_graphs, "c-container m_small",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS), ' '.join(initialClassFeaturesS),
                    student_container_graphs, student_date_dropdown_options,
                    csv_string, ""]
        
        # extract dictionary string and convert it to real dictionary
        start_index = triggered_id.index('{')
        end_index = triggered_id.rindex('}') + 1
        dictionary_str = triggered_id[start_index:end_index]
        triggered_id_dict = json.loads(dictionary_str)

        if triggered_id_dict["button-type"] == "students-select-classes-button" and triggered_id_dict["class-id"] >= 0:
            subprocess.Popen(['echo', 'callback - ' + str(triggered_id_dict["button-type"])])
            subprocess.Popen(['echo', 'callback - return 1'])
            class_id = triggered_id_dict["class-id"]
            current_class = class_id

            return ["choose-learning-activity-buttons hidden", classes.getButtonLabel(class_id),
                    "choose-learning-activity-buttons", "",
                    createStudentButtonsFromClassId(class_id), "choose-students-buttons",
                    "Select a Student", "choose-students-buttons hidden", 
                    "c-container hidden", [],
                    "hidden", "c-container m_small hidden",
                    "c-container hidden", "c-container hidden",
                    "hidden", "c-container p-bottom_15 hidden",
                    [], "c-container m_small hidden",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS), ' '.join(initialClassFeaturesS),
                    [], [],
                    "", "disabled"]
        
        elif triggered_id_dict["button-type"] == "students-select-student-button" and triggered_id_dict["student-id"] >= 0:
            subprocess.Popen(['echo', 'callback - ' + str(triggered_id_dict["button-type"])])
            subprocess.Popen(['echo', 'callback - return 2'])
            student_id = triggered_id_dict["student-id"]
            current_student = student_id

            student_overview_graphs = []
            student_container_graphs = []
            student_date_dropdown_options = []
            if studentSelectedDate is None  or  studentSelectedDate == '':
                studentSelectedDate = ''
            if isStudentInGroup(student_id, current_class):
                student_overview_graphs = plotStudentOverview(student_id, current_class)
                student_container_graphs = plotStudent(student_id, current_class, format(studentSelectedDate), studentGraphDirection)
                dfStudentData                     = getStudentData(student_id, current_class)
                if not (dfStudentData is None or dfStudentData.empty == True):
                    student_date_dropdown_options = [{'label': d, 'value': d} for d  in dfStudentData['Start'].dt.date.unique()]
                
                csv_string = ""
                try:    
                    csv_string = util.get_download_link_data_uri(getStudentData(student_id, current_class, format(studentSelectedDate)))
                except Exception as e:
                    subprocess.Popen(['echo', 'download - callback Exception'])
                    subprocess.Popen(['echo', str(e)]) 
                    print('groupStudents update_download_link__details_student ')
                    print(e)

            initialClassDateS.discard('disabled')
            initialClassDirS.discard('disabled')
            initialClassFeaturesS.discard('disabled')

            return ["choose-learning-activity-buttons hidden", dash.no_update,
                    "choose-learning-activity-buttons", "",
                    [], "choose-students-buttons hidden",
                    getButtonLabel(student_id), "choose-students-buttons", 
                    "c-container", getFeatureOptions(),
                    "", "c-container m_small",
                    "c-container", "c-container",
                    "", "c-container p-bottom_15",
                    student_overview_graphs, "c-container m_small",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS), ' '.join(initialClassFeaturesS),
                    student_container_graphs, student_date_dropdown_options,
                    csv_string, ""]
        
        elif triggered_id_dict["button-type"] == "students-select-student-button" and triggered_id_dict["student-id"] == -1:
            subprocess.Popen(['echo', 'callback - ' + str(triggered_id_dict["button-type"])])
            subprocess.Popen(['echo', 'callback - return 3'])
            current_student = -1

            return ["choose-learning-activity-buttons hidden", dash.no_update,
                    "choose-learning-activity-buttons", "",
                    createStudentButtonsFromClassId(current_class), "choose-students-buttons",
                    "Select a Student", "choose-students-buttons hidden", 
                    "c-container hidden", [],
                    "hidden", "c-container m_small hidden",
                    "c-container hidden", "c-container hidden",
                    "hidden", "c-container p-bottom_15 hidden",
                    [], "c-container m_small hidden",
                    ' '.join(initialClassDateS), ' '.join(initialClassDirS), ' '.join(initialClassFeaturesS),
                    [], [],
                    "", "disabled"]

    current_class = -1
    current_student = -1
    subprocess.Popen(['echo', 'callback - return 4'])
    return ["choose-learning-activity-buttons", "Select a Class",
            "choose-learning-activity-buttons hidden", "hidden",
            [], "choose-students-buttons hidden",
            "Select a Student", "choose-students-buttons hidden", 
            "c-container hidden", [],
            "hidden", "c-container m_small hidden",
            "c-container hidden", "c-container hidden",
            "hidden", "c-container p-bottom_15 hidden",
            [], "c-container m_small hidden",
            ' '.join(initialClassDateS), ' '.join(initialClassDirS), ' '.join(initialClassFeaturesS),
            [], [],
            "", "disabled"]


# Update bar plot
#----------------------------------------------------------------------------------------------------------------------
@app.callback(
    Output("students-features-overview-container", "children"),
    [Input("students-feature-overview-dropdown", "value")]
)
def onSelectFeatureOverview(selectedFeatures):

    global current_class
    global current_student
    graphs = []

    if  not util.isValidValueId(current_class) or  not util.isValidValueId(current_student):
        return html.Div(graphs)
 
    graphs = plotStudentOverviewFeatures(current_student, current_class, selectedFeatures)    
    
    return  html.Div(graphs)