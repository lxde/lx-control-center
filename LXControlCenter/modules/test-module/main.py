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

# Import your current toolkit (must be specify in X-LX-Control-Toolkit of the desktop file).
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# For logging, it can be removed if you don't use logging facility
import os.path
import logging

# Init the LXCC_Module.
class LXCC_Module(object):
    def __init__(self):
        logging.debug("LXCC_Module.__init__: Init module %s" % os.path.abspath(__file__))

        # Create all your widget in __init__
        # LXCC will attach self.main_box to the main window
        self.main_box = Gtk.Box()

        self.test_label = Gtk.Label("This is a test label")
        self.main_box.add(self.test_label)
