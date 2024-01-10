## Librerías de dash, son las que permiten crear la aplicación
import dash
from dash import no_update
from dash import Dash, dash_table, dcc, callback, Output, Input, html, State

## Librerías más específicas de dash
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto

## Librería de visualización
import plotly.express as px
import plotly.graph_objects as go

## Librería para el manejo de datos
import pandas as pd

import numpy as np

## Librerías para trabajar datos temporales
from datetime import datetime
from datetime import timedelta
from datetime import date

## Librerías para trabajar con archivos e interactuar con GitHub.
from io import BytesIO, StringIO

from github import Github
from github import Auth

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

access_tocken = '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' 

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])

server = app.server

theme = {
    'dark': True,
    'detail': '#007439',
    'primary': '#00EA64',
    'secondary': '#6E6E6E',
}

############## extraer datos ################

df = pd.read_excel('https://github.com/dashanid/dashboard_zendesk/raw/main/descargaTicket.xlsx', sheet_name = 'Hoja 1').loc[lambda x: (x['cuenta_que_recibe'] != 'latindex@anid.cl') & (x['cuenta_que_recibe'] != 'issn@anid.cl')]

## preparación de los dropdown

cuentas = list(df.groupby('cuenta_que_recibe').size().reset_index(name = 'count')['cuenta_que_recibe'])

opciones = [{'label': f'{cuenta}', 'value': cuenta} for cuenta in cuentas]

app.layout = dbc.Container([
    
    ############ Título del dashboard ###############
    
    html.Div(className='row', children='Panel de control de tickets.',
             style={'textAlign': 'center', 'color': 'black', 'fontSize': 30}),

    ############ Subir nuevos archivos #############

    dcc.Upload(
        id = 'upload-data',
        children = html.Div([
            'Para actualizar los datos arrastra o selecciona el archivo'
        ]),
        style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            }
    ),
    
    ########### Aquí van los gráficos ###############
    
    dbc.Row([
        
        ############ Gráfico de consultas por cuenta ##############
        
        dbc.Col(
            dcc.Graph(
                figure = px.pie(
                    df.groupby('cuenta_que_recibe').size().reset_index(name = 'número de consultas'),
                    names = 'cuenta_que_recibe',
                    values = 'número de consultas',
                    title = 'Número de consultas por cuenta'
                ),
                style = {'height': '400px', 'width': '600px'}
            ),
            width = 6
        ),
        
        ############ Gráfico de porcentaje por tipo de pregunta ################
        
        dbc.Col([
            dcc.Graph(id = 'graph-1'),
            dcc.Dropdown(
                id = 'select-1',
                options = opciones,
                value = None
            ),
            dcc.DatePickerRange(
                minimum_nights=5,
                clearable=True,
                with_portal=True,
                start_date = date(2023, 1, 1),
                end_date = date(2023, 11, 27),
                id = 'date-1'
            )],
            width = 6
        )
    ]),
    dbc.Row([
        
        ############ gráfico de respuestas por persona ################
        
        dbc.Col([
            dcc.Graph(id = 'graph-2'),
            dcc.Dropdown(
                id = 'select-2',
                options = opciones,
                value = None
            ),
            dcc.DatePickerRange(
                minimum_nights=5,
                clearable=True,
                with_portal=True,
                start_date = date(2023, 1, 1),
                end_date = date(2023, 11, 27),
                id = 'date-2'
            )],
            width = 6
        ),
        
        ############ Gráfico de consultas respondidas a tiempo #################
        
        dbc.Col([
            dcc.Graph(id = 'graph-3'),
            dcc.Dropdown(
                id = 'select-3',
                options = opciones,
                value = None
            ), 
            dcc.DatePickerRange(
                minimum_nights=5,
                clearable=True,
                with_portal=True,
                start_date = date(2023, 1, 1),
                end_date = date(2023, 11, 27),
                id = 'date-3'
            )],
            width = 6
        )
    ])
])

@app.callback(
    [Output('graph-1', 'figure'),
     Output('graph-2', 'figure'),
     Output('graph-3', 'figure')],
    [Input('select-1', 'value'),
     Input('select-2', 'value'),
     Input('select-3', 'value'),
     Input('date-1', 'start_date'),
     Input('date-1', 'end_date'),
     Input('date-2', 'start_date'),
     Input('date-2', 'end_date'),
     Input('date-3', 'start_date'),
     Input('date-3', 'end_date'),
     Input('upload-data', 'contents'),
     Input('upload-data', 'filename')]
)

def update_output(cuenta_1, cuenta_2, cuenta_3, start_date_1, end_date_1, start_date_2, end_date_2, start_date_3, end_date_3, data, file_name):
    
    ## Cálculo del cumplimiento del SLA

    # serie_actualizada = pd.to_datetime(df_solved['fecha_actualizacion'], errors = 'coerce')
    # serie_creada = pd.to_datetime(df_solved['fecha_creacion'], errors = 'coerce')
    # dt = df_solved.loc[lambda x: (start_date < pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d'))) &
    # (pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d')) < end_date)]

    ## Filtros para cada df según las fechas seleccionadas. Si no se selecciona fecha, se queda sin filtrar.

    global df
    
    if data:
        try:
            content_type, content_string = data.split(',')
            decoded = base64.b64decode(content_string)
            if 'xlsx' in file_name:
                df = pd.read_excel(BytesIO(decoded), sheet_name = 'Hoja 1')
            else:
                df = pd.read_csv(StringIO(decoded.decode('utf-8')))
            csv_encoded = df.to_csv(index = False).encode('utf-8')
            auth = Auth.Token(access_token)
            g = Github(auth = auth)
            repo = g.get_repo('dashanid/data_monitoreo')
            contents = repo.get_contents('descargaTicket.csv')
            repo.update_file('descargaTicket.csv', f'modificacion a traves de python con fecha {str(date.today())}',decoded, contents.sha)        
            g.close
        
        except Exception as e:
                print(f"An error occurred: {e}")
                children = [html.Div('Error processing file. Please try again.', style={'color': 'red'})]

    df_solved = df.loc[lambda x: x['estado'] == 'Cerrado']

    if (start_date_1 != None) and  (end_date_1 != None):
        df_1 = df_solved.loc[lambda x: (start_date_1 < pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d'))) &
        (pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d')) < end_date_1)]
    else:
        df_1 = df_solved

    if (start_date_2 != None) and  (end_date_2 != None):
        df_2 = df_solved.loc[lambda x: (start_date_2 < pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d'))) &
        (pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d')) < end_date_2)]
    else:
        df_2 = df_solved
    
    if (start_date_3 != None) and  (end_date_3 != None):
        dt = df_solved.loc[lambda x: (start_date_3 < pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d'))) &
        (pd.to_datetime(pd.to_datetime(x['fecha_creacion'], errors = 'coerce').dt.strftime('%Y-%m-%d')) < end_date_3)]
    else:
        dt = df_solved
    
    # df_solved = df_solved.assign(in_time=(serie_actualizada - serie_creada).dt.days < 5)
    
    ## Filtro de los df según cuenta, en caso de que no se seleccione cuenta, no se filtra.

    if cuenta_1 == None:
        df_clas = df_1.groupby('clasificación_pregunta').size().reset_index(name = 'número')
    else:
        df_clas = df_1.loc[lambda x: x['cuenta_que_recibe'] == cuenta_1].groupby('clasificación_pregunta').size().reset_index(name = 'número')
    
    if cuenta_2 == None:
        df_quien_contesto = df_2.groupby('quien_respondio').size().reset_index(name = 'Numero de respuestas')
    else:
        df_quien_contesto = df_2.loc[lambda x: x['cuenta_que_recibe'] == cuenta_2].groupby('quien_respondio').size().reset_index(name = 'Numero de respuestas')
    if cuenta_3 == None:
        df_a_tiempo = dt.groupby('Cumplimiento SLA').size().reset_index(name = 'Número')
    else:
        df_a_tiempo = dt.loc[lambda x: x['cuenta_que_recibe'] == cuenta_3].groupby('Cumplimiento SLA').size().reset_index(name = 'Número')
    
    ## Creación de los 3 gráficos faltantes con la data procesada

    fig_1 = px.pie(
                    df_clas,
                    values = 'número',
                    names = 'clasificación_pregunta',
                    title = 'Distribución de preguntas por clasificación'
                )
    fig_2 = px.bar(
                    df_quien_contesto,
                    x = 'quien_respondio',
                    y = 'Numero de respuestas',
                    title = 'Número de respuestas por persona'
                )
    fig_3 = px.pie(
                    df_a_tiempo,
                    values = 'Número',
                    names = 'Cumplimiento SLA',
                    title = 'Cumplimiento SLA',
                    category_orders={'Cumplimiento SLA': ['Cumple', 'No cumple']}
                )
    return fig_1, fig_2, fig_3

if __name__ == '__main__':
    app.run_server(debug=True)