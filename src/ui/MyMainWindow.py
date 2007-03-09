from MainWindow import Form
from SubmitDialog import SubmitDialog
from bts.Bugreport import Bugreport
from bts.BTS import BTS

import commands

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
        """The user changed the text in the combobox and pressed enter"""
        
        self.currentPackage = unicode(self.lineEdit.text())
        self.textBrowser.setText("Fetching bugreports for package %s, please wait." % self.currentPackage)
        self.lineEdit.setText("")
        self.pushButtonNewBugreport.setEnabled(1)
    
        self.bugs = []
        
        self.bugs = BTS().getBugsByPackage(self.currentPackage)
        self.visibleBugs = self.bugs

        self.listBox.clear()
        for bug in self.visibleBugs:
            self.listBox.insertItem(str(bug))
	    
        if len(self.visibleBugs) == 0:
            self.textBrowser.setText("No bugreports for package %s found!" % self.currentPackage)
        else:
            self.textBrowser.setText("Click on bugreport for package to see the full text.")
        

    def lineEdit_textChanged(self, a0):
        """Text in Filter has changed"""
        
        self.visibleBugs = []
        self.listBox.clear()
        
        for bug in self.bugs:
            if str(bug).lower().find(a0.lower()) != -1:
                self.visibleBugs.append(bug)
                self.listBox.insertItem(str(bug))        

        
    def listBox_highlighted(self,a0):
        """The user selected a Bug from the list"""
        
        self.listBox.update()
        self.pushButtonAdditionalInfo.setEnabled(1)
        
        self.currentBug = self.visibleBugs[a0]
        
        # Fetch the fulltext if not yet available.
        if len(self.visibleBugs[a0].fulltext) == 0:
            self.visibleBugs[a0].fulltext = BTS().getFullText(self.visibleBugs[a0].nr)
        
        self.textBrowser.setText(self.visibleBugs[a0].fulltext)
        
    
    def pushButtonAdditionalInfo_clicked(self):
        """The user wants to provide additional info to current bug"""
    
        summary = ""
        mua = ""
        package = self.currentPackage
        try:
            version = commands.getoutput("dpkg --print-avail %s 2>/dev/null | grep Version:" % package).split(": ", 1)[1]
        except:
            version = ""
        
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
            
            self.prepareMail(mua, self.createMailtoString(to, subject, package, version))
        else:
            pass

    
    def pushButtonNewBugreport_clicked(self):
        """The User wants to file a new bugreport against the current package"""
        
        summary = ""
        severity = ""
        tags = ""
        mua = ""
        package = self.currentPackage
        try:
            version = commands.getoutput("dpkg --print-avail %s 2>/dev/null | grep Version:" % package).split(": ", 1)[1]
        except:
            version = ""
        
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
            
            self.prepareMail(mua, self.createMailtoString(to, subject, package, version, severity))
        else:
            pass


    def prepareMail(self, mua, text):
        """Tries to call mua with the text (mailto-format)"""
        
        command = str(mua + " " + text.encode("ascii", "replace"))
        if not commands.getstatusoutput(command)[0] == 0:
            print "Reportbug was not able to start your mailclient."
            print "Please copy-paste the following text to your mailclient and send it to submit@bugs.debian.org"
            print text
        
        
    def createMailtoString(self, to, subject, package, version, severity=None):
        """Creates a Mailto-Line containing the whole email plus some sysinfo."""
        
        s = "mailto:%s?subject=%s" % (to, subject)
        
        s += "&body=" 
        s += "Package: %s\n" % package
        s += "Version: %s\n" % version 

        if severity:
            s += "Severity: %s\n" % severity
        
        s += "\n"
        s += "--- Please enter the report below this line. ---\n\n\n"

        #s self.getSystemInformation()
                
        s = s.replace("\n", "%0D%0A")
        s = "\"" + s + "\""
        
        return s

    def getSystemInformation(self):
        """Returns some hopefully usefull sysinfo"""
        
        s = "--- System infomation. ---\n"
        
        list = ("dpkg --print-installation-architecture", 
                "uname -srv",
                "uname -mpio",
                "apt-cache policy | grep Packages$")
        
        for cmd in list:
            s += "%s:\n" % cmd
            s += commands.getoutput("%s 2>/dev/null" % cmd)
            s += "\n\n"
        
        return s
        