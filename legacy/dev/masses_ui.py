from __future__ import generators
import os, sys
import re

import config
import areas, days, churches, masses
import i18n
import utils
from doc import Doc
import ui

class MassesDoc (Doc):

    def __init__ (self, request, language, day, area):
        Doc.__init__ (self, request, language)
        self.day = day
        self.area = area

    def title (self):
        return self.translate ("masses_%s_masses_in_area" % self.day.code, day=self.translate ("day_%s" % self.day.code), area=self.area.name)

    def body (self):
        contents = []

        area_churches = [churches.church (c) for c in areas.all_churches_in (self.area.id)]
        if self.area.latitude and self.area.longitude:
            if self.area.zoom:
                zoom = "zoom=%s" % self.area.zoom
            else:
                zoom = ""
            contents.append (
                '<p class="breadcrumbs"><a href="/%s/map?day=%s&lat=%s&lon=%s&%s">%s</a></p>' %
                (self.language, self.day.code, self.area.latitude, self.area.longitude, zoom, self.translate ("general_locate_on_map"))
            )

        area_breadcrumbs = []
        containing_areas = areas.in_areas (self.area.id)
        if len (containing_areas) > 1:
            for area_id in reversed (containing_areas):
                area = areas.area (id=area_id)
                if area_id == self.area.id:
                    area_breadcrumbs.append ('<b>%s</b>' % area.name)
                else:
                    area_breadcrumbs.append ('<a href="/%s/day/%s/area/%s">%s</a>' % (self.language, self.day.code, area.code, area.name))
        if area_breadcrumbs:
            contents.append (
                '<p class="breadcrumbs">%s: %s</p>' % (
                    self.translate ("area_%s_masses" % self.day.code),
                    " &rarr; ".join (area_breadcrumbs)
                )
            )

        daily_masses = []
        for day in days.days ():
            if day.code != self.day.code:
                if areas.n_masses (self.area, day):
                    daily_masses.append ('<a href="/%s/day/%s/area/%s">%s</a>' % (self.language, day.code, self.area.area_code, self.translate ("day_%s" % day.code)))
        if daily_masses:
            contents.append ('<p class="breadcrumbs">%s: %s</p>' % (self.title (), " | ".join (daily_masses)))

        masses_data = {}
        for row in masses.masses (self.area.id, self.day.code):
            masses_data.setdefault ((row.eve, row.hh24), []).append (row)
        href_template = u"/%s/area/%s/churches" % (self.language, self.area.area_code)
        contents.extend (self.masses_table (masses_data, url_base=href_template))
        return "\n".join (contents)

    def masses_table (self, masses_data, url_base):
        html = []
        html.append (u"<table>")
        times = [((not eve), eve, hh24) for (eve, hh24) in masses_data.keys ()]
        times.sort ()
        for is_not_eve, eve, hh24 in times:
            klass = "%s-%s" % (hh24, "01"[int (eve or 0)])
            html.append (u'<tr><td colspan=2 class="%s"><h2>%s</h2></td></tr>' % (klass, i18n.masstime_format (self.translations, hh24 + (" (eve)" if eve else ""))))

            sortable_masses = []
            for m in masses_data[(eve, hh24)]:
                sort_key = []
                match = re.search (u"(M|-)(Tu|-)(W|-)(Th|-)(F|-)", m.restrictions)
                if match:
                    for i in range (1, len (match.groups ()) + 1):
                        if match.group (i) <> '-':
                            sort_key.append (i)
                else:
                    sort_key = [9, 9, 9, 9, 9]
                sort_key.append (m.name)
                sortable_masses.append ((sort_key, m))
            sortable_masses.sort ()

            html.append (u"<tr>")
            masstimes = [m[-1] for m in sortable_masses]
            for row in masstimes:
                if row.restrictions:
                    if len (row.restrictions) >= len (u"termtime"):
                        restrictions = u"<br>".join (row.restrictions.split (u" ", 1))
                    else:
                        restrictions = row.restrictions
                    html.append (u'<td class="%s"><p class=restrictions>%s</p></td>' % (klass, restrictions))
                else:
                    html.append (u'<td class="%s"></td>' % klass)

                href = utils.url (self.request, url_base, u"p%d" % row.church_id, with_query=False)
                html.append (u'<td class="%s"><p class=details><a href=%s>%s</a></p></td>' % (klass, href, churches.church_name (church=row)))
                html.append (u"</tr>")

        html.append (u"</table>")
        return html



class MassesUI (ui.UI):

    _q_exports = ["_q_index"]

    def __init__ (self, language, day, area):
        ui.UI.__init__ (self, language)
        self.day = day
        self.area = area

    def _q_index (self, request):
        return MassesDoc (request, self.language, self.area, self.day)
    __call__ = _q_index