create schema if not exists clean;

drop table if exists clean.zip_zones;

create table clean.zip_zones (
	"zip" integer,
	"latitude" numeric,
	"longitude" numeric,
	"city" text,
	"zone" text
 );
