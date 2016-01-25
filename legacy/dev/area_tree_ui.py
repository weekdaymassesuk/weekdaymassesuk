from __future__ import generators
import os, sys

import areas
import config
import database
import i18n
import utils
import ui
from doc import Doc

class AreaTreeDoc (Doc):

  def __init__ (self, request, language, root, title=u"Areas", filter_callback = None, href_callback = None, **kwargs):
    Doc.__init__ (self, request, language, use_fs_cache=True, **kwargs)
    self.root = root
    self.filter_callback = filter_callback
    self.href_callback = href_callback
    self._title = title

  def title (self):
    return self._title

  def body (self):
    intro = u'<p class="instructions">%s</p>' % self.translate ("area_click_on_interest")
    return intro + u'<div class="area-tree">%s</div>' % u"\n".join (self.area_tree_as_html ())

  def area_tree_as_html (self):
    for area, level in areas.area_tree (self.root):
      if self.filter_callback:
        keep = self.filter_callback (area)
      else:
        keep = True

      if keep:
        if area.details:
          description = u' - <span class="description">%s</span>' % area.details
        else:
          description = u""

        if self.href_callback:
          href, href_class = self.href_callback (self.request, area)
        else:
          href, href_class = u"", u""

        if href:
          href_string = u'<a href="%s" class="%s">%s</a>' % (href, href_class, area.area_name)
        else:
          href_string = area.area_name

        yield u'<p class="tree%d">%s%s</p>' % (level, href_string, description)

class AreaTreeUI (ui.UI):

  _q_exports = [u"_q_index"]

  def __init__ (self, language, title, filter_callback=None, href_callback=None):
    ui.UI.__init__ (self, language)
    self.filter_callback = filter_callback
    self.href_callback = href_callback
    self.title = title

  def _q_index (self, request):
    return request.redirect (config.ROOT_AREA_NAME)
  __call__ = _q_index

  def _q_lookup (self, request, component):
    component = utils.unquote (component)
    try:
      id = int (component)
    except ValueError:
      root = areas.area (code=component)
    else:
      root = areas.area (id=id)
    if root is None:
      root = areas.area (code=config.ROOT_AREA_CODE)

    return AreaTreeDoc (request, self.language, root, self.title, self.filter_callback, self.href_callback)

