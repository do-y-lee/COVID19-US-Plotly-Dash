import json
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import dash_table
from dash_table.Format import Format
import dash_table.FormatTemplate as FormatTemplate

from covid.transform.covid_states_agg import complete_states_agg
from covid.transform.covid_states_ts import complete_states_ts
from covid.transform.covid_national_ts import latest_national_snapshot

from app import app


# initiate base dataframe builds
df_states_ts = complete_states_ts()
df_states_agg = complete_states_agg()
df_snapshot = latest_national_snapshot()


def create_us_heatmap_states(metric_name):
    jsonfile = open('static/geojson/us-states-geojson.json', 'r')
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
                               labels = {'confirmed': 'Confirmed Cases'},
                               hover_name = 'State/Territory'
                               )
    fig.update_layout(
        margin = {"r": 0, "t": 0, "l": 100, "b": 0},
        autosize = True,
        height = 500
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
        margin = dict(l=150, r=150, b=120, t=40),
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
                      "Death Rate": "Death Rate (%) (Cumulative)"})
    fig.update_layout(
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        height=700,
        margin = dict(l=150, r=150, b=120, t=40),
        autosize = True
    )

    return fig


def create_df_metric_datatable():
    df_states_data_table = df_states_agg.loc[:,
                           ['State/Territory', 'confirmed', 'deaths', 'cc_per_100k', 'Death Rate (%)']]
    df_states_data_table['Death Rate'] = df_states_data_table['Death Rate (%)'].div(100)
    return df_states_data_table


layout = html.Div([
    html.Br(),
    html.Div([
        dash_table.DataTable(
            id='t1_national_datatable',
            columns=[{"name": i, "id": i} for i in df_snapshot.columns],
            data = df_snapshot.to_dict('records'),
            style_header = {'fontSize': 20, 'border': '1px solid white', 'color': 'lightslategray'},
            style_cell = {'fontSize': 48, 'textAlign': 'center', 'fontWeight': 'bold', 'font-family': 'sans-serif', 'color': 'lightslategray'},
            style_data={'border': '1px solid white'}
        )
    ]),
    html.Br(),
    html.Div([dcc.Dropdown(
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
              ], style={'margin-left': '120px', 'width': '20%', 'padding': 10}),
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(id = 't1_covid_states_heatmap',
                          figure = create_us_heatmap_states('confirmed'))
            ),
            dbc.Col(
                dash_table.DataTable(
                    id = 't1_states_datatable',
                    columns = [
                        {'name': 'State/Territory', 'id': 'State/Territory'},
                        {'name': 'Cases/100k', 'id': 'cc_per_100k', 'type': 'numeric', 'format': Format(group = ',')},
                        {'name': 'Death Rate', 'id': 'Death Rate', 'type': 'numeric',
                         'format': FormatTemplate.percentage(2)}
                    ],
                    fixed_rows = {'headers': True},
                    style_table = {'height': '900px', 'width': '500px', 'padding-right': 100, 'overflowX': 'auto'},
                    data = create_df_metric_datatable().to_dict('records'),
                    sort_action = 'native',
                    style_cell = {'fontSize': 14, 'textAlign': 'left'},
                    style_header = {
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    style_cell_conditional = [
                        {'if': {'column_id': 'State/Territory'},
                         'width': '20%'},
                        {'if': {'column_id': 'Cases/100k'},
                         'width': '20%'},
                        {'if': {'column_id': 'Death Rate'},
                         'width': '25%'}
                    ]
                ), width={'size': 3}
            )
        ]
    ),
    html.Div([
        dcc.Graph(id='t1_covid_states_bar_chart',
                  figure=create_states_bar_chart('confirmed'),
                  config={'displayModeBar': False, 'scrollZoom': False})
    ]),
    html.Br(),
    html.Div([
        dcc.Graph(id = 't1_covid_states_line_chart',
                  figure = create_states_line_chart('Confirmed Cases'),
                  config = {'displayModeBar': False, 'scrollZoom': False})
    ]),
    html.Br()
])


@app.callback(Output('t1_covid_states_heatmap', 'figure'),
              [Input('t1_covid_metric_dropdown', 'value')])
def update_states_heatmap(selected_metric):
    fig = create_us_heatmap_states(selected_metric)
    return fig


@app.callback(Output('t1_covid_states_bar_chart', 'figure'),
              [Input('t1_covid_metric_dropdown', 'value')])
def update_states_bar_chart(selected_metric):
    fig = create_states_bar_chart(selected_metric)
    return fig


@app.callback(Output('t1_covid_states_line_chart', 'figure'),
              [Input('t1_covid_metric_dropdown', 'value')])
def update_states_line_chart(selected_metric):
    fig = create_states_line_chart(selected_metric)
    return fig
