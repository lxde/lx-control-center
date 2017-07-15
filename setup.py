#!/usr/bin/env python

from distutils.core import setup
import glob
import os
from DistUtilsExtra.command import *

setup(name='lx-control-center',
      version='0.1',
      packages=[
                'LXControlCenter',
                'LXControlCenter.widgets',
                ],
      scripts=[
               'lx-control-center',
               ],
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons }
     )
