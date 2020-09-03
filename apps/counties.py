import json
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import dash_table
from dash_table.Format import Format
import dash_table.FormatTemplate as FormatTemplate
import plotly.express as px

from covid.transform.covid_counties_agg import complete_counties_agg
from covid.transform.covid_counties_ts import complete_counties_ts
from covid.stats import states_stats

from app import app


# call dataframe functions and build base dataframes
df_complete_counties_agg = complete_counties_agg()
df_counties_ts = complete_counties_ts()
df_state_location = states_stats()


def create_us_bubble_map_counties(metric_name):
    # remove counties without lat and long
    df_counties = df_complete_counties_agg[
        (df_complete_counties_agg['Lat'] != 0) & (df_complete_counties_agg['Lat'] != 0)]

    fig = px.scatter_mapbox(df_counties,
                            lat='Lat',
                            lon='Long_',
                            color=metric_name,
                            size=metric_name,
                            mapbox_style='carto-positron',
                            color_continuous_scale=px.colors.diverging.balance,
                            size_max=80,
                            zoom=3.2,
                            center = {"lat": 37.0002, "lon": -95.7129},
                            opacity=0.5,
                            hover_data={'Confirmed Cases': True,
                                        'Deaths': True,
                                        'Death Rate (%)': True,
                                        'Cases per 1000': True,
                                        'Est Pop': True,
                                        'confirmed': False,
                                        'Lat': False,
                                        'Long_': False},
                            hover_name='County-State',
                            labels={'confirmed': 'Cases'})

    fig.update_layout(
        margin={"r": 200, "t": 10, "l": 100, "b": 10},
        autosize=True,
        height = 600
    )

    return fig


def create_state_map_counties(state_name, metric_name):
    if state_name == 'Alaska':
        zoom_num = 2.7
    elif state_name == 'California':
        zoom_num = 5
    elif state_name in ['Texas', 'Montana', 'New Mexico', 'Arizona', 'Nevada', 'Colorado', 'Wyoming', 'Oregon', 'Idaho']:
        zoom_num = 5.4
    elif state_name in ['Vermont', 'Rhode Island', 'Hawaii', 'Connecticut', 'New Jersey', 'New Hampshire']:
        zoom_num = 6.8
    elif state_name == 'Delaware':
        zoom_num = 7.8
    elif state_name == 'District of Columbia':
        zoom_num = 10
    else:
        zoom_num = 5.6

    # grab geojson for US counties
    if 'counties' in locals():
        pass
    else:
        jsonfile = open('static/geojson/us-counties-fips-geojson.json', 'r')
        counties_json = json.loads(jsonfile.read())

    # df_state_location for lat and lon per state
    lat = df_state_location[df_state_location['State/Territory'] == state_name]['lat'].iloc[0]
    lon = df_state_location[df_state_location['State/Territory'] == state_name]['lon'].iloc[0]

    # Grab the state FIPS with most count if there are more than one state FIPS per state
    if state_name == 'District of Columbia':
        max_state_fips = '11'
    else:
        state_fips = df_complete_counties_agg[df_complete_counties_agg['State/Territory'] == state_name]['State FIPS'].value_counts()
        max_state_fips = state_fips.idxmax()

    # define the start and end of range_color based on min and max confirmed cases per state
    max_rcolor = df_complete_counties_agg[df_complete_counties_agg['State FIPS'] == max_state_fips][metric_name].max()
    min_rcolor = df_complete_counties_agg[df_complete_counties_agg['State FIPS'] == max_state_fips][metric_name].min()

    # parsing geojson data per state
    state_counties = [county for county in counties_json['features'] if county['id'][:2] == max_state_fips]
    state_geojson = {'type': 'FeatureCollection', 'features': state_counties}

    fig = px.choropleth_mapbox(df_complete_counties_agg[df_complete_counties_agg['State/Territory'] == state_name],
                               geojson=state_geojson,
                               locations='FIPS',
                               mapbox_style='carto-positron',
                               zoom=zoom_num,
                               color=metric_name,
                               color_continuous_scale='matter',
                               range_color=(min_rcolor, max_rcolor),
                               hover_name='State/Territory',
                               hover_data={'County': True, 'confirmed': True, 'Est Pop': True, 'FIPS': False},
                               center = {"lat": lat, "lon": lon},
                               opacity=0.5,
                               labels={'confirmed': 'Cases'})

    fig.update_layout(
        margin={"r": 200, "t": 10, "l": 100, "b": 10},
        height=700,
    )

    return fig


def create_state_line_counties(state_name, metric_name):
    if metric_name == 'confirmed':
        metric_name = 'Confirmed Cases'
    elif metric_name == 'deaths':
        metric_name = 'Deaths'
    elif metric_name == 'Death Rate':
        metric_name = 'Death Rate (%)'
    else:
        metric_name = metric_name

    fig = px.line(df_counties_ts[df_counties_ts['State/Territory'] == state_name], x='Date', y=metric_name, color='County',
                  labels = {
                      "Confirmed Cases": "Confirmed Cases (Cumulative)",
                      "Deaths": "Deaths (Cumulative)",
                      "Death Rate (%)": "Death Rate (%) (Cumulative)"
                  })
    fig.update_layout(
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1),
        height=700,
        margin=dict(l=0, r=100, b=0, t=0)
    )

    return fig


def create_state_datatable_counties(state_name):
    df_counties_data_table = df_complete_counties_agg[df_complete_counties_agg['State/Territory'] == state_name].\
                                 loc[:, ['County-State', 'confirmed', 'deaths', 'Death Rate (%)', 'Population', 'Cases per 1000']]
    df_counties_data_table['Death Rate (%)'] = df_counties_data_table['Death Rate (%)'].div(100)

    return df_counties_data_table


layout = html.Div([
    html.Div([
        html.Br(),
        dcc.Dropdown(
            id='t2_covid_us_map_dropdown',
            options=[
                {'label': 'Confirmed Cases', 'value': 'confirmed'},
                {'label': 'Deaths', 'value': 'deaths'},
                {'label': 'Cases per 1000', 'value': 'Cases per 1000'},
                {'label': 'Death Rate (%)', 'value': 'Death Rate (%)'},
            ],
            value='confirmed',
            clearable=False)
    ], style={'width': '20%', 'margin-left': '120px', 'padding': 10}),
    html.Div([
        dcc.Graph(
            id='t2_covid_counties_heatmap',
            figure=create_us_bubble_map_counties('confirmed')
        )
    ]),
    html.Br(),
    html.Br(),
    html.Div([
        dcc.Dropdown(
            id='t2_geo_select_state_show_counties',
            options=[{'label': i, 'value': i} for i in df_state_location['State/Territory'].unique()],
            value='California',
            clearable=False
        )
    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'margin-left': '120px', 'width': '15%', 'padding': 10}),
    html.Div([
        dcc.Dropdown(
            id='t2_select_metric_show_counties',
            options=[
                {'label': 'Confirmed Cases', 'value': 'confirmed'},
                {'label': 'Deaths', 'value': 'deaths'},
                {'label': 'Cases per 1000', 'value': 'Cases per 1000'},
                {'label': 'Death Rate (%)', 'value': 'Death Rate (%)'},
            ],
            value='confirmed',
            clearable=False
        )
    ], style={'display': 'inline-block', 'width': '15%', 'padding': 10}),
    html.Div([
        dbc.Button(
            'Submit',
            id='t2_submit_button',
            n_clicks=0,
            color='secondary',
            className='mr-1'
        )
    ], style = {'display': 'inline-block', 'verticalAlign': 'top', 'padding': 10}),
    dbc.Row(
        [
            dbc.Col(
                dcc.Graph(
                    id='t2_geo_state_map_show_counties',
                    figure=create_state_map_counties('California', 'confirmed')
                )
            ),
            dbc.Col(
                dcc.Graph(
                    id='t2_select_state_line_chart',
                    figure=create_state_line_counties('California', 'Confirmed Cases')
                )
            )
        ]
    ),
    html.Br(),
    html.Div([
        dash_table.DataTable(
            id = 't2_state_counties_datatable',
            columns = [
                {'name': 'County', 'id': 'County-State'},
                {'name': 'Cases', 'id': 'confirmed', 'type': 'numeric', 'format': Format(group = ',')},
                {'name': 'Deaths', 'id': 'deaths', 'type': 'numeric', 'format': Format(group = ',')},
                {'name': 'Cases/1000', 'id': 'Cases per 1000', 'type': 'numeric', 'format': Format(group = ',')},
                {'name': 'Death Rate', 'id': 'Death Rate (%)', 'type': 'numeric',
                 'format': FormatTemplate.percentage(2)},
                {'name': 'Population', 'id': 'Population', 'type': 'numeric', 'format': Format(group = ',')},
            ],
            fixed_rows = {'headers': True},
            style_table = {'width': '1600px', 'padding-left': 100, 'overflowX': 'auto'},
            data = create_state_datatable_counties('California').to_dict('records'),
            sort_action = 'native',
            style_cell = {'fontSize': 16, 'textAlign': 'left'},
            style_header = {
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold',
            },
            style_cell_conditional = [
                {'if': {'column_id': 'State/Territory'},
                 'width': '20%'},
                {'if': {'column_id': 'Death Rate (%)'},
                 'width': '20%'}
            ]
        )
    ]),
    html.Br()
])


@app.callback(Output('t2_covid_counties_heatmap', 'figure'),
              [Input('t2_covid_us_map_dropdown', 'value')])
def update_bubble_heatmap_counties(selected_metric):
    fig = create_us_bubble_map_counties(selected_metric)
    return fig


@app.callback(Output('t2_geo_state_map_show_counties', 'figure'),
              [Input('t2_submit_button', 'n_clicks')],
              [State('t2_geo_select_state_show_counties', 'value'),
               State('t2_select_metric_show_counties', 'value')])
def update_state_counties_map(n_clicks, state_name, metric_name):
    fig = create_state_map_counties(state_name, metric_name)
    return fig


@app.callback(Output('t2_select_state_line_chart', 'figure'),
              [Input('t2_submit_button', 'n_clicks')],
              [State('t2_geo_select_state_show_counties', 'value'),
               State('t2_select_metric_show_counties', 'value')])
def update_state_counties_line(n_clicks, state_name, metric_name):
    fig = create_state_line_counties(state_name, metric_name)
    return fig


@app.callback(Output('t2_state_counties_datatable', 'data'),
              [Input('t2_submit_button', 'n_clicks')],
              [State('t2_geo_select_state_show_counties', 'value')])
def update_state_counties_datatable(n_clicks, state_name):
    data = create_state_datatable_counties(state_name).to_dict('records')
    return data
