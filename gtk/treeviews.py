#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import *
from core import *
from const import *
import gtk
import gobject

class CategoryTreeview(gtk.TreeView):
    
    class CategoryNode(): 
        
        def __init__(self, name, id, type):   
            self.name = name
            self.id = id
            self.type = type
            self.init_icon()
            
        def init_icon(self):
            if self.type == Song:
                self.icon = ICON_DICT["song"]
            if self.type == Songlist:
                self.icon = ICON_DICT["songlist"]
            if self.type == Directory:
                self.icon = ICON_DICT["directory"]
    
    def __init__(self, gmbox):
        gtk.TreeView.__init__(self)
        self.gmbox = gmbox
        self.init_treestore()
        self.init_column()
        self.init_menu()
        self.set_headers_visible(False)
        self.set_model(self.treestore)
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.connect("button-press-event", self.on_button_press_event)
        self.expand_all()
        
    def init_treestore(self):
        self.treestore = gtk.TreeStore(gobject.TYPE_PYOBJECT)
        

        parent_library = CategoryTreeview.CategoryNode("Library", None, Directory)
        parent_library_iter = self.treestore.append(None, (parent_library,))

        parent_store = CategoryTreeview.CategoryNode("Store", None, Directory)
        parent_store_iter = self.treestore.append(None, (parent_store,))        
        
        for value in LIBRARY_DIR:
                node = CategoryTreeview.CategoryNode(value[0], value[1], Song)
                self.treestore.append(parent_library_iter, (node,))
        for value in STORE_DIR:
                node = CategoryTreeview.CategoryNode(value[0], value[1], Songlist)
                self.treestore.append(parent_store_iter, (node,))
         
        # other
        parent_playlist = CategoryTreeview.CategoryNode("PlayList", None, Directory)
        parent_playlist_iter = self.treestore.append(None, (parent_playlist,))
        for value in PLAYLIST_DIR:
                node = CategoryTreeview.CategoryNode(value[0],value[1], Songlist)
                self.treestore.append(parent_playlist_iter, (node,))
    
    def init_column(self):
        
        def pixbuf_cell_data_func(column, cell, model, iter, data=None):
            category_node = model.get_value(iter, 0)
            cell.set_property("pixbuf", category_node.icon)
            
        def text_cell_data_func(column, cell, model, iter, data=None):
            category_node = model.get_value(iter, 0)
            cell.set_property("text", category_node.name)
        
        renderer = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn("test")
        column.pack_start(renderer, False)
        column.set_cell_data_func(renderer, pixbuf_cell_data_func)
        renderer = gtk.CellRendererText()
        column.pack_start(renderer)
        column.set_cell_data_func(renderer, text_cell_data_func)        
        column.set_resizable(True)      
        self.append_column(column)    
    
    def init_menu(self): 
        self.menu = gtk.Menu()
        self.menuitem = gtk.MenuItem("获取")
        self.menu.append(self.menuitem)
        self.menu.connect("selection-done", self.on_menu_selection_done)
        self.menuitem.connect("activate", self.on_menuitem_activate)
        self.menu.show_all()

    def analyze_and_search(self, node):
        print "just test"
        #if node.id == "tag":
        #    self.gmbox.do_tag(node.name, node.type)
        #elif node.id == "topiclistingdir":
        #    self.gmbox.do_topiclistingdir()
        #elif node.id == "starrecommendationdir":
        #    self.gmbox.do_starrecommendationdir()
        #else: 
        #    # chartlisting
        #    self.gmbox.do_chartlisting(node.name, node.type)
           
    def on_button_press_event(self, widget, event, data=None):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            model, rows = self.get_selection().get_selected_rows()            
            if len(rows) == 0:
                return False    
            for path in rows:
                iter = model.get_iter(path)
                if model.iter_depth(iter) != 0:
                    node = model.get_value(iter, 0)
                    self.analyze_and_search(node)
        elif event.button == 3:
            self.menu.popup(None, None, None, event.button, event.time)
            return True
        
    def on_menu_selection_done(self, widget, data=None):
        self.queue_draw()
        
    def on_menuitem_activate(self, widget, data=None):
        model, rows = self.get_selection().get_selected_rows()
        if len(rows) == 0:
            return
        
        for path in rows:
            iter = model.get_iter(path)
            node = model.get_value(iter, 0)
            self.analyze_and_search(node)
        self.get_selection().unselect_all()  
 
