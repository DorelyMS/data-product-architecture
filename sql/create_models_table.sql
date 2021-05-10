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
