create schema if not exists clean;

drop table if exists clean.clean_food_data;

create table clean.clean_food_data (
	"inspection_id" integer,
	"dba_name" text,
	"aka_name" text,
	"license_" integer,
	"facility_type" text,
	"risk" integer,
	"address" text,
	"zip" integer,
	"inspection_date" date,
	"inspection_type" text,
	"results" text,
	"violations" text,
	"latitude" double precision,
	"longitude" double precision
 );
