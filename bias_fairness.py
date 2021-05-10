def fun_bias_fair():

    import numpy as np
    import pandas as pd
    import psycopg2
    import boto3
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



    import luigi.contrib.s3
    import pickle
    import joblib

    s3_creds = general.get_s3_credentials(PATH_CREDENCIALES)
    client = luigi.contrib.s3.S3Client(
    aws_access_key_id=s3_creds['aws_access_key_id'],
    aws_secret_access_key=s3_creds['aws_secret_access_key'])
    output_path = 's3://' + NOMBRE_BUCKET + '/modelos/modelo_seleccionado/'
    gen = client.list(output_path)
    archivo = next(gen)
    client.get(output_path+archivo, './modelo.joblib')
    #model_p = pickle.loads(mod)
    #model = pickle.loads(model_p)
    model = joblib.load('./modelo.joblib')

    # Conexion S3
    session = boto3.Session(
        aws_access_key_id=s3_creds['aws_access_key_id'],
        aws_secret_access_key=s3_creds['aws_secret_access_key']
    )

    a_zip = pd.read_sql_query("select zip, zone from clean.zip_zones;", con=conn)
    a_type = pd.read_sql_query("select * from clean.facility_group;", con=conn)
    fea_eng = pd.read_sql_query("select * from clean.feature_eng;", con=conn)
    conn.close()

    X = fea_eng.drop(
        ['aka_name', 'facility_type', 'address', 'inspection_date', 'inspection_type', 'violations', 'results', 'pass','days_since_last_inspection'],
        axis=1)
    y_pred = model.predict(X)



    xt = pd.DataFrame([fea_eng['zip'].astype(float), fea_eng['facility_type'], fea_eng['pass'], y_pred]).transpose()
    a_zip['zip']=a_zip['zip'].astype(float)
    compas = pd.merge(left=xt, right=a_zip, how = 'left', left_on= 'zip', right_on = 'zip')
    compas = pd.merge(left=compas, right=a_type, how = 'left', left_on= 'facility_type', right_on = 'facility_type')
    compas = compas.rename(columns={'Unnamed 0':'score', 'pass':'label_value'})

    compas.pop('zip')
    compas.pop('facility_type')

    compas['zone'] = compas['zone'].astype(str)
    compas['score'] = compas['score'].astype(int)
    compas['label_value'] = compas['label_value'].astype(int)
    #print(compas.isnull().sum())

    from aequitas.group import Group
    from aequitas.bias import Bias
    from aequitas.fairness import Fairness

    #Group
    g = Group()
    xtab, attrbs = g.get_crosstabs(compas)
    absolute_metrics = g.list_absolute_metrics(xtab)
    xtab[[col for col in xtab.columns if col not in absolute_metrics]]
    group_df = xtab[['attribute_name', 'attribute_value']+[col for col in xtab.columns if col in absolute_metrics]].round(4)
    abs_gpo = xtab[['attribute_name', 'attribute_value']+[col for col in xtab.columns if col in absolute_metrics]].round(4)


    #Bias
    bias = Bias()
    bdf = bias.get_disparity_predefined_groups(xtab, original_df=compas,
                                            ref_groups_dict={'zone':'West','facility_group':'grocery'},
                                            alpha=0.05)
    # View disparity metrics added to dataframe
    bias_bdf = bdf[['attribute_name', 'attribute_value'] +
         bias.list_disparities(bdf)].round(2)
    majority_bdf = bias.get_disparity_major_group(xtab, original_df=compas)
    bias_maj_bdf = majority_bdf[['attribute_name', 'attribute_value'] +  bias.list_disparities(majority_bdf)].round(2)
    min_bdf = bias.get_disparity_min_metric(xtab, original_df=compas)
    bias_min_bdf = min_bdf[['attribute_name', 'attribute_value'] +  bias.list_disparities(min_bdf)].round(2)
    min_bdf[['attribute_name', 'attribute_value'] +  bias.list_disparities(min_bdf)].round(2)

    #Fairness
    fair = Fairness()
    fdf = fair.get_group_value_fairness(bdf)
    parity_determinations = fair.list_parities(fdf)
    fair_fdf = fdf[['attribute_name', 'attribute_value'] + absolute_metrics +
        bias.list_disparities(fdf) + parity_determinations].round(2)
    gaf = fair.get_group_attribute_fairness(fdf)
    fairness_df = fdf.copy()
    gof = fair.get_overall_fairness(fdf)

    tab_bias_fair=fair_fdf[['attribute_name','attribute_value','for','fnr','for_disparity','fnr_disparity','FOR Parity','FNR Parity']]


    print(tab_bias_fair)


    return tab_bias_fair

if __name__=="__main__":
    fun_bias_fair()


