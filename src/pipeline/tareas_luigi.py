import numpy as np
import pandas as pd
import boto3
import boto3.session
import json
import datetime
import psycopg2
import socket

import pickle
from sodapy import Socrata
import src.utils.general as general
from src.utils.constants import NOMBRE_BUCKET, ID_SOCRATA, PATH_CREDENCIALES
from src.etl.cleaning import cleaning
from src.etl.feature_engineering import feature_engineering

import luigi
import luigi.contrib.s3
from luigi.contrib.postgres import CopyToTable, PostgresQuery



def get_client(cred_path=PATH_CREDENCIALES):
	"""
	Esta función regresa un cliente que se puede conectar a la API de inspecciones
	de establecimiento dándole un token previamente generado.
	"""

	token = general.get_api_token(cred_path)
	client = Socrata("data.cityofchicago.org", token)

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


def get_s3_resource(cred_path=PATH_CREDENCIALES):
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


class IngTask(luigi.Task):
	"""
	Clase de Luigi encargada de la ingesta (descarga) de la base de datos, ya sea:
	- historica (historic) que trae todos las inspecciones hasta la fecha de ingesta
	que se pase como parámetro
	- consecutiva (consecutive) obtiene todos las inspecciones de los 7 días anteriores a
	la fecha de ingesta
	Las bases se descargan en la carpeta /conf/base/ separadas por tipo de ingesta, año y mes
	"""
	socrata_id = ID_SOCRATA
	date_ing = luigi.DateParameter(default=datetime.date.today())
	type_ing = luigi.Parameter(default='consecutive')

	def run(self):
		client = get_client()

		if self.type_ing == 'consecutive':
			init_date = self.date_ing - datetime.timedelta(days=6)
			soql_query = "inspection_date between'{}' and '{}'".format(init_date.strftime("%Y-%m-%d"), self.date_ing.strftime("%Y-%m-%d"))
			results = client.get_all(self.socrata_id, where=soql_query)

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


class IngMetaTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de Ingesta
	"""	

	fecha_ejecucion = datetime.datetime.now()
	tarea = "Ingestion"
	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	creds = general.get_db_credentials(PATH_CREDENCIALES)

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'meta.food_metadata'

	columns = [
	("fecha_ejecucion", "timestamp"),
	("tarea", "text"),
	("usuario", "text"),
	("metadata", "jsonb")
	]

	def requires(self):
		return IngTask(date_ing=self.date_ing, type_ing=self.type_ing)

	def rows(self):

		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		local_path = './conf/base/' + aux_path + file_name
		with open(local_path, 'rb') as p:
			file = pickle.load(p)

		metadata = {
		'type_ing': self.type_ing,
		'date_ing': self.date_ing.strftime("%Y-%m-%d"),
		'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
		'num_registros': len(file),
		'variables': list(file[0].keys())
		}

		print("Ingestion metadata")
		print(self.fecha_ejecucion)
		print(self.tarea)
		print(metadata)

		r = [
		(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
		]
		for element in r:
			yield element


class AlmTask(luigi.Task):
	"""
	Clase de Luigi encargada de subir la base requerida a un bucket de s3 especificado
	(nube AWS), según sea historic/consecutive y que corresponde a la fecha de pasada
	como parámetro (fecha de ingestion). Como requisito se debe tener la base, que es creada con IngTask
	"""
	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	def requires(self):
		return IngMetaTask(date_ing=self.date_ing, 
			type_ing=self.type_ing,
			bucket_name=self.bucket_name)

	def run(self):
		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'

		output_path = 's3://' + self.bucket_name + '/' + aux_path + file_name
		local_path = './conf/base/' + aux_path + file_name

		s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
		client = luigi.contrib.s3.S3Client(
		aws_access_key_id=s3_creds['aws_access_key_id'],
		aws_secret_access_key=s3_creds['aws_secret_access_key'])

		client.put(local_path, output_path)

		# with self.output()

	def output(self):
		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'

		output_path = 's3://' + self.bucket_name + '/' + aux_path + file_name

		s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
		client = luigi.contrib.s3.S3Client(
		aws_access_key_id=s3_creds['aws_access_key_id'],
		aws_secret_access_key=s3_creds['aws_secret_access_key'])

		return luigi.contrib.s3.S3Target(path=output_path, client=client, format=luigi.format.Nop)


class AlmMetaTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de Ingesta
	"""	

	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	fecha_ejecucion = datetime.datetime.now()
	tarea = "Almacenamiento"

	creds = general.get_db_credentials(PATH_CREDENCIALES)

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'meta.food_metadata'

	columns = [
	("fecha_ejecucion", "timestamp"),
	("tarea", "text"),
	("usuario", "text"),
	("metadata", "jsonb")
	]

	def requires(self):
		return AlmTask(bucket_name=self.bucket_name,
			type_ing=self.type_ing,
			date_ing=self.date_ing)

	def rows(self):


		metadata = {
		'type_ing': self.type_ing,
		'date_ing': self.date_ing.strftime("%Y-%m-%d"),
		'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
		'bucket': self.bucket_name,
		'host': socket.gethostbyname(socket.gethostname())
		}

		print("Almacenamiento metadata")
		print(self.fecha_ejecucion)
		print(self.tarea)
		print(metadata)

		r = [
		(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
		]
		for element in r:
			yield element

class PrepTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de Ingesta
	"""	

	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	creds = general.get_db_credentials(PATH_CREDENCIALES)

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'clean.clean_food_data'

	columns = [("inspection_id", "integer"),
	# ("dba_name", "text"),
	("aka_name", "text"),
	("license_", "integer"),
	("facility_type", "text"),
	("risk", "integer"),
	("address", "text"),
	("zip", "integer"),
	("inspection_date", "date"),
	("inspection_type", "text"),
	("results", "text"),
	("violations", "text"),
	("latitude", "double precision"),
	("longitude", "double precision")
	]

	col_dic = dict(columns)

	def requires(self):
		return AlmMetaTask(bucket_name=self.bucket_name,
			type_ing=self.type_ing,
			date_ing=self.date_ing)

	def rows(self):

		file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
		if self.type_ing == 'consecutive':
		    aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		else:
		    aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
		local_path = './conf/base/' + aux_path + file_name
		with open(local_path, 'rb') as p:
			file = pickle.load(p)

		num_registros= len(file),
		variables= list(file[0].keys())

		for p in file:
			d = dict(self.columns)
			for k in d: d[k] = None
			d['city'] = 'chicago'
			d['state'] = 'il'
			d.update(p)
			try:
				d.pop('location')
			except:
				pass
			try:
				d.pop('dba_name')
			except:
				pass
			df = pd.DataFrame(d, index = [0])
			df = cleaning(df)

			try:
				yield tuple(df.values[0])
			except:
				pass


class PrepMetaTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de Ingesta
	"""	

	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	fecha_ejecucion = datetime.datetime.now()
	tarea = "Preprocesamiento"

	creds = general.get_db_credentials(PATH_CREDENCIALES)

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'meta.food_metadata'

	columns = [
	("fecha_ejecucion", "timestamp"),
	("tarea", "text"),
	("usuario", "text"),
	("metadata", "jsonb")
	]

	def requires(self):
		return PrepTask(bucket_name=self.bucket_name,
			type_ing=self.type_ing,
			date_ing=self.date_ing)

	def rows(self):

		metadata = {
		'type_ing': self.type_ing,
		'date_ing': self.date_ing.strftime("%Y-%m-%d"),
		'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
		}

		print("Almacenamiento metadata")
		print(self.fecha_ejecucion)
		print(self.tarea)
		print(metadata)

		r = [
		(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
		]
		for element in r:
			yield element



class FeatEngTask(CopyToTable):

	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())


	#Para conectarse a la base
	creds = general.get_db_credentials(PATH_CREDENCIALES)
	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'clean.feature_eng'

	columns = [
		("inspection_id", "integer"),
		#("dba_name", "text"),
		("aka_name", "text"),
		("license_num", "integer"),
		("facility_type", "text"),
		("risk", "integer"),
		("address", "text"),
		("zip", "text"),
		("inspection_date", "date"),
		("inspection_type", "text"),
		("results", "text"),
		("violations", "text"),
		("latitude", "double precision"),
		("longitude", "double precision"),
		("inspection_year", "integer"),
		("pass", "text"),
		("days_since_last_inspection", "integer"),
		("approved_insp", "integer"),
		("num_viol_last_insp", "integer"),
		("mon", "text"),
		("tue", "text"),
		("wed", "text"),
		("thu", "text"),
		("fri", "text"),
		("sat", "text"),
		("sun", "text"),
		("ene", "text"),
		("feb", "text"),
		("mar", "text"),
		("abr", "text"),
		("may", "text"),
		("jun", "text"),
		("jul", "text"),
		("ago", "text"),
		("sep", "text"),
		("oct", "text"),
		("nov", "text"),
		("dic", "text"),
		("inspection_month", "integer")
	]

	def requires(self):
		return PrepMetaTask(bucket_name=self.bucket_name,
			type_ing=self.type_ing,
			date_ing=self.date_ing)

	def rows(self):

		query = "SELECT * FROM clean.clean_food_data;"

		conn = psycopg2.connect(dbname = self.database,
			user = self.user,
			host = self.host,
			password = self.password)
		df = pd.read_sql_query(query, con=conn)
		df = feature_engineering(df)

		cursor = conn.cursor()
		cursor.execute("drop table if exists clean.feature_eng;")
		conn.commit()
		conn.close()



		for r in df.itertuples():
			res = r[1:]
			yield res



class FeatEngMetaTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de FeatEngTask
	"""

	bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	fecha_ejecucion = datetime.datetime.now()
	tarea = "Feature_Engineering"

	creds = general.get_db_credentials(PATH_CREDENCIALES)

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'meta.food_metadata'

	columns = [
	("fecha_ejecucion", "timestamp"),
	("tarea", "text"),
	("usuario", "text"),
	("metadata", "jsonb")
	]

	def requires(self):
		return FeatEngTask(bucket_name=self.bucket_name,
			type_ing=self.type_ing,
			date_ing=self.date_ing)

	def rows(self):

		metadata = {
		'type_ing': self.type_ing,
		'date_ing': self.date_ing.strftime("%Y-%m-%d"),
		'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
		}

		print("Feature Engineering metadata")
		print(self.fecha_ejecucion)
		print(self.tarea)
		print(metadata)

		r = [
		(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
		]
		for element in r:
			yield element