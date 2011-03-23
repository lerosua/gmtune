#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os,sys
import locale
from PyQt4 import QtCore,QtGui

def dbg(s):
    print (u'GMTune  %s' %s).encode(locale.getlocale()[1])

class QMTune():
    def __init__(self):
        self.init_mainwin()
        self.init_tray_icon()



    def tr(self,msg):
        return QtCore.QCoreApplication.translate("@default",msg)

    def init_mainwin(self):
        self.mainwin = QtGui.QMainWindow()
        self.mainwin.hided = False
        self.mainwin.setWindowIcon( QtGui.QIcon("../gtk/pixbufs/gmbox.png"))
        self.mainwin.resize(800,600)
        #self.mainwin.setTitle("QMTune - 0.1")

    def init_tray_icon(self):
        self.tray_icon = QtGui.QSystemTrayIcon(QtGui.QIcon("../gtk/pixbufs/gmbox.png"), None)
        menu = QtGui.QMenu(self.mainwin)
        exitAction = menu.addAction(self.tr("Exit"))
        QtCore.QObject.connect(exitAction, QtCore.SIGNAL("triggered()"), sys.exit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("GMTune")
        self.tray_icon.activated.connect(self.on_tray_icon_activate)
        self.tray_icon.show()

    def on_tray_icon_activate(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            if self.mainwin.hided:
                self.mainwin.show()
            else:
                self.mainwin.hide()
            self.mainwin.hided = not self.mainwin.hided
