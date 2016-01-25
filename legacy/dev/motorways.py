import motorway
import database
from churches import church
from utils import *

class x_motorway_parsing (Exception):
  pass

_motorways = None
def motorways ():
  global _motorways
  if _motorways is None:
    _motorways = sorted (row.motorway for row in database.select ("SELECT DISTINCT motorway FROM motorway_churches"))
  return _motorways

_junctions = {}
def junctions (motorway=None):
  global _junctions
  if motorway not in _junctions:
    if motorway is None:
      _junctions[motorway] = sorted (row.junction for row in database.select ("SELECT DISTINCT junction FROM motorway_churches"))
    else:
      _junctions[motorway] = sorted (row.junction for row in database.select ("SELECT DISTINCT junction FROM motorway_churches WHERE motorway = ?", [motorway]))
  return _junctions[motorway]

_churches = {}
def churches (motorway, junction):
  global _churches
  if (motorway, junction) not in _churches:
    _churches[motorway, junction] = sorted (church (row.church_id) for row in database.select ("SELECT * FROM motorway_churches WHERE motorway = ? AND junction = ?", [motorway, junction]))
  return _churches[motorway, junction]

def motorway_junctions (motorway, from_junction=None, to_junction=None):
  jns = junctions (motorway)
  if from_junction is None: from_junction = jns[0]
  if to_junction is None: to_junction = jns[-1]
  return [j for j in jns if from_junction <= j <= to_junction]

JUNCTION_MASSES_SQL = """
  SELECT DISTINCT
     adcm.church_id AS church_id,
     c.name AS name,
     c.alias AS alias,
     adcm.hh24 AS hh24,
     adcm.eve AS eve,
     adcm.restrictions AS restrictions,
     mch.motorway AS motorway,
     mch.junction AS junction,
     mch.distance AS distance,
     mch.notes AS notes
  FROM
    area_day_church_masses AS adcm
  JOIN churches AS c ON
    c.id = adcm.church_id
  JOIN motorway_churches AS mch ON
    mch.church_id = adcm.church_id
  WHERE
    adcm.day_code = ? AND
    mch.motorway = ?
"""
def junction_masses (day, motorway_junctions):
  masses = []
  for motorway, junctions in from_string (motorway_junctions):
    data = database.select (JUNCTION_MASSES_SQL, (day, motorway))
    masses.extend (mass for mass in data if mass.junction in junctions)
  return masses

#
# A motorway junctions string has a motorway
# plus at least one junction, possibly two
# separated by a dash, eg:
# M4 J1, M5 J2-J10, M6 J2-3
#
def from_string (s):
  try:
    result = set ()
    for mway_jns in [i.strip () for i in s.split (",")]:
      items = mway_jns.split ()
      if len (items) == 1:
        m, js = items[0], "J1-99"
      elif len (items) == 2:
        m, js = items
      else:
        raise x_motorway_parsing
      mway = motorway.Motorway (m)
      js = js.split ("-")
      jns = [motorway.Junction (js[0])]
      if len (js) > 1:
        jns.append (motorway.Junction (js[1]))
      else:
        jns.append (jns[0])
      jns.sort ()
      result.add ((mway, tuple (motorway_junctions (mway, jns[0], jns[1]))))

    return result
  except:
    raise x_motorway_parsing
