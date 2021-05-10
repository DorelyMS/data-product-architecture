# libraries requiered
import pandas as pd
from datetime import datetime
from datetime import date
# from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import VarianceThreshold
import numpy as np
from src.etl.cleaning import c_date_transformation

# Función que manda a llamar las funciones con las que se crean nuevas
# variables
def feature_engineering(df):
    df = c_date_transformation('inspection_date', df)
    fe_add_column_year_of_insp_date(df)
    fe_add_column_month_of_insp_date(df)
    fe_add_column_day_of_insp_date(df)
    fe_add_column_pass_int(df)
    df = fe_add_column_days_since_last_insp(df)
    df = fe_add_column_approved_insp(df)
    df = fe_add_column_num_viol_last_insp(df)
    df = fe_imputer(df)
    df = dummies_day(df)
    df = dummies_month(df)
    fe_add_column_month_of_insp_date(df)
    return df


# Se crea variable con el numero de mes en que se hizo la inspección
def fe_add_column_year_of_insp_date(df):
    df['inspection_year'] = df['inspection_date'].dt.year

# Se crea variable con el numero de mes en que se hizo la inspección
def fe_add_column_month_of_insp_date(df):
    df['inspection_month'] = df['inspection_date'].dt.month


# Se crea variable con el numero de semana en que se hizo la inspección
def fe_add_column_day_of_insp_date(df):
    df['inspection_day'] = df['inspection_date'].dt.dayofweek


# Función que crea la variable objetivo que señala con 1 si se pasó la
# inspección y 0 en caso contrario
# Obs: Se debe considerar 'not ready', 'out of business' o
#      'business not located' como 'fail'?
def fe_add_column_pass_int(df):
    dic_results = {'pass': 1,
                   'out of business': 0,
                   'no entry': 0,
                   'fail': 0,
                   'not ready': 0,
                   'pass w/ conditions': 1,
                   'business not located': 0}
    df['pass'] = df.results.map(dic_results)
    df['pass'] = df['pass'].convert_dtypes()


# Función que crea una variable que señala los días transcurridos
# desde la última inspección (requiere que todos los registros
# tengan un numero de licencia)
# Obs: Toma unos 2.5 minutos en ejecutar
def fe_add_column_days_since_last_insp(df):
    # Se ordena en forma ascendente por license_ (que se considera representa un mismo individuo)
    # y en forma descendente por fecha de inspección, lo cual será de apoyo para recorrer todos los registros
    # y hacer cálculos de nuevas variables
    df = df.sort_values(['license_', 'inspection_date'], ascending=[True, False])
    df = df.reset_index(drop=True)
    df['days_since_last_inspection'] = 0
    flag = 0
    for i in range(df.shape[0]):
        if df.iloc[i]['license_'] != flag:
            # Cada que observamos un nuevo numero de licencia, estaremos parados en la última inspección
            # por lo que calcularemos los días transcurridos del día en que se ejecute este código y la fecha
            # de dicha inspección
            df.at[i, 'days_since_last_inspection'] = (datetime.now() - df.iloc[i]['inspection_date']).days
        else:
            # Cuando estamos en esta parte del operador if, estamos en una 2da, 3ra, etc, observación de un mismo
            # numero de licencia
            df.at[i, 'days_since_last_inspection'] = (
                        df.iloc[i - 1]['inspection_date'] - df.iloc[i]['inspection_date']).days
        flag = df.iloc[i]['license_']
    return df


# Función que crea una variable que señala el número de inspecciones anteriores
# Obs: Toma unos 2.5 minutos en ejecutar
def fe_add_column_approved_insp(df):
    df = df.sort_values(['license_', 'inspection_date'], ascending=[True, True])
    df = df.reset_index(drop=True)
    df['approved_insp'] = 0
    flag = 0
    for i in range(df.shape[0]):
        if df.iloc[i]['license_'] != flag:
            df.at[i, 'approved_insp'] = 0
        else:
            # El conteo de inspecciones pasadas no hace diferencia entre las que fueron aprobadas
            # con condiciones o sin condiciones
            if df.iloc[i - 1]['results'] == 'pass w/ conditions' or df.iloc[i - 1]['results'] == 'pass':
                # si la última inspección fue aprobada se suma 1 al conteo acumulado
                df.at[i, 'approved_insp'] = df.iloc[i - 1]['approved_insp'] + 1
            else:
                # si la última inspección fue reaprobada no se suma nada al conteo acumulado
                df.at[i, 'approved_insp'] = df.iloc[i - 1]['approved_insp']
        flag = df.iloc[i]['license_']
    return df


def fe_add_column_num_viol_last_insp(df):
    df = df.sort_values(['license_', 'inspection_date'], ascending=[True, True])
    df = df.reset_index(drop=True)
    df['num_viol_last_insp'] = 0
    flag = 0
    for i in range(df.shape[0]):
        if df.iloc[i]['license_'] != flag:
            df.at[i, 'num_viol_last_insp'] = 0
        else:
            if pd.isnull(df.iloc[i - 1]['violations']):
                df.at[i, 'num_viol_last_insp'] = 0
            else:
                # si el valor de violation de la inspección es no nullo es porque existe una violación (por ello
                # de entrada se suma 1), cada violación adicional está señalado separandolo con '| ' (por ello
                # se cuentan las veces que aparece dicha secuencia). La violación 60 se refiere a comentarios relativos
                # al complimiento de violaciones anteriores ('previous core violation corrected') y como no es una violación
                # adicional a la inspección, si se tiene esta nota se resta 1
                df.at[i, 'num_viol_last_insp'] = 1 + df.iloc[i - 1]['violations'].count('| ') - df.iloc[i - 1][
                    'violations'].count('previous core violation corrected')
        flag = df.iloc[i]['license_']
    return df


def fe_imputer(df):
    # Función para imputar columnas específicas
    # Obs: Cada variable señalada se imputa con el valor más frecuente. Dada la frecuencia observada
    #      en los datos, se puede decir que:
    #      - los campos vacíos de 'dba_name' se llenas con 'subway'
    #      - los campos vacíos de 'aka_name' se llenas con 'subway'
    #      - los campos vacíos de 'facility_type' se llenas con 'restaurant'
    #      - los campos vacíos de 'risky' se llenas con 1
    #      - El valor que se inserte en los campos vacíos de 'zip' podría no se congruente con 'location'
    #        (la mayoría de las veces que no se tiene zip sí se tiene 'location', pero en general son pocos
    #        datos faltantes de 'zip')
    #      - los campos vacíos de 'inspection_type' se llenas con 'canvass'
    #      - los campos vacíos de 'results' se llenas con 'pass'
    #      En general no hay datos faltantes en 'inspection_id', 'risk', 'inspection_date', 'results'
    transformers = [
        ('impute_facility_type', SimpleImputer(strategy="most_frequent"), ['facility_type']),
        ('impute_risk', SimpleImputer(strategy="most_frequent"), ['risk']),
        ('impute_zip', SimpleImputer(strategy="most_frequent"), ['zip']),
        ('impute_inspection_type', SimpleImputer(strategy="most_frequent"), ['inspection_type']),
        ('impute_results', SimpleImputer(strategy="most_frequent"), ['results']),
        ('impute_latitude', SimpleImputer(strategy="most_frequent"), ['latitude']),
        ('impute_longitude', SimpleImputer(strategy="most_frequent"), ['longitude'])
    ]
    # Definimos el transformador con las transformaciones arriba definidas
    col_trans = ColumnTransformer(transformers, remainder="passthrough", n_jobs=-1, verbose=True)
    # Ajustamos
    col_trans.fit(df)
    # Obtenemos el resultado de las transformaciones (imputaciones) aplicadas a la base
    aux = col_trans.transform(df)
    # Generamos un arreglo auxiliar que contiene los nombres de las variables transformadas
    aux_var_imput = pd.DataFrame(transformers[:])[0].str.replace('impute_', '')
    # Generamos un arreglo auxiliar que contiene las variables no transformadas
    aux_var_no_imput = df.columns[~np.in1d(df.columns, aux_var_imput)]
    # Guardamos el orden original de las columnas de la base
    col_original_order = df.columns
    # creamos un dataframe con los resultados del transformador, plasmando los
    # de columnas correspondientes

    # creamos un dataframe con las variables dummies y otro dataframe con las variables
    # que no transformamos (no dummies) para después unirlos
    aux_df_var_no_imput = df[df.columns[~np.in1d(df.columns, aux_var_imput)]]
    aux_df_var_imput = pd.DataFrame(aux[:, 0:len(aux_var_imput)], columns=aux_var_imput)
    # unimos los 2 dataframes para tener una única base conservando el tipo
    # de datos que previamente definimos para las variables que no transformamos
    df = pd.concat([aux_df_var_no_imput, aux_df_var_imput], axis=1)
    df = df[col_original_order]
    return df


# def fe_dummier(df):
#     transformer = [('one_hot', OneHotEncoder(), ['inspection_month', 'inspection_day'])]
#     col_trans = ColumnTransformer(transformer, remainder="passthrough", n_jobs=-1, verbose=True)
#     col_trans.fit(df)
#     aux = col_trans.transform(df)
#     aux_var_dummies = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', \
#                        'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
#     # identificamos las variables que no son dummies
#     aux_var_no_dummies = df.columns[~np.in1d(df.columns, ['inspection_month', 'inspection_day'])]

#     # creamos un dataframe con las variables dummies y otro dataframe con las variables
#     # que no transformamos (no dummies) para después unirlos
#     aux_df_var_no_dummies = df[df.columns[~np.in1d(df.columns, ['inspection_month', 'inspection_day'])]]
#     aux_df_var_dummies = pd.DataFrame(aux[:, 0:len(aux_var_dummies)], columns=aux_var_dummies).convert_dtypes()
#     # unimos los 2 dataframes para tener una única base conservando el tipo
#     # de datos que previamente definimos para las variables que no transformamos
#     df = pd.concat([aux_df_var_no_dummies, aux_df_var_dummies], axis=1)
#     return df

def dummies_month(df):
    d = {
        1: 'ene',
        2: 'feb',
        3: 'mar',
        4: 'abr',
        5: 'may',
        6: 'jun',
        7: 'jul',
        8: 'ago',
        9: 'sep',
        10: 'oct',
        11: 'nov',
        12: 'dic'
    }
    # Dataframe de ceros con las columnas de todos los meses
    df_total_dummies = pd.DataFrame(0, index=np.arange(df.shape[0]), columns=d.values())
    # Dataframe con las dummies creadas a partir de los valores encontrados
    # (no necesariamente estarían todos los meses)
    df_current_dummies = pd.get_dummies(df['inspection_month'])
    # Ponemos el nombre de estas dummies acorde al diccionario
    # (ejemplo: la columan 1 cambia de nombre a 'ene')
    df_current_dummies.columns = df_current_dummies.columns.map(d)
    # dataframe auxiliar que une los dos dataframes
    aux = pd.concat([df_current_dummies, df_total_dummies], axis=1)
    # quitamos las columnas duplicadas, prevaleciendo las que primero encuentra
    # que son las current dummies
    df_dummies = aux.loc[:,~aux.columns.duplicated()]
    df_dummies = df_dummies.astype(int)
    # se regresa el dataframe original sin la variable a la que se crearon las dummies,
    # uniando al final las columnas dummies
    df_new = pd.concat([df.drop(['inspection_month'], axis=1), df_dummies[d.values()]], axis=1)
    return df_new

def dummies_day(df):
    d = {
        1: 'mon',
        2: 'tue',
        3: 'wed',
        4: 'thu',
        5: 'fri',
        6: 'sat',
        7: 'sun'
    }
    # Dataframe de ceros con las columnas de todos los dias de la semana
    df_total_dummies = pd.DataFrame(0, index=np.arange(df.shape[0]), columns=d.values())
    # Dataframe con las dummies creadas a partir de los valores encontrados
    # (no necesariamente estarían todos los dias)
    df_current_dummies = pd.get_dummies(df['inspection_day'])
    # Ponemos el nombre de estas dummies acorde al diccionario
    # (ejemplo: la columan 1 cambia de nombre a 'mon')
    df_current_dummies.columns = df_current_dummies.columns.map(d)
    # dataframe auxiliar que une los dos dataframes
    aux = pd.concat([df_current_dummies, df_total_dummies], axis=1)
    # quitamos las columnas duplicadas, prevaleciendo las que primero encuentra
    # que son las current dummies
    df_dummies = aux.loc[:,~aux.columns.duplicated()]
    df_dummies = df_dummies.astype(int)
    # se regresa el dataframe original sin la variable a la que se crearon las dummies,
    # uniando al final las columnas dummies
    df_new = pd.concat([df.drop(['inspection_day'], axis=1), df_dummies[d.values()]], axis=1)
    return df_new