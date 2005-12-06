#!/usr/bin/env python

from setuptools import setup
from twill.twill_build_utils import twill_build_py

from ez_setup import use_setuptools
use_setuptools()

#### twill info.

setup(name = 'twill',
      
      version = '0.8.1a5',
      download_url = 'http://darcs.idyll.org/~t/projects/twill-0.8.tar.gz',
      
      description = 'twill Web testing environment',
      author = 'C. Titus Brown',
      author_email = 'titus@caltech.edu',
      license='LGPL',

      packages = ['twill', 'twill.wwwsearch',
                  'twill.wwwsearch.ClientCookie',
                  'twill.wwwsearch.mechanize'],
      scripts = ['twill-sh', 'twill-fork'],
      cmdclass = {'build_py' : twill_build_py },
      maintainer = 'C. Titus Brown',
      maintainer_email = 'titus@caltech.edu',

      url = 'http://www.idyll.org/~t/www-tools/twill.html',
      long_description = """\
A scripting system for automating Web browsing.  Useful for testing
Web pages or grabbing data from password-protected sites automatically.
""",
      classifiers = ['Development Status :: 3 - Alpha',
                     'Environment :: Console',
                     'Intended Audience :: Developers',
                     'Intended Audience :: System Administrators',
                     'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Programming Language :: Other Scripting Engines',
                     'Topic :: Internet :: WWW/HTTP',
                     'Topic :: Software Development :: Testing',
                     ],

      test_suite = 'nose.collector'
      )
