create schema if not exists clean;

drop table if exists clean.facility_group;

create table clean.facility_group (
	"facility_type" text,
	"facility_group" text
 );

insert into clean.facility_group (facility_type, facility_group)
values 
('restaurant','restaurant'),
('grocery store','grocery'),
('school','school'),
('children''s services facility','school'),
('bakery','other'),
('daycare above and under 2 years','school'),
('hotel','hotel'),
('daycare (2 - 6 years)','school'),
('catering','other'),
('NaN','other'),
('liquor','bar'),
('daycare (under 2 years)','school'),
('mobile food preparer','other'),
('roof tops','other'),
('live poultry','other'),
('hospital','other'),
('commissary','other'),
('shared kitchen user (long term)','other'),
('shared kitchen','other'),
('banquet hall','other'),
('golden diner','other'),
('1023 childern''s service facility','school'),
('cafeteria','other'),
('daycare combo 1586','school'),
('grocery/deli','grocery'),
('grocery store/cooking school','grocery'),
('daycare','school'),
('mobile frozen desserts vendor','other'),
('pastry school','school'),
('cooking school','school'),
('charter school','school'),
('pop-up food establishment user-tier iii','other'),
('long term care','school'),
('ice cream shop','other'),
('high school kitchen','school'),
('tavern','other'),
('grocery/restaurant','grocery'),
('1023 childern''s services facility','school'),
('hotel','other');