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
from qttable import QTable
from qt import Qt
from qt import QWhatsThis

import thread
import sys
import logging


REPORTBUG_NG_INSTRUCTIONS = _("""\
<h2>Using Reportbug-NG</h2>
<h3>Step 1: Finding Bugs</h3>
<p>To find a bug just enter a query and press Enter. Loading the list might take a few seconds.</p>

<p>The following queries are supported:
<dl>
<dt><code>package</code></dt><dd>Returns all the bugs belonging to the PACKAGE</dd>
<dt><code>bugnumber</code></dt><dd>Returns the bug with BUGNUMBER</dd>
<dt><code>maintainer@foo.bar</code></dt><dd>Returns all the bugs assigned to MAINTAINER</dd>
<dt><code>src:sourcepackage</code></dt><dd>Returns all the bugs belonging to the SOURCEPACKAGE</dd>
<dt><code>from:submitter@foo.bar</code></dt><dd>Returns all the bugs filed by SUBMITTER</dd>
<dt><code>severity:foo</code></dt><dd>Returns all the bugs of SEVERITY. Warning: this list is probably very long. Recognized are the values: critical, grave, serious, important, normal, minor and wishlist</dd>
<dt><code>tag:bar</code></dt><dd>Returns all the bugs marked with TAG</dd>
</dl>
</p>

<p>To see the full bugreport click on the bug in the list. Links in the bugreport will open in an external browser when clicked.</p>

<h3>Step 2: Filtering Bugs</h3>
<p>To filter the list of existing bugs enter a few letters (without pressing Enter). The filter is case insensitive and
affects the packagename, bugnumber, summary, status and severity of a bug.</p>

<h3>Step 3: Reporting Bugs</h3>
<p>You can either provide additional information for an existing bug by clicking on the bug in the list and pressing the "Additional Info" button or you can create a new bugreport for the current package by clicking the "New Bugreport" button.</p>
""")

# Those strings must not be translated!
SEVERITY = ("Critical", "Grave", "Serious", "Important", "Normal", "Minor", "Wishlist")

SEVERITY_EXPLANATION = _("\
<b>%(cri)s</b> makes unrelated software on the system (or the whole system) break, or causes serious data loss, or introduces a security hole on systems where you install the package. \
<br> \
<b>%(gra)s</b> makes the package in question unusable or mostly so, or causes data loss, or introduces a security hole allowing access to the accounts of users who use the package. \
<br> \
<b>%(ser)s</b> is a severe violation of Debian policy (roughly, it violates a \"must\" or \"required\" directive), or, in the package maintainer's opinion, makes the package unsuitable for release. \
<br> \
<b>%(imp)s</b> a bug which has a major effect on the usability of a package, without rendering it completely unusable to everyone. \
<br> \
<b>%(nor)s</b> the default value, applicable to most bugs. \
<br> \
<b>%(min)s</b> a problem which doesn't affect the package's usefulness, and is presumably trivial to fix. \
<br> \
<b>%(wis)s</b> for any feature request, and also for any bugs that are very difficult to fix due to major design considerations.") % {'cri':"Critical", 'gra':"Grave", 'ser':"Serious", 'imp':"Important", 'nor':"Normal", 'min':"Minor", 'wis':"Wishlist"}

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
    
    def __init__(self, settings, args):
        self.logger = logging.getLogger("MainWindow")
        self.logger.info("Logger initialized.")
        
        Form.__init__(self)
        self.bugs = []
        self.stateChanged(None, None)

        # The ID of the latest Thread which queried the BTS
        self.currentQuery = 0
        self.queryLock = thread.allocate_lock()

        self.table.setColumnStretchable(0, True)
        self.splitter.setSizes([150,300])

        self.settings = settings
        self.resize(self.settings.width, self.settings.height)
        self.move(self.settings.x, self.settings.y)

        self.textBrowser.setText(REPORTBUG_NG_INSTRUCTIONS)
        # For debugging purpose only:
        # self.pushButtonNewBugreport.setEnabled(1)
        
        
        if args:
            self.lineEdit.setText(unicode(args[0], "utf-8"))
            self.lineEdit_returnPressed()
            
    def closeEvent(self, ce):
        # Dirty Hack. Due X's limitations, we must get the position of the 
        # window *before* it is get's undecorated.
        # See: http://doc.trolltech.com/3.3/geometry.html
        # So we overwrite the closeEvent to get the position before we
        # distroy the window.
        p = self.pos()
        s = self.size()
        self.settings.x = p.x()
        self.settings.y = p.y()
        self.settings.width = s.width()
        self.settings.height = s.height()

        # Accecpt the closeEvent 
        ce.accept()

    
    def stateChanged(self, package, bug):
        """Transition for our finite state machine logic"""
        
        if package:
            self.currentPackage = package
            self.pushButtonNewBugreport.setEnabled(1)
        else:
            self.currentPackage = ""
            self.pushButtonNewBugreport.setEnabled(0)
        
        if bug:
            self.currentBug = bug
            self.pushButtonAdditionalInfo.setEnabled(1)
        else:
            self.currentBug = Bugreport(0)
            self.pushButtonAdditionalInfo.setEnabled(0)
        
    
    def loadAllBugSummaries(self, query):
        """Loads all bug summaries of a package. (Intended to run as thread)"""
        
        bugs = []
        bugs = DebianBTS.getBugsByQuery(query)
        
        # Check if we are still the latest query
        if self.currentQuery != thread.get_ident():
            return
        
        self.queryLock.acquire()
        
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
            self.textBrowser.setText(_("<h2>No bugreports for package %s found!</h2>") % self.currentPackage + REPORTBUG_NG_INSTRUCTIONS)
        if len(self.bugs) == 1:
            self.table.selectRow(0)
            self.table_selectionChanged()
        else:
            self.textBrowser.setText(_("<h2>Click on a bugreport to see the full text.</h2>") + REPORTBUG_NG_INSTRUCTIONS)
    
        self.queryLock.release()

    
    def lineEdit_returnPressed(self):
        """The user changed the text in the combobox and pressed enter."""

        # The following Queries are supported:
        #     Bugnumber
        #     Packagename
        #     maintainer@foo.bar
        #     src:Packagename
        #     from:submitter@foo.bar
        #     severity:foo
        #     tag:bar
        
        self.bugs = []
        s = unicode(self.lineEdit.text()).strip()
        if (s.startswith('src:')):
            what = _("<h2>Fetching bugreports of source package %s, please wait.</h2>") % s.split(":")[1]
            self.stateChanged(s.split(":")[1], None)
        elif (s.startswith('from:')):
            what = _("<h2>Fetching bugreports from submitter %s, please wait.</h2>") % s.split(":")[1]
            self.stateChanged(None, None)
        elif (s.startswith('severity:')):
            what = _("<h2>Fetching bugreports of severity %s, please wait.</h2>") % s.split(":")[1]
            self.stateChanged(None, None)
        elif (s.startswith('tag:')):
            what = _("<h2>Fetching bugreports with tag %s, please wait.</h2>") % s.split(":")[1]
            self.stateChanged(None, None)
        elif (s.find("@") != -1):
            what = _("<h2>Fetching bugreports assigned to %s, please wait.</h2>") % s
            self.stateChanged(None, None)
        elif (re.match("^[0-9]*$", s)):
            what = _("<h2>Fetching bugreport with bug number %s, please wait.</h2>") % s
            self.stateChanged(None, s)
        else:
            what = _("<h2>Fetching bugreports for package %s, please wait.</h2>") % s
            self.stateChanged(s, None)

        self.lineEdit.setText("")
        self.table.setNumRows(0)
        self.textBrowser.setText(what)
    
        # Fetch the bugs in a thread
        self.currentQuery = thread.start_new_thread(self.loadAllBugSummaries, (s,))
        

    def lineEdit_textChanged(self, a0):
        """The filter text has changed."""
        # Supress thousands of new selections everytime a row gets hided:
        # would be better if I just could turn of selections if the selected
        # row gets hided.
        selectionmode = self.table.SelectionMode()
        self.table.setSelectionMode(QTable.NoSelection)

#        self.table.viewport().setUpdatesEnabled(False)
        filter = unicode(a0).lower()
        for row in range(len(self.bugs)):
            if unicode(self.bugs[row]).lower().find(filter) != -1:
                self.table.showRow(row)
            else:
                self.table.hideRow(row)           
#        self.table.viewport().setUpdatesEnabled(True)
#        self.table.updateContents()

        # Re-Enable selections again
        self.table.setSelectionMode(selectionmode)
        
        
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
        self.textBrowser.setText(_("<h2>Fetching bugreport %s, please wait.</h2>") % self.currentBug)
        self.stateChanged(self.currentBug.package, self.currentBug)
        
        # Fetch the fulltext in a thread
        thread.start_new_thread(self.loadBugreport, (self.currentBug.nr,))
        
    
    def pushButtonAdditionalInfo_clicked(self):
        """The user wants to provide additional info for the current bug."""
    
        package = self.currentBug.package
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        for mua in SUPPORTED_MUA:
            dialog.comboBoxMUA.insertItem(mua.title())
        if self.settings.lastmua in SUPPORTED_MUA:
            dialog.comboBoxMUA.setCurrentItem(SUPPORTED_MUA.index(self.settings.lastmua))
        for sev in SEVERITY:
            dialog.comboBoxSeverity.insertItem(sev)
        # Set default severity to 'normal'
        dialog.comboBoxSeverity.setCurrentItem(4)
        QWhatsThis.add(dialog.comboBoxSeverity, SEVERITY_EXPLANATION)
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
            
            self.settings.lastmua = mua
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
        if self.settings.lastmua in SUPPORTED_MUA:
            dialog.comboBoxMUA.setCurrentItem(SUPPORTED_MUA.index(self.settings.lastmua))
        for sev in SEVERITY:
            dialog.comboBoxSeverity.insertItem(sev)
        # Set default severity to 'normal'
        dialog.comboBoxSeverity.setCurrentItem(4)
        QWhatsThis.add(dialog.comboBoxSeverity, SEVERITY_EXPLANATION)
               
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
            
            self.settings.lastmua = mua
            prepareMail(mua, to, subject, body)

    
    def textBrowser_linkClicked(self,a0):
        """The user clicked a link in the Bugreport."""
  
        url = unicode(a0)
        callBrowser(url)
        # Hack to open link in external Browser: just reload the current bugreport
        self.textBrowser.setText(self.currentBug.fulltext)
