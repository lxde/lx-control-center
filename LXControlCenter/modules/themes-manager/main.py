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

from LXControlCenter.utils import Utils
from LXControlCenter.runtime import Runtime
from LXControlCenter.setting import *

# For logging, it can be removed if you don't use logging facility
import os.path
import logging

class LXCC_Module():
    def __init__(self, toolkit):
        logging.debug("LXCC_Module.__init__: Init module %s" % os.path.abspath(__file__))

        self.toolkit = toolkit

        self.util = Utils()
        self.runtime = Runtime()
        
        # Module Settings
        self.module_name = "themes-manager"
        self.module_keyfile = self.util.load_object("keyfile", os.path.join("lx-control-center", "modules", self.module_name, "module_settings.conf"))
        self.setting_current_theme = None
        
        # System Settings
        self.icon_theme_setting = IconThemeSetting(self.runtime)
        self.gtk_theme_setting = GtkThemeSetting(self.runtime)
        self.cursor_theme_setting = CursorThemeSetting(self.runtime)
        self.cursor_size_setting = CursorSizeSetting(self.runtime)
        self.openbox_theme_setting = OpenboxThemeSetting(self.runtime)

        # Variables / Data-structures
        # List of index.theme path, of themes found on the system
        self.themes_index_files = []
        # Themes usables by the module
        # Format self.themes_db[index_file] = Theme()
        self.themes_db = {}
        # Themes sorted by name
        # Format self.themes_db_names[theme.name] = index_file
        self.themes_db_names = {}

        #List Icons theme (to check support)
        self.icons_index_files = []
        self.icons_db_names = {}

        #List Cursor theme (to check support)
        self.cursors_index_files = []
        self.icons_db_names = {}

        self.init()

    def init(self):
        global Gtk
        if (self.toolkit == "GTK3"):
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            self.icon_theme = Gtk.IconTheme().get_default()
            self.icon_lookup = Gtk.IconLookupFlags.FORCE_SIZE
        else:
            import pygtk
            pygtk.require('2.0')
            import gtk as Gtk
            self.icon_theme = Gtk.icon_theme_get_default()
            self.icon_lookup = Gtk.ICON_LOOKUP_USE_BUILTIN
        # LXCC will attach self.main_box to the main window
        self.main_box = Gtk.VBox()
        self.run()
        
    def run (self):
        # Load configuration settings
        self.load_settings()
        # Read .desktop themes files, and populate self.themes_index_files
        self.read_themes()
        # Populate the theme database self.themes_db = {}
        self.generate_theme_db()
        
        self.icons_db_names = self.generate_icons_db(self.icons_index_files)
        self.icons_db_names = self.generate_icons_db(self.cursors_index_files)

        self.draw()

        #Debug mode
        #self.debug()


    def load_settings(self):
        self.setting_current_theme = self.util.get_setting("keyfile", self.module_keyfile, "Configuration", "current_theme", None, "string")
    
    def read_themes(self):
        self.themes_index_files = self.read_index_files("themes", "index.theme")
        self.icons_index_files = self.read_index_files("icons", "index.theme")
        self.cursors_index_files = self.read_index_files("icons", "cursor.theme")

    def read_index_files(self, directory, index_file):
        """ Generate a list of index.theme files
            directory: the directory to search (it will be in /usr/share/the_directory and /home/the_user/.the_directory
            index_file: the name of the index.theme file to search (cursor.theme for cursor)
            
            return: A list of index.theme path
        """
        home_directory = '.' + directory
        system_directory = os.path.join('/', 'usr', 'share', directory)
        themes_path_list = [os.path.join(os.path.expanduser('~'),home_directory), system_directory]
        themes_list = []
        for directory_list in themes_path_list:
            for directory in os.listdir(directory_list):
                path = os.path.join(directory_list, directory)
                try:
                    list_files = [f for f in os.listdir(os.path.join(directory, path)) if os.path.isfile(os.path.join(path, f))]
                    for theme_file in list_files:
                        if (theme_file == index_file):
                            index_path = os.path.join(path, theme_file)
                            themes_list.append(index_path)
                            
                except OSError:
                    logging.info("read_themes: %s not found path" % path)
        return themes_list

    def generate_icons_db(self, current_list):
        return_dict = {}
        for index_file in current_list:
            keyfile = self.util.load_object("keyfile", index_file)
            if (keyfile.has_section("Icon Theme")):
                name = self.util.get_setting("keyfile", keyfile, "Icon Theme", "Name", None, "string-no-locale")
                return_dict[name] = index_file
        return return_dict
        
    def generate_theme_db(self):
        for index_file in self.themes_index_files:
            keyfile = self.util.load_object("keyfile", index_file)
            if (keyfile.has_section("X-GNOME-Metatheme")):
                theme = Theme()
                theme.read_index_file(index_file)
                theme.read_directory()
                if (theme.name in self.themes_db_names.keys()):
                    theme.name = theme.name + " (" + theme.directory_name + ")"
                self.themes_db[index_file] = theme
                self.themes_db_names[theme.name] = index_file

        # Sort self.themes_db_names
        items = self.themes_db_names.items()
        items.sort() 
        self.themes_db_names = [value for key, value in items]

    def apply_settings(self):
        theme = self.themes_db[self.setting_current_theme]
        if (theme.support["icon_theme"][0] is not None):
            self.icon_theme_setting.set(theme.support["icon_theme"][0])
            logging.debug("Apply setting icon_theme with value %s: "% theme.support["icon_theme"][0])
        if (theme.support["gtk_theme"][0] is not None):
            self.gtk_theme_setting.set(theme.support["gtk_theme"][0])
            logging.debug("Apply setting gtk_theme with value %s: "% theme.support["gtk_theme"][0])
        if (theme.support["cursor_theme"][0] is not None):
            self.cursor_theme_setting.set(theme.support["cursor_theme"][0])
            logging.debug("Apply setting cursor_theme with value %s: "% theme.support["cursor_theme"][0])
        if (theme.support["cursor_size"][0] is not None):
            self.cursor_size_setting.set(theme.support["cursor_size"][0])
            logging.debug("Apply setting cursor_size with value %s: "% theme.support["cursor_size"][0])
        if (theme.support["openbox_settings"][0] is not None):
            self.openbox_theme_setting.set(theme.support["openbox_settings"][0])
            logging.debug("Apply setting openbox theme with value %s: " % theme.support["openbox_settings"][0])

    def generate_row_col(self, key, entry_list):
        col = entry_list[0]
        row = entry_list[1]
        row_col1 = entry_list[2]
        row_col2 = entry_list[3]
        if (key == "directory_structure"):
            col = 1
            row_col1 = row_col1 + 1
            row = row_col1
        else:
            col = 4
            row_col2 = row_col2 + 1
            row = row_col2
        return [col, row, row_col1, row_col2]

    def check_install(self, support):
        return_value = True
        if (support == "icon_theme"):
            if (theme.support["icon_theme"][0] not in self.icons_db_names.items()):
                return_value = False
        elif (support == "cursor_theme"):
            if (theme.support["cursor_theme"][0] not in self.cursors_db_names.items()):
                return_value = False
        return return_value

    def gtk_generate_theme_box(self, theme):
        # Generate a box of theme
        # 1 Frame (frame)
        #   ==> 1 VBox (For box + Expander)
        #       ==> 1 HBox (hbox)
        #           ==> 1 image / background 
        #           ==> 1 Grid 5x3
        #               ==> gtk-ok icon + support
        #               ==> 1 switch button to apply
        #       ==> 1 Expander
        
        frame = Gtk.Frame(label=theme.name)
        self.main_box.add(frame)

        vbox = Gtk.VBox()
        frame.add(vbox)

        hbox = Gtk.HBox()
        vbox.add(hbox)

        image = self.gtk_generate_preview_image(theme)
        hbox.pack_start(image, False, False, 0)

        grid = self.gtk_generate_grid()
        hbox.pack_start(grid, False, False, 0)

        # Row / Col for support grid
        row_max = 7
        # support_grid = [col, row, row on col 1, row on col 2]
        support_grid = [1, 0, 0, 0]
        
        expander = Gtk.Expander()
        vbox.add(expander)
        expander.set_label(_('Details'))
        grid_ex = self.gtk_generate_grid()
        expander.add(grid_ex)
        expander_grid = [1, 0, 0, 0]

        expander_name_label = Gtk.Label(_("Name: %s") % theme.name, xalign=0)
        expander_name_label.set_size_request(230, -1)
        expander_grid = self.generate_row_col("directory_structure", expander_grid)
        grid_ex.attach(expander_name_label,expander_grid[0],expander_grid[1],1,1)

        expander_location_label = Gtk.Label(_("Location: %s") % theme.index_file, xalign=0)
        expander_location_label.set_size_request(230, -1)
        expander_grid = self.generate_row_col("directory_structure", expander_grid)
        grid_ex.attach(expander_location_label,expander_grid[0],expander_grid[1],1,1)

        #TODO Make [...] when too much support
        for support in theme.support:
            # Is the theme support this setting ?
            if (theme.support[support][0] is not None):
                # If the support doesn't need any application to be apply
                # Or look for settings on running applications
                if (theme.support[support][5] is None or self.runtime.support[support][2] == True):
                    support_grid = self.generate_row_col(theme.support[support][1], support_grid)
                    label = Gtk.Label("%s" % theme.support[support][3], xalign=0)
                    label.set_size_request(230, -1)
                    label.set_justify(Gtk.Justification.LEFT)
                    if (self.icon_theme.has_icon("gtk-apply")):
                        pixbuf = self.icon_theme.load_icon("gtk-apply", 16, self.icon_lookup)
                        image = self.gtk_generate_image(pixbuf)
                        grid.attach(image,support_grid[0],support_grid[1],1,1)
                        grid.attach_next_to(label, image, Gtk.PositionType.RIGHT, 2, 1)
                    else:
                        grid.attach(label,support_grid[0],support_grid[1],2,1)
            is_install = True
            is_install = self.check_install(theme.support[support])
            expander_label_text = "%s: %s" % (theme.support[support][3], theme.support[support][0])
            if (is_install == False):
                expander_label_text = expander_label_text + _(" (but not currently installed)")
            expander_label = Gtk.Label(expander_label_text, xalign=0)
            expander_label.set_size_request(230, -1)
            expander_grid = self.generate_row_col(theme.support[support][1], expander_grid)
            grid_ex.attach(expander_label,expander_grid[0],expander_grid[1],1,1)

        switch_label = Gtk.Label(_("Enable"), xalign=0)
        switch_label.set_size_request(50, -1)
        switch_widget = Gtk.Switch()
        if (self.setting_current_theme == theme.index_file):
            switch_widget.set_active(True)
        else:
            switch_widget.set_active(False)
        switch_widget.connect("notify::active", self.on_switch_click, theme.index_file)
        grid.attach(switch_label,7,1,2,1)
        grid.attach_next_to(switch_widget, switch_label, Gtk.PositionType.RIGHT, 2, 1)     

    def on_switch_click(self, switch, gparam, index_file):
        logging.debug("Apply current theme to %s: "% index_file)
        self.setting_current_theme = index_file
        self.util.set_setting("keyfile", self.module_keyfile, "Configuration", "current_theme", self.setting_current_theme, None, "string")
        self.apply_settings()
        self.util.save_object("keyfile", self.module_keyfile, os.path.join("lx-control-center", "modules", self.module_name, "module_settings.conf"))
        self.draw()

    
    def gtk_generate_preview_image(self, theme):
        icon_theme = Gtk.IconTheme()
        icon_theme.set_custom_theme(theme.support["icon_theme"][0])
        icon_example = icon_theme.get_example_icon_name()

        try:
            pixbuf = icon_theme.load_icon(icon_example, 128, self.icon_lookup)
        except:
            try:
                pixbuf = icon_theme.load_icon("folder", 128, self.icon_lookup)
            except:
                try:
                    pixbuf = icon_theme.load_icon("computer", 128, self.icon_lookup)
                except:
                    pixbuf = self.icon_theme.load_icon("gtk-stop", 128, self.icon_lookup)

        image = self.gtk_generate_image(pixbuf)
        return image

    def gtk_generate_grid(self):
        if (self.toolkit == "GTK3"):
            grid = Gtk.Grid()
            grid.set_column_homogeneous(False)
            grid.set_row_homogeneous(False)
            grid.set_column_spacing(5)
            grid.set_row_spacing(5)
            grid.set_margin_left(30)
            grid.set_margin_right(30)
            grid.set_margin_top(10)
            grid.set_margin_bottom(10)
        else:
            grid = Gtk.Table()
            grid.set_homogeneous(False)
            grid.set_col_spacings(20)
            grid.set_row_spacings(20)
        return grid

    def gtk_generate_image(self, pixbuf):
        if (self.toolkit == "GTK3"):
            image = Gtk.Image.new_from_pixbuf(pixbuf)
            return image
        else:
            image = Gtk.Image()
            image.set_from_pixbuf(pixbuf)
        return image

    def draw(self):
        for children in self.main_box.get_children():
            self.main_box.remove(children)

        for theme in self.themes_db_names:
            self.gtk_generate_theme_box(self.themes_db[theme])

        self.main_box.show_all()
    
    def debug(self):
        for i in self.themes_db:
            self.themes_db[i].debug()

                #list_options = []
        #for i in self.themes_index_files_gnome:
        #    keyfile = self.load_inifile(i)
        #    for options in keyfile.options("X-GNOME-Metatheme"):
        #        if (options not in list_options):
        #            list_options.append(options)
        #for i in list_options:
        #    print(i)

class Theme():
    def __init__(self):
        self.util = Utils()
        # Location
        self.index_file = None
        self.directory = None
        self.directory_name = None

        # Description
        self.name = None
        self.comment = None

        # Support
        # self.support[name_of_the_support] = ([0] Value or None, [1] "type of conf", [2] "Folder or Key", [3] "Pretty Name", [4] version, [5] needed running application)
        self.support = {}
        self.support["gtk2"] = [None, "directory_structure", "gtk-2.0", "Gtk+2", 2, None]
        self.support["gtk3"] = [None, "directory_structure", "gtk-3", "Gtk+3", 3, None]
        self.support["openbox_settings"] = [None, "directory_structure", "openbox-3", "Openbox", 0, "openbox"]
        #TODO Implement into setting.py
        #self.support["metacity"] = [None, "directory_structure", "metacity-1", "Metacity", 0, "metacity"]
        #self.support["unity"] = [None, "directory_structure", "unity", "Unity", 0, "compiz"]
        #self.support["xfce-notify"] = [None, "directory_structure", "xfce-notify", "Xfce Notify", 0, "xfce-notify"]
        #self.support["xfwm"] = [None, "directory_structure", "xfwm4", "Xfwm", 0, "xfwm"]

        self.support["gtk_theme"] = [None, "theme_index", "GtkTheme", "GTK theme", 0, None]
        self.support["icon_theme"] = [None, "theme_index", "IconTheme", "Icon theme", 0, None]
        self.support["cursor_theme"] = [None, "theme_index", "CursorTheme", "Cursor theme", 0, None]
        self.support["cursor_size"] = [None, "theme_index", "CursorSize", "Cursor Size", 0, None]
        #TODO Implement into setting.py
        #self.support["metacity_theme"] = [None, "theme_index", "MetacityTheme", "Metacity theme", 0, "metacity"]
        #self.support["button_layout"] = [None, "theme_index", "ButtonLayout", "Layout of the buttons", 0, None]
        #self.support["overlay_scrollbars"] = [None, "theme_index", "X-Ubuntu-UseOverlayScrollbars", "Overlay scrollbars from Ubuntu", 0, None]
        #self.support["notification_theme"] = [None, "theme_index", "NotificationTheme", "Notification Theme", 0, None]
        #TODO Also read the configuration of the icon_theme on index.theme of the icon

        # ???
        self.type = None
        self.encoding = None 
        
    def read_index_file(self, index_file):
        self.index_file = index_file
        self.directory = os.path.dirname(self.index_file)

        keyfile = self.util.load_object("keyfile", self.index_file)
        
        self.name = self.util.get_setting("keyfile", keyfile, 'Desktop Entry', 'Name', None, 'string')
        if (self.name == None):
            self.name = self.util.get_setting("keyfile", keyfile, 'X-GNOME-Metatheme', 'Name', None, 'string')

        self.comment = self.util.get_setting("keyfile", keyfile, 'Desktop Entry', 'Comment', None, 'string')
        if (self.comment == None):
            self.comment = self.util.get_setting("keyfile", keyfile, 'X-GNOME-Metatheme', 'Comment', None, 'string')

        for conf in self.support:
            if (self.support[conf][1] == "theme_index"):
                self.support[conf][0] = self.util.get_setting("keyfile", keyfile, 'X-GNOME-Metatheme', self.support[conf][2], None, 'string')
        
        self.type = self.util.get_setting("keyfile", keyfile, 'X-GNOME-Metatheme', 'Type', None, 'string')
        self.encoding = self.util.get_setting("keyfile", keyfile, 'X-GNOME-Metatheme', 'Encoding', None, 'string')

    def read_directory(self):
        self.directory_name = os.path.basename(self.directory)
        list_directory = os.listdir(self.directory)
        for directory in list_directory:
            for theme in self.support:
                if (self.support[theme][1] == "directory_structure"):
                    if (directory == self.support[theme][2]):
                        self.support[theme][0] = self.directory_name
                    if (directory[:5] == 'gtk-3'):
                        self.support['gtk3'][0] = self.directory_name
                        version = float(directory[5:])
                        if (version > self.support['gtk3'][4]):
                            self.support['gtk3'][4] = float(directory[4:])
                    
    def debug(self):
        """ Prints variables and other useful items for debug purpose"""
        print("Printing variables for %s" % self.index_file)
        print("self.index_file : %s" % self.index_file)
        print("self.support items: (value, type, group/folder, key, Pretty Name, version)")
        for i in self.support:
            print("self.support for %s: %s - %s - %s - %s" % (i, self.support[i][0], self.support[i][1], self.support[i][2], self.support[i][3]))
        print("==========================")

# For testing purpose only
if __name__ == "__main__":
    app = LXCC_Module()
    app.debug()
