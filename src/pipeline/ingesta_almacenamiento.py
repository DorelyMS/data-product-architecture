import boto3
import csv
import json
import os
import pickle
from sodapy import Socrata
# import /src/utils/general as general
import sys
sys.path.insert(1, 'C:/Users/GZARAZUA/PycharmProjects/data-product-architecture/src/utils')
import general

def get_client(cred_path):
	"""
	Esta función regresa un cliente que se puede conectar a la API de inspecciones
	de establecimiento dándole un token previamente generado.
	"""

	token = general.get_api_token(cred_path)
	client = Socrata("data.cityofchicago.org", token)

	return client

def ingesta_inicial(client, limit=None):
	"""
	Esta función recibe como parámetros el cliente 	con el que nos podemos comunicar 
	con la API, y el límite de registros que queremos obtener al llamar a la API. 
	Regresa una lista de los elementos que la API regresó.
	"""

	socrata_id = "4ijn-s7e5"

	if limit is None:

		results = client.get_all(socrata_id)

		data = []

		for line in results:
			data.append(line)

		with open('datos.pkl', 'wb') as pkl:
			pickle.dump(data, pkl)

	else:

		results = client.get(socrata_id, limit=limit)

		with open('datos.pkl', 'wb') as pkl:
			pickle.dump(results, pkl)


	return None

def get_s3_resource(cred_path):
	"""
	Esta función regresa un resource de S3 para poder guardar datos en el bucket
	"""

	s3_creds = general.get_s3_credentials(cred_path)

	session = boto3.Session(
	    aws_access_key_id=s3_creds['aws_access_key_id'],
	    aws_secret_access_key=s3_creds['aws_secret_access_key']
	)
	s3 = session.client('s3')

	return s3

def guardar_ingesta(bucket, bucket_path, data, cred_path):
	"""
	Esta función recibe como parámetros el nombre de tu bucket de S3, 
	la ruta en el bucket en donde se guardarán los datos 
	y los datos ingestados en pkl.
	"""

	s3 = get_s3_resource(cred_path)

	file_name = bucket_path + data.split(sep='/')[-1]

	s3.upload_file(data, bucket, file_name)


if __name__ == "__main__":
	

	client = get_client("C:/Users/GZARAZUA/PycharmProjects/data-product-architecture/conf/local/credentials.yaml")

	ingesta_inicial(client,5)

	guardar_ingesta('data-product-architecture-4',
	 'ingestion/test-memo/',
	  './datos.pkl',
	  'C:/Users/GZARAZUA/PycharmProjects/data-product-architecture/conf/local/credentials.yaml')
