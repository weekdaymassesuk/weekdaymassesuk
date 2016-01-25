import math
import sqlite3

from config import *

#
# Decimal conversion temporarily included
#  here; hopefully patch will be accepted
#  into pysqlite
#
import decimal
def adapt_decimal (decimal):
  return str (decimal)
def convert_decimal (s):
  #
  # NB the Decimal constructor is over-sensitive
  # to leading spaces (and possibly trailing ones).
  #
  if s is None:
    return None
  try:
    return decimal.Decimal (s.strip ())
  except:
    raise Exception ("Problem converting %s" % s)
sqlite3.register_adapter (decimal.Decimal, adapt_decimal)
sqlite3.register_converter ("DECIMAL", convert_decimal)

import motorway
def adapt_motorway (m):
  return str (m)
def convert_motorway (m):
  if m is None:
    return None
  else:
    return motorway.Motorway (m)
sqlite3.register_adapter (motorway.Motorway, adapt_motorway)
sqlite3.register_converter ("MOTORWAY", convert_motorway)

def adapt_junction (j):
  return str (j)
def convert_junction (j):
  if j is None:
    return None
  else:
    return motorway.Junction (j)
sqlite3.register_adapter (motorway.Junction, adapt_junction)
sqlite3.register_converter ("JUNCTION", convert_junction)

sqlite3.register_converter("DATETIME", sqlite3.converters["TIMESTAMP"])

def _set (instance, attr, value):
  instance.__dict__[attr] = value

class Row (object):

  def __init__ (self, cursor, row):
    names = [d[0] for d in cursor.description]
    _set (self, '_description', dict ((name, index) for index, name in enumerate (names)))
    _set (self, "_row", list (row))

  def __getitem__ (self, index):
    if isinstance (index, int):
      return self._row[index]
    else:
      return self._row[self._description[index]]

  def __setitem__ (self, index, value):
    if isinstance (index, int):
      self._row[index] = value
    else:
      self._row[self._description[index]] = value

  def __getattr__ (self, key):
    try:
      return self._row[self._description[key]]
    except KeyError:
      raise AttributeError

  def __setattr__ (self, key, value):
    self._row[self._description[key]] = value

  def __repr__ (self):
    return "<Row: %s>" % self.as_string ()

  def __str__ (self):
    return self.as_string ()

  def as_tuple (self):
    return tuple (self._row)

  def as_dict (self):
    return dict ((name, self._row[index]) for name, index in self._description.items ())

  def as_string (self):
    return str (self.as_tuple ())

  def columns (self):
    columns = [(index, name) for name, index in self._description.items ()]
    columns.sort ()
    return [name for index, name in columns]

def distance (x1, y1, x2, y2):
  if None in (x1, y1, x2, y2):
    return None
  x1 = float (x1)
  y1 = float (y1)
  x2 = float (x2)
  y2 = float (y2)
  return math.sqrt (((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2)))

def connect (*args, **kwargs):
  #
  # Create a standard connection but with the built-in
  #  date/time handling enabled.
  #
  # NB DECLTYPES looks for the first word of the declared type,
  #  so you can declare a column of type DATE or TIMESTAMP, and
  #  pysqlite will automatically convert to and from a datetime.
  #
  connection = sqlite3.connect (
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    *args,
    **kwargs
  )

  #
  # Add a row-handler to allow attribute, index and dict-based columns
  #
  connection.row_factory = Row

  #
  # Add convenience functions to database
  #
  connection.create_function ("sqrt", 1, math.sqrt)
  connection.create_function ("distance", 4, distance)

  return connection

db = connect (DATABASE_NAME)

def execute (sql_statement, params=()):
  db.execute (sql_statement, params)

def executemany (sql_statement, params=[]):
  db.executemany (sql_statement, params)

def select (sql_statement, params=()):
  for row in db.execute (sql_statement, params):
    yield row

def one (sql_statement, params=()):
  for row in select (sql_statement, params):
    return row
