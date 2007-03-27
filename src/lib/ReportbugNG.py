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
import urllib
import thread


VERSION = "0.2007.03.24"

RFC_MAILTO = '"mailto:%(to)s?subject=%(subject)s&body=%(body)s"'
MUA_SYNTAX = {
    "icedove" : 'icedove -compose ' + RFC_MAILTO,
    "iceape" : 'iceape -compose ' + RFC_MAILTO,
    "evolution" : 'evolution ' + RFC_MAILTO,
    "kmail" : 'kmail --composer --subject "%(subject)s" --body "%(body)s" "%(to)s"',
    "opera" : 'opera -newpage ' + RFC_MAILTO,
    "sylpheed" : 'sylpheed --compose ' + RFC_MAILTO,
    "sylpheed-claws" : 'sylpheed-claws --compose ' + RFC_MAILTO,
    "sylpheed-claws-gtk2" : 'sylpheed-claws-gtk2 --compose ' + RFC_MAILTO,
    "mutt" : 'mutt ' + RFC_MAILTO,
    "pine" : 'pine -url ' + RFC_MAILTO,
    "googlemail" : 'https://gmail.google.com/gmail?view=cm&cmid=0&fs=1&tearoff=1&to=%(to)s&su=%(subject)s&body=%(body)s'
              }

MUA_NO_URLQUOTE = ["kmail"]            # Don't do urllib.quote their strings
MUA_NEEDS_TERMINAL = ["mutt", "pine"]  # 
WEBMAIL = ["googlemail"]               # Call Browser

SUPPORTED_MUA = MUA_SYNTAX.keys()
SUPPORTED_MUA.sort()

def prepareMail(mua, to, subject, body):
    """Tries to call MUA with given parameters"""
    
    mua = mua.lower()
    
    if mua not in MUA_NO_URLQUOTE:
        subject = urllib.quote(subject.encode("ascii", "replace"))
        body = urllib.quote(body.encode("ascii", "replace"))
    else:
        to = to.encode("ascii", "replace")
        subject = subject.encode("ascii", "replace")
        body = body.encode("ascii", "replace")
    
    
    command = MUA_SYNTAX[mua] % {"to":to, "subject":subject, "body":body}
    
    if mua in MUA_NEEDS_TERMINAL:
        command = "x-terminal-emulator -e "+command

    if mua in WEBMAIL:
        callBrowser(command)
    elif not commands.getstatusoutput(command)[0] == 0:
        print "Reportbug was not able to start your mailclient."
        print "Please copy-paste the following text to your mailclient and send it to submit@bugs.debian.org"
        print body
    
    
def prepareBody(package, version, severity=None, tags=[]):
    """Prepares the empty bugreport."""
    
    s = ""
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

    return s

def getSystemInfo():
    """Returns some hopefully usefull sysinfo"""
    
    s = "--- System information. ---\n"
    s += "Architecture: %s\n" % commands.getoutput("dpkg --print-installation-architecture 2>/dev/null")
    s += "Kernel:       %s\n" % commands.getoutput("uname -sr 2>/dev/null")
    
    return s


def getPackageInfo(package):
    """Returns some Info about the package."""
    
    pwidth = len("Depends ")
    vwidth = len("(Version) ")

    s = "--- Package information. ---\n"
    
    depends = getDepends(package)
    if not depends:
        return "Package depends on nothing."
    
    plist = []
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
        
        if pwidth < len(depname):
            pwidth = len(depname)
        if vwidth < len(depversion):
            vwidth = len(depversion)
            
        plist.append(depname)
    
    instversions = getInstalledPackageVersions(plist)
    
    pwidth += len(" OR ")
    vwidth += 1

    s += "Depends".ljust(pwidth) + "(Version)".rjust(vwidth) +" | " + "Installed\n"
    s += "".zfill(pwidth).replace("0", "=")+"".zfill(vwidth).replace("0", "=")+"-+-"+"".zfill(vwidth).replace("0", "=") +"\n"
    
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
            
        if alternative:
            alternative = False
            s += (" OR "+depname).ljust(pwidth) +depversion.rjust(vwidth)+" | "+ instversions[depname] + "\n"
        else:
            s += depname.ljust(pwidth) +depversion.rjust(vwidth)+" | "+ instversions[depname] + "\n"
    
    return s


def getInstalledPackageVersion(package):
    """Returns the version of package, if installed or empty string not installed"""
    
    out = commands.getoutput("dpkg --status %s 2>/dev/null" % package)
    version = re.findall("^Version:\s(.*)$", out, re.MULTILINE)
    
    if version:
        return version[0]
    else:
        return ""


def getInstalledPackageVersions(packages):
    """Returns a dictionary package:version."""
    
    result = {}
    
    packagestring = ""
    for i in packages:
        packagestring += " "+i
        result[i] = ""
    
    out = commands.getoutput("dpkg --status %s 2>/dev/null" % packagestring)
    
    packagere = re.compile("^Package:\s(.*)$", re.MULTILINE)
    versionre = re.compile("^Version:\s(.*)$", re.MULTILINE)
    
    for line in out.splitlines():
        pmatch = re.match(packagere, line)
        vmatch = re.match(versionre, line)
        
        if pmatch:
            package = pmatch.group(1)
        if vmatch:
            version = vmatch.group(1)
            result[package] = version
    
    return result


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


def getSourceName(package):
    """Returns source package name for given package."""
    
    out = commands.getoutput("dpkg --print-avail %s 2>/dev/null" % package)
    source = re.findall("^Source:\s(.*)$", out, re.MULTILINE)
    
    if source:
        return source[0]
    else:
        return package


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

    thread.start_new_thread(webbrowser.open, (url,))


if __name__ == "__main__":
    #print getSystemInfo()
    #print getDebianReleaseInfo()
    #for package in "icedove", "wordpress", "foo":
    #    print getPackageInfo(package)
    
    print "*** Supportet MUAs: ***"
    print SUPPORTED_MUA
    for mua in MUA_SYNTAX:
        print mua.title().ljust(15), MUA_SYNTAX[mua] % {"to":"foo@example.com", "subject":"my subject", "body":"some body"}
    
    
