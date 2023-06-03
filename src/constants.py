# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 22:42:22 2020

@author: tilan
"""


#----------------------------------------------------------------
#-- Database Connection
#---------------------------------------------------------------

'''
Driver = 'MySQL ODBC 8.0 Driver'
Server = 'codislabgraz.org'
DatabaseName = 'thesesweb'
Uid = 'scool'
Pwd = '6R45gynw429wCIXO'
Port = '3306'
'''

Driver = 'MySQL ODBC 8.0 Driver'
Server = '127.0.0.1'
DatabaseName = 'scoolDev'
Uid = 'root'
Pwd = 'sturm321graz.'
Port = '3306'


#----------------------------------------------------------------
#-- app settings
#---------------------------------------------------------------


loginRedirect               = "/Welcome"



languageLocal               = "en"



#----------------------------------------------------------------
#-- main key value
#---------------------------------------------------------------

keyLabel                    = 'label'
keyHref                     = 'href'
keySubmenu                  = 'submenu'
keyValue                    = 'value'
keyScrollTo                 = 'scrollTo'
keyClassName                = 'className'
keyHasMeanStd               = 'hasMeanStd'
keyIsAxisEnabled            = 'isAxisEnabled'
keyIsFeature3Enabled        = 'isFeature3Enabled'
keyIsDistributionEnabled    = 'isDistributionEnabled'
keyIsMultiFeatureEnabled    = 'isMultiFeatureEnabled'
keyIsDccGraph               = 'isDccGraph'
keyColor                    = 'color'
keyBackgroundColor          = 'backgroundColor'
keyExpress                  = 'express'
keyLight                    = 'light'
keyIsDefault                = 'isDefault'
keyOnlyForAdmin             = 'onlyForAdmin'




#--------------------------------------------------------------------------------
#-------------------------------- STYLES START -----------------------------------
# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "marginLeft": "18rem",
    "marginRight": "2rem",
    "padding": "2rem 1rem",
}

THEME           = "theme-app"

THEME_COLOR_MAP = {
	"theme-app": {
        keyLabel : 'app', 
        keyBackgroundColor  : '#3aaab2',
		keyColor : 'white',
		keyLight 	: "rgb(232 252 253)",
        keyClassName : 'theme-color-app',
		keyExpress	: {
			"plot_bgcolor"      : 'rgb(243, 243, 243)',
			"paper_bgcolor"     : 'rgb(243, 243, 243)',
		},
        keyIsDefault : True
	},
	"theme-teal": {
        keyLabel : 'teal', 
        keyBackgroundColor  : '#009688',
		keyColor : 'white',
		keyLight 	: "#e9fffd",
        keyClassName : 'theme-color-teal',
		keyExpress	: {
			"plot_bgcolor"      : '#e9fffd',
			"paper_bgcolor"     : '#e9fffd',
		},
        keyIsDefault : False
	},
	"theme-pink": {
        keyLabel : 'pink', 
        keyBackgroundColor  : '#e91e63',
		keyColor : 'white',
		keyLight 	: "#fbd2e0",
        keyClassName : 'theme-color-pink',
		keyExpress	: {
			"plot_bgcolor"      : '#fef2f6',
			"paper_bgcolor"     : '#fef2f6',
		},
        keyIsDefault : False
	},
	"theme-dark": {
        keyLabel : 'dark', 
        keyBackgroundColor  : 'black',
		keyColor : 'white',
		keyLight 	: "grey",
        keyClassName : 'theme-color-dark',
		keyExpress	: {
			"plot_bgcolor"      : 'rgb(243, 243, 243)',
			"paper_bgcolor"     : 'rgb(243, 243, 243)',
		},
        keyIsDefault : False
	}
}  

THEME_COLOR = 'black'
THEME_BACKGROUND_COLOR = 'white'
THEME_COLOR_LIGHT  = 'white'
THEME_EXPRESS_LAYOUT = THEME_COLOR_MAP.get(THEME).get(keyExpress)


def refreshThemeColor():
    if THEME in THEME_COLOR_MAP.keys():    
        THEME_COLOR                     = THEME_COLOR_MAP.get(THEME).get(keyColor)
        THEME_BACKGROUND_COLOR          = THEME_COLOR_MAP.get(THEME).get(keyBackgroundColor)
        THEME_COLOR_LIGHT               = THEME_COLOR_MAP.get(THEME).get(keyLight)
        THEME_EXPRESS_LAYOUT            = THEME_COLOR_MAP.get(THEME).get(keyExpress)
    return THEME_COLOR, THEME_BACKGROUND_COLOR, THEME_COLOR_LIGHT, THEME_EXPRESS_LAYOUT

THEME_COLOR, THEME_BACKGROUND_COLOR, THEME_COLOR_LIGHT, THEME_EXPRESS_LAYOUT = refreshThemeColor()


ERROR_COLOR = "#FF4136"
SUCCESS_COLOR = "#4caf50"

THEME_MARKER = dict(size = 16
                                            , showscale    = False
                                            ,  line = dict(width=1,
                                                        color='DarkSlateGrey'))


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


THEME_TABLE_HEADER_STYLE = {
    'backgroundColor'   : 'rgb(230, 230, 230)',
    'fontWeight'        : 'bold'
}
THEME_TABLE_ODDROW_COLOR_STYLE = 'rgb(248, 248, 248)'
#--------------------------------------------------------------------------------
#-------------------------------- STYLES END -----------------------------------
#---------------------------------------------------------------------------------





#--------------------------------------------------------------------------------
#------------------- feature related START -----------------------------------------------
#--------------------------------------------------------------------------------

GROUPBY_FEATURE         =  'LearningActivityId'
COUNT_STUDENT_FEATURE   =  'CountOfStudents'
STUDENT_ID_FEATURE      =  'StudentId'
TASK_TYPE_FEATURE       =  'TaskType'



featureAdderGroup = "LAId-"
featureAdderAvg = ' Avg.'

featuresCombined = [GROUPBY_FEATURE,'SessionDuration', 'Points', 'Attempts' ]
featuresOverview = featuresCombined + ['itemsCollectedCount' ]
featuresOverviewAvg = [GROUPBY_FEATURE, 'SessionDuration'+ featureAdderAvg, 'Points'+ featureAdderAvg
                       , 'Attempts'+ featureAdderAvg, 'itemsCollectedCount'+ featureAdderAvg ]

featuresOverviewAvgNames = {
        'SessionDuration': 'SessionDuration'+ featureAdderAvg,
                                      'Points': 'Points' + featureAdderAvg,
                                      'Attempts' : 'Attempts' + featureAdderAvg,
                                      'itemsCollectedCount' : 'itemsCollectedCount' + featureAdderAvg
  }




countStudentCompletingTaskFeature   = "Number of Students"
countTaskCompletedByStudentFeature  = "Number of Tasks Completed"
featureSessionDuration              = "SessionDuration"
featurePracticeTaskDesc             = "PracticeTaskDesc"
featureTheoryTaskDesc               = "TheoryTaskDesc"
featureTaskDesc                     = "TaskDesc"
featureTaskType                     = TASK_TYPE_FEATURE
featureDescription                  = "Description"
featureConceptsUsed                 = "Concept Used"
featureConceptsUsedDetails          = "ConceptsUsedDetails"
featureConceptsUsedDetailsStr       = "ConceptsUsedDetailsStr"
featureItemsCollectedCount          = "itemsCollectedCount"
featureSolution                     = "Solution"
featurePlayerShootEndEnemyHitCount  = "playerShootEndEnemyHitCount"
featureRobotCollisionsBoxCount      = "robotCollisionsBoxCount"
featureLineOfCodeCount              = "lineOfCodeCount"
featurePoints                       = "Points"
featureCollectedCoins               = "CollectedCoins"

TaskTypePractice                    = "Practice"
TaskTypeTheory                      = "Theory"
TypeCourse                          = "Course"
featureCourse                       = "Course"
TypeTask                            = "Task"
featureTask                         = "Task"
featureTaskId                       = "TaskId"
TypeSkill                           = "Skill"
featureSkill                        = "Skill"
TypeStudent                         = "Student"
featureStudent                      = "Student"
TypeGroup                           = "LA"
featureGroup                        = "LA"



codeConceptNameDict = {
    "hasLoop" : "Used Loop"
	,"hasNestedLoop" : "Used Nested Loop"
	,"hasCondition" : "Used Condition"
	,"hasVariable" : "Used Variable"
	,"hasAsyncOrAwait" : "Used Async"
	,"hasFunctionClass" : "Used Function or Class"
	,"hasStatements" : "Used Statements (e.g. Assignment, Assert, Delete)"
	,"hasExpressionsArithematic" : "Used Arithematic Operators (e.g. Add, Div, Mult)"
	,"hasExpressionsBool" : "Used Boolean (And, Or)"
	,"hasExpressionsLogical" : "Used Logical Operators (e.g. Eq, Lt, Gt)"
	,"hasExpressionsUnary" : "Used Unary Operators"
	,"hasExpressionsBitwise" : "Used Bitwise Operators"
	,"hasExpressionsDict" : "Used Dictionary Or Map (Dict)"
	,"hasExpressionsDataStructure" : "Used Data Structure (e.g. Dict, List, Set)"
    ,"hasExpressionsFunctionCall" : "Used function call (e.g. call('friend'))"
	,"hasControlFlowConditional" : "Used Conditional Flows (e.g. If, continue, break)"
	,"hasControlFlowTryException" : "Used Try Exception"
	,"hasConstantsUseful" : "Used Constants (e.g. 3 or 'a' or None)"
	,"hasExpressionsKeyword" : "Used Keyword (e.g. and, while, None)"
}

codeConceptDescriptionDict = {
    "hasLoop" : "Loops allow the programmer to repeat a block of code multiple times. (e.g. for, while)"
	,"hasNestedLoop" : "Nested Loops are simple loops that are defined inside of another loop. (e.g. for, while)"
	,"hasCondition" : "Conditions are used to make decisions during runtime of the program. (e.g. if)"
	,"hasVariable" : "Variables are named storage locations that are holding values."
	,"hasAsyncOrAwait" : "Used to work with asynchronous operations. "
	,"hasFunctionClass" : "Functions are reusable blocks of code. Classes are blueprints that define the structure of objects."
	,"hasStatements" : "Statements are complete instructions or commands performing specific actions."
	,"hasExpressionsArithematic" : "Arithmetic Operators are used to perform mathematical operations. (e.g. <, >, ==, !=)"
	,"hasExpressionsBool" : "Boolean Operators are used to perform logical operations. (e.g. or, and)"
	,"hasExpressionsLogical" : "Logical Operators are used to perform logical operations. (e.g. &&, ||, !)"
	,"hasExpressionsUnary" : "Unary Operators perform a single action on a single operand or variable. (e.g. ++, --)"
	,"hasExpressionsBitwise" : "Bitwise Operators are used to manipulate bits of binary values. (e.g. &, |, ^, ~)"
	,"hasExpressionsDict" : "A dictionary or map is a data structure that stores key-value pairs."
	,"hasExpressionsDataStructure" : "Dictionary, List or Set was used."
    ,"hasExpressionsFunctionCall" : "Function Calls are expressions that execute a function."
	,"hasControlFlowConditional" : "Control Flow Conditions allow you to control which parts of the code are executed. (if, switch, continue, break)"
	,"hasControlFlowTryException" : "Try-Except blocks are used to handle errors that may occur during execution of code."
	,"hasConstantsUseful" : "Constants are values remaining unchanged during the execution of a program. (e.g. 3 or 'a' or None)"
	,"hasExpressionsKeyword" : "Keywords are reserved words with special meaning or purpose within a programming language. (e.g. and, while, None)"
}


#User understandable Column names
feature2UserNamesDict = {
		"Attempts" : "Attempts"
		,"PracticeTaskId" : "Practice Task Id"
		,featurePoints : "Points"
		,featureConceptsUsed : 'Concept Used'
		,"studentTaskCount" : "Number of Tasks performed"
		,"studentAttemptsTotal" : "Total Attempts"
		,featureRobotCollisionsBoxCount : "Number of Robot Collisions"
		,featureCollectedCoins :  "Coins Collected"
		,"coinCollectedCount" : "Coins Collected"
		
        ,"keyboardKeyPressedCount" : "Number of Keyboard Key Presses"
		,"deletedCodesCount" : "Number of Deleted Codes"
        ,"tabsSwitchedOutputCount" : "Number of Tab Switches to Output"
		,"tabsSwitchedCodeCount" : "Number of Tab Switches to Code"
		,"tabsSwitchedDescriptionCount" : "Number of Switches to Read Description"
		,"tabsSwitchedCount" : "Number of Tab Switches"
		,"draggedCount" : "Number of Drags"
		
        ,"NumberOfBoxes" : "Number of Boxes"
		,"NumberOfCoins" : "Number of Coins"
		,"NumberOfHidden" : "Number of hidden items"
		,featureLineOfCodeCount : "Count of Lines of Code" 
        ,featureConceptsUsedDetailsStr : "Concepts used details"
        ,"StudentId" : "StudentId"
        , "Result" : "Result"
        
		,"runsErrorAttribiteCount" : "Number of Attribute Errors in Code Runs"
		,"runsErrorTypeCount" : "Number of Type Errors in Code Runs"
		,"runsErrorNameCount" : "Number of Name Errors in Code Runs"
		,"runsErrorSyntaxCount" : "Number of Syntax Errors in Code Runs"
        
		,"runsSuccessCount" : "Number of Successful Code Runs"
		,"runsErrorCount" : "Number of Code Errors in Code Runs"
		,"runsCount" : "Number of Code Executions in Code Runs"
        
		,"runsLineOfCodeCountAvg" : "Average Line Count of Code in all Code Runs"  
		,"runsHasVariableCount" : "Number of Used Variables in all Code Runs"
		,"runsHasConditionCount" : "Number of Used Conditions in all Code Runs"
		,"runsHasNestedLoopCount" : "Number of Used Nested Loops in all Code Runs"
		,"runsHasLoopCount" : "Number of Used Loops in all Code Runs"
		,"runsHasExpressionsCount" : "Number of Used Expressions in all Code Runs"
		,"runsHasAsyncOrAwaitCount" : "Number of Uses of 'async' in all Code Runs"
		,"runsHasFunctionClassCount" : "Number of Used Functions or Classes in all Code Runs"
		,"runsHasControlFlowCount" : "Number of Used Control Flows in all Code"
		,"runsHasImportsCount" : "Number of Used Imports in all Code Runs"
		,"runsHasStatementsCount" : "Number of Used Statements (e.g., Assignment, Assert, Delete) in all Code Runs"
		,"runsHasComprehensionsCount" : "Number of Used Comprehensions (ListComp, SetComp, GeneratorExp, DictComp) in all Code Runs"
		,"runsHasSubscriptingCount" : "Number of Used Subscriptions in all Code Runs"
		,"runsHasExpressionsArithematicCount" : "Number of Used Arithmetic Operators in all Code Runs"
		,"runsHasExpressionsBoolCount" : "Number of Used Boolean Values in all Code Runs"
		,"runsHasExpressionsLogicalCount" : "Number of Used Logical Operators in all Code Runs"
		,"runsHasExpressionsUnaryCount" : "Number of Used Unary Operators in all Code Runs"
		,"runsHasExpressionsBitwiseCount" : "Number of Used Bitwise Operators in all Code Runs"
		,"runsHasExpressionsDictCount" : "Number of Used Dictionaries or Maps in all Code Runs"
		,"runsHasExpressionsDataStructureCount" : "Number of Used Data Structures in all Code Runs"
		,"runsHasExpressionsFunctionCall" : "Number of Used Function Calls in all Code Runs"
		,"runsHasControlFlowConditionalCount" : "Number of Used Conditional Flows in all Code Runs"
		,"runsHasExpressionsKeywordCount" : "Number of Used Keywords in all Code Runs"
		,"runsHasControlFlowTryExceptionCount" : "Number of Used Try-Except Blocks in all Code Runs"        
		,"runsHasVariablesNamedCount" : "Number of Used Variables (Name, Name Constant, Starred) in all Code Runs"
		,"runsHasConstantsUsefulCount" : "Number of Used Constants (e.g., Numbers, Strings) in all Code Runs"
		,"runsHasConstantsCount" : "Number of Used Constants in all Code Runs"
		,"runsHasVariablesCount" : "Number of Used Variables (Load, Store, Del, Name, Starred) in all Code Runs"

		,"hasLoop" : "Used Loop"
		,"hasNestedLoop" : "Used Nested Loop"
		,"hasCondition" : "Used Condition"
		,"hasVariable" : "Used Variable"
		,"hasExpressions" : "Used Expressions"
		,"hasAsyncOrAwait" : "Used Async"
		,"hasFunctionClass" : "Used Function or Class"
		,"hasControlFlow" : "Used Control Flows"
		,"hasImports" : "Used Imports"
		,"hasStatements" : "Used Statements (e.g. Assignment, Assert, Delete)"
		,"hasComprehensions" : "Used Comprehensions (ListComp, SetComp, GeneratorExp, DictComp, comprehension)"
		,"hasSubscripting" : "Used Subscription (Subscript, Slice)"
		,"hasExpressionsArithematic" : "Used Arithematic Operators (e.g. Add, Div, Mult)"
		,"hasExpressionsBool" : "Used Boolean (And, Or)"
		,"hasExpressionsLogical" : "Used Logical Operators (e.g. Eq, Lt, Gt)"
		,"hasExpressionsUnary" : "Used Unary Operators"
		,"hasExpressionsBitwise" : "Used Bitwise Operators"
		,"hasExpressionsDict" : "Used Dictionary Or Map (Dict)"
		,"hasExpressionsDataStructure" : "Used Data Structure (e.g. Dict, List, Set)"
        ,"hasExpressionsFunctionCall" : "Used function call (e.g. call('friend'))"
		,"hasControlFlowConditional" : "Used Conditional Flows (e.g. if, continue, break)"
		,"hasControlFlowTryException" : "Used Try exception"
		,"hasVariablesNamed" : "Used Variables"
		,"hasConstantsUseful" : "Used Constants (e.g. 3 or 'a' or None)"
		,"hasExpressionsKeyword" : "Used Keyword (e.g. and, while, None)"
		,"hasConstants" : "Used Constants (e.g. 3 or 'a' or JoinedStr or List)"
		,"hasVariables" : "Used Variables (Load, Store, Del, Name, Starred)"
        
        
        
		, "PracticeSessionDuration" : "Time spent in Practice"
		, "TheorySessionDuration" : "Time spent in Theory"
        , featureSessionDuration : "Total Time spent"
        , COUNT_STUDENT_FEATURE : "Number of Students"
        
        
        , featurePlayerShootEndEnemyHitCount : "Player Shoot Enemy Hit Count"
        , "enemiesCount" : "Count of Enemies"
        , "playerShootCount" : "Player Shoot Count"
        , "playerShootEndCount" : "Player Shoot End Count"
        , "playerShootEndEnemyMissedHitCount" : "Player Shoot Enemy Missed Count"
        , "enemysShootEndPlayerHitCount" : "Enemies Shoot Player Hit Count"
        , "enemysShootEndPlayerNotHitCount" : "Enemies Shoot Player Missed Count"
	}


feature2UserNamesDict[featurePracticeTaskDesc] = "Practice Task"
feature2UserNamesDict[featureTheoryTaskDesc] = "Theory Task"
feature2UserNamesDict[featureTaskDesc] = "Task"
feature2UserNamesDict[featureTaskType] = "Task Type"
feature2UserNamesDict[featureItemsCollectedCount] = "Number of Items Collected"
feature2UserNamesDict[featureRobotCollisionsBoxCount] = "Robot box collision Count"
feature2UserNamesDict[featureConceptsUsedDetailsStr] = "Concepts used details"











#----------------------------------------------------------------
#- Program Concepts Used
#---------------------------------------------------------------
#https://docs.python.org/dev/library/ast.html
ProgramConceptsUsefull2UserNames =  {
		"Name" : "Variable",
		"Starred" : "Variable",
        "Store" : "Variable",
        
        "BinOp" : "Binary operation (Syntax: left operator right ; e.g. a + b ) ",
		
        "Expr" : "Expression (e.g. function call or Add or BitOr etc.)",
		"Add" : "Addition ",
		"Sub" : "Subtraction ",
		"Mult" : "Multiplication",
		"Div" : "Division",
		"BoolOp" : "Boolean operation",
		"And" : "Boolean And",
		"Or" : "Boolean Or",
		"Eq" : "Equal",
		"NotEq" : "Not Equal",
		"Lt" : "Less Than",
		"Is" : "Is",
		"In" : "In",
        
		"Num" : "Number",
		"Str" : "String",
		
        "Assign" : "Assignment (e.g. a = 2)",
		"For" : "For loop",
		"While" : "While loop",
		"If" : "If",
		"Break" : "Break",
		"Continue" : "Continue",
        
		"Try" : "Try",
        "ExceptHandler" : "Exception handler",
		
        "Call" : "Function call",
        "FunctionDef" : "Function definition",
		"arguments" : "Arguments for a function",
		"arg" : "Argument for a Function",
		"Return" : "Return",
		
        "ClassDef" : "Class definition",
        
        "Dict" : "Dictionary (key value)",
		
        "Import" : "Import",
		
        "ListComp" : "List comprehension (Comprehensions)",
		"SetComp" : "Set comprehension (Comprehensions)",
		"DictComp" : "Dict comprehension (Comprehensions)",
	}




#----------------------------------------------------------------
#------------------- feature related END -----------------------------------------------
#----------------------------------------------------------------





#----------------------------------------------------------------
#------------------- GRAPHS START -----------------------------------------------
#----------------------------------------------------------------
graphHeight     = 800
graphWidth      =  1300
graphHeightMin  = 400

graphTemplete = 'seaborn'

successPieFigClassSuccess = "Successfully completed a task"
successPieFigClassOthers = "Fail"

StudentResultExplanation = '        (*has student completed this task in any runs)'

colorError = 'rgb(255,127,80)'
colorSuccess = 'rgb(0,128,0)'
colorPractice = 'rgb(76, 114, 176)'
colorPracticeError = 'rgb(204, 204, 255)'
colorTheory = 'rgb(214,12,140)'
colorTheoryError = 'rgb(255,127,80)'


sortOrderDescending = 'Desc'
sortOrderAscending = 'Asc'
sortOrder = {
        'Desc' : 'Desc',
        'Asc' : 'Asc'
}


#----------------------------------------------------------------
#------------------- GRAPHS END ----------------------------------------------
#----------------------------------------------------------------






#----------------------------------------------------------------
#--------------------------------- General ---------------------------------------
#----------------------------------------------------------------
labelNoData                 = "Has no game interactions"

iconNameHome                = "fa-home"
iconNameGroups              = "fa-list"
iconNameClasses				= "fa-clipboard"
iconNameDetails             = "fa-clipboard"
iconNameStudents            = "fa-user-graduate"
iconNameCustom              = "fa-wrench"
iconNameTutorial            = "fa-question-circle"



labelMedian                 = 'median'
labelMean                   = 'mean'
labelStd                    = 'std'
labelDistAll                = 'All details'
labelTotal                  = 'total'
labelSuccess                = "Success"
labelFail                   = "Fail"

labelStudentTimeline        = "Student Timeline"


FigureTypeScatter           = 'Scatter'
FigureTypePie               = 'Pie.'
FigureTypeBar               = 'Bar'
FigureTypeLine              = 'Line'
FigureTypeBubble            = 'Bubble'
FigureTypeTable             = 'Table'
     
AxisV                       = 'v'
AxisH                       = 'h'
MarginalPlotDefault         = 'box'

PlotDistributionMedian      = "median"
PlotDistributionMean        = "mean"
PlotDistributionStd         = "std"
PlotDistributionAll         = "all"


FigureTypes                 = {
     FigureTypeBar      : { keyLabel        : FigureTypeBar, 
                   keyValue                 : FigureTypeBar,
                  keyIsAxisEnabled          : True,
                  keyIsFeature3Enabled      : False,
                  keyIsDistributionEnabled  : False  ,
                  keyIsMultiFeatureEnabled  : False ,
                  keyIsDccGraph             : True,       }
    ,   
     FigureTypeScatter : { keyLabel             : FigureTypeScatter, 
                  keyValue                      : FigureTypeScatter,
                  keyIsAxisEnabled              : True,
                  keyIsFeature3Enabled          : False,
                  keyIsDistributionEnabled      : True  ,
                  keyIsMultiFeatureEnabled      : False  ,
                  keyIsDccGraph                 : True,       }
#    ,   
#     FigureTypePie      : { keyLabel      : FigureTypePie, 
#                   keyValue     : FigureTypePie,
#                  keyIsAxisEnabled : False,
#                  keyIsFeature3Enabled : False  }
    ,   
     FigureTypeBubble     : { keyLabel      : FigureTypeBubble, 
                   keyValue                 : FigureTypeBubble,
                  keyIsAxisEnabled          : True,
                  keyIsFeature3Enabled      : True,
                  keyIsDistributionEnabled  : False ,
                  keyIsMultiFeatureEnabled  : False   }
    ,   
     FigureTypeLine     : { keyLabel        : FigureTypeLine, 
                   keyValue                 : FigureTypeLine,
                  keyIsAxisEnabled          : True,
                  keyIsFeature3Enabled      : False ,
                  keyIsDistributionEnabled  : False ,
                  keyIsMultiFeatureEnabled  : False,
                  keyIsDccGraph             : True,      }
    ,   
     FigureTypeTable     : { keyLabel       : FigureTypeTable, 
                   keyValue                 : FigureTypeTable,
                  keyIsAxisEnabled          : False,
                  keyIsFeature3Enabled      : False ,
                  keyIsDistributionEnabled  : False ,
                  keyIsMultiFeatureEnabled  : True,
                  keyIsDccGraph             : False, 
                  keyClassName              : " col-sm-12 " }
}
     
     
     
def getFigureTypesOptions():
    return [{keyLabel: FigureTypes.get(i).get(keyLabel) , keyValue: FigureTypes.get(i).get(keyValue)} for i in FigureTypes]





FeaturesCustom          = ['SessionDuration', 'Points', 'Attempts', 'CollectedCoins', 'Difficulty']

FeaturesCustomPractice  = ['NumberOfCoins', 'runsCount', 'runsErrorCount', 'runsSuccessCount', 'runsErrorSyntaxCount',
                                           'runsErrorNameCount', 'runsErrorTypeCount', 'runsLineOfCodeCountAvg',
                                           'tabsSwitchedCount', 'tabsSwitchedDescriptionCount', 'deletedCodesCount', 'robotCollisionsBoxCount']
FeaturesCustomTheory    = ['playerShootCount', 'playerShootEndCount', 'playerShootEndEnemyHitCount',
                                         'playerShootEndEnemyMissedHitCount', 'enemysShootEndPlayerHitCount']
hoverData               = ["CollectedCoins", "Result", "SessionDuration", "Attempts", "robotCollisionsBoxCount", "Points", "lineOfCodeCount", 'StudentId']








colors = ['skyblue', 'palegreen', 'mistyrose', 'cadetblue', 'pink', 'lightcoral'
         ,'violet' , 'lime', 'tomato', 'lightgrey', 'darkslategray']
markers = ['.', 'o', 'v', '^', '<', '>', '*', 's', '+', 'x', 'D', 'H', '|', '-']
markerfacecolors = ['navy', 'seagreen', 'red', 'cyan', 'magenta', 'maroon'
                   ,'darkviolet' , 'green', 'tomato', 'grey', 'mediumturqoise']





codeSubmissionParagraph = "Select a task in the dropdown menu below to see the code submissions your students submitted and how long it took them to write the code. There will also be more information about how many students used certain coding concepts in the chosen task."

studentsGameInteractionParagraph = "This section shows you how much time a student spends on certain tasks. It contains a details table, where you can see every game interaction your student ever had and it contains the student timeline, there you can more easily verify if your student was active in your teaching lessons. You can filter the data per day and choose between ascending or descending sort of the data (per default all of the data is visible)."


#------------------------------------
#-- Label
#------------------------------------
labelSelectLA = 'Select Learning Activity'





#------------------------------------
#-- Strings for Navbar
#------------------------------------

navbarEducator = "Educator"
navbarAdmin = "Admin"

navbarTestUsername = "Markus Zangl"
navbarTestRole = "Admin"




#------------------------------------
#-- Strings for Welcome Site
#------------------------------------

welcomeHeading = "Welcome to the sCool Learning Analytics Web Application!"

welcomeText = ("This website will make tracking student progress and ensuring their success easy. "
               "With this powerful analytics tool, you'll gain insights into your students' performance, enabling you to provide personalized support and drive their academic growth. "
               "You are just a few clicks away from in-depth reports and comprehensive data visualizations, allowing you to easily monitor individual student needs and class-wide trends.")

tutorialHeading = "Tutorial"

tutorialText = "Here is a quick tutorial explaining the most important components of the website to help you take the first steps faster. You can click on the following headlines for better visibility of the explained website components."

searchBarHeading = "Search Bar"

searchBarText = "At the top of the page is a search bar that allows you to search for classes and students the fast way. Simply type in your wanted student or class and the available results will be displayed immediately."

userInformationHeading = "User Information"

userInformationText = "At the top of the page right next to the search bar, you can see the user information field where your account information is displayed. If you click on the user icon you will see some options for managing your user account."

websiteTabsHeading = "Website Tabs"

websiteTabsText = "On the left side of the screen, you can see your available tabs, which are:"

tutorialTabText = "a.) Tutorial tab: This is the tab you currently see. It enables you to have a quick overview of the user interface."

classesTabText = "b.) Classes tab: The classes tab offers class-related information. It allows you to analyze trends and patterns within a specific group of students."

studentsTabText = "c.) Students tab: The students' tab provides student-related information. Gain valuable insights into individual student performance and engagement metrics."

customTabText = "d.) Custom tab: In the Custom tab, you have the freedom to generate your own data visualizations."

infoIconHeading = "Info Icon"

infoIconText = "Located at the bottom left side of the screen, the info icon provides a help center, additional information about courses & tasks, and settings for the look of the webpage."