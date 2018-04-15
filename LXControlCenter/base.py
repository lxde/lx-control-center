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
import gettext

import logging
import collections

from LXControlCenter.utils import Utils
from LXControlCenter.item import Item
from LXControlCenter.runtime import Runtime
from LXControlCenter.setting import *

_ = gettext.gettext

gettext.install("lx-control-center", "/usr/share/locale")
gettext.bindtextdomain("lx-control-center", "/usr/share/locale")
gettext.textdomain("lx-control-center")

class Base(Utils):
    def __init__(self):
        logging.info("Base__init__: enter function")

        self.util = Utils()
        self.runtime = Runtime()

        # Base
        self.version_config = 0.1
        self.keyfile_settings = None
        self.keyfile_items = None

        self.items = {}
        self.items_conf_path = None

        self.desktop_environments = []
        self.trigger_save_settings_file = False
        self.module_activated = None
        self.toolkit = None
        self.standalone_module = None

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

        self.frontend_control_center_setting = FrontendControlCenterSetting(self.runtime)

        self.frontend = "GTK3"

        self.version_config_default = 0.1
        self.version_config = self.version_config_default

        self.modules_support_control_center_setting = ModulesSupportControlCenterSetting(self.runtime)
        self.modules_experimental_control_center_setting = ModulesExperimentalControlCenterSetting(self.runtime)
        self.applications_support_control_center_setting = ApplicationsSupportControlCenterSetting(self.runtime)
        self.category_other_control_center_setting = CategoryOtherControlCenterSetting(self.runtime)

        self.blacklist_default = ["debian-xterm.desktop","debian-uxterm.desktop"]
        self.blacklist =  self.blacklist_default

        self.whitelist_default = []
        self.whitelist =  self.whitelist_default

        # Order by importance (first read take advantage)
        self.applications_path_default = ["/usr/share/applications"]
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

        self.categories_triaged = {}
        
        # UI - View
        self.window_size_w_default = 800
        self.window_size_w = self.window_size_w_default

        self.window_size_h_default = 600
        self.window_size_h = self.window_size_h_default

        self.window_icon_default = "preferences-system"
        self.window_icon = self.window_icon_default

        self.window_title_default = _("LX-Control-Center")
        self.window_title = self.window_title_default

        self.icon_view_columns_default = 3
        self.icon_view_columns = self.icon_view_columns_default

        self.icons_size_control_center_setting = IconsSizeControlCenterSetting(self.runtime)

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

        # UI

        # Items visible in the view, to be display
        self.items_visible = []

        # Items visible, triage by categories
        self.items_visible_by_categories = {}

        # Items, triage by categories
        self.items_by_categories = {}

        # Different mode of display the UI :
        #  - main-UI => Icons view
        #  - pref-UI => Preferences view
        #  - edit-UI => Edit mode of the icons view
        #  - edit-item-UI => Edit an item, after clicking on a icon of edit mode
        #  - category-UI => View of only 1 category
        #  - module-UI ==> Display the current module loaded
        self.mode = "main-UI"

        # Menu items labels & tooltips
        self.icons_menu_item = _("Icons")
        self.preferences_menu_item = _("Preferences")
        self.edit_menu_item = _("Edit")
        # TODO Find something useful to display
        self.icons_menu_item_tooltip = _("Icons")
        self.preferences_menu_item_tooltip = _("Preferences")
        self.edit_menu_item_tooltip = _("Edit")

        # Pref Mode labels
        self.pref_category_configuration_label = _("Configuration")
        self.pref_category_ui_label = _("Visual")

        # UI Items
        self.content_ui_vbox = None
        self.search_string = None

    def init(self):
        logging.info("Base.init: enter function")
        # Load configuration file, and the settings in it
        self.load_settings()
        # Normal startup, if no module arg set
        if (self.standalone_module == None):
            self.load_all_applications()
            self.load_all_modules()
            self.desktop_environments_generate()

            # Desactivate items
            self.triage_items()

            # Load specific item conf
            self.load_items_conf()
        else:
            self.load_all_modules()
            for i in self.items:
                self.triage_modules(i)

        # Debug if enable
        self.print_debug()

    # Base functions
    def triage_items(self):
        logging.info("Base.triage_items: enter function")
        for i in self.items:
            self.apply_applications_modules_suport(i)
            self.triage_modules(i)
            self.apply_desktop_env_sort(i)
            self.apply_try_exec_test(i)
            self.apply_no_exec_applications(i)
            self.apply_blacklist(i)
            self.apply_module_toolkit(i)
            self.apply_items_categories(i)
            self.apply_category_other(i)
            self.apply_whitelist(i)

        self.load_items_conf()

    def triage_modules(self, item):
        logging.info("Base.triage_modules: enter function")
        self.apply_module_experimental_support(item)
        self.apply_module_toolkit(item)
       
    def load_settings (self):
        logging.info("Base.load_settings: enter function")
        """ Load settings from lx-control-center/settings.conf"""
        self.keyfile_settings = self.runtime.support["lx_control_center_setting"][3]

        if(self.keyfile_settings != None):
            # Configuration
            self.keyword_categories_settings_list = self.util.get_setting("keyfile", self.keyfile_settings, "Configuration", "desktop_categories", self.keyword_categories_settings_list_default, "list")
            self.desktop_environments_setting = self.util.get_setting("keyfile", self.keyfile_settings, "Configuration", "desktop_environments", self.desktop_environments_setting_default, "list")
            self.frontend_setting = self.frontend_control_center_setting.get()
            self.version_config = self.util.get_setting("keyfile", self.keyfile_settings, "Configuration", "version_config", self.version_config_default, "float")
            self.modules_support = self.modules_support_control_center_setting.get()
            self.modules_experimental_support = self.modules_experimental_control_center_setting.get()
            self.applications_support = self.applications_support_control_center_setting.get()
            self.categories_fixed = self.util.get_setting("keyfile", self.keyfile_settings, "Configuration", "categories_fixed", self.categories_fixed_default, "boolean")
            self.show_category_other = self.category_other_control_center_setting.get()
            self.blacklist = self.util.get_setting("keyfile", self.keyfile_settings, "Configuration","blacklist", self.blacklist_default, "list")
            self.whitelist = self.util.get_setting("keyfile", self.keyfile_settings, "Configuration","whitelist", self.whitelist_default, "list")

            # Categories
            if (self.categories_fixed == False):
                if (self.keyfile_settings.has_section("Categories")):
                    self.categories_keys.clear()
                    self.categories_triaged.clear()
                    tmp_categories_keys = self.keyfile_settings.options("Categories")
                    for key in tmp_categories_keys:
                        logging.debug("load_settings: key in tmp_categories_keys = %s" % key)
                        self.categories_keys[key] = self.util.get_setting("keyfile", self.keyfile_settings, "Categories", key, self.categories_keys_default, "list")
                        logging.debug("load_settings: self.categories_keys = %s" % self.categories_keys)
                self.categories_triaged_generate()

            # Path
            self.applications_path = self.util.get_setting("keyfile", self.keyfile_settings, "Path","applications_path", self.applications_path_default, "list")
            self.modules_path = self.util.get_setting("keyfile", self.keyfile_settings, "Path","modules_path", self.modules_path_default, "list")

            # UI
            self.window_size_w = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "window_size_w", self.window_size_w_default, "int")
            self.window_size_h = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "window_size_h", self.window_size_h_default, "int")
            self.window_icon = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "window_icon", self.window_icon_default, "string")
            self.window_title = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "window_title", self.window_title_default, "string")
            self.icon_view_columns = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "icon_view_columns", self.icon_view_columns_default, "int")
            self.icon_view_icons_size = self.icons_size_control_center_setting.get()
            self.icon_not_theme_allow = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "icon_not_theme_allow", self.icon_not_theme_allow_default, "boolean")
            self.icon_force_size = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "icon_force_size", self.icon_force_size_default, "boolean")
            self.icon_fallback = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "icon_fallback", self.icon_fallback_default, "string")
            self.view_mode = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "view_mode", self.view_mode_default, "string")
            self.view_visual_effects = self.util.get_setting("keyfile", self.keyfile_settings, "UI", "view_visual_effects", self.view_visual_effects_default, "boolean")

    def load_items_conf(self):
        logging.info("Base.load_items_conf: enter function")
        if (self.keyfile_items == None):
            self.keyfile_items = self.util.load_object("ini", os.path.join("lx-control-center","items.conf"))

        for keyfile_item in self.keyfile_items.sections():
            logging.debug("load_items_conf: keyfile_item =%s" % keyfile_item)
            for setting in self.keyfile_items.options(keyfile_item):
                logging.debug("load_items_conf: setting =%s" % setting)
                if (setting == "name"):
                    self.items[keyfile_item].name = self.keyfile_items.get(keyfile_item, setting)
                    self.items[keyfile_item].changed = True
                elif (setting == "comment"):
                    self.items[keyfile_item].comment = self.keyfile_items.get(keyfile_item, setting)
                    self.items[keyfile_item].changed = True
                elif (setting == "icon"):
                    self.items[keyfile_item].icon = self.keyfile_items.get(keyfile_item, setting)
                    self.items[keyfile_item].changed = True
                elif (setting == "activate"):
                    self.items[keyfile_item].activate = self.keyfile_items.getboolean(keyfile_item, setting)
                    self.items[keyfile_item].changed = True

    def list_all_applications_from_dirs(self):
        """ List all applications from applications directories"""
        logging.info("list_all_applications_from_dirs: enter function")
        return_list = []
        for path in self.applications_path:
            try:
                list_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
                for application_file in list_files:
                    app_path = os.path.join(path,application_file)
                    keyfile = None
                    if (os.path.splitext(app_path)[1] == ".desktop"):
                        keyfile = self.util.load_object("xdg",app_path)
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
        logging.info("Base.load_all_applications: enter function")
        list_app = self.list_all_applications_from_dirs()
        logging.debug("load_all_applications: %s" % list_app)
        for i in list_app:
            item = Item(self.categories_triaged)
            item.load_application_from_path(i)
            if (item.check == True):
                self.items[item.path] = item

    def list_all_modules_from_dirs(self):
        logging.info("Base.list_all_modules_from_dirs: enter function")
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
                            keyfile = self.util.load_object("xdg",file_path)
                            return_list.append(file_path)
            else:
                logging.info("list_all_modules_from_dirs: %s doesn't exist in path" % path)
        return return_list

    def load_all_modules (self):
        logging.info("Base.load_all_modules: enter function")
        list_modules = self.list_all_modules_from_dirs()
        logging.debug("load_all_modules: %s :" % list_modules)
        for m in list_modules:
            item = Item(self.categories_triaged)
            item.load_module_from_path(m, self.toolkit)
            if (item.check == True):
                self.items[item.path] = item

    # TODO Store list of running applications, to filter desktop application
    # Use self.generate_running_applications

    def apply_desktop_env_sort(self, i):
        logging.info("Base.apply_desktop_env_sort: enter function")
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
        logging.info("Base.apply_try_exec_test: enter function")
        if (self.items[i].type == "application"):
            if (self.items[i].try_exec != ""):
                if (os.path.exists(self.items[i].try_exec) == False):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Excecutable in TryExec doesn't exist"))

    def apply_no_exec_applications(self, i):
        logging.info("Base.apply_no_exec_applications: enter function")
        if (self.items[i].type == "application"):
            if (self.items[i].execute_command is None):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Excecutable path doesn't exist"))

    def apply_blacklist (self, i):
        logging.info("Base.apply_blacklist: enter function")
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
        logging.info("Base.apply_whitelist: enter function")
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
        logging.info("Base.apply_category_other: enter function")
        if (self.show_category_other == False):
            if (self.items[i].category_other == True):
                self.items[i].activate = False
                self.items[i].activate_original = False
                self.items[i].add_deactivate_reason(_("Category Other deactivated"))

    def apply_applications_modules_suport(self, i):
        logging.info("Base.apply_applications_modules_suport: enter function")
        if (self.items[i].type == "module"):
            self.items[i].activate = self.modules_support
            self.items[i].activate_original = self.modules_support
        elif (self.items[i].type == "application"):
            self.items[i].activate = self.applications_support
            self.items[i].activate_original = self.modules_support

    def apply_triage_module(self, i):
        logging.info("Base.apply_triage_module: enter function")
        if (self.items[i].type == "module"):
            if (self.modules_support == True):
                to_replace = self.items[i].module_replace_application
                for r in to_replace:
                    if (self.items[i].filename == r):
                        self.items[i].activate = False
                        self.items[i].activate_original = False
                        self.items[i].add_deactivate_reason(_("Replaced by an active module"))
            else:
                self.items[i].activate = False
                self.items[i].activate_original = False
                self.items[i].add_deactivate_reason(_("Module support deactivated"))

    def apply_module_toolkit(self, i):
        logging.info("Base.apply_module_toolkit: enter function")
        if (self.items[i].type == "module"):
            if (len(self.items[i].module_toolkits) > 0):
                if (self.toolkit not in self.items[i].module_toolkits):
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Module is not compatible with current toolkit"))

    def apply_module_experimental_support(self, i):
        logging.info("Base.apply_module_experimental_support: enter function")
        if (self.items[i].type == "module"):
            if (self.items[i].module_experimental == True):
                if (self.modules_experimental_support == True):
                    self.items[i].add_deactivate_reason(_("Experimental module, with support enabled"))
                else:
                    self.items[i].activate = False
                    self.items[i].activate_original = False
                    self.items[i].add_deactivate_reason(_("Experimental module, but the support is not enabled"))

    def apply_items_categories(self, i):
        logging.info("Base.apply_items_categories: enter fonction")
        self.items[i].category_array = self.categories_triaged
        self.items[i].define_category_from_list()

    def desktop_environments_generate(self):
        logging.info("Base.desktop_environments_generate: enter function")
        if self.desktop_environments_setting == ["Auto"]:
            new_list = []
            new_list.append(os.getenv("XDG_CURRENT_DESKTOP"))
            self.desktop_environments = new_list
        else:
            self.desktop_environments = self.desktop_environments_setting

    def categories_triaged_generate(self):
        logging.info("Base.categories_triaged_generate: enter function")
        for key in self.categories_keys.keys():
            for item in self.categories_keys[key]:
                if (len(item) > 1):
                    self.categories_triaged[item] = key
                else:
                    to_add = self.categories_keys[key]
                    self.categories_triaged[to_add] = key
                    break

    def save_settings(self):
        logging.info("Base.save_settings: enter function")
        self.keyfile_settings = self.runtime.support["lx_control_center_setting"][3]
        # Configuration
        self.util.set_setting("keyfile", self.keyfile_settings, "Configuration","desktop_categories", self.keyword_categories_settings_list, self.keyword_categories_settings_list_default,"list", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "Configuration","desktop_environments", self.desktop_environments_setting, self.desktop_environments_setting_default, "list", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "Configuration", "version_config", self.version_config, self.version_config_default, "float", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "Configuration", "categories_fixed", self.categories_fixed, self.categories_fixed_default, "boolean", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "Configuration", "blacklist", self.blacklist, self.blacklist_default, "list", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "Configuration", "whitelist", self.whitelist, self.whitelist_default, "list", self.trigger_save_settings_file)

        # Categories
        if (self.categories_fixed == False):
            if (self.categories_keys != self.categories_keys_default):
                for category in self.categories_keys:
                    self.util.set_setting("keyfile", self.keyfile_settings, "Categories",category, self.categories_keys[category], None, "list", self.trigger_save_settings_file)

        # Path
        self.util.set_setting("keyfile", self.keyfile_settings, "Path","applications_path", self.applications_path, self.applications_path_default, "list", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "Path","modules_path", self.modules_path, self.modules_path_default, "list", self.trigger_save_settings_file)


        # UI
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "window_size_w", self.window_size_w, self.window_size_w_default, "int", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "window_size_h", self.window_size_h, self.window_size_h_default, "int", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "window_icon", self.window_icon, self.window_icon_default, "generic", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "window_title", self.window_title, self.window_title_default, "generic", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "icon_view_columns", self.icon_view_columns, self.icon_view_columns_default, "int", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "icon_not_theme_allow", self.icon_not_theme_allow, self.icon_not_theme_allow_default, "boolean", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "icon_force_size", self.icon_force_size, self.icon_force_size_default, "boolean", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "icon_fallback", self.icon_fallback, self.icon_fallback_default, "generic", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "view_mode", self.view_mode, self.view_mode_default, "generic", self.trigger_save_settings_file)
        self.util.set_setting("keyfile", self.keyfile_settings, "UI", "view_visual_effects", self.view_visual_effects, self.view_visual_effects_default, "boolean", self.trigger_save_settings_file)

        if (self.trigger_save_settings_file == True):
            self.util.save_object(self.keyfile_settings, os.path.join("lx-control-center", "settings.conf"))
            self.trigger_save_settings_file = False

        # items.conf
        if (self.keyfile_items == None):
            self.keyfile_items = self.util.load_object("ini", os.path.join("lx-control-center","items.conf"))
        logging.debug("save_settings: loading %s as a keyfile_items" % os.path.join("lx-control-center","items.conf"))

        for i in self.items:
            if (self.items[i].changed == True):
                self.util.set_setting("keyfile", self.keyfile_items, self.items[i].path, "name", self.items[i].name, self.items[i].name_original, "generic", self.trigger_save_settings_file)
                self.util.set_setting("keyfile", self.keyfile_items, self.items[i].path, "icon", self.items[i].icon, self.items[i].icon_original, "generic", self.trigger_save_settings_file)
                self.util.set_setting("keyfile", self.keyfile_items, self.items[i].path, "comment", self.items[i].comment, self.items[i].comment_original, "generic", self.trigger_save_settings_file)
                self.util.set_setting("keyfile", self.keyfile_items, self.items[i].path, "activate", self.items[i].activate, self.items[i].activate_original, "boolean", self.trigger_save_settings_file)

        if (self.trigger_save_settings_file == True):
            self.util.save_object(self.keyfile_settings, os.path.join("lx-control-center", "items.conf"))
            self.trigger_save_settings_file = False
            
    def module_active(self,item):
        logging.info("Base.module_active: enter function")
        self.module_activated = item

    # UI functions
    def generate_view(self):
        logging.info("Base.generate_view: enter function")
        self.items_visible_generate()
        self.items_visible_by_categories_generate()
        self.items_by_categories_generate()
        self.icon_view_columns_generate()

    def build_generic_icon_view(self, type_view):
        """ Re-implement me on a toolkit backend
        """
        pass

    def build_icon_view(self):
        logging.info("Base.build_icon_view: enter function")
        self.clean_main_view()
        # Generate the view again, to take the modifications of edit_view
        self.generate_view()
        self.build_generic_icon_view("visible")

    def build_edit_view(self):
        logging.info("Base.build_edit_view: enter function")
        self.clean_main_view()
        # Update items for search filter
        self.items_by_categories_generate()
        self.build_generic_icon_view("all")

    def filter_item_by_search(self, item):
        logging.info("Base.filter_item_by_search: enter function")
        match = False
        if (self.search_string == None):
            logging.debug("Base.filter_item_by_search, no search")
            match = True
        elif (self.search_string in item.name.lower()):
            logging.debug("Base.filter_item_by_search, search %s in name: match for %s with %s" % (self.search_string, item.path, item.name))
            match = True
        elif (self.search_string in item.comment.lower()):
            logging.debug("Base.filter_item_by_search, search %s in comment: match for %s with %s" % (self.search_string, item.path, item.comment))
            match = True
        else:
            math = False
        return match

    def items_visible_generate(self):
        logging.info("Base.items_visible_generate: enter function")
        self.items_visible = []
        for i in self.items:
            if (self.items[i].activate == True):
                if (self.filter_item_by_search(self.items[i]) == True):
                    logging.debug("items_visible_generate, append %s in items_visible_generate" % self.items[i].path)
                    self.items_visible.append(self.items[i])

    def items_visible_by_categories_generate(self):
        logging.info("Base.items_visible_by_categories_generate: enter function")
        self.items_visible_by_categories = {}
        non_order_dict = {}
        for i in self.items_visible:
            if (i.category not in non_order_dict):
                empty_list = []
                non_order_dict[i.category] = empty_list

            non_order_dict[i.category].append(i)

        self.items_visible_by_categories = collections.OrderedDict(sorted(non_order_dict.items()))

    def items_by_categories_generate(self):
        # TODO Factorise with items_visble_by_categories_generate
        logging.info("Base.items_by_categories_generate: enter function")
        self.items_by_categories = {}
        non_order_dict = {}
        for i in self.items:
            if (self.filter_item_by_search(self.items[i]) == True):
                if (self.items[i].category not in non_order_dict):
                    empty_list = []
                    non_order_dict[self.items[i].category] = empty_list
                non_order_dict[self.items[i].category].append(self.items[i])
                self.items_by_categories = collections.OrderedDict(sorted(non_order_dict.items()))

    #TODO Sorting items inside categories

    def icon_view_columns_generate(self):
        logging.info("Base.icon_view_columns_generate: enter function")
        # TODO use iconview item size (or any way to have the size of the item instead of the size of the icon)
        logging.debug("icon_view_columns_generate: self.window_size_w : %s" % self.window_size_w)
        logging.debug("icon_view_columns_generate: self.icon_view_icons_size : %s" % self.icon_view_icons_size)
        blank_pixels = 10
        max_nbr_col_win = 0
        max_nbr_col_categories = 0
        max_nbr_col_win = self.window_size_w // ((4 * self.icon_view_icons_size) + (2 * blank_pixels))
        logging.debug("icon_view_columns_generate: max_nbr_col_win : %s" % max_nbr_col_win)
        if (self.items_visible == []):
            max_nbr_col_categories = 0
            max_categories = 0
            logging.warning("icon_view_columns_generate: no icons visible")
        else:
            max_categories = max(self.items_visible_by_categories.keys(), key=(lambda k: len(self.items_visible_by_categories[k])))
            max_nbr_col_categories = len(self.items_visible_by_categories[max_categories])
        logging.debug("icon_view_columns_generate: max_nbr_col_categories : %s" % max_nbr_col_categories)

        if (max_nbr_col_categories >= max_nbr_col_win):
            self.icon_view_columns = max_nbr_col_win
        else:
            self.icon_view_columns = max_nbr_col_categories

    def on_icons_mode_menu_click(self, widget, data=None):
        logging.info("Base.on_icons_mode_menu_click: Clicked")
        self.mode = "main-UI"
        self.load_settings()
        self.triage_items()
        self.generate_view()
        self.draw_ui()

    def on_edit_mode_menu_click(self, widget, data=None):
        logging.info("Base.on_edit_mode_menu_click: Clicked")
        self.mode = "edit-UI"
        self.load_settings()
        self.triage_items()
        self.generate_view()
        self.draw_ui()

    def on_pref_mode_menu_click(self, widget, data=None):
        logging.info("Base.on_pref_mode_menu_click: Clicked")
        self.mode = "pref-UI"
        self.load_settings()
        self.triage_items()
        self.generate_view()
        self.draw_ui()

    def build_module_view(self):
        logging.info("Base.build_module_view: enter function")
        self.clean_main_view()
        module_class = self.module_activated.module_spec.LXCC_Module(self.toolkit)
        self.content_ui_vbox.add(module_class.main_box)

    def on_item_activated_common(self, path):
        logging.info("Base.on_item_activated_common: enter function")
        item_to_launch = self.items[path]
        if (self.items[path].type == "module"):
            self.mode = "module-UI"
            self.module_active(self.items[path])
            self.items[path].launch()
            self.draw_ui()
        else:
            self.items[path].launch()

    def draw_ui(self):
        logging.info("Base.draw_ui: enter function")
        pass

    def on_resize_common(self, w, h):
        logging.info("Base.on_resize_common: enter function")
        if (self.mode == "main-UI"):
            self.on_resize_function(w, h)
        elif (self.mode == "edit-UI"):
            self.on_resize_function(w, h)

    def on_resize_function(self, w, h):
        logging.info("Base.on_resize: resize activated")
        self.window_size_w = w
        self.window_size_h = h
        tmp_icons_col = self.icon_view_columns
        self.icon_view_columns_generate()
        if (self.icon_view_columns != tmp_icons_col):
            self.draw_ui()

    def set_standalone(self):
        logging.info("Base.set_standalone: enter function")
        logging.debug("set_standalone: value of standalone_module: %s" % self.standalone_module)
        if (self.standalone_module != None):
            self.mode = "module-UI"
            for i in self.items:
                if (self.items[i].filename == self.standalone_module + '.desktop'):
                    if (self.toolkit in self.items[i].module_toolkits):
                        self.on_item_activated_common(i)
                        return True
                    else:
                        logging.error("Module %s is not compatible with current toolkit %s." % (self.standalone_module, self.toolkit))
                        return False
        else:
            return True

    def print_debug(self):
        """ Prints variables and other useful items for debug purpose"""
        logging.debug("Printing variables")
        logging.debug("self.keyword_categories_settings_list : %s" % self.keyword_categories_settings_list)
        logging.debug("self.applications_path : %s" % self.applications_path)
        logging.debug("self.modules_path : %s" % self.modules_path)
        logging.debug("self.applications_support: %s" % self.applications_support)
        logging.debug("self.modules_support: %s" % self.modules_support)
        logging.debug("self.modules_experimental_support: %s" % self.modules_experimental_support)
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
            logging.debug("Item deactivation reasons : %s" % self.items[i].deactivate_reasons)
            logging.debug("Item module_replace_application : %s" % self.items[i].module_replace_application)
            logging.debug("Item module_toolkits : %s" % self.items[i].module_toolkits)
            logging.debug("Item module_experimental : %s" % self.items[i].module_experimental)
            logging.debug("=================")

