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
from rngsettingsdialog import RngSettingsDialog
import bug


class RngGui(QtGui.QMainWindow, mainwindow.Ui_MainWindow):

    def __init__(self, args):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.logger = logging.getLogger("RngGui")
        self.logger.info("Logger initialized.")

        # Since this is not possible withon qtcreator
        self.toolButton.setDefaultAction(self.actionClearLineEdit)

        # connect actions to methods
        QtCore.QObject.connect(self.actionNewBugreport,
                               QtCore.SIGNAL("triggered()"),
                               self.new_bugreport)
        QtCore.QObject.connect(self.actionAdditionalInfo,
                               QtCore.SIGNAL("triggered()"),
                               self.additional_info)
        QtCore.QObject.connect(self.actionCloseBugreport,
                               QtCore.SIGNAL("triggered()"),
                               self.close_bugreport)
        QtCore.QObject.connect(self.actionNewWnpp,
                               QtCore.SIGNAL("triggered()"),
                               self.new_wnpp)
        QtCore.QObject.connect(self.actionClearLineEdit,
                               QtCore.SIGNAL("triggered()"),
                               self.clear_lineedit)
        QtCore.QObject.connect(self.actionSettings,
                               QtCore.SIGNAL("triggered()"),
                               self.settings_diag)
        QtCore.QObject.connect(self.actionAbout,
                               QtCore.SIGNAL("triggered()"),
                               self.about)
        QtCore.QObject.connect(self.actionAboutQt,
                               QtCore.SIGNAL("triggered()"),
                               self.about_qt)
        QtCore.QObject.connect(self.lineEdit,
                               QtCore.SIGNAL("textChanged(const QString&)"),
                               self.lineedit_text_changed)
        QtCore.QObject.connect(self.lineEdit,
                               QtCore.SIGNAL("returnPressed()"),
                               self.lineedit_return_pressed)
        QtCore.QObject.connect(self.tableView,
                               QtCore.SIGNAL("activated(const QModelIndex&)"),
                               self.activated)

        # setup the table
        self.model = TableModel(self)
        self.proxymodel = MySortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.model)
        self.proxymodel.setFilterKeyColumn(-1)
        self.tableView.setModel(self.proxymodel)
        self.tableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
        self.tableView.verticalHeader().setVisible(False)

        # setup the settings
        self.settings = rng.Settings(rng.Settings.CONFIGFILE)
        self.settings.load()
        self._apply_settings()

        self.webView.setHtml(rng.REPORTBUG_NG_INSTRUCTIONS)

        # setup the finite state machine
        self._stateChanged(None, None)

        if args:
            self.lineEdit.setText(unicode(args[0]))
            self.lineedit_return_pressed()


    def closeEvent(self, ce):
        """Save the settings and close the GUI."""
        self.logger.info("Catched close event.")
        self._get_settings()
        self.settings.save()
        ce.accept()

    def activated(self, index):
        """React on click in table."""
        self.logger.info("Row %s activated." % str(index.row()))
        realrow = self.proxymodel.mapToSource(index).row()
        bugnr = self.model.elements[realrow].bug_num
        # find the bug in our list, and get the package and nr
        for i in self.bugs:
            if i.bug_num == bugnr:
                self.currentBug = i
                break
        self._stateChanged(self.currentBug.package, self.currentBug)
        url = bts.BTS_URL + str(bugnr)
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
        self.proxymodel.setFilterRegExp(\
            QtCore.QRegExp(text,
                           QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.FixedString)
            )

    def lineedit_return_pressed(self):
        #
        # just in case ;)
        #
        text = unicode(self.lineEdit.text())
        if text.startswith("http://"):
            self._show_url(text)
            return

        self.logger.info("Return pressed.")
        # TODO: self.lineEdit.clear() does not always work, why?
        QtCore.QTimer.singleShot(0,self.lineEdit,QtCore.SLOT("clear()"))
        query = rng.translate_query(text)
        self.logger.debug("Query: %s" % str(query))
        if query[0]:
            if query[0] == 'package':
                # test if there is a submit-as field available and rename the
                # package if neccessairy
                realname = bug.submit_as(query[1])
                if query[1] != realname:
                    self.logger.debug("Using %s as package name as requested by developer." % str(realname))
                    query[1] = realname
            buglist = bts.get_bugs(query)
        else:
            # just a signle bug
            buglist = [query[1]]
        # ok, we know the package, so enable some buttons which don't depend
        # on the existence of the acutal packe (wnpp) or bugreports for that
        # package.
        if query[0] in ("src", "package"):
            self._stateChanged(query[1], None)
        # if we got a bugnumber we'd like to select it and enable some more
        # buttons. unfortunately we don't know if the bugnumber actually exists
        # for now, so we have to wait a bit until the bug is fetched.
        else:
            self._stateChanged(None, None)
        self.logger.debug("Buglist matching the query: %s" % str(buglist))
        self.bugs = bts.get_status(buglist)
        # ok, we fetched the bugs. see if the list isn't empty
        if query[0] in (None,) and len(self.bugs) > 0:
            self.currentBug = self.bugs[0]
            self.currentPackage = self.currentBug.package
            self._stateChanged(self.currentPackage, self.currentBug)
        self.model.set_elements(self.bugs)
        self.tableView.resizeRowsToContents()


    def settings_diag(self):
        """Spawn settings dialog and get settings."""
        s = RngSettingsDialog(self.settings)
        if s.exec_() == s.Accepted:
            self.logger.debug("Accepted settings change, applying.")
            self.settings = s.settings

    def about(self):
        """Shows the about box."""
        # TODO: copyright string below should be a constant
        QtGui.QMessageBox.about(\
            self,
            self.tr("About Reportbug-NG"),
            self.tr(\
"""Copyright (C) 2007-2009 Bastian Venthur <venthur at debian org>

Homepage: http://reportbug-ng.alioth.debian.org

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version."""))

    def about_qt(self):
        QtGui.QMessageBox.aboutQt(self, self.tr("About Qt"))

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
            self.currentBug = bts.Bugreport()
            self.actionAdditionalInfo.setEnabled(0)
            self.actionCloseBugreport.setEnabled(0)


    def __submit_dialog(self, type):
        """Setup and spawn the submit dialog."""
        dialog = SubmitDialog()
        dialog.checkBox_script.setChecked(self.settings.script)
        dialog.checkBox_presubj.setChecked(self.settings.presubj)

        if type == 'wnpp':
            dialog.wnpp_groupBox.setEnabled(1)
            dialog.wnpp_groupBox.setChecked(1)
            dialog.groupBox_other.setEnabled(0)
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
            to = "%s@bugs.debian.org" % self.currentBug.bug_num
        elif type == 'close':
            dialog.groupBox_other.setEnabled(0)
            dialog.wnpp_groupBox.setEnabled(0)
            dialog.comboBoxSeverity.setEnabled(0)
            dialog.checkBoxSecurity.setEnabled(0)
            dialog.checkBoxPatch.setEnabled(0)
            dialog.checkBoxL10n.setEnabled(0)
            dialog.lineEditSummary.setText("Done: %s" % self.currentBug.subject)
            package = self.currentBug.package
            to = "%s-done@bugs.debian.org" % self.currentBug.bug_num
        else:
            self.logger.critical("Received unknown submit dialog type!")

        version = rng.getInstalledPackageVersion(package)
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        for action in rng.WNPP_ACTIONS:
            dialog.wnpp_comboBox.addItem(action)
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
            mua = self.settings.lastmua
            script = dialog.checkBox_script.isChecked()
            presubj = dialog.checkBox_presubj.isChecked()

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
                body = rng.prepareBody(package, version, severity, tags, cc, script)

            if len(subject) == 0:
                subject = "Please enter a subject before submitting the report."

            if presubj:
                txt = rng.get_presubj(package)
                if txt:
                    QtGui.QMessageBox.information(self, "Information", txt)
            thread.start_new_thread(rng.prepareMail, (mua, to, subject, body))


    def _apply_settings(self):
        """Apply settings."""
        self.resize(self.settings.width, self.settings.height)
        self.move(self.settings.x, self.settings.y)
        self.tableView.horizontalHeader().resizeSection(0, self.settings.bugnrWidth)
        self.tableView.horizontalHeader().resizeSection(1, self.settings.summaryWidth)
        self.tableView.horizontalHeader().resizeSection(2, self.settings.statusWidth)
        self.tableView.horizontalHeader().resizeSection(3, self.settings.severityWidth)
        self.tableView.horizontalHeader().resizeSection(4, self.settings.lastactionWidth)
        order = QtCore.Qt.DescendingOrder
        if self.settings.sortAsc:
            order = QtCore.Qt.AscendingOrder
        self.tableView.horizontalHeader().setSortIndicator(self.settings.sortByCol, order)

    def _get_settings(self):
        """Get current settings."""
        p = self.pos()
        s = self.size()
        self.settings.x = p.x()
        self.settings.y = p.y()
        self.settings.width = s.width()
        self.settings.height = s.height()
        self.settings.sortByCol = self.tableView.horizontalHeader().sortIndicatorSection()
        self.settings.sortAsc = {QtCore.Qt.AscendingOrder : True,
                                 QtCore.Qt.DescendingOrder : False}[self.tableView.horizontalHeader().sortIndicatorOrder()]
        self.settings.bugnrWidth = self.tableView.columnWidth(0)
        self.settings.summaryWidth = self.tableView.columnWidth(1)
        self.settings.statusWidth = self.tableView.columnWidth(2)
        self.settings.severityWidth = self.tableView.columnWidth(3)
        self.settings.lastactionWidth = self.tableView.columnWidth(4)

    def _show_url(self, url):
        url = QtCore.QUrl(url)
        self.webView.setUrl(url)



class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self.parent = parent
        self.logger = logging.getLogger("TableModel")
        self.elements = []

    def rowCount(self, parent):
        return len(self.elements)

    def columnCount(self, parent):
        return 6

    #
    # DAMMIT DONT IGNORE THE DISPLAY ROLE!!
    #
    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        if role == QtCore.Qt.ForegroundRole:
            severity = self.elements[index.row()].severity.lower()
            done = self.elements[index.row()].done
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
            if done:
                c = self.parent.settings.c_resolved
            return QtCore.QVariant(QtGui.QColor(c))
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        bug = self.elements[index.row()]
        if bug.archived:
            status = "Archived"
        elif bug.done:
            status = "Closed"
        else:
            status = "Open"
        data = {0 : bug.bug_num,
                1 : bug.subject,
                2 : status,
                3 : bug.severity,
                4 : bug.tags,
                5 : QtCore.QDate(bug.log_modified)}[index.column()]
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
                4 : "Tags",
                5 : "Last Action"}[section]
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

    def __init__(self, parent=None):
        QtGui.QSortFilterProxyModel.__init__(self, parent)

    def lessThan(self, left, right):
        if left.column() != 3:
            return QtGui.QSortFilterProxyModel.lessThan(self, left, right)
        l = left.row()
        r = right.row()
        return self.sourceModel().elements[l] < self.sourceModel().elements[r]


class SubmitDialog(QtGui.QDialog, submitdialog.Ui_SubmitDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        QtCore.QObject.connect(self.buttonBox.button(QtGui.QDialogButtonBox.Ok),
                               QtCore.SIGNAL("clicked()"),
                               self.accept)
        QtCore.QObject.connect(self.buttonBox.button(QtGui.QDialogButtonBox.Cancel),
                               QtCore.SIGNAL("clicked()"),
                               self.reject)

