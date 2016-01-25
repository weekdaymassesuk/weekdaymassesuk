CREATE TABLE
  days
(
  code VARCHAR (10),
  name VARCHAR (60),
  seq INT,
  PRIMARY KEY (code)
);

INSERT INTO days (code, name, seq) VALUES ('K', 'Weekday', 1);
INSERT INTO days (code, name, seq) VALUES ('A', 'Saturday', 2);
INSERT INTO days (code, name, seq) VALUES ('U', 'Sunday', 3);
INSERT INTO days (code, name, seq) VALUES ('H', 'Holy Day of Obligation', 4);

CREATE TABLE
  churches
(
  id INTEGER PRIMARY KEY,
  name VARCHAR (60),
  alias VARCHAR (60),
  is_parish BIT,
  is_shrine BIT,
  is_external BIT,
  address VARCHAR (60),
  postcode VARCHAR (60),
  phone VARCHAR (60),
  public_transport VARCHAR (60),
  directions VARCHAR (100),
  x_coord INTEGER,
  y_coord INTEGER,
  zoom_level INTEGER,
  map_link VARCHAR (100),
  website VARCHAR (200),
  weekday_mass_times VARCHAR (100),
  saturday_mass_times VARCHAR (100),
  sunday_mass_times VARCHAR (100),
  holy_day_of_obligation_mass_times VARCHAR (100),
  confession_times VARCHAR (100),
  latitude DECIMAL,
  longitude DECIMAL,
  scale INTEGER,
  email VARCHAR (100),
  is_persistent_offender CHAR (1),
  last_updated_on DATE
);
CREATE UNIQUE INDEX churches0 ON churches (id);
CREATE INDEX churches1 ON churches (name);
CREATE INDEX churches2 ON churches (latitude, longitude);

CREATE TABLE
  areas
(
  id INTEGER PRIMARY KEY,
  code VARCHAR (60),
  name VARCHAR (60),
  details VARCHAR (100),
  weekday_website VARCHAR (200),
  sunday_website VARCHAR (200),
  saturday_website VARCHAR (200),
  holy_day_of_obligation_website VARCHAR (200),
  is_external BOOLEAN,
  area_order INT,
  latitude0 DECIMAL,
  longitude0 DECIMAL,
  latitude1 DECIMAL,
  longitude1 DECIMAL,
  latitude DECIMAL,
  longitude DECIMAL,
  zoom INTEGER
);
CREATE UNIQUE INDEX areas0 ON areas (id);
CREATE UNIQUE INDEX areas1 ON areas (name);

CREATE TABLE
  area_areas
(
  area_id INTEGER NOT NULL
    REFERENCES areas (id),
  in_area_id INTEGER NOT NULL
    REFERENCES areas (id),
  PRIMARY KEY (area_id, in_area_id)
);
CREATE UNIQUE INDEX area_areas0 ON area_areas (area_id, in_area_id);
CREATE UNIQUE INDEX area_areas1 ON area_areas (in_area_id, area_id);

CREATE TABLE
  church_areas
(
  id INTEGER PRIMARY KEY,
  church_id INTEGER NOT NULL
    REFERENCES churches (id),
  in_area_id INTEGER NULL
    REFERENCES areas (id)
);
CREATE UNIQUE INDEX church_areas0 ON church_areas (church_id, in_area_id);

CREATE TABLE
  mass_times
(
  church_id INTEGER NOT NULL,
  day CHAR NOT NULL,
  hh24 VARCHAR (4) NOT NULL,
  eve BOOLEAN NOT NULL,
  restrictions VARCHAR (100),
  PRIMARY KEY (church_id, day, hh24, eve)
);
CREATE UNIQUE INDEX mass_times0 ON mass_times (church_id, day, hh24, eve);

CREATE TABLE
  area_day_church_masses
(
  area_id INTEGER NOT NULL,
  day_code CHAR NOT NULL,
  church_id INTEGER NULL,
  hh24 VARCHAR (4) NULL,
  eve BOOLEAN NULL,
  restrictions VARCHAR (100) NULL,
  PRIMARY KEY (area_id, day_code, church_id, hh24, eve)
);
CREATE UNIQUE INDEX area_day_church_masses0 ON area_day_church_masses (area_id, day_code, church_id, hh24, eve);
CREATE INDEX area_day_church_masses1 ON area_day_church_masses (area_id, church_id);

CREATE TABLE
  whats_new
(
  id INTEGER PRIMARY KEY,
  updated_on DATE NOT NULL,
  text VARCHAR (100) NOT NULL
);

CREATE TABLE
  postcode_coords
(
  id INTEGER NOT NULL PRIMARY KEY,
  area_id INT NULL,
  outcode VARCHAR (10) NOT NULL,
  os_x INTEGER NULL,
  os_y INTEGER NULL,
  latitude DECIMAL NULL,
  longitude DECIMAL NULL
);
CREATE UNIQUE INDEX pk_pco ON postcode_coords (id);
CREATE UNIQUE INDEX uq_pco ON postcode_coords (outcode);

CREATE TABLE
  motorway_churches
(
  id INTEGER NOT NULL PRIMARY KEY,
  church_id INTEGER NOT NULL,
  motorway MOTORWAY NOT NULL,
  junction JUNCTION NOT NULL,
  distance DECIMAL NULL,
  notes VARCHAR (100) NULL
)
;

CREATE TABLE
  hdos
(
  id INTEGER NOT NULL PRIMARY KEY,
  area_id INT NULL,
  name VARCHAR (60) NOT NULL,
  yyyymmdd CHAR (8) NOT NULL,
  notes VARCHAR (100)
)
;

CREATE TABLE
  links
(
  id INTEGER NOT NULL PRIMARY KEY,
  type VARCHAR(100) NOT NULL DEFAULT "Documents",
  subject VARCHAR (50) NOT NULL,
  title VARCHAR (100) NOT NULL,
  link VARCHAR (150) NOT NULL,
  sequence INTEGER NULL
)
;

CREATE TABLE
  search_scores
(
  church_id INTEGER NOT NULL,
  word VARCHAR (100) NOT NULL,
  score INTEGER NOT NULL,
  PRIMARY KEY (church_id, word)
)
;
CREATE UNIQUE INDEX pk_search_scores ON search_scores (word, church_id);

CREATE TABLE
  translations
(
  key VARCHAR (200) NOT NULL,
  language VARCHAR (2) NOT NULL,
  translation VARCHAR (200) NOT NULL,
  PRIMARY KEY (key, language)
)
;
CREATE UNIQUE INDEX pk_translations ON translations (key, language);

CREATE TABLE
  translation_urls
(
  key VARCHAR (200) NOT NULL,
  sequence INT NOT NULL,
  url VARCHAR (200) NOT NULL,
  PRIMARY KEY (key, sequence)
)
;
CREATE UNIQUE INDEX pk_translation_urls ON translation_urls (key, sequence);

CREATE TABLE
  adverts
(
  id INTEGER PRIMARY KEY,
  organisation VARCHAR(200) NOT NULL,
  filename VARCHAR(200) NOT NULL,
  url VARCHAR(200) NOT NULL,
  image BLOB NULL
)
;

CREATE VIEW
  v_area_day_masses
AS SELECT
  area_id,
  day_code,
  COUNT (*) AS n_total_masses
FROM
  area_day_church_masses
GROUP BY
  area_id,
  day_code
;

CREATE VIEW
  v_area_sub_day_masses
AS SELECT
  aa.in_area_id AS area_id,
  adcm.day_code AS day_code,
  COUNT (*) AS n_sub_masses
FROM
  area_areas AS aa
JOIN area_day_church_masses AS adcm ON
  adcm.area_id = aa.area_id
GROUP BY
  aa.in_area_id,
  adcm.day_code
;

CREATE VIEW
  v_area_day_info
AS SELECT
  a.id AS area_id,
  d.code AS day_code,
  SUM (adm.n_total_masses) AS n_total_masses,
  SUM (asdm.n_sub_masses) AS n_sub_masses
FROM
  days As d,
  areas AS a
LEFT OUTER JOIN v_area_day_masses AS adm ON
  adm.area_id = a.id AND
  adm.day_code = d.code
LEFT OUTER JOIN v_area_sub_day_masses AS asdm ON
  asdm.area_id = a.id AND
  asdm.day_code = d.code
GROUP BY
  a.id,
  d.code
;

CREATE VIEW
  v_area_areas
AS SELECT
  area_id,
  a1.name AS area_name,
  in_area_id,
  a2.name AS in_area_name
FROM
  area_areas AS aa
JOIN areas AS a1 ON
  a1.id = aa.area_id
JOIN areas AS a2 ON
  a2.id = aa.in_area_id
;

CREATE VIEW
  v_church_areas
AS SELECT
  church_id,
  c.name AS church_name,
  in_area_id,
  a.name AS in_area_name
FROM
  church_areas AS ca
JOIN churches AS c ON
  c.id = ca.church_id
JOIN areas AS a ON
  a.id = ca.in_area_id
;

CREATE VIEW
  v_church_days
AS SELECT
  church_id,
  day,
  COUNT (*) AS n_masses
FROM
  mass_times
GROUP BY
  church_id,
  day
;

CREATE VIEW
  v_area_days
AS SELECT
  ca.in_area_id AS area_id,
  day,
  SUM (n_masses) AS n_masses
FROM
  v_church_areas AS ca
JOIN v_church_days AS cd ON
  cd.church_id = ca.church_id
GROUP BY
  ca.in_area_id,
  day
;

CREATE VIEW
  v_church_day_masses
AS SELECT
  mti.church_id AS church_id,
  mti.day AS day_code,
  COUNT (*) AS n_masses
FROM
  mass_times AS mti
GROUP BY
  mti.church_id,
  mti.day
;

CREATE VIEW
  v_church_all_areas
AS SELECT DISTINCT
  adcm.church_id AS church_id,
  c.name AS church_name,
  adcm.area_id AS area_id,
  a.code AS area_code,
  a.name AS area_name
FROM
  area_day_church_masses AS adcm
JOIN churches AS c ON
  c.id = adcm.church_id
JOIN areas AS a ON
  a.id = adcm.area_id
;
