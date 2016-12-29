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

from ..base import Main

import collections
import logging

class UI(Main):
    def __init__(self):
        Main.__init__(self)

        # Items visible in the view, to be display
        self.items_visible = []

        # Items visible, triage by categories
        self.items_visible_by_categories = {}

        # Different mode of display the UI : 
        #  - main-UI => Icons view
        #  - pref-UI => Preferences view
        #  - edit-UI => Edit mode of the icons view
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
        self.pref_modules_support_label = _("Activate module support")
        self.pref_applications_support_label = _("Activate applications support")

    def generate_view(self):
        self.triage_items()
        self.items_visible_generate()
        self.items_visible_by_categories_generate()
        self.icon_view_columns_generate()

    def items_visible_generate(self):
        logging.debug("items_visible_generate: enter function")
        self.items_visible = []
        for i in self.items:
            if (i.activate == True):
                logging.debug("items_visible_generate: append %s in items_visible_generate" % i.path)
                self.items_visible.append(i)

    def items_visible_by_categories_generate(self):
        logging.debug("items_visible_by_categories_generate: enter function")
        self.items_visible_by_categories = {}
        non_order_dict = {}
        for i in self.items_visible:
                if (i.category not in non_order_dict):
                    empty_list = []
                    non_order_dict[i.category] = empty_list

                non_order_dict[i.category].append(i)

        self.items_visible_by_categories = collections.OrderedDict(sorted(non_order_dict.items()))

    #TODO Sorting items inside categories

    def icon_view_columns_generate(self):
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
        logging.debug("on_icons_mode_menu_click: Clicked")
        self.mode = "main-UI"
        self.draw_ui()

    def on_edit_mode_menu_click(self, widget, data=None):
        logging.debug("on_edit_mode_menu_click: Clicked")
        self.mode = "edit-UI"
        self.draw_ui()
        pass

    def on_pref_mode_menu_click(self, widget, data=None):
        logging.debug("on_pref_mode_menu_click: Clicked")
        self.mode = "pref-UI"
        self.draw_ui()

    def build_module_view(self):
        self.clean_main_view()
        module_class = self.module_activated.module_spec.LXCC_Module()
        self.content_ui_vbox.add(module_class.main_box)

    def on_item_activated_common(self, path):
        for i in self.items:
            logging.debug("on_item_activated: test item path = %s" % i.path)
            if (i.path == path):
                i.launch()
                if (i.type == "module"):
                    self.mode = "module-UI"
                    self.module_active(i)
                    self.draw_ui()
                break

    def draw_ui(self):
        pass

    def on_resize_common(self, w, h):
        if (self.mode == "main-UI"):
            logging.debug("on_resize: resize activated")
            self.window_size_w = w
            self.window_size_h = h
            tmp_icons_col = self.icon_view_columns
            self.icon_view_columns_generate()
            if (self.icon_view_columns != tmp_icons_col):
                self.draw_ui()
