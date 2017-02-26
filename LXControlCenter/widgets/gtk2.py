#!/usr/bin/env python2
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

import pygtk
pygtk.require('2.0')
import gtk as Gtk

import logging

from .common import UI

class Gtk2App(UI):
    def __init__(self):
        UI.__init__(self)

        self.toolkit = "GTK2"

        window = Gtk.Window()
        self.window=window
        self.window.set_title(self.window_title)
        self.window.set_icon_name(self.window_icon)
        self.window.set_default_size(self.window_size_w,self.window_size_h)

        self.window.connect("destroy", self.destroy)
        self.window.connect("check-resize", self.on_resize)

        window_scrolled = Gtk.ScrolledWindow()
        # GTK2 specific
        #window_scrolled.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        self.window.add(window_scrolled)

        self.window_box = Gtk.VBox()
        # GTK2 Specific: add_with_viewport
        window_scrolled.add_with_viewport(self.window_box)

        self.main_ui_vbox = Gtk.VBox()
        self.window_box.add(self.main_ui_vbox)

        # GTK2 Specific
        self.menu_bar = Gtk.MenuBar()
        self.main_ui_vbox.pack_start(self.menu_bar, False, True, 0)

        self.content_ui_vbox = Gtk.VBox()
        self.main_ui_vbox.pack_start(self.content_ui_vbox, False, True, 0)

        # GTK2 Specific
        self.filem_icons = Gtk.MenuItem(self.icons_menu_item)
        self.filem_pref = Gtk.MenuItem(self.preferences_menu_item)
        self.filem_edit = Gtk.MenuItem(self.edit_menu_item)
        #self.menu_button = Gtk.ToolButton()

        self.action_group = Gtk.ActionGroup("actions")

        #GTK2 specific
        self.theme = Gtk.icon_theme_get_default()

        # Function to launch at startup
        self.generate_view()
        self.build_toolbar()
        self.draw_ui()

    def draw_ui(self):
        if (self.mode == "main-UI"):
            self.filem_icons.set_sensitive(False)
            self.filem_pref.set_sensitive(True)
            self.filem_edit.set_sensitive(True)
            self.build_icon_view()
        elif (self.mode == "edit-UI"):
            self.filem_icons.set_sensitive(True)
            self.filem_pref.set_sensitive(True)
            self.filem_edit.set_sensitive(False)
            self.build_edit_view()
        elif (self.mode == "pref-UI"):
            self.filem_icons.set_sensitive(True)
            self.filem_pref.set_sensitive(False)
            self.filem_edit.set_sensitive(True)
            self.build_pref_view()
        elif (self.mode == "module-UI"):
            self.filem_icons.set_sensitive(True)
            self.filem_pref.set_sensitive(True)
            self.filem_edit.set_sensitive(True)
            self.build_module_view()
        self.window.show_all()

    def build_toolbar(self):

        filem = Gtk.ImageMenuItem(Gtk.STOCK_PREFERENCES)
        filemenu = Gtk.Menu()
        filem.set_submenu(filemenu)

        self.filem_icons.connect("activate", self.on_icons_mode_menu_click)
        filemenu.append(self.filem_icons)

        self.filem_pref.connect("activate", self.on_pref_mode_menu_click)
        filemenu.append(self.filem_pref)

        self.filem_edit.connect("activate", self.on_edit_mode_menu_click)
        filemenu.append(self.filem_edit)

        self.menu_bar.append(filem)
  

    def clean_main_view(self):
        for children in self.content_ui_vbox.get_children():
            self.content_ui_vbox.remove(children)

    def create_switch_conf(self, grid, label, default, group, key, position):
        label_widget = Gtk.Label(label)
        switch_widget = Gtk.ToggleButton("?")
        logging.debug(" create_switch_conf: default = %s" % default)
        switch_widget.set_size_request(30, 30)
        if (default == True):
            switch_widget.set_active(1)
            switch_widget.set_label("ON")
        else:
            switch_widget.set_active(0)
            switch_widget.set_label("OFF")

        switch_widget.connect("toggled", self.on_switch_click, group, key)
        grid.attach(label_widget, 0, 1, position, position + 1)
        grid.attach(switch_widget, 1, 2, position, position + 1)

    def create_table_conf(self):
        grid = Gtk.Table()
        #grid.set_column_homogeneous(False)
        #grid.set_row_homogeneous(False)
        grid.set_col_spacings(0)
        grid.set_row_spacings(0)
        return grid

    def on_switch_click(self, switch, group, key):
        logging.debug("on_switch_click: Setting %s - %s to %s" % (group, key, switch.get_active()))
        self.set_setting(group, key, switch.get_active())
        if (switch.get_active() == True):
            switch.set_label("ON")
        else:
            switch.set_label("OFF")
        self.generate_view()

    def build_pref_view(self):
        #TODO
        self.clean_main_view()
        # Configuration
        configuration_frame = Gtk.Frame(label=self.pref_category_configuration_label)
        self.content_ui_vbox.pack_start(configuration_frame, False, False)
        configuration_grid = self.create_table_conf()
        configuration_frame.add(configuration_grid)

        self.create_switch_conf(configuration_grid, self.pref_modules_support_label, self.modules_support, "Configuration", "modules_support", 0)
        self.create_switch_conf(configuration_grid, self.pref_applications_support_label, self.applications_support, "Configuration", "applications_support", 1)

    def build_edit_view(self):
        self.clean_main_view()
        self.build_generic_icon_view("all")

    def build_icon_view(self):
        self.clean_main_view()
        self.build_generic_icon_view("visible")

    def build_generic_icon_view(self, type_view):

        items_to_draw = self.items_visible_by_categories

        if (type_view == "all"):
            items_to_draw = self.items_by_categories

        for category in items_to_draw:
            logging.debug("build_generic_icon_view - category loop: %s" % category)
            frame = Gtk.Frame(label=category)
            self.content_ui_vbox.add(frame)

            hbox = Gtk.HBox()
            frame.add(hbox)

            #Impossible to add a custom structure in liststore ...
            liststore = Gtk.ListStore(Gtk.gdk.Pixbuf, str, str)
            iconview = Gtk.IconView(liststore)
            iconview.set_pixbuf_column(0)
            iconview.set_text_column(1)
            #GTK2 Specific => Force width to avoid too much spacing
            iconview.set_item_width(self.icon_view_icons_size * 4)
            iconview.set_columns(self.icon_view_columns)
            iconview.set_selection_mode(Gtk.SELECTION_SINGLE)

            #GTK2 spcific => enable single selection click
            iconview.connect("selection_changed", self.on_icon_view_selection_changed)

            logging.debug("build_UI: get_item_width = %s" % iconview.get_item_width())
            logging.debug("build_UI: get_spacing = %s" % iconview.get_spacing())
            logging.debug("build_UI: get_row_spacing = %s" % iconview.get_row_spacing())
            logging.debug("build_UI: get_column_spacing = %s" % iconview.get_column_spacing())
            logging.debug("build_UI: get_margin = %s" % iconview.get_margin())
            logging.debug("build_UI: get_item_padding = %s" % iconview.get_item_padding())
            logging.debug("build_UI: item orientation = %s" % iconview.get_item_orientation())


            if (self.icon_force_size == True):
                icon_lookup_flags = Gtk.ICON_LOOKUP_FORCE_SVG
            else:
                icon_lookup_flags = Gtk.ICON_LOOKUP_USE_BUILTIN

            self.define_icon_type_with_gtk_theme()

            for i in items_to_draw[category]:
                logging.debug("build_generic_icon_view - item loop: %s" % i.path)
                if (i.icon_type == "fix"):
                    pixbuf = Gtk.gdk.pixbuf_new_from_file(i.icon)
                elif (i.icon_type == "themed"):
                    try:
                        pixbuf = self.theme.load_icon(i.icon, self.icon_view_icons_size, icon_lookup_flags)
                    except:
                        pixbuf = self.theme.load_icon(self.icon_fallback, self.icon_view_icons_size, icon_lookup_flags)
                else:
                    pixbuf = self.theme.load_icon(self.icon_fallback, self.icon_view_icons_size, icon_lookup_flags)
                logging.debug("build_generic_icon_view - item add: %s - %s" % (i.name, i.path))

                # TODO grey icon if activate == False

                liststore.append([pixbuf, i.name, i.path])

            hbox.add(iconview)

    def define_icon_type_with_gtk_theme(self):
        for i in self.items:
            if (self.items[i].icon_type == "fix"):
                if (self.icon_not_theme_allow == False):
                    self.items[i].icon_type = "fallback"
            elif (self.items[i].icon_type == "themed"):
                if (self.theme.has_icon(self.items[i].icon) == False):
                    self.items[i].icon_type = "fallback"

    # GTK2 specific => enable single selection click
    def on_icon_view_selection_changed(self, widget, data=None):
        self.on_item_activated(widget, widget.get_selected_items()[0])
    def on_edit_view_selection_changed(self, widget, data=None):
        self.on_item_edit_activated(widget, widget.get_selected_items()[0])

    def on_item_activated(self, icon_view, tree_path):
        logging.debug("on_item_activated: click activated")
        model = icon_view.get_model()
        path = model[tree_path][2]
        logging.debug("on_item_activated: path = %s" % path)
        self.on_item_activated_common(path)
        icon_view.unselect_all()

    def on_item_edit_activated(self, icon_view, tree_path):
        logging.debug("on_item_edit_activated: click activated")
        model = icon_view.get_model()
        path = model[tree_path][2]
        logging.debug("on_item_edit_activated: path = %s" % path)
        #TODO Create widget for modification
        self.item_edit_widget(path)
        icon_view.unselect_all()

    def item_edit_widget(self, item_path):
        # TODO Input Text for name
        # TODO Input Text for comment
        # TODO Icon image for icon
        # TODO Checkbox for activate
        # TODO reason for activate state
        # TODO Button save
        # TODO Button cancel

    def on_resize(self, widget, data=None):
        self.on_resize_common(self.window.get_size()[0], self.window.get_size()[1])

    def destroy(self, widget, data=None):
        self.save_settings()
        Gtk.main_quit()

    def main(self):
        Gtk.main()
