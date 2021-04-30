# Paquetes pyhon para diversos propósitos
import numpy as np
import pandas as pd
import boto3
import json, pickle
import datetime
import psycopg2
import socket
from sodapy import Socrata

# Funciones importadas de data-product-architecture/src/utils/general.py
# para lectura de credenciales, apis y funciones auxiliares
import src.utils.general as general


# Constantes importadas de data-product-architecture/src/utils/constants.py
# para que el usuario ingrese sus propias credenciales, bucket de s3
from src.utils.constants import NOMBRE_BUCKET, FOOD_CONECTION, ID_SOCRATA, PATH_CREDENCIALES


def get_client(cred_path=PATH_CREDENCIALES):
    """
    Esta función regresa un cliente que se puede conectar a la API de inspecciones
    de establecimiento dándole un token previamente generado.
    """

    token = general.get_api_token(cred_path)
    client = Socrata(FOOD_CONECTION, token)

    return client


def ingesta_inicial(client):
    """
    Esta función recibe como parámetros el cliente 	con el que nos podemos comunicar
    con la API, y el límite de registros que queremos obtener al llamar a la API.
    Regresa una lista de los elementos que la API regresó.
    """

    socrata_id = ID_SOCRATA
    file_name = 'historic_inspections-' + str(datetime.date.today()) + '.pkl'

    results = client.get_all(socrata_id)

    data = []

    for line in results:
        data.append(line)

    with open(file_name, 'wb') as pkl:
        pickle.dump(data, pkl)

    return file_name
