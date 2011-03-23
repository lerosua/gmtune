#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from qmtune import *

def main():
    app = QtGui.QApplication(sys.argv)
    qmtune = QMTune();
    qmtune.mainwin.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
