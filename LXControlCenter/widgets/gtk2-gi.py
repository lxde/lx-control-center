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
gi.require_version('Gtk', '2.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf

import logging

from .common import UI

class Gtk2App(UI):
    def __init__(self):
        UI.__init__(self)
        window = Gtk.Window()
        self.window=window
        window.set_title(self.window_title)
        window.connect("destroy", self.destroy)
        window.set_icon_name(self.window_icon)
        # TODO
        #window.connect("resize", self.destroy)

        self.window.set_default_size(self.window_size_w,self.window_size_h)

        window_scrolled = Gtk.ScrolledWindow()
        window.add(window_scrolled)
        self.vbox = Gtk.VBox()
        # GTK2 Specific: add_with_viewport
        window_scrolled.add_with_viewport(self.vbox)

        #Function to launch at startup
        self.build_UI()

    def build_UI(self):
        for category in self.items_visible_by_categories:
            frame = Gtk.Frame(label=category)
            self.vbox.add(frame)

            hbox = Gtk.HBox()
            frame.add(hbox)

            #Impossible to add a custom structure in liststore ...
            liststore = Gtk.ListStore(Pixbuf, str, str)
            iconview = Gtk.IconView.new()
            iconview.set_model(liststore)
            iconview.set_pixbuf_column(0)
            iconview.set_text_column(1)

            #GTK2 Specific => Force width to avoid too much spacing
            iconview.set_item_width(self.icon_view_icons_size * 4)

            iconview.set_columns(self.icon_view_columns)
            iconview.set_selection_mode(Gtk.SelectionMode.SINGLE)

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
                icon_lookup_flags = Gtk.IconLookupFlags.FORCE_SIZE
            else:
                icon_lookup_flags = Gtk.IconLookupFlags.GENERIC_FALLBACK

            theme = Gtk.IconTheme.get_default()

            for i in self.items_visible_by_categories[category]:
                if (len(i.icon) > 0):
                    if (self.icon_not_theme_allow == True):
                        if (i.icon[0] == "/"):
                            #Absolute path
                            try:
                                pixbuf = GdkPixbuf.Pixbuf.new_from_file(i.icon)
                            except:
                                pixbuf = theme.load_icon( self.icon_fallback,
                                                                                self.icon_view_icons_size,
                                                                                icon_lookup_flags)
                                logging.info("Error loading icon %s" % i.icon)                   
                    else:
                        try:
                            pixbuf = theme.load_icon( i.icon,
                                                                            self.icon_view_icons_size,
                                                                            icon_lookup_flags)
                        except:
                            pixbuf = theme.load_icon( self.icon_fallback,
                                                                            self.icon_view_icons_size,
                                                                            icon_lookup_flags)
                else:
                    pixbuf = theme.load_icon(self.icon_fallback, self.icon_view_icons_size, icon_lookup_flags)

                liststore.append([pixbuf, i.name, i.path])
            hbox.add(iconview)
       
        self.window.show_all()

    # GTK2 specific => enable single selection click
    def on_icon_view_selection_changed(self, widget):
        # TODO fix IndexError out of range
        self.on_item_activated(widget, widget.get_selected_items()[0])
                
    def on_item_activated(self, icon_view, tree_path):
        logging.debug("on_item_activated: click activated")
        model = icon_view.get_model()
        path = model[tree_path][2]
        logging.debug("on_item_activated: path = %s" % path)
        for i in self.items_visible:
            logging.debug("on_item_activated: test item path = %s" % i.path)
            if (i.path == path):
                i.launch()
                break
        icon_view.unselect_all()

    def on_resize(self):
        logging.debug("on_resize: resize activated")

    def destroy(self, widget, data=None):
        #TODO
        #UI.save_settings()
        Gtk.main_quit()

    def main(self):
        Gtk.main()
