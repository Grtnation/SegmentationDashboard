from numpy import append
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output
from dash import Dash, html, dcc
import plotly.express as px
from pandas import DataFrame
from pandas.io.parsers import TextFileReader
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc


df = pd.read_csv("example_segments.csv")
#app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])


#Side Bar 
SIDEBAR_STYLE = {
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '12rem',
    'padding': '2rem 1rem',
    'background-color': 'lightgrey',
    'color': 'black',
}
CONTENT_STYLE = {
    'margin-left': '15rem',
    'margin-right': '2rem',
    'padding': '2rem' '1rem',
    'color': 'black',
}


#Overlapping segments data
fixed_time = df[df["Segment Type"].str.contains("Segment_Type.FIXED_TIME")]
generate = df[df["Segment Type"].str.contains("Segment_Type.GENERATE")]
deadspace = df[df["Segment Type"].str.contains("Segment_Type.DEADSPACE")]

deadspace = deadspace.head()
generate = generate.head()
fixed_time = fixed_time.head()
All = [fixed_time,generate, deadspace]
result = pd.concat(All)

#Overlapping Segments Graph
fig = px.timeline(result, x_start="Start Time", x_end="End Time", y="Segment Type", color="Segment Type")
fig.update_yaxes(autorange="reversed")
    

#Line Graph
df["timeline"] = df["Start Time"] + df["End Time"]
df['timeline'] = pd.to_datetime(df['timeline']).dt.time
fig_line = px.line(df, x="timeline", y="Number of Logs",title = 'Segments')
fig_line.update_traces(mode='markers+lines')
fig_line.update_xaxes(rangeslider_visible=True)


fig_line.update_layout(
    title = 'Number of Logs by Time'
    ,xaxis_title = 'Timeline'
    ,yaxis_title = 'Number of logs'
    ,font = dict(size = 15)
    ,template = 'plotly_dark' #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
)

#Bubble Chart
fig_bubble = px.scatter(df.head(100),x="Start Time", y="End Time",
	         size="Number of Logs", color="Segment Type",
                 hover_name="Generate Matched Values")

#Pie Chart
fig_pie = px.pie(df, values='Number of Logs', names='Segment Type')
#fig_pie.show()

#Bar Chart
fig_bar = px.histogram(df, x="Segment Type", y="Number of Logs",
             color='Segment Type', barmode='group',
             histfunc='avg',
             height=400)
#Area Chart
fig_area = px.area(df, x="Start Time", y="End Time", color="Segment Type", line_group="Number of Logs")


#Time Between Segments Conversion
df["Start Time"] = pd.to_datetime(df["Start Time"])
df["End Time"] = pd.to_datetime(df["End Time"])
# Duration of segments 
lst = []
for i in range(len(df["End Time"])):
    lst.append((df["End Time"][i] - df["Start Time"][i]).total_seconds())
    
#print(lst)
       
df["Duration"] = lst

#Time Between Segments in a Gantt Chart
fig_gantt = px.timeline(df, x_start="Start Time", x_end="End Time", y="Segment Type", color="Duration")
fig.update_yaxes(autorange="reversed")

#Time Between Segments in a Histogram
fig_hist = px.histogram(df, x="Segment Type", y="Number of Logs",
             color='Duration', barmode='group',
             histfunc='avg',
             height=400
            )


child = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Segments Plotly Dashboard"))), #header
        dbc.Row([
            dbc.Col([
            html.H5("Overlapping Segments", className="text-center"),
            dcc.Tab(label='Segment Types Overlapping', children=[
            dcc.Graph(
                id='chrt-portfolio-main',
                figure = fig.update_layout(template = 'plotly_dark'),
                style={'height': 550}),
            html.Hr(),
                
        ]),        
        ],width={'size': 8, 'offset': 0, 'order': 1}),
            dbc.Col([  # second column on second row
            html.H5('Bar Chart', className='text-center'),
            dcc.Graph(id='indicators-ptf',
                      figure = fig_bar.update_layout(template='plotly_dark'),
                      style={'height':550}),
            html.Hr()
            ], width={'size': 4, 'offset': 0, 'order': 2}),  # width second column on second row
            dbc.Col([  # third column on second row
            html.H5('Pie Chart', className='text-center'),
            dcc.Graph(id='pie-top15',
                      figure = fig_pie.update_layout(template='plotly_dark'),
                      style={'height':380}),
            html.Hr()
            ], width={'size': 4, 'offset': 0, 'order': 2}),
            
            
    ]),
        dbc.Row([  # start of third row
            dbc.Col([  # first column on third row
                html.H5('Number of logs by Time', className='text-center'),
                dcc.Graph(id='chrt-portfolio-secondary',
                      figure=fig_line,
                      style={'height':380}),
            ], width={'size': 8, 'offset': 0, 'order': 1}),
    ]),
        dbc.Row([  # start of third row
            dbc.Col([  # first column on third row
                html.H5('Filtering By Segment Type', className='text-center'),
                
                dcc.Tab(label='Filtering By Segment Type', children=[
            dcc.Dropdown(id="Segment_Types",
                 options=[
                     {"label": "Fixed Times", "value": "Segment_Type.FIXED_TIME"},
                     {"label": "Generate", "value": "Segment_Type.GENERATE"},
                     {"label": "Deadspace", "value": "Segment_Type.DEADSPACE"}],
                 multi=False,
                 value="Segment_Type.FIXED_TIME"

                 ),
            html.Div(id='output_container', children=[]),
            html.Br(),
            dcc.Graph(id="segment", figure={}),
        ]),
            ], width={'size': 8, 'offset': 0, 'order': 1}),
    ]),
    ])
    
        
sidebar = html.Div(
    [
#         html.H5("Navigation Menu", className='display-6'),
        html.Hr(),
        html.P('Dashboard Menu', className='text-center'),
        
        
        
        dbc.Nav(
            [
                dbc.NavLink('Home', href="/", active='exact'),
                dbc.NavLink('Plotly', href="/page-2", active='exact'),
                dbc.NavLink('Gantt', href="/page-Gantt", active='exact'),
                dbc.NavLink('Documentation', href="/page-docs", active='exact'),
                dbc.DropdownMenu(
                    label="Plotly Graphs",
                    toggle_style={
                        "color":"#008080",
                        "background": "#D3D3D3",
                    },
                    children=[
                        dbc.DropdownMenuItem("Gantt Chart"),
                        dbc.DropdownMenuItem("Bar Chart"),
                        dbc.DropdownMenuItem("Pie Chart"),
                    ],
                    
                )
            ],
            
            vertical=True,
            pills=True,
        ),
        
        
    ],
    
    style=SIDEBAR_STYLE,
)




content = html.Div(id='page-content', children=child, style=CONTENT_STYLE)

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])
# app = JupyterDash(__name__)
app.layout = html.Div([
    dcc.Location(id='url'),
    sidebar,
    content
])

@app.callback(
    [
        Output(component_id='output_container', component_property="children"),
        Output(component_id='segment', component_property="figure")],
    [Input(component_id='Segment_Types', component_property="value")]
)

def update_graph(option_segment):
    print(option_segment)
    print(type(option_segment))

    container = "Segment Types is:{}".format(option_segment)
    dff = df.copy()
    dff = dff[dff['Segment Type'] == option_segment]
    # Plotly Express
    fig = px.timeline(dff.head(50), x_start="Start Time", x_end="End Time", y="Segment Name", color="Number of Logs")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template = 'plotly_dark')
    #fig.show()

    return container, fig

if __name__ == '__main__':
    app.run_server(debug=True, port=3096)
    
    
    
    
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output
from dash import Dash, html, dcc
import plotly.express as px
from pandas import DataFrame
from pandas.io.parsers import TextFileReader
import plotly.figure_factory as ff
import dash_bootstrap_components as dbc

app = Dash(__name__)
# the style arguments for the sidebar. We use position:fixed and a fixed width



df = pd.read_csv("example_segments.csv")


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Page 1", href="/page-1", active="exact"),
                dbc.NavLink("Page 2", href="/page-2", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)


fig_pie = px.pie(df, values='Number of Logs', names='Segment Type')
#Overlapping segments data
fixed_time = df[df["Segment Type"].str.contains("Segment_Type.FIXED_TIME")]
generate = df[df["Segment Type"].str.contains("Segment_Type.GENERATE")]
deadspace = df[df["Segment Type"].str.contains("Segment_Type.DEADSPACE")]

deadspace = deadspace.head()
generate = generate.head()
fixed_time = fixed_time.head()
All = [fixed_time,generate, deadspace]
result = pd.concat(All)

#Overlapping Segments Graph
fig = px.timeline(result, x_start="Start Time", x_end="End Time", y="Segment Type", color="Segment Type")
fig.update_yaxes(autorange="reversed")
fig.update_layout(
    autosize=False,
    width=1000,
    height=500,
    template = 'plotly_dark'
)
    

#Line Graph
df["timeline"] = df["Start Time"] + df["End Time"]
df['timeline'] = pd.to_datetime(df['timeline']).dt.time
fig_line = px.line(df, x="timeline", y="Number of Logs",title = 'Segments')
fig_line.update_traces(mode='markers+lines')
fig_line.update_xaxes(rangeslider_visible=True)


fig_line.update_layout(
    title = 'Number of Logs by Time',
    xaxis_title = 'Timeline',
    yaxis_title = 'Number of logs',
    font = dict(size = 15),
    template = 'plotly_dark', #"plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"
    autosize=False,
    width=500,
    height=500
)


trends = ['HOME', 'ABOUT', 'CHARTS']

app.layout = html.Div(children=[
    
    html.H1(children='Segment Plotly Dashboard'),
    html.P('By Grant Tamrakar'),
    html.Div(
    className="right_content",
    children=[
        html.Div(
    className="left_menu",
    children=[
        html.H1(
            'Segmentation Dashboard'
        ),
        
        html.Div(
            className="trend",
            children=[
            html.Ul(id='my-list', children=[html.Li(i) for i in trends])
        ],
    )

        
    ]
),
        html.Div(
            className="top_metrics",
            children=[
                html.H1('Segments Dashboard')
            
            ]
        ),
        html.Div(
            'This down top metrics'
        ),
    ]
),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),
    dcc.Graph(
                #OverLapping Segments 
                figure = fig,
                style={'width': '49%','padding-left':'100px', "margin-right": "auto","margin-left":"auto"},
            
            ),

    
    dcc.Graph(
        
        id='pie-graph',
        figure=fig_pie.update_layout(template='plotly_dark'),
        style={'width': '49%','padding-left':'100px', "margin-left":"auto"},
        
    ),

    dcc.Graph(
                #Line Graph
                id='Line',
                figure=fig_line,
                style={'width': '49%',
                'padding-left':'100px',  
                
                "margin-left": 'auto'}
    ),
    dcc.Dropdown(id="Segment_Types",
                 options=[
                     {"label": "Fixed Times", "value": "Segment_Type.FIXED_TIME"},
                     {"label": "Generate", "value": "Segment_Type.GENERATE"},
                     {"label": "Deadspace", "value": "Segment_Type.DEADSPACE"}],
                 multi=False,
                 value="Segment_Type.FIXED_TIME"

                 ),
            html.Div(id='output_container', children=[]),
            html.Br(),
            dcc.Graph(id="segment", figure={},style={'width': '49%',
                'padding-left':'100px',  
                
                "margin-left": 'auto'},),
            


])

@app.callback(
    [
        Output(component_id='output_container', component_property="children"),
        Output(component_id='segment', component_property="figure")],
    [Input(component_id='Segment_Types', component_property="value")]
)

def update_graph(option_segment):
    print(option_segment)
    print(type(option_segment))

    container = "Segment Types is:{}".format(option_segment)
    dff = df.copy()
    dff = dff[dff['Segment Type'] == option_segment]
    # Plotly Express
    fig = px.timeline(dff.head(50), x_start="Start Time", x_end="End Time", y="Segment Name", color="Number of Logs")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(template = 'plotly_dark')
    fig.show()

    return container, fig

if __name__ == '__main__':
    app.run_server(debug=True)