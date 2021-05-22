# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import numpy as np
import pandas as pd
import psycopg2, pickle
import boto3
import src.utils.general as general
from src.utils.constants import NOMBRE_BUCKET, ID_SOCRATA, PATH_CREDENCIALES

import luigi.contrib.s3


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
    port = creds['port']

    conn = psycopg2.connect(dbname = database,
        user = user,
        host = host,
        password = password)

    aux_path = 'modelos/modelo_seleccionado/'
    output_path = 's3://' + NOMBRE_BUCKET + "/" + aux_path

    s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
    client = luigi.contrib.s3.S3Client(
        aws_access_key_id=s3_creds['aws_access_key_id'],
        aws_secret_access_key=s3_creds['aws_secret_access_key'])
    gen = client.list(output_path)
    file_name = next(gen)

    session = boto3.session.Session(region_name='us-west-2')
    s3client = session.client('s3', config=boto3.session.Config(signature_version='s3v4'),
                             aws_access_key_id=s3_creds['aws_access_key_id'],
                             aws_secret_access_key=s3_creds['aws_secret_access_key'])

    path_s3 = aux_path + file_name

    response = s3client.get_object(Bucket=NOMBRE_BUCKET, Key=path_s3)
    body_string = response['Body'].read()
    model = pickle.loads(body_string)
    model = pickle.loads(model)

    # Conexion postgres
    predictions = pd.read_sql_query("select score_0, score_1 from pred.predicciones;", con=conn)
    conn.close()

    fun_monit(predictions)



def fun_monit(predictions, bias_fair):
    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = predictions
#df = pd.DataFrame({
#    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#    "Amount": [4, 1, 2, 2, 4, 5],
#    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
#})

fig = px.histogram(df, x='Scores', 
                   #y="Amount", color="City", 
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

#if __name__ == '__main__':
#    app.run_server(debug=True)
    
    


if __name__=="__main__":

    auxiliar2()







