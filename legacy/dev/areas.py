from __future__ import generators
import config
import database

def area (id=None, code=None, day_code=None):
  ID_SQL = u"""
  SELECT
    id AS area_id,
    code AS area_code,
    name AS area_name,
    id,
    code,
    name,
    weekday_website,
    sunday_website,
    saturday_website,
    holy_day_of_obligation_website,
    details,
    is_external,
    area_order,
    latitude0,
    longitude0,
    latitude1,
    longitude1,
    latitude,
    longitude,
    zoom,
    NULL AS n_total_masses
  FROM
    areas
  WHERE
    areas.id = ?
  """

  ID_AND_DAY_SQL = u"""
  SELECT
    id AS area_id,
    code AS area_code,
    name AS area_name,
    id,
    code,
    name,
    weekday_website,
    sunday_website,
    saturday_website,
    holy_day_of_obligation_website,
    details,
    is_external,
    area_order,
    latitude0,
    longitude0,
    latitude1,
    longitude1,
    latitude,
    longitude,
    zoom,
    SUM (n_total_masses) AS n_total_masses
  FROM
    areas
  LEFT OUTER JOIN v_area_day_masses AS adm ON
    adm.area_id = areas.id AND
    adm.day_code = ?
  WHERE
    areas.id = ?
  GROUP BY
    area_id,
    area_name,
    id,
    name,
    weekday_website,
    sunday_website,
    saturday_website,
    holy_day_of_obligation_website,
    details,
    is_external,
    area_order
  """

  CODE_SQL = u"""
  SELECT
    id AS area_id,
    code AS area_code,
    name AS area_name,
    id,
    code,
    name,
    weekday_website,
    sunday_website,
    saturday_website,
    holy_day_of_obligation_website,
    details,
    is_external,
    area_order,
    latitude0,
    longitude0,
    latitude1,
    longitude1,
    latitude,
    longitude,
    zoom,
    NULL AS n_total_masses
  FROM
    areas
  WHERE
    areas.code = ?
  """

  CODE_AND_DAY_SQL = u"""
  SELECT
    id AS area_id,
    code AS area_code,
    name AS area_name,
    id,
    code,
    name,
    weekday_website,
    sunday_website,
    saturday_website,
    holy_day_of_obligation_website,
    details,
    is_external,
    area_order,
    latitude0,
    longitude0,
    latitude1,
    longitude1,
    latitude,
    longitude,
    zoom,
    SUM (n_total_masses) AS n_total_masses
  FROM
    areas
  LEFT OUTER JOIN v_area_day_masses AS adm ON
    adm.area_id = areas.id AND
    adm.day_code = ?
  WHERE
    areas.code = ?
  GROUP BY
    area_id,
    area_name,
    id,
    name,
    weekday_website,
    sunday_website,
    saturday_website,
    holy_day_of_obligation_website,
    details,
    is_external,
    area_order
  """

  if id is not None:
    if day_code is not None:
      for row in database.select (ID_AND_DAY_SQL, (day_code, id)): return row
    else:
      for row in database.select (ID_SQL, [id]): return row

  elif code:
    if day_code is not None:
      for row in database.select (CODE_AND_DAY_SQL, [day_code, code]): return row
    else:
      for row in database.select (CODE_SQL, [code]): return row

  else:
    raise RuntimeError, u"Id or Code must be specified"

def in_areas (area_id):
  area_ids = [area_id]
  for a in database.select (u"SELECT in_area_id FROM area_areas WHERE area_id = ?", [int (area_id)]):
    area_ids.extend (in_areas (a.in_area_id))
  return area_ids

def areas_in (area_id):
  area_ids = set ([area_id])
  for sub_area in database.select (u"SELECT area_id FROM area_areas WHERE in_area_id = ?", [int (area_id)]):
    area_ids |= areas_in (sub_area.area_id)
  return area_ids

def areas_in_immediate (area_id):
  for area in database.select (u"SELECT area_id FROM area_areas WHERE in_area_id = ?", [int (area_id)]):
    yield area.area_id

def churches_in (area_id):
  for row in database.select (u"SELECT church_id FROM church_areas WHERE in_area_id = ?", [area_id]):
    yield row.church_id

def all_churches_in (in_area_id):
  for church_id in churches_in (in_area_id):
    yield church_id
  for area_id in areas_in_immediate (in_area_id):
    for church_id in all_churches_in (area_id):
      yield church_id

def masses_in (area, day):
  for row in database.select (u"SELECT * FROM v_area_day_masses WHERE area_id = ? AND day_code = ?", [area.id, day.code]):
    yield row

def n_masses (area, day):
  for row in masses_in (area, day):
    return int (row.n_total_masses)
  else:
    return 0

AREA_TREE_SQL = u"""
  SELECT
    aa.area_id AS area_id,
    aa.area_name AS area_name,
    aa.in_area_id AS in_area_id,
    aa.in_area_name AS in_area_name
  FROM
    v_area_areas AS aa
  JOIN areas AS a ON
    a.name = aa.area_name
  WHERE
    aa.in_area_name = ?
  ORDER BY
    a.area_order DESC,
    aa.area_name
"""

def area_tree (start_area, start_level=0):
  yield area (id=start_area.area_id), start_level
  for a in database.select (AREA_TREE_SQL, [start_area.area_name]):
    for branch in area_tree (a, start_level+1):
      yield branch

TOP_LEVEL_SQL = """
  SELECT
    a.id
  FROM
    areas AS a
  WHERE NOT EXISTS (
    SELECT *
    FROM area_areas AS aa
    WHERE aa.area_id = a.id
  )
"""
def top_level_areas ():
  return [area (id=row.id) for row in database.select (TOP_LEVEL_SQL)]

if __name__ == '__main__':
  pass
