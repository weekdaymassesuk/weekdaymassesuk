from __future__ import generators
import math
import datetime
import urllib

import i18n

import config
import database
import utils
import days
import postcode
from distance import Distance

def church (id=None, full_name=None):
  if id is not None:
    for row in database.select (u"SELECT id AS church_id, name AS church_name, * FROM churches WHERE id = ?", [int (id)]):
      return row
  elif full_name is not None:
    name, alias = full_name
    for row in database.select (u"SELECT id AS church_id, name AS church_name, * FROM churches WHERE name = ? and alias = ?", (utils.quoted (name), utils.quoted (alias))):
      return row
  else:
    raise RuntimeError, u"Id or Name must be specified"

def church_name (church=None, name_alias=(None, None)):
  if church:
    name, alias = church.name, church.alias
  else:
    name, alias = name_alias

  if alias:
    return u"%s (%s)" % (name, alias)
  else:
    return name

def church_areas (church_id):
  for row in database.select (u"SELECT in_area_id FROM church_areas WHERE church_id = ?", [church_id]):
    yield row.in_area_id

def church_is_in_area(church_id, area_code):
    return bool(database.one("SELECT * FROM v_church_all_areas WHERE church_id = ? AND area_code = ?", [church_id, area_code]))

def mass_times (church, day_code):
  for row in database.select (u"SELECT * FROM mass_times WHERE church_id = ? AND day = ? ORDER BY eve, hh24", (church.id, day_code)):
    yield "%s%s" % (row.hh24, " (eve)" if row.eve else "")

def churches_in_area (area_id):
  for c in database.select (u"SELECT DISTINCT church_id FROM area_day_church_masses WHERE area_id = ? AND church_id IS NOT NULL", [area_id]):
    yield church (id=c.church_id)

def churches_near_postcode (outcode, distance, units):
  """Find all churches within <distance> <units> of <outcode>"""
  UNIT_METRES = {
    u"miles" : 1609,
    u"km" : 1000
  }
  #
  # sqlite doesn't have a sqrt function, so
  # pull out all churches within the bounding
  # square (which will narrow it down considerably)
  #
  Q_CHURCHES = u"""
    SELECT
      id,
      x_coord,
      y_coord
    FROM
      churches
    WHERE
      ABS (x_coord - ?) < ? AND
      ABS (y_coord - ?) < ?
  """
  metres = float (distance) * UNIT_METRES[units]
  coords = postcode.postcode (outcode).coords ()
  if coords:
    x, y = coords
    for c in database.select (Q_CHURCHES, (x, metres, y, metres)):
      dx = x - c.x_coord
      dy = y - c.y_coord
      distance = math.sqrt ((dx * dx) + (dy * dy))
      if distance <= metres:
        yield church (id=c.id)

def shrines_in_area (area_id):
  SELECT_SQL = u"""
    SELECT DISTINCT
      church_id
    FROM
      area_day_church_masses AS adcm
    JOIN churches AS c ON
      c.id = adcm.church_id
    WHERE
      c.is_shrine = 1 AND
      adcm.area_id = ?
  """
  for c in database.select (SELECT_SQL, [area_id]):
    yield church (id=c.church_id)

def churches_in_postcode_area (area_id, postcode_area):
  for _church in churches_in_area (area_id):
    p = postcode.postcode (_church.postcode)
    if p.letters == postcode_area:
      yield _church

def churches_near_junction (motorway, junction):
  SELECT_SQL = """
    SELECT
      mch.church_id
    FROM
      motorway_churches AS mch
    WHERE
      mch.motorway = ? AND
      mch.junction = ?
  """
  for c in database.select (SELECT_SQL, [motorway, junction]):
    yield church (id=c.church_id)

def motorway_junctions (church_id):
  SELECT_SQL = """
    SELECT
      mch.motorway,
      mch.junction,
      mch.distance,
      mch.distance / 1609.0 AS miles
    FROM
      motorway_churches AS mch
    WHERE
      mch.church_id = ?
  """
  for j in database.select (SELECT_SQL, [church_id]):
    yield j

def junction_as_html (junction):
  if junction.distance:
    distance = " (%s miles)" % Distance (junction.distance).as_miles ()
  else:
    distance = ""
  return "%s %s" % (junction.motorway, junction.junction) + distance

church_template = i18n.load_template ("church.html")
def church_as_html (church, renderer):
  dictionary = dict (church=church)
  dictionary['name'] = church_name (church)
  dictionary['days'] = days.days ()
  times = {}
  for day in days.days ():
    field_name = u'%s_mass_times' % utils.code (day.name)
    if church[field_name]:
      times[day.code] = [field.strip () for field in church[field_name].split (",")]
    else:
      times[day.code] = list (mass_times (church, day.code))
  dictionary['times'] = times
  #
  # eg 609327 WeekdayMassTimes: 7am (In small chapel beside Sacristy); \r\n+ Tue,Wed,Fri 10am(Korean), Thu 7pm(Korean)
  #
  dictionary['junctions'] = list (motorway_junctions (church.id))
  dictionary['is_gb'] = church_is_in_area(church.id, "gb")
  dictionary['confessions'] = (church.confession_times or "").replace("\r\n", "<br/>")
  return renderer (church_template, dictionary)

def ids_from_coords ((lat0, long0), (lat1, long1)):
  return [row.id for row in
    database.select (
      "SELECT id FROM churches WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?",
      (long0, long1, lat0, lat1)
    )
  ]

def ascoords ((lat0, long0), (lat1, long1), day_code="K", language="en"):
  return [
    dict (id=c.id, name=church_name (c), latitude=str (c.latitude), longitude=str (c.longitude), text=church_as_html (c, i18n.translator (language)), masstimes=[]) for \
      c in (church (id) for id in ids_from_coords ((lat0, long0), (lat1, long1)))
  ]


if __name__ == '__main__':
  pass
