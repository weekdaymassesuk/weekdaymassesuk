import i18n
import utils

class UI:

  def __init__ (self, language):
    self.language = language
    self.translations = i18n.translations (language)

  def translate (self, text, **kwargs):
    return i18n.translate (text, self.translations, **kwargs)

  def redirect (self, request, path):
    return request.redirect ("/%s/%s" % (self.language, path))
