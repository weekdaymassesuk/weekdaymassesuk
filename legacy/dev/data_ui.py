import decimal
try:
  import json
except ImportError:
  import simplejson as json
import urllib

import config
import utils
import areas
import days
from churches import church_name, church_areas, mass_times
import database
import i18n
import ui

def churches_in_coords (lat0, lat1, long0, long1):
  return database.select ("""
    SELECT
      c.*
    FROM
      churches AS c
    WHERE
      c.longitude BETWEEN ? AND ? AND
      c.latitude BETWEEN ? AND ?
    """,
    (long0, long1, lat0, lat1)
  )

#
# Leave this -- theoretically superior -- algorithm
# in here for now
#
def areas_in_coords (lat0, lat1, long0, long1):
  for area in database.select ("""
    SELECT
      a.id
    FROM
      areas AS a
    WHERE
      a.latitude0 <= ? AND
      a.longitude0 <= ? AND
      a.latitude1 >= ? AND
      a.longitude1 >= ?
    ORDER BY
      ABS (a.latitude1 - a.latitude0) ASC,
      ABS (a.longitude1 - a.longitude0) ASC
    LIMIT
      1
    """,
    (lat1, long1, lat0, long0)
  ):
    return areas.area (area.id)

def areas_in_coords0 (lat0, lat1, long0, long1):
  cs = churches_in_coords (lat0, lat1, long0, long1)
  axs = {}
  for c in cs:
    for a_id in church_areas (c.id):
      axs.setdefault (a_id, []).append (c)
  area_id, n_churches = min (axs.items (), key=len)
  return areas.area (area_id)


def masses_by_church (church_id):
  return database.select ("SELECT mti.day, mti.hh24, mti.eve, mti.restrictions FROM mass_times AS mti WHERE mti.church_id = ?", (church_id,))

def timecode (hh24, eve):
  return str ("10"[bool (eve)]) + '-' + hh24

def add_html (church, field, label="", style=""):
  value = getattr (church, field)
  if value:
    return '<p class="%s"><span class="label">%s:</span> %s</p>' % (style or field, label or field.title (), value)
  else:
    return ""

church_template = i18n.load_template("church-all.html")
def church_as_html(church, renderer):
    dictionary = dict(church=church)
    dictionary['name'] = church_name(church)
    dictionary['days'] = days.days()
    times = {}
    for day in days.days():
        field_name = u'%s_mass_times' % utils.code(day.name)
        if church[field_name]:
            times[day.code] = [field.strip() for field in church[field_name].split(",")]
        else:
            times[day.code] = list(mass_times(church, day.code))
    dictionary['times'] = times
    return renderer(church_template, dictionary)

class DataUI (ui.UI):

  _q_exports = ["churches", "xlate", "box"]

  def __init__ (self, language):
    ui.UI.__init__ (self, language)
    self.translator = i18n.translator (self.language)
    self.renderer = i18n.renderer (self.language)

  def xlate (self, request):
    response = request.response
    response.cache = config.CACHE_FOR_SECS
    response.set_header ("cache-control", "max-age=%d" % config.CACHE_FOR_SECS)
    response.set_header ("last-modified", config.LAST_UPDATE.strftime (config.HTTP_TIMESTAMP))
    response.set_content_type ("text/plain; charset=%s" % config.OUTPUT_ENCODING)
    params = dict (request.form)
    key = params.pop ("key")
    return self.translate (key, **params).encode (config.OUTPUT_ENCODING)

  def box (self, request):
    response = request.response
    response.set_content_type ("application/json")

    lat = decimal.Decimal (request.form.get ("lat"))
    lon = decimal.Decimal (request.form.get ("lon"))
    nearest = database.one ("""
      SELECT
        distance (?, ?, latitude, longitude) AS dist,
        latitude, longitude
      FROM
        churches
      WHERE
        latitude IS NOT NULL AND
        longitude IS NOT NULL
      ORDER BY
        distance (?, ?, latitude, longitude) ASC
      LIMIT
        1
      """, [lat, lon, lat, lon]
    )
    dlat = lat - nearest.latitude
    dlon = lon - nearest.longitude
    return json.dumps ([float (lat - dlat), float (lon - dlon), float (lat + dlat), float (lon + dlon)])

  def churches (self, request):
    response = request.response
    response.cache = config.CACHE_FOR_SECS
    response.set_header ("cache-control", "max-age=%d" % config.CACHE_FOR_SECS)
    response.set_header ("last-modified", config.LAST_UPDATE.strftime (config.HTTP_TIMESTAMP))
    response.set_content_type ("application/json")

    lat0 = request.form.get ("lat0")
    lat1 = request.form.get ("lat1")
    long0 = request.form.get ("long0")
    long1 = request.form.get ("long1")

    churches = []
    masstimes = {}
    area = ""

    area = areas_in_coords (lat0, lat1, long0, long1)
    if area:
      area_code = area.code
      area_name = area.name
    else:
      area_code = area_name = ""
    possible_churches = list (churches_in_coords (lat0, lat1, long0, long1))
    for c in possible_churches:
      full_name = church_name (name_alias=(c.name, c.alias))
      church_masstimes = {}
      for m in masses_by_church (c.id):
        time = timecode (m.hh24, m.eve)
        hh12 = i18n.masstime_format (self.translations, m.hh24 + (" (eve)" if m.eve else ""))
        church_masstimes.setdefault (m.day, []).append (time)
        masstime_hh12, masstime_churches = masstimes.setdefault (m.day, {}).setdefault (time, (hh12, []))
        masstime_churches.append (dict (id=c.id, name=full_name, restrictions=m.restrictions))
      churches.append (dict (
        id=c.id,
        name=full_name,
        latitude=str (c.latitude),
        longitude=str (c.longitude),
        postcode = c.postcode,
        is_external = c.is_external,
        website = c.website,
        html=church_as_html(c, self.renderer),
        masstimes = church_masstimes
      ))

    return json.dumps ([churches, masstimes, len (possible_churches), (area_code, area_name)])
