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
from xdg import BaseDirectory
import gettext

import logging
import argparse

from .utils import Utils
from .item import Item

_ = gettext.gettext

gettext.install("lx-control-center", "/usr/share/locale")
gettext.bindtextdomain("lx-control-center", "/usr/share/locale")
gettext.textdomain("lx-control-center")

class Main(Utils):
    def __init__(self):
        Utils.__init__(self)

        self.version_config = 0.1
        self.settings_path = None
        self.loglevel_args = None
        self.logfile_args = None

        self.items = {}
        self.items_conf_path = None

        self.desktop_environments = []
        self.trigger_save_settings_file = False
        self.module_activated = None
        self.toolkit = None

        self.keyword_categories_settings_list_default = [   "Settings",
													        "System",
													        "DesktopSettings",
                                                            "X-LXDE-Settings",
                                                            "X-GNOME-Settings-Panel",
													        "X-GNOME-PersonalSettings",
													        "X-XFCE-SettingsDialog",
												            "X-XFCE-HardwareSetting"]
        self.keyword_categories_settings_list = self.keyword_categories_settings_list_default

        self.desktop_environments_setting_default = ["Auto"]
        self.desktop_environments_setting = self.desktop_environments_setting_default

        self.version_config_default = 0.1
        self.version_config = self.version_config_default

        self.modules_support_default = True
        self.modules_support = self.modules_support_default

        self.applications_support_default = True
        self.applications_support = self.applications_support_default

        self.show_category_other_default = True
        self.show_category_other = self.show_category_other_default

        self.blacklist_default = ["debian-xterm.desktop","debian-uxterm.desktop"]
        self.blacklist =  self.blacklist_default

        self.whitelist_default = []
        self.whitelist =  self.whitelist_default

        # Order by importance (first read take advantage)
        self.applications_path_default = ["/usr/share/applications", ";"]
        self.applications_path = self.applications_path_default

        self.modules_path_default = [   "/usr/lib/lx-control-center",
                                        "/usr/share/lx-control-center",
                                        "LXControlCenter/modules/"]
        self.modules_path = self.modules_path_default

        self.categories_fixed_default = False
        self.categories_fixed = self.categories_fixed_default

        self.categories_keys_default = {    _("DesktopSettings"):("DesktopSettings",),
                                            _("HardwareSettings"):("HardwareSettings",),
                                            _("Printing"):("Printing",),
                                            _("System"):("PackageManager","TerminalEmulator"),
                                            _("FileManager"):("FileManager","FileTools","Filesystem"),
                                            _("Monitor"):("Monitor",),
                                            _("Security"):("Security",),
                                            _("Accessibility"):("Accessibility",)
                                        }
        self.categories_keys = self.categories_keys_default
        
        # UI - View
        self.window_size_w_default = 800
        self.window_size_w = self.window_size_w_default

        self.window_size_h_default = 600
        self.window_size_h = self.window_size_h_default

        self.window_icon_default = "preferences-system"
        self.window_icon = self.window_icon_default

        self.window_title_default = _("LX-Control-Center")
        self.window_title = self.window_title_default

        self.icon_view_columns_default = 5
        self.icon_view_columns = self.icon_view_columns_default

        self.icon_view_icons_size_default = 48
        self.icon_view_icons_size = self.icon_view_icons_size_default

        self.icon_not_theme_allow_default = False
        self.icon_not_theme_allow = self.icon_not_theme_allow_default

        self.icon_force_size_default = True
        self.icon_force_size = self.icon_force_size_default

        self.icon_fallback_default = "gtk-stop"
        self.icon_fallback = self.icon_fallback_default

        self.view_mode_default = "icons-all"
        self.view_mode = self.view_mode_default

        self.view_visual_effects_default = False
        self.view_visual_effects = self.view_visual_effects_default

        # Parse command line arguments
        self.get_args_parameters()

        # Enable log
        self.set_log()

        self.categories_triaged = {}
        self.categories_triaged_generate()

        # Function to launch at startup
        self.load_configuration_file()
        self.load_settings()

        self.load_all_applications()
        self.load_all_modules()

        self.desktop_environments_generate()

        # Desactivate items
        self.triage_items()

        # Load specific item conf
        self.load_items_conf()

        # Debug if enable
        self.print_debug()

    def triage_items(self):
        for i in self.items:
            self.apply_applications_modules_suport(i)
            self.apply_desktop_env_sort(i)
            self.apply_try_exec_test(i)
            self.apply_no_exec_applications(i)
            self.apply_blacklist(i)
            self.apply_module_toolkit(i)
            self.apply_items_categories(i)
            self.apply_category_other(i)
            self.apply_whitelist(i)

        self.load_items_conf()

    def get_args_parameters(self):
        parser = argparse.ArgumentParser(description='Launch LX Control Center')
        parser.add_argument('-l', '--log', help='Set log level (values available : WARNING, INFO or DEBUG)')
        parser.add_argument('-f', '--logfile', help='Set log file to write logs')
        args = parser.parse_args()
        self.loglevel_args =  args.log
        self.logfile_args =  args.logfile

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
       

    def load_configuration_file (self):
        """ Set configuration path to self.settings_path"""

        config_dirs = BaseDirectory.xdg_config_dirs

        for path in config_dirs:
            test_path = os.path.join(path,"lx-control-center","settings.conf")
            if(os.path.exists(test_path)):
                self.settings_path = test_path
                break
        if (self.settings_path == None):
            self.settings_path = os.path.join(os.getcwd(), "data","settings.conf")

        logging.debug("load_configuration_file : self.settings_path = %s" % self.settings_path)

    def load_settings (self):
        """ Load settings from self.settings_path"""

        if (self.settings_path is None):
            self.load_configuration_file ()

        keyfile = self.load_inifile(self.settings_path)

        if(os.path.exists(self.settings_path)):
            # Configuration
            self.keyword_categories_settings_list = self.load_setting(keyfile, "Configuration", "desktop_categories", self.keyword_categories_settings_list_default, "list")
            self.desktop_environments_setting = self.load_setting(keyfile, "Configuration", "desktop_environments", self.desktop_environments_setting_default, "list")
            self.version_config = self.load_setting(keyfile, "Configuration", "version_config", self.version_config_default, "float")
            self.modules_support = self.load_setting(keyfile, "Configuration", "modules_support", self.modules_support_default, "boolean")
            self.applications_support = self.load_setting(keyfile, "Configuration", "applications_support", self.applications_support_default, "boolean")
            self.categories_fixed = self.load_setting(keyfile, "Configuration", "categories_fixed", self.categories_fixed_default, "boolean")
            self.show_category_other = self.load_setting(keyfile, "Configuration", "show_category_other", self.show_category_other_default, "boolean")
            self.blacklist = self.load_setting(keyfile, "Configuration","blacklist", self.blacklist_default, "list")
            self.whitelist = self.load_setting(keyfile, "Configuration","whitelist", self.whitelist_default, "list")

            # Categories
            if (self.categories_fixed == False):
                if (keyfile.has_section("Categories")):
                    self.categories_keys.clear()
                    self.categories_triaged.clear()
                    tmp_categories_keys = keyfile.options("Categories")
                    for key in tmp_categories_keys:
                        logging.debug("load_settings: key in tmp_categories_keys = %s" % key)
                        self.categories_keys[key] = self.load_setting(keyfile, "Categories", key, self.categories_keys_default, "list")
                        logging.debug("load_settings: self.categories_keys = %s" % self.categories_keys)
                    self.categories_triaged_generate()

            # Path
            self.applications_path = self.load_setting(keyfile, "Path","applications_path", self.applications_path_default, "list")
            self.modules_path = self.load_setting(keyfile, "Path","modules_path", self.modules_path_default, "list")

            # UI
            self.window_size_w = self.load_setting(keyfile, "UI", "window_size_w", self.window_size_w_default, "int")
            self.window_size_h = self.load_setting(keyfile, "UI", "window_size_h", self.window_size_h_default, "int")
            self.window_icon = self.load_setting(keyfile, "UI", "window_icon", self.window_icon_default, "string")
            self.window_title = self.load_setting(keyfile, "UI", "window_title", self.window_title_default, "string")
            self.icon_view_columns = self.load_setting(keyfile, "UI", "icon_view_columns", self.icon_view_columns_default, "int")
            self.icon_view_icons_size = self.load_setting(keyfile, "UI", "icon_view_icons_size", self.icon_view_icons_size_default, "int")
            self.icon_not_theme_allow = self.load_setting(keyfile, "UI", "icon_not_theme_allow", self.icon_not_theme_allow_default, "boolean")
            self.icon_force_size = self.load_setting(keyfile, "UI", "icon_force_size", self.icon_force_size_default, "boolean")
            self.icon_fallback = self.load_setting(keyfile, "UI", "icon_fallback", self.icon_fallback_default, "string")
            self.view_mode = self.load_setting(keyfile, "UI", "view_mode", self.view_mode_default, "string")
            self.view_visual_effects = self.load_setting(keyfile, "UI", "view_visual_effects", self.view_visual_effects_default, "boolean")

    def load_items_conf(self):
        config_dirs = BaseDirectory.xdg_config_dirs

        for path in config_dirs:
            test_path = os.path.join(path,"lx-control-center","items.conf")
            if(os.path.exists(test_path)):
                self.items_conf_path = test_path
                break

        keyfile = self.load_inifile(self.items_conf_path)

        for keyfile_item in keyfile.sections():
            logging.debug("load_items_conf: keyfile_item =%s" % keyfile_item)
            for setting in keyfile.options(keyfile_item):
                logging.debug("load_items_conf: setting =%s" % setting)
                if (setting == "name"):
                    self.items[keyfile_item].name = keyfile.get(keyfile_item, setting)
                    self.items[keyfile_item].changed = True
                elif (setting == "comment"):
                    self.items[keyfile_item].comment = keyfile.get(keyfile_item, setting)
                    self.items[keyfile_item].changed = True
                elif (setting == "icon"):
                    self.items[keyfile_item].icon = keyfile.get(keyfile_item, setting)
                    self.items[keyfile_item].changed = True
                elif (setting == "activate"):
                    self.items[keyfile_item].activate = keyfile.getboolean(keyfile_item, setting)
                    self.items[keyfile_item].changed = True

    def list_all_applications_from_dirs(self):
        """ List all applications from applications directories"""
        logging.debug("list_all_applications_from_dirs: enter function")
        return_list = []
        for path in self.applications_path:
            try:
                list_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
                for application_file in list_files:
                    app_path = os.path.join(path,application_file)
                    keyfile = None
                    if (os.path.splitext(app_path)[1] == ".desktop"):
                        keyfile = self.load_xdgfile(app_path)
                        categories = []
                        categories = keyfile.getCategories()
                        if (categories != []):
                            to_add = 0
                            for item in self.keyword_categories_settings_list:
                                if (item in categories):
                                    to_add = 1
                            if (to_add == 1):
                                item_to_add = app_path
                                if (item_to_add not in return_list):
                                    return_list.append(app_path)
            except OSError:
                logging.info("list_all_applications_from_dirs: %s not found in applications path" % path)
        return return_list

    def load_all_applications (self):
        list_app = self.list_all_applications_from_dirs()
        logging.debug("load_all_applications: %s" % list_app)
        for i in list_app:
            item = Item(self.categories_triaged)
            item.load_application_from_path(i)
            if (item.check == True):
                self.items[item.path] = item

    def list_all_modules_from_dirs(self):
        return_list = []
        for path in self.modules_path:
            if(os.path.exists(path)):
                list_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                for dirs in list_dirs:
                    dir_path = os.path.join(path, dirs)
                    logging.debug("list_all_modules_from_dirs: list_dirs = %s " % dirs)
                    list_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
                    for module_file in list_files:
                        file_path = os.path.join(dir_path, module_file)
                        logging.debug("list_all_modules_from_dirs: list_files = %s " % module_file)
                        if (os.path.splitext(file_path)[1] == ".desktop"):
                            keyfile = None
                            keyfile = self.load_xdgfile(file_path)
                            return_list.append(file_path)
            else:
                logging.info("list_all_modules_from_dirs: %s doesn't exist in path" % path)
        return return_list

    def load_all_modules (self):
        list_modules = self.list_all_modules_from_dirs()
        logging.debug("load_all_modules: %s :" % list_modules)
        for m in list_modules:
            item = Item(self.categories_triaged)
            item.load_module_from_path(m)
            if (item.check == True):
                self.items[item.path] = item

            to_replace = item.module_replace_application
            for i in self.items:
                for r in to_replace:
                    if (self.items[i].filename == r):
                        self.items[i].activate = False
                        self.items[i].activate_original = False
                        self.items[i].add_deactivate_reason(_("Replaced by an active module"))

    # TODO Store list of running applications, to filter desktop application
    # procs = psutil.process_iter()
    # for proc in procs:
    #   print(proc.name())

    def apply_desktop_env_sort(self, i):
        if (len(self.items[i].not_show_in) != 0):
            for desktop in self.desktop_environments:
                if (desktop in self.items[i].not_show_in):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Current environment in NotShow field"))

        if (self.items[i].activate == True):
            if (len(self.items[i].only_show_in) != 0):
                for desktop in self.desktop_environments:
                    if (desktop not in self.items[i].only_show_in):
                        self.items[i].activate = False
                        self.items[i].activate_original = False
                        self.items[i].add_deactivate_reason(_("Current environment not in OnlyShow field"))

    def apply_try_exec_test(self, i):
        if (self.items[i].type == "application"):
            if (self.items[i].try_exec != ""):
                if (os.path.exists(self.items[i].try_exec) == False):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Excecutable in TryExec doesn't exist"))

    def apply_no_exec_applications(self, i):
        if (self.items[i].type == "application"):
            if (self.items[i].execute_command is None):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Excecutable path doesn't exist"))

    def apply_blacklist (self, i):
        # Test abslotute path
        if (self.items[i].path in self.blacklist):
            self.items[i].activate = False
            self.items[i].activate_original = False
            self.items[i].add_deactivate_reason(_("Blacklisted (absolute path)"))
        # Test desktop file name
        if (self.items[i].filename in self.blacklist):
            self.items[i].activate = False
            self.items[i].activate_original = False
            self.items[i].add_deactivate_reason(_("Blacklisted (desktop file name)"))

    def apply_whitelist (self, i):
        # Test abslotute path
        if (self.items[i].path in self.whitelist):
            self.items[i].activate = True
            self.items[i].activate_original = True
            self.items[i].add_deactivate_reason(_("Whitelisted (absolute path)"))
        # Test desktop file name
        if (self.items[i].filename in self.whitelist):
            self.items[i].activate = True
            self.items[i].activate_original = True
            self.items[i].add_deactivate_reason(_("Whitelisted (desktop file name)"))

    def apply_category_other (self, i):
        if (self.show_category_other == False):
            if (self.items[i].category_other == True):
                self.items[i].activate = False
                self.items[i].activate_original = False
                self.items[i].add_deactivate_reason(_("Category Other deactivated"))

    def apply_applications_modules_suport(self, i):
        if (self.items[i].type == "module"):
            self.items[i].activate = self.modules_support
            self.items[i].activate_original = self.modules_support
        elif (self.items[i].type == "application"):
            self.items[i].activate = self.applications_support
            self.items[i].activate_original = self.modules_support

    def apply_module_toolkit(self, i):
        if (self.items[i].type == "module"):
            if (self.items[i].module_toolkit != None):
                if (self.items[i].module_toolkit != self.toolkit):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Module is not compatible with current toolkit"))

    def apply_items_categories(self, i):
        logging.debug("apply_items_categories: enter fonction with self.categories_triaged = %s" % self.categories_triaged)
        self.items[i].category_array = self.categories_triaged
        self.items[i].define_category_from_list()

    def desktop_environments_generate(self):
        if self.desktop_environments_setting == ["Auto"]:
            new_list = []
            new_list.append(os.getenv("XDG_CURRENT_DESKTOP"))
            self.desktop_environments = new_list
        else:
            self.desktop_environments = self.desktop_environments_setting

    def categories_triaged_generate(self):
        for key in self.categories_keys.keys():
            for item in self.categories_keys[key]:
                if (len(item) > 1):
                    self.categories_triaged[item] = key
                else:
                    to_add = self.categories_keys[key]
                    self.categories_triaged[to_add] = key
                    break

    def save_settings(self):
        keyfile = self.load_inifile(self.settings_path)
        logging.debug("save_settings: loading %s as a keyfile" % self.settings_path)

        # Configuration
        self.save_setting(keyfile, "Configuration","desktop_categories", self.keyword_categories_settings_list, self.keyword_categories_settings_list_default,"list")
        self.save_setting(keyfile, "Configuration","desktop_environments", self.desktop_environments_setting, self.desktop_environments_setting, "list")
        self.save_setting(keyfile, "Configuration", "version_config", self.version_config, self.version_config_default, "float")
        self.save_setting(keyfile, "Configuration", "modules_support", self.modules_support, self.modules_support_default, "boolean")
        self.save_setting(keyfile, "Configuration", "applications_support", self.applications_support, self.applications_support_default, "boolean")
        self.save_setting(keyfile, "Configuration", "categories_fixed", self.categories_fixed, self.categories_fixed_default, "boolean")

        # Categories
        if (self.categories_fixed == False):
            if (self.categories_keys != self.categories_keys_default):
                for category in self.categories_keys:
                    self.save_setting(keyfile, "Categories",category, self.categories_keys[category], None, "list")

        # Path
        self.save_setting(keyfile, "Path","applications_path", self.applications_path, self.applications_path_default, "list")
        self.save_setting(keyfile, "Path","modules_path", self.modules_path, self.modules_path_default, "list")


        # UI
        self.save_setting(keyfile, "UI", "window_size_w", self.window_size_w, self.window_size_w_default, "int")
        self.save_setting(keyfile, "UI", "window_size_h", self.window_size_h, self.window_size_h_default, "int")
        self.save_setting(keyfile, "UI", "window_icon", self.window_icon, self.window_icon_default, "generic")
        self.save_setting(keyfile, "UI", "window_title", self.window_title, self.window_title_default, "generic")
        self.save_setting(keyfile, "UI", "icon_view_columns", self.icon_view_columns, self.icon_view_columns_default, "int")
        self.save_setting(keyfile, "UI", "icon_view_icons_size", self.icon_view_icons_size, self.icon_view_icons_size_default, "int")
        self.save_setting(keyfile, "UI", "icon_not_theme_allow", self.icon_not_theme_allow, self.icon_not_theme_allow_default, "boolean")
        self.save_setting(keyfile, "UI", "icon_force_size", self.icon_force_size, self.icon_force_size_default, "boolean")
        self.save_setting(keyfile, "UI", "icon_fallback", self.icon_fallback, self.icon_fallback_default, "generic")
        self.save_setting(keyfile, "UI", "view_mode", self.view_mode, self.view_mode_default, "generic")
        self.save_setting(keyfile, "UI", "view_visual_effects", self.view_visual_effects, self.view_visual_effects_default, "boolean")

        if (self.trigger_save_settings_file == True):
            self.save_file(keyfile, "settings")
            self.trigger_save_settings_file = False

        # items.conf
        keyfile_items = self.load_inifile(self.items_conf_path)
        logging.debug("save_settings: loading %s as a keyfile_items" % self.items_conf_path)

        for i in self.items:
            if (self.items[i].changed == True):
                self.save_setting(keyfile_items, self.items[i].path, "name", self.items[i].name, self.items[i].name_original, "generic")
                self.save_setting(keyfile_items, self.items[i].path, "icon", self.items[i].icon, self.items[i].icon_original, "generic")
                self.save_setting(keyfile_items, self.items[i].path, "comment", self.items[i].comment, self.items[i].comment_original, "generic")
                self.save_setting(keyfile_items, self.items[i].path, "activate", self.items[i].activate, self.items[i].activate_original, "boolean")

        if (self.trigger_save_settings_file == True):
            self.save_file(keyfile_items, "items")
            self.trigger_save_settings_file = False

    def save_setting(self, keyfile, group, key, variable, default, type_to_set):
        logging.debug("save_setting: group, key and variable => %s, %s, %s" %(group, key, variable))
        if (variable == default):
            logging.debug("save_setting: variable == default, checking for existing key")
            if(keyfile.has_option(group, key)):
                logging.debug("save_setting: variable == default, existing key, removing")
                keyfile.remove_option(group, key)
                self.trigger_save_settings_file = True
            # TODO Remove section if it's empty
        else:
            if (keyfile.has_section(group) == False):
                keyfile.add_section(group)
                self.trigger_save_settings_file = True

            if (type_to_set == "float"):
                if (keyfile.has_option(group, key) == False):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True 
  
                elif (keyfile.getfloat(group, key) != variable):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True

            elif(type_to_set == "int"):
                if (keyfile.has_option(group, key) == False):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True
                
                elif (keyfile.getint(group, key) != variable):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True

            elif(type_to_set == "boolean"):
                if (keyfile.has_option(group, key) == False):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True

                elif (keyfile.getboolean(group, key) != variable):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True

            elif(type_to_set == "list"):
                if (keyfile.has_option(group, key) == False):
                    list_to_save = ';'.join(variable) + ";"
                    keyfile.set(group, key, list_to_save)
                    self.trigger_save_settings_file = True

                elif (keyfile.get(group, key) != variable):
                    list_to_save = ';'.join(variable) + ";"
                    keyfile.set(group, key, list_to_save)
                    self.trigger_save_settings_file = True
            else:
                if (keyfile.has_option(group, key) == False):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True

                elif (keyfile.get(group, key) != variable):
                    keyfile.set(group, key, str(variable))
                    self.trigger_save_settings_file = True

    def save_file(self, keyfile, settings_type):
        dir_path = os.path.join(os.path.expanduser('~'), ".config","lx-control-center")
        file_path = settings_type + ".conf"
        home_path = os.path.join(dir_path, file_path)

        if (self.settings_path != home_path):
            self.settings_path = home_path

        if (os.path.exists(dir_path) == False):
            logging.debug("save_file: Directory doesn't exist => create it")
            os.makedirs(dir_path)

        if (os.path.exists(home_path) == False):
            logging.debug("save_file: File doesn't exist => create it")
            file_to_create = open(home_path,'a')
            file_to_create.close()

        logging.debug("save_file: Save file on %s" % home_path)
        file_to_save = open(home_path,'w')
        keyfile.write(file_to_save)
        file_to_save.close()

    def set_setting(self, group, key, variable):
        if (group == "Configuration"):
            if (key == "modules_support"):
                self.modules_support = variable
            elif (key == "applications_support"):
                self.applications_support = variable
            elif (key == "icon_view_icons_size"):
                self.icon_view_icons_size = variable
            else:
                logging.debug("set_setting: %s - %s not implemented" % (group, key))
        else:
            logging.debug("set_setting: %s - %s not implemented" % (group, key))
            
    def module_active(self,item):
        self.module_activated = item

    def print_debug(self):
        """ Prints variables and other useful items for debug purpose"""
        logging.debug("Printing variables")
        logging.debug("self.settings_path : %s" % self.settings_path)
        logging.debug("self.keyword_categories_settings_list : %s" % self.keyword_categories_settings_list)
        logging.debug("self.applications_path : %s" % self.applications_path)
        logging.debug("self.modules_path : %s" % self.modules_path)
        logging.debug("self.applications_support: %s" % self.applications_support)
        logging.debug("self.modules_support: %s" % self.modules_support)
        logging.debug("self.categories_triaged: %s" % self.categories_triaged)
        logging.debug("self.categories_keys : %s" % self.categories_keys)
        logging.debug("self.desktop_environments : %s" % self.desktop_environments)
        logging.debug("Print items")
        for i in self.items:
            logging.debug("Item name : %s" % self.items[i].name)
            logging.debug("Item filename : %s" % self.items[i].filename)
            logging.debug("Item path : %s" % self.items[i].path)
            logging.debug("Item category : %s" % self.items[i].category)
            logging.debug("Item icon : %s" % self.items[i].icon)
            logging.debug("Item only_show_in : %s" % self.items[i].only_show_in)
            logging.debug("Item not_show_in : %s" % self.items[i].not_show_in)
            logging.debug("Item execute : %s" % self.items[i].execute_command)
            logging.debug("Item activate : %s" % self.items[i].activate)
            logging.debug("Item changed : %s" % self.items[i].changed)
            logging.debug("Item check : %s" % self.items[i].check)
            logging.debug("Item module_replace_application : %s" % self.items[i].module_replace_application)
            logging.debug("Item module_toolkit : %s" % self.items[i].module_toolkit)
            logging.debug("=================")

