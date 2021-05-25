# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import psycopg2, pickle
import src.utils.general as general
from src.utils.constants import NOMBRE_BUCKET, ID_SOCRATA, PATH_CREDENCIALES
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd


def auxiliar2():
    creds = general.get_db_credentials(PATH_CREDENCIALES)
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    # port = creds['port']

    conn = psycopg2.connect(dbname=database,
                            user=user,
                            host=host,
                            password=password)

    # Conexion postgres

    score_pred = pd.read_sql_query("select * from api.monitoreo;", con=conn)
    score_mod = pd.read_sql_query("select score_0, score_1 from models.predicciones_train;", con=conn)
    conn.close()

    fun_monit(score_pred, score_mod)


def fun_monit(score_pred, score_mod):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    colors = {
        'background': '#111111',
        'text': '#7FDBFF'
    }


    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    df1 = score_mod
    df2 = score_pred
    

    fig1 = px.histogram(df1, x='score_1',
                       barmode="overlay")

    fig2 = px.histogram(df2, x='score_1',
                       barmode="overlay")
    
    fig1.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    fig2.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )    
    
    
    app.layout = html.Div(children=[
        # All elements from the top of the page
        html.Div([
            html.H1(children='Histograma de Scores Modelo'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),

            dcc.Graph(
                id='graph1',
                figure=fig1
            ),  
        ]),
        # New Div for all elements in the new 'row' of the page
        html.Div([
            html.H1(children='Histograma de Scores Predicciones'),

            html.Div(children='''
                Dash: A web application framework for Python.
            '''),

            dcc.Graph(
                id='graph2',
                figure=fig2
            ),  
        ]),
    ])
    app.run_server(host='0.0.0.0', port=8050,debug=True)


if __name__ == "__main__":
    auxiliar2()

