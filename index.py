import pandas as pd
import dash_table
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# import all apps into index.py
from app import app
from apps import app_counties, app_states

''' 
    Further reading on multi-page Dash apps - https://dash.plotly.com/urls
'''

# CSS styling for tabs - Tab1: National & States and Tab2: Counties under dcc.Tabs()
tabs_styles = {
    'height': '60px',
    'margin-bottom': '50px',
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '10px',
    'fontWeight': 'bold',
    'fontSize': 28,
}
tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'lightslategray',
    'color': 'white',
    'padding': '10px',
    'fontSize': 28,
}

# title for the dashboard and used in datatable id='index_title'
df_title = pd.DataFrame({'Title': ['COVID-19 United States Tracker']})

app.layout = html.Div([
    html.Div([
        dash_table.DataTable(
            id='index_title',
            columns=[{'name': i, 'id': i} for i in df_title.columns],
            data=df_title.to_dict('records'),
            style_header = {'display': 'none'},
            style_cell = {'fontSize': 48, 'textAlign': 'left', 'fontWeight': 'bold',
                          'font-family': 'sans-serif', 'border': '1px solid white'},
            style_table = {'padding-left': 10}
        )
    ]),
    dcc.Tabs(id='tabs-styled-with-inline',
             value='tab-1',
             children=[
                 dcc.Tab(label='National & States', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                 dcc.Tab(label='Counties', value='tab-2', style=tab_style, selected_style=tab_selected_style),
             ],
             style=tabs_styles),
    html.Br(),
    html.Div(id='tabs-content-inline')
])


@app.callback(Output('tabs-content-inline', 'children'),
              [Input('tabs-styled-with-inline', 'value')])
def display_page(tab):
    if tab == 'tab-1':
        return app_states.layout
    elif tab == 'tab-2':
        return app_counties.layout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
