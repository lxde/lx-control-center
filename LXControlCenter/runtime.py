#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#  lx-control-center
#
#       Copyright 2017 (c) Julien Lavergne <gilir@ubuntu.com>
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

import logging
import os
import os.path

from LXControlCenter.utils import Utils

class Runtime():
    # Class to check support (applications runnings) on current machine. It only needs to be instantiate once, and be reused.
    def __init__(self):
        logging.info("Runtime.__init__: enter function")
        self.util =  Utils()

        # Format for runtime key
        # self.support[key] = [pretty_name, binary, running ?, configuration_object, configuration_path]
        self.support = {}
        self.support["lxsession_file"] = ["LXSession (keyfile)", "lxsession", False, None, None]
        self.support["lxsession_dbus"] = ["LXSession (dbus)", "lxsession", False, None, None
        self.support["cinnamon_settings"] = ["Cinnamon", "cinnamon-settings-daemon", False, None, None]
        self.support["gnome_settings"] = ["GNOME", "gnome-settings-daemon", False, None, None]
        self.support["mate_settings"] = ["MATE", "mate-settings-daemon", False, None, None]
        self.support["lxqt_settings"] = ["LXQt", "lxqt-session", False, None, None]
        self.support["gtk3_settings"] = ["GTK3", None, False, None, None]

        # List of support key which are actually running on the system
        self.running = []

        # Startup functions
        self.running_aplications = self.util.generate_running_applications()
        self.check_running_support()
        self.check_conf_support()
        self.generate_support_list()


    def generate_running(self):
        for support in self.support:
            if(support[2] == True):
                self.running.append(support)

    def check_running_support(self):
        logging.info("Runtime.check_running_support: enter function")
        for support in self.support:
            if (support[1] == None):
                support[2] = True
            elif (support[1] in self.running_aplications):
                support[2] = True

    def check_conf_support(self):
        logging.info("Runtime.check_running_support: enter function")
        for support in self.support:
            if (support == "lxsession_file"):
                profile = os.environ['DESKTOP_SESSION']
                lxsession_dir = os.path.join("lxsession", profile)
                try:
                    support[4] = os.path.join(lxsession_dir, "desktop.conf")
                    if (support[4] is not None):
                        support[3] = self.util.load_object("ini", support[4])
                except:
                    pass
            elif (support == "lxsession_dbus"):
                try:
                    bus = SessionBus()
                    remote_object = bus.get("org.lxde.SessionManager", "/org/lxde/SessionManager")
                    support[3] = remote_object
                except:
                    pass
            elif (support == "gtk3_settings"):
                try:
                    support[4] = os.path.join("gtk-3.0", "settings.ini")
                    if (support[4] is not None):
                        support[3] = self.util.load_object("ini", support[4])
                except:
                    pass
            elif (support == "lxqt_settings"):
                try:
                    support[4] = os.path.join("lxqt", "lxqt.conf")
                    if (support[4] is not None):
                        support[3] = self.util.load_object("ini", support[4])
                except:
                    pass
