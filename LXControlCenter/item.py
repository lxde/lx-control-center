#!/usr/bin/env python3
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
import sys
import logging

from LXControlCenter.utils import Utils

import gettext
_ = gettext.gettext

class Item():
    def __init__(self, categories_array):

        self.util = Utils()

        # Item structure
        self.path = ""
        self.filename = ""
        self.version_config = 0.1
        self.name = ""
        self.name_original = ""
        self.comment = ""
        self.comment_original = ""
        self.category = ""
        self.categories_list = []
        self.categories_array = categories_array
        self.category_other = False
        self.icon = ""
        # Icon type : themed, fix or fallback
        self.icon_type = ""
        self.icon_original = ""
        self.try_exec = ""
        self.only_show_in = []
        self.not_show_in = []
        self.activate = True
        self.activate_original = True
        self.deactivate_reasons = []
        self.changed = False
        self.check = True

        # module or application
        self.type = ""

        # application specific
        self.execute_command =""
        
        # module specific
        self.module_replace_application = []
        self.module_depends = []
        self.module_version = 0.0
        self.module_api_version = 0.0
        self.module_spec = None
        self.module_toolkit = None
        self.module_experimental = False

    def load_common_app_module_from_path(self,path,keyfile):
        self.path = path
        self.filename = os.path.basename(path)

        self.name = keyfile.getName()
        self.comment = keyfile.getComment()
        self.categories_list = keyfile.getCategories()
        self.icon = keyfile.getIcon()
        self.only_show_in = keyfile.getOnlyShowIn()
        self.not_show_in = keyfile.getNotShowIn()
        self.execute_command = keyfile.getExec()
        self.try_exec = keyfile.getTryExec()

        self.name_original = self.name
        self.comment_original = self.comment
        self.icon_original = self.icon

        self.category = None
        self.version_config = 0.1
        # Check if there are the minimum informations
        self.check_common()

        self.define_category_from_list()
        self.define_icon_type()

    def load_application_from_path(self, path):
        keyfile = self.util.load_object("xdg",path)
        self.load_common_app_module_from_path(path, keyfile)
        self.type = "application"


    def load_module_from_path(self, path):
        keyfile = self.util.load_object("xdg",path)
        self.load_common_app_module_from_path(path, keyfile)
        self.type = "module"
        self.module_replace_application = keyfile.get("X-LX-Control-Center-Application-Replaces", group="Desktop Entry", type="string", list=True)
        self.module_depends = keyfile.get("X-LX-Control-Center-Depends", group="Desktop Entry", type="string", list=True)
        self.module_version = keyfile.get("X-LX-Control-Center-Version", group="Desktop Entry", type="numeric")
        self.module_api_version = keyfile.get("X-LX-Control-Center-API-Version", group="Desktop Entry", type="numeric")
        self.module_toolkit = keyfile.get("X-LX-Control-Center-Toolkit", group="Desktop Entry", type="string")
        self.module_experimental = keyfile.get("X-LX-Control-Center-Experimental", group="Desktop Entry", type="boolean")
        self.check_module()

    def define_category_from_list(self):
        logging.debug("define_category_from_list: enter function with categories_list for %s = %s" % (self.path, self.categories_list))
        logging.debug("define_category_from_list: enter function with categories_array for %s = %s" % (self.path, self.categories_array))
        tmp_dict = {}
        keys = self.categories_array.keys()
        for item in self.categories_list:
            if (item in keys):
                if (item in tmp_dict.keys()):
                    tmp_dict[item] = tmp_dict[item] + 1
                else:
                    tmp_dict[item] = 1
        if (len(tmp_dict) == 0):
            self.category = _("Other")
            self.category_other = True
        else:
            max_category = max(tmp_dict.keys(), key=(lambda k: tmp_dict[k]))
            self.category = self.categories_array[max_category]

    def define_icon_type(self):
        if (len(self.icon) > 0):
            if (self.icon[0] == "/"):
                self.icon_type = "fix"
            else:
                self.icon_type = "themed"
        else:
            self.icon_type = "fallback"

    def check_common(self):
        if (self.name == None):
            self.check = False
        if (self.categories_list == None):
            self.check = False
        if (self.execute_command == None):
            self.check = False

    def check_module(self):
        if (self.module_api_version <= 0.0):
            self.check = False
            logging.warning("check_module: Module name %s, on %s is outdated with current version of lx-control-center. Please contact the module author" % (self.name, self.path))
        if (self.module_version == 0.0):
            self.check = False

    def add_deactivate_reason(self, reason):
        if (reason not in self.deactivate_reasons):
            self.deactivate_reasons.append(reason)
            
    def launch(self):
        logging.info("launch: trying execute : %s" % self.execute_command)
        if (self.type == "application"):
            self.util.launch_command(self.execute_command)

        elif (self.type == "module"):
            python_version = sys.version_info
            module_path = os.path.join(os.path.dirname(self.path),self.execute_command)
            if (python_version[0] == 2):
                import imp
                self.module_spec = imp.load_source('module.name', module_path)
            elif (python_version[0] == 3):
                if(python_version[1] < 3.5):
                    from importlib.machinery import SourceFileLoader
                    self.module_spec = SourceFileLoader("module.name", module_path).load_module()
                else:
                    import importlib.util
                    logging.debug("launch: trying to import : %s" % module_path)
                    spec = importlib.util.spec_from_file_location("module.name", module_path)
                    self.module_spec = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(self.module_spec)
