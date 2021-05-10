import numpy as np
import pandas as pd
import psycopg2
import src.utils.general as general
from src.utils.constants import NOMBRE_BUCKET, ID_SOCRATA, PATH_CREDENCIALES


creds = general.get_db_credentials(PATH_CREDENCIALES)
user = creds['user']
password = creds['password']
database = creds['database']
host = creds['host']
port = creds['port']

conn = psycopg2.connect(dbname = database,
    user = user,
    host = host,
    password = password)

# Conexion S3
session = boto3.Session(
    aws_access_key_id=s3_creds['aws_access_key_id'],
    aws_secret_access_key=s3_creds['aws_secret_access_key']
)

import luigi.contrib.s3
import pickle

s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
client = luigi.contrib.s3.S3Client(
aws_access_key_id=s3_creds['aws_access_key_id'],
aws_secret_access_key=s3_creds['aws_secret_access_key'])
output_path = 's3://' + NOMBRE_BUCKET + '/modelos/modelo_seleccionado/'
gen = client.list(output_path)
archivo = next(gen)
mod = client.get_as_bytes(output_path+archivo)
model_p = pickle.loads(mod)
model = pickle.loads(model_p)

a_zip = pd.read_sql_query("select zip, zone from clean.zip_zones;", con=conn)
a_type = pd.read_sql_query("select * from clean.facility_group;", con=conn)
fea_eng = pd.read_sql_query("select * from from clean.feature_eng;", con=conn)
conn.close()

y_pred = model.predict(fea_eng)

xt = pd.DataFrame([fea_eng['zip'], fea_eng['facility_type'], fea_eng['pass'], y_pred]).transpose()
compas = pd.merge(left=xt, right=a_zip, how = 'left', left_on= 'zip', right_on = 'zip')
compas = pd.merge(left=xt, right=a_type, how = 'left', left_on= 'facility_type', right_on = 'facility_type')
compas = compas.rename(columns={'Unnamed 0':'score', 'pass':'label_value'})

compas['zone'] = compas['zone'].astype(str)
compas['score'] = compas['score'].astype(int)
compas['label_value'] = compas['label_value'].astype(int)

compas.pop('zip', 'facility_type')


from aequitas.group import Group
from aequitas.bias import Bias
from aequitas.fairness import Fairness

#Group
g = Group()
xtab, attrbs = g.get_crosstabs(compas)
absolute_metrics = g.list_absolute_metrics(xtab)
xtab[[col for col in xtab.columns if col not in absolute_metrics]]
group_df = xtab[['attribute_name', 'attribute_value']+[col for col in xtab.columns if col in absolute_metrics]].round(4)
xtab[['attribute_name', 'attribute_value']+[col for col in xtab.columns if col in absolute_metrics]].round(4)

#Bias
bias = Bias()
bdf = bias.get_disparity_predefined_groups(xtab, original_df=compas,
                                        ref_groups_dict={'zone':'West','facility_group':'grocery'},
                                        alpha=0.05)
# View disparity metrics added to dataframe
bdf[['attribute_name', 'attribute_value'] +
     bias.list_disparities(bdf)].round(2)
majority_bdf = bias.get_disparity_major_group(xtab, original_df=compas)
majority_bdf[['attribute_name', 'attribute_value'] +  bias.list_disparities(majority_bdf)].round(2)
min_bdf = bias.get_disparity_min_metric(xtab, original_df=compas)
bias_df = min_bdf[['attribute_name', 'attribute_value'] +  bias.list_disparities(min_bdf)].round(2)
min_bdf[['attribute_name', 'attribute_value'] +  bias.list_disparities(min_bdf)].round(2)

#Fairness
fair = Fairness()
fdf = fair.get_group_value_fairness(bdf)
parity_determinations = fair.list_parities(fdf)
fdf[['attribute_name', 'attribute_value'] + absolute_metrics +
    bias.list_disparities(fdf) + parity_determinations].round(2)
gaf = fair.get_group_attribute_fairness(fdf)
fairness_df = fdf.copy()
gof = fair.get_overall_fairness(fdf)








