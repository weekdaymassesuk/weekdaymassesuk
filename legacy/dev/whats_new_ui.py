from __future__ import generators
import os, sys
import re

import config
import utils
import doc
import whats_new
import areas
import churches
import ui

class WhatsNewDoc (doc.Doc):

  def __init__ (self, request, language):
    doc.Doc.__init__ (self, request, language)

  def title (self):
    return self.translate ("whatsnew_title")

  def body (self):
    updated_on = None
    n_update = 1

    updates = []
    for update in whats_new.latest_updates ():
      if updated_on <> update.updated_on.toordinal ():
        n_update += 1
        if n_update > config.N_UPDATES:
          break
        updated_on = update.updated_on.toordinal ()
        updates.append (u'<p class="whatsnew_date">%s</p>' % utils.format_date (update.updated_on))

      text = update.text
      church_match = re.search (u"\[(.*)\]", text)
      if church_match:
        church_name = church_match.group (1)
        if "," in church_name:
          name, alias = [i.strip () for i in church_name.split (",", 1)]
        else:
          name, alias = church_name, ""
        church = churches.church (full_name=(name, alias))
        if church:
          for area_id in churches.church_areas (church.id):
            area = areas.area (area_id)
            link = utils.church_link (self.request, self.language, area=area, church=church)
            href = u'<a href="%s">%s</a>' % (link, churches.church_name (church))
            text = text.replace (u"[%s]" % church_name, href)
            break
          else:
            text = text.replace (u"[", u"").replace (u"]", u"")
            text += u"<!-- No area found for church id %d -->" % church.id
        else:
          text = text.replace (u"[", u"").replace (u"]", u"")

      updates.append (u'<p class="details">%s</p>' % text)

    return u"\n".join (updates)

class WhatsNewUI (ui.UI):

  _q_exports = ["_q_index"]

  def _q_index (self, request):
    return WhatsNewDoc (request, self.language)
  __call__ = _q_index
