import logging

from PyQt5 import QtCore, QtWidgets
from apt.cache import Cache, FilteredCache, Filter

class InstalledFilter(Filter):
    """ Filter that returns all installed packages """
    def apply(self, pkg):
        return pkg.is_installed

class PackageLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.logger = logging.getLogger("PackageLineEdit")
        cache = FilteredCache(Cache())
        cache.set_filter(InstalledFilter())
        self._completer = QtWidgets.QCompleter(sorted(cache.keys()))
        self._completer.setModelSorting(QtWidgets.QCompleter.CaseSensitivelySortedModel)
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
            QtWidgets.QLineEdit.keyPressEvent(self, event)
