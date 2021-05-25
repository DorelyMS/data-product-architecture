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

    predictions = pd.read_sql_query("select score_0, score_1 from pred.predicciones;", con=conn)
    conn.close()

    fun_monit(predictions)


def fun_monit(predictions):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    colors = {
        'background': '#111111',
        'text': '#7FDBFF'
    }


    # assume you have a "long-form" data frame
    # see https://plotly.com/python/px-arguments/ for more options
    df = predictions
    # df = pd.DataFrame({
    #    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    #    "Amount": [4, 1, 2, 2, 4, 5],
    #    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
    # })

    fig = px.histogram(df, x='score_0',
                       # y="Amount", color="City",
                       barmode="overlay")

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
        html.H1(
            children='Histograma de Scores',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),

        html.Div(children='Score_0', style={
            'textAlign': 'center',
            'color': colors['text']
        }),

        dcc.Graph(
            id='example-graph-2',
            figure=fig
        )
    ])
    app.run_server(host='0.0.0.0', port=8050,debug=True)


if __name__ == "__main__":
    auxiliar2()

