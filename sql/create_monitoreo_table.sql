create schema if not exists api;

drop table if exists api.monitoreo;

create table api.monitoreo (
	"score_0" double precision,
	"score_1" double precision
 );


