import numpy as np
import pandas as pd
import json
import pickle
import datetime

from sklearn.model_selection import TimeSeriesSplit
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV



def split_tiempo(archivo,campo_criterio,criterio):
    datos_ordenados=archivo.sort_values(by=campo_criterio)
    archivo_2=datos_ordenados.loc[datos_ordenados[campo_criterio]<=criterio]
    archivo_3=datos_ordenados.loc[datos_ordenados[campo_criterio]>criterio]
    return archivo_2, archivo_3


def magic_loop(X_train,y_train, cols, date_ing):
    #for i in range(0,len(modelos_to_run)):
    classifier = RandomForestClassifier()
    hyper_param_grid= {'n_estimators': [100,500,800], 
                    'max_depth': [1,5,10,50], 
#                     'max_features': ['sqrt','log2'],
#                     'min_samples_split': [2,5,10],
                       'min_samples_leaf':[1,2,4]}
    grid_search1 = GridSearchCV(classifier, 
                           hyper_param_grid, 
                           scoring = 'f1',
#                            cv = cv, 
                           n_jobs = -1,
                           verbose = 3)
    grid_search1.fit(X_train, y_train)
    
    cv_results = pd.DataFrame({k: grid_search1.cv_results_[k] for k in cols})
    l = len(X_train)
    res = []
    fecha_ejecucion = datetime.datetime.today()
    for r in cv_results.itertuples():
        line = []
        line.append(fecha_ejecucion)
        line.append(date_ing)
        line.append(l)
        line.append('modelo_'+date_ing.strftime("%Y%m%d")+"_"+str(r.rank_test_score))
        line.append(json.dumps(r[1]))
        line = line+list(r[2:])
        if r.rank_test_score == 1:
            line.append(pickle.dumps(grid_search1))
        else:
            line.append(None)
        res.append(tuple(line))
    
                               
#     results_1 = cv_results.sort_values(by='rank_test_score', ascending=True)
    
       
        
#     classifier = tree.DecisionTreeClassifier()
#     hyper_param_grid= {'max_depth': [3,5,10,25],
#                        'min_samples_split': [2,5,10,15],
#                        'min_samples_leaf':[1,2,4],
#                        'max_features': ['sqrt','log2']}
#     grid_search2 = GridSearchCV(classifier, 
#                            hyper_param_grid, 
#                            scoring = 'f1',
#                            cv = cv, 
#                            n_jobs = -1,
#                            verbose = 3)
#     grid_search2.fit(X_train, y_train)
#     cv_results = pd.DataFrame(grid_search2.cv_results_)
#     results_2 = cv_results.sort_values(by='rank_test_score', ascending=True)

    return res
    