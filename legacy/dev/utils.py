import os, sys
import codecs
import datetime
import math
import re
import string
import tempfile
import time
import unicodedata
import urlparse
import urllib
from urllib import unquote

import config
import database

def quoted (s):
    return s.replace ("'", "''")

def format_date (date):
    """Return the date in the form: Sunday 16th December 2001
    """
    day = date.day
    if day in (1, 21, 31):
        suffix = u"st"
    elif day in (2, 22):
        suffix = u"nd"
    elif day in (3, 23):
        suffix = u"rd"
    else:
        suffix = u"th"

    return u"%s %d%s %s" % (date.strftime ("%A"), date.day, suffix, date.strftime ("%B %Y"))

def format_distance (n_units):
    return u"%0.1f" % n_units

def code (name):
    return name.lower ().replace (" ", "_")

TRANSLATION = string.maketrans (
    string.uppercase + string.whitespace,
    string.lowercase + " " * len (string.whitespace)
)
def as_code (text, delimeter=u"-"):
    #
    # Convert to lowercase
    # Perform specific conversions
    # Remove all punctuation
    # Convert all whitespace to spaces
    # Strip leading / trailing space
    # Collapse multiple spaces to single
    # Convert spaces to underscores
    # eg,
    #     The Owl & the Pussycat => the_owl_and_the_pussycat
    #
    text = unicodedata.normalize ("NFKD", unicode (text)).encode ("ascii", "ignore")
    text = text.lower ().strip ()
    text = string.translate (text.strip ().replace ("_", " "), TRANSLATION, string.punctuation)
    words = text.split ()
    return unicode (delimeter.join (words))

def dump (request, field):
    return u"<!-- %s: %s -->" % (field, request.get_environ (field, u"<UNKNOWN>"))

##
## See implementation of urlbase etc. in doc.py
##

def urlquery (request):
    query_string = request.get_environ (u"QUERY_STRING", "")
    if query_string:
        return u"?" + query_string
    else:
        return u""

def urlbase (request, with_query=True):
    #
    # request_uri comes ready-quoted, so unquote
    #
    request_uri = urllib.unquote_plus (request.get_environ (u"REQUEST_URI"))
    path_info = request.get_environ (u"PATH_INFO", u"")
    if with_query:
        query_string = u"?" + request.get_environ (u"QUERY_STRING", u"")
    else:
        query_string = u""

    if path_info.endswith (query_string):
        path_info = path_info[:len (path_info) - len (query_string)]
    if request_uri.endswith (query_string):
        request_uri = request_uri[:len (request_uri) - len (query_string)]

    if request_uri.endswith (path_info):
        return request_uri[:len (request_uri) - len (path_info)]
    else:
        return request_uri

##def url (request, additional_path, fragment=""):
##    return urlbase (request) + additional_path + urlquery (request) + fragment

#
# REQUEST_URI - /qmass/en/postcode?postcode=W5+3PB&distance=1.0
# PATH_INFO - /en/postcode
# QUERY_STRING - postcode=W5+3PB&distance=1.0
#
# REQUEST_URI is the only place where the redirected qmass appears
# REQUEST_URI = (redirected) + PATH_INFO + ? + QUERY_STRING
# REQUEST_URI is url-quoted, eg /qmass/en/area/Outside%20GB
# PATH_INFO is *un*-quoted, eg /en/area/Outside GB
#
def urlparts (request):
    "Return base, path, query, fragment from the current request"
    schema, server, full_path, params, query, fragment = \
        urlparse.urlparse (request.get_environ (u"REQUEST_URI"))
    path_info = request.get_environ (u"PATH_INFO")
    path_info = u"/".join ([urllib.quote (s) for s in path_info.split (u"/")])

    if path_info:
        ipath = full_path.index (path_info)
        base, path = full_path[:ipath], full_path[ipath:]
    else:
        base, path = full_path, u""

    return base, path, query, fragment

def url (request, path="", fragment="", with_query=True):
    base, _, query, _ = urlparts (request)
    url = path
    #~ if path:
        #~ url = url + path
    if with_query and query:
        url = url + u"?" + query
    if fragment:
        url = url + u"#" + fragment
    return url

def link (language=None, day_code=None, area_id=None, area_code=None):
    parts = []
    if language is not None:
        parts.append (language)
    if day_code is not None:
        parts.extend ([u"day", day_code])
    if area_id is not None:
        parts.extend ([u"area", area_id])
    elif area_code is not None:
        parts.extend ([u"area", area_code])
    return u"/" + u"/".join ([str (p) for p in parts])

def area_link (request, area, day, language):
    website_fieldname = u'%s_website' % code (day.name)
    if area[website_fieldname]:
        return (area[website_fieldname], u"external")
    else:
        return (url (request, link (language=language, day_code=day.code, area_code=area.area_code)), u"internal")

def church_link (request, language, area=None, church=None, area_code=None, church_id=None):
    base_link = link (language=language, area_id=(area_code or area.area_code))
    return url (request, u"%s/churches#p%d" % (base_link, church_id or church.id), with_query=False)

def hh24_to_hh12 (hh24, eve=None):
    hrs = int (hh24[:2])
    mins = int (hh24[2:])

    if hrs < 12:
        suffix = u"am"
    elif hrs == 12 and mins == 0:
        suffix = u" noon"
        mins = None
    else:
        if hrs > 12:
            hrs -= 12
        suffix = u"pm"

    if mins is None:
        hh12 = u"%d%s" % (hrs, suffix)
    else:
        hh12 = u"%d.%02d%s" % (hrs, mins, suffix)
    if eve:
        return hh12 + u" (eve)"
    else:
        return hh12

def distance ((x1, y1), (x2, y2)):
    return math.sqrt ((y2 - y1) * (y2 - y1) + (x2 - x1) * (x2 - x1))

UNIT_METRES = {
    u"miles" : 1609.0,
    u"km" : 1000.0
}
def from_metres (n_metres, units):
    return n_metres / UNIT_METRES[units]

def to_metres (n, units):
    return n * UNIT_METRES[units]

def format_distance (n_units):
    return u"%0.1f" % n_units

def preferred_languages (http_accept_language):
    lang_prefs = [i.strip () for i in http_accept_language.split (",")]

    languages = []
    for i, lang_pref in enumerate (lang_prefs):
        lang, pref = (lang_pref + ";").split (";")[:2]
        q, val = (pref + "=").split ("=")[:2]
        languages.append ((float (val or 1.0), -i, lang))

    languages.sort ()
    languages.reverse ()
    return [l[-1] for l in languages]

splitter = re.compile ("|".join ("\\%s" % x for x in string.punctuation + string.whitespace))
words_to_exclude = set (["&", "and", "of", "the", "st", "ss", "saint"])
def filter_search_words (phrase):
    words = set (w.strip () for w in splitter.split (phrase.lower ())) - words_to_exclude
    return [w for w in words if len (w) >= 3]

def filestamp (filename, ftime=os.path.getmtime):
    return datetime.datetime.utcfromtimestamp (ftime (filename))
