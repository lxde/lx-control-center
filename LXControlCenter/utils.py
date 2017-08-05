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
    # Public API
    #
    # Utilities
    # generate_running_applications = generate a list of running applications
    #
    # Settings access
    # load_object = load setting object (file, or gsetting, or dbus ...)
    # save_object = save setting object (file, or gsetting, or dbus ...)
    # get_setting = get setting from object
    # set_setting = set setting from object

    def generate_running_applications(self):
        """
            return: A list of running applications
        """
        logging.info("Utils.generate_running_applications: enter function")
        return_list = []
        procs = psutil.process_iter()
        for proc in procs:
            return_list.append(proc.name())
        return return_list

    def load_object (self, object_type, relative_path):
        """ Load object with setting.
            object_type: ini (inifile), xdg (xdg ini file)
            relative_path: relative path to the object (exemple = os.path.join("lx-control-center","settings.conf")

            return: Return the object (keyfile)
        """
        logging.info("Utils.load_object: enter function")
        return_value = None
        if (relative_path[0] == "/"):
            path = relative_path
        else:
            path = self.__get_path(relative_path)
        if (object_type == "ini" or object_type == "keyfile"):
            return_value = configparser.ConfigParser()
            return_value.optionxform = str
            try:
                return_value.read_file(open(path))
            except:
                try:
                    return_value.readfp(open(path))
                except:
                    logging.error("Utils.load_object(ini): error, when loading %s as a ini file" % path)
        elif (object_type == "xdg"):
            try:
                return_value = xdg.DesktopEntry.DesktopEntry(path)
            except:
                logging.error("load_xdgfile: error, %s is not a desktop file" % path)
        else:
            logging.error("Utils.load_object: object type %s not supported" % object_type)

        return return_value

    def save_object(self, object_type, object_to_save, relative_path = None):
        """ Save object with setting.
            object_type: file (ini or xdg)
            relative_path: relative path to the object (exemple = os.path.join("lx-control-center","settings.conf")
        """
        logging.info("Utils.save_object: enter function")
        if (object_type == "file" or object_type == "keyfile"):
            path = self.__get_path(relative_path)
            dir_path = os.path.dirname(path)
            if (os.path.exists(dir_path) == False):
                logging.debug("save_file: Directory doesn't exist => create it")
                os.makedirs(dir_path)

            if (os.path.exists(path) == False):
                logging.debug("save_file: File doesn't exist => create it")
                file_to_create = open(path,'a')
                file_to_create.close()

            logging.debug("save_file: Save file on %s" % path)
            file_to_save = open(path,'w')
            object_to_save.write(file_to_save)
            file_to_save.close()

    def get_setting(self, object_type, object_to_get, group, key, default_value, type_to_get):
        """ Get setting from a setting object.
            object_type: Type of setting (keyfile, gsetting)
            object_to_get: keyfile object, or None
            group: First setting parameter
            key: Second setting parameter
            default_value: Value to return if nothing is find, or None (Not apply on gsetting)
            type_to_get: Type of the setting (string, int, list, float, boolean)

            return: Return the object
        """
        #TODO Dbus Backend
        #TODO XML Backend
        #https://stackoverflow.com/questions/1629687/alter-xml-while-preserving-layout
        logging.info("Utils.get_setting: enter function")
        return_value = default_value
        # Keyfile
        if (object_type == "keyfile"):
            keyfile = object_to_get
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
        elif (object_type == "gsetting"):
            gsettings = Gio.Settings.new(group)
            if (type_to_set == "string"):
                return_value = gsettings.get_string(key)
            else:
                logging.warning("Utils.get_setting: GSetting not supported for type %s." % type_to_set)
        else:
            logging.warning("Utils.get_setting: type %s is not supported." % object_type)

        return return_value

    def set_setting(self, object_type, object_to_get, group, key, variable, default, type_to_set, trigger = False):
        """ Set a setting from a setting object.
            object_type: keyfile (ini), gsetting
            object_to_get: keyfile object, or None
            group: First setting parameter
            key: Second setting parameter
            variable: Value to set
            default_value: Value to return if nothing is find, or None
            type_to_get: Type of the setting (string, int, list, float, boolean)
            trigger: (Optionnal) pass a variable to trigger a file save trigger

            return True is the object need to be saved
        """
        #TODO Dbus Backend
        #TODO XML Backend
        #TODO binary Backend
        logging.info("Utils.set_setting: enter function")
        logging.debug("Utils.set_setting: group, key and variable => %s, %s, %s" %(group, key, variable))
        trigger_save_settings_file = False
        # Keyfile
        if (object_type == "keyfile"):
            keyfile = object_to_get
            logging.debug("set_setting: variable: %s" % variable)
            logging.debug("set_setting: default: %s" % default)
            if (variable == default):
                logging.debug("set_setting: variable == default, checking for existing key")
                if(keyfile.has_option(group, key)):
                    logging.debug("set_setting: variable == default, existing key, removing")
                    keyfile.remove_option(group, key)
                    trigger_save_settings_file = True
                #TODO Remove section if it's empty
            else:
                if (keyfile.has_section(group) == False):
                    keyfile.add_section(group)
                    trigger_save_settings_file = True

                if (type_to_set == "float"):
                    if (keyfile.has_option(group, key) == False):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                    elif (keyfile.getfloat(group, key) != variable):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                elif(type_to_set == "int" or type_to_set == "integer"):
                    if (keyfile.has_option(group, key) == False):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                    elif (keyfile.getint(group, key) != variable):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                elif(type_to_set == "boolean" or type_to_set == "bool"):
                    if (keyfile.has_option(group, key) == False):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                    elif (keyfile.getboolean(group, key) != variable):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                elif(type_to_set == "list"):
                    if (keyfile.has_option(group, key) == False):
                        list_to_save = ';'.join(variable) + ";"
                        keyfile.set(group, key, list_to_save)
                        trigger_save_settings_file = True

                    elif (keyfile.get(group, key) != variable):
                        list_to_save = ';'.join(variable) + ";"
                        keyfile.set(group, key, list_to_save)
                        trigger_save_settings_file = True
                else:
                    if (keyfile.has_option(group, key) == False):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True

                    elif (keyfile.get(group, key) != variable):
                        keyfile.set(group, key, str(variable))
                        trigger_save_settings_file = True
        # GSetting
        elif (object_type == "gsetting"):
            gsettings = Gio.Settings.new(group)
            if (gsettings.get_default_value(key) == variable):
                gsettings.reset(key)
            elif (type_to_set == "string"):
                if (gsettings.get_string(key) != variable):
                    gsettings.set_string(key, value)
                    gsettings.apply()
            else:
                logging.warning("Utils.set_setting: GSetting not supported for type %s." % type_to_set)
        else:
            logging.warning("Utils.set_setting: type %s is not supported." % object_type)

        if (trigger == False):
            trigger = trigger_save_settings_file
        return trigger_save_settings_file

    def __get_path (self, relative_path):
        """ Find the current configuration file, using XDG standart
            path: relative path to the object (exemple = os.path.join("lx-control-center","settings.conf")

            return the absolute path
        """
        logging.info("Utils.__get_path : enter function")
        config_dirs = xdg.BaseDirectory.xdg_config_dirs
        return_path = None

        for path in config_dirs:
            test_path = os.path.join(path, relative_path)
            if(os.path.exists(test_path)):
                return_path = test_path
                break

        if (return_path == None):
            test_path = os.path.join(os.getcwd(), "data", os.path.basename(relative_path))
            if (os.path.exists(test_path)):
                return_path = test_path

        if (return_path == None):
            test_path = os.path.join(os.getcwd(), relative_path)
            if (os.path.exists(test_path)):
                return_path = test_path

        if (return_path == None):
            logging.warning("Utils.__get_path : Can't find an existing file for relative path %s" % return_path)

        logging.debug("Utils.__get_path : return_path = %s" % return_path)
        return return_path
