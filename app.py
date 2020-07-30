# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 19:06:08 2020

@author: tilan
"""

# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from dash.dependencies import Input, Output, State


import numpy as np
import pandas as pd
import dash_table
import flask
import math


FA = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"
MATERIAL_CSS = "https://fonts.googleapis.com/icon?family=Material+Icons"

external_stylesheets = [
                        dbc.themes.BOOTSTRAP,
                        dbc.themes.MATERIA,
                        FA,
#                        MATERIAL_CSS
                        ]



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True






#returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [
            
            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id = id_value,
                className="indicator_value"
            ),
        ],
        className="four columns indicator",
    )



def generateCardBase(label, value):
    return html.Div(
        [
            html.Span(
                children = [ value ],
                className="card_value"
            ),
            html.P(
                label,
                className="card_label"
            ),
        ],
        className="c-card card-base",
    )
        
  
def generateCardDetail(label, valueMain = '', value1 = '', value2 = '', 
                       valueMainLabel = '', value1Label = '', value2Label = '',
                       
                       
                       description = '', ):
    return html.Div(
        [
            html.Div(
                children = [html.Div(
                                    children = [ value1Label ],
                                    className="card_value_label"
                                ), value1 ],
                className="card_value1"
            ),
            html.Div(
                children = [html.Div(
                                    children = [ value2Label ],
                                    className="card_value_label"
                                ),   value2 ],
                className="card_value2"
            ),
            html.Div(
                children =[html.Div(
                                    children = [ valueMainLabel ],
                                    className="card_value_label"
                                ),  valueMain],
                className="card_value"
            ),
            html.Span(
                label,
                className="card_label"
            ),
            html.Span(
                description,
                className="card_description"
            ),
        ],
        className="c-card card-detail",
    )
              

def generateCardDetail2(label, value1 = '', value2 = '',
                        value1Label = '', value2Label = '',
                        description = '', ):
    return html.Div(
        [
            html.Div(
                children = [html.Div(
                                    children = [ value1Label ],
                                    className="card_value_label"
                                ),  value1 ],
                className="card_value1"
            ),
            html.Div(
                children = [html.Div(
                                    children = [ value2Label ],
                                    className="card_value_label"
                                ),  value2 ],
                className="card_value2"
            ),
            html.Span(
                label,
                className="card_label"
            ),
            html.Span(
                description,
                className="card_description"
            ),
        ],
        className="c-card card-detail-2",
    )
                      

millnames = ["", " K", " M", " B", " T"] # used to convert numbers

#returns most significant part of a number
def millify(n):
    n = float(n)
    millidx = max(
        0,
        min(
            len(millnames) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))
        ),
    )

    return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])


#converts seconds to Day, Hour, Minutes, Seconds
def seconds_2_dhms(time, isLong = False):
    seconds_to_minute   = 60
    seconds_to_hour     = 60 * seconds_to_minute
    seconds_to_day      = 24 * seconds_to_hour

    days    =   time // seconds_to_day
    time    %=  seconds_to_day

    hours   =   time // seconds_to_hour
    time    %=  seconds_to_hour

    minutes =   time // seconds_to_minute
    time    %=  seconds_to_minute

    seconds = time
    
    result = ''
    
    dayLabel = 'days' if days > 1 else 'day'
    hoursLabel = 'hours' if hours > 1 else 'hour'
    minutesLabel = 'minutes' if minutes > 1 else 'minute'
    secondsLabel = 'seconds' if seconds > 1 else 'second'
    
    if days > 0:
            result = "%d %s, %02d:%02d:%02d" % (days, dayLabel, hours, minutes, seconds)
            if isLong :
                result = "%d %s, %d %s, %d %s, %d %s" % (days, dayLabel, hours, hoursLabel, minutes, minutesLabel, seconds, secondsLabel)
    else :
        if isLong :
            if hours > 0 :
                result = "%d %s, %d %s, %d %s" % (hours, hoursLabel, minutes, minutesLabel, seconds, secondsLabel)
            else :
                result = "%d %s, %d %s" % (minutes, minutesLabel, seconds, secondsLabel)
        else :
            result = "%02d:%02d:%02d" % (hours, minutes, seconds)
            
    return result
            