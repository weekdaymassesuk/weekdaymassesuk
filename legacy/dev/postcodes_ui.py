from __future__ import generators
import os, sys
import datetime
import math
import re

import config
import database
import utils
import doc
import areas
import churches
import masses
import masses_ui
import postcode
from churches_ui import ChurchesDoc
import ui
import i18n

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

_days = None
def days ():
  global _days
  if _days is None:
    days = list (database.select (u"SELECT * FROM days"))
    _days = dict ([(row.code, row) for row in days])
  return _days

def format_distance (n_units):
  return u"%0.1f" % n_units

class SearchDoc (doc.Doc):

  UNITS = [u'miles', u'km']

  def __init__ (self, request, params, language):
    doc.Doc.__init__ (self, request, language, use_fs_cache=False)
    self.params = params

  def title (self):
    return self.translate ("postcodes_search_title")

  def form (self):
    pcode = self.params[u'postcode']
    if pcode.is_valid ():
      outcode = pcode.prefix ()
    else:
      outcode = ""

    yield u'<form method="GET" action="%s">' % self.url (u"/%s/postcode" % self.language)
    yield u'<label>%s </label> <select name="area">' % self.translate ("label_area")
    for code, name in postcode.postcode_areas ():
      if code == self.params[u'area']:
        yield u'<option value="%s" selected>%s</option>' % (code, name)
      else:
        yield u'<option value="%s">%s</option>' % (code, name)
    yield u'</select>'
    yield u'<label>%s: </label><input type="text" name="postcode" value="%s" />' % (self.translate ("label_postcode"), outcode)
    yield u'<label>%s: </label><input type="text" name="distance" value="%s" />' % (self.translate ("label_distance"), self.params['distance'])
    yield u'<select name="units">'
    for unit in self.UNITS:
      unit_name = self.translate ("unit_%s" % unit)
      if unit == self.params[u'units']:
        yield u'<option value="%s" selected>%s</option>' % (unit, unit_name)
      else:
        yield u'<option value="%s">%s</option>' % (unit, unit_name)
    yield u'</select>'
    yield u'<label>%s: </label>'  % self.translate ("label_day")
    yield u'<select name="day">'
    for day_code, day in days ().items ():
      day_name = self.translate ("day_%s" % day_code)
      if day_code == self.params[u'day']:
        yield u'<option value="%s" selected>%s</option>' % (day_code, day_name)
      else:
        yield u'<option value="%s">%s</option>' % (day_code, day_name)
    yield u'</select>'
    yield u'<input type="submit" value="%s">' % self.translate ("general_button_find")
    yield u'</form>'

  def by_time (self, masses):
    pcode = self.params[u'postcode']
    href_template = u"/%s/postcode/churches" % self.language

    if self.params[u'day'] == u'H' and self.language == "en":
      area_hdos = hdos (self.params[u'area'])
      if area_hdos:
        yield u'<table cellspacing="0" id="hdos">'
        yield u'<thead><th>%s</th><th>%s</th><th>%s</th></thead>' % tuple (self.translate ("label_%s" % f) for f in "feast date notes".split ())
        for name, yyyymmdd, notes in area_hdos:
          y, m, d = [int (i) for i in yyyymmdd[:4], yyyymmdd[4:6], yyyymmdd[6:]]
          yield u'<tr>'
          yield u'<td class="name">%s</td>' % name
          yield u'<td class="yyyymmdd">%s</td>' % datetime.date (y, m, d).strftime ("%d %b %Y")
          yield u'<td class="notes">%s</td>' % (notes or "")
          yield u'</tr>'
        yield u'</table>'

    yield u'<table cellspacing="0" class="by-time">'

    #
    # Construct a dictionary, keyed by time of day
    #  consisting of a list of masses at that time,
    #  to be sorted by restriction and then by name.
    #
    masses_data = {}
    for row in masses:
      masses_data.setdefault ((row.eve, row.hh24), []).append (row)
    times = [((not eve), eve, hh24) for (eve, hh24) in masses_data.keys ()]
    times.sort ()

    for is_not_eve, eve, hh24 in times:
      #
      # Desperately artificial vertical space before time-break header
      # No amount of margin-top on tr.header seems to work
      #
      yield u'<tr class="filler"><td colspan="4">&nbsp;</td></tr>'

      yield u'<tr class="header">'
      yield u'<td class="time">%s</td>' % i18n.masstime_format (self.translations, hh24 + (" (eve)" if eve else ""))
      yield u'<td class="church">&nbsp;</td>'
      yield u'<td class="distance">%s</td>' % self.translate ("label_distance")
      yield u'<td class="transport">%s</td>' % self.translate ("label_station")
      yield u'</tr>'

      sortable_masses = []
      for m in masses_data[(eve, hh24)]:
        sort_key = [utils.distance ((m.x_coord, m.y_coord), pcode.coords ())]
        match = re.search (u"(M|-)(Tu|-)(W|-)(Th|-)(F|-)", m.restrictions)
        if match:
          for i in range (1, len (match.groups ()) + 1):
            if match.group (i) <> '-':
              sort_key.append (i)
            else:
              sort_key.append (9)
        else:
          sort_key.extend ([9, 9, 9, 9, 9])
        sort_key.append (m.name)
        sortable_masses.append ((sort_key, m))
      sortable_masses.sort ()

      yield u"<tr>"
      masstimes = [m[-1] for m in sortable_masses]
      for row in masstimes:
        distance = utils.distance ((row.x_coord, row.y_coord), pcode.coords ())
        distance_in_units = utils.from_metres (distance, self.params[u'units'])
        if row.restrictions:
          if len (row.restrictions) >= len (u"termtime"):
            restrictions = u"<br>".join (row.restrictions.split (" ", 1))
          else:
            restrictions = row.restrictions
          yield u'<td class="restrictions"><p class="restrictions">%s</p></td>' % restrictions
        else:
          yield u'<td class="restrictions"></td>'

        href = self.url (href_template, u"p%d" % row.church_id)
        yield u'<td class="church"><p class="details"><a href="%s">%s</a></p></td>' % (href, churches.church_name (church=row))
        yield u'<td class="distance">%s %s</td>' % (format_distance (distance_in_units), self.params[u'units'])
        if row.public_transport:
          yield u'<td class="transport">%s</td>' % row.public_transport
        else:
          yield u'<td class="transport"></td>'
        yield u"</tr>"

    yield u"</table>"

  def by_distance (self):
    yield ''

  def body (self):
    html = []
    html.extend (self.form ())
    html.append (u'<p class="notes"><strong>NB:</strong>&nbsp;%s</p>' % self.translate ("postcodes_nb"))
    html.append (u'<hr />')

    full_postcode = self.params[u'postcode']
    if full_postcode.is_valid ():
      outcode = full_postcode.prefix ()
    else:
      outcode = ''
    distance = self.params[u'distance']
    units = self.params[u'units']
    day = days ()[self.params[u'day']]
    day_name = self.translate ("day_%s" % day.code)
    if full_postcode:
      if not full_postcode.is_valid ():
        html.append (u"<p class=warning>%s</p>" % self.translate ("postcodes_invalid_postcode", postcode=full_postcode.postcode_text))
      elif not full_postcode.coords ():
        html.append (u"<p class=warning>%s</p>" % self.translate ("postcodes_nocoords_postcode", postcode=outcode))
      else:
        churches_data = list (churches.churches_near_postcode (outcode, distance, units))
        if churches_data:
          html.append (u"<h2>%s</h2>" % self.translate ("postcodes_masses_within", distance=format_distance (distance), units=units, outcode=outcode, day=day_name))
          masses_data = masses.masses_by_church ([c.id for c in churches_data], day.code)
          html.extend (self.by_time (masses_data))
        else:
          html.append (u"<h2>%s</h2>" % self.translate ("postcodes_no_masses_within", distance=format_distance (distance), units=units, outcode=outcode, day=day.name))

    return "\n".join (html)

class SearchUI (ui.UI):

  _q_exports = ["_q_index", "churches"]

  AREA = u"GB"
  DISTANCE = 1.0
  UNITS = u"miles"
  DAY = u"K"

  def __init__ (self, language):
    ui.UI.__init__ (self, language)

  def get_params (self, request):
    "Return a dict guaranteeing a key-value for each param, albeit None"
    fields = {}
    fields[u'area'] = request.form.get (u"area", self.AREA)
    fields[u'distance'] = float (request.form.get (u"distance", self.DISTANCE))
    fields[u'units'] = request.form.get (u"units", self.UNITS)
    fields[u'postcode'] = postcode.postcode (request.form.get (u"postcode", ""))
    fields[u'day'] = request.form.get (u"day", self.DAY)
    return fields

  def _q_index (self, request):
    return SearchDoc (request, self.get_params (request), self.language)
  __call__ = _q_index

  def churches (self, request):
    fields = self.get_params (request)
    postcode = fields[u'postcode']
    distance = fields[u'distance']
    units = fields[u'units']

    churches_near_postcode = churches.churches_near_postcode (
      postcode.prefix (),
      distance,
      units
    )
    return ChurchesDoc (
      request,
      self.language,
      churches_near_postcode,
      sort_keys = (),
      title = self.translate ("postcodes_churches_within", distance=format_distance (distance), units=units, outcode=postcode.prefix ()),
      use_fs_cache=False
    )

class PostcodesDoc (doc.Doc):

  def __init__ (self, request, language, area):
    doc.Doc.__init__ (self, request, language)
    self.area = area

  def title (self):
    return self.translate ("postcodes_title", area=self.area.name)

  def postcode_areas (self):
    postcodes = set ()
    for church in churches.churches_in_area (self.area.id):
      p = postcode.postcode (church.postcode)
      if p.letters:
        postcodes.add ((p.order (), p.letters, p.in_london ()))

    return list (postcodes)

  def body (self):
    html = []
    postcode_areas = self.postcode_areas ()
    postcode_areas.sort ()

    _first_letter = None
    _in_london = None
    for (order, postcode_area, in_london) in postcode_areas:
      if in_london <> _in_london:
        _in_london = in_london
        if _in_london:
          html.append (u'<p><span class="label">%s: </span>' % self.translate ("postcodes_london"))

      if not in_london and _first_letter <> postcode_area[0]:
        _first_letter = postcode_area[0]
        html.append (u'<p><span class="label">%s: </span>' % _first_letter)

      html.append (u'<a href="%s" class="internal">[%s]</a>' % (postcode_area, postcode_area))

    return u"\n".join (html)

class PostcodesUI (ui.UI):

  _q_exports = ["_q_index", "churches"]

  def __init__ (self, language, area):
    ui.UI.__init__ (self, language)
    self.area = area

  def _q_index (self, request):
    return PostcodesDoc (request, self.language, self.area)
  __call__ = _q_index

  def _q_lookup (self, request, component):
    self.postcode_area = component
    return ChurchesDoc (
      request,
      self.language,
      self.churches_in_postcode (),
      sort_keys = (),
      title=self.translate ("postcodes_churches_in_postcode_area", area=self.area.name, postcode_area=self.postcode_area)
    )

  def churches_byoutcode (self, churches):
    sortable = [(postcode.postcode (church.postcode, london_is_special=False), church.alias, church.name, church) for church in churches]
    sortable.sort ()
    for s in sortable:
      yield s[-1]

  def churches_in_postcode (self):
    parishes = churches.churches_in_postcode_area (self.area.id, self.postcode_area)
    for church in self.churches_byoutcode (parishes):
      yield church

  def churches_in_area (self):
    parishes = churches.churches_in_area (self.area.id)
    for church in self.churches_byoutcode (parishes):
      yield church

  def churches (self, request):
    return ChurchesDoc (
      request,
      self.language,
      self.churches_in_area (),
      sort_keys = (),
      title = self.translate ("postcodes_all_churches", area=self.area.name)
    )
