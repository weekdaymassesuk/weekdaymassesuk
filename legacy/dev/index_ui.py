from __future__ import generators
import os, sys

from quixote import errors

import config
from doc import BaseDoc, Doc
import utils

import i18n
import data_ui
import day_ui
import area_ui
import whats_new_ui
import shrines_ui
import postcodes_ui
import motorways_ui
import contact_ui
import links_ui
import search_ui
import ui
from lib import cache
import adverts

class IndexDoc (Doc):

    def header_plugin(self):
        scripts = [
            "/static/js/index.js",
        ]
        return "\n".join (self.script (script) for script in scripts)
    
    def body_title (self):
        index_language = self.translate ("index_language")
        languages_bar = '<b>%s:</b>&nbsp;%s' % (index_language, self.languages_ui)
        return u'''<div id="body-title"><h1>%s</h1><p class="links" id="languages">%s</p></div>''' % (self.title (), languages_bar)
    
    def footer(self):
        advert = adverts.random_advert()
        footer_text = """
<div id="advert"><p class="caption">Sponsored Ad</p>
<a href="{advert_url}"><img class="advert" src="/static/images/adverts/{advert_image_filename}" alt="Ad for {advert_organisation}" /></a>
</div>
""".format(advert_url=advert.url, advert_image_filename=advert.filename, advert_organisation=advert.organisation)

        return footer_text + BaseDoc.footer(self)

class MapDoc (IndexDoc):

    def header_plugin (self):
        scripts = [
            "http://maps.googleapis.com/maps/api/js?key=AIzaSyABWy2qSVLkW72hEAxw6Q7WtSTjVIRbnbI&sensor=false",
            "/static/js/lib/modernizr.js",
            "/static/js/helpers.js",
            "/static/js/geocoder.js",
            "/static/js/map.js",
            "/static/js/weekdaymasses.js",
        ]
        return "\n".join (self.script (script) for script in scripts)
    
    def footer(self):
        return Doc.footer(self)

class SpecificIndexUI (ui.UI):

    _q_exports = ["_q_index", "main", "map", "admin", "whats_new", "acks"]

    def __init__ (self, language):
        ui.UI.__init__ (self, language)

    def acks (self, request):
        return Doc (
            language=self.language,
            request=request,
            use_fs_cache=True,
            title=u"Acknowledgements",
            context=["index"],
            filename=u"acks.ihtml"
        )

    def map (self, request):
        return MapDoc (
            language=self.language,
            request=request,
            use_fs_cache=True,
            title=u"weekdaymasses.org.uk",
            context=["index", "map"],
            filename=u"map.html"
        )

    def main (self, request):
        return IndexDoc (
            language=self.language,
            request=request,
            use_fs_cache=False,
            title=u"weekdaymasses.org.uk",
            context=["index"],
            filename=u"index.ihtml"
        )

    def _q_index (self, request):
        return self.redirect (request, "map")
    __call__ = _q_index

    def admin (self, request):
        cache.clear()
        return u"""
        <h1>Admin Complete</h1>
        <p>Language = %s</p>
        """ % (self.language)

    def whats_new (self, request):
        return whats_new_ui.WhatsNewDoc (request=request, language=self.language)

    def _q_lookup (self, request, component):
        if component == u"day":
            return day_ui.DayUI (language=self.language)
        elif component == u"area":
            return area_ui.AreaUI (language=self.language)
        elif component == u"shrine":
            return shrines_ui.ShrineUI (language=self.language)
        elif component == u"postcode":
            return postcodes_ui.SearchUI (language=self.language)
        elif component == u"intouch":
            return contact_ui.ContactUI (language=self.language)
        elif component == u"links":
            return links_ui.LinksUI (language=self.language)
        elif component == u"dump":
            return u"\n<br>".join ([u"%s = %s" % (k, v) for k, v in sorted (request.environ.items ())])
        elif component == u"search":
            return search_ui.SearchUI (language=self.language)
        elif component == u"data":
            return data_ui.DataUI (language=self.language)
        else:
            raise errors.TraversalError

class IndexUI:

    _q_exports = []

    languages = ["raw"] + i18n.languages ()
    def _q_index (self, request):
        languages = utils.preferred_languages (request.environ.get ("HTTP_ACCEPT_LANGUAGE", "en"))
        for language in languages:
            language, _, _ = language.partition ("-")
            if language in self.languages:
                return request.redirect ("/" + language)
        else:
            return request.redirect ("/" + config.DEFAULT_LANGUAGE)
    __call__ = _q_index

    def _q_lookup (self, request, component):
        language = component.lower ()
        if component == "autolocate":
            return BaseDoc(request)
        if language in self.languages:
            return SpecificIndexUI (language)
        else:
            return request.redirect ("/" + config.DEFAULT_LANGUAGE)
