#!/usr/bin/env python

from ui.MyMainWindow import MyMainWindow

import qt
import sys

VERSION = "0.2007.03.08"

if __name__ == "__main__":
    app = qt.QApplication(sys.argv)
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), app, qt.SLOT("quit()"))
    
    mw = MyMainWindow()
    app.setMainWidget(mw)
    mw.setCaption(mw.caption() + "   " + VERSION)
    mw.show()
    app.exec_loop()

