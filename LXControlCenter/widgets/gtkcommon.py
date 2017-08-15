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

import logging

class GtkWidgets(object):
    def __init__(self, toolkit):
        self.toolkit = toolkit
        # Set to True to display all the widget, even without supports (for debug purpose only)
        self.gtk_widgets_debug_mode = False

        global Gtk
        if self.toolkit == "GTK3":
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
        else:
            import gi
            gi.require_version('Gtk', '2.0')
            from gi.repository import Gtk

    # Grid / Table
    def create_table_conf(self):
        grid = None
        if self.toolkit == "GTK3":
            grid = Gtk.Grid()
            grid.set_column_homogeneous(False)
            grid.set_row_homogeneous(False)
            grid.set_column_spacing(20)
            grid.set_row_spacing(20)
            grid.set_margin_left(30)
            grid.set_margin_right(30)
            grid.set_margin_top(10)
            grid.set_margin_bottom(10)
            grid.set_size_request(self.window_size_w - 480, -1)
        else:
            grid = Gtk.Table()
            grid.set_homogeneous(False)
            grid.set_col_spacings(20)
            grid.set_row_spacings(20)
            grid.set_size_request(self.window_size_w - 240, -1)
        return grid

    # Font selection
    def add_font_chooser(self, setting, grid, position):
        if len(setting.support_list) > 0 or self.gtk_widgets_debug_mode == True:
            font_button = Gtk.FontButton()
            if setting.get() != None:
                font_button.set_font_name(setting.get())
            font_button.connect("font_set", self.on_default_font_setting_set, setting)
            font_label = Gtk.Label(setting.display_name)
            self.attach_widget(position, font_label, font_button, grid)
            position = position +1
        return position

    def on_default_font_setting_set(self, widget, setting):
        logging.debug("Save value: %s" % widget.get_font_name())
        setting.set(widget.get_font_name())

    # Spinbutton
    def add_spin_button(self, setting, grid, position, spin_conf):
        """
        setting = Setting to get / set
        grid = GtkTable / GtkGrid to attach the widget
        position = where to attach the widget
        spin_conf = list of spinbutton options
                    [0] = minimum
                    [1] = maximum
                    [2] = step
                    [3] = digits
        
        return: Return the position after attaching the widget.
        """
        if len(setting.support_list) > 0 or self.gtk_widgets_debug_mode == True:
            default_value = setting.get()
            if default_value is None:
                default_value = spin_conf[0]
            adjustment = Gtk.Adjustment(value=default_value, lower=spin_conf[0], upper=spin_conf[1], step_incr=spin_conf[2], page_incr=1, page_size=0)
            spin_button = Gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=spin_conf[3])
            spin_button.connect("value-changed", self.on_spin_button_change, setting)
            spin_label = Gtk.Label(setting.display_name)
            self.attach_widget(position, spin_label, spin_button, grid)
            position = position +1
        return position

    def on_spin_button_change(self, widget, setting):
        logging.debug("Save value: %s" % widget.get_value_as_int())
        setting.set(widget.get_value_as_int())
    
    def add_combobox_text(self, setting, grid, position):
        logging.info("gtkcommon.add_combobox: enter function")
        if len(setting.support_list) > 0 or self.gtk_widgets_debug_mode == True:
            default_value = setting.get()
            combo_label = Gtk.Label(setting.display_name)
            store = Gtk.ListStore(int, str, str)
            index = 0
            for item in setting.available_values:
                store.append([index, item, setting.available_values[item]])
                index = index + 1
            combo = Gtk.ComboBox.new_with_model(store)
            renderer_text = Gtk.CellRendererText()
            combo.pack_start(renderer_text, True)
            combo.add_attribute(renderer_text, "text", 2)
            for i in store:
                if store[i.iter][1] == default_value:
                    combo.set_active(store[i.iter][0])
                    break
            combo.connect("changed", self.on_combobox_text_change, setting)   
            self.attach_widget(position, combo_label, combo, grid)
            position = position +1
        return position

    def on_combobox_text_change(self, widget, setting):
        logging.info("gtkcommon.on_combobox_text_change: enter function")
        iter = widget.get_active_iter()
        model = widget.get_model()
        setting.set(model[iter][1])

    def add_switch(self, setting, grid, position):
        logging.info("gtkcommon.add_switch: enter function")
        if len(setting.support_list) > 0 or self.gtk_widgets_debug_mode == True:
            default_value = setting.get()
            switch_label = Gtk.Label(setting.display_name)
            if self.toolkit == "GTK3":
                switch_widget = Gtk.Switch()
                switch_widget.set_active(default_value)
                switch_widget.connect("notify::active", self.on_gtk3_switch_change, setting)
                self.attach_widget(position, switch_label, switch_widget, grid)
                position = position +1
            else:
                switch_widget = Gtk.ToggleButton("?")
                logging.debug(" create_switch_conf: default = %s" % default_value)
                switch_widget.set_size_request(60, 30)
                if (default_value == True):
                    switch_widget.set_active(1)
                    switch_widget.set_label("ON")
                else:
                    switch_widget.set_active(0)
                    switch_widget.set_label("OFF")
                switch_widget.connect("toggled", self.on_gtk2_switch_change, setting)
                self.attach_widget(position, switch_label, switch_widget, grid)
                position = position +1
        return position

    def on_gtk3_switch_change(self, widget, gparam, setting):
        logging.debug("Save value: %s" % widget.get_active())
        setting.set(widget.get_active())
    
    def on_gtk2_switch_change(self, widget, setting):
        if (widget.get_active() == True):
            widget.set_label("ON")
            setting.set(True)
        else:
            widget.set_label("OFF")
            setting.set(False)

    def attach_widget(self,position, label, widget, grid):
        if self.toolkit == "GTK3":
            # (0, 0, 1, 1)
            # (1, 0, 1, 1)
            grid.attach(label, 0, position, 1, 1)
            grid.attach(widget, 1, position, 1, 1)
            label.set_alignment(0,0.5)
        else:
            # (0, 1, 0, 1)
            # (1, 2, 0, 1)
            grid.attach(label, 0, 1, position, position +1, xpadding=30, ypadding=10)
            grid.attach(widget, 1, 2, position, position +1, xpadding=30, ypadding=10)
            label.set_alignment(0,0.5)
            try:
                widget.set_alignment(0.5,0)
            except:
                widget.set_alignment(0.5)