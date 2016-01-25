from __future__ import generators

import config
import database

def day (code=None, name=None):
  if code is not None:
    for row in database.select (u"SELECT code AS day_code, name AS day_name, * FROM days WHERE code = ?", [code]):
      return row
  elif name is not None:
    for row in database.select (u"SELECT code AS day_code, name AS day_name, * FROM days WHERE name = ?", [name]):
      return row
  else:
    raise RuntimeError, u"Code or Name must be specified"

def days ():
  return database.select (u"SELECT code AS day_code, name AS day_name, * FROM days ORDER BY seq")

if __name__ == '__main__':
  pass

