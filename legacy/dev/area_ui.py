from __future__ import generators
import os, sys

from quixote import errors

import config
import churches
import areas
import days
import utils
import doc
import ui
from masses_ui import MassesDoc
from churches_ui import ChurchesDoc
from area_tree_ui import AreaTreeDoc
from postcodes_ui import PostcodesUI

class SpecificAreaUI (ui.UI):

    _q_exports = ["_q_index", "masses", "churches"]

    def __init__ (self, language, day, area):
        ui.UI.__init__ (self, language)
        self.day = day
        self.area = area

    def _q_index (self, request):
        if self.day is None:
            raise errors.TraversalError, u"Day must be specified"
        return MassesDoc (request, self.language, self.day, self.area)
    __call__ = _q_index

    def _q_lookup (self, request, component):
        if component == u"postcodes":
            return PostcodesUI (self.language, self.area)
        else:
            raise errors.TraversalError

    def masses (self, request):
        if self.day is None:
            raise TraversalError, u"Day must be specified"
        return MassesDoc (request, self.language, self.day, self.area)

    def churches_in_area (self):
        for church in churches.churches_in_area (self.area.id):
            yield church

    def churches (self, request):
        return ChurchesDoc (
            request,
            self.language,
            self.churches_in_area (),
            title=u"%s %s" % (self.translate ("churches_churches_in"), self.area.name)
        )

class AreaUI (ui.UI):

    _q_exports = []

    def __init__ (self, language, day=None):
        ui.UI.__init__ (self, language)
        self.day = day

    def _q_index (self, request):
        return request.redirect ("/%s/day/%s/area_tree/%s" % (self.language, self.day or "K", config.ROOT_AREA_CODE))
    __call__ = _q_index

    def _q_lookup (self, request, component):
        try:
            id = int (component)
        except ValueError:
            root = areas.area (code=component)
        else:
            root = areas.area (id=id)
        if root is None:
            root = areas.area (code=config.ROOT_AREA_CODE)

        return SpecificAreaUI (self.language, self.day, root)
