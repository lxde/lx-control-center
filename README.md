# LX-Control-Center

## Description

lx-control-center is a utility to display and launch system utilies, like configuration programs.

### Application launcher

It parses directories with desktop files to populate the list of applications to display, according to the content of each desktop file :
 - Categories field.
 - OnlyShowIn and NotShowIn fields.
See data/settings.conf for all the configuration possibilities.

### Modules

It also supports extensions with modules, to display directly settings inside lx-control-center window.

You can also run 1 specific module in a standalone mode, by passing -m or --module with the filename of the desktop file of the module (without the .desktop), like -m lxcc-module-test.

Current modules are available on experimental mode :
 - themes-manager: A theme switcher, to apply all the settings of a theme (icon theme, gtk theme, cursor theme ...) - GTK3 frontend only


### Multi - Desktop environment support

 - It can run on any desktop environment which support GTK2 or GTK3 or Qt5 (experimental). You can use the --ui flag to set your prefered frontend.
 - It will save setting based on your current envrionment. If LXDE is detected, it will use lxsession to save the settings. If GNOME environment is detected, it will save using GSettings.


## Run

You can run locally by doing "python lx-control-center", it will detect the better frontend available for your environment.
You can specify the frontend by parsing --ui the_name_of_the_frontend (see below)
There are currently 4 frontends:
 - GTK3 version (--ui GTK3) : the most complete frontend (also the default).
 - GTK2 version (--ui GTK2) : close to the GTK3 version
 - Qt5 version (--ui Qt5) : experimental
 - Webkit - GTK2 version (--ui webkitgtk2) : port of the lxde-ctrl-center - tuquito-control-center

You can also build debian packages by running "dpkg-buildpackage -tc"

To enable debug, pass --log=INFO or --log=DEBUG

To save the output to a file, pass --logfile=the_log_file

To run only 1 module in a standalone mode, pass -m or --module with the filename of the desktop file of the module (without the .desktop), like -m lxcc-module-test.


## Install on Ubuntu / PPA

Packages for Ubuntu are available (temporary) on https://launchpad.net/~gilir/+archive/ubuntu/unstable


## Build / Install

Commands to build and install
 - python setup.py build
 - python setup.py install


## Dependencies

For all versions :
 - python DistUtils and DistUtilsExtra

GTK2 frontend
 - python2
 - pygtk

GTK3 frontend
 - python3
 - pygi
 - GLib GIR
 - GTK3 GIR

Qt5 frontend
 - python3
 - pyqt5

Webkit frontend
 - python2
 - pygtk
 - python-webkit
 - python-json


## Update .pot file

Run "python setup.py build"
