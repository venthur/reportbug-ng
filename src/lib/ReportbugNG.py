import commands

VERSION = "0.2007.03.08"


def prepareMail(mua, text):
    """Tries to call MUA with the text (mailto-format)"""
    
    command = str(mua + " " + text.encode("ascii", "replace"))
    if not commands.getstatusoutput(command)[0] == 0:
        print "Reportbug was not able to start your mailclient."
        print "Please copy-paste the following text to your mailclient and send it to submit@bugs.debian.org"
        print text
    
    
def createMailtoString(to, subject, package, version, severity=None):
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

def getSystemInformation():
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

def getInstalledPackageVersion(package):
    """Returns the version of package, if installed or empty string not installed"""
    
    try:
        version = commands.getoutput("dpkg --print-avail %s 2>/dev/null | grep Version:" % package).split(": ", 1)[1]
    except:
        version = ""
        
    return version


def callBrowser(url):
    """Calls an external Browser to upen the URL."""
    
    import webbrowser
    webbrowser.open(url)
