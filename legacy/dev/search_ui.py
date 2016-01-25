import os, sys
import datetime
import operator
try:
  import json
except ImportError:
  import simplejson as json

import config
import database
import utils
import doc
import areas
from churches_ui import ChurchesDoc
import data_ui
import churches
import search
import ui

class SearchDoc (doc.Doc):

  def __init__ (self, request, params, language):
    doc.Doc.__init__ (self, request, language, use_fs_cache=False)
    self.area = areas.area (code=params['area'])
    self.terms = params['terms']

  def title (self):
    if self.terms:
      return self.translate ("search_churches_containing", area=self.area.name, terms=", ".join (self.terms))
    else:
      return self.translate ("search_churches")

  def form (self):
    yield u'<form method="GET" action="%s">' % self.url (u"/%s/search" % self.language)
    yield u'<label>%s:</label> <select name="area">' % self.translate ("label_area")
    for area in areas.top_level_areas ():
      if area.code == self.area.code:
        yield u'<option value="%(code)s" selected>%(name)s</option>' % area
      else:
        yield u'<option value="%(code)s">%(name)s</option>' % area
    yield u'</select>'

    yield u'<label>%s: </label> <input type="text" size="60" name="terms" value="%s" />' % (self.translate ("search_label_containing"), " ".join (self.terms))
    yield u'<input class="go-button" type="submit" value="%s">' % self.translate ("search_find_button")

  def body (self):
    html = []
    html.extend (self.form ())
    html.append (u'<hr />')

    href_template = u"/%s/search/churches" % self.language
    if self.terms:
      matching_churches = search.find_churches (self.area.area_code, self.terms)
      if matching_churches:
        for church_id in matching_churches:
          church = churches.church (church_id)
          href = self.url (href_template, u"p%d" % church.id)
          html.append ('<p><a href="%s">%s</a></p>' % (href, churches.church_name (church=church)))
      else:
        html.append ('<p>%s</p>' % self.translate ("search_none_found"))

    return u"\n".join (html)

class SearchUI (ui.UI):

  _q_exports = ["_q_index", "churches", "map_search"]

  AREA = config.ROOT_AREA_CODE

  def __init__ (self, language):
    ui.UI.__init__ (self, language)

  def get_params (self, request):
    "Return a dict guaranteeing a key-value for each param, possibly empty"
    fields = {}
    fields[u'area'] = request.form.get (u"area", self.AREA)
    terms = request.form.get (u"terms", "")
    if not isinstance (terms, basestring):
      terms = " ".join (terms)
    fields[u'terms'] = utils.filter_search_words (terms)
    fields[u'lat0'] = request.form.get (u"lat0")
    fields[u'lon0'] = request.form.get (u"lon0")
    fields[u'lat1'] = request.form.get (u"lat1")
    fields[u'lon1'] = request.form.get (u"lon1")
    fields[u'day'] = request.form.get (u"day")
    fields[u'threshold'] = request.form.get (u"threshold", 100)
    fields[u'n0'] = int (request.form.get (u"n0", 0))
    fields[u'n'] = int (request.form.get (u"n", 10))
    return fields

  def _q_index (self, request):
    return SearchDoc (request, self.get_params (request), self.language)
  __call__ = _q_index

  def map_search (self, request):
    request.response.set_content_type ("application/json")
    fields = self.get_params (request)
    terms = fields[u'terms']
    n0 = fields[u'n0']
    n = fields[u'n']
    cs = []
    cs.extend (churches.church (c) for c in search.find_churches ("gb", terms))
    cs.extend (churches.church (c) for c in search.find_churches ("outside-gb", terms))
    return json.dumps ([(c.name + (" (%s)" % c.alias if c.alias else ""), (float (c.latitude), float (c.longitude))) for c in cs][n0:n0+n])

  def churches (self, request):
    fields = self.get_params (request)
    if fields['lat0']:
      title = self.translate ("search_churches_on_map")
      area = data_ui.areas_in_coords (
        fields[u'lat0'], fields[u'lat1'],
        fields[u'lon0'], fields[u'lon1']
      )
      return request.redirect (("/%s/day/%s/area/%s" % (self.language, fields['day'], area.code)).encode ("iso-8859-1"))
    else:
      title = self.translate ("search_churches_containing", area=fields['area'], terms=u", ".join (fields['terms']))
      matching_churches = [churches.church (c) for c in search.find_churches (fields['area'], fields['terms'])]
      return ChurchesDoc (
        request,
        self.language,
        sorted (matching_churches, key=lambda c: (c.alias, c.name)),
        sort_keys = (),
        title=title,
        use_fs_cache=False
      )
