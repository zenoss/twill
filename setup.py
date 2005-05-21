from distutils.core import setup
from twill.twill_build_utils import twill_build_py

setup(name = 'twill', version = '0.6',
      description = 'twill Web testing language',
      author = 'C. Titus Brown',
      author_email = 'titus@caltech.edu',
      packages = ['twill',],
      scripts = ['twill-sh',],
      cmdclass = {'build_py' : twill_build_py })
