import boto3
import boto3.session
import csv
import json
import os
import pickle
from sodapy import Socrata
import sys
import src.utils.general as general
import datetime
import luigi
import luigi.contrib.s3


def get_client(cred_path="./conf/local/credentials.yaml"):
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


def get_s3_resource(cred_path="./conf/local/credentials.yaml"):
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


def ingesta_consecutiva(client, fecha, limit=None):
	"""
	 Esta función recibe como parámetros el cliente con el que nos podemos
	 comunicar con la API, la fecha de la que se quieren obtener nuevos datos
	 al llamar a la API y el límite de registros para obtener de regreso.
	"""

	socrata_id = "4ijn-s7e5"
	#hoy = datetime.date.today().strftime("%Y-%m-%d")
	fecha_inicial = datetime.datetime.strptime(fecha, "%Y-%m-%d")
	fecha_inicial = fecha_inicial- datetime.timedelta(days=6)
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


def guardar_ingesta(bucket, bucket_path, data, cred_path="./conf/local/credentials.yaml"):
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


class IngTask(luigi.Task):
	"""
	Clase de Luigi encargada de la ingesta (descarga) de la base de datos, ya sea:
	- historica (historic) que trae todos las inspecciones hasta la fecha de ingesta
	que se pase como parámetro
	- consecutiva (consecutive) obtiene todos las inspecciones de los 7 días anteriores a
	la fecha de ingesta
	Las bases se descargan en la carpeta /conf/base/ separadas por tipo de ingesta, año y mes
	"""
	socrata_id = "4ijn-s7e5"
	limit = luigi.Parameter(default=None)
	date_ing = luigi.DateParameter(default=datetime.date.today())
	type_ing = luigi.Parameter(default='consecutive')

	def run(self):
		client = get_client()

		if self.type_ing == 'consecutive':
			init_date = self.date_ing - datetime.timedelta(days=6)
			soql_query = "inspection_date between'{}' and '{}'".format(init_date.strftime("%Y-%m-%d"), self.date_ing.strftime("%Y-%m-%d"))
			data = client.get(self.socrata_id, limit=self.limit, where=soql_query)

		else:
			init_date = '1900-01-01'
			soql_query = "inspection_date between'{}' and '{}'".format(init_date, self.date_ing.strftime("%Y-%m-%d"))
			results = client.get_all(self.socrata_id, where=soql_query)
			data = []
			for line in results:
				data.append(line)

		with self.output().open('w') as outfile:
			pickle.dump(data, outfile)

	def output(self):
		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'

		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'

		local_path = './conf/base/' + aux_path + file_name
		return luigi.local_target.LocalTarget(local_path, format=luigi.format.Nop)


class AlmTask(luigi.Task):
	"""
	Clase de Luigi encargada de subir la base requerida a un bucket de s3 especificado
	(nube AWS), según sea historic/consecutive y que corresponde a la fecha de pasada
	como parámetro (fecha de ingestión). Como requisito se debe tener la base, que es creada con IngTask
	"""
	bucket_name = luigi.Parameter(default='data-product-architecture-4')
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	def requires(self):
		return IngTask(date_ing=self.date_ing, type_ing=self.type_ing)

	def run(self):
		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'

		output_path = 's3://' + self.bucket_name + '/' + aux_path + file_name
		local_path = './conf/base/' + aux_path + file_name

		s3_creds = general.get_s3_credentials("./conf/local/credentials.yaml")
		client = luigi.contrib.s3.S3Client(
		aws_access_key_id=s3_creds['aws_access_key_id'],
		aws_secret_access_key=s3_creds['aws_secret_access_key'])

		client.put(local_path, output_path)

	def output(self):
		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'

		output_path = 's3://' + self.bucket_name + '/' + aux_path + file_name

		s3_creds = general.get_s3_credentials("./conf/local/credentials.yaml")
		client = luigi.contrib.s3.S3Client(
		aws_access_key_id=s3_creds['aws_access_key_id'],
		aws_secret_access_key=s3_creds['aws_secret_access_key'])

		return luigi.contrib.s3.S3Target(path=output_path, client=client)
