from __future__ import generators

import os, sys
import re
import utils
import urllib
import urlparse

import config
import database
import i18n
import utils
from lib import cache

class BaseDoc(object):

    _title = "weekdaymasses.org.uk"
    _q_exports = ["_q_index"]

    def __init__(self, request, language=None):
        self.request = request
        self.branch = getattr(config, "VERSION", "")
        self.language = language or config.DEFAULT_LANGUAGE

    def title (self):
        _title = self._title
        if self.branch:
            _title += " - " + self.branch
        return _title

    def google_tracker(self):
        if self.request.get_server ().startswith("local.weekdaymasses.org.uk"):
            return "<!-- No Google Tracker -->"
        else:
            return """
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-2798383-2']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>"""

    def stylesheets(self):
        return "<!-- No stylesheets -->"

    def script (self, script_path):
        return u'<script src="%s" type="text/javascript"></script>' % script_path

    def javascript(self):
        return "<!-- No Javascript -->"

    def header_plugin (self):
        return "<!-- No header plugin -->"

    def header (self):
        return u"""
        <!DOCTYPE html>
        <html>
        <head>
        <title>%s</title>
        <script src="http://code.jquery.com/jquery-1.10.1.min.js"></script>
        <meta name="verify-v1" content="P6x5UZUvbcpZ9CBG4lsI/99vbk0yTe8T/ar3Jka+Grc=" />
        %s
        %s
        %s
        %s
        </head>
        <!-- %s -->
        <body class="%s">
        """ % (self.title (), self.stylesheets(), self.javascript(), self.header_plugin(), self.google_tracker(), self.request.get_server(), self.language)

    def body(self):
        path = self.request.environ.get('PATH_INFO', '')
        args = u"<br/>\n".join (
            u"%s = %s" % (k, v) for k, v in sorted(self.request.formiter())
        )
        return "<h1>%s</h1>\n\n<p>%s</p>\n" % (path, args)
    _body = body

    def footer(self):
        return u"</body></html>"

    def as_string (self):
        text = self.header () + self._body () + self.footer ()
        return text.encode (config.OUTPUT_ENCODING)

    def __str__ (self):
        return self.as_string ()

    def _q_index (self, request):
        return self.as_string ()
    __call__ = _q_index


class Doc(BaseDoc):

    def __init__ (
        self,
        request,
        language=None,
        use_fs_cache=config.USE_FS_CACHE,
        filename=None,
        title="",
        context="masses"
    ):
        BaseDoc.__init__(self, request, language)
        self.content = ""
        self.base = ""
        if request:
            request.response.set_content_type ("text/html; charset=%s" % config.OUTPUT_ENCODING)
            request.response.cache = config.CACHE_FOR_SECS
            request.response.set_header ("cache-control", "max-age=%d" % config.CACHE_FOR_SECS)
            self.base, self.path, _, _ = utils.urlparts (request)
        self.translations = i18n.translations (self.language)
        if self.branch:
            languages_offered = ["raw"]
        else:
            languages_offered = []
        languages_offered += [l for l in i18n.languages () if l != self.language]
        self.languages_ui = (
            '<span class="current">%s</span>&nbsp;' % self.language) + "".join ('%s' % ('<a href="%s" class="internal">%s</a>' % (
                self.url (path=self.path_by_language (language)), language)
            )
            for language in languages_offered
        )
        self.use_fs_cache = use_fs_cache
        if filename:
            filepath = self.include (filename)
            self.last_modified_on = utils.filestamp (filepath)
        else:
            self.last_modified_on = config.LAST_UPDATE
        if request:
            request.response.set_header ("Last-Modified", self.last_modified_on.strftime (config.HTTP_TIMESTAMP))
        self._title = title
        self.context = context

    def url(self, path="", fragment="", with_query=True):
        if self.request:
            return utils.url(self.request, path, fragment, with_query)
        else:
            return ""

    def quick_links (self):
        urls = [
            (u"qlinks_home", u"/%s/main" % self.language),
            (u"qlinks_gb_churches_by_postcode", u"/%s/area/gb/postcodes/" % self.language),
            (u"qlinks_gb_weekday_masses_by_area", u"/%s/day/Weekday/area_tree/gb/" % self.language),
            (u"qlinks_shrines", u"/%s/shrine/" % self.language),
            (u"qlinks_whatsnew", u"/%s/whats_new" % self.language),
            (u"qlinks_links", u"/%s/links/" % self.language),
            (u"qlinks_find", u"/%s/search/" % self.language),
            (u"qlinks_maps", u"/%s/map" % self.language),
        ]
        for url in urls:
            yield url

    def _quick_links (self):
        output = []
        output.append (u"<div class=links>")
        for text, path in self.quick_links ():
            text = self.translate (text)
            output.append (u'<a href=%s class="internal">%s</a>' % (self.url (path, with_query=False) + "?quick=1", text))
        output.append (u"</div>")
        return "\n".join (output)

    def stylesheets(self):
        stylesheets = []
        stylesheets.append (u"weekdaymasses.css")
        if self.context:
            if isinstance (self.context, basestring):
                context = [self.context]
            else:
                context = self.context
            stylesheets.extend (u"%s.css" % c for c in context)
        return u"\n".join ([u'<link rel=StyleSheet href="/static/css/%s" type="text/css" title="Styles">' % self.url (s, with_query=False) for s in stylesheets])

    def header (self):
        middle = self._quick_links ()
        if "weekdaymasses.org.uk" not in self.request.environ.get ("HTTP_REFERER", ""):
            middle += "\n".join (self.language_switch ())

        return BaseDoc.header(self) + middle

    def footer (self):
        return self._quick_links () + BaseDoc.footer(self)

    def language_switch (self):
        allowed_languages = i18n.languages ()
        for preferred_language in utils.preferred_languages (self.request.environ.get ("HTTP_ACCEPT_LANGUAGE", "en")):
            language, _, _ = preferred_language.lower ().partition ("_")
            if language == self.language:
                break
            elif language in allowed_languages:
                translator = i18n.translator (language)
                yield '<p class="switch-language">'
                yield translator ("general_not_preferred_language")
                yield '<a href="%s">%s</a>' % (self.url (path=self.path_by_language (language)), translator ("general_switch_language"))
                yield '</p>'
                break

    def path_by_language (self, language):
        paths = self.path.split ("/")
        paths[1] = language
        return "/".join (paths)

    def include (self, ihtml_filename):
        ihtml_filepath = "html/%s" % ihtml_filename
        template = i18n.load_template (ihtml_filename)

        dictionary = dict (
            url = self.base,
            language = self.language,
            last_updated = config.LAST_UPDATE,
            map_threshold = unicode (config.THRESHOLD),
            languages = self.languages_ui
        )
        dictionary.update (self.translations)
        self.content = i18n.template (template.render (dictionary)).render (dictionary)
        return ihtml_filepath

    def body (self):
        return self.content

    def body_title (self):
        return u'<h1>%s</h1>' % self.title ()

    def _body (self):
        body_text = u""
        request_fs_cache = int(self.request.get_form_var (u"cache", True))
        if self.use_fs_cache and config.USE_FS_CACHE and request_fs_cache:
            body_text = cache.get(self.request, since=config.LAST_UPDATE)

        if not body_text:
            body_text = "\n<!-- Start of generated body -->\n%s\n<!-- End of generated body -->\n" % self.body ()
            cache.put(self.request, body_text)

        return u'<div class="body">%s %s</div>' % (self.body_title (), body_text)

    def translate (self, text, **kwargs):
        defaults = {
            "language" : self.language,
            "url" : self.base
        }
        return i18n.translate (text, self.translations, defaults, **kwargs)

    def renderer (self):
        return i18n.renderer (self.language, url=self.base)

