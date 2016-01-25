from __future__ import generators
from quixote import errors

import utils
import config
import areas
import churches
import area_tree_ui
import churches_ui
import ui

class ShrineUI (ui.UI):

  _q_exports = []

  def __init__ (self, language):
    ui.UI.__init__ (self, language)

  def area_tree_filter (self, area):
    """Keep areas in the tree if they have any shrines
    """
    for row in churches.shrines_in_area (area.id):
      return True
    else:
      return False

  def area_tree_href (self, request, area):
    return str (area.area_code), u"internal"

  def shrines (self, area):
    for church in churches.shrines_in_area (area.id):
      yield church

  def _q_index (self, request):
    root = areas.area (code=config.ROOT_AREA_CODE)
    return area_tree_ui.AreaTreeDoc (
      request,
      self.language,
      root,
      self.translate ("shrines_by_area", area=root.name),
      self.area_tree_filter,
      self.area_tree_href,
      context=u"shrines"
    )
  __call__ = _q_index

  def _q_lookup (self, request, component):
    try:
      id = int (component)
    except ValueError:
      area = areas.area (code=component)
    else:
      area = areas.area (id=id)

    return churches_ui.ChurchesDoc (
      request,
      self.language,
      self.shrines (area),
      title=self.translate ("shrines_title", area=area.name),
      context=u"shrines"
    )

