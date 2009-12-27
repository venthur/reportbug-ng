# rngsettings.py - SettingsDialog of Reportbug-NG.
# Copyright (C) 2007-2008  Bastian Venthur
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

from PyQt4 import QtCore, QtGui

from ui import settings
import rnghelpers as rng
from rnghelpers import Settings, getMUAString

class RngSettingsDialog(QtGui.QDialog, settings.Ui_Dialog):
    
    def __init__(self, settings):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        
        self.logger = logging.getLogger("Settings")
        self.logger.info("Logger initialized.")
        
        self.settings = copy.deepcopy(settings)

        QtCore.QObject.connect(self.buttonBox.button(QtGui.QDialogButtonBox.RestoreDefaults), QtCore.SIGNAL("clicked()"), self.load_default)
        QtCore.QObject.connect(self.buttonBox.button(QtGui.QDialogButtonBox.Ok), QtCore.SIGNAL("clicked()"), self.accept)
        QtCore.QObject.connect(self.buttonBox.button(QtGui.QDialogButtonBox.Cancel), QtCore.SIGNAL("clicked()"), self.reject)
        QtCore.QObject.connect(self.pushButton_wishlist, QtCore.SIGNAL("clicked()"), self._change_wishlist_color)
        QtCore.QObject.connect(self.pushButton_minor, QtCore.SIGNAL("clicked()"), self._change_minor_color)
        QtCore.QObject.connect(self.pushButton_normal, QtCore.SIGNAL("clicked()"), self._change_normal_color)
        QtCore.QObject.connect(self.pushButton_important, QtCore.SIGNAL("clicked()"), self._change_important_color)
        QtCore.QObject.connect(self.pushButton_serious, QtCore.SIGNAL("clicked()"), self._change_serious_color)
        QtCore.QObject.connect(self.pushButton_grave, QtCore.SIGNAL("clicked()"), self._change_grave_color)
        QtCore.QObject.connect(self.pushButton_critical, QtCore.SIGNAL("clicked()"), self._change_critical_color)
        QtCore.QObject.connect(self.pushButton_resolved, QtCore.SIGNAL("clicked()"), self._change_resolved_color)
        QtCore.QObject.connect(self.checkBox_presubj, QtCore.SIGNAL("stateChanged(int)"), self._presubj_changed)
        QtCore.QObject.connect(self.checkBox_script, QtCore.SIGNAL("stateChanged(int)"), self._script_changed)
        QtCore.QObject.connect(self.comboBox_mua, QtCore.SIGNAL("activated(int)"), self._mua_changed)

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
        return str(QtGui.QColorDialog.getColor(QtGui.QColor(color)).name())
        
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

