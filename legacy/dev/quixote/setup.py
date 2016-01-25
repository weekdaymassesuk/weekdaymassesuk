#!/usr/bin/env python

# Setup script for Quixote

import sys, os
from distutils import core
from distutils.extension import Extension
from qx_distutils import qx_build_py

# a fast htmltext type
htmltext = Extension(name="quixote._c_htmltext",
                     sources=["src/_c_htmltext.c"])

# faster import hook for PTL modules
cimport = Extension(name="quixote.cimport",
                    sources=["src/cimport.c"])

kw = {'name': "Quixote",
      'version': "1.3",
      'description': "A highly Pythonic Web application framework",
      'author': "MEMS Exchange",
      'author_email': "quixote@mems-exchange.org",
      'url': "http://quixote.ca/",
      'license': "DFSG approved (see LICENSE.txt)",

      'package_dir': {'quixote':os.curdir},
      'packages': ['quixote',  'quixote.demo', 'quixote.form',
                   'quixote.form2', 'quixote.server'],

      'ext_modules': [],

      'cmdclass': {'build_py': qx_build_py},
     }


build_extensions = sys.platform != 'win32'

if build_extensions:
    # The _c_htmltext module requires Python 2.2 features.
    if sys.hexversion >= 0x20200a1:
        kw['ext_modules'].append(htmltext)
    kw['ext_modules'].append(cimport)

# If we're running Python 2.3, add extra information
if hasattr(core, 'setup_keywords'):
    if 'classifiers' in core.setup_keywords:
        kw['classifiers'] = ['Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'License :: OSI Approved :: Python License (CNRI Python License)',
          'Intended Audience :: Developers',
          'Operating System :: Unix',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: MacOS :: MacOS X',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          ]
    if 'download_url' in core.setup_keywords:
        kw['download_url'] = ('http://www.mems-exchange.org/software/files'
                              '/quixote/Quixote-%s.tar.gz' % kw['version'])

core.setup(**kw)
