#! /home/tgolden/apps/bin/python
## import cgitb; cgitb.enable ()

import os, sys

from quixote import publish
import index_ui
import config

app = publish.Publisher(index_ui.IndexUI())

if os.path.exists(config.QCONFIG_FILEPATH):
        app.read_config(config.QCONFIG_FILEPATH)
system = os.environ.get("HTTP_HOST", "").split(".")
if system[0] in ("localhost", "local", "dev") and os.path.exists("dev.cfg"):
        app.read_config("dev.cfg")

app.setup_logs()
app.publish_cgi()
