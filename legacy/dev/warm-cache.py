#!/usr/bin/env python
"""Warm the static HTML cache by pre-generating the 20 biggest areas

This invokes the standard publish/cache mechanism so shouldn't interfere with any
live requests: the cacheing logic should apply equally to both. The intention is
that this be run as a post-processing step after a data update to speed up access
to notoriously slow pages (which will cause the nginx -> apache gateway to time out).
"""
import os, sys
import itertools
import tempfile
import urlparse

from quixote import publish
import index_ui
import config
import database
from lib import cache

def languages():
    return [row.language for row in database.select("SELECT DISTINCT language FROM translations")]

def days():
    return ["A", "U", "K", "H"]

def areas():
    for area in database.select("SELECT * FROM areas"):
        yield area.code

def urls():
    #
    # Find the 50 most populous areas and generate their text
    # pages into the cache
    #
    areas = database.select("""
    SELECT
        a.code AS area_code,
        COUNT(DISTINCT adcm.church_id) AS n_churches
    FROM
        area_day_church_masses AS adcm
    JOIN areas AS a ON
        a.id = adcm.area_id
    GROUP BY
        a.code
    ORDER BY
        COUNT(DISTINCT adcm.church_id) DESC
    LIMIT
        3
    """)
    for n, area in enumerate(areas):
        print "%02d) %s (%s)" % (n + 1, area.area_code, area.n_churches)
        for language in languages():
            print "  ", language
            yield "/%s/area/%s/churches" % (language, area.area_code)
            for day in days():
                print "    ", day
                yield "/%s/day/%s/area/%s" % (language, day, area.area_code)

def get_environ(url):
    parts = urlparse.urlparse(url)
    env = dict(os.environ)
    env['REQUEST_URI'] = parts.path + parts.query
    env['PATH_INFO'] = parts.path
    env['SCRIPT_NAME'] = "/weekdaymasses.cgi"
    env['QUERY_STRING'] = parts.query
    env['SERVER_NAME'] = parts.netloc
    env['HTTP_HOST'] = parts.netloc
    return env

def generate(app, url):
    env = get_environ(url)
    with tempfile.TemporaryFile() as f:
        app.publish(f, f, f, dict(env))

def main(root_url="http://weekdaymasses.org.uk"):
    app = publish.Publisher(index_ui.IndexUI())
    if os.path.exists(config.QCONFIG_FILEPATH):
        app.read_config(config.QCONFIG_FILEPATH)
    system = os.environ.get("HTTP_HOST", "").split(".")
    if system[0] in ("local", "dev") and os.path.exists("dev.cfg"):
        app.read_config("dev.cfg")
    app.setup_logs()

    for url in urls():
        generate(app, root_url + url)

if __name__ == '__main__':
    main(*sys.argv[1:])
