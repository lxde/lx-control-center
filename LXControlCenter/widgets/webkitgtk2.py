#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Based on tuquito-control-center: https://github.com/tuquito/tuquito-control-center
 by Mario Colque <mario@tocuito.org.ar>
 
 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; version 3 of the License.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
"""
import pygtk
pygtk.require('2.0')
import gtk

import webkit
import string
import json
import sys

import gettext
_ = gettext.gettext

import logging

import os

from .common import UI

class WebkitApp(UI):
    def __init__(self):
        UI.__init__(self)
        self.share_path = os.path.join('data/webkit')
        self.define_paths()

        self.builder = gtk.Builder()
        self.builder.add_from_file(os.path.join(self.share_path, 'control-center.glade'))
        self.window = self.builder.get_object('window')
        self.builder.get_object('window').set_title(_('LXDE Control Center'))
        self.edit_handler_id = False
        self.add_handler_id = False
        self.items_cache = []
        self.items_advanced_cache = []
        self.theme = gtk.icon_theme_get_default()

        # Text mapping
        self.text = {}

        # The list of categories is fixed and hardcoded in js files.
        self.categories_fixed = True
        self.categories_triaged.clear()
        self.categories_keys.clear()

        self.categories_keys = {    "x0001x":("DesktopSettings"),
                                    "x0002x":("Network", "X-GNOME-NetworkSettings"),
                                    "x0003x":("PackageManager"),
                                    "x0004x":("Users"),
                                    "x0005x":("Security", "TerminalEmulator", "FileManager","FileTools","Filesystem", "Monitor", "Accessibility", "Other"),
                                    "x0006x":("HardwareSettings", "Printing")
                                }
        self.categories_triaged_generate()       

        self.generate_view()

        self.print_debug()

        self.read_strings(self)

        # Define treeview
        self.treeview_items = self.builder.get_object('treeview_items')
        self.column1 = gtk.TreeViewColumn(_('Item'), gtk.CellRendererText(), text=0)
        self.column1.set_sort_column_id(0)
        self.column1.set_resizable(True)
        self.column2 = gtk.TreeViewColumn(_('Command'), gtk.CellRendererText(), text=1)
        self.column2.set_sort_column_id(1)
        self.column2.set_resizable(True)
        self.treeview_items.append_column(self.column1)
        self.treeview_items.append_column(self.column2)
        self.treeview_items.set_headers_clickable(True)
        self.treeview_items.set_reorderable(False)
        self.treeview_items.show()

        self.builder.get_object('window').connect('destroy', gtk.main_quit)
        self.browser = webkit.WebView()
        self.builder.get_object('window').add(self.browser)
        self.browser.connect('button-press-event', lambda w, e: e.button == 3)

        self.set_options_status()

        if (self.view_mode == "icons-all"):
            self.load_advanced()

        template = self.get_template()
        html = string.Template(template).safe_substitute(self.text)
        self.browser.load_html_string(html, "file://%s/" % self.html_path)
        self.browser.connect('title-changed', self.title_changed)

        self.window.show_all()

    def get_template(self):
        if (self.view_visual_effects == True and self.view_mode == "icons-categories"):
            template_file = os.path.join(self.html_path, 'frontend/default.html')
        elif (self.view_visual_effects == False and self.view_mode == "icons-categories"):
            template_file = os.path.join(self.html_path, 'frontend/default-faster.html')
        elif (self.view_visual_effects == True and self.view_mode == "icons-all"):
            template_file = os.path.join(self.html_path, 'frontend/advanced.html')
        else:
            template_file = os.path.join(self.html_path, 'frontend/advanced-faster.html')
        with open(template_file, 'r') as f:
            template = f.read()
        return template

    def read_strings(self, widget):
        self.string_file = os.path.join(self.share_path, 'strings/y0001y')
        if os.path.isfile(self.string_file):
            with open(self.string_file, 'r') as string_file:
                string = json.load(string_file)
        for k in string:
           self.text = {}
           self.text['x0001x'] = _(string['x0001x'])
           self.text['x0002x'] = _(string['x0002x'])
           self.text['x0003x'] = _(string['x0003x'])
           self.text['x0004x'] = _(string['x0004x'])
           self.text['x0005x'] = _(string['x0005x'])
           self.text['x0006x'] = _(string['x0006x'])
           self.text['x0007x'] = _(string['x0007x'])
           self.text['x0008x'] = _(string['x0008x'])
           self.text['x0009x'] = _(string['x0009x'])
           self.text['x0010x'] = _(string['x0010x'])
           self.text['x0011x'] = _(string['x0011x'])
           self.text['x0012x'] = _(string['x0012x'])
           self.text['x0013x'] = _(string['x0013x'])
           self.text['x0014x'] = _(string['x0014x'])
           self.text['x0015x'] = _(string['x0015x'])
           self.text['x0016x'] = _(string['x0016x'])
           self.text['x0017x'] = _(string['x0017x'])
           self.text['x0018x'] = _(string['x0018x'])
           self.text['x0019x'] = _(string['x0019x'])
           self.text['x0020x'] = _(string['x0020x'])
           self.text['x0021x'] = _(string['x0021x'])
           self.text['x0022x'] = _(string['x0022x'])
           self.text['x0023x'] = _(string['x0023x'])
           self.text['x0024x'] = _(string['x0024x'])
           self.text['back'] = _('Back to menu')
           self.text['options'] = _('Options')
           self.text['mode'] = _('Mode')
           self.text['advanced_mode'] = _('Advanced mode')
           self.text['normal_mode'] = _('Normal mode')
           self.text['visual'] = _('Visual effects')
           self.text['nice'] = _('Use visual effects (slower)')
           self.text['note_visual'] = _('If you want better performance (faster), disable visual effects.')
           self.text['apply'] = _('Apply')
           self.text['edit_items'] = _('Edit items')

    def set_options_status(self):
        if (self.view_mode == "icons-categories"):
            self.text['input_mode_id'] = 'checked="checked"'
            self.text['input_mode'] = ''
        else:
            self.text['input_mode_id'] = ''
            self.text['input_mode'] = 'checked="checked"'
        if (self.view_visual_effects == True):
            self.text['input_visual'] = 'checked="checked"'
        else:
            self.text['input_visual'] = ''

    def title_changed(self, view, frame, title):
        """Item clicked"""
        self.current_commands = []
        if title.startswith('exec:'):
            command = title.split(':', 1)[1]
            for item in self.items_visible:
                if (item.path  == command):
                    item.launch()
        # TODO show an error message if it's not launched           
        elif title.startswith('category:'):
            category = title.split(':')[1]
            for item in self.items_visible:
                try:
                    if (self.categories_triaged[item.category] == category):
                        command = item.path
                        title = item.name
                        owner = "user"
                        icon = item.icon
                        icon_theme = self.theme
                        if (len(item.icon) > 0):
                            if (self.icon_not_theme_allow == True):
                                if (item.icon[0] == "/"):
                                    icon = item.icon
                                else:
                                    icon_info = icon_theme.lookup_icon(self.icon_fallback, 32, 0)
                            else:
                                try:
                                    icon_info = icon_theme.lookup_icon(item.icon, 32, 0)
                                    icon = icon_info.get_filename()
                                except:
                                    logging.info("title_changed: error when loading icon from %s" % item.path)

                        self.browser.execute_script("addItem('%s','%s','%s','%s')" % (title, command, category, icon))
                        self.browser.execute_script("setContent('" + category + "')")
                except KeyError as e:
                    logging.error("title_changed: error on loading %s with error %s" % (item.path, e))
# TODO To Implement
#        elif title == 'edit-item':
#            self.items_window(self)
        elif title.startswith('save-options:'):
            self.mode = title.split(':')[1]
            if (self.mode == "false"):
                self.view_mode = "icons-all"
            elif (self.mode == False):
                self.view_mode = "icons-all"
            elif (self.mode == "true"):
                self.view_mode = "icons-categories"
            elif (self.mode == True):
                self.view_mode = "icons-categories"

            self.view_visual_effects = title.split(':')[2]

            if (self.view_visual_effects == "false"):
                self.view_visual_effects = False
            elif (self.view_visual_effects == "true"):
                self.view_visual_effects = True

            print("self.view_mode: %s" % self.view_mode)
            print("self.mode: %s" % self.mode)
            print("self.view_visual_effects: %s" % self.view_visual_effects)

            self.save_settings()
            self.change_skin(self)

    def load_advanced(self):
        li_content = []
        self.category = 'advanced'
        for item in self.items_visible:
            command = item.path
            title = item.name
            owner = "user"
            icon = item.icon
            icon_theme = self.theme
            if (len(item.icon) > 0):
                if (self.icon_not_theme_allow == True):
                    if (item.icon[0] == "/"):
                        icon = item.icon
                    else:
                        icon_info = icon_theme.lookup_icon(self.icon_fallback, 32, 0)
                else:
                    try:
                        icon_info = icon_theme.lookup_icon(item.icon, 32, 0)
                        icon = icon_info.get_filename()
                    except:
                        logging.info("title_changed: error when loading icon from %s" % item.path)
            content = "<li id='" + command + "' onclick='javascript:changeTitle(\"exec:" + command + "\")' class='item' style='background-image: url(" + icon + ")'>" + _(title) + "</li>"
            li_content.append(content)
        self.text['li_content'] = '\n'.join(li_content)

    def change_skin(self, widget):
        # TODO make a draw_ui function
        self.set_options_status()
        template = self.get_template()
        if not self.mode:
            self.load_advanced()
        html = string.Template(template).safe_substitute(self.text)
        self.browser.load_html_string(html, "file://%s/" % self.html_path)

    def define_paths(self):
        # TODO dynamicly define path for ressources
        self.share_path = os.path.join('data','webkit')
        self.html_path = os.path.join(os.getcwd(), 'data', 'webkit')

    def main(self):
        gtk.gdk.threads_init()
        gtk.main()
