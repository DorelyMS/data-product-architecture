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

## Summary

+ Número de registros:
+ Número de columnas:
+ Qué variables son, qué información tiene

## Pregunta analítica

La pregunta analítica a contestar con el modelo predictivo es: ¿El establecimiento pasará o no la inspección?

## Frecuencia de actualización de los datos

La frecuencia de la actualización de los datos [Chicago Food Inspections](https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5) es:

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

