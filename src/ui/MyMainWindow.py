# MyMainWindow.py - Mainwindow of Reportbug-NG.
# Copyright (C) 2007  Bastian Venthur
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


from MainWindow import Form
from SubmitDialog import SubmitDialog
from lib.Bugreport import Bugreport
from lib import DebianBTS
from lib.ReportbugNG import *

from qttable import QTableItem
from qt import Qt

import thread


REPORTBUG_NG_INSTRUCTIONS = """\
<h2>Using Reportbug-NG</h2>
<h3>Step 1: Finding Bugs</h3>
<p>To find a bug just enter the name of the package and press Enter. Loading the list might take a few seconds.</p>
<p>To see the full bugreport click on the bug in the list. Links in the bugreport will open in an external browser when clicked.</p>

<h3>Step 2: Filtering Bugs</h3>
<p>To filter the list of existing bugs enter a few letters (without pressing Enter). The filter is case insensitive.</p>

<h3>Step 3: Reporting Bugs</h3>
<p>You can either provide additional information for an existing bug by clicking on the bug in the list and pressing the "Additional Info" button or you can create a new bugreport for the current package by clicking the "New Bugreport" button.</p>
"""


class MyTableItem(QTableItem):
    """Derived from QTableItem to pretty-paint different bugtypes"""

    def __init__(self, table, editType, text, status, severity):
        QTableItem.__init__(self, table, editType, text)
        self.status = status.lower()
        self.severity = severity.lower()

    def paint(self, painter, colorGroup, rect, selected):
        if self.severity in ("grave", "serious", "critical"):
            colorGroup.setColor(colorGroup.Text, Qt.darkMagenta)
        elif self.severity == "important":
            colorGroup.setColor(colorGroup.Text, Qt.red)
        elif self.severity == "minor":
            colorGroup.setColor(colorGroup.Text, Qt.darkGreen)
        elif self.severity == "wishlist":
            colorGroup.setColor(colorGroup.Text, Qt.darkYellow)

        if self.status == "resolved":
            colorGroup.setColor(colorGroup.Text, Qt.gray)
        
        QTableItem.paint(self, painter, colorGroup, rect, selected)


class MyMainWindow(Form):
    
    def __init__(self, lastMUA=""):
        Form.__init__(self)
        self.bugs = []
        self.currentPackage = ""
        self.currentBug = Bugreport(0)

        self.table.setColumnStretchable(0, True)
        self.splitter.setSizes([150,300])

        self.lastMUA = lastMUA
        
        self.textBrowser.setText(REPORTBUG_NG_INSTRUCTIONS)
        # For debugging purpose only:
        # self.pushButtonNewBugreport.setEnabled(1)
    
    
    def loadAllBugSummaries(self, package):
        """Loads all bug summaries of a package. (Intended to run as thread)"""
        
        bugs = []
        bugs = DebianBTS.getBugsByPackage(self.currentPackage)
        
        # Check if our package is still current.
        if package != self.currentPackage:
            return
        
        self.bugs = bugs

        self.table.setNumRows(len(self.bugs))
        row = 0
        for bug in self.bugs:
            self.table.verticalHeader().setLabel(row,bug.nr)
            #self.table.setText(row,0, bug.summary)
            #self.table.setText(row,1, bug.status)
            #self.table.setText(row,2, bug.severity)
            self.table.setItem(row,0, MyTableItem(self.table, QTableItem.Never, bug.summary, bug.status, bug.severity))
            self.table.setItem(row,1, MyTableItem(self.table, QTableItem.Never, bug.status, bug.status, bug.severity))
            self.table.setItem(row,2, MyTableItem(self.table, QTableItem.Never, bug.severity, bug.status, bug.severity))
            row += 1
        
        if len(self.bugs) == 0:
            self.textBrowser.setText("<h2>No bugreports for package %s found!</h2>" % self.currentPackage + REPORTBUG_NG_INSTRUCTIONS)
        else:
            self.textBrowser.setText("<h2>Click on a bugreport to see the full text.</h2>" + REPORTBUG_NG_INSTRUCTIONS)
    
    
    def lineEdit_returnPressed(self):
        """The user changed the text in the combobox and pressed enter."""
        
        self.currentPackage = unicode(self.lineEdit.text())
        self.lineEdit.setText("")
        self.table.setNumRows(0)
        self.textBrowser.setText("<h2>Fetching bugreports for package %s, please wait.</h2>" % self.currentPackage)
        self.pushButtonNewBugreport.setEnabled(1)
        self.pushButtonAdditionalInfo.setEnabled(0)
    
        # Fetch the bugs in a thread
        thread.start_new_thread(self.loadAllBugSummaries, (self.currentPackage,))
        

    def lineEdit_textChanged(self, a0):
        """The filter text has changed."""
        
        self.table.viewport().setUpdatesEnabled(False)
 
        filter = unicode(a0).lower()
        for row in range(len(self.bugs)):
            if unicode(self.bugs[row]).lower().find(filter) != -1:
                self.table.showRow(row)
            else:
                self.table.hideRow(row)           
        print "just after hiding/showing everyting"
        
        self.table.viewport().setUpdatesEnabled(True)
        self.table.updateContents()


    def loadBugreport(self, bugnr):
        """Loads the bugreport and writes the result to build in browser. (Intended to run in a thread)"""

        for bug in self.bugs:
            if bug.nr == bugnr:
                if len(bug.fulltext) == 0:
                    bug.fulltext = DebianBTS.getFullText(bugnr)
                break
        
        # While loading the bugreport the user switched to another bug, abort showing
        # the report.
        if bugnr != self.currentBug.nr:
            return
        
        self.textBrowser.setText(self.currentBug.fulltext, DebianBTS.BTS_CGIBIN_URL)


    def table_selectionChanged(self):
        """The user selected a Bug from the list."""
        if self.table.currentRow() < 0 or self.table.currentRow() > len(self.bugs)-1:
            return
        
        self.currentBug = self.bugs[self.table.currentRow()]
        self.textBrowser.setText("<h2>Fetching bugreport %s, please wait.</h2>" % self.currentBug)
        self.pushButtonAdditionalInfo.setEnabled(1)
        
        # Fetch the fulltext in a thread
        thread.start_new_thread(self.loadBugreport, (self.currentBug.nr,))
        
    
    def pushButtonAdditionalInfo_clicked(self):
        """The user wants to provide additional info for the current bug."""
    
        package = self.currentPackage
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        for mua in SUPPORTED_MUA:
            dialog.comboBoxMUA.insertItem(mua.title())
        if self.lastMUA in SUPPORTED_MUA:
            dialog.comboBoxMUA.setCurrentItem(SUPPORTED_MUA.index(self.lastMUA))
        dialog.comboBoxSeverity.setEnabled(0)
        dialog.checkBoxSecurity.setEnabled(0)
        dialog.checkBoxPatch.setEnabled(0)
        dialog.checkBoxL10n.setEnabled(0)
        
        if dialog.exec_loop() == dialog.Accepted:
            subject = unicode(dialog.lineEditSummary.text())
            mua = str(dialog.comboBoxMUA.currentText().lower())
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            to = "%s@bugs.debian.org" % self.currentBug.nr
            body = prepareBody(package, version)
            
            self.lastMUA = mua
            prepareMail(mua, to, subject, body)

    
    def pushButtonNewBugreport_clicked(self):
        """The User wants to file a new bugreport against the current package."""
        
        package = self.currentPackage
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        for mua in SUPPORTED_MUA:
            dialog.comboBoxMUA.insertItem(mua.title())
        if self.lastMUA in SUPPORTED_MUA:
            dialog.comboBoxMUA.setCurrentItem(SUPPORTED_MUA.index(self.lastMUA))
        
        if dialog.exec_loop() == dialog.Accepted:
            subject = unicode(dialog.lineEditSummary.text())
            severity = dialog.comboBoxSeverity.currentText().lower()
            tags = []
            if dialog.checkBoxL10n.isChecked():
                tags.append("l10n")
            if dialog.checkBoxPatch.isChecked():
                tags.append("patch")
            if dialog.checkBoxSecurity.isChecked():
                tags.append("security")
            
            mua = str(dialog.comboBoxMUA.currentText().lower())
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            to = "submit@bugs.debian.org"
            body = prepareBody(package, version, severity, tags)
            
            self.lastMUA = mua
            prepareMail(mua, to, subject, body)

    
    def textBrowser_linkClicked(self,a0):
        """The user clicked a link in the Bugreport."""
  
        url = unicode(a0)
        callBrowser(url)
        # Hack to open link in external Browser: just reload the current bugreport
        self.textBrowser.setText(self.currentBug.fulltext)
