# python -m unittest marbles (dentro del directorio que contiene las pruebas). Puedes agregar la bandera -v para tener más información de la corrida de las pruebas.

import marbles.core
import pandas as pd
import pickle
import src.utils.general as general


class test_ingesta(marbles.core.TestCase):
    """
    Clase con pruebas de Task Ingesta usando marbles:
    1.- Probar que el pickle tiene las 17 columnas
    """

    def __init__(self, type_ing, date_ing):
        super(test_ingesta, self).__init__()
        self.type_ing = type_ing
        self.date_ing = date_ing

    def test_num_columnas(self):
        file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
        aux_path = 'ingestion/' + general.type_ing_aux(str(self.type_ing)) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[5:7] + '/'
        local_path = './conf/base/' + aux_path + file_name

        try:
            infile = open(local_path, 'rb')
            ingestion_data = pickle.load(infile)
            infile.close()
            df = pd.DataFrame.from_dict(ingestion_data)
        except (OSError, IOError) as e:
            print("No existe un archivo en la ruta: ", local_path)
            df = pd.DataFrame([])

        self.assertEqual(df.shape[1], 17, note="El número de columnas en ingesta debe ser 17")

    def runTest(self):
        self.test_num_columnas()



