from __future__ import generators

import database

ADVERTS_SQL = """
SELECT
    id,
    organisation,
    filename,
    url
FROM
    adverts
"""

def adverts():
    for row in database.select(ADVERTS_SQL):
        yield row

def random_advert():
    for row in database.select(ADVERTS_SQL + " ORDER BY RANDOM() LIMIT 1"):
        return row
