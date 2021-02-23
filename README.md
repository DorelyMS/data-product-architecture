## Proyecto Arquitectura de Productos de Datos

Este es el repositorio del Proyecto Final para la materia de Arquitectura de Productos de Datos del semestre 2021-2 en la Maestría en Ciencia de Datos, ITAM. El presente trabajo analiza el dataset [Chicago Food Inspections](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5) que incluye información sobre las inspecciones de restaurantes y otros establecimientos de comida en Chicago desde el 1 de Enero 2010 al presente con el fin de predecir para nuevas observaciones si el establecimiento pasará o no la inspección. 

## Contenido

+ [Integrantes del equipo](https://github.com/DorelyMS/data-product-architecture#integrantes-del-equipo)
+ [Summary](https://github.com/DorelyMS/data-product-architecture#summary-de-los-datos-con-los-que-trabajamos)
+ [Pregunta analítica](https://github.com/DorelyMS/data-product-architecture/blob/main/README.md#pregunta-anal%C3%ADtica)
+ [Frecuencia de actualización de los datos](https://github.com/DorelyMS/data-product-architecture#frecuencia-de-actualización-de-los-datos)
+ [Estructura básica del proyecto](https://github.com/DorelyMS/data-product-architecture#estructura-básica-del-proyecto)

## Integrantes del equipo

En la siguiente tabla se encuentran los integrantes del equipo:

| #    | Persona      | Github    |
| ---- | ------------ | --------- |
| 1    |  Bruno       | brunocgf     |
| 2    |  Dorely      | DorelyMS     |
| 3    |  Guillermo   | gzarazua     |
| 4    |  Yusuri      | YusuriAR     |

## Summary de los datos con los que trabajamos

+ Número de registros: 215,026 (Es importante resaltar que esta base fue extraída el día 15/01/2021 y el número de registros varía con una nueva fecha.)
+ Número de columnas: 17
+ Las variables originales que integran el dataset son: 'Inspection ID', 'DBA Name', 'AKA Name', 'License #', 'Facility Type',
       'Risk', 'Address', 'City', 'State', 'Zip', 'Inspection Date',
       'Inspection Type', 'Results', 'Violations', 'Latitude', 'Longitude',
       'Location'.
+ A continuación agregamos la información correspondiente a la descripción de cada variable la cual fue tomada directamente de la [referencia oficial](http://bit.ly/tS9IE8) sugerida para su consulta dentro del portal [Chicago Food Inspections](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5) 
    + **Inspection ID**: Es el ID o número único asignado a la inspección.
  + **DBA Name:** Esta variable corresponde al nombre legal del establecimiento. DBA significa: 'Doing business as'.
  + **AKA Name:** Esta variable corresponde al nombre comercial del establecimiento, es decir, el nombre con el que sus clientes identifican al restaurante. AKA significa 'Also known as'.
  + **License #:** Es el ID o número único asignado al establecimiento para el propósito de asignar una licencia por parte del Departamento de Asuntos de Negocios y Protección al Consumidor.
  + **Facility Type:** Tipo de Establecimiento. Cada establecimiento se clasifica en uno de los siguientes tipos: 'Bakery', 'Banquet Hall', 'Candy Store', 'Caterer', 'Coffee shop', 'Day Care Center (for ages less than 2)', 'Day Care Center (for ages 2 – 6)', 'Day Care Center (combo, for ages less than 2 and 2 – 6 combined)', 'Gas Station', 'Golden Diner', 'Grocery store', 'Hospital', 'Long term Care Center(nursing home)', 'Liquor Store', 'Mobile Food Dispenser', 'Restaurant', 'Paleteria', 'School', 'Shelter', 'Tavern', 'Social club', 'Wholesaler', o 'Wrigley Field Rooftop'.
  + **Risk:** Esta variable corresponde al Riesgo asociado a la Categoría del Establecimiento. Cada establecimiento es categorizado de acuerdo a su riesgo asociado a dañar la salud de los consumidores, siendo 1 el mayor riesgo y 3 el de menor riesgo. La frecuencia de la inspección está relacionada con el nivel de riesgo, donde el riesgo 1 corresponde a los establecimientos inspeccionados con mayor frecuencia y el riesgo 3 a los establecimientos inspeccionados con menos frecuencia.
  + **Address:** Esta variable corresponde a la dirección completa donde se localiza el establecimiento.
  + **City:** Esta variable corresponde a la ciudad donde se localiza el establecimiento.
  + **State:** Esta variable corresponde al estado donde se localiza el establecimiento.
  + **Zip:** Esta variable corresponde al código postal donde se localiza el establecimiento.
  + **Inspection Date:** Esta variable es la fecha en la que se llevó a cabo la inspección. Es probable que un establecimiento en particular tenga varias inspecciones que son identificadas por diferentes fechas de inspección.
  + **Inspection Type:** Esta variable se refiere al tipo de inspección que se realizó. Los tipos de inspección se dividen en: 'Canvass', es la inspección más común cuya frecuencia se relaciona con el riesgo relativo del establecimiento; 'Consultation', cuando la inspección se realiza a solicitud del dueño del establecimiento previo a su apertura; 'Complaint', cuando la inspección se realiza en respuesta a una queja contra el establecimiento; 'License', cuando la inspección se realiza como parte del requisito para que el establecimiento reciba su licencia para operar; 'Suspect Food Poisoning', cuando la inspección se lleva a cabo en respuesta a que una o más personas reclaman haberse enfermado como consecuencia de haber comido en el establecimiento; 'Task-force inspection', cuando se realiza la inspección a un bar or taverna. 'Re-inspections' o reinspecciones pueden llevarse a cabo en la mayoría de estos tipos de inspección y están indicadas como tal.
  + **Results:** Corresponde al resultado de una inspección: 'Pass', 'Pass with conditions' o 'Fail' son posibles resultados. En los establecimientos que recibieron como resultado ‘Pass’ no se encontraron violaciones de caracter crítico o serio (que corresponden a los números de violación del 1 al 14 y 15 al 29, respectivamente). En los establecimientos que recibieron ‘Pass with conditions’ se encontraron violaciones críticas o serias pero fueron corregidas durante la inspección. En los establecimientos que recibieron ‘Fail’ se encontraron violaciones críticas o serias que no fueron corregidas durante la inspección. Si un establecimiento recibe como resultado ‘Fail’ no necesariamente significa que su licencia es suspendida. Establecimientos que fueron encontrados  cerrados de manera permanente 'Out of Business' o sin localizar 'Not Located' están indicados como tal.
  + **Violations:** Un establecimiento puede recibir una o más de 45 violaciones diferentes (los números de violación van de 1 al 44 y el 70). Para evitar cada número de violación listado en un establecimiento dado, el establecimiento debe cumplir con cada requisito para no recibir una violación en el reporte de la inspección, donde se detalla una descripción  específica de los hallazgos que causaron la violación por la que fueron reportados.
  + **Latitude:** Esta variable corresponde a la coordenada geográfica de latitud donde se localiza el establecimiento.
  + **Longitude:** Esta variable corresponde a la coordenada geográfica de longitud donde se localiza el establecimiento.
  + **Location:** Esta variable corresponde a las coordenadas geográficas de (longitud y latitud) donde se localiza el establecimiento.

## Pregunta analítica

La pregunta analítica a contestar con el modelo predictivo es: ¿El establecimiento pasará o no la inspección?

## Frecuencia de actualización de los datos

La frecuencia de la actualización del dataset [Chicago Food Inspections](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5) es diaria. Sin embargo, la frecuencia de actualización de nuestro producto de datos será semanal.



## Estructura básica del proyecto

```bash
├── README.md             <- The top-level README for developers using this project.
├── conf
│   ├── base              <- Space for shared configurations like parameters
│   ├── local             <- Space for local configurations, usually credentials
│
├── docs                  <- Space for Sphinx documentation
│
├── notebooks             <- Jupyter notebooks.
│   ├── eda               <- Previous analisis of data
│
├── references            <- Data dictionaries, manuals, and all other explanatory materials.
│
├── results               <- Intermediate analysis as HTML, PDF, LaTeX, etc.
│
├── requirements.txt      <- The requirements file
│
├── .gitignore            <- Avoids uploading data, credentials, outputs, system files etc
│
├── infrastructure
├── sql
├── setup.py
├── src                   <- Source code for use in this project.
    ├── __init__.py       <- Makes src a Python module
    │
    ├── utils             <- Functions used across the project
    │
    │
    ├── etl               <- Scripts to transform data from raw to intermediate
    │
    │
    ├── pipeline

```

Figura 1. Estructura básica del proyecto.

## Requerimientos

En este proyecto se utiliza un pyenv-virtualenv con la versión de 
Python 3.6.8

Para poder replicar el proyecto es necesario ejecutar dentro del ambiente virtual:

<pip install -r requirements.txt> 
       
## Instrucciones

- Para tener comunicación con la API, todas las solicitudes deben incluir un token que identifica su aplicación y cada aplicación debe tener su token único. Para crear un usuario y token dar click [aquí](https://data.cityofchicago.org/profile/edit/developer_settings)

- Se debe crear un archivo: ./conf/local/credentials.yaml. Este archivo debe contener las credenciales de s3  y el token de *Food Inspections* antes mencionado, a continuación se muestra un ejemplo genérico:

```yaml

s3:

   aws_access_key_id: XXXXXX

   aws_secret_access_key: XXXXXXXXXX

food_inspections:

   api_token: XXXX
```

- Es necesario agregar al $PYTHONPATH$ la ubicación del proyecto

```bash
export PYTHONPATH=$PWD
```

#### Ingesta Inicial

* Primero es necesario crear un cliente con la función *get_client*, que tiene como parámetro la ubicación del token de Food Inspections dentro del archivo *credentials.yaml*

* Para la ingesta inicial se usa la función *ingesta_inicial*, la cual recibe como parámetros el cliente, y el límite de registros a obtener. En caso de no especificar ningún límite, se obtienen todos los registros.

* Finalmente, para guardar los registros en el bucket, se usa la función *guardar_ingesta*, ésta toma como parámetros:
    - bucket donde se desea guardar
    - ruta del bucket donde se desea guardar
    - datos a ingestar (pkl)
    - ruta donde se encuentran las credenciales

```python
from src.pipeline.ingesta_almacenamiento import get_client
from src.pipeline.ingesta_almacenamiento import ingesta_inicial
from src.pipeline.ingesta_almacenamiento import guardar_ingesta

#Se obtiene cliente con función get_client
client = get_client("./conf/local/credentials.yaml")

#Se obtienen los registros con ingesta_consecutiva, regresa los datos de la API
archivo = ingesta_inicial(client, 1000)

#Se guardan los registros en el bucket
guardar_ingesta('data_product_architecture-4', 
  'ingestion/initial/', 
  archivo, 
  './conf/local/credentials.yaml')

```

#### Ingesta Consecutiva

* Al igual que en la ingesta inicial,  primero es necesario crear un cliente con la función *get_client*.

* Para la ingesta consecutiva se usa la función *ingesta_consecutiva*, la cual recibe como parámetros:
    - cliente
    - fecha de la que se quieren obtener los datos
    - límite de registros a obtener, en caso de no especificar ningún límite, se obtienen todos los registros.


* Finalmente, para guardar los registros en el bucket, se usa la función *guardar_ingesta*

```python
from src.pipeline.ingesta_almacenamiento import get_client
from src.pipeline.ingesta_almacenamiento import ingesta_consecutiva
from src.pipeline.ingesta_almacenamiento import guardar_ingesta

#Se obtiene cliente con función get_client
client = get_client("./conf/local/credentials.yaml")

#Se obtienen los registros con ingesta_consecutiva, regresa los datos de la API
archivo = ingesta_consecutiva(client, '2021-01-21', 1000)

#Se guardan los registros en el bucket
guardar_ingesta('data_product_architecture-4', 
  'ingestion/consecutive/', 
  archivo, 
  './conf/local/credentials.yaml')

```