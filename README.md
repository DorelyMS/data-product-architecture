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

## Summary de los datos con los que trabajamos para el reporte EDA

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
│   ├── eda               <- In this folder you can find our Exploratory Data Analysis (EDA)
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
    ├── pipeline          <- Script with Luigi Tasks for ingestion and storage

```

Figura 1. Estructura básica del proyecto.

## Requerimientos para ejecución

Para poder interactuar con este repositorio, debes clonar la rama main para hacer una copia local del repo en tu máquina. Es necesario crear un pyenv-virtualenv con la versión de **Python 3.6.8**, activarlo e instalar los **requirements.txt** ejecutando el siguiente comando una vez estando dentro del ambiente virtual:

```bash
pip install -r requirements.txt
```

Por otra parte, se espera que tengas un bucket de Amazon [S3](https://aws.amazon.com/es/s3/) con el nombre de **data-product-architecture-equipo-4**

## Proceso de Ingestión

### Para ejecutar el proceso de ingestión es necesario estar posicionado en la carpeta de data-product-arquitecture

- Para poder ingestar los datos del dataset [Chicago Food Inspections](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5) se utilizó una conexión con la API de Food Inspections cuya documentación puedes encontrar [aquí](https://dev.socrata.com/foundry/data.cityofchicago.org/4ijn-s7e5). La API nos permite conectarnos de manera programática y descargar los datos de Food Inspections.

- Para tener comunicación con la API, todas las solicitudes deben incluir un token que identifica su aplicación y cada aplicación debe tener un token único. Para crear un usuario y token dar click [aquí](https://data.cityofchicago.org/profile/edit/developer_settings)

- Se debe crear un archivo: **./conf/local/credentials.yaml**. 

Este archivo debe contener las credenciales de S3  y el App Token generado de *Food Inspections* antes mencionado, a continuación se muestra un ejemplo genérico del contenido que debe tener este archivo:

```yaml

s3:

   aws_access_key_id: "XXXXXX"

   aws_secret_access_key: "XXXXXXXXXX"

food_inspections:

   api_token: "XXXX"
```

- Una vez posicionado en la carpeta de data-product-arquitecture es necesario agregar al $PYTHONPATH$ (si se ejecuta en terminal) la ubicación del proyecto y del código donde se ubican los tasks de Luigi que se encargan de la ingesta de datos de la API de Food Inspections y el almacenamiento en el bucket de S3.

```bash
export PYTHONPATH=$PWD:$PYTHONPATH   
export PYTHONPATH=./src/pipeline:$PYTHONPATH
```

Luego debes abrir otra terminal, activar el pyenv y habilitar el scheduler de Luigi desde el browser de tu navegador con el siguiente comando:

```bash
luigid
```

Después puedes abrir un browser y escribir *localhost:8082/*

#### Ingesta Inicial

* Primero es necesario crear un cliente con la función *get_client*, que tiene como parámetro la ubicación del token de Food Inspections dentro del archivo *credentials.yaml*

* Para la ingesta inicial se usa la clase de Luigi *IngTask*, la cual debe recibir como parámetros: 

    - el cliente con el que nos podemos comunicar con la API
    - el límite de registros que queremos obtener al llamar a la API (en caso de no especificar ningún límite se obtienen todos los registros)
    - la fecha de ejecución en formato 'YYYY-MM-DD' (la cual indica el último día de corte hasta donde se descargarán los datos históricos)
    - el tipo de ingestión deberá ser *historic* en este caso para obtener la información desde Enero de 2010

A continuación un ejemplo de cómo generamos la ingesta histórica hasta un día determinado en formato 'YYYY-MM-DD' desde la terminal:

```bash
luigi --module ingesta_almacenamiento IngTask --bucket-name data-product-architecture-4 --date-ing YYYY-MM-DD --type-ing historic
```

* Posteriormente, para el almacenamiento de los registros en el bucket de s3, se usa la clase de Luigi *AlmTask*, ésta toma como parámetros:
    - nombre del bucket (en nuestro caso es: data-product-architecture-4) donde se desea guardar el archivo con los datos históricos en formato .pkl
    - el tipo de ingestión que deberá ser *historic* en este caso para obtener la información desde Enero de 2010
    - la fecha de ejecución en formato 'YYYY-MM-DD' (la cual indica el último día de corte hasta donde se descargarán los datos históricos)

A continuación un ejemplo de cómo corremos el task de almacenamiento desde la terminal:

```bash
luigi --module ingesta_almacenamiento_luigi AlmTask --bucket-name data-product-architecture-4 --date-ing YYYY-MM-DD --type-ing historic
```

#### Ingesta Consecutiva

* Al igual que en la ingesta inicial,  primero es necesario crear un cliente con la función *get_client*.

* Para la ingesta consecutiva también se usa la clase de Luigi *IngTask*, la cual debe recibir como parámetros:
    - el cliente con el que nos podemos comunicar con la API
    - el límite de registros que queremos obtener al llamar a la API (en caso de no especificar ningún límite se obtienen todos los registros)
    - la fecha de ejecución en formato 'YYYY-MM-DD' (la cual indica el día de corte hasta donde se descargarán los datos de la última semana)
    - el tipo de ingestión deberá ser *consecutive* para obtener una actualización de los últimos 7 días incluyendo la fecha de corte

A continuación un ejemplo de cómo generamos la ingesta histórica hasta un día determinado en formato 'YYYY-MM-DD' desde la terminal:

```bash
luigi --module ingesta_almacenamiento IngTask --bucket-name data-product-architecture-4 --date-ing YYYY-MM-DD --type-ing consecutive
```

* Posteriormente, para guardar los registros de la ingesta consecutiva en el bucket, se usa nuevamente la clase de Luigi *AlmTask*, ésta toma como parámetros:

    - nombre del bucket (en nuestro caso es: data-product-architecture-4) donde se desea guardar el archivo con los datos históricos en formato .pkl
    - el tipo de ingestión que deberá ser *consecutive* en este caso para obtener la información de la última semana
    - la fecha de ejecución en formato 'YYYY-MM-DD' (la cual indica el último día de corte hasta donde se descargarán los datos de los últimos 7 días)

A continuación un ejemplo de cómo corremos el task de almacenamiento desde la terminal:

```bash
luigi --module ingesta_almacenamiento_luigi AlmTask --bucket-name data-product-architecture-4 --date-ing YYYY-MM-DD --type-ing consecutive
```

Cabe mencionar que para Luigi no es necesario correr los tasks de ingesta y almacenamiento de forma individual. Sino que es posible correr directamente el task de almacenamiento para que Luigi ejecute el de ingesta primero con los parámetros de fecha y tipo de ingesta especificados.

#### DAG con las tasks del Checkpoint 3 en verde

Una vez ejecutado los comandos anteriores, se presenta una captura de nuestro DAG con las tasks de Almacenamiento e Ingesta en "Done"

<img src="https://dl.dropboxusercontent.com/s/wad6d6hwhontuoj/Captura%20de%20Pantalla%202021-03-16%20a%20la%28s%29%200.17.08.png?dl=0" heigth="500" width="1500">
