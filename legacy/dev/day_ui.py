from __future__ import generators
from quixote import errors

import utils
import config
import days
import areas
import area_tree_ui
import area_ui
from doc import Doc
import ui

class SpecificDayUI (ui.UI):

    _q_exports = ["_q_index"]

    def __init__ (self, language, day):
        ui.UI.__init__ (self, language)
        self.day = day

    def area_tree_filter (self, area):
        """Keep areas in the tree if they have any
         masses in this area on this day or if they
         have a website defined for this day.
        """
        website_fieldname = u'%s_website' % utils.code (self.day.name)
        if area[website_fieldname]:
            return True
        else:
            for row in areas.masses_in (area, self.day):
                return True
            else:
                return False

    def _q_index (self, request):
        return Doc (
            request=request,
            filename=u"html/%s/day.ihtml" % self.language,
            title=self.translate ("area_%s_masses" % self.day.code)
        )
    __call__ = _q_index

    def area_tree_href (self, request, area):
        return utils.area_link (request, area, self.day, self.language)

    def _q_lookup (self, request, component):
        if component == u"area_tree":
            return area_tree_ui.AreaTreeUI (
                self.language,
                self.translate ("area_%s_masses_by_area" % self.day.code),
                self.area_tree_filter,
                self.area_tree_href
            )
        elif component == u"area":
            return area_ui.AreaUI (self.language, self.day)
        else:
            raise errors.TraversalError

class DayUI (ui.UI):

    _q_exports = []

    def __init__ (self, language):
        ui.UI.__init__ (self, language)

    def _q_lookup (self, request, component):
        day = days.day (code=component.upper ()) or days.day (name=component)
        return SpecificDayUI (self.language, day)
