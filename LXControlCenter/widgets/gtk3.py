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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

import logging

from .common import UI

class Gtk3App(UI):
    def __init__(self):
        UI.__init__(self)

        self.toolkit = "GTK3"

        window = Gtk.Window()
        self.window=window
        self.window.set_title(self.window_title)
        self.window.set_icon_name(self.window_icon)
        self.window.set_default_size(self.window_size_w,self.window_size_h)

        self.window.connect("destroy", self.destroy)
        self.window.connect("check-resize", self.on_resize)

        window_scrolled = Gtk.ScrolledWindow()
        self.window.add(window_scrolled)

        self.window_box = Gtk.VBox()
        window_scrolled.add(self.window_box)

        self.header_bar = Gtk.HeaderBar()

        self.content_ui_vbox = Gtk.VBox()
        self.window_box.pack_start(self.content_ui_vbox, True, True, 0)

        self.menu_button = Gtk.MenuButton()

        self.action_group = Gtk.ActionGroup("actions")

        self.theme = Gtk.IconTheme.get_default()

        # Function to launch at startup
        self.generate_view()
        self.build_toolbar()
        self.draw_ui()

    def draw_ui(self):
        if (self.mode == "main-UI"):
            self.action_group.get_action("IconsMode").set_visible(False)
            self.action_group.get_action("PrefMode").set_visible(True)
            self.action_group.get_action("EditMode").set_visible(True)
            self.build_icon_view()
        elif (self.mode == "edit-UI"):
            self.action_group.get_action("IconsMode").set_visible(True)
            self.action_group.get_action("PrefMode").set_visible(True)
            self.action_group.get_action("EditMode").set_visible(False)
            self.build_edit_view()
        elif (self.mode == "pref-UI"):
            self.action_group.get_action("IconsMode").set_visible(True)
            self.action_group.get_action("PrefMode").set_visible(False)
            self.action_group.get_action("EditMode").set_visible(True)
            self.build_pref_view()
        elif (self.mode == "module-UI"):
            self.action_group.get_action("IconsMode").set_visible(True)
            self.action_group.get_action("PrefMode").set_visible(True)
            self.action_group.get_action("EditMode").set_visible(True)
            self.build_module_view()
        self.window.show_all()

    def build_toolbar(self):
        self.header_bar.set_show_close_button(True)
        self.header_bar.props.title = self.window_title
        self.window.set_titlebar(self.header_bar)

        UI_INFO =   """
                    <ui>
                        <popup name='PopupMenu'>
                            <menuitem action='IconsMode' />
                            <menuitem action='PrefMode' />
                            <menuitem action='EditMode' />
                        </popup>
                    </ui>
                    """
        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(UI_INFO)
        self.action_group.add_actions([
            ("IconsMode", Gtk.STOCK_APPLY, self.icons_menu_item, None, self.icons_menu_item_tooltip, self.on_icons_mode_menu_click),
            ("PrefMode", Gtk.STOCK_PREFERENCES, self.preferences_menu_item, None, self.preferences_menu_item_tooltip, self.on_pref_mode_menu_click),
            ("EditMode", Gtk.STOCK_EDIT , self.edit_menu_item, None, self.edit_menu_item_tooltip, self.on_edit_mode_menu_click)
                                    ])
        uimanager.insert_action_group(self.action_group)
        popup = uimanager.get_widget("/PopupMenu")
        self.menu_button.set_popup(popup)

        pixbuf = self.theme.get_default().load_icon("open-menu-symbolic", 16, Gtk.IconLookupFlags.FORCE_SIZE)
        image = Gtk.Image.new_from_pixbuf(pixbuf)
        self.menu_button.add(image)
        self.header_bar.pack_start(self.menu_button)

    def create_switch_conf(self, grid, label, default, group, key, position):
        label_widget = Gtk.Label(label)
        switch_widget = Gtk.Switch()
        switch_widget.set_active(default)
        switch_widget.connect("notify::active", self.on_switch_click, group, key)
        grid.attach(label_widget, 0, position, 1, 1)
        grid.attach_next_to(switch_widget, label_widget, Gtk.PositionType.RIGHT, 1, 1)

    def create_table_conf(self):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)
        grid.set_row_homogeneous(False)
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)
        return grid

    def on_switch_click(self, switch, gparam, group, key):
        logging.debug("on_switch_click: Setting %s - %s to %s" % (group, key, switch.get_active()))
        self.set_setting(group, key, switch.get_active())

        # Need to re-triage the item, because we changed the filters
        self.triage_items()
        self.generate_view()

    def clean_main_view(self):
        for children in self.content_ui_vbox.get_children():
            self.content_ui_vbox.remove(children)

    def build_pref_view(self):
        #TODO
        self.clean_main_view()
    
        # Configuration
        configuration_frame = Gtk.Frame(label=self.pref_category_configuration_label)
        self.content_ui_vbox.add(configuration_frame)
        configuration_grid = self.create_table_conf()
        configuration_frame.add(configuration_grid)

        self.create_switch_conf(configuration_grid, self.pref_modules_support_label, self.modules_support, "Configuration", "modules_support", 0)
        self.create_switch_conf(configuration_grid, self.pref_applications_support_label, self.applications_support, "Configuration", "applications_support", 1)

    def build_edit_view(self):
        #TODO
        self.clean_main_view()       

    def build_icon_view(self):

        self.clean_main_view()

        for category in self.items_visible_by_categories:
            frame = Gtk.Frame(label=category)
            self.content_ui_vbox.add(frame)

            hbox = Gtk.HBox()
            frame.add(hbox)

            #Impossible to add a custom structure in liststore ...
            liststore = Gtk.ListStore(Pixbuf, str, str)
            iconview = Gtk.IconView.new()
            iconview.set_model(liststore)
            iconview.set_pixbuf_column(0)
            iconview.set_text_column(1)
            iconview.set_columns(self.icon_view_columns)
            iconview.set_selection_mode(Gtk.SelectionMode.SINGLE)
            iconview.set_activate_on_single_click(True)

            iconview.connect("item-activated", self.on_item_activated)

            logging.debug("build_UI: get_item_width = %s" % iconview.get_item_width())
            logging.debug("build_UI: get_spacing = %s" % iconview.get_spacing())
            logging.debug("build_UI: get_row_spacing = %s" % iconview.get_row_spacing())
            logging.debug("build_UI: get_column_spacing = %s" % iconview.get_column_spacing())
            logging.debug("build_UI: get_margin = %s" % iconview.get_margin())
            logging.debug("build_UI: get_item_padding = %s" % iconview.get_item_padding())
            logging.debug("build_UI: item orientation = %s" % iconview.get_item_orientation())


            if (self.icon_force_size == True):
                icon_lookup_flags = Gtk.IconLookupFlags.FORCE_SIZE
            else:
                icon_lookup_flags = Gtk.IconLookupFlags.GENERIC_FALLBACK

            self.define_icon_type_with_gtk_theme()

            for i in self.items_visible_by_categories[category]:
                if (i.icon_type == "fix"):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(i.icon)
                elif (i.icon_type == "themed"):
                    pixbuf = self.theme.load_icon(i.icon, self.icon_view_icons_size, icon_lookup_flags)
                else:
                    pixbuf = self.theme.load_icon(self.icon_fallback, self.icon_view_icons_size, icon_lookup_flags)

                liststore.append([pixbuf, i.name, i.path])

            hbox.add(iconview)

    def define_icon_type_with_gtk_theme(self):
        for i in self.items_visible:
            if (i.icon_type == "fix"):
                if (self.icon_not_theme_allow == False):
                    i.icon_type = "fallback"
            elif (i.icon_type == "themed"):
                if (self.theme.has_icon(i.icon) == False):
                    i.icon_type = "fallback"


    def on_item_activated(self, icon_view, tree_path):
        logging.debug("on_item_activated: click activated")
        model = icon_view.get_model()
        path = model[tree_path][2]
        logging.debug("on_item_activated: path = %s" % path)
        self.on_item_activated_common(path)
        icon_view.unselect_all()

    def on_resize(self, widget, data=None):
        self.on_resize_common(self.window.get_size()[0], self.window.get_size()[1])

    def destroy(self, widget, data=None):
        self.save_settings()
        Gtk.main_quit()

    def main(self):
        Gtk.main()
