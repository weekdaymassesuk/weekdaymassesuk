from __future__ import generators
import os, sys

import config
import database
import utils

MASSES_SQL = u"""
  SELECT
    church_id,
    name,
    alias,
    hh24,
    eve,
    restrictions
  FROM
    area_day_church_masses AS adcm
  JOIN churches ON
    id = adcm.church_id
  WHERE
    adcm.area_id = ? AND
    adcm.day_code = ?
  ORDER BY
    adcm.eve,
    adcm.hh24,
    adcm.restrictions,
    adcm.church_id
"""
def masses (area_id, day_code):
  for row in database.select (MASSES_SQL, (area_id, day_code)):
    yield row

#
# The DISTINCT is a bit of a fudge,
#  because I'm essentially using a table
#  containing denormalised area-driven
#  data but without the area.
#
MASSES_BY_CHURCH_SQL = u"""
  SELECT DISTINCT
    church_id,
    name,
    alias,
    hh24,
    eve,
    restrictions,
    x_coord,
    y_coord,
    public_transport
  FROM
    area_day_church_masses AS adcm
  JOIN churches ON
    id = adcm.church_id
  WHERE
    adcm.day_code = ?
  ORDER BY
    adcm.eve,
    adcm.hh24,
    adcm.restrictions,
    adcm.church_id
"""
def masses_by_church (church_ids, day_code):
  for row in database.select (MASSES_BY_CHURCH_SQL, [day_code]):
    if row.church_id in church_ids:
      yield row
