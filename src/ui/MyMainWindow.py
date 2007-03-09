from MainWindow import Form
from SubmitDialog import SubmitDialog
from lib.Bugreport import Bugreport
from lib import DebianBTS
from lib.ReportbugNG import *


class MyMainWindow(Form):
    
    def __init__(self):
        Form.__init__(self)
        self.bugs = []
        self.visibleBugs = []
        self.currentPackage = ""
        self.currentBug = Bugreport(0)
        
        # For debugging purpose only:
        #self.pushButtonNewBugreport.setEnabled(1)
    
    
    def lineEdit_returnPressed(self):
        """The user changed the text in the combobox and pressed enter."""
        
        self.currentPackage = unicode(self.lineEdit.text())
        self.textBrowser.setText("Fetching bugreports for package %s, please wait." % self.currentPackage)
        self.lineEdit.setText("")
        self.pushButtonNewBugreport.setEnabled(1)
    
        self.bugs = []
        
        self.bugs = DebianBTS.getBugsByPackage(self.currentPackage)
        self.visibleBugs = self.bugs

        self.listBox.clear()
        for bug in self.visibleBugs:
            self.listBox.insertItem(str(bug))
	    
        if len(self.visibleBugs) == 0:
            self.textBrowser.setText("No bugreports for package %s found!" % self.currentPackage)
        else:
            self.textBrowser.setText("Click on bugreport for package to see the full text.")
        

    def lineEdit_textChanged(self, a0):
        """The filter text has changed."""
        
        self.visibleBugs = []
        self.listBox.clear()
        
        for bug in self.bugs:
            if str(bug).lower().find(a0.lower()) != -1:
                self.visibleBugs.append(bug)
                self.listBox.insertItem(str(bug))        

        
    def listBox_highlighted(self,a0):
        """The user selected a Bug from the list."""
        
        self.listBox.update()
        self.pushButtonAdditionalInfo.setEnabled(1)
        
        self.currentBug = self.visibleBugs[a0]
        
        # Fetch the fulltext if not yet available.
        if len(self.visibleBugs[a0].fulltext) == 0:
            self.visibleBugs[a0].fulltext = DebianBTS.getFullText(self.visibleBugs[a0].nr)
        
        self.textBrowser.setText(self.visibleBugs[a0].fulltext)
        
    
    def pushButtonAdditionalInfo_clicked(self):
        """The user wants to provide additional info for the current bug."""
    
        package = self.currentPackage
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        dialog.comboBoxSeverity.setEnabled(0)
        dialog.comboBoxTags.setEnabled(0)
        
        if dialog.exec_loop() == dialog.Accepted:
            subject = unicode(dialog.lineEditSummary.text())
            mua = dialog.comboBoxMUA.currentText().lower()
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            to = "%s@bugs.debian.org" % self.currentBug.nr
            
            prepareMail(mua, createMailtoString(to, subject, package, version))

    
    def pushButtonNewBugreport_clicked(self):
        """The User wants to file a new bugreport against the current package."""
        
        package = self.currentPackage
        version = getInstalledPackageVersion(package)
        
        dialog = SubmitDialog()
        dialog.lineEditPackage.setText(package)
        dialog.lineEditVersion.setText(version)
        
        if dialog.exec_loop() == dialog.Accepted:
            subject = unicode(dialog.lineEditSummary.text())
            severity = dialog.comboBoxSeverity.currentText().lower()
            tags = dialog.comboBoxTags.currentText()
            mua = dialog.comboBoxMUA.currentText().lower()
            package = dialog.lineEditPackage.text()
            version = dialog.lineEditVersion.text()
            to = "submit@bugs.debian.org"
            
            prepareMail(mua, createMailtoString(to, subject, package, version, severity))


