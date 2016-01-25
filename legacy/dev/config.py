import os, sys
import datetime
import re
import tempfile

#
# This should be blank on a live installation
#
SVN_URL = "$URL: svn+ssh://tgolden@web30.webfaction.com/home/tgolden/svn/weekdaymasses.org.uk/dev/config.py $"
_root, _branch = re.search(r"/(dev|live|branches)/([^/]+)", SVN_URL).groups ()
if _root == "live":
    VERSION = ""
elif _root == "dev":
    VERSION = "dev"
else:
    VERSION = _branch

QCONFIG_FILEPATH = "weekdaymasses.cfg"
#~ ROOT_AREA_NAME = u'GB'
ROOT_AREA_CODE = 'gb'
DATABASE_NAME = u"data/masses.db"
if os.path.exists(DATABASE_NAME):
    LAST_UPDATE = datetime.datetime.utcfromtimestamp(os.path.getmtime(DATABASE_NAME))
else:
    LAST_UPDATE = None
N_UPDATES = 10
TRANSLATIONS_WORKBOOK = "data/translations.xls"
DEFAULT_LANGUAGE = "en"

#
# Whether to use filesystem cache, and where to store the files
#
USE_FS_CACHE = (_root == "live")
if VERSION:
    cache_extension = ".%s" % VERSION
else:
    cache_extension = ""
FS_CACHE_LOCATION = "cache"

INPUT_ENCODING = "utf-8"
OUTPUT_ENCODING = "utf-8"
ENCODING = OUTPUT_ENCODING
CONTACT_EMAIL="317056cd-e90f-4e6d-8f67-7929e58e@weekdaymasses.org.uk"

#
# Number of churches to display on a map
#
THRESHOLD = 100

HTTP_TIMESTAMP = "%a, %d %b %Y %H:%M:%S GMT"
#
# By default, tell caches not to bother looking
# before a week's up.
#
CACHE_FOR_SECS = 60 * 60 * 24 * 7

