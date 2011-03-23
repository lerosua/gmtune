#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import gtk
import platform
import glib

def get_module_path():
    if hasattr(sys, "frozen"):
        module_path = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))
    else:
        module_path = os.path.dirname(unicode(os.path.abspath(__file__), sys.getfilesystemencoding()))
    return module_path

MODULE_PATH = get_module_path()

def create_icon_dict():
    icon_names = ["gmbox", "song", "songlist", "directory", "refresh", "info"]
    icon_dict = {}
    for name in icon_names:
        icon_path = "%s/pixbufs/%s.png" % (MODULE_PATH, name)
        icon = gtk.gdk.pixbuf_new_from_file(icon_path)
        icon_dict[name] = icon
    return icon_dict

ICON_DICT = create_icon_dict()


