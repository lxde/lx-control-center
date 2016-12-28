# LX-Control-Center

## Description

 * lx-control-center is a utility to display and launch system utilies, like configuration programs.
 * It parses directories with desktop files to populate the list of applications to display, according to the content of each desktop file :
  - Categories field.
  - OnlyShowIn and NotShowIn fields.
 * It also supports extensions with modules, to display directly settings inside lx-control-center window.
 * It is desktop agnostic :
  - It can run on any desktop environment which support GTK2 or GTK3 or Qt5 (experimental).
  - The lists of applications available is adapted to the current desktop environment.
 * See data/settings.conf for all the configuration possibilities.

## Run

 * You can run locally by doing : 
  - python lx-control-center-gtk2 or python lx-control-center-gtk3
 * To enable debug, pass --log=INFO or --log=DEBUG
 * To save the output to a file, pass -logfile=the_log_file

## Build / Install

 * Commands to build and install
  - python setup.py build
  - python setup.py install

## Dependencies

 * For all versions :
  - python DistUtils and DistUtilsExtra

 * GTK2 version (lx-control-center-gtk2)
  - python2
  - pygtk

 * GTK3 version (lx-control-center-gtk3)
  - python3
  - pygi
  - GLib GIR
  - GTK3 GIR

 * Qt5 version (lx-control-center-qt5)
  - python3
  - pyqt5

## Update .pot file

 *  Run "python setup.py build"
