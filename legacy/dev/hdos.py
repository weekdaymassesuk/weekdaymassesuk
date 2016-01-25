import datetime
import database

_days = None
def days ():
  global _days
  if _days is None:
    days = list (database.select (u"SELECT * FROM days"))
    _days = dict ([(row.code, row) for row in days])
  return _days

def hdos (area_name):
  SQL = u"""
    SELECT
      h.name AS name,
      h.yyyymmdd AS yyyymmdd,
      h.notes AS notes
    FROM
      hdos AS h
    JOIN areas AS a ON
      a.id = h.area_id
    WHERE
      a.name = ?
    AND
      h.yyyymmdd BETWEEN ? AND ?
    ORDER BY
      h.yyyymmdd
  """
  today = datetime.date.today ()
  sdny = today + datetime.timedelta (364)
  for row in database.select (SQL, (area_name, today.strftime ("%Y%m%d"), sdny.strftime ("%Y%m%d"))):
    yield row.as_tuple ()

