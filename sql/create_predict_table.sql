create schema if not exists pred;

drop table if exists pred.predicciones;

create table pred.predicciones (
	"inspection_id"  integer,
	"license_num" integer,
	"inspection_date"  date,
	"fecha_ejecucion" date,
	"modelo" text,
	"score_0" double precision,
	"score_1" double precision,
	"predict" integer,
	"pass" integer
 );


