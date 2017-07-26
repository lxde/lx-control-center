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

from ..base import Base

class Gtk3App(Base):
    def __init__(self):
        Base.__init__(self)

    def draw_ui(self):
        logging.info("GTK3.draw_ui: enter function")
        if (self.mode == "main-UI"):
            if (self.standalone_module == None):
                self.action_group.get_action("IconsMode").set_visible(False)
                self.action_group.get_action("PrefMode").set_visible(True)
                self.action_group.get_action("EditMode").set_visible(True)
                self.icon_view_button.set_sensitive(False)
                self.edit_view_button.set_sensitive(True)
                self.pref_view_button.set_sensitive(True)
            self.build_icon_view()
        elif (self.mode == "edit-UI"):
            if (self.standalone_module == None):
                self.action_group.get_action("IconsMode").set_visible(True)
                self.action_group.get_action("PrefMode").set_visible(True)
                self.action_group.get_action("EditMode").set_visible(False)
                self.icon_view_button.set_sensitive(True)
                self.edit_view_button.set_sensitive(False)
                self.pref_view_button.set_sensitive(True)
            self.build_edit_view()
        elif (self.mode == "pref-UI"):
            if (self.standalone_module == None):
                self.action_group.get_action("IconsMode").set_visible(True)
                self.action_group.get_action("PrefMode").set_visible(False)
                self.action_group.get_action("EditMode").set_visible(True)
                self.icon_view_button.set_sensitive(True)
                self.edit_view_button.set_sensitive(True)
                self.pref_view_button.set_sensitive(False)
            self.build_pref_view()
        elif (self.mode == "module-UI"):
            if (self.standalone_module == None):
                self.action_group.get_action("IconsMode").set_visible(True)
                self.action_group.get_action("PrefMode").set_visible(True)
                self.action_group.get_action("EditMode").set_visible(True)
                self.icon_view_button.set_sensitive(True)
                self.edit_view_button.set_sensitive(True)
                self.pref_view_button.set_sensitive(True)
            self.build_module_view()
        elif (self.mode == "edit-item-UI"):
            if (self.standalone_module == None):
                self.action_group.get_action("IconsMode").set_visible(True)
                self.action_group.get_action("PrefMode").set_visible(True)
                self.action_group.get_action("EditMode").set_visible(True)
                self.icon_view_button.set_sensitive(True)
                self.edit_view_button.set_sensitive(True)
                self.pref_view_button.set_sensitive(True)
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

        menu_pixbuf = self.theme.get_default().load_icon("open-menu-symbolic", 16, Gtk.IconLookupFlags.FORCE_SIZE)
        image = Gtk.Image.new_from_pixbuf(menu_pixbuf)
        self.menu_button.add(image)
        self.header_bar.pack_start(self.menu_button)

    def clean_main_view(self):
        for children in self.content_ui_vbox.get_children():
            self.content_ui_vbox.remove(children)

    def create_switch_conf(self, grid, label, default, group, key, position):
        label_widget = Gtk.Label(label, xalign=0)
        switch_widget = Gtk.Switch()
        switch_widget.set_active(default)
        switch_widget.connect("notify::active", self.on_switch_click, group, key)
        grid.attach(label_widget, 0, position, 1, 1)
        grid.attach_next_to(switch_widget, label_widget, Gtk.PositionType.RIGHT, 1, 1)

    def on_switch_click(self, switch, gparam, group, key):
        logging.debug("on_switch_click: Setting %s - %s to %s" % (group, key, switch.get_active()))
        self.set_setting(group, key, switch.get_active())

        # Need to re-triage the item, because we changed the filters
        self.triage_items()
        self.generate_view()

    # SpinButton
    def create_spinbutton_conf(self, grid, label, default, group, key, position):
        label_widget = Gtk.Label(label, xalign=0)
        adjustment = Gtk.Adjustment(value=default, lower=8, upper=128, step_incr=1, page_incr=1, page_size=0)
        spin_button_widget = Gtk.SpinButton(adjustment=adjustment, climb_rate=0.0, digits=0)
        spin_button_widget.connect("value-changed", self.on_spinbutton_change, group, key)
        grid.attach(label_widget, 0, position, 1, 1)
        grid.attach_next_to(spin_button_widget, label_widget, Gtk.PositionType.RIGHT, 1, 1)

    def on_spinbutton_change(self, spinbutton, group, key):
        logging.debug("on_spinbutton_change: Setting %s - %s to %s" % (group, key, spinbutton.get_value_as_int()))
        self.set_setting(group, key, spinbutton.get_value_as_int())
        self.generate_view()

    def create_table_conf(self):
        grid = Gtk.Grid()
        grid.set_column_homogeneous(False)
        grid.set_row_homogeneous(False)
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)
        grid.set_margin_left(30)
        grid.set_margin_right(30)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        return grid

    def build_pref_view(self):
        #TODO Complete options
        self.clean_main_view()
    
        # Configuration
        configuration_frame = Gtk.Frame(label=self.pref_category_configuration_label)
        self.content_ui_vbox.add(configuration_frame)
        configuration_grid = self.create_table_conf()
        configuration_frame.add(configuration_grid)

        self.create_switch_conf(configuration_grid, self.pref_modules_support_label, self.modules_support, "Configuration", "modules_support", 0)
        self.create_switch_conf(configuration_grid, self.pref_applications_support_label, self.applications_support, "Configuration", "applications_support", 1)
        self.create_switch_conf(configuration_grid, self.pref_show_category_other_label, self.show_category_other, "Configuration", "show_category_other", 2)
        self.create_switch_conf(configuration_grid, self.pref_enable_experimental_module_label, self.modules_experimental_support, "Configuration", "modules_experimental_support", 3)
        self.create_spinbutton_conf(configuration_grid, self.pref_icon_view_icons_size, self.icon_view_icons_size, "Configuration", "icon_view_icons_size", 4)

    def build_edit_view(self):
        logging.info("GTK3.build_edit_view: enter function")
        self.clean_main_view()
        # Update items for search filter
        self.items_by_categories_generate()
        self.build_generic_icon_view("all")

    def build_icon_view(self):
        self.clean_main_view()
        # Generate the view again, to take the modifications of edit_view
        self.generate_view()
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
            liststore = Gtk.ListStore(Pixbuf, str, str)
            iconview = Gtk.IconView.new()
            iconview.set_model(liststore)
            iconview.set_pixbuf_column(0)
            iconview.set_text_column(1)
            iconview.set_columns(self.icon_view_columns)
            iconview.set_selection_mode(Gtk.SelectionMode.SINGLE)
            iconview.set_activate_on_single_click(True)

            if (self.mode == "main-UI"):
                iconview.connect("item-activated", self.on_item_activated)
            elif (self.mode == "edit-UI"):
                iconview.connect("item-activated", self.on_item_edit_activated)

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

            for i in items_to_draw[category]:
                logging.debug("build_generic_icon_view - item loop: %s" % i.path)
                if (i.icon_type == "fix"):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(i.icon)
                elif (i.icon_type == "themed"):
                    try:
                        pixbuf = self.theme.load_icon(i.icon, self.icon_view_icons_size, icon_lookup_flags)
                    except:
                        pixbuf = self.theme.load_icon(self.icon_fallback, self.icon_view_icons_size, icon_lookup_flags)
                else:
                    pixbuf = self.theme.load_icon(self.icon_fallback, self.icon_view_icons_size, icon_lookup_flags)
                logging.debug("build_generic_icon_view - item add: %s - %s" % (i.name, i.path))

                display_name = i.name

                if (i.activate == False):
                    logging.debug("build_generic_icon_view - Grey inactive icons: %s - %s" % (i.name, i.path))
                    desaturated = pixbuf.copy()
                    pixbuf.saturate_and_pixelate(desaturated, 0.1, True)
                    display_name = _("(Inactive) - ") + i.name
                    liststore.append([desaturated, display_name, i.path])
                else:
                    liststore.append([pixbuf, display_name, i.path])

            hbox.add(iconview)

    def define_icon_type_with_gtk_theme(self):
        for i in self.items:
            if (self.items[i].icon_type == "fix"):
                if (self.icon_not_theme_allow == False):
                    self.items[i].icon_type = "fallback"
            elif (self.items[i].icon_type == "themed"):
                if (self.theme.has_icon(self.items[i].icon) == False):
                    self.items[i].icon_type = "fallback"


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
        self.build_edit_item_view(path)
        icon_view.unselect_all()

    def build_edit_item_view(self, path):
        # TODO Icon image for icon
        self.clean_main_view()
        self.mode = "edit-item-UI"
        self.item_to_save = self.items[path]

        box_name = Gtk.HBox()
        label_name = Gtk.Label()
        label_name.set_text(_("Name"))
        box_name.pack_start(label_name, False, False, 3)
        self.entry_name = Gtk.Entry()
        self.entry_name.set_text(self.item_to_save.name)
        box_name.pack_start(self.entry_name, False, False, 3)
        self.content_ui_vbox.pack_start(box_name, False, False, 3)

        box_comment = Gtk.HBox()
        label_comment = Gtk.Label()
        label_comment.set_text(_("Comment"))
        box_comment.pack_start(label_comment, False, False, 3)
        self.entry_comment = Gtk.Entry()
        self.entry_comment.set_text(self.item_to_save.comment)
        box_comment.pack_start(self.entry_comment, False, False, 3)
        self.content_ui_vbox.pack_start(box_comment, False, False, 3)

        box_activate = Gtk.HBox()
        self.check_activate = Gtk.CheckButton()
        self.check_activate.set_label(_("Activate ?"))
        self.check_activate.set_active(self.item_to_save.activate)
        box_activate.add(self.check_activate)
        self.content_ui_vbox.pack_start(box_activate, False, False, 0)

        if (self.item_to_save.deactivate_reasons != []):
            box_deactivate_reasons = Gtk.HBox()
            deactivate_reasons_title = Gtk.Label()
            deactivate_reasons_title.set_text(_("Reason(s) for deactivation"))
            box_deactivate_reasons.add(deactivate_reasons_title)

            deactivate_reasons_label = Gtk.Label()
            label_to_display = ""
            for label in self.item_to_save.deactivate_reasons:
                label_to_display = label_to_display + label + "\n"
            deactivate_reasons_label.set_text(label_to_display)
            box_deactivate_reasons.add(deactivate_reasons_label)
            self.content_ui_vbox.pack_start(box_deactivate_reasons, False, False, 3)

        box_buttons = Gtk.HBox()
        save_button = Gtk.Button()
        save_button.set_label(_("Save"))
        save_button.connect("clicked", self.on_edit_item_save)
        box_buttons.add(save_button)
        default_button = Gtk.Button()
        default_button.set_label(_("Set to default values"))
        default_button.connect("clicked", self.on_edit_item_default)
        box_buttons.add(default_button)
        cancel_button = Gtk.Button()
        cancel_button.set_label(_("Cancel"))
        cancel_button.connect("clicked", self.on_edit_item_cancel)
        box_buttons.add(cancel_button)
        self.content_ui_vbox.pack_start(box_buttons, False, False, 0)

        # TODO Display other information about the desktop file
        box_location = Gtk.HBox()
        label_location = Gtk.Label()
        label_location.set_text(_("Location"))
        box_location.pack_start(label_location, False, False, 3)
        self.entry_location = Gtk.Label()
        self.entry_location.set_text(self.item_to_save.path)
        box_location.pack_start(self.entry_location, False, False, 3)
        self.content_ui_vbox.pack_start(box_location, False, False, 3)

        self.draw_ui()

    def on_edit_item_save(self, button):
        if (self.item_to_save.name != self.entry_name.get_text()):
            self.item_to_save.name = self.entry_name.get_text()
            self.item_to_save.changed = True

        if (self.item_to_save.comment != self.entry_comment.get_text()):
            self.item_to_save.comment = self.entry_comment.get_text()
            self.item_to_save.changed = True

        if (self.item_to_save.activate != self.check_activate.get_active()):
            self.item_to_save.activate = self.check_activate.get_active()
            self.item_to_save.changed = True

        self.mode = "edit-UI"
        self.build_edit_view()
        self.draw_ui()

    def on_edit_item_cancel(self, button):
        self.mode = "edit-UI"
        self.build_edit_view()
        self.draw_ui()

    def on_edit_item_default(self, button):
        self.entry_name.set_text(self.item_to_save.name_original)
        #self.item_to_save.icon = self.item_to_save.icon_original
        self.entry_comment.set_text(self.item_to_save.comment_original)
        self.check_activate.set_active(self.item_to_save.activate_original)
        self.item_to_save.changed = True

    def on_resize(self, widget, data=None):
        self.on_resize_common(self.window.get_size()[0], self.window.get_size()[1])

    def on_search(self, widget, data=None):
        logging.info("GTK3.on_search: enter function")
        self.search_string = self.search_box.get_text()
        self.draw_ui()

    def create_togglebutton(self, label, icon):
        button = Gtk.Button(label = label)
        button.set_size_request(200, -1)
        icon_pixbuf = self.theme.get_default().load_icon(icon, 24, Gtk.IconLookupFlags.FORCE_SIZE)
        icon_image = Gtk.Image.new_from_pixbuf(icon_pixbuf)
        button.set_image(icon_image)
        button.set_sensitive(False)
        return button

    def destroy(self, widget, data=None):
        self.save_settings()
        Gtk.main_quit()

    def main(self):
        # Function to launch at startup
        self.init()
        logging.info("GTK3.main: finish init()")

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

        # Header
        # Icon view - Edit View - Preferences - Search
        self.header_box = Gtk.HBox()
        self.window_box.pack_start(self.header_box, False, False, 0)

        self.theme = Gtk.IconTheme.get_default()

        self.icon_view_button = self.create_togglebutton(self.icons_menu_item, Gtk.STOCK_APPLY)
        self.icon_view_button.connect("clicked", self.on_icons_mode_menu_click)
        self.header_box.pack_start(self.icon_view_button, False, False, 0)

        self.edit_view_button = self.create_togglebutton(self.edit_menu_item, Gtk.STOCK_EDIT)
        self.edit_view_button.connect("clicked", self.on_edit_mode_menu_click)
        self.header_box.pack_start(self.edit_view_button, False, False, 0)

        self.pref_view_button = self.create_togglebutton(self.preferences_menu_item, Gtk.STOCK_PREFERENCES)
        self.pref_view_button.connect("clicked", self.on_pref_mode_menu_click)
        self.header_box.pack_start(self.pref_view_button, False, False, 0)

        self.search_box = Gtk.Entry()
        self.search_box.set_placeholder_text(_("Search")
        self.search_box.connect("changed", self.on_search)
        self.header_box.pack_end(self.search_box, True, True, 0)

        self.content_ui_vbox = Gtk.VBox()
        self.window_box.pack_start(self.content_ui_vbox, False, False, 0)

        self.menu_button = Gtk.MenuButton()

        self.action_group = Gtk.ActionGroup("actions")

        self.generate_view()
        if (self.standalone_module == None):
            self.build_toolbar()
        self.draw_ui()
        self.set_standalone()
        Gtk.main()
