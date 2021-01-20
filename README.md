## Proyecto Arquitectura de Productos de Datos

Este es el repositorio del Proyecto Final para la materia de Arquitectura de Productos de Datos del semestre 2021-2 en la Maestría en Ciencia de Datos, ITAM. El presente trabajo analiza el dataset [Chicago Food Inspections](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5) que incluye información sobre las inspecciones de restaurantes y otros establecimientos de comida en Chicago desde el 1 de Enero 2010 al presente con el fin de predecir para nuevas observaciones si el establecimiento pasará o no la inspección. 

## Contenido

+ [Integrantes del equipo](https://github.com/DorelyMS/data-product-architecture#integrantes-del-equipo)
+ [Summary](https://github.com/DorelyMS/data-product-architecture#summary)
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

+ Número de registros:
+ Número de columnas:
+ Las variables originales que integran el dataset son: 'Inspection ID', 'DBA Name', 'AKA Name', 'License #', 'Facility Type',
       'Risk', 'Address', 'City', 'State', 'Zip', 'Inspection Date',
       'Inspection Type', 'Results', 'Violations', 'Latitude', 'Longitude',
       'Location'.
+ A continuación agregamos la información correspondiente a la descripción de cada variable:
    + **Inspection ID**: Es el ID o número único asignado a la inspección.
  + **DBA Name:** Esta variable corresponde al nombre legal del establecimiento. DBA significa Doing business as.
  + **AKA Name:** Esta variable corresponde al nombre comercial del establecimiento, es decir, el nombre con el que sus clientes identifican al restaurante. AKA significa Also known as.
  + **License #:** Es el ID o número único asignado al establecimiento para el propósito de asignar una licencia por parte del Departamento de Asuntos de Negocios y Protección al Consumidor.
  + **Facility Type:** Tipo de Establecimiento. Cada establecimiento se clasifica en uno de los siguientes tipos: bakery, banquet hall, candy store, caterer, coffee shop, day care center (for ages less than 2), day care center (for ages 2 – 6), day care center (combo, for ages less than 2 and 2 – 6 combined), gas station, Golden Diner, grocery store, hospital, long term care center(nursing home), liquor store, mobile food dispenser, restaurant, paleteria, school, shelter, tavern, social club, wholesaler, or Wrigley Field Rooftop.
  + **Risk:** Esta variable corresponde al Riesgo asociado a la Categoría del Establecimiento. Cada establecimiento es categorizado de acuerdo a su riesgo adverso para dañar la salud de los consumiores, siendo 1 el mayor riesgo y 3 el de menor riesgo. La frecuencia de la inspección está asociada al riesgo, donde el riesgo 1 corresponde a los establecimientos inspeccionados con mayor frecuencia y el riesgo 3 a los establecimientos inspeccionados con menos frecuencia.
  + **Address:** Esta variable corresponde a la dirección completa donde se localiza el establecimiento.
  + **City:** Esta variable corresponde a la ciudad donde se localiza el establecimiento.
  + **State:** Esta variable corresponde al estado donde se localiza el establecimiento.
  + **Zip:** Esta variable corresponde al código postal donde se localiza el establecimiento.
  + **Inspection Date:** Esta variable es la fecha en la que se llevó a cabo la inspección. Es probable que un establecimiento en particular tenga varias inspecciones que son identificadas por diferentes fechas de inspección.
  + **Inspection Type:** Esta variable se refiere al tipo de inspección que se realizó. Los tipos de inspección se dividen en: canvass, es la inspección más común cuya frecuencia se relaciona con el riesgo relativo del establecimiento; consultation, cuando la inspección se realiza a solicitud del dueño del establecimiento previo a su apertura; complaint, cuando la inspección se realiza en respuesta a una queja contra el establecimiento; license, cuando la inspección se realiza como parte del requisito para que el establecimiento reciba su licencia para operar; suspect food poisoning, cuando la inspección se lleva a cabo en respuesta a que una o más personas reclaman haberse enfermado como consecuencia de haber comido en el establecimiento; task-force inspection, cuando se realiza la inspección a un bar or taverna. Re-inspections o reinspecciones pueden llevarse a cabo en la mayoría de estos tipos de inspección y están indicadas como tal.
  + **Results:** Corresponde al resultado de una inspección: can pass, pass with conditions o fail son posibles resultados. En los establecimientos que recibieron como resultado ‘pass’ no se encontraron violaciones de caracter crítico o serio (que corresponden a los números de violación del 1 al 14 y 15 al 29, respectivamente). En los establecimientos que recibieron ‘pass with conditions’ se encontraron violaciones críticas o serias pero fueron corregidas durante la inspección. En los establecimientos que recibieron ‘fail’ se encontraron violaciones críticas o serias que no fueron corregidas durante la inspección. Si un establecimiento recibe como resultado ‘fail’ no necesariamente significa que su licencia es suspendida. Establecimientos que fueron encontrados  cerrados de manera permanente 'out of business' o sin localizar 'not located' están indicados como tal.
  + **Violations:** Un establecimiento puede recibir una o más de 45 violaciones diferentes (los números de violación van de 1 al 44 y el 70). Para evitar cada número de violación listado en un establecimiento dado, el establecimiento debe cumplir con cada requisito para no recibir una violación en el reporte de la inspección, donde se detalla una descripción  específica de los hallazgos que causaron la violación por la que fueron reportados.
  + **Latitude:** Esta variable corresponde a la coordenada de latitud donde se localiza el establecimiento.
  + **Longitude:** Esta variable corresponde a la coordenada de longitud donde se localiza el establecimiento.
  + **Location:** Esta variable corresponde a las coordenadas de (longitud y latitud) donde se localiza el establecimiento.

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

