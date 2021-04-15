create schema if not exists meta;

drop table if exists meta.metadata;

create table meta.metadata (
	"fecha_ejecucion" timestamp,
	"tarea" text,
	"usuario" text,
	"metadata" jsonb
);

