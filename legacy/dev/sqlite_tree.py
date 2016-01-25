import sqlite3

CHURCHES_IN_AREA_SQL = """SELECT
  c.id,
  c.name,
  c.alias
FROM
  churches AS c
JOIN church_areas AS ca ON
  ca.church_id = c.id
WHERE
  ca.in_area_id = ?
ORDER BY
  c.id
"""

AREAS_IN_AREA_SQL = """SELECT
  a.id,
  a.name,
  a.is_external
FROM
  areas AS a
JOIN area_areas AS aa ON
  aa.area_id = a.id
WHERE
  aa.in_area_id = ?
ORDER BY
  a.code
"""

def output (text="", level=0):
  print "  " * level + text.encode ("utf-8")

def tree (db, id, area, external, level=0):
  output ("%s%s" % (area.upper (), " (E)" if external else ""), level)
  for church_id, church_name, church_alias in db.execute (CHURCHES_IN_AREA_SQL, [id]):
    output (u"%s - %s (%d)" % (church_name, church_alias, church_id), level+1)
  for a_id, a_code, a_external in db.execute (AREAS_IN_AREA_SQL, [id]):
    tree (db, a_id, a_code, a_external, level+1)

if __name__ == '__main__':
  db = sqlite3.connect ("data/masses.db")
  for id, area, external in db.execute ("SELECT a.id, a.name, a.is_external FROM areas a WHERE NOT EXISTS (SELECT * FROM area_areas aa WHERE aa.area_id = a.id) ORDER BY a.code"):
    tree (db, id, area, external)
    output ()
