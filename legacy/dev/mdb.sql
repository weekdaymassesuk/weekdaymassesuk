
Areas - TABLE
   area VARWCHAR
   area_order SMALLINT
   centre_latitude NUMERIC
   centre_longitude NUMERIC
   description VARWCHAR
   external BOOLEAN
   holy_day_of_obligation_website VARWCHAR
   in_area VARWCHAR
   saturday_website VARWCHAR
   sunday_website VARWCHAR
   weekday_website VARWCHAR
   zoom INTEGER

Church2Area - TABLE
   Area VARWCHAR
   ChurchId INTEGER

Churches - TABLE
   Address VARWCHAR
   Alias VARWCHAR
   Confession_times VARWCHAR
   Diocese VARWCHAR
   Directions VARWCHAR
   email VARWCHAR
   id INTEGER
   Is_external VARWCHAR
   Is_persistent_offender VARWCHAR
   IsParish BOOLEAN
   IsShrine BOOLEAN
   last_updated_on DATE
   Latitude VARWCHAR
   Link_to_us BOOLEAN
   Longitude VARWCHAR
   map_link VARWCHAR
   Motorway VARWCHAR
   old_website VARWCHAR
   Parish VARWCHAR
   Phone VARWCHAR
   Postcode VARWCHAR
   Prospective_link_to_us VARWCHAR
   Scale INTEGER
   Tube VARWCHAR
   US_masstimes_ID INTEGER
   US_masstimes_last_updated DATE
   website VARWCHAR
   XCoord INTEGER
   YCoord INTEGER
   Zoom SMALLINT

Churches Query - VIEW
   Latitude VARWCHAR
   Postcode VARWCHAR

churches_without_areas - VIEW
   Alias VARWCHAR
   id INTEGER
   Parish VARWCHAR

Diocese - TABLE
   Diocese_country VARWCHAR
   Diocese_ID INTEGER
   Diocese_name VARWCHAR

Diocese Weekday Mass Totals 1 - VIEW
   Day VARWCHAR
   Diocese_name VARWCHAR
   hh24 VARWCHAR
   Postcode VARWCHAR
   restrictions VARWCHAR

DioceseQuery1 - VIEW
   Diocese_name VARWCHAR

HDOMassTimes - VIEW
   Day VARWCHAR
   eve BOOLEAN
   hh24 VARWCHAR
   ParishId INTEGER
   restrictions VARWCHAR

Holy_days_of_obligation - TABLE
   Area VARWCHAR
   Holy_day_date DATE
   ID INTEGER
   Name VARWCHAR
   Notes VARWCHAR

Lat/Long Query1 - VIEW
   Alias VARWCHAR
   Latitude VARWCHAR
   Parish VARWCHAR
   Postcode VARWCHAR

MassTimes - TABLE
   Day VARWCHAR
   eve BOOLEAN
   hh24 VARWCHAR
   ParishId INTEGER
   restrictions VARWCHAR

Motorway_Query1 - VIEW
   Alias VARWCHAR
   Day VARWCHAR
   hh24 VARWCHAR
   Junction VARWCHAR
   Motorway VARWCHAR
   Parish VARWCHAR
   restrictions VARWCHAR

Motorways - TABLE
   Church_ID INTEGER
   Distance_Miles NUMERIC
   ID INTEGER
   Junction VARWCHAR
   Motorway VARWCHAR
   Notes VARWCHAR

Old Websites - VIEW
   old_website VARWCHAR
   Parish VARWCHAR
   Postcode VARWCHAR
   website VARWCHAR

Parishes - TABLE
   ChurchId INTEGER
   HDOMassTimes VARWCHAR
   SaturdayMassTimes VARWCHAR
   SundayMassTimes VARWCHAR
   WeekdayMassTimes VARWCHAR

Postcode_Lat_Long_Lookup - TABLE
   ID INTEGER
   Latitude DOUBLE
   Longitude DOUBLE
   OS_X INTEGER
   OS_Y INTEGER
   Postcode_outcode VARWCHAR

qParishDetails - VIEW
   Address VARWCHAR
   Alias VARWCHAR
   Directions VARWCHAR
   HDOMassTimes VARWCHAR
   id INTEGER
   IsParish BOOLEAN
   map_link VARWCHAR
   Parish VARWCHAR
   Phone VARWCHAR
   Postcode VARWCHAR
   SaturdayMassTimes VARWCHAR
   SundayMassTimes VARWCHAR
   Tube VARWCHAR
   website VARWCHAR
   WeekdayMassTimes VARWCHAR
   XCoord INTEGER
   YCoord INTEGER
   Zoom SMALLINT

qShrineDetails - VIEW
   Address VARWCHAR
   Alias VARWCHAR
   Directions VARWCHAR
   id INTEGER
   IsParish BOOLEAN
   IsShrine BOOLEAN
   OpeningTimes VARWCHAR
   Parish VARWCHAR
   Phone VARWCHAR
   Postcode VARWCHAR
   Tube VARWCHAR
   website VARWCHAR
   XCoord INTEGER
   YCoord INTEGER
   Zoom SMALLINT

qWeekdayMassTimes - VIEW
   Alias VARWCHAR
   hh24 VARWCHAR
   id INTEGER
   Parish VARWCHAR
   restrictions VARWCHAR
   WeekdayMassTimes VARWCHAR

qWhatsNew - VIEW
   text VARWCHAR
   updated_on DATE

Results - LINK
   <Can't get columns>

SaturdayMassTimes - VIEW
   Day VARWCHAR
   eve BOOLEAN
   hh24 VARWCHAR
   ParishId INTEGER
   restrictions VARWCHAR

Shrines - TABLE
   ChurchId INTEGER
   OpeningTimes VARWCHAR

SundayMassTimes - VIEW
   Day VARWCHAR
   eve BOOLEAN
   hh24 VARWCHAR
   ParishId INTEGER
   restrictions VARWCHAR

Useful Links - TABLE
   ID INTEGER
   Link VARWCHAR
   Media VARWCHAR
   Sort Order INTEGER
   Subject Heading VARWCHAR
   Title VARWCHAR

WeekdayMassTimes - VIEW
   Day VARWCHAR
   eve BOOLEAN
   hh24 VARWCHAR
   ParishId INTEGER
   restrictions VARWCHAR

WhatsNew - TABLE
   text VARWCHAR
   updated_on DATE
