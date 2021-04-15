import boto3
import boto3.session
import json

import pickle
from sodapy import Socrata

import src.utils.general as general
import datetime
import psycopg2
import socket

import luigi
import luigi.contrib.s3
from luigi.contrib.postgres import CopyToTable



def get_client(cred_path="./conf/local/credentials.yaml"):
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

	socrata_id = "4ijn-s7e5"
	file_name = 'historic_inspections-' + str(datetime.date.today()) + '.pkl'


	results = client.get_all(socrata_id)

	data = []

	for line in results:
		data.append(line)

	with open(file_name, 'wb') as pkl:
		pickle.dump(data, pkl)


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

# class IngMetaTask(luigi.Task):
# 	"""
# 	Clase de Luigi que guarda los metadatos de Ingesta
# 	"""	
# 	task_complete = False

# 	bucket_name = luigi.Parameter()
# 	date_ing = luigi.DateParameter()
# 	type_ing = luigi.Parameter()

# 	def requires(self):
# 		return IngTask(date_ing=self.date_ing, type_ing=self.type_ing)

# 	def run(self):
# 		metadata = {
# 		'date_ing': self.date_ing.strftime("%Y-%m-%d"),
# 		'type_ing': self.type_ing
# 		}
# 		print("Ingestion metadata")
# 		print(datetime.datetime.now())
# 		print("ingestion")
# 		print(metadata)
# 		# self.task_complete = True

# 		with self.output().open('w') as outfile:
# 				json.dump(metadata, outfile)

# 	# def complete(self):
# 	# 	return self.task_complete
# 	def output(self):
# 		 return luigi.local_target.LocalTarget("./meta.json")

class IngMetaTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de Ingesta
	"""	

	fecha_ejecucion = datetime.datetime.now()
	tarea = "Ingestion"
	bucket_name = luigi.Parameter(default='data-product-architecture-4')
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	creds = general.get_db_credentials("./conf/local/credentials.yaml")

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'meta.metadata'

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
	bucket_name = luigi.Parameter(default='data-product-architecture-4')
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

		s3_creds = general.get_s3_credentials("./conf/local/credentials.yaml")
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

		s3_creds = general.get_s3_credentials("./conf/local/credentials.yaml")
		client = luigi.contrib.s3.S3Client(
		aws_access_key_id=s3_creds['aws_access_key_id'],
		aws_secret_access_key=s3_creds['aws_secret_access_key'])

		return luigi.contrib.s3.S3Target(path=output_path, client=client, format=luigi.format.Nop)


class AlmMetaTask(CopyToTable):
	"""
	Clase de Luigi que guarda los metadatos de Ingesta
	"""	

	bucket_name = luigi.Parameter(default='data-product-architecture-4')
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	fecha_ejecucion = datetime.datetime.now()
	tarea = "Almacenamiento"

	creds = general.get_db_credentials("./conf/local/credentials.yaml")

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'meta.metadata'

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

	bucket_name = luigi.Parameter(default='data-product-architecture-4')
	type_ing = luigi.Parameter(default='consecutive')
	date_ing = luigi.DateParameter(default=datetime.date.today())

	creds = general.get_db_credentials("./conf/local/credentials.yaml")

	user = creds['user']
	password = creds['password']
	database = creds['database']
	host = creds['host']
	port = creds['port']
	table = 'clean.clean'

	columns = [("inspection_id", "text"),
	("dba_name", "text"),
	("aka_name", "text"),
	("license_", "text"),
	("facility_type", "text"),
	("risk", "text"),
	("address", "text"),
	("city", "text"),
	("state", "text"),
	("zip", "text"),
	("inspection_date", "text"),
	("inspection_type", "text"),
	("results", "text"),
	("violations", "text"),
	("latitude", "text"),
	("longitude", "text"),
	("location", "jsonb")
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
			for k in d: d[k] = ''
			d.update(p)
			q = list(d.values())
			r = q[:-1]
			r.append(json.dumps(q[-1]))
			yield tuple(r)

