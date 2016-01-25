import pyodbc

CHURCHES_IN_AREA_SQL = """SELECT
  c.id,
  c.Parish,
  c.Alias
FROM
  Churches c,
  Church2Area c2a
WHERE
  c2a.ChurchId = c.id
AND
  c2a.Area = ?
ORDER BY
  c.id
"""

def output (text="", level=0):
  print "  " * level + text.encode ("utf-8")

def tree (db, area, external, level=0):
  output ("%s%s" % (area.upper (), " (E)" if external else ""), level)
  for church in db.execute (CHURCHES_IN_AREA_SQL, [area]):
    output (u"%s - %s (%d)" % (church.Parish, church.Alias, church.id), level+1)
  for a in db.execute ("SELECT area, [external] FROM Areas WHERE in_area = ? ORDER BY area", [area]):
    tree (db, a.area, a.external, level+1)

if __name__ == '__main__':
  db = pyodbc.connect ("Driver={Microsoft Access Driver (*.mdb)};Dbq=data/masses.mdb;Uid=Admin;Pwd=;")
  for area in db.execute ("SELECT area, external FROM Areas WHERE in_area IS NULL ORDER BY area"):
    tree (db, area.area, area.external)
    output ()
