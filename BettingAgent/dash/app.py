# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import csv
import re
import pandas as pd


# LOAD DATA
data = []
i = 0
with open('../data/nba-daily_player_stats-20170120-2016-2017-regular.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
        if i == 0:
            names = re.sub("#","",row[0]).split(',')
            #print row
        else:
            data.append(re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', re.sub("#","",row[0])))
            #parsing at each , except when ","
        i = i+1
df = pd.DataFrame(data, columns = names)


# START APP
app = dash.Dash(static_folder='static')

external_css = ["https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
                "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
                '/css/first_css.css']



for css in external_css:
    app.css.append_css({"external_url": css})

app.layout = html.Div(children=[
    html.Div(children = [
        html.Div(children="First Div", className="col-md-6"),
        html.Div(children="Second Div", className="col-md-6"),
    ],
    className = "row"
    ),
    
    html.Div(children=[
        html.H1(children='Hello Dash', className = "myClass"),
        html.Div(children='Dash: A web application framework for Python.', className = "row-content"),
        html.Div(children = 
            dcc.Graph(
                id='example-graph',
                figure={
                    'data': [go.Histogram(
                        x=df['Pts']
                    )],
                    'layout': go.Layout(
                        title="Daily Stats from 20th of Jan 2017"
                    )
                }
            ),
            className = "row-content"
        )#end of graph div
    ],
    className = ["row", "h-100"]
    )
],
className = "container"
)



if __name__ == '__main__':
    app.run_server(debug=True)
    
    