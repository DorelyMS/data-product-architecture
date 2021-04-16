create schema if not exists clean;

drop table if exists clean.food_clean;

create table clean.food_clean (
	"inspection_id" integer,
	"dba_name" text,
	"aka_name" text,
	"license_" integer,
	"facility_type" text,
	"risk" text,
	"address" text,
	"city" text,
	"state" text,
	"zip" integer,
	"inspection_date" date,
	"inspection_type" text,
	"results" text,
	"violations" text,
	"latitude" double precision,
	"longitude" double precision,
	"location" jsonb
 );
