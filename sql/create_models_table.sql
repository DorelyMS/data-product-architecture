create schema if not exists models;

drop table if exists models.entrenamiento;

create table models.entrenamiento (
	"fecha_ejecucion"  date,
	"nombre" text,
	"modelo" bytea,
	"precision_train" numeric,
	"precision_test" numeric,
	"recall_train" numeric,
	"recall_test" numeric
 );
