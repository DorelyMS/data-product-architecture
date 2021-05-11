create schema if not exists models;

drop table if exists models.entrenamiento;

create table models.entrenamiento (
	"fecha_ejecucion"  date,
	"date_ing"  date,
	"registros" integer,
	"nombre" text,
	"hiperparametros" jsonb,
	"score" numeric,
	"rank" integer,
	"modelo" bytea
 );

insert into models.entrenamiento (fecha_ejecucion, date_ing, registros, nombre, hiperparametros, score, rank, modelo)
values (CURRENT_DATE, null, null, null, null, 0, null, null)

