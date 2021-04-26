# python -m unittest marbles (dentro del directorio que contiene las pruebas). Puedes agregar la bandera -v para tener más información de la corrida de las pruebas.

import marbles.core
import pandas as pd
import pickle
import src.utils.general as general
import boto3
import boto3.session
from src.utils.constants import PATH_CREDENCIALES
from src.utils.general import get_s3_credentials

class test_almacenamiento(marbles.core.TestCase):
    """
       Clase con pruebas de Task Almacenamiento usando marbles:
       1.- Probar que el pickle se guardó en S3
    """

    def __init__(self, type_ing, date_ing, bucket_name):
        super(test_almacenamiento, self).__init__()
        self.type_ing = type_ing
        self.date_ing = date_ing
        self.bucket_name = bucket_name

    def test_almacenamiento(self):
        print('****aqui estoy****')
        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
        print(file_name)
        s3_creds = get_s3_credentials('./../../../conf/local/credentials.yaml')
        session = boto3.Session(
            aws_access_key_id=s3_creds['aws_access_key_id'],
            aws_secret_access_key=s3_creds['aws_secret_access_key']
        )
        aux_path = 'ingestion/' + general.type_ing_aux(str(self.type_ing)) + '/Yearr-' + str(self.date_ing)[
                                                                                        0:4] + '/MONTH-' + str(
            self.date_ing)[5:7] + '/'
        output_path = aux_path + file_name
        print(s3_creds['aws_access_key_id'])
        client = boto3.client('s3', region_name='us-west-2')

        # create a file object using the bucket and object key.
        print('****voy a leer****')
        #fileobj = 'hola'

        #print(fileobj['Body'])
        #df = pd.read_csv(fileobj['Body'], sep="\t")
        #print(df.columns)

        try:
            fileobj = client.get_object(Bucket=self.bucket_name, Key=output_path)
            print('****leí el archivo****')
        except (OSError, IOError, ValueError) as e:
            print("No existe un archivo en S3:", output_path)


        self.assertEqual(df.shape[1], 17, note="El número de columnas en ingesta debe ser 17")

    def runTest(self):
        self.test_almacenamiento()

def main():
    clase=test_almacenamiento(type_ing='consecutive',date_ing='2015-01-08',bucket_name='data-product-architecture-4')
    resultados=clase()
    print(len(resultados.failures))

if __name__ == "__main__":
    main()


