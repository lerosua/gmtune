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
        self.init_notebook()

        settings = gtk.settings_get_default()
        settings.props.gtk_button_images=True

    def init_mainwin(self):
        #main window
        self.mainwin = gtk.Window()
        self.mainwin.hided = False
        self.mainwin.connect('destroy',gtk.main_quit)

        #just test ui
        self.all_vbox = gtk.VBox()
        n1_hbox = self.init_top_hbox()
        self.all_vbox.pack_start(n1_hbox,False)
        self.all_hpaned = gtk.HPaned()

        self.all_vbox.pack_start(self.all_hpaned)
        self.mainwin.add(self.all_vbox)

        #main window attribute setting
        self.mainwin.resize(800,600)
        self.mainwin.set_title("GMTune")
        self.mainwin.set_icon(ICON_DICT["gmbox"])

    def init_category_treeview(self):
        category_scrolledwindow = gtk.ScrolledWindow()
        category_scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        category_scrolledwindow.set_size_request(150,600)
        category_treeview = CategoryTreeview(self)
        category_scrolledwindow.add(category_treeview)
        category_scrolledwindow.show_all()
        self.all_hpaned.pack1(category_scrolledwindow)

    def init_notebook(self):
        self.notebook = gtk.Notebook()
        self.music_store_treeview = PlaylistTreeview(self)
        self.notebook.append_page(self.music_store_treeview)
        self.notebook.set_show_tabs(False)
        self.all_hpaned.pack2(self.notebook)

    def init_status_icon(self):
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_pixbuf(ICON_DICT["gmbox"])
        self.status_icon.connect("activate", self.on_status_icon_activate)
        self.status_icon.connect("popup-menu",self.on_status_icon_menu)
        #self.status_icon.set_visible(CONFIG["show_status_icon"])

    def init_top_hbox(self):
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

        self.search_entry = gtk.Entry()
        self.search_entry.set_property("secondary-icon-stock",gtk.STOCK_CLEAR)
        self.search_entry.connect("icon-press", self.search_entry_icon)
        self.search_entry.connect("activate", self.search_entry_do)
        n1_hbox.pack_start(self.search_entry,False)

        return n1_hbox

    def search_entry_icon(self,entry,icon_pos,event):
        self.search_entry.set_text("")

    def search_entry_do(self, entry):
        print "search entry"

    def prev_bt_clicked(self,widget):
        print "prev button clicked"

    def play_bt_clicked(self,widget):
        print "play button clicked"

    def next_bt_clicked(self,widget):
        print "next button clicked"


    def load_music_store(self):
        print "load"
        #just fixme

    def on_status_icon_activate(self, widget, data=None):
        if self.mainwin.hided:
            self.mainwin.show()
        else:
            self.mainwin.hide()
        self.mainwin.hided = not self.mainwin.hided

    def on_status_icon_menu(self,statusicon,button,activate_time):
        popup_menu = gtk.Menu()
        quit_item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quit_item.connect("activate", self.on_quit)
        popup_menu.append(quit_item)
        popup_menu.show_all()
        time = gtk.get_current_event_time()
        popup_menu.popup(None, None, None, 0, time)

    def on_quit(self,win,evt=gtk.gdk.DELETE):
        gtk.main_quit(win)
