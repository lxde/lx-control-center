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
import gettext

from LXControlCenter.utils import Utils

_ = gettext.gettext

# Documentation / Examples
# LXDE / LXSession: https://github.com/lxde/lxsession/blob/master/data/desktop.conf.example
#                   https://wiki.lxde.org/en/index.php?title=LXSession
# LXQt: https://github.com/lxde/lxqt-session/blob/master/config/lxqt.conf
# Ubuntu / GNOME: https://code.launchpad.net/~vcs-imports/ubuntu-tweak/master
# GNOME:  https://git.gnome.org/browse/gnome-tweak-tool/tree/
# Cinnamon: https://github.com/linuxmint/Cinnamon/tree/master/files/usr/share/cinnamon/cinnamon-settings/modules
# Mate: https://github.com/mate-desktop/mate-control-center/blob/master/capplets/appearance/appearance.h

class Setting():
    def __init__(self, runtime):
        logging.info("Setting.__init__: enter function")
        self.util =  Utils()
        self.runtime = runtime

        self.name = None
        self.setting_type = "string"

        self.available_values = {}

        # LXSesion file: Format .ini file: ["lxsession", support, group, key]
        self.lxsession_file_setting = ["lxsession_file", False, None, None]
        # LXSession Dbus: Format Dbus: ["lxsession", support, Method, key1, key2]
        self.lxsession_dbus_setting = ["lxsession_dbus", False, None, None, None]
        # Cinnamon Setting: Format GSettings [group, key]
        self.cinnamon_setting = ["cinnamon_settings", False, None, None]
        # Gnome Setting: Format GSettings [group, key]
        self.gnome_setting = ["gnome_settings", False, None, None]
        # Mate Setting: Format GSettings [group, key]
        self.mate_setting = ["mate_settings", False, None, None]
        # LXQt Setting: Format GSettings [group, key]
        self.lxqt_setting = ["lxqt_settings", False, None, None]
        # GTK3 Setting: Format .ini [group, key]
        self.gtk3_setting = ["gtk3_settings", False, None, None]
        # Openbox Setting: Format xml [support, Tag1, Tag2]
        self.openbox_setting = ["openbox_settings", False, None, None]
        # LX Control Center: Format .ini file ["lx_control_center_setting", support, group, key]
        self.lx_control_center_setting = ["lx_control_center_setting", False, None, None]

        #List of settings
        self.settings_list =    [   self.lxsession_file_setting,
                                    self.lxsession_dbus_setting,
                                    self.cinnamon_setting,
                                    self.gnome_setting,
                                    self.mate_setting,
                                    self.lxqt_setting,
                                    self.gtk3_setting,
                                    self.openbox_setting,
                                    self.lx_control_center_setting
                                ]

        self.support_list = []

    def get(self):
        logging.info("Setting.get: enter function")
        return_value = None
        # TODO Break when we found a setting ?
        for setting in self.support_list:
            # Check if the setting is handle
            if (setting[1] == True):
                if (setting[0] == "lx_control_center_setting"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["lx_control_center_setting"][3],
                                                            self.lx_control_center_setting[2],
                                                            self.lx_control_center_setting[3],
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "lxsession_file"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["lxsession_file"][3],
                                                            self.lxsession_file_setting[2],
                                                            self.lxsession_file_setting[3],
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "lxsession_dbus"):
                    #TODO
                    #support.lxsession_dbus_runtime.SessionSet(key1,key2)
                    logging.warning("lxsession_dbus not supported")
                elif (setting[0] == "cinnamon_settings"):
                    return_value = self.util.get_setting(   "gsetting",
                                                            None,
                                                            self.cinnamon_setting[2], 
                                                            self.cinnamon_setting[3], 
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "gnome_settings"):
                    return_value = self.util.get_setting(   "gsetting",
                                                            None,
                                                            self.gnome_setting[2],
                                                            self.gnome_setting[3],
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "mate_settings"):
                    return_value = self.util.get_setting(   "gsetting",
                                                            None,
                                                            self.mate_setting[2],
                                                            self.mate_setting[3],
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "gtk3_settings"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["gtk3_settings"][3],
                                                            self.gtk3_setting[2],
                                                            self.gtk3_setting[3],
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "lxqt_settings"):
                    return_value = self.util.get_setting(   "keyfile",
                                                            self.runtime.support["lxqt_settings"][3],
                                                            self.lxqt_setting[2], 
                                                            self.lxqt_setting[3], 
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                elif (setting[0] == "openbox_settings"):
                    return_value = self.util.get_setting(   "xml",
                                                            self.runtime.support["openbox_settings"][3],
                                                            self.openbox_setting[2],
                                                            self.openbox_setting[3],
                                                            None,
                                                            self.setting_type)
                    return_value = self.transcode_values(setting[0], return_value)
                else:
                    logging.warning("%s not supported for %s" % (setting[0], self.name))
        if (return_value is None and self.default_value is not None):
            return_value = self.default_value
        return return_value

    def set(self, value):
        logging.info("Setting.set: enter function")
        current_value = self.get()
        for setting in self.support_list:
            # Check if the setting is handle
            if (setting[1] == True):
                if (setting[0] == "lx_control_center_setting"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["lx_control_center_setting"][3],
                                                            self.lx_control_center_setting[2],
                                                            self.lx_control_center_setting[3],
                                                            self.transcode_values(setting[0], value),
                                                            self.default_value,
                                                            self.setting_type)
                    if (trigger_save == True):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["lx_control_center_setting"][3],
                                                self.runtime.support["lx_control_center_setting"][4])
                elif (setting[0] == "lxsession_file"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["lxsession_file"][3],
                                                            self.lxsession_file_setting[2],
                                                            self.lxsession_file_setting[3],
                                                            self.transcode_values(setting[0], value),
                                                            current_value,
                                                            self.setting_type)
                    if (trigger_save == True):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["lxsession_file"][3],
                                                self.runtime.support["lxsession_file"][4])
                elif (setting[0] == "lxsession_dbus"):
                    #TODO
                    #support.lxsession_dbus_runtime.SessionSet(key1,key2)
                    logging.warning("lxsession_dbus not supported")
                elif (setting[0] == "cinnamon_settings"):
                    self.util.set_setting(  "gsetting",
                                            None,
                                            self.cinnamon_setting[2],
                                            self.cinnamon_setting[3],
                                            self.transcode_values(setting[0], value),
                                            current_value,
                                            self.setting_type)
                elif (setting[0] == "gnome_settings"):
                    self.util.set_setting(  "gsetting",
                                            None,
                                            self.gnome_setting[2], 
                                            self.gnome_setting[3],
                                            self.transcode_values(setting[0], value),
                                            current_value, 
                                            self.setting_type)
                elif (setting[0] == "mate_settings"):
                    self.util.set_setting(  "gsetting",
                                            None,
                                            self.mate_setting[2], 
                                            self.mate_setting[3], 
                                            self.transcode_values(setting[0], value),
                                            current_value, 
                                            self.setting_type)
                elif (setting[0] == "gtk3_settings"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["gtk3_settings"][3],
                                                            self.gtk3_setting[2],
                                                            self.gtk3_setting[3],
                                                            self.transcode_values(setting[0], value),
                                                            current_value,
                                                            self.setting_type)
                    if (trigger_save == True):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["gtk3_settings"][3],
                                                self.runtime.support["gtk3_settings"][4])
                elif (setting[0] == "lxqt_settings"):
                    trigger_save = self.util.set_setting(   "keyfile",
                                                            self.runtime.support["lxqt_settings"][3],
                                                            self.lxqt_setting[2],
                                                            self.lxqt_setting[3],
                                                            self.transcode_values(setting[0], value),
                                                            current_value,
                                                            self.setting_type)
                    if (trigger_save == True):
                        self.util.save_object(  "keyfile",
                                                self.runtime.support["lxqt_settings"][3],
                                                self.runtime.support["lxqt_settings"][4])
                elif (setting[0] == "openbox_settings"):
                    trigger_save = self.util.set_setting(   "xml",
                                                            self.runtime.support["openbox_settings"][3],
                                                            self.openbox_setting[2],
                                                            self.openbox_setting[3],
                                                            self.transcode_values(setting[0], value),
                                                            current_value,
                                                            self.setting_type)
                    if (trigger_save == True):
                        self.util.save_object(  "xml",
                                                self.runtime.support["openbox_settings"][3],
                                                self.runtime.support["openbox_settings"][4])
                        self.util.launch_command("openbox --reconfigure")
                else:
                    logging.warning("%s not supported for %s" % (setting[0], self.name))

        self.set_after_hooks(value)

    def set_settings_support(self):
        logging.info("Setting.set_settings_support: enter function")
        if (self.lxsession_file_setting[1] == True):
            if (self.runtime.support["lxsession_file"][2] == True):
                self.support_list.append(self.lxsession_file_setting)

        if (self.lxsession_dbus_setting[1] == True):
            if (self.runtime.support["lxsession_dbus"][2] == True):
                self.support_list.append(self.lxsession_dbus_setting)

        if (self.cinnamon_setting[1] == True):
            if (self.runtime.support["cinnamon_settings"][2] == True):
                self.support_list.append(self.cinnamon_setting)

        if (self.gnome_setting[1] == True):
            if (self.runtime.support["gnome_settings"][2] == True):
                self.support_list.append(self.gnome_setting)

        if (self.mate_setting[1] == True):
            if (self.runtime.support["mate_settings"][2] == True):
                self.support_list.append(self.mate_setting)

        if (self.gtk3_setting[1] == True):
            if (self.runtime.support["gtk3_settings"][2] == True):
                self.support_list.append(self.gtk3_setting)

        if (self.lxqt_setting[1] == True):
            if (self.runtime.support["lxqt_settings"][2] == True):
                self.support_list.append(self.lxqt_setting)

        if (self.openbox_setting[1] == True):
            if (self.runtime.support["openbox_settings"][2] == True):
                self.support_list.append(self.openbox_setting)

        if (self.lx_control_center_setting[1] == True):
            if (self.runtime.support["lx_control_center_setting"][2] == True):
                self.support_list.append(self.lx_control_center_setting)

    def update_list(self, setting, arg_0, arg_1, arg_2, arg_3):
        setting[0] = arg_0
        setting[1] = arg_1
        setting[2] = arg_2
        setting[3] = arg_3

    def set_after_hooks(self, value):
        """ Function to launch after set function """
        pass
    
    def transcode_values(self, setting, value):
        return value

# Control Center
class ModulesSupportControlCenterSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("ModulesSupportControlCenterSetting.__init__: enter function")
        self.name = "Modules Support for Control Center"
        self.display_name = _("Activate modules support")
        self.setting_type = "boolean"
        self.default_value = True
        self.update_list(self.lx_control_center_setting, "lx_control_center_setting", True, "Configuration", "modules_support")
        self.set_settings_support()

class ApplicationsSupportControlCenterSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("ApplicationsSupportControlCenterSetting.__init__: enter function")
        self.name = "Applications Support for Control Center"
        self.display_name = _("Activate applications support")
        self.setting_type = "boolean"
        self.default_value = True
        self.update_list(self.lx_control_center_setting, "lx_control_center_setting", True, "Configuration", "applications_support")
        self.set_settings_support()

class CategoryOtherControlCenterSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("CategoryOtherControlCenterSetting.__init__: enter function")
        self.name = "Show Category Other for Control Center"
        self.display_name = _("Show category Other")
        self.setting_type = "boolean"
        self.default_value = True
        self.update_list(self.lx_control_center_setting, "lx_control_center_setting", True, "Configuration", "show_category_other")
        self.set_settings_support()

class ModulesExperimentalControlCenterSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("ModulesExperimentalControlCenterSetting.__init__: enter function")
        self.name = "Experimental Modules for Control Center"
        self.display_name = _("Enable experimental modules")
        self.setting_type = "boolean"
        self.default_value = False
        self.update_list(self.lx_control_center_setting, "lx_control_center_setting", True, "Configuration", "modules_experimental_support")
        self.set_settings_support()

class IconsSizeControlCenterSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("IconsSizeControlCenterSetting.__init__: enter function")
        self.name = "Icons Size for Control Center"
        self.display_name = _("Icon size for the view")
        self.setting_type = "int"
        self.default_value = 48
        self.update_list(self.lx_control_center_setting, "lx_control_center_setting", True, "UI", "icon_view_icons_size")
        self.set_settings_support()

# Theme
# GNOME / GTK: https://git.gnome.org/browse/gnome-tweak-tool/tree/gtweak/tweaks/tweak_group_appearance.py
# LXSession: https://github.com/lxde/lxsession/blob/master/data/desktop.conf.example
# LXQt: https://github.com/lxde/lxqt-session/blob/master/config/lxqt.conf
# Cinnamon: https://github.com/linuxmint/Cinnamon/blob/master/files/usr/share/cinnamon/cinnamon-settings/modules/cs_themes.py
# Mate: https://github.com/mate-desktop/mate-control-center/blob/master/capplets/appearance/appearance.h
# GTK3: https://developer.gnome.org/gtk3/stable/GtkSettings.html

class IconThemeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("IconThemeSetting.__init__: enter function")
        self.name = "Icon Theme Support"
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "sNet/IconThemeName")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.desktop.interface", "icon-theme")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "icon-theme")
        self.update_list(self.mate_setting, "mate_settings", True, "org.mate.interface", "icon-theme")
        self.update_list(self.lxqt_setting, "lxqt_settings", True, "General", "icon_theme")
        self.update_list(self.gtk3_setting, "gtk3_settings", True, "Settings", "gtk-icon-theme-name")
        self.set_settings_support()

class GtkThemeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("GtkThemeSetting.__init__: enter function")
        self.name = "Gtk Theme Support"
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "sNet/ThemeName")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.desktop.interface", "gtk-theme")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "gtk-theme")
        self.update_list(self.mate_setting, "mate_settings", True, "org.mate.interface", "gtk-theme")
        self.update_list(self.gtk3_setting, "gtk3_settings", True, "Settings", "gtk-theme-name")
        self.set_settings_support()

class CursorThemeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("CursorThemeSetting.__init__: enter function")
        self.name = "Cursor Theme Support"
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "sGtk/CursorThemeName")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.desktop.interface", "cursor-theme")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "cursor-theme")
        self.update_list(self.mate_setting, "mate_settings", True, "org.mate.interface", "cursor-theme")
        self.update_list(self.gtk3_setting, "gtk3_settings", True, "Settings", "gtk-cursor-theme-name")
        self.set_settings_support()

    def set_after_hooks(self, value):
        #TODO Link default icon theme to apply cursor theme
        index_file_path = os.path.join(os.path.expanduser("~"), ".icons", "default", "index.theme")
        #if (os.path.exist(index_file_path) == False):
            #create the file
        #else:
        keyfile = self.util.load_object ("keyfile", index_file_path)
        self.util.set_setting("keyfile", keyfile, "Icon Theme", "Name", "Default", None, "string")
        self.util.set_setting("keyfile", keyfile, "Icon Theme", "Comment", "Default Cursor Theme", None, "string")
        self.util.set_setting("keyfile", keyfile, "Icon Theme", "Inherits", value, None, "string")
        self.util.save_object ("keyfile", keyfile, index_file_path)


class CursorSizeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("CursorSizeSetting.__init__: enter function")
        self.name = "Cursor Size Support"
        self.setting_type = "int"
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "iGtk/CursorThemeSize")
        self.update_list(self.mate_setting, "mate_settings", True, "org.mate.interface", "cursor-size")
        self.update_list(self.gtk3_setting, "gtk3_settings", True, "Settings", "gtk-cursor-theme-size")
        self.set_settings_support()

class OpenboxThemeSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("OpenboxThemeSetting.__init__: enter function")
        self.name = "Openbox Theme Support"
        self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "name")
        self.set_settings_support()

# Font Settings
class DefaultFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("DefaultFontSetting.__init__: enter function")
        self.name = "Default Font Support"
        self.display_name = _("Default Font")
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "sGtk/FontName")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.desktop.interface", "font-name")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "font-name")
        self.set_settings_support()

class MonospaceFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("MonospaceFontSetting.__init__: enter function")
        self.name = "Monospace Font Support"
        self.display_name = _("Monospace font")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "monospace-font-name")
        self.set_settings_support()

class DocumentFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("DocumentFontSetting.__init__: enter function")
        self.name = "Document Font Support"
        self.display_name = _("Document font")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "document-font-name")
        self.set_settings_support()

class TextScalingFactorSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("TextScalingFactorSetting.__init__: enter function")
        self.name = "Text Scaling Factor Support"
        self.display_name = _("Text scaling factor")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.interface", "text-scaling-factor")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.desktop.interface", "text-scaling-factor")
        self.set_settings_support()

class HintingSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("HintingSetting.__init__: enter function")
        self.name = "Hinting Support"
        self.display_name = _("Hinting")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.settings-daemon.plugins.xsettings", "hinting")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.settings-daemon.plugins.xsettings", "hinting")
        self.set_settings_support()
        #values=('none', 'slight', 'medium', 'full'),
        #texts=(_('No hinting'), _('Basic'),_('Moderate'),_('Maximum')),
        #lxsession GTK #iXft/Hinting & #iXft/HintStyle

class AntialiasingSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("AntialiasingSetting.__init__: enter function")
        self.name = "Antialiasing Support"
        self.display_name = _("Antialiasing")
        self.available_values["none"] = _('No antialiasing')
        self.available_values["grayscale"] = _('Standard grayscale antialiasing')
        self.available_values["rgba"] = _('Subpixel antialiasing (LCD screens only)')
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.settings-daemon.plugins.xsettings", "antialiasing")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.settings-daemon.plugins.xsettings", "antialiasing")
        self.update_list(self.lxsession_file_setting, "lxsession_file", True, "GTK", "iXft/Antialias")
        self.set_settings_support()

    def transcode_values(self, setting, value):
        # lxsession values:
        lxsession = {}
        lxsession["none"] = "0"
        lxsession["grayscale"] = "1"
        lxsession["rgba"] = "1"
        # Reverse
        lxsession["1"] = "grayscale"
        lxsession["0"] = "none"

        return_value = value
        if (setting == "lxsession_file"):
            return_value = lxsession[value]
        return return_value

class RGBASetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("RGBASetting.__init__: enter function")
        self.name = "RGBA Support"
        self.display_name = _("RGBA")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.settings-daemon.plugins.xsettings", "rgba-order")
        self.set_settings_support()
        #"The order of subpixel elements on an LCD screen, only used when antialiasing is set to 'rgba'"
        #rgba_options = [["rgba", _("Rgba")], ["rgb", _("Rgb")], ["bgr", _("Bgr")], ["vrgb", _("Vrgb")], ["vbgr", _("Vbgr")]]
        #lxsession GTK #iXft/RGBA

class WindowTitleBarFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("WindowTitleBarFontSetting.__init__: enter function")
        self.name = "Window Title Bar Font Support"
        self.display_name = _("Window Title Bar Font")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.desktop.wm.preferences", "titlebar-font")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.cinnamon.desktop.wm.preferences", "titlebar-font")
        #TODO Gconf
        #/apps/metacity/general/titlebar_font
        self.set_settings_support()

class ActiveWindowFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("ActiveWindowFontSetting.__init__: enter function")
        self.name = "Active Window Font Setting Support"
        self.display_name = _("Active Window Font")
        #TODO openbox theme font place="ActiveWindow" name
        #self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "font")
        self.set_settings_support()

class InactiveWindowFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("InactiveWindowFontSetting.__init__: enter function")
        self.name = "Inactive Window Font Setting Support"
        self.display_name = _("Inactive Window Font")
        #TODO openbox theme font place="InactiveWindow" name
        #self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "font")
        self.set_settings_support()

class MenuHeaderWindowFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("MenuHeaderWindowFontSetting.__init__: enter function")
        self.name = "Menu Header Window Font Setting Support"
        self.display_name = _("Menu Header Window Font")
        #TODO openbox theme font place="MenuHeader" name
        #self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "font")
        self.set_settings_support()

class MenuItemWindowFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("MenuItemWindowFontSetting.__init__: enter function")
        self.name = "Menu Item Window Font Setting Support"
        self.display_name = _("Menu Item Window Font")
        #TODO openbox theme font place="MenuItem" name
        #self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "font")
        self.set_settings_support()

class ActiveOnScreenDisplayWindowFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("ActiveOnScreenDisplayWindowFontSetting.__init__: enter function")
        self.name = "Active On Screen Display Window Font Setting Support"
        self.display_name = _("Active On Screen Display Window Font")
        #TODO openbox theme font place="ActiveOnScreenDisplay" name
        #self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "font")
        self.set_settings_support()

class InactiveOnScreenDisplayWindowFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("Inactive OnScreenDisplayWindowFontSetting.__init__: enter function")
        self.name = "Inactive On Screen Display Window Font Setting Support"
        self.display_name = _("Inactive On Screen Display Window Font")
        #TODO openbox theme font place="InactiveOnScreenDisplay" name
        #self.update_list(self.openbox_setting, "openbox_settings", True, "theme", "font")
        self.set_settings_support()

class DesktopFontSetting(Setting):
    def __init__(self, support):
        Setting.__init__(self, support)
        logging.info("DesktopFontSetting.__init__: enter function")
        self.name = "Desktop Font Support"
        self.display_name = _("Desktop Font Font")
        self.update_list(self.gnome_setting, "gnome_settings", True, "org.gnome.nautilus.desktop", "font")
        self.update_list(self.cinnamon_setting, "cinnamon_settings", True, "org.nemo.desktop", "font")
        #TODO PCManfm
        #pcmanfm.conf [desktop] desktop_font
        self.set_settings_support()
        