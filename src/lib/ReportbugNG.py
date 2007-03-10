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

    s += getSystemInformation()
    s += getDebianReleaseInfo()
            
    s = s.replace("\n", "%0D%0A")
    s = "\"" + s + "\""
    
    return s

def getSystemInformation():
    """Returns some hopefully usefull sysinfo"""
    
    s = "--- System infomation. ---\n"
    
    #list = ("dpkg --print-installation-architecture", 
    #        "uname -srv",
    #        "uname -mpio",
    #        "apt-cache policy | grep Packages$")
    #
    #for cmd in list:
    #    s += "%s:\n" % cmd
    #    s += commands.getoutput("%s 2>/dev/null" % cmd)
    #    s += "\n\n"
    
    s += "Architecture: %s\n" % commands.getoutput("dpkg --print-installation-architecture 2>/dev/null")
    s += "Kernel:       %s\n" % commands.getoutput("uname -sr 2>/dev/null")
    
    return s

def getInstalledPackageVersion(package):
    """Returns the version of package, if installed or empty string not installed"""
    
    try:
        version = commands.getoutput("dpkg --print-avail %s 2>/dev/null | grep Version:" % package).split(": ", 1)[1]
    except:
        version = ""
        
    return version


# Stolen from reportbug, might need improvements.
def getDebianReleaseInfo():
    """Returns a string with Debian relevant info."""
    
    DISTORDER = ['stable', 'testing', 'unstable', 'experimental']
    debvers = debinfo = verfile = warn = ''
    dists = []
    output = commands.getoutput('apt-cache policy 2>/dev/null')
    if output:
        mre = re.compile('\s+(\d+)\s+.*$\s+release\s.*o=(Ubuntu|Debian),a=([^,]+),', re.MULTILINE)
        found = {}
        for match in mre.finditer(output):
            pword, distname = match.group(1, 3)
            if distname in DISTORDER:
                pri, dist = int(pword), DISTORDER.index(distname)
            else:
                pri, dist = int(pword), len(DISTORDER)

            found[(pri, dist, distname)] = True

        if found:
            dists = found.keys()
            dists.sort()
            dists.reverse()
            dists = [(x[0], x[2]) for x in dists]
            debvers = dists[0][1]

    if os.path.exists('/etc/debian_version'):
        verfile = file('/etc/debian_version').readline().strip()

    if verfile:
        debinfo += 'Debian Release: '+verfile+'\n'
    if debvers:
        debinfo += '  APT prefers '+debvers+'\n'
    if dists:
        policystr = ', '.join([str(x) for x in dists])
        debinfo += '  APT policy: %s\n' % policystr
    if warn:
        debinfo += warn

    return debinfo


def callBrowser(url):
    """Calls an external Browser to upen the URL."""
    
    webbrowser.open(url)
    
    
if __name__ == "__main__":
    print getSystemInformation()
    print getDebianReleaseInfo()

