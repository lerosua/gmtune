#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
import gtk

class MainWindow(gtk.Window):
    def __init__(self, parent=None):
        gtk.Window.__init__(self)
        self.connect('destroy', gtk.main_quit)
        all_vbox = gtk.VBox()

        n1_hbox = self.create_top_hbox()
        all_vbox.pack_start(n1_hbox,False)

        all_hpaned = gtk.HPaned()

        treeview = gtk.TreeView()
        notebook = gtk.Notebook()
        label = gtk.Label("test")
        notebook.append_page(label)

        all_hpaned.add1(treeview)
        all_hpaned.add2(notebook)

        all_vbox.pack_start(all_hpaned)
        self.add(all_vbox)

        self.set_title('GMTune')
        self.resize(800,600)

    def create_top_hbox(self):
        n1_hbox = gtk.HBox()
        prev_button = gtk.Button("Prev")
        play_button = gtk.Button("Play")
        next_button = gtk.Button("Next")

        prev_button.connect("clicked", self.prev_bt_clicked)
        play_button.connect("clicked", self.play_bt_clicked)
        next_button.connect("clicked", self.next_bt_clicked)
        n1_hbox.pack_start(prev_button,False)
        n1_hbox.pack_start(play_button,False)
        n1_hbox.pack_start(next_button,False)

        timeline = gtk.HScale()
        n1_hbox.pack_start(timeline)

        return n1_hbox

    def prev_bt_clicked(self,widget):
        print "prev button clicked"

    def play_bt_clicked(self,widget):
        print "play button clicked"

    def next_bt_clicked(self,widget):
        print "next button clicked"
