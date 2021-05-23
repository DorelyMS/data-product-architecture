create schema if not exists pred;

drop table if exists models.predicciones_train;

create table models.predicciones_train (
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



