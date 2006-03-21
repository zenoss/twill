#!/usr/bin/env python

from setuptools import setup

#### twill info.

setup(name = 'twill',
      
      version = '0.8.4a12',
      download_url = 'http://darcs.idyll.org/~t/projects/twill-0.8.4.tar.gz',
      
      description = 'twill Web browsing language',
      author = 'C. Titus Brown',
      author_email = 'titus@caltech.edu',
      license='LGPL',

      packages = ['twill', 'twill.other_packages',
                  'twill.other_packages.ClientCookie',
                  'twill.other_packages.mechanize',
                  'twill.extensions'],

      # allow both 
      entry_points = dict(console_scripts=['twill-sh = twill.shell:main'],),
      scripts = ['twill-fork'],
      
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
