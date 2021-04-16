create schema if not exists meta;

drop table if exists meta.food_metadata;

create table meta.food_metadata (
	"fecha_ejecucion" timestamp,
	"tarea" text,
	"usuario" text,
	"metadata" jsonb
);

