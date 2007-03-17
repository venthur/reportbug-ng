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
import re
import os
import webbrowser


VERSION = "0.2007.03.10"


def prepareMail(mua, text):
    """Tries to call MUA with the text (mailto-format)"""
    
    command = str(mua + " " + text.encode("ascii", "replace"))
    if not commands.getstatusoutput(command)[0] == 0:
        print "Reportbug was not able to start your mailclient."
        print "Please copy-paste the following text to your mailclient and send it to submit@bugs.debian.org"
        print text
    
    
def createMailtoString(to, subject, package, version, severity=None, tags=[]):
    """Creates a Mailto-Line containing the whole email plus some sysinfo."""
    
    s = "mailto:%s?subject=%s" % (to, subject)
    
    s += "&body=" 
    s += "Package: %s\n" % package
    s += "Version: %s\n" % version 

    if severity:
        s += "Severity: %s\n" % severity
    
    if tags:
        s += "Tags:"
        for tag in tags:
            s += " %s" % tag
        s += "\n"
    
    s += "\n"
    s += "--- Please enter the report below this line. ---\n\n\n"

    s += getSystemInfo() + "\n"
    s += getDebianReleaseInfo() + "\n"
    s += getPackageInfo(package) + "\n"
            
    s = s.replace("\n", "%0D%0A")
    s = "\"" + s + "\""
    
    return s

def getSystemInfo():
    """Returns some hopefully usefull sysinfo"""
    
    s = "--- System information. ---\n"
    s += "Architecture: %s\n" % commands.getoutput("dpkg --print-installation-architecture 2>/dev/null")
    s += "Kernel:       %s\n" % commands.getoutput("uname -sr 2>/dev/null")
    
    return s


def getPackageInfo(package):
    """Returns some Info about the package."""
    
    width=25
    
    s = "--- Package information. ---\n"
    s += "Depends".ljust(width) + "(Version)".rjust(width) +" | " + "Installed\n"
    s += "".zfill(2*width).replace("0", "=")+"-+-"+"".zfill(width).replace("0", "=") +"\n"
    
    depends = getDepends(package)
    if not depends:
        return s
    
    alternative = False
    for packagestring in depends:
        split = packagestring.split(" ", 1)
        if len(split) > 1:
            depname, depversion = split
        else:
            depname = split[0]
            depversion = ""
        
        if depname.startswith("|"):
            alternative = True
            depname = depname.lstrip("|")
            
        instversion = getInstalledPackageVersion(depname)
        
        if alternative:
            depname = " OR "+depname
            alternative = False
        
        s += depname.ljust(width) +depversion.rjust(width)+" | "+ instversion + "\n"
    
    return s
    

def getInstalledPackageVersion(package):
    """Returns the version of package, if installed or empty string not installed"""
    
    out = commands.getoutput("dpkg --status %s 2>/dev/null" % package)
    version = re.findall("^Version:\s(.*)$", out, re.MULTILINE)
    
    if version:
        return version[0]
    else:
        return ""


def getDepends(package):
    """Returns strings of all the packages the given package depends on. The format is like:
       ['libapt-pkg-libc6.3-6-3.11', 'libc6 (>= 2.3.6-6)', 'libstdc++6 (>= 4.1.1-12)']"""

    out = commands.getoutput("dpkg --print-avail %s 2>/dev/null" % package)
    depends = re.findall("^Depends:\s(.*)$", out, re.MULTILINE)
    
    if depends:
        depends = depends[0]
    else:
        depends = ""
    
    depends = depends.replace("| ", ", |")
    
    list = depends.split(", ")
    return list


def getDebianReleaseInfo():
    """Returns a string with Debian relevant info."""
    
    debinfo = ''
    mylist = []
    output = commands.getoutput('apt-cache policy 2>/dev/null')
    if output:
        mre = re.compile('\s+(\d+)\s+.*$\s+release\s.*a=(.*?),.*$\s+origin\s(.*)$', re.MULTILINE)
        for match in mre.finditer(output):
            try:
                mylist.index(match.groups())
            except:
                mylist.append(match.groups())
    
    mylist.sort(reverse=True)

    if os.path.exists('/etc/debian_version'):
        debinfo += 'Debian Release: %s\n' % file('/etc/debian_version').readline().strip()

    for i in mylist:
        debinfo += "%+5s %-15s %s \n" % i

    return debinfo



def callBrowser(url):
    """Calls an external Browser to upen the URL."""
    
    webbrowser.open(url)
    
    
if __name__ == "__main__":
    print getSystemInfo()
    print getDebianReleaseInfo()
    print getPackageInfo("icedove")
    print getPackageInfo("wordpress")
    
