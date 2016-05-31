# rngsettings.py - SettingsDialog of Reportbug-NG.
# Copyright (C) 2007-2014  Bastian Venthur
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import logging
import copy

from PyQt5 import QtCore, QtWidgets, QtGui

from ui import settings
import rnghelpers as rng
from rnghelpers import Settings, getMUAString

class RngSettingsDialog(QtWidgets.QDialog, settings.Ui_Dialog):

    def __init__(self, settings):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)

        self.logger = logging.getLogger("Settings")
        self.logger.info("Logger initialized.")

        self.settings = copy.deepcopy(settings)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.RestoreDefaults).clicked.connect(self.load_default)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self.pushButton_wishlist.clicked.connect(self._change_wishlist_color)
        self.pushButton_minor.clicked.connect(self._change_minor_color)
        self.pushButton_normal.clicked.connect(self._change_normal_color)
        self.pushButton_important.clicked.connect(self._change_important_color)
        self.pushButton_serious.clicked.connect(self._change_serious_color)
        self.pushButton_grave.clicked.connect(self._change_grave_color)
        self.pushButton_critical.clicked.connect(self._change_critical_color)
        self.pushButton_resolved.clicked.connect(self._change_resolved_color)
        self.checkBox_presubj.stateChanged.connect(self._presubj_changed)
        self.checkBox_script.stateChanged.connect(self._script_changed)
        self.comboBox_mua.activated.connect(self._mua_changed)

        self.load_settings()


    def load_settings(self):

        # mua
        for mua in rng.SUPPORTED_MUA:
            self.comboBox_mua.addItem(rng.getMUAString(mua))
        if self.settings.lastmua in rng.SUPPORTED_MUA:
            self.comboBox_mua.setCurrentIndex(rng.SUPPORTED_MUA.index(self.settings.lastmua))

        # colors
        buttoncolor = [(self.pushButton_wishlist, self.settings.c_wishlist),
                       (self.pushButton_minor, self.settings.c_minor),
                       (self.pushButton_normal, self.settings.c_normal),
                       (self.pushButton_important, self.settings.c_important),
                       (self.pushButton_serious, self.settings.c_serious),
                       (self.pushButton_grave, self.settings.c_grave),
                       (self.pushButton_critical, self.settings.c_critical),
                       (self.pushButton_resolved, self.settings.c_resolved)]
        for button, color in buttoncolor:
            self._change_button_color(button, color)

        # the rest
        self.checkBox_script.setChecked(self.settings.script)
        self.checkBox_presubj.setChecked(self.settings.presubj)


    def load_default(self):
        self.settings.load_defaults()
        self.load_settings()

    def _change_button_color(self, button, color):
        button.setStyleSheet("background-color: %s; color: %s" % (color, color))


    def _change_wishlist_color(self):
        self.settings.c_wishlist = self._get_color(self.settings.c_wishlist)
        self._change_button_color(self.pushButton_wishlist, self.settings.c_wishlist)

    def _change_minor_color(self):
        self.settings.c_minor = self._get_color(self.settings.c_minor)
        self._change_button_color(self.pushButton_minor, self.settings.c_minor)

    def _change_normal_color(self):
        self.settings.c_normal = self._get_color(self.settings.c_normal)
        self._change_button_color(self.pushButton_normal, self.settings.c_normal)

    def _change_important_color(self):
        self.settings.c_important = self._get_color(self.settings.c_important)
        self._change_button_color(self.pushButton_important, self.settings.c_important)

    def _change_serious_color(self):
        self.settings.c_serious = self._get_color(self.settings.c_serious)
        self._change_button_color(self.pushButton_serious, self.settings.c_serious)

    def _change_grave_color(self):
        self.settings.c_grave = self._get_color(self.settings.c_grave)
        self._change_button_color(self.pushButton_grave, self.settings.c_grave)

    def _change_critical_color(self):
        self.settings.c_critical = self._get_color(self.settings.c_critical)
        self._change_button_color(self.pushButton_critical, self.settings.c_critical)

    def _change_resolved_color(self):
        self.settings.c_resolved = self._get_color(self.settings.c_resolved)
        self._change_button_color(self.pushButton_resolved, self.settings.c_resolved)

    def _get_color(self, color):
        return str(QtWidgets.QColorDialog.getColor(QtGui.QColor(color)).name())

    def _presubj_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.settings.presubj = True
        else:
            self.settings.presubj = False

    def _script_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.settings.script = True
        else:
            self.settings.script = False

    def _mua_changed(self, index):
        mua = unicode(self.comboBox_mua.currentText())
        # translate back
        found = False
        for mua_orig in rng.MUA_SYNTAX.keys():
            if getMUAString(mua_orig) == mua:
                self.settings.lastmua = mua_orig
                found = True
                self.logger.debug("Found match for MUA: %s %s" % (mua, mua_orig))
                break
        if not found:
            self.logger.error("Mua not found: %s" % mua)

