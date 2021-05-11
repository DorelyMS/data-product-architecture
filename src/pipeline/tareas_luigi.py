# Paquetes pyhon para diversos propósitos
import numpy as np
import pandas as pd
import boto3
import json, pickle, joblib
import datetime
import psycopg2
import socket
from sodapy import Socrata
import luigi
import luigi.contrib.s3
from luigi.contrib.postgres import CopyToTable, PostgresQuery
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Funciones importadas de data-product-architecture/src/utils/general.py
# para lectura de credenciales, apis y funciones auxiliares
import src.utils.general as general

# Funciones importadas de data-product-architecture/src/utils/general.py
# para lectura de credenciales, apis y funciones auxiliares
import src.pipeline.ingesta_alamacenamiento as ingesta_almacenamiento

# Funciones importadas de data-product-architecture/src/utils/train.py
# para dividir base (entrenamiento y prueba) y generar modelos (magic-loop)
import src.utils.train as train

# Funciones importadas de data-product-architecture/src/etl/cleaning.py
# para el preprocesarmiento y limpieza de la base
from src.etl.cleaning import cleaning

# Funciones importadas de data-product-architecture/src/etl/feature_engineering.py
# para la imputación de datos, creación y selección de variables
from src.etl.feature_engineering import feature_engineering

# Funciones importadas de data-product-architecture/src/utils/luigi_extras.py
# en general para trabajar las bases en RDS
from src.utils.luigi_extras import PostgresQueryPickle

# Funciones importadas de data-product-architecture/src/pipeline/tests/unittest_tareas_luigi.py
# para realizar pruebas unitarias en todas las task de luigi
from src.pipeline.tests.unittests_tareas_luigi import test_ing, test_alm, test_prep, test_feateng, test_train, test_seleccion, test_bias_fairness

# Constantes importadas de data-product-architecture/src/utils/constants.py
# para que el usuario ingrese sus propias credenciales, bucket de s3
from src.utils.constants import NOMBRE_BUCKET, FOOD_CONECTION, ID_SOCRATA, PATH_CREDENCIALES


from src.utils.bias_fairness import fun_bias_fair


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
        client = ingesta_almacenamiento.get_client()

        if self.type_ing == 'consecutive':
            init_date = self.date_ing - datetime.timedelta(days=6)
            soql_query = "inspection_date between'{}' and '{}'".format(init_date.strftime("%Y-%m-%d"),
                                                                       self.date_ing.strftime("%Y-%m-%d"))
            results = client.get_all(self.socrata_id, where=soql_query)

        else:
            init_date = '2020-01-01'
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
            aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(
                self.date_ing)[5:7] + '/'

        else:
            aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[
                                                                                                   5:7] + '/'

        local_path = './conf/base/' + aux_path + file_name
        return luigi.local_target.LocalTarget(local_path, format=luigi.format.Nop)


class TestIngTask(CopyToTable):
    """
    Clase de Luigi que genera test de Ingesta
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_Ingestion"
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi para subir
    # los registros del método rows a RDS
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
        # Primero se checará la existencia y lectura de la base .pkl guardada
        # en local (no en AWS) que guarda IngTask
        # Definimos nombres de archivos y paths apropiados para la busqueda
        # de la base
        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
        aux_path = 'ingestion/' + general.type_ing_aux(str(self.type_ing)) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
        local_path = './conf/base/' + aux_path + file_name
        # Intentamos leer la base y en caso de que no se encuentre se interrumpe
        # la ejecución del task, impidiendo así que el siguiente Task
        # guarde los metadatos
        try:
            infile = open(local_path, 'rb')
            ingestion_data = pickle.load(infile)
            infile.close()
            df = pd.DataFrame.from_dict(ingestion_data)
        except (OSError, IOError) as e:
            print("No existe un archivo en la ruta: ", local_path)
            # Aquí se interrumpe la ejecución del Task. Otra opción es no
            # interrumpir y definir pasar un dataframe vacío que no pasará
            # las pruebas unitarias con: df = pd.DataFrame([])
            raise Exception()

        # Inicializamos la clase que contiene las unittest adecuadas y
        # ejecutamos el método runTest (con 'pruebas()' )
        pruebas=test_ing(df=df)
        resultados=pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            # Si cacha un error, detiene la ejecución cuando len(failures)>0
            raise Exception("Falló pruebas unitarias Ingestion")

        # Si no hubo error se procede a subir la info de este Task a RDS
        metadata = {'type_ing': self.type_ing,
                   'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                   'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                   'test_results': 'No error unittest: ' + ','.join([i for i in dir(test_ing) if i.startswith('test_')])
                   }
        print("Test Ingestion metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


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
        return TestIngTask(date_ing=self.date_ing, type_ing=self.type_ing)

    def rows(self):

        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
        if self.type_ing == 'consecutive':
            aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(
                self.date_ing)[5:7] + '/'
        else:
            aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[
                                                                                                   5:7] + '/'
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

    s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
    client = luigi.contrib.s3.S3Client(
        aws_access_key_id=s3_creds['aws_access_key_id'],
        aws_secret_access_key=s3_creds['aws_secret_access_key'])

    def requires(self):
        return IngMetaTask(date_ing=self.date_ing,
                           type_ing=self.type_ing,
                           bucket_name=self.bucket_name)

    def run(self):
        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

        if self.type_ing == 'consecutive':
            aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(
                self.date_ing)[5:7] + '/'
        else:
            aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[
                                                                                                   5:7] + '/'

        output_path = 's3://' + self.bucket_name + '/' + aux_path + file_name
        local_path = './conf/base/' + aux_path + file_name

        self.client.put(local_path, output_path)

    # with self.output()

    def output(self):
        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'

        if self.type_ing == 'consecutive':
            aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(
                self.date_ing)[5:7] + '/'
        else:
            aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[
                                                                                                   5:7] + '/'

        output_path = 's3://' + self.bucket_name + '/' + aux_path + file_name

        return luigi.contrib.s3.S3Target(path=output_path, client=self.client, format=luigi.format.Nop)


class TestAlmTask(CopyToTable):
    """
    Clase de Luigi que genera test de Almacenamiento
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_Alm"
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi para subir
    # los registros del método rows a RDS
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
        return AlmTask(date_ing=self.date_ing,
                     type_ing=self.type_ing,
                     bucket_name=self.bucket_name)

    def rows(self):
        # Se comienza por checar la existencia y lectura de la base en s3
        s3_creds = general.get_s3_credentials('./conf/local/credentials.yaml')
        session = boto3.session.Session(region_name='us-west-2')
        s3client = session.client('s3', config=boto3.session.Config(signature_version='s3v4'),
                                 aws_access_key_id=s3_creds['aws_access_key_id'],
                                 aws_secret_access_key=s3_creds['aws_secret_access_key'])

        # definimos nombres y paths apropiados
        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
        aux_path = 'ingestion/' + general.type_ing_aux(str(self.type_ing)) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
        # A diferencia de otros Task, aquí no obtendremos local_path ni output_path,
        # sino un path conveniente para la función que usamos para leer de s3
        # (ligeramente diferente)
        path_s3 = aux_path + file_name

        try:
            # Usamos 'try' porque "tratamos" de leer el pkl de s3,
            # si no existe provocará error y se ejecutará lo que está en 'except'
            response = s3client.get_object(Bucket=self.bucket_name, Key=path_s3)
            body_string = response['Body'].read()
            data = pickle.loads(body_string)
            # Columnas de la base que el task AlmTask sube a s3
            columns = [("inspection_id", "integer"),
                      ("dba_name", "text"),
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
                      ("longitude", "double precision"),
                      ("city", "text"),
                      ("state", "text"),
                      ("location", "double precision")
                      ]
            # Reacomodamos la lista "columns" para obtener la 1era "columna" que contiene
            # las variables y con ello inicializar un dataframe que llenaremos con los
            # renglones que se vayan obteniendo del pkl
            df = pd.DataFrame(columns=list(zip(*columns))[0])
            # Creamos un diccionario a partir de la lista "columns"
            d = dict(columns)
            for p in data:
                # Actualizamos la info del diccionario (la "columna" derecha
                # para que en lugar de contener los tipos de variables
                # contenga los valores asociados a cada renglón de la base)
                d.update(p)
                # Construimos el dataframe renglón por renglón
                df = df.append(d, ignore_index=True)

        except:
            print("No existe el archivo de S3:", self.bucket_name + '/' + path_s3)
            # Como no existe el archivo detenemos la ejecución de este task
            # por lo que el Task que almacena los metadatos de Almacenamiento no se ejecutará
            # Este error no se alcanzará si se ejecuta correctamente el DAG compuesto
            # por los diferentes Task, pues primeramente se checa la existencia de este archivo
            # en "def requires(self):", y si no existe lo crea
            raise Exception()

        # Inicializamos una clase que contiene las pruebas que queremos
        # y ejecutamos su método runTest para que ejecute todas las pruebas
        # allí contenidas. Haciendo esto también aseguramos que se define el
        # atributo failures, el cual contiene el numero de errores encontrados
        # (si es cero entonces se pasaron todas las pruebas)
        pruebas=test_alm(df=df)
        resultados=pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            # Detenemos la ejecución del task dado que no se pasó todos
            # los unittest contenidos en 'test_almacenamiento'
            # por el Task que almacena los metadatos no se ejecutará
            raise Exception("Falló pruebas unitarias almacenamiento")

        # Si no hubo errores se procede a subir la info de este Task de unittest a RDS
        metadata = {'type_ing': self.type_ing,
                    'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                    'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                    'test_results': 'No error unittest: ' + ','.join([i for i in dir(test_alm) if i.startswith('test_')])
                    }
        print("Test Almacenamiento metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


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
        return TestAlmTask(bucket_name=self.bucket_name,
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
    Clase de Luigi que se encarga de Preprocesing and Cleaning
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
            aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(
                self.date_ing)[5:7] + '/'
        else:
            aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[
                                                                                                   5:7] + '/'
        local_path = './conf/base/' + aux_path + file_name
        with open(local_path, 'rb') as p:
            file = pickle.load(p)

        num_registros = len(file),
        variables = list(file[0].keys())

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
            df = pd.DataFrame(d, index=[0])
            df = cleaning(df)

            try:
                yield tuple(df.values[0])
            except:
                pass


class TestPrepTask(CopyToTable):
    """
    Clase de Luigi que genera test de Preprocessing and Cleaning
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_Prep"
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi para subir
    # los registros del método rows a RDS
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    # Tabla a la que enviaremos resultados de este task (si no hay fallas)
    table = 'meta.food_metadata'
    columns = [
      ("fecha_ejecucion", "timestamp"),
      ("tarea", "text"),
      ("usuario", "text"),
      ("metadata", "jsonb")
    ]
    # Tabla que leeremos para hacer pruebas unitarias
    table_base="clean.clean_food_data"

    def requires(self):
        return PrepTask(date_ing=self.date_ing,
                     type_ing=self.type_ing,
                     bucket_name=self.bucket_name)

    def rows(self):
        # Guardamos en un string el query con el que obtendremos todos
        # los datos de la base
        query = "SELECT * FROM " + self.table_base + ";"

        try:
            # Se hace la conexión con los servicios de RDS de donde
            # obtendremos la base y la guardamos en un dataframe
            conn = psycopg2.connect(dbname=self.database,
                                    user=self.user,
                                    host=self.host,
                                    password=self.password)
            df = pd.read_sql_query(query, con=conn)

        except:
            print("No existe el archivo de RDS:", self.table_base)
            # Como no existe el archivo detenemos la ejecución de este task
            # por lo que el Task que almacena los metadatos de
            # Preprocessing and Cleaning no se ejecutará
            # Este error no se alcanzará si se ejecuta correctamente el DAG compuesto
            # por los diferentes Task, pues primeramente se checa la existencia de este archivo
            # en "def requires(self):", y si no existe lo crea
            raise Exception()

        # Inicializamos una clase que contiene las pruebas que queremos
        # y ejecutamos su método runTest para que ejecute todas las pruebas
        # allí contenidas. Haciendo esto también aseguramos que se define el
        # atributo failures, el cual contiene el numero de errores encontrados
        # (si es cero entonces se pasaron todas las pruebas)
        pruebas = test_prep(df=df)
        resultados = pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            # Detenemos la ejecución del task dado que no se pasó todos
            # los unittest contenidos en 'test_almacenamiento'
            # por el Task que almacena los metadatos no se ejecutará
            raise Exception("Falló pruebas unitarias Preprocessing and Cleaning")

        # Si no hubo errores se procede a subir la info de este Task de unittest a RDS
        metadata = {'type_ing': self.type_ing,
                    'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                    'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                    'test_results': 'No error unittest: ' + ','.join([i for i in dir(test_prep) if i.startswith('test_')])
                    }
        print("Test Preprocessing and Cleaning metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


class PrepMetaTask(CopyToTable):
    """
    Clase de Luigi que guarda los metadatos de Preprocessing and Cleaning
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
        return TestPrepTask(bucket_name=self.bucket_name,
                        type_ing=self.type_ing,
                        date_ing=self.date_ing)

    def rows(self):
        metadata = {
            'type_ing': self.type_ing,
            'date_ing': self.date_ing.strftime("%Y-%m-%d"),
            'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
        }

        print("Preprocessing and Cleaning metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [
            (self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
        ]
        for element in r:
            yield element


class FeatEngTask(CopyToTable):
    """
    Clase de Luigi que se encarga de Feature Engineering
    """
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    # Para conectarse a la base
    creds = general.get_db_credentials(PATH_CREDENCIALES)
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    table = 'clean.feature_eng'

    columns = [
        ("inspection_id", "integer"),
        # ("dba_name", "text"),
        ("aka_name", "text"),
        ("license_num", "integer"),
        ("facility_type", "text"),
        ("risk", "numeric"),
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

        conn = psycopg2.connect(dbname=self.database,
                                user=self.user,
                                host=self.host,
                                password=self.password)
        df = pd.read_sql_query(query, con=conn)
        df = feature_engineering(df)

        cursor = conn.cursor()
        cursor.execute("drop table if exists clean.feature_eng;")
        conn.commit()
        conn.close()

        for r in df.itertuples():
            res = r[1:]
            yield res


class TestFeatEngTask(CopyToTable):
    """
    Clase de Luigi que genera test de Feature Engineering
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_FeatEng"
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi (CopyToTable)
    # para subir los registros del método rows a RDS
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    # Tabla donde enviaremos resultados de este task (si pasa todas las pruebas)
    table = 'meta.food_metadata'
    columns = [
      ("fecha_ejecucion", "timestamp"),
      ("tarea", "text"),
      ("usuario", "text"),
      ("metadata", "jsonb")
    ]
    # Tabla/base que leeremos para hacer pruebas unitarias
    table_base = 'clean.feature_eng'

    def requires(self):
        return FeatEngTask(date_ing=self.date_ing,
                     type_ing=self.type_ing,
                     bucket_name=self.bucket_name)

    def rows(self):
        # Guardamos en un string el query con el que obtendremos todos
        # los datos de la base
        query = "SELECT * FROM " + self.table_base + ";"

        try:
            # Se hace la conexión con los servicios de RDS de donde
            # obtendremos la base y la guardamos en un dataframe
            conn = psycopg2.connect(dbname=self.database,
                                    user=self.user,
                                    host=self.host,
                                    password=self.password)
            df = pd.read_sql_query(query, con=conn)

        except:
            print("No existe el archivo de RDS:", self.table_base)
            # Como no existe el archivo detenemos la ejecución de este task
            # por lo que el Task que almacena los metadatos de
            # Preprocessing and Cleaning no se ejecutará
            # Este error no se alcanzará si se ejecuta correctamente el DAG compuesto
            # por los diferentes Task, pues primeramente se checa la existencia de este archivo
            # en "def requires(self):", y si no existe lo crea
            raise Exception()

        # Inicializamos una clase que contiene las pruebas que queremos
        # y ejecutamos su método runTest para que ejecute todas las pruebas
        # allí contenidas. Haciendo esto también aseguramos que se define el
        # atributo failures, el cual contiene el numero de errores encontrados
        # (si es cero entonces se pasaron todas las pruebas)
        pruebas = test_feateng(df=df)
        resultados = pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            # Detenemos la ejecución del task dado que no se pasó todos
            # los unittest contenidos en 'test_almacenamiento'
            # por el Task que almacena los metadatos no se ejecutará
            raise Exception("Falló pruebas unitarias Feature Engineering")

        # Si no hubo errores se procede a subir la info de este Task de unittest a RDS
        metadata = {'type_ing': self.type_ing,
                    'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                    'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                    'test_results': 'No error unittest: ' + ','.join([i for i in dir(test_feateng) if i.startswith('test_')])
                    }
        print("Test Feature Engineering metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


class FeatEngMetaTask(CopyToTable):
    """
    Clase de Luigi que guarda los metadatos de Feature Engineering
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
        return TestFeatEngTask(bucket_name=self.bucket_name,
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


class TrainTask(PostgresQueryPickle):
    """
    Clase de Luigi que se encarga de Trainning
    """

    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    fecha_ejecucion = datetime.datetime.today()

    creds = general.get_db_credentials(PATH_CREDENCIALES)

    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    table = 'models.entrenamiento'

    columns = [
        ("fecha_ejecucion", "date"),
        ("nombre", "text"),
        ("hiperparametros", "jsonb"),
        ("score", "numeric"),
        ("rank", "integer"),
        ("modelo", "bytea")
    ]

    def requires(self):
        return FeatEngMetaTask(bucket_name=self.bucket_name,
                               type_ing=self.type_ing,
                               date_ing=self.date_ing)

    # Carga
    query = "select * from clean.feature_eng where inspection_date >= '2020-11-01';"
    conn = psycopg2.connect(dbname=database,
                            user=user,
                            host=host,
                            password=password)
    df = pd.read_sql_query(query, con=conn, parse_dates=['inspection_date'])
    conn.close()

    # Guarda
    query = """
	INSERT INTO models.entrenamiento (fecha_ejecucion, date_ing, registros, nombre, hiperparametros, score, rank, modelo)  
	VALUES %s
	"""


class TestTrainTask(CopyToTable):
    """
    Clase de Luigi que genera test de Trainning
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_Train"
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi (CopyToTable)
    # para subir los registros del método rows a RDS
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    # Tabla donde enviaremos resultados de este task (si pasa todas las pruebas)
    table = 'meta.food_metadata'
    columns = [
      ("fecha_ejecucion", "timestamp"),
      ("tarea", "text"),
      ("usuario", "text"),
      ("metadata", "jsonb")
    ]
    # Tabla/base que leeremos para hacer pruebas unitarias
    table_base = 'models.entrenamiento'

    def requires(self):
        return TrainTask(date_ing=self.date_ing,
                     type_ing=self.type_ing,
                     bucket_name=self.bucket_name)

    def rows(self):
        # Guardamos en un string el query con el que obtendremos todos
        # los datos de la base
        query = "SELECT * FROM " + self.table_base + ";"

        try:
            # Se hace la conexión con los servicios de RDS de donde
            # obtendremos la base y la guardamos en un dataframe
            conn = psycopg2.connect(dbname=self.database,
                                    user=self.user,
                                    host=self.host,
                                    password=self.password)
            df = pd.read_sql_query(query, con=conn)

        except:
            print("No existe el archivo de RDS:", self.table_base)
            # Como no existe el archivo detenemos la ejecución de este task
            # por lo que el Task que almacena los metadatos de
            # Preprocessing and Cleaning no se ejecutará
            # Este error no se alcanzará si se ejecuta correctamente el DAG compuesto
            # por los diferentes Task, pues primeramente se checa la existencia de este archivo
            # en "def requires(self):", y si no existe lo crea
            raise Exception()

        # Inicializamos una clase que contiene las pruebas que queremos
        # y ejecutamos su método runTest para que ejecute todas las pruebas
        # allí contenidas. Haciendo esto también aseguramos que se define el
        # atributo failures, el cual contiene el numero de errores encontrados
        # (si es cero entonces se pasaron todas las pruebas)
        pruebas = test_train(df=df)
        resultados = pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            # Detenemos la ejecución del task dado que no se pasó todos
            # los unittest contenidos en 'test_almacenamiento'
            # por el Task que almacena los metadatos no se ejecutará
            raise Exception("Falló pruebas unitarias preprocessing and cleaning")

        # Si no hubo errores se procede a subir la info de este Task de unittest a RDS
        metadata = {'type_ing': self.type_ing,
                    'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                    'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                    'test_results': 'No error unittest: ' + ','.join([i for i in dir(test_feateng) if i.startswith('test_')])
                    }
        print("Test Trainning metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


class TrainMetaTask(CopyToTable):
    """
    Clase de Luigi que guarda los metadatos de Trainning
    """

    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Training"

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
        return TestTrainTask(bucket_name=self.bucket_name,
                         type_ing=self.type_ing,
                         date_ing=self.date_ing)

    def rows(self):
        metadata = {
            'modelo': 'modelo_' + self.date_ing.strftime("%Y-%m-%d")
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


class SeleccionTask(luigi.Task):
    """
    Clase de Luigi encargada de la guardar el modelo seleccionado
    """

    # Parametros
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    # Conexion S3
    s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
    client = luigi.contrib.s3.S3Client(
        aws_access_key_id=s3_creds['aws_access_key_id'],
        aws_secret_access_key=s3_creds['aws_secret_access_key'])

    # Lectura RDS
    creds = general.get_db_credentials(PATH_CREDENCIALES)
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']

    query = "select * from clean.feature_eng where inspection_date >= '2020-11-01';"
    conn = psycopg2.connect(dbname=database,
                            user=user,
                            host=host,
                            password=password)
    df = pd.read_sql_query(query, con=conn, parse_dates=['inspection_date'])
    cur = conn.cursor()
    query = """
	select hiperparametros from models.entrenamiento 
	order by fecha_ejecucion desc, score desc
	limit 1
	"""
    cur.execute(query)
    res = cur.fetchone()
    cur.close()
    conn.close()
    hiperparametros = res[0]

    def requires(self):
        return TrainMetaTask(bucket_name=self.bucket_name,
                             type_ing=self.type_ing,
                             date_ing=self.date_ing)

    def run(self):
        X_train, X_test = train.split_tiempo(self.df, 'inspection_date', '2021-04-01')
        X = X_train.drop(
            ['aka_name', 'facility_type', 'address', 'inspection_date', 'inspection_type', 'violations', 'results',
             'pass'], axis=1)
        y = X_train['pass'].astype(int)
        rfc = RandomForestClassifier(**self.hiperparametros)
        rfc.fit(X, y)
        print(rfc)

        model = pickle.dumps(rfc)

        output_path = 's3://' + self.bucket_name + '/modelos/modelo_seleccionado/'
        self.client.remove(output_path)

        with self.output().open('w') as outfile:
            pickle.dump(model, outfile)

    def output(self):
        file_name = "modelo_" + str(self.date_ing) + '.pkl'
        output_path = 's3://' + self.bucket_name + '/modelos/modelo_seleccionado/' + file_name

        return luigi.contrib.s3.S3Target(path=output_path, client=self.client, format=luigi.format.Nop)


class TestSeleccionTask(CopyToTable):
    """
    Clase de Luigi que genera test de Seleccion
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_Seleccion"
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi para subir
    # los registros del método rows a RDS
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
        return SeleccionTask(date_ing=self.date_ing,
                     type_ing=self.type_ing,
                     bucket_name=self.bucket_name)

    def rows(self):
        # Se comienza por checar la existencia y lectura de la base en s3
        s3_creds = general.get_s3_credentials('./conf/local/credentials.yaml')
        session = boto3.session.Session(region_name='us-west-2')
        s3client = session.client('s3', config=boto3.session.Config(signature_version='s3v4'),
                                 aws_access_key_id=s3_creds['aws_access_key_id'],
                                 aws_secret_access_key=s3_creds['aws_secret_access_key'])

        # definimos nombres y paths apropiados
        file_name= "modelo_" + str(self.date_ing) + '.pkl'
        aux_path = 'modelos/modelo_seleccionado/'
        # A diferencia de otros Task, aquí no obtendremos local_path ni output_path,
        # sino un path conveniente para la función que usamos para leer de s3
        # (ligeramente diferente)
        path_s3 = aux_path + file_name
        try:
            # Usamos 'try' porque "tratamos" de leer el pkl de s3,
            # si no existe provocará error y se ejecutará lo que está en 'except'
            response = s3client.get_object(Bucket=self.bucket_name, Key=path_s3)
            body_string = response['Body'].read()
            model = pickle.loads(body_string)
            model = pickle.loads(model)
            # Aquí le preguntamos si tenemos un árbol de decisión como modelo
            type_model = str(model.base_estimator_).replace("()","")

        except:
            print("No existe el archivo de S3:", self.bucket_name + '/' + path_s3)
            raise Exception()

        # Inicializamos una clase que contiene las pruebas que queremos
        # y ejecutamos su método runTest para que ejecute todas las pruebas
        # allí contenidas. Haciendo esto también aseguramos que se define el
        # atributo failures, el cual contiene el numero de errores encontrados
        # (si es cero entonces se pasaron todas las pruebas)
        pruebas=test_seleccion(type_model=type_model)
        resultados=pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            # Detenemos la ejecución del task dado que no se pasó todos
            # los unittest contenidos en 'test_almacenamiento'
            # por el Task que almacena los metadatos no se ejecutará
            raise Exception("Falló pruebas unitarias en seleccion modelo")

        # Si no hubo errores se procede a subir la info de este Task de unittest a RDS
        metadata = {'type_ing': self.type_ing,
                    'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                    'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                    'test_results': 'No hubo errores'
                    }
        print("Test Seleccion metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


class SeleccionMetaTask(CopyToTable):
    """
    Clase de Luigi que guarda los metadatos de Seleccion
    """

    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Select"

    # Conexion S3
    s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
    client = luigi.contrib.s3.S3Client(
        aws_access_key_id=s3_creds['aws_access_key_id'],
        aws_secret_access_key=s3_creds['aws_secret_access_key'])

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
        # return SeleccionTask(bucket_name=self.bucket_name,
        return TestSeleccionTask(bucket_name=self.bucket_name,
                             type_ing=self.type_ing,
                             date_ing=self.date_ing)

    def rows(self):
        output_path = 's3://' + self.bucket_name + '/modelos/modelo_seleccionado/'
        res = self.client.list(output_path)
        modelo = next(res)

        # Lectura RDS
        creds = general.get_db_credentials(PATH_CREDENCIALES)
        user = creds['user']
        password = creds['password']
        database = creds['database']
        host = creds['host']
        port = creds['port']

        query = """
		select hiperparametros from models.entrenamiento
		order by score desc, fecha_ejecucion desc
		limit 1
		"""
        conn = psycopg2.connect(dbname=database,
                                user=user,
                                host=host,
                                password=password)
        df = pd.read_sql_query(query, con=conn, parse_dates=['inspection_date'])
        cur = conn.cursor()
        cur.execute(query)
        res = cur.fetchone()
        cur.close()
        conn.close()
        hiperparametros = res[0]

        metadata = {
            'modelo_elegido': modelo,
            'hiperparametros': hiperparametros
        }

        print("Seleccion metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [
            (self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
        ]
        for element in r:
            yield element















class BiasFairnessTask(CopyToTable):
    """
    Clase de Luigi que se encarga de Bias Fairness
    """
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    # Para conectarse a la base
    creds = general.get_db_credentials(PATH_CREDENCIALES)
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    table = 'models.bias_fairness'

    columns = [
        ("attribute_name", "text"),
        ("group_name", "text"),
        ("for_", "double precision"),
        ("fnr", "double precision"),
        ("for_disparity", "double precision"),
        ("fnr_disparity", "double precision"),
        ("for_parity", "boolean"),
        ("fnr_parity", "boolean")
    ]

    def requires(self):
        return SeleccionMetaTask(bucket_name=self.bucket_name,
                            type_ing=self.type_ing,
                            date_ing=self.date_ing)

    def rows(self):
        conn = psycopg2.connect(dbname=self.database,
                                user=self.user,
                                host=self.host,
                                password=self.password)

        a_zip = pd.read_sql_query("select zip, zone from clean.zip_zones;", con=conn)
        a_type = pd.read_sql_query("select * from clean.facility_group;", con=conn)
        fea_eng = pd.read_sql_query("select * from clean.feature_eng;", con=conn)



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

        df = fun_bias_fair(a_zip, a_type, fea_eng, model)

        cursor = conn.cursor()
        # cursor.execute("drop table if exists models.bias_fairness;")
        conn.commit()
        conn.close()

        for r in df.itertuples():
            res = r[1:]
            yield res


class TestBiasFairnessTask(CopyToTable):
    """
    Clase de Luigi que genera test de BiasFairness
    """

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Test_BiasFairness"
    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    creds = general.get_db_credentials(PATH_CREDENCIALES)
    # Parametros requeridos por la task de luigi (CopyToTable)
    # para subir los registros del método rows a RDS
    user = creds['user']
    password = creds['password']
    database = creds['database']
    host = creds['host']
    port = creds['port']
    # Tabla donde enviaremos resultados de este task (si pasa todas las pruebas)
    table = 'meta.food_metadata'
    columns = [
      ("fecha_ejecucion", "timestamp"),
      ("tarea", "text"),
      ("usuario", "text"),
      ("metadata", "jsonb")
    ]
    # Tabla/base que leeremos para hacer pruebas unitarias
    table_base = 'models.bias_fairness'

    def requires(self):
        return BiasFairnessTask(date_ing=self.date_ing,
                     type_ing=self.type_ing,
                     bucket_name=self.bucket_name)

    def rows(self):
        # Guardamos en un string el query con el que obtendremos todos
        # los datos de la base
        query = "SELECT * FROM " + self.table_base + ";"

        try:
            # Se hace la conexión con los servicios de RDS de donde
            # obtendremos la base y la guardamos en un dataframe
            conn = psycopg2.connect(dbname=self.database,
                                    user=self.user,
                                    host=self.host,
                                    password=self.password)
            df = pd.read_sql_query(query, con=conn)

        except:
            print("No existe el archivo de RDS:", self.table_base)
            raise Exception()

        pruebas = test_bias_fairness(df=df)
        resultados = pruebas()
        if len(resultados.failures) >0:
            for failure in resultados.failures:
                print(failure)
            raise Exception("Falló pruebas unitarias Bias Fairness")

        # Si no hubo errores se procede a subir la info de este Task de unittest a RDS
        metadata = {'type_ing': self.type_ing,
                    'date_ing': self.date_ing.strftime("%Y-%m-%d"),
                    'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                    'test_results': 'No error unittest: ' + ','.join([i for i in dir(test_bias_fairness) if i.startswith('test_')])
                    }
        print("Test Bias Fairness metadata")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [(self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))]
        for element in r:
            yield element


class BiasFairnessMetaTask(CopyToTable):
    """
    Clase de Luigi que guarda los metadatos de Bias Fairness
    """

    bucket_name = luigi.Parameter(default=NOMBRE_BUCKET)
    type_ing = luigi.Parameter(default='consecutive')
    date_ing = luigi.DateParameter(default=datetime.date.today())

    fecha_ejecucion = datetime.datetime.now()
    tarea = "Bias_Fairness"

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
        return TestBiasFairnessTask(bucket_name=self.bucket_name,
                           type_ing=self.type_ing,
                           date_ing=self.date_ing)

    def rows(self):
        metadata = {
            'type_ing': self.type_ing,
            'date_ing': self.date_ing.strftime("%Y-%m-%d"),
            'date_inic': (self.date_ing - datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
        }

        print("Feature Bias Fairness")
        print(self.fecha_ejecucion)
        print(self.tarea)
        print(metadata)

        r = [
            (self.fecha_ejecucion, self.tarea, self.user, json.dumps(metadata))
        ]
        for element in r:
            yield element