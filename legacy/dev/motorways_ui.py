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
import i18n
import masses
import motorways
from churches_ui import ChurchesDoc
from hdos import days, hdos
from motorway import Motorway, Junction
import ui

class SearchDoc (doc.Doc):

  def __init__ (self, request, params, language):
    doc.Doc.__init__ (self, request, language, use_fs_cache=False)
    self.params = params

  def title (self):
    return self.translate ("motorways_title")

  def form (self):
    yield u'<form method="GET" action="%s">' % self.url (u"/%s/motorway" % self.language)
    yield u'<label>%s:</label> <select name="area">' % self.translate ("label_area")
    for code, name in [('gb', 'GB')]:
      if code == self.params[u'area']:
        yield u'<option value="%s" selected>%s</option>' % (code, name)
      else:
        yield u'<option value="%s">%s</option>' % (code, name)
    yield u'</select>'

    motorway_junctions = self.params.get ("motorway-junctions", "")
    yield u'<label>%s: </label> <input type="text" size="60" name="motorway-junctions" value="%s" />' % (
      self.translate ("label_motorway_junctions"),
      motorway_junctions
    )

    yield u'<label>%s: </label>' % self.translate ("label_day")
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

    yield '<p>%s</p>' % self.translate ("motorways_prompt")

  def by_time (self, masses):
    href_template = u"/%s/motorway/churches" % self.language

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
    # consisting of a list of masses at that time,
    # to be sorted by motorway junction, then restriction
    # and then by name.
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
      yield u'<td class="junction">%s</td>' % self.translate ("label_junction")
      yield u'<td class="notes">%s</td>' % self.translate ("label_notes")
      yield u'</tr>'

      sortable_masses = []
      for m in masses_data[(eve, hh24)]:
        sort_key = [(m.motorway, m.junction)]
        match = re.search (u"(M|-)(Tu|-)(W|-)(Th|-)(F|-)", m.restrictions)
        if match:
          for i in range (1, len (match.groups ()) + 1):
            if match.group (i) <> '-':
              sort_key.append (i)
            else:
              sort_key.append (9)
        else:
          sort_key.extend ([9, 9, 9, 9, 9])
        sortable_masses.append ((sort_key, m))
      sortable_masses.sort ()

      masstimes = [m[-1] for m in sortable_masses]
      for row in masstimes:
        yield u"<tr>"
        distance = row.distance
        distance_in_units = utils.from_metres (float (distance or 0), self.params['units'])
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
        yield u'<td class="distance">%s %s</td>' % (utils.format_distance (distance_in_units), self.params[u'units'])
        if row.junction:
          yield u'<td class="junction">%(motorway)s %(junction)s</td>' % row
        else:
          yield u'<td class="junction"></td>'
        yield u'<td class="notes"><i>%s</i></td>' % (row.notes or "")
        yield u"</tr>"

    yield u"</table>"

  def by_distance (self):
    yield ''

  def body (self):
    html = []
    html.extend (self.form ())
    html.append (u'<hr />')

    motorway_junctions = self.params[u'motorway-junctions']
    day = days ()[self.params[u'day']]
    day_name = self.translate ("day_%s" % day.code)

    masses_data = []
    if motorway_junctions:
      try:
        masses_data = motorways.junction_masses (day.code, motorway_junctions)
      except motorways.x_motorway_parsing:
        masses_data = []
        error_text = self.translate ("motorways_error")
        html.append (u'<p class="error">%s</p>' % error_text)
      else:
        if masses_data:
          html.append (u"<h2>%s</h2>" % self.translate ("motorways_masses_near", junctions=motorway_junctions, day=day_name))
          html.extend (self.by_time (masses_data))
        else:
          html.append (u"<h2>%s</h2>" % self.translate ("motorways_no_masses_near", junctions=motorway_junctions, day=day.name))

    if not masses_data:
      html.append (self.translate ("motorways_quick_choices"))
      for motorway in motorways.motorways ():
        html.append (u'<a href=/%s/motorway?motorway-junctions=%s>%s</a>&nbsp;&middot;&nbsp;' % (self.language, motorway, motorway))
    return u"\n".join (html)

class SearchUI (ui.UI):

  _q_exports = ["_q_index", "churches"]

  AREA = u"GB"
  MOTORWAY_JUNCTIONS = ""
  DAY = u"K"
  UNITS = u"miles"

  def __init__ (self, language):
    ui.UI.__init__ (self,language)

  def get_params (self, request):
    "Return a dict guaranteeing a key-value for each param, albeit None"
    fields = {}
    fields[u'area'] = request.form.get (u"area", self.AREA)
    fields[u'motorway-junctions'] = request.form.get (u"motorway-junctions", "").upper ()
    fields[u'day'] = request.form.get (u"day", self.DAY)
    fields[u'units'] = request.form.get (u"units", self.UNITS)
    return fields

  def _q_index (self, request):
    return SearchDoc (request, self.get_params (request), self.language)
  __call__ = _q_index

  def churches (self, request):
    fields = self.get_params (request)
    motorway_junctions = fields[u'motorway-junctions']

    churches_near_junction = set ()
    for motorway, junctions in motorways.from_string (motorway_junctions):
      for junction in junctions:
        churches_near_junction.update (
          churches.churches_near_junction (
            motorway,
            junction
          )
        )
    return ChurchesDoc (
      request,
      self.language,
      churches_near_junction,
      sort_keys = (),
      title=self.translate ("motorways_churches_near", junctions=motorway_junctions),
      use_fs_cache=False
    )
