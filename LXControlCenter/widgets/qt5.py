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

import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import logging

from ..base import Base

class Qt5App(Base):
    def __init__(self):
        Base.__init__(self)

    def clean_main_view(self):
        for children in self.grid.children():
            self.grid.removeItem(children)

    def draw_ui(self):
        if (self.mode == "main-UI"):
            self.build_icon_view()

    def build_icon_view(self):
        self.clean_main_view()
        # Generate the view again, to take the modifications of edit_view
        self.generate_view()
        self.build_generic_icon_view("visible")

    def build_generic_icon_view(self, type_view):
        items_to_draw = self.items_visible_by_categories

        if (type_view == "all"):
            items_to_draw = self.items_by_categories

        row = 0
        for category in items_to_draw:
            groupBox = QGroupBox(category)
            groupGrid = QGridLayout()
            groupGrid.setAlignment(Qt.AlignCenter)
            groupBox.setLayout(groupGrid)
            self.grid.addWidget(groupBox, row, 0)
            row = row + 1
            groupCol = 0
            groupRow = 0
# Need Qt 5.7 https://woboq.com/blog/qicon-reads-gtk-icon-cache-in-qt57.html
            for i in items_to_draw[category]:
                if (i.icon_type == "fix"):
                    pixbuf = QIcon(i.icon)
                elif (i.icon_type == "themed"):
                    pixbuf = QIcon.fromTheme(i.icon, QIcon.fromTheme(self.icon_fallback))
                else:
                    pixbuf = QIcon.fromTheme(self.icon_fallback)

                # Add icon button
                image = QToolButton()
                image.setIcon(pixbuf)
                image.setIconSize(QSize(self.icon_view_icons_size, self.icon_view_icons_size))

                # Add text for icon
                text = QLabel()
                text.setText(i.name)
                text.setWordWrap(True)
                text.setAlignment(Qt.AlignCenter)

                if (groupCol > self.icon_view_columns):
                    groupCol = 0
                    groupRow = groupRow + 1

                iconview = QWidget()
                vbox = QVBoxLayout()
                vbox.addWidget(image, Qt.AlignCenter, Qt.AlignCenter)
                vbox.addWidget(text, Qt.AlignCenter, Qt.AlignCenter)
                iconview.setLayout(vbox)

                groupGrid.addWidget(iconview, groupRow, groupCol, Qt.AlignLeft, Qt.AlignLeft)
                groupCol = groupCol + 1

        self.window.show()

    def main(self):
        self.app = QApplication(sys.argv)

        # Main WIndow
        self.window = QWidget()
        self.layout = QVBoxLayout(self.window)
        self.scroll = QScrollArea()
        self.window.setWindowTitle(self.window_title)
        self.window.setWindowIcon(QIcon.fromTheme(self.window_icon))
        self.window.resize(self.window_size_w, self.window_size_h)

        # Content UI
        self.widget = QWidget()
        self.grid = QGridLayout()
        self.vbox1 = QVBoxLayout()
        self.vbox1.addLayout(self.grid)
        self.widget.setLayout(self.vbox1)
        self.widget.show()

        #Function to launch at startup
        self.init()
        self.generate_view()
        self.draw_ui()

        # Add content Widget to ScrollArea, and ScrollArea to window layout
        self.scroll.setWidget(self.widget)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll) 
        self.window.show()

        sys.exit(self.app.exec_())

    def on_item_activated(self,item):
          QMessageBox.information(self, "ListWidget", "You clicked: "+item.text())
