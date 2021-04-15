create schema if not exists clean;

drop table if exists clean.clean;

create table clean.clean (
	"inspection_id"text,
	"dba_name" text,
	"aka_name" text,
	"license_" text,
	"facility_type" text,
	"risk" text,
	"address" text,
	"city" text,
	"state" text,
	"zip" text,
	"inspection_date" text,
	"inspection_type" text,
	"results" text,
	"violations" text,
	"latitude" text,
	"longitude" text,
	"location" jsonb
 );
