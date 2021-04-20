# libraries requiered
import pandas as pd


# Función que manda a llamar las trasnformaciones de estandarización de nombre
# de variables, ajustes en valores de varia
def cleaning(df):
    df = c_standarize_column_names(df)
    df = c_change_to_lowercase(df, ['aka_name', 'facility_type', 'risk', 'city', 'state', 'inspection_type',
                               'results', 'violations'])
    df = c_numeric_transformation_risk(df)
    df = c_categoric_transformation(df, ['aka_name', 'facility_type', 'inspection_type'])
    df = c_date_transformation('inspection_date', df)
    df = c_correct_chicago_in_state(df)
    df = c_drop_rows_not_chicago(df)
    df = c_drop_rows_not_illinois(df)
    df = c_drop_rows_nulls_0_in_license(df)
    df = c_drop_columns(df)
    return df


# Ajusta los nombres de las columnas del dataframe que se pase
# como parámetro (entre ellos cambia todo a minísuculas)
def c_standarize_column_names(df):
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('#', '')
    df.columns = df.columns.str.lower()
    return df


# Ajusta los valores de los variables (columnas) que se pasen como
# parámetro del dataframe señalado
def c_change_to_lowercase(df, variables):
    for name in variables:
        df[name] = df[name].str.lower()
    return df


# Cambiamos la variable categorica de risk a numerica, considerando
# que existe un orden natural
# Obs: Para la categoría 'All' se le asignó el riesgo máximo de 1
#      pero no se tiene un fundamento. En la base se observa que
#      la mayoría de estos registros tienen por resultado de auditoría
#      ausente, por lo que más bien se trata de un sentinel value
def c_numeric_transformation_risk(df):
    df['risk'] = df['risk'].replace({'risk 1 (high)': 3, 'risk 2 (medium)': 2, 'risk 3 (low)': 1, 'all': 3})
    df['risk'] = df['risk'].convert_dtypes()
    return df


# Cambia el tipo de columna indicada como 'category'
def c_categoric_transformation(df, variables):
    for name in variables:
        df[name] = df[name].astype("category")
    return df


# Cambia el tipo de columna indicada como 'date'
def c_date_transformation(col, df):
    df[col] = pd.to_datetime(df[col])
    return df


# Homologa el valor de la variable
def c_correct_chicago_in_state(df):
    df['state'] = df['state'].replace(to_replace=["312chicago", "cchicago", "chchicago", "chcicago", \
                                           "chicagochicago", "chicagohicago", "chicagoi", \
                                           "chicago."], value="chicago")
    return df


# Función para quitar los registros que no corresponden a chicago
def c_drop_rows_not_chicago(df):
    df = df[df['city'] == 'chicago']
    return df

def c_drop_rows_not_illinois(df):
    df = df[df['state'] == 'il']
    return df


# Función para quitar los registros cuyo numero de licencia es cero o
# nulo (vacío)
def c_drop_rows_nulls_0_in_license(df):
    df = df[df['license_'].notnull()]
    df = df[df['license_'] != 0]
    return df


# Se seleccionan las variables deseadas
# Obs: Quizá aka_name podría servir, ya que contiene info del tipo de restaurante
#      Para pruebas unitarias se podría llenar el zip con los valores de latitud y longitud
#      y/o validar la congruencia entre estos 2 datos
def c_drop_columns(df):
    # df = df.drop(['dba_name', 'aka_name', 'address', 'city', 'state', 'location'], axis=1)
    df = df.drop(['city', 'state'], axis=1)
    return df