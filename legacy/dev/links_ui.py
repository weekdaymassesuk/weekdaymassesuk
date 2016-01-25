from __future__ import generators
import os, sys

import config
import database
import utils
import links
from doc import Doc
import ui

class LinksDoc(Doc):

    def __init__(self, request, language):
        Doc.__init__(self, request, language, use_fs_cache=True)
        self.links = {}
        for row in links.subject_links():
            self.links.setdefault(row.type, {}).setdefault(row.subject, []).append(row)

    def title(self):
        return self.translate("links_title")

    def body(self):
        contents = []
        for type in sorted(self.links):
            contents.append('<h2>%s</h2>' % type.title())
            for subject in sorted(self.links[type]):
                contents.append('<p class="tree0">%s</p>' % subject)
                for link in self.links[type][subject]:
                    contents.append('<p class="tree1"><a href="%(link)s">%(title)s</a></p>' % link)

        return "\n".join(contents)

class LinksUI(ui.UI):

    _q_exports = [u"_q_index"]

    def __init__(self, language):
        ui.UI.__init__(self, language)
        self.title = self.translate("links_title")

    def _q_index(self, request):
        return LinksDoc(request, self.language)
    __call__ = _q_index
