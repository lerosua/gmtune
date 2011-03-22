#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from mainwindow import *

def main():
    app = QtGui.QApplication(sys.argv)
    win = MainWindow();
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
