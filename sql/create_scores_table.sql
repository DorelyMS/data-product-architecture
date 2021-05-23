create schema if not exists api;

drop table if exists api.scores;

create table api.scores (
	"license_num" integer,
	"inspection_date"  date,
	"fecha_ejecucion" date,
	"score_1" double precision,
	"predict" integer
 );