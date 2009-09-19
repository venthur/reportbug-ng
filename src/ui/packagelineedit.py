import logging

from PyQt4 import QtCore, QtGui
from apt.cache import Cache, FilteredCache, Filter

class InstalledFilter(Filter):
    """ Filter that returns all installed packages """
    def apply(self, pkg):
        return pkg.isInstalled

class PackageLineEdit(QtGui.QLineEdit):
    def __init__(self, parent):
        QtGui.QLineEdit.__init__(self, parent)
        self.logger = logging.getLogger("PackageLineEdit") 
        cache = FilteredCache(Cache())
        cache.setFilter(InstalledFilter())
        self._completer = QtGui.QCompleter(sorted(cache.keys()))
        self._completer.setModelSorting(QtGui.QCompleter.CaseSensitivelySortedModel)
        self.setCompleter(self._completer)
        #QtCore.QObject.connect(self, QtCore.SIGNAL("returnPressed()"), self.__disable_completion)
    
    def __enable_completion(self):
        self.logger.debug("Enabled completion.")
        self.setCompleter(self._completer)
        self.completer().setCompletionPrefix(self.text())
        QtCore.QTimer.singleShot(0, self.completer().complete)

    def __disable_completion(self):
        self.logger.debug("Disabled completion.")
        self.setCompleter(None)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Down:
            QtCore.QTimer.singleShot(0, self.__enable_completion)
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)
