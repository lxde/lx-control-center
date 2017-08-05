#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#  lx-control-center
#
#       Copyright 2016 (c) Julien Lavergne <gilir@ubuntu.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import os.path
import logging
import argparse

import gettext
_ = gettext.gettext

from LXControlCenter.utils import Utils

class Runner(object):
    def __init__(self):
        self.util = Utils()
        self.loglevel_args = None
        self.logfile_args = None
        self.standalone_module = False

    def get_args_parameters(self):
        parser = argparse.ArgumentParser(description='Launch LX Control Center')
        parser.add_argument('-l', '--log', help='Set log level (values available : WARNING, INFO or DEBUG)')
        parser.add_argument('-f', '--logfile', help='Set log file to write logs')
        parser.add_argument('-u', '--ui', help='Set Frontend - UI (values available: GTK2, GTK3, Qt5, Auto ...')
        parser.add_argument('-m', '--module', help='Launch only the specific module. Must be the desktop filename, without .desktop')
        args = parser.parse_args()
        self.loglevel_args =  args.log
        self.logfile_args =  args.logfile
        self.frontend_args =  args.ui
        self.standalone_module =  args.module

    def set_log(self):
        """ Set log level by parsing"""
        if (self.loglevel_args != None):
            numeric_level = getattr(logging, self.loglevel_args.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % self.loglevel_args)
            if (self.logfile_args == None):
                logging.basicConfig(level=numeric_level)
            else:
                logging.basicConfig(filename=self.logfile_args, level=numeric_level)

    def frontend_generate(self, keyfile):
        supported_frontend = ["GTK3", "GTK2", "Qt5", "webkitgtk2"]
        frontend_setting = self.util.get_setting("keyfile", keyfile, "Configuration","frontend", None, "string")
        frontend = None
        if (self.frontend_args != None):
            if (self.frontend_args in supported_frontend):
                frontend = self.frontend_args
            else:
                logging.warning(_("%s desktop environment unknown or not supported. Default to GTK3" % self.frontend_args))
                frontend = 'GTK3'
        elif (frontend_setting == "Auto" or frontend_setting == None):
            current_desktop = os.getenv("XDG_CURRENT_DESKTOP")
            gtk2_list = ['LXDE']
            gtk3_list = ['GNOME']
            qt5_list = ['KDE', 'LXQt']
            if (current_desktop in gtk2_list):
                frontend = 'GTK2'
            elif (current_desktop in gtk3_list):
                frontend = 'GTK3'
            elif (current_desktop in qt5_list):
                frontend = 'Qt5'
            else:
                logging.warning(_("%s desktop environment not supported, please report it as a bug. Default to GTK3" % current_desktop))
                frontend = 'GTK3'
        else:
            frontend = self.frontend_setting

        return frontend

    def run (self):
        # Parse command line arguments
        self.get_args_parameters()

        # Enable log
        self.set_log()

        keyfile = self.util.load_object("ini", os.path.join("lx-control-center", "settings.conf"))
        frontend = self.frontend_generate(keyfile)
        app = None
        if (frontend == "GTK2"):
            from LXControlCenter.widgets.gtk2 import Gtk2App
            app = Gtk2App()
            app.toolkit = "GTK2"
        elif (frontend == "GTK3"):
            from LXControlCenter.widgets.gtk3 import Gtk3App
            app = Gtk3App()
            app.toolkit = "GTK3"
        elif (frontend == "Qt5"):
            from LXControlCenter.widgets.qt5 import Qt5App
            app = Qt5App()
            app.toolkit = "Qt5"
        elif (frontend == "webkitgtk2"):
            from LXControlCenter.widgets.webkitgtk2 import WebkitApp
            app = WebkitApp()
            app.toolkit = None
        else:
            # Default to GTK3
            from LXControlCenter.widgets.gtk3 import Gtk3App
            app = Gtk3App()
            app.toolkit = "GTK3"

        app.frontend = frontend
        app.standalone_module = self.standalone_module
        app.main()
