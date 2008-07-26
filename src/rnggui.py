# rnggui.py - MainWindow of Reportbug-NG.
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
import thread

from PyQt4 import QtCore, QtGui

from ui import mainwindow
from ui import submitdialog
import rnghelpers as rng
import debianbts as bts
from rngsettings import RngSettings


class RngGui(QtGui.QMainWindow, mainwindow.Ui_MainWindow):
    
    def __init__(self, args):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        
        self.logger = logging.getLogger("RngGui")
        self.logger.info("Logger initialized.")
        
        # connect toolbuttons to actions
        #self.toolButton_clear.setDefaultAction(self.actionClearLineEdit)

        # connect acionts to methods
        QtCore.QObject.connect(self.actionNewBugreport, QtCore.SIGNAL("triggered()"), self.new_bugreport)
        QtCore.QObject.connect(self.actionAdditionalInfo, QtCore.SIGNAL("triggered()"), self.additional_info)
        QtCore.QObject.connect(self.actionCloseBugreport, QtCore.SIGNAL("triggered()"), self.close_bugreport)
        QtCore.QObject.connect(self.actionNewWnpp, QtCore.SIGNAL("triggered()"), self.new_wnpp)
        QtCore.QObject.connect(self.actionClearLineEdit, QtCore.SIGNAL("triggered()"), self.clear_lineedit)
        QtCore.QObject.connect(self.actionSettings, QtCore.SIGNAL("triggered()"), self.settings)

        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL("textChanged(const QString&)"), self.lineedit_text_changed)
        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL("returnPressed()"), self.lineedit_return_pressed)

        QtCore.QObject.connect(self.tableView, QtCore.SIGNAL("activated(const QModelIndex&)"), self.activated)

        # setup the table
        self.model = TableModel(self)
        #self.proxymodel = QtGui.QSortFilterProxyModel(self)
        self.proxymodel = MySortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.setFilterKeyColumn(-1)
        self.tableView.setModel(self.proxymodel)
        self.tableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        #self.tableView.horizontalHeader().setMovable(True)
        #self.tableView.horizontalHeader().setVisible(True)
        self.tableView.verticalHeader().setVisible(False)

        self.toolBar.insertWidget(self.actionNewBugreport, self.label)
        self.toolBar.insertWidget(self.actionNewBugreport, self.lineEdit)
        self.toolBar.insertAction(self.actionNewBugreport, self.actionClearLineEdit)
        self.toolBar.insertSeparator(self.actionNewBugreport)
        
        self.settings = rng.Settings(rng.Settings.CONFIGFILE)
        self.settings.load()
        self._apply_settings()

        self.webView.setHtml(rng.REPORTBUG_NG_INSTRUCTIONS)
        
        self._stateChanged(None, None)
        
        if args:
            self.lineEdit.setText(unicode(args[0]))
            self.lineedit_return_pressed()

    def closeEvent(self, ce):
        self.logger.info("Catched close event.")
        self._get_settings()
        self.settings.save()
        ce.accept()

    def activated(self, index):
        self.logger.info("Row %s activated." % str(index.row()))
        realrow = self.proxymodel.mapToSource(index).row()
        bugnr = self.model.elements[realrow].nr
        # find the bug in our list, and get the package and nr
        package = None
        for i in self.bugs:
            if i.nr == bugnr:
                self.currentBug = i
                break
            
        self._stateChanged(self.currentBug.package, self.currentBug)
        url = bts.BTS_URL + bugnr
        self._show_url(url)
    
    def new_bugreport(self):
        self.logger.info("New Bugreport.")
        self.__submit_dialog("newbug")
    
    def additional_info(self):
        self.logger.info("Additional Info.")
        self.__submit_dialog("moreinfo")
    
    def close_bugreport(self):
        self.logger.info("Close Bugreport.")
        self.__submit_dialog("close")
    
    def new_wnpp(self):
        self.logger.info("New WNPP.")
        self.__submit_dialog("wnpp")
    
    def clear_lineedit(self):
        self.logger.info("Clear Lineedit.")
        self.lineEdit.clear()
    
    def lineedit_text_changed(self, text):
        self.logger.info("Text changed: %s" % text)
        text = unicode(text)
        self.proxymodel.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString))

    
    def lineedit_return_pressed(self):
        
        #
        # just in case ;)
        #
        text = unicode(self.lineEdit.text())
        if text.startswith("http://"):
            self._show_url(text)
            return
        
        self.logger.info("Return pressed.")
        text = unicode(self.lineEdit.text())
        self.lineEdit.clear()
        query = rng.translate_query(text)
        self.logger.debug("Query: %s" % str(query))
        list = None
        if query[0]:
            list = bts.get_bugs(query)
        else:
            # just a signle bug
            list = [query[1]]
        # change the state
        if query[0] in ("src", "package"):
            self._stateChanged(query[1], None)
        elif query[0] in (None,):
            self._stateChanged(None, query[1])
        else:
            self._stateChanged(None, None)
        self.logger.debug("Buglist matching the query: %s" % str(list))
        self.bugs = bts.get_status(list)
        self.model.set_elements(self.bugs)
        self.tableView.resizeRowsToContents()
        
    
    def settings(self):
        s = RngSettings(self.settings)
        if s.exec_() != s.Accepted:
            self.settings = s.settings


    def _stateChanged(self, package, bug):
        """Transition for our finite state machine logic"""
        if package:
            self.currentPackage = package
            self.actionNewBugreport.setEnabled(1)
        else:
            self.currentPackage = ""
            self.actionNewBugreport.setEnabled(0)
        
        if bug:
            self.currentBug = bug
            self.actionAdditionalInfo.setEnabled(1)
            self.actionCloseBugreport.setEnabled(1)
        else:
            self.currentBug = bts.Bugreport(0)
            self.actionAdditionalInfo.setEnabled(0)
            self.actionCloseBugreport.setEnabled(0)
        
    def __submit_dialog(self, type):
        
#        dialog = submitdialog.Ui_SubmitDialog()
#        dialog.setupUi()
        dialog = SubmitDialog()
        
        if type == 'wnpp':
            dialog.wnpp_groupBox.setEnabled(1)
            dialog.wnpp_groupBox.setChecked(1)
            package = self.currentPackage
            to = "submit@bugs.debian.org"
        elif type == 'newbug':
            dialog.wnpp_groupBox.setEnabled(1)
            dialog.wnpp_groupBox.setChecked(0)
            package = self.currentPackage
            to = "submit@bugs.debian.org"
        elif type == 'moreinfo':
            dialog.wnpp_groupBox.setEnabled(0)
            dialog.comboBoxSeverity.setEnabled(0)
            dialog.checkBoxSecurity.setEnabled(0)
            dialog.checkBoxPatch.setEnabled(0)
            dialog.checkBoxL10n.setEnabled(0)
            package = self.currentBug.package
            to = "%s@bugs.debian.org" % self.currentBug.nr
        elif type == 'close':
            dialog.wnpp_groupBox.setEnabled(0)
            dialog.comboBoxSeverity.setEnabled(0)
            dialog.checkBoxSecurity.setEnabled(0)
            dialog.checkBoxPatch.setEnabled(0)
            dialog.checkBoxL10n.setEnabled(0)
            dialog.lineEditSummary.setText("Done: %s" % self.currentBug.summary)
            package = self.currentBug.package
            to = "%s-done@bugs.debian.org" % self.currentBug.nr
        else:
            logger.critical("Received unknown submit dialog type!")
        
        version = rng.getInstalledPackageVersion(package)
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        for action in rng.WNPP_ACTIONS:
            dialog.wnpp_comboBox.addItem(action)
        for mua in rng.SUPPORTED_MUA:
            dialog.comboBoxMUA.addItem(mua.title())
        if self.settings.lastmua in rng.SUPPORTED_MUA:
            dialog.comboBoxMUA.setCurrentIndex(rng.SUPPORTED_MUA.index(self.settings.lastmua))
        for sev in rng.SEVERITY:
            dialog.comboBoxSeverity.addItem(sev)
        # Set default severity to 'normal'
        dialog.comboBoxSeverity.setCurrentIndex(4)
        dialog.comboBoxSeverity.setWhatsThis(rng.SEVERITY_EXPLANATION)
        
        # Run the dialog
        if dialog.exec_() == dialog.Accepted:
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            severity = unicode(dialog.comboBoxSeverity.currentText()).lower()
            tags = []
            cc = []
            if dialog.checkBoxL10n.isChecked():
                tags.append("l10n")
            if dialog.checkBoxPatch.isChecked():
                tags.append("patch")
            if dialog.checkBoxSecurity.isChecked():
                tags.append("security")
                cc.append("secure-testing-team@lists.alioth.debian.org")
            mua = unicode(dialog.comboBoxMUA.currentText()).lower()
            self.settings.lastmua = mua

            body, subject = '', ''
            # WNPP Bugreport
            if dialog.wnpp_comboBox.isEnabled():
                action = dialog.wnpp_comboBox.currentText()
                descr = dialog.wnpp_lineEdit.text()
                body = rng.prepare_wnpp_body(action, package, version)
                subject = rng.prepare_wnpp_subject(action, package, descr)
            # Closing a bug
            elif type == 'close':
                severity = ""
                subject = unicode(dialog.lineEditSummary.text())
                body = rng.prepare_minimal_body(package, version, severity, tags, cc)
            # New or moreinfo
            else:
                if type == 'moreinfo':
                    severity = ""
                subject = unicode("[%s] %s" % (package, dialog.lineEditSummary.text()))
                body = rng.prepareBody(package, version, severity, tags, cc)

            if len(subject) == 0:
                subject = "Please enter a subject before submitting the report."
            
            thread.start_new_thread( rng.prepareMail, (mua, to, subject, body) )
            
            
    def _apply_settings(self):

        self.resize(self.settings.width, self.settings.height)
        self.move(self.settings.x, self.settings.y)
        #self.reportbug_ngMenubarAction.setOn(self.settings.menubar)
        self.tableView.horizontalHeader().resizeSection(0, self.settings.bugnrWidth)
        self.tableView.horizontalHeader().resizeSection(1, self.settings.summaryWidth)
        self.tableView.horizontalHeader().resizeSection(2, self.settings.statusWidth)
        self.tableView.horizontalHeader().resizeSection(3, self.settings.severityWidth)
        self.tableView.horizontalHeader().resizeSection(4, self.settings.lastactionWidth)
#           self.listView.setSorting(self.settings.sortByCol, self.settings.sortAsc)

    def _get_settings(self):
        p = self.pos()
        s = self.size()
        self.settings.x = p.x()
        self.settings.y = p.y()
        self.settings.width = s.width()
        self.settings.height = s.height()
        #self.settings.menubar = self.reportbug_ngMenubarAction.isOn()
        #self.settings.sortByCol = self.tableView.sortColumn()
        #self.settings.sortAsc = {Qt.Ascending : True, 
        #                         Qt.Descending : False}[self.listView.sortOrder()]
        self.settings.bugnrWidth = self.tableView.columnWidth(0)
        self.settings.summaryWidth = self.tableView.columnWidth(1)
        self.settings.statusWidth = self.tableView.columnWidth(2)
        self.settings.severityWidth = self.tableView.columnWidth(3)
        self.settings.lastactionWidth = self.tableView.columnWidth(4)
        
    def _show_url(self, url):
        url = QtCore.QUrl(url)
        self.webView.setUrl(url)
        


class TableModel(QtCore.QAbstractTableModel):
    
    def __init__(self, parent = None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.logger = logging.getLogger("TableModel")
        self.elements = []
    
    def rowCount(self, parent):
        return len(self.elements)
    
    def columnCount(self, parent):
        return 5

    #
    # DAMMIT DONT IGNORE THE DISPLAY ROLE!!
    #
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.ForegroundRole:
            severity = self.elements[index.row()].severity.lower()
            status = self.elements[index.row()].status.lower()
            c = QtCore.Qt.black
            if severity == "grave":
                c = self.parent.settings.c_grave
            elif severity == "serious":
                c = self.parent.settings.c_serious
            elif severity == "critical":
                c = self.parent.settings.c_critical
            elif severity == "important":
                c = self.parent.settings.c_important
            elif severity == "minor":
                c = self.parent.settings.c_minor
            elif severity == "wishlist":
                c = self.parent.settings.c_wishlist
            if status == "resolved":
                c = self.parent.settings.c_resolved
            return QtCore.QVariant(QtGui.QColor(c))
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        bug = self.elements[index.row()]
        data = {0 : bug.nr,
                1 : bug.summary,
                2 : bug.status,
                3 : bug.severity,
                4 : bug.lastaction}[index.column()]
        return QtCore.QVariant(data)

    #
    # DAMMIT DONT IGNORE THE DISPLAY ROLE!!
    #
    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        if orientation == QtCore.Qt.Horizontal:
            txt = {0 : "Bugnumber",
                1 : "Summary",
                2 : "Status",
                3 : "Severity",
                4 : "Last Action"}[section]
            return QtCore.QVariant(txt)
        else:
            return QtCore.QVariant()
        

    def set_elements(self, entries):
        self.logger.info("Setting Elements.")
        self.beginInsertRows(QtCore.QModelIndex(), 0, len(entries))
        self.elements = entries
        self.endInsertRows()
        self.emit(QtCore.SIGNAL("layoutChanged()"))


class MySortFilterProxyModel(QtGui.QSortFilterProxyModel):
    
    def __init__(self, parent = None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)
        
    def lessThan(self, left, right):
        if left.column() != 3:
            return QtGui.QSortFilterProxyModel.lessThan(self, left, right)
        l = left.row()
        r = right.row()
        return self.sourceModel().elements[l].value() < self.sourceModel().elements[r].value()

class SubmitDialog(QtGui.QDialog, submitdialog.Ui_SubmitDialog):
    
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
