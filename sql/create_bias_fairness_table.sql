create schema if not exists models;

drop table if exists models.bias_fairness;

create table models.bias_fairness (
    "attribute_name" text,
    "group_name" text,
    "for_" double precision,
    "fnr" double precision,
    "for_disparity" double precision,
    "fnr_disparity" double precision,
    "for_parity" boolean,
    "fnr_parity" boolean,
    "date_ing" date
 );
