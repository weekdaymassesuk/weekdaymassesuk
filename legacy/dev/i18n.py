import datetime
import re
import urllib

import jinja2

import config
import database
import utils

class i18nError (Exception):
  pass

class Loader (jinja2.BaseLoader):

  def get_source (self, environment, string):
    return string, "<string>", lambda: True

environment = jinja2.Environment (loader=jinja2.FileSystemLoader ("html"))
def load_template (filename):
  return environment.get_template (filename)

string_environment = jinja2.Environment (loader=Loader ())
def template (string):
  return string_environment.get_template (string)

URLS = {}
for key, url in database.select ("SELECT key, url FROM translation_urls ORDER BY key, sequence"):
  URLS.setdefault (key, []).append (url)

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
@jinja2.evalcontextfilter
def nl2br(context, text):
    result = text.replace("\n", jinja2.Markup("<br>\n"))
    if context.autoescape:
        result = jinja2.Markup(result)
    return result    

weekdays = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
@jinja2.contextfilter
def date_format (context, timestamp):
  """A more flexible, locale-aware version of the standard strftime
  function. Includes date ordinals (st, nd, th) and multilanguage
  months / days of week
  """
  weekday = context["day_%s" % weekdays[timestamp.isoweekday ()-1]]
  day = timestamp.day
  ordinal = "st" if day in (1, 21, 31) else "nd" if day in (2, 22) else "rd" if day in (3, 23) else "th"
  month = context["month_%s" % months[timestamp.month-1]]
  year = timestamp.year
  return jinja2.Template (context['date_format']).render (locals ())

@jinja2.contextfilter
def time_format (context, timestamp):
  """A more flexible, locale-aware version of the standard strftime
  function. Includes date ordinals (st, nd, th) and multilanguage
  months / days of week
  """
  hh24 = timestamp.strftime ("%H:%M")
  hh12 = timestamp.strftime ("%I.%M%p").lower ().lstrip ("0")
  return jinja2.Template (context['time_format']).render (locals ())

hh12_matcher = re.compile (r"(\d\d?)(?:[.:](\d\d))?\s*(am|pm|noon)")
hh24_matcher = re.compile (r"(\d{4})")
weekday_matcher = re.compile (r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", re.IGNORECASE)
eve_matcher = re.compile (r"\beve\b")
@jinja2.contextfilter
def masstime_format (context, masstime_string):
  def hh12_converter (match):
    hh12, mi, mer = match.groups ()
    hh24 = int (hh12) + (12 if int (hh12) < 12 and mer in ("pm") else 0)
    if not 0 <= hh24 <= 23:
      raise i18nError ("%s is not between 0 and 23" % hh24)
    timestamp = datetime.datetime.now ().replace (hour=hh24, minute=int (mi or 0))
    return time_format (context, timestamp)
  def hh24_converter (match):
    try:
      t = datetime.datetime.strptime (match.group (), "%H%M")
    except ValueError:
      return match.group()
    else:
      return time_format (context, t)
  def weekday_converter (match):
    return context['day_%s' % match.group ().lower ()]
  def eve_converter (match):
    return context['date_eve']
  result = masstime_string
  result = hh12_matcher.sub (hh12_converter, result)
  result = hh24_matcher.sub (hh24_converter, result)
  result = weekday_matcher.sub (weekday_converter, result)
  result = eve_matcher.sub (eve_converter, result)
  return result

@jinja2.contextfilter
def day_format (context, day):
  return context["day_%s" % day.code.lower ()]

@jinja2.contextfilter
def phone_format(context, phone):
  if context.get("is_gb", True) and not context.get("language", "en") == "en":
    return "+44 " + phone.lstrip("0")
  else:
    return phone

filters = dict (
  date_format = date_format,
  time_format = time_format,
  masstime_format = masstime_format,
  day_format = day_format,
  phone_format = phone_format,
  urlquote = urllib.quote,
  nl2br = nl2br
)
environment.filters.update (filters)
string_environment.filters.update (filters)

def languages ():
  return [row.language for row in database.select ("SELECT DISTINCT language FROM translations")]

TRANSLATE_SQL = """
SELECT
  dflt.key,
  COALESCE (lang.translation, dflt.translation)
FROM
  translations AS dflt
LEFT OUTER JOIN translations AS lang ON
  dflt.key = lang.key AND
  lang.language = ?
WHERE
  dflt.language = ?
"""
def translations (language):
  def translate_urls (key, value):
    for n, text in enumerate (re.findall (r"\[[^]]+\]", value)):
      value = value.replace (text, '<a href="{{url}}/{{language}}/%s">%s</a>' % (URLS[key][n], text[1:-1]))
    return value

  rows = database.select (TRANSLATE_SQL, [language, config.DEFAULT_LANGUAGE])
  if language == "raw":
    return dict ((k, k + " " + translate_urls (k, " ".join ("[%s]" % url for url in URLS.get (k, [])))) for (k, v) in rows)
  else:
    return dict ((k, translate_urls (k, v)) for (k, v) in rows)

def translate (_key, _translations, _dictionary=None, **kwargs):
  if _dictionary is None:
    _dictionary = {}
  _dictionary.update (kwargs)
  return jinja2.Template (_translations[_key.lower ()]).render (_dictionary)

def translator (language):
  _translations = translations (language)
  def translate (_key, _dictionary=None, **kwargs):
    if _dictionary is None:
      _dictionary = {}
    _dictionary.update (kwargs)
    return jinja2.Template (_translations[_key.lower ()]).render (_dictionary)
  return translate

def renderer (language, defaults=None, **kwargs):
  if defaults is None:
    defaults = {}
  defaults.update (translations (language))
  defaults.update (kwargs)
  if "language" not in defaults:
    defaults["language"] = language
  def render (template, dictionary=None, **kwargs):
    if dictionary is None:
      dictionary = {}
    dictionary.update (defaults)
    dictionary.update (kwargs)
    return template.render (dictionary)
  return render
