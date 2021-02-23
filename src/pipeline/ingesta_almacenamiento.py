import boto3
import csv
import json
import os
import pickle
from sodapy import Socrata
# import /src/utils/general as general
import sys
sys.path.insert(1, '/home/bruno/Repos/data-product-architecture-trabajo/src/utils')
import general
import datetime

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
	file_name = 'historic_inspections-' + str(datetime.date.today()) + '.pkl'

	if limit is None:

		results = client.get_all(socrata_id)

		data = []

		for line in results:
			data.append(line)

		with open(file_name, 'wb') as pkl:
			pickle.dump(data, pkl)

	else:

		results = client.get(socrata_id, limit=limit)

		with open(file_name, 'wb') as pkl:
			pickle.dump(results, pkl)

	return file_name

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

def prueba_guardar_ingesta(bucket, bucket_path, data, cred_path):
	socrata_id = "4ijn-s7e5"

	if limit is None:
		results = client.get_all(socrata_id)
		data = []
		for line in results:
			data.append(line)
		client.put_object(Body=b'data', Bucket='bucket_name', Key='key/key.txt')
		# with open('datos.pkl', 'wb') as pkl:
		# 	pickle.dump(data, pkl)

	else:
		results = client.get(socrata_id, limit=limit)
		client.put_object(Body=b'data', Bucket='bucket_name', Key='key/key.txt')
		# with open('datos.pkl', 'wb') as pkl:
		# 	pickle.dump(results, pkl)

	s3 = get_s3_resource(cred_path)

	# file_name = bucket_path + data.split(sep='/')[-1]
	file_name=bucket_path + 'ingesta-inicial-' + str(datetime.date.today())

	s3.upload_file(data, bucket, file_name)


def guardar_ingesta(bucket, bucket_path, data, cred_path):
	"""
	Esta función recibe como parámetros el nombre de tu bucket de S3, 
	la ruta en el bucket en donde se guardarán los datos 
	y los datos ingestados en pkl.
	"""

	s3 = get_s3_resource(cred_path)

	file_name = bucket_path + data.split(sep='/')[-1]
	#file_name = bucket_path + 'ingesta-inicial-' + str(datetime.date.today())

	s3.upload_file(data, bucket, file_name)

	os.remove(data)


def ingesta_consecutiva(cliente, fecha, limit):
	"""
	 Esta función recibe como parámetros el cliente con el que nos podemos 
	 comunicar con la API, la fecha de la que se quieren obtener nuevos datos 
	 al llamar a la API y el límite de registros para obtener de regreso.
	"""

	socrata_id = "4ijn-s7e5"
	#hoy = datetime.date.today().strftime("%Y-%m-%d")
	fecha_inicial = datetime.datetime.strptime(fecha, "%Y-%m-%d") 
	fecha_inicial = fecha_inicial- datetime.timedelta(days=7)
	fecha_inicial = fecha_inicial.strftime("%Y-%m-%d")

	file_name = 'consecutive-inspections-' + str(datetime.date.today()) + '.pkl'


	soql_query = f"inspection_date between'{fecha_inicial}' and '{fecha}'"
	print(soql_query)

	if limit is None:

		results = client.get_all(socrata_id, where=soql_query)
		data = []

		for line in results:
			data.append(line)

		with open(file_name, 'wb') as pkl:
			pickle.dump(data, pkl)

	else:

		results = client.get(socrata_id, limit=limit, where=soql_query)

		with open(file_name, 'wb') as pkl:
			pickle.dump(results, pkl)

	return file_name


if __name__ == "__main__":


	client = get_client("/home/bruno/Repos/data-product-architecture-trabajo/conf/local/credentials.yaml")

	archivo = ingesta_inicial(client,1000)

	#archivo = ingesta_consecutiva(client, '2021-02-21', 1000)

	guardar_ingesta('data-product-architecture-4',
	 'ingestion/initial/',
	  archivo,
	  '/home/bruno/Repos/data-product-architecture-trabajo/conf/local/credentials.yaml')
