create schema if not exists clean;

drop table if exists clean.facility_group;

create table clean.facility_group (
	"facility_type" text,
	"facility_group" text
 );
