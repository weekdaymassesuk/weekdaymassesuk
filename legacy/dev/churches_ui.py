from __future__ import generators
import os, sys

import config
import utils
import areas, days, churches
import doc
import ui

class ChurchesDoc (doc.Doc):

  def __init__ (
    self,
    request,
    language,
    churches_iterator=None,
    sort_keys=(u"alias", u"name"),
    **kwargs
  ):
    doc.Doc.__init__ (self, request, language, **kwargs)
    self.churches_iterator = churches_iterator
    self.sort_keys = sort_keys

  def churches (self):
    for church in self.churches_iterator:
      yield church

  def body (self):
    if self.sort_keys:
      sortable = []
      for church in self.churches ():
        sortable.append ([church[key] for key in self.sort_keys] + [church])
      sortable.sort ()
      parishes = [s[-1] for s in sortable]
    else:
      parishes = list (self.churches ())

    parishes_as_html = [churches.church_as_html (church, self.renderer ()) for church in parishes]
    return u"\n".join (parishes_as_html)

class ChurchesUI (ui.UI):

  _q_exports = ["_q_index"]

  def __init__ (self, language, area):
    ui.UI.__init__ (self, language)
    self.area = area

  def _q_index (self, request):
    return AreaChurchesDoc (request, self.language, self.area)
  __call__ = _q_index