# python -m unittest marbles (dentro del directorio que contiene las pruebas). Puedes agregar la bandera -v para tener más información de la corrida de las pruebas.

import marbles.core
import pandas as pd
import pickle


class test_ingesta(marbles.core.TestCase):
    """
        Clase con pruebas de Task Ingesta Metadata usando marbles:
        1.- Probar que el pickle tiene las 17 columnas
        """

#    def __init__(self, type_ingx='consecutive', date_ingx='2015-01-01'):
#        super(test_ingesta, self).__init__()
#        self.type_ing = type_ingx
#        self.date_ing = date_ingx

    def test_num_columnas(self):
        #     file_name = str(self.type_ing) + '-inspections-' + str(self.date_ing) + '.pkl'
        #     if self.type_ing == 'consecutive':
        #         aux_path = 'ingestion/' + str(self.type_ing) + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(
        #             self.date_ing)[5:7] + '/'
        #     else:
        #         aux_path = 'ingestion/' + 'initial' + '/YEAR-' + str(self.date_ing)[0:4] + '/MONTH-' + str(self.date_ing)[
        #                                                                                                5:7] + '/'
        # local_path = './conf/base/' + aux_path + file_name
        local_path = './../../../conf/base/ingestion/consecutive/YEAR-2015/MONTH-01/consecutive-inspections-2015-01-01.pkl'
        infile = open(local_path, 'rb')
        ingestion_data = pickle.load(infile)
        infile.close()
        df = pd.DataFrame.from_dict(ingestion_data)

        self.assertEqual(df.shape[1], 17, note="El número de columnas en ingesta debe ser 17")

    # if __name__ == '__main__':
    #    marbles.core.main()