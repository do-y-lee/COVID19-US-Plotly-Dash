import json
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import dash_table
from dash_table.Format import Format
import dash_table.FormatTemplate as FormatTemplate

from models.covid_states import CovidStates
from app import app


# initiate base dataframe builds
df_states_ts = CovidStates.ts_complete_states()
df_states_agg = CovidStates.agg_complete_states()
df_snapshot = CovidStates.latest_national_snapshot()


# ---------------- Section 1: Define functions to generate Dash figures and datatables ------------------ #

def create_us_heatmap_states(metric_name):
    jsonfile = open('data/geojson/us-states-geojson.json', 'r')
    states_geojson = json.loads(jsonfile.read())

    fig = px.choropleth_mapbox(df_states_agg,
                               geojson=states_geojson,
                               locations='State FIPS',
                               color=metric_name,
                               color_continuous_scale='matter',
                               range_color=(0, df_states_agg[metric_name].max()),
                               mapbox_style='carto-positron',
                               zoom=3,
                               center={"lat": 37.0902, "lon": -95.7129},
                               opacity=0.5,
                               hover_data={
                                   'Cases per 100k': True,
                                   'Confirmed Cases': True,
                                   'Deaths per 100k': True,
                                   'Deaths': True,
                                   '2019 Est Pop': True,
                                   'State FIPS': False,
                                   'confirmed': False,
                                   'cc_per_100k': False,
                                   'd_per_100k': False
                               },
                               labels = {'confirmed': 'Cases'},
                               hover_name = 'State/Territory'
                               )
    fig.update_layout(
        margin = {"r": 100, "t": 10, "l": 50, "b": 10},
        autosize = True,
        height = 600
    )

    return fig


def create_states_bar_chart(metric_name):
    df_states_agg['Death Rate (%)'] = df_states_agg['Death Rate (%)'].round(2)
    fig = px.bar(df_states_agg,
                 y=metric_name,
                 x='State/Territory',
                 text=metric_name,
                 labels={'confirmed': 'Confirmed Cases',
                         'deaths': 'Deaths',
                         'cc_per_100k': 'Case per 100k',
                         'd_per_100k': 'Deaths per 100k'}
                 )

    if metric_name == 'Death Rate (%)':
        fig.update_traces(textposition='outside', marker_color='lightslategray')
    else:
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside', marker_color='lightslategray')

    fig.update_layout(
        plot_bgcolor="white",
        hoverlabel = dict(
            bgcolor = "white",
            font_size = 14,
            font_family = "Rockwell"
        ),
        xaxis={'categoryorder': 'total descending'},
        bargap=0.01,
        height = 500,
        margin = dict(l=100, r=50, b=120, t=40),
        autosize = True
    )

    return fig


def create_states_line_chart(metric_name):
    if metric_name == 'confirmed':
        metric_name = 'Confirmed Cases'
    elif metric_name == 'deaths':
        metric_name = 'Deaths'
    elif metric_name == 'cc_per_100k':
        metric_name = 'Cases per 100k'
    elif metric_name == 'd_per_100k':
        metric_name = 'Deaths per 100k'
    else:
        metric_name = metric_name

    fig = px.line(df_states_ts, x='Date', y=metric_name, color='State/Territory',
                  labels={
                      "Confirmed Cases": "Confirmed Cases (Cumulative)",
                      "Deaths": "Deaths (Cumulative)",
                      "Cases per 100k": "Cases per 100k (Cumulative)",
                      "Deaths per 100k": "Deaths per 100k (Cumulative)",
                      "Death Rate": "Death Rate (%) (Cumulative)"}
                  )
    fig.update_layout(
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        height=700,
        margin = dict(l=100, r=50, b=120, t=40),
        autosize = True
    )

    return fig


def create_df_metric_datatable():
    df_states_data_table = df_states_agg.loc[:, ['State/Territory', 'confirmed', 'deaths',
                                                 'cc_per_100k', 'd_per_100k',
                                                 'Death Rate (%)', 'Population']]
    df_states_data_table['Death Rate'] = df_states_data_table['Death Rate (%)'].div(100)

    return df_states_data_table


# ---------------- Section 2: Create Dash layout object ------------------ #

layout = html.Div([
    html.Br(),
    # row with six columns and each column contains a datatable with xl=2
    dbc.Row([
        dbc.Col(
            dash_table.DataTable(
                id='t1_national_datatable',
                columns=[{"name": 'U.S. Population', "id": 'U.S. Population'}],
                data = [{'U.S. Population': df_snapshot.loc[:, 'U.S. Population']}],
                style_header = {'fontSize': 18, 'border': '1px solid white', 'color': 'lightslategray'},
                style_cell = {'fontSize': 34, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif', 'color': 'lightslategray'},
                style_data={'border': '1px solid white'}
            ), xl=2
        ),
        dbc.Col(
            dash_table.DataTable(
                id = 't1_national_datatable',
                columns = [{"name": 'Confirmed Cases', "id": 'Confirmed Cases'}],
                data = [{'Confirmed Cases': df_snapshot.loc[:, 'Confirmed Cases']}],
                style_header = {'fontSize': 18, 'border': '1px solid white', 'color': 'lightslategray'},
                style_cell = {'fontSize': 34, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif',
                              'color': 'lightslategray'},
                style_data = {'border': '1px solid white'}
            ), xl=2
        ),
        dbc.Col(
            dash_table.DataTable(
                id = 't1_national_datatable',
                columns = [{"name": 'Deaths', "id": 'Deaths'}],
                data = [{'Deaths': df_snapshot.loc[:, 'Deaths']}],
                style_header = {'fontSize': 18, 'border': '1px solid white', 'color': 'lightslategray'},
                style_cell = {'fontSize': 34, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif',
                              'color': 'lightslategray'},
                style_data = {'border': '1px solid white'}
            ), xl=2
        ),
        dbc.Col(
            dash_table.DataTable(
                id = 't1_national_datatable',
                columns = [{"name": 'Cases per 100k', "id": 'Cases per 100k'}],
                data = [{'Cases per 100k': df_snapshot.loc[:, 'Cases per 100k']}],
                style_header = {'fontSize': 18, 'border': '1px solid white', 'color': 'lightslategray'},
                style_cell = {'fontSize': 34, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif',
                              'color': 'lightslategray'},
                style_data = {'border': '1px solid white'}
            ), xl=2
        ),
        dbc.Col(
            dash_table.DataTable(
                id = 't1_national_datatable',
                columns = [{"name": 'Deaths per 100k', "id": 'Deaths per 100k'}],
                data = [{'Deaths per 100k': df_snapshot.loc[:, 'Deaths per 100k']}],
                style_header = {'fontSize': 18, 'border': '1px solid white', 'color': 'lightslategray'},
                style_cell = {'fontSize': 34, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif',
                              'color': 'lightslategray'},
                style_data = {'border': '1px solid white'}
            ), xl=2
        ),
        dbc.Col(
            dash_table.DataTable(
                id = 't1_national_datatable',
                columns = [{"name": 'Death Rate', "id": 'Death Rate'}],
                data = [{'Death Rate': df_snapshot.loc[:, 'Death Rate']}],
                style_header = {'fontSize': 18, 'border': '1px solid white', 'color': 'lightslategray'},
                style_cell = {'fontSize': 34, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif',
                              'color': 'lightslategray'},
                style_data = {'border': '1px solid white'}
            ), xl=2
        )
    ]),
    html.Br(),
    html.Br(),
    # row with one column and column contains a div with dropdown
    dbc.Row(
        dbc.Col(
            html.Div([
                dcc.Dropdown(
                    id='t1_covid_metric_dropdown',
                    options=[
                        {'label': 'Confirmed Cases', 'value': 'confirmed'},
                        {'label': 'Deaths', 'value': 'deaths'},
                        {'label': 'Cases per 100k', 'value': 'cc_per_100k'},
                        {'label': 'Deaths per 100k', 'value': 'd_per_100k'},
                        {'label': 'Death Rate (%)', 'value': 'Death Rate (%)'},
                    ],
                    value='confirmed',
                    clearable=False)
            ], style={'padding-left': '20px', 'padding-right': '20px', 'padding-bottom': '20px'}),
            lg=3
        )
    ),
    # row with one column and column contains a graph
    dbc.Row(
        dbc.Col(
            dcc.Graph(id = 't1_covid_states_heatmap',
                      figure = create_us_heatmap_states('confirmed'))
        )
    ),
    # row with one column and column contains a graph
    dbc.Row(
        dbc.Col(
            dcc.Graph(id='t1_covid_states_bar_chart',
                      figure=create_states_bar_chart('confirmed'),
                      config={'displayModeBar': False, 'scrollZoom': False})
        )
    ),
    html.Br(),
    # row with one column and column contains a graph
    dbc.Row(
        dbc.Col(
            dcc.Graph(id = 't1_covid_states_line_chart',
                      figure = create_states_line_chart('Confirmed Cases'),
                      config = {'displayModeBar': False, 'scrollZoom': False})
        )
    ),
    html.Hr(),
    html.Br(),
    dbc.Row(
        dbc.Col(
            html.Div([
                html.H2("U.S. States COVID-19 Summary")
                ], style={'padding-left': '20px', 'padding-right': '20px',
                          'fontWeight': 'bold', 'font-family': 'sans-serif'}
            ),
            xl=6
        )
    ),
    html.Br(),
    # row with one column and column contains a datatable
    dbc.Row(
        dbc.Col(
            dash_table.DataTable(
                id = 't1_states_covid_summary',
                columns = [
                    {'name': 'State/Territory', 'id': 'State/Territory'},
                    {'name': 'Cases', 'id': 'confirmed', 'type': 'numeric', 'format': Format(group=',')},
                    {'name': 'Deaths', 'id': 'deaths', 'type': 'numeric', 'format': Format(group=',')},
                    {'name': 'Cases/100k', 'id': 'cc_per_100k', 'type': 'numeric', 'format': Format(group=',')},
                    {'name': 'Deaths/100k', 'id': 'd_per_100k', 'type': 'numeric', 'format': Format(group=',')},
                    {'name': 'Death Rate', 'id': 'Death Rate', 'type': 'numeric',
                     'format': FormatTemplate.percentage(2)},
                    {'name': 'Population', 'id': 'Population', 'type': 'numeric', 'format': Format(group=',')},
                ],
                style_table = {'padding-left': 50, 'padding-right': 50, 'overflowX': 'auto'},
                data = create_df_metric_datatable().to_dict('records'),
                sort_action = 'native',
                style_cell = {'fontSize': 14, 'textAlign': 'left'},
                style_header = {
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            )
        )
    ),
    html.Br(),
    html.Br(),
    # row with one column and column contains markdown
    dbc.Row(
        dbc.Col(
            html.Div(
                dcc.Markdown('''
                >
                > The models that powers this metrics dashboard comes from [Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19)
                > and [U.S. Census](https://www.census.gov). The U.S. COVID-19 metrics dashboard is only for educational purposes.
                > This dashboard is not be used for any medical reasons and contents should not be interpreted as professional or medical guidance.
                >
                '''),
                style={'marginLeft': 40, 'marginRight': 40, 'marginTop': 0, 'marginBottom': 30,
                       'textAlign': 'left', 'padding': '6px 0px 0px 8px', 'border': 'thin grey dashed'}
            )
        )
    )
])


# ---------------- Section 3: Define Dash callback functions ------------------ #

# callback 1
@app.callback(Output('t1_covid_states_heatmap', 'figure'),
              [Input('t1_covid_metric_dropdown', 'value')])
def update_states_heatmap(selected_metric):
    fig = create_us_heatmap_states(selected_metric)
    return fig


# callback 2
@app.callback(Output('t1_covid_states_bar_chart', 'figure'),
              [Input('t1_covid_metric_dropdown', 'value')])
def update_states_bar_chart(selected_metric):
    fig = create_states_bar_chart(selected_metric)
    return fig


# callback 3
@app.callback(Output('t1_covid_states_line_chart', 'figure'),
              [Input('t1_covid_metric_dropdown', 'value')])
def update_states_line_chart(selected_metric):
    fig = create_states_line_chart(selected_metric)
    return fig
