#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import gtk

class MainWindow(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self)
        self.connect('destroy', gtk.main_quit)      

	m_vbox = gtk.VBox()
	self.add(m_vbox)

        self.set_title('GMTune')

