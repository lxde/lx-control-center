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

import logging
import xdg.BaseDirectory
import xdg.DesktopEntry
import xdg.IniFile
import xdg.Locale
import os.path
import psutil
try:
    import configparser as configparser
except:
    import ConfigParser as configparser

class Utils(object):
    def load_xdgfile(self,path):
        xdgfile = None
        try:
            xdgfile = xdg.DesktopEntry.DesktopEntry(path)
        except:
            logging.error("load_xdgfile: error, %s is not a desktop file" % path)
        return xdgfile

    def load_inifile(self,path):
        inifile = None
        inifile = configparser.ConfigParser()
        inifile.optionxform = str
        try:
            inifile.read_file(open(path))
        except:
            try:
                inifile.readfp(open(path))
            except:
                logging.error("load_inifile: error, when loading %s as a ini file" % path)
        return inifile

    def load_setting(self, keyfile, group, key, default_value, type_to_get):
        return_value = default_value
        if (keyfile.has_section(group)):
            if (keyfile.has_option(group, key)):
                if(type_to_get == "list"):
                    return_value = keyfile.get(group,key).split(";")
                    return_value.pop()

                elif (type_to_get == "float"):
                    return_value = keyfile.getfloat(group,key)

                elif (type_to_get == "int"):
                    return_value = keyfile.getint(group,key)

                elif (type_to_get == "boolean"):
                    return_value = keyfile.getboolean(group,key)

                elif (type_to_get == "string"):
                    new_key = key
                    for lang in xdg.Locale.langs:
                        langkey = "%s[%s]" % (key, lang)
                        if (keyfile.has_option(group, langkey)):
                           new_key =  langkey
                    return_value = keyfile.get(group, new_key)
                else:
                    return_value = keyfile.get(group,key)

        return return_value

    def load_configuration_file (self, directory, name, local = False):
        """ Set configuration path to self.settings_path"""

        config_dirs = xdg.BaseDirectory.xdg_config_dirs

        return_path = None

        for path in config_dirs:
            test_path = os.path.join(path, directory, name)
            if(os.path.exists(test_path)):
                return_path = test_path
                break

        if (local == True):
            if (return_path == None):
                return_path = os.path.join(os.getcwd(), "data",name)

        logging.debug("load_configuration_file : return_path = %s" % return_path)

        return return_path

    def generate_running_applications(self):
        return_list = []
        procs = psutil.process_iter()
        for proc in procs:
            return_list.append(proc.name())
        return return_list

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

    def save_file(self, keyfile, settings_type, module = None):
        if (module == None):
            dir_path = os.path.join(os.path.expanduser('~'), ".config","lx-control-center")
        else:
            dir_path = os.path.join(os.path.expanduser('~'), ".config","lx-control-center", "modules", module)
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
            elif (key == "modules_experimental_support"):
                self.modules_experimental_support = variable
            elif (key == "show_category_other"):
                self.show_category_other = variable
            else:
                logging.warning("set_setting: %s - %s not implemented" % (group, key))
        else:
            logging.warning("set_setting: %s - %s not implemented" % (group, key))
