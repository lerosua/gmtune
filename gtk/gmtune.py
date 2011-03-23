#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
from treeviews import *
import os,sys
import gtk

class GMTune():
    def __init__(self):

        self.init_mainwin()
        self.init_status_icon()
        self.init_category_treeview()

        settings = gtk.settings_get_default()
        settings.props.gtk_button_images=True

    def init_mainwin(self):
        #main window
        self.mainwin = gtk.Window()
        self.mainwin.hided = False
        #self.mainwin.connect('destory',gtk.main_quit)

        #just test ui
        self.all_vbox = gtk.VBox()
        n1_hbox = self.create_top_hbox()
        self.all_vbox.pack_start(n1_hbox,False)
        all_hpaned = gtk.HPaned()

        self.category_scrolledwindow = gtk.ScrolledWindow()
        self.category_scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.category_scrolledwindow.set_size_request(150,600)

        notebook = gtk.Notebook()
        label = gtk.Label("test")
        notebook.append_page(label)
        notebook.set_show_tabs(False)

        all_hpaned.pack1(self.category_scrolledwindow)
        all_hpaned.pack2(notebook)

        self.all_vbox.pack_start(all_hpaned)
        self.mainwin.add(self.all_vbox)

        #main window attribute setting
        self.mainwin.resize(800,600)
        self.mainwin.set_title("GMTune - 0.1")
        self.mainwin.set_icon(ICON_DICT["gmbox"])
        #self.mainwin.show_all()

    def init_category_treeview(self):
        category_treeview = CategoryTreeview(self)
        self.category_scrolledwindow.add(category_treeview)
        self.category_scrolledwindow.show_all()

    def init_status_icon(self):
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_pixbuf(ICON_DICT["gmbox"])
        self.status_icon.connect("activate", self.on_status_icon_activate)
        #self.status_icon.set_visible(CONFIG["show_status_icon"])

    def create_top_hbox(self):
        n1_hbox = gtk.HBox()
        prev_button = gtk.Button(stock=gtk.STOCK_MEDIA_PREVIOUS)
        play_button = gtk.Button(stock=gtk.STOCK_MEDIA_PLAY)
        next_button = gtk.Button(stock=gtk.STOCK_MEDIA_NEXT)

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


    def on_status_icon_activate(self, widget, data=None):
        if self.mainwin.hided:
            self.mainwin.show()
        else:
            self.mainwin.hide()
        self.mainwin.hided = not self.mainwin.hided
