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

from pydbus import SessionBus

from gi.repository import Gio
from LXControlCenter.utils import Utils

# Documentation / Examples
# LXDE / LXSession: https://github.com/lxde/lxsession/blob/master/data/desktop.conf.example
#                   https://wiki.lxde.org/en/index.php?title=LXSession
# LXQt: https://github.com/lxde/lxqt-session/blob/master/config/lxqt.conf
# Ubuntu / GNOME: https://code.launchpad.net/~vcs-imports/ubuntu-tweak/master
# GNOME:  https://git.gnome.org/browse/gnome-tweak-tool/tree/
# Cinnamon: https://github.com/linuxmint/Cinnamon/tree/master/files/usr/share/cinnamon/cinnamon-settings/modules
# Mate: https://github.com/mate-desktop/mate-control-center/blob/master/capplets/appearance/appearance.h


# Theme
# GNOME / GTK: https://git.gnome.org/browse/gnome-tweak-tool/tree/gtweak/tweaks/tweak_group_appearance.py
# LXSession: https://github.com/lxde/lxsession/blob/master/data/desktop.conf.example
# LXQt: https://github.com/lxde/lxqt-session/blob/master/config/lxqt.conf
# Mate: https://github.com/mate-desktop/mate-control-center/blob/master/capplets/appearance/appearance.h

class Setting():
    def __init__(self, runtime):
        logging.info("Setting.__init__: enter function")
        self.util =  Utils()
        self.runtime = runtime
        self.name = None

        # LXSesion file: Format .ini file: ["lxsession", support, group, key]
        self.lxsession_file_setting = ["lxsession_file", False, None, None]
        # LXSession Dbus: Format Dbus: ["lxsession", support, Method, key1, key2]
        self.lxsession_dbus_setting = ["lxsession_dbus", False, None, None, None]
        # Cinnamon Setting: Format GSettings [group, key]
        self.cinnamon_setting = ["cinnamon", False, None, None]
        # Gnome Setting: Format GSettings [group, key]
        self.gnome_setting = ["gnome", False, None, None]
        # Mate Setting: Format GSettings [group, key]
        self.mate_setting = ["mate", False, None, None]
        # LXQt Setting: Format GSettings [group, key]
        self.lxqt_setting = ["lxqt", False, None, None]
        # GTK3 Setting: Format .ini [group, key]
        self.gtk3_setting = ["gtk3", False, None, None]

        #List of settings
        self.settings_list =    [   self.lxsession_file_setting,
                                    self.lxsession_dbus_setting,
                                    self.cinnamon_setting,
                                    self.gnome_setting,
                                    self.mate_setting,
                                    self.lxqt_setting,
                                    self.gtk3_setting
                                ]

    def get(self):
        logging.info("Setting.get: enter function")
        return_value = None
        for setting in self.settings_list:
            # Check if the setting is handle
            if (setting[1] == True):
                if (setting[0] == "lxsession_file"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["lxsession_file"][3],
                                                            self.lxsession_file_setting[2],
                                                            self.lxsession_file_setting[3],
                                                            None,
                                                            "string")
                elif (setting[0] == "lxsession_dbus"):
                    #TODO
                    #support.lxsession_dbus_runtime.SessionSet(key1,key2)
                    logging.warning("lxsession_dbus not supported")
                elif (setting[0] == "cinnamon"):
                    return_value = self.util.get_setting(   "gsetting",
                                                            None,
                                                            self.cinnamon_setting[2], 
                                                            self.cinnamon_setting[3], 
                                                            None
                                                            "string")
                elif (setting[0] == "gnome"):
                    return_value = self.util.get_setting(   "gsetting",
                                                            None,
                                                            self.gnome_setting[2],
                                                            self.gnome_setting[3],
                                                            None,
                                                            "string")
                elif (setting[0] == "mate"):
                    return_value = self.util.get_setting(   "gsetting",
                                                            None,
                                                            self.mate_setting[2],
                                                            self.mate_setting[3],
                                                            None,
                                                            "string")
                elif (setting[0] == "gtk3"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["gtk3_settings"][3],
                                                            self.gtk3_setting[2],
                                                            self.gtk3_setting[3],
                                                            None,
                                                            "string")
                elif (setting[0] == "lxqt"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["lxqt_settings"][3],
                                                            self.lxqt_setting[2], 
                                                            self.lxqt_setting[3], 
                                                            None,
                                                            "string")
            else:
                logging.warning("%s not supported for %s" % (setting[0], self.name))
        return return_value

    def set(self, value):
        logging.info("Setting.set: enter function")
        current_value = self.get()
        for setting in self.settings_list:
            # Check if the setting is handle
            if (setting[1] == True):
                if (setting[0] == "lxsession_file"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["lxsession_file"][3],
                                                            self.lxsession_file_setting[2],
                                                            self.lxsession_file_setting[3],
                                                            current_value,
                                                            value,
                                                            "string")
                    if (trigger_save == true):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["lxsession_file"][3],
                                                self.runtime.support["lxsession_file"][4])
                elif (setting[0] == "lxsession_dbus"):
                    #TODO
                    #support.lxsession_dbus_runtime.SessionSet(key1,key2)
                    logging.warning("lxsession_dbus not supported")
                elif (setting[0] == "cinnamon"):
                    self.util.set_setting(  "gsetting",
                                            None,
                                            self.cinnamon_setting[2], 
                                            self.cinnamon_setting[3], 
                                            None,
                                            value, 
                                            "string")
                elif (setting[0] == "gnome"):
                    self.util.set_setting(  "gsetting",
                                            None,
                                            self.gnome_setting[2], 
                                            self.gnome_setting[3], 
                                            None,
                                            value, 
                                            "string")
                elif (setting[0] == "mate"):
                    self.util.set_setting(  "gsetting",
                                            None,
                                            self.mate_setting[2], 
                                            self.mate_setting[3], 
                                            None,
                                            value, 
                                            "string")
                elif (setting[0] == "gtk3"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["gtk3_settings"][3],
                                                            self.gtk3_setting[2],
                                                            self.gtk3_setting[3],
                                                            current_value,
                                                            value,
                                                            "string")
                    if (trigger_save == true):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["gtk3_settings"][3],
                                                self.runtime.support["gtk3_settings"][4])
                if (setting[0] == "lxqt"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["lxqt_settings"][3],
                                                            self.lxqt_setting[2],
                                                            self.lxqt_setting[3],
                                                            current_value,
                                                            value,
                                                            "string")
                    if (trigger_save == true):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["lxqt_settings"][3],
                                                self.runtime.support["lxqt_settings"][4])
            else:
                logging.warning("%s not supported for %s" % (setting[0], self.name))

    def set_settings_support(self):
        logging.info("Setting.set_settings_support: enter function")
        if (self.lxsession_file_setting[1] == True):
            self.support_list.append("lxsession")
        elif (self.lxsession_dbus_setting[1] == True):
            self.support_list.append("lxsession")

        if (self.cinnamon_setting[1] == True):
            self.support_list.append("cinnamon")

        if (self.gnome_setting[1] == True):
            self.support_list.append("gnome")

        if (self.mate_setting[1] == True):
            self.support_list.append("mate")

        if (self.gtk3_setting[1] == True):
            self.support_list.append("gtk3")

        if (self.lxqt_setting[1] == True):
            self.support_list.append("lxqt")

    def update_list(self, setting, arg_0, arg_1, arg_2, arg_3):
        setting[0] = arg_0
        setting[1] = arg_1
        setting[2] = arg_2
        setting[3] = arg_3

class IconThemeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("IconThemeSetting.__init__: enter function")
        self.name = "Icon Theme Support"
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "sNet/IconThemeName")
        self.update_list(self.cinnamon_setting, "cinnamon", True, "org.cinnamon.desktop.interface", "icon-theme")
        self.update_list(self.gnome_setting, "gnome", True, "org.gnome.desktop.interface", "icon-theme")
        self.update_list(self.mate_setting, "mate", True, "org.mate.interface", "icon-theme")
        self.update_list(self.lxqt_setting, "lxqt", True, "General", "icon_theme")
        self.update_list(self.gtk3_setting, "gtk3", True, "Settings", "gtk-icon-theme-name")
        self.set_settings_support()

class GtkThemeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("GtkThemeSetting.__init__: enter function")
        self.name = "Gtk Theme Support"
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "sNet/ThemeName")
        self.update_list(self.cinnamon_setting, "cinnamon", True, "org.cinnamon.desktop.interface", "gtk-theme")
        self.update_list(self.gnome_setting, "gnome", True, "org.gnome.desktop.interface", "gtk-theme")
        self.update_list(self.mate_setting, "mate", True, "org.mate.interface", "gtk-theme")
        self.update_list(self.gtk3_setting, "gtk3", True, "Settings", "gtk-theme-name")
        self.set_settings_support()
