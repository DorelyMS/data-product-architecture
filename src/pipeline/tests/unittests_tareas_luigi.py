# Paquetes python para poder definir las clases de unittest
import marbles.core


class test_ing(marbles.core.TestCase):
    """
        Clase con pruebas de Task Almacenamiento usando marbles:
        1.- Probar que el pickle tiene las 17 columnas
    """

    def __init__(self, df):
        super(test_ing, self).__init__()
        self.df = df

    def test_num_columns(self):
        self.assertEqual(self.df.shape[1], 17, note="El número de columnas de la base de Ingesta (local) debe ser 17")

    def runTest(self):
        self.test_num_columns()


class test_alm(marbles.core.TestCase):
    """
        Clase con pruebas de Task Almacenamiento usando marbles:
        1.- Probar que el pickle tiene cuando menos un registro
    """

    def __init__(self, df):
        super(test_alm, self).__init__()
        self.df = df

    def test_base_no_vacia(self):
        self.assertNotEqual(self.df.shape[0], 0, note="El número de renglones de la base de Almacenamiento (S3) es cero (está vacía)")

    def runTest(self):
        self.test_base_no_vacia()


class test_prep(marbles.core.TestCase):
    """
        Clase con pruebas de Task Almacenamiento usando marbles:
        1.- Probar que el pickle tiene las 13 columnas
        2.- Probar que el pickle tiene cuando menos un registro
    """

    def __init__(self, df):
        super(test_prep, self).__init__()
        self.df = df

    def test_num_columns(self):
        self.assertEqual(self.df.shape[1], 13, note="El número de columnas de la base de Preprocessing and Cleaning (RDS) debe ser 13")

    def test_base_no_vacia(self):
        self.assertNotEqual(self.df.shape[0], 0, note="El número de renglones de la base de Preprocessing and Cleaning (RDS) es cero (está vacía)")

    def runTest(self):
        self.test_num_columns()
        self.test_base_no_vacia()


class test_feateng(marbles.core.TestCase):
    """
        Clase con pruebas de Task Feature Enginnering usando marbles:
        1.- Probar que el pickle tiene las 38 columnas
        2.- Probar que el pickle tiene cuando menos un registro
    """

    def __init__(self, df):
        super(test_feateng, self).__init__()
        self.df = df

    def test_num_columns(self):
        self.assertEqual(self.df.shape[1], 38, note="El número de columnas de la base de Feature Engineering (RDS) debe ser 38")

    def test_base_no_vacia(self):
        self.assertNotEqual(self.df.shape[0], 0, note="El número de renglones de la base de Feature Engineering (RDS) es cero (está vacía)")


    def runTest(self):
        self.test_num_columns()
        self.test_base_no_vacia()
        self.test_fecha_min()

class test_train(marbles.core.TestCase):
    """
        Clase con pruebas de Task Trainning usando marbles:
        1.- Probar que el pickle tiene las 8 columnas
        2.- Probar que el pickle tiene cuando menos un registro
    """

    def __init__(self, df):
        super(test_train, self).__init__()
        self.df = df

    def test_num_columns(self):
        self.assertEqual(self.df.shape[1], 8, note="El número de columnas de la base de Trainning (RDS) debe ser 8")

    def test_base_no_vacia(self):
        self.assertNotEqual(self.df.shape[0], 0, note="El número de renglones de la base de Trainning (RDS) es cero (está vacía)")

    def runTest(self):
        self.test_num_columns()
        self.test_base_no_vacia()

class test_seleccion(marbles.core.TestCase):
    """
        Clase con pruebas de Task Seleccion usando marbles:
        1.- Señlar si el modelo es un árbol de decisión
    """

    def __init__(self, type_model):
        super(test_seleccion, self).__init__()
        self.type_model = type_model

    def test_tipo_modelo_arbol(self):
        self.assertEqual(self.type_model, 'DecisionTreeClassifier', note="El modelo seleccionado no fue un DecisionTreeClassifier")
        # self.assertEqual(self.type_model, 'DecisionTrooClassifier',note="El modelo seleccionado no fue un DecisionTrooClassifier")

    def runTest(self):
        self.test_tipo_modelo_arbol()
