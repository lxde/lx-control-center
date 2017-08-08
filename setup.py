#!/usr/bin/env python

from distutils.core import setup
import glob
import os
from DistUtilsExtra.command import *

setup(
      name='lx-control-center',
      version='0.1',
      author ='Julien Lavergne',
      author_email='gilir@ubuntu.com',
      description = ('A too to centralise all settings for an LXDE environment.'),
      licence = 'GPL2',
      keywords = 'LXDE control-center settings',
      url = 'https://github.com/lxde/lx-control-center',
      packages=[
                'LXControlCenter',
                'LXControlCenter.widgets',
                'LXControlCenter.modules.themes-manager',
                ],
      scripts=[
               'lx-control-center',
               ],
      cmdclass = { "build" : build_extra.build_extra,
                   "build_i18n" :  build_i18n.build_i18n,
                   "build_help" :  build_help.build_help,
                   "build_icons" :  build_icons.build_icons }
     )
