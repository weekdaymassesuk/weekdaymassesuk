from __future__ import generators

import config
import database

SUBJECT_LINKS_SQL = """
SELECT
  type,
  subject,
  id,
  title,
  link,
  sequence
FROM
  links
"""

def subject_links ():
  for row in database.select (SUBJECT_LINKS_SQL):
    yield row

if __name__ == '__main__':
  pass
