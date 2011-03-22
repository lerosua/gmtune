#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from mainwindow import *

def main():
    win = MainWindow();
    win.show_all()
    gtk.main()


if __name__ == '__main__':
    main()
