# BugreportNG.py - Reportbug-NG's main library.
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


import commands
import webbrowser

VERSION = "0.2007.03.10"


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
    
    webbrowser.open(url)
