# encoding: utf8
# rnghelpers.py - Various helpers for Reportbug-NG.
# Copyright (C) 2007-2014  Bastian Venthur
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
import logging
import ConfigParser
import tempfile

from PyQt5.QtCore import QCoreApplication

import bug


logger = logging.getLogger("ReportbugNG")


RFC_MAILTO = '"mailto:%(to)s?subject=%(subject)s&body=%(body)s"'
MUA_SYNTAX = {
    "default" : 'xdg-email --utf8 --subject "%(subject)s" --body "%(body)s" "%(to)s"',
    "icedove" : 'icedove -compose ' + RFC_MAILTO,
    "iceape" : 'iceape -compose ' + RFC_MAILTO,
    "evolution" : 'evolution ' + RFC_MAILTO,
    "kmail" : 'kmail --composer --subject "%(subject)s" --body "%(body)s" "%(to)s"',
#    "opera" : 'opera -newpage ' + RFC_MAILTO,
    "sylpheed" : 'sylpheed --compose ' + RFC_MAILTO,
    "claws-mail" : 'claws-mail --compose ' + RFC_MAILTO,
    "mutt" : 'mutt ' + RFC_MAILTO,
    "mutt-ng" : 'muttng ' + RFC_MAILTO,
    "pine" : 'pine -url ' + RFC_MAILTO,
#    "googlemail" : 'https://gmail.google.com/gmail?view=cm&cmid=0&fs=1&tearoff=1&to=%(to)s&su=%(subject)s&body=%(body)s'
    'alpine' : 'alpine -url ' + RFC_MAILTO,
              }


def getMUAString(mua):
    """ Return the translated string for the specified MUA."""
    if mua == "default": return QCoreApplication.translate("rnghelpers", "Default")
    if mua == "icedove" : return QCoreApplication.translate("rnghelpers", "Icedove")
    if mua == "iceape" : return QCoreApplication.translate("rnghelpers", "Iceape")
    if mua == "evolution" : return QCoreApplication.translate("rnghelpers", "Evolution")
    if mua == "kmail" : return QCoreApplication.translate("rnghelpers", "KMail")
#   if mua == "opera" : return QCoreApplication.translate("rnghelpers", "Opera")
    if mua == "sylpheed" : return QCoreApplication.translate("rnghelpers", "Sylpheed")
    if mua == "claws-mail" : return QCoreApplication.translate("rnghelpers", "Claws Mail")
    if mua == "mutt" : return QCoreApplication.translate("rnghelpers", "Mutt")
    if mua == "mutt-ng" : return QCoreApplication.translate("rnghelpers", "Mutt NG")
    if mua == "pine" : return QCoreApplication.translate("rnghelpers", "Pine")
#   if mua == "googlemail" : return QCoreApplication.translate("Google")
    # If everything else fails, just return the string we got
    if mua == 'alpine': return QCoreApplication.translate("rnghelpers", "Alpine")
    return mua

MUA_STRINGS = {
              }
# Don't urllib.quote() their strings
MUA_NO_URLQUOTE = ["default", "kmail"]
# Who needs a terminal?
MUA_NEEDS_TERMINAL = ["mutt", "mutt-ng", "pine", 'alpine']
# Who needs a browser?
WEBMAIL = ["googlemail"]

# HACK: don't know the maximum lenght of a command yet
MAX_BODY_LEN = 10000


# Those strings must not be translated!
WNPP_ACTIONS = ("RFP", "ITP", "RFH", "RFA", "O")
SEVERITY = ("Critical", "Grave", "Serious", "Important", "Normal", "Minor", "Wishlist")

def getSeverityExplanation(severity):
    """Return a translated explanation of the severity."""
    if severity == 0: return QCoreApplication.translate("rnghelpers", "Makes unrelated software on the system (or the whole system) break, or causes serious data loss, or introduces a security hole on systems where you install the package.")
    if severity == 1: return QCoreApplication.translate("rnghelpers", "Makes the package in question unusable or mostly so, or causes data loss, or introduces a security hole allowing access to the accounts of users who use the package.")
    if severity == 2: return QCoreApplication.translate("rnghelpers", "Is a severe violation of Debian policy (roughly, it violates a \"must\" or \"required\" directive), or, in the package maintainer's opinion, makes the package unsuitable for release.")
    if severity == 3: return QCoreApplication.translate("rnghelpers", "A bug which has a major effect on the usability of a package, without rendering it completely unusable to everyone.")
    if severity == 4: return QCoreApplication.translate("rnghelpers", "The default value, applicable to most bugs.")
    if severity == 5: return QCoreApplication.translate("rnghelpers", "A problem which doesn't affect the package's usefulness, and is presumably trivial to fix.")
    if severity == 6: return QCoreApplication.translate("rnghelpers", "For any feature request, and also for any bugs that are very difficult to fix due to major design considerations.")
    # if erverything fails return severity:
    return severity


def getRngInstructions():
    """Return translated instructions for reportbug ng."""
    # TODO: use system colors?
    return """<div style="background: #fff; color: #000;" >""" + \
        QCoreApplication.translate("rnghelpers", """<h2>Using Reportbug-NG</h2>
<h3>Step 1: Finding Bugs</h3>
<p>To find a bug just enter a query and press Enter. Combinations of multiple
queries are supported, e.g.: "severity:grave tag:patch".</p>

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
""") + """</div>"""

def getAvailableMUAs():
    """
    Returns a tuple of strings with available MUAs on this system. The Webmails
    are always available, since there is no way to check.
    """
    list = []
    for mua in MUA_SYNTAX:
        if mua in WEBMAIL:
            list.append(mua)
            continue
        command = MUA_SYNTAX[mua].split()[0]
        for p in os.defpath.split(os.pathsep):
            if os.path.exists(os.path.join(p, command)):
                list.append(mua)
                continue
    return list


SUPPORTED_MUA = getAvailableMUAs()
SUPPORTED_MUA.sort()


def prepareMail(mua, to, subject, body, firstcall=True):
    """Tries to call MUA with given parameters."""

    mua = mua.lower()

    if mua not in MUA_NO_URLQUOTE:
        subject = urllib.quote(subject.encode("ascii", "replace"))
        body = urllib.quote(body.encode("ascii", "replace"))
    else:
        to = to.encode("ascii", "replace")
        subject = subject.encode("ascii", "replace")
        body = body.encode("ascii", "replace")

    # If quotes are used for this MUA, escape the quotes in the arguments:
    if '"' in MUA_SYNTAX[mua] and MUA_SYNTAX[mua].count('"')%2 == 0:
        to = to.replace('"', '\\"')
        subject = subject.replace('"', '\\"')
        body = body.replace('"', '\\"')

    command = MUA_SYNTAX[mua] % {"to":to, "subject":subject, "body":body}

    if mua in MUA_NEEDS_TERMINAL:
        command = "x-terminal-emulator -e "+command

    if mua in WEBMAIL:
        callBrowser(command)
    else:
        status, output = callMailClient(command)
        if status == 0:
            return
        # Great, calling the MUA failed, probably due too long output of the
        # /usr/share/bug/$package/script...
        if firstcall == False:
            logger.error("Calling the MUA a second time with an even shorter message failed. Giving up.")
            return
        logger.warning("Grr! Calling the MUA failed. Status and output was: %s, %s. Length of the command is: %s" % (str(status), str(output), str(len(command))))
        body = body[:MAX_BODY_LEN] + "\n\n[ MAILBODY EXCEEDED REASONABLE LENGTH, OUTPUT TRUNCATED ]"
        prepareMail(mua, to, subject, body, False)



def prepareBody(package, version=None, severity=None, tags=[], cc=[], script=True):
    """Prepares the empty bugreport including body and system information."""

    s = prepare_minimal_body(package, version, severity, tags, cc)

    s += getSystemInfo() + "\n"
    s += getDebianReleaseInfo() + "\n"
    s += getPackageInfo(package) + "\n"

    if not script:
        return s

    s2 = getPackageScriptOutput(package) + "\n"
    if len(s+s2) > MAX_BODY_LEN:
        logger.warning("Mailbody to long for os.pipe")
        fd, fname = tempfile.mkstemp(".txt", "reportbug-ng-%s-" % package)
        f = os.fdopen(fd, "w")
        f.write(s2.encode('utf-8', 'replace'))
        f.close()
        s2 = """
-8<---8<---8<---8<---8<---8<---8<---8<---8<--
Please attach the file:
  %s
to the mail. I'd do it myself if the output wasn't too long to handle.

  Thank you!
->8--->8--->8--->8--->8--->8--->8--->8--->8--""" % fname
    s += s2

    return s


def prepare_minimal_body(package, version=None, severity=None, tags=[], cc=[]):
    """Prepares the body of the empty bugreport."""

    s = ""
    s += "Package: %s\n" % package
    if version:
        s += "Version: %s\n" % version
    if severity:
        s += "Severity: %s\n" % severity
    if tags:
        s += "Tags:"
        for tag in tags:
            s += " %s" % tag
        s += "\n"
    for i in cc:
        s += "X-Debbugs-CC: %s\n" % i
    s += "\n"
    s += "--- Please enter the report below this line. ---\n\n\n"

    return s


def prepare_wnpp_body(action, package, version=""):
    """Prepares a WNPP bugreport."""

    s = ""
    s += "Package: wnpp\n"
    if action in ("ITP", "RFP"):
        s += "Severity: wishlist\n"
    else:
        s += "Severity: normal\n"
    s += "X-Debbugs-CC: debian-devel@lists.debian.org\n"

    if action in ("ITP", "RFP"):
        s += """\

--- Please fill out the fields below. ---

   Package name: %(p)s
        Version: %(v)s
Upstream Author: [NAME <name@example.com>]
            URL: [http://example.com]
        License: [GPL, LGPL, BSD, MIT/X, etc.]
    Description: [DESCRIPTION]
""" % {'p': package, 'v': version}
    return s


def prepare_wnpp_subject(action, package, descr):
    if not package:
        package = "[PACKAGE]"
    if not descr:
        descr = "[SHORT DESCRIPTION]"
    return "%s: %s -- %s" % (action, package, descr)


def getSystemInfo():
    """Returns some hopefully useful sysinfo"""

    s = "--- System information. ---\n"
    s += "Architecture: %s\n" % commands.getoutput("dpkg --print-installation-architecture 2>/dev/null")
    s += "Kernel:       %s\n" % commands.getoutput("uname -sr 2>/dev/null")

    return s


def getPackageInfo(package):
    """Returns some Info about the package."""

    pwidth = len("Depends ")
    vwidth = len("(Version) ")

    s = "--- Package information. ---\n"

    plist = bug.report_with(package)
    if len(plist) > 1:
        logger.debug("Reporting with additional packages as requested by maintainers: %s" % str(plist[1:]))

    depends = getDepends(plist)
    s += pretty_print_depends(depends, "Depends")
    s += "\n\n"

    package_status = bug.package_status(package)
    if package_status:
        logging.debug("Reporting wit additional status of packages as requested by maintainers: %s" % str(package_status))
        s += pretty_print_depends(package_status, "Package Status")
        s += "\n\n"

    depends = getRecommends(plist)
    s += pretty_print_depends(depends, "Recommends")
    s += "\n\n"

    depends = getSuggests(plist)
    s += pretty_print_depends(depends, "Suggests")
    s += "\n\n"
    return s


def pretty_print_depends(depends, depstring):
    """Pretty prints dependencies in a table.

    The in the depstring goes: Depends, Suggests or Recommends.
    """

    if not depends:
        return "Package's %s field is empty." % depstring

    pwidth = len(depstring)
    vwidth = len("(Version) ")
    s = ""

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

    s += depstring.ljust(pwidth) + "(Version)".rjust(vwidth) +" | " + "Installed\n"
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


def getPackageScriptOutput(package):
    """Runs the package's script in /usr/share/bug/packagename/script or
    /usr/share/bug/packagename and returns the output."""
    output = ''
    # In the first case the script is called "script", in the second one the
    # script is just the packagename under /usr/share/bug
    path = ["/usr/share/bug/" + str(package) + "/script",
             "/usr/share/bug/" +str(package)]
    xterm_path = "/usr/bin/xterm"
    # pop up a terminal if we can because scripts can be interactive
    if os.path.exists(xterm_path):
        cmd = xterm_path + " -e "
    else:
        logger.error("Xterm not found, cannot start bugscript.")
        cmd = ""
    if os.path.isfile(path[1]):
        cmd += commands.mkarg(path[1]) + " 3>&1"
        output += "--- Output from package bug script ---\n"
        output += commands.getoutput(cmd)
    elif os.path.exists(path[0]):
        cmd += commands.mkarg(path[0]) + " 3>&1"
        output += "--- Output from package bug script ---\n"
        output += commands.getoutput(cmd)
    return unicode(output, errors="replace")


def getInstalledPackageVersion(package):
    """Returns the version of package, if installed or empty string if not installed"""

    out = commands.getoutput("dpkg-query --status %s 2>/dev/null" % package)
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

    out = commands.getoutput("dpkg-query --status %s 2>/dev/null" % packagestring)

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


def getDepends(packagelist):
    """Returns strings of all the packages the given package depends on. The format is like:
       ['libapt-pkg-libc6.3-6-3.11', 'libc6 (>= 2.3.6-6)', 'libstdc++6 (>= 4.1.1-12)']"""

    list = []
    for package in packagelist:
        out = commands.getoutput("dpkg-query --status %s 2>/dev/null" % package)
        depends = re.findall("^Depends:\s(.*)$", out, re.MULTILINE)
        if depends:
            depends = depends[0]
        else:
            continue

        depends = depends.replace("| ", ", |")

        list.extend(depends.split(", "))
    return list


def getSuggests(packagelist):
    """Returns strings of all the packages the given package suggests.
    The format is like:
    ['libapt-pkg-libc6.3-6-3.11', 'libc6 (>= 2.3.6-6)', 'libstdc++6 (>= 4.1.1-12)']"""

    list = []
    for package in packagelist:
        out = commands.getoutput("dpkg-query --status %s 2>/dev/null" % package)
        suggests = re.findall("^Suggests:\s(.*)$", out, re.MULTILINE)
        if suggests:
            suggests = suggests[0]
        else:
            continue

        suggests = suggests.replace("| ", ", |")

        list.extend(suggests.split(", "))
    return list


def getRecommends(packagelist):
    """Returns strings of all the packages the given package recommends.
    The format is like:
    ['libapt-pkg-libc6.3-6-3.11', 'libc6 (>= 2.3.6-6)', 'libstdc++6 (>= 4.1.1-12)']"""

    list = []
    for package in packagelist:
        out = commands.getoutput("dpkg-query --status %s 2>/dev/null" % package)
        recommends = re.findall("^Recommends:\s(.*)$", out, re.MULTILINE)
        if recommends:
            recommends = recommends[0]
        else:
            continue

        recommends = recommends.replace("| ", ", |")

        list.extend(recommends.split(", "))
    return list


def getSourceName(package):
    """Returns source package name for given package."""

    out = commands.getoutput("dpkg-query --status %s 2>/dev/null" % package)
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


def get_presubj(package):
    path = "/usr/share/bug/" + str(package) + "/presubj"
    if not os.path.exists(path):
        return None
    f = file(path)
    c = f.read()
    f.close()
    return c


def callBrowser(url):
    """Calls an external Browser to upen the URL."""

    # Try to find user's preferred browser via xdg-open. If that fails
    # (xdg-utils not installed or some other error), fall back to pythons
    # semi optimal solution.
    logger.debug("Just before xdg-open")
    status, output = commands.getstatusoutput('xdg-open "%s"' % url)
    logger.debug("After xdg-open")
    if status != 0:
        logger.warning("xdg-open %s returned (%i, %s), falling back to python's webbrowser.open" % (url, status, output))
        logger.debug("Just before webbrowser.open")
        thread.start_new_thread(webbrowser.open, (url,))
        logger.debug("After webbrowser.open")


def callMailClient(command):
    """
    Calls the external mailclient via command and returns the tuple:
    (status, output)
    """
    logger.debug("Just before the MUA call: %s" % str(command))
    status, output = commands.getstatusoutput(command)
    logger.debug("After the  MUA call")
    return status, output

def translate_query(query):
    """Translate query to a query the SOAP interface accepts.

    Complex queries are seperated by one or more spaces:
    "somepackage severity:normal tag:patch"
    """

    queries = query.split()
    logger.debug("First split: %s" % queries)
    ans = []
    for q in queries:
        split = q.split(':', 1)
        logger.debug("Nested split: %s" % split)
        if (q.startswith('src:')):
            ans.extend(split)
        elif (q.startswith('from:')):
            ans.extend(['submitter', split[1]])
        elif (q.startswith('severity:')):
            ans.extend(split)
        elif (q.startswith('tag:')):
            ans.extend(split)
        elif (q.find("@") != -1):
            ans.extend(['maint', q])
        elif (re.match("^[0-9]*$", q)):
            ans.extend([None, q])
        else:
            ans.extend(['package', q])
    logger.debug("Translated query to %s" % ans)
    return ans


class Settings(object):
    """A Settings object contains all the settings for reportbug-ng.

    This object supports, loading default values, as well as loading and saving
    the settings to a configfile.
    """

    CONFIGFILE = os.path.expanduser("~/.reportbug-ng")

    def __init__(self, configfile):
        """Initialize Settings object and load defaults."""
        self.configfile = configfile
        self.load_defaults()


    def load_defaults(self):
        """Load default settings."""
        # Users preferred mailclient
        self.lastmua = "default"

        self.script = True
        self.presubj = True

        self.c_wishlist = "#808000"
        self.c_minor = "#008000"
        self.c_normal = "#000000"
        self.c_important = "#ff0000"
        self.c_serious = "#800080"
        self.c_grave = "#800080"
        self.c_critical = "#800080"
        self.c_resolved = "#a0a0a4"

        # Sorting option
        self.sortByCol = 2
        self.sortAsc = False

        # Mainwindow
        self.x = 0
        self.y = 0
        self.width = 800
        self.height = 600
        self.menubar = True

        # ListView
        self.bugnrWidth = 100
        self.packageWidth = 150
        self.summaryWidth = 350
        self.statusWidth = 100
        self.severityWidth = 100
        self.lastactionWidth = 100
        self.hideClosedBugs = True


    def load(self):
        """Load settings from configfile."""
        config = ConfigParser.ConfigParser()
        config.read(self.configfile)
        if config.has_option("general", "lastMUA"):
            self.lastmua = config.get("general", "lastMUA")
        if config.has_option("general", "sortByCol"):
            self.sortByCol = config.getint("general", "sortByCol")
        if config.has_option("general", "sortAsc"):
            self.sortAsc = config.getboolean("general", "sortAsc")

        if config.has_option("general", "script"):
            self.script = config.getboolean("general", "script")
        if config.has_option("general", "presubj"):
            self.presubj = config.getboolean("general", "presubj")

        if config.has_option("general", "wishlist"):
            self.c_wishlist = config.get("general", "wishlist")
        if config.has_option("general", "minor"):
            self.c_minor = config.get("general", "minor")
        if config.has_option("general", "normal"):
            self.c_normal = config.get("general", "normal")
        if config.has_option("general", "important"):
            self.c_important = config.get("general", "important")
        if config.has_option("general", "serious"):
            self.c_serious = config.get("general", "serious")
        if config.has_option("general", "grave"):
            self.c_grave = config.get("general", "grave")
        if config.has_option("general", "critical"):
            self.c_critical = config.get("general", "critical")
        if config.has_option("general", "resolved"):
            self.c_resolved = config.get("general", "resolved")

        if config.has_option("mainwindow", "x"):
            self.x = config.getint("mainwindow", "x")
        if config.has_option("mainwindow", "y"):
            self.y = config.getint("mainwindow", "y")
        if config.has_option("mainwindow", "width"):
            self.width = config.getint("mainwindow", "width")
        if config.has_option("mainwindow", "height"):
            self.height = config.getint("mainwindow", "height")
        if config.has_option("mainwindow", "menubar"):
            self.menubar = config.getboolean("mainwindow", "menubar")

        if config.has_option("listview", "bugnrwidth"):
            self.bugnrWidth = config.getint("listview", "bugnrwidth")
        if config.has_option("listview", "summarywidth"):
            self.summaryWidth = config.getint("listview", "summarywidth")
        if config.has_option("listview", "statuswidth"):
            self.statusWidth = config.getint("listview", "statuswidth")
        if config.has_option("listview", "severitywidth"):
            self.severityWidth = config.getint("listview", "severitywidth")
        if config.has_option("listview", "lastactionwidth"):
            self.lastactionWidth = config.getint("listview", "lastactionwidth")
        if config.has_option("listview", "hideClosedBugs"):
            self.hideClosedBugs = config.getboolean("listview", "hideclosedbugs")


    def save(self):
        """Save settings to configfile."""
        config = ConfigParser.ConfigParser()
        config.read(self.configfile)
        if not config.has_section("general"):
            config.add_section("general")
        config.set("general", "lastMUA", self.lastmua)
        config.set("general", "sortByCol", self.sortByCol)
        config.set("general", "sortAsc", self.sortAsc)

        config.set("general", "script", self.script)
        config.set("general", "presubj", self.presubj)

        config.set("general", "wishlist", self.c_wishlist)
        config.set("general", "minor", self.c_minor)
        config.set("general", "normal", self.c_normal)
        config.set("general", "important", self.c_important)
        config.set("general", "serious", self.c_serious)
        config.set("general", "grave", self.c_grave)
        config.set("general", "critical", self.c_critical)
        config.set("general", "resolved",self.c_resolved)


        if not config.has_section("mainwindow"):
            config.add_section("mainwindow")
        config.set("mainwindow", "x", self.x)
        config.set("mainwindow", "y", self.y)
        config.set("mainwindow", "width", self.width)
        config.set("mainwindow", "height", self.height)
        config.set("mainwindow", "menubar", self.menubar)

        if not config.has_section("listview"):
            config.add_section("listview")
        config.set("listview", "bugnrwidth", self.bugnrWidth)
        config.set("listview", "summarywidth", self.summaryWidth)
        config.set("listview", "statuswidth", self.statusWidth)
        config.set("listview", "severitywidth", self.severityWidth)
        config.set("listview", "lastactionwidth", self.lastactionWidth)
        config.set("listview", "hideclosedbugs", self.hideClosedBugs)

        # Write everything to configfile
        config.write(open(self.configfile, "w"))

