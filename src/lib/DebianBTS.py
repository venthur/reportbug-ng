# DebianBTS.py - Some helper functions working with Debian's BTS.
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


from Bugreport import Bugreport
import ReportbugNG

import urllib
import re
from HTMLParser import HTMLParser


BTS_URL = "http://bugs.debian.org/"
BTS_CGIBIN_URL = BTS_URL + "cgi-bin/"

#BUG_RE = "<a href=\"bugreport.cgi\?bug=([0-9]*)\">"
BUG_RE = "<a href=\"bugreport.cgi\?bug=[0-9]*\">(.*)</a>"

BUG_SUMMARY_RE = "<br>(.*)</h1>"

def getBugsByPackage(package):
    """Returns a list of bugs belonging to the package."""

    # This will get way too much unrelated bugs (a query for "kate" will return all bugs belonging to kdebase)
    # srcpackage = ReportbugNG.getSourceName( package.encode("ascii", "replace") )
    # report = urllib.urlopen(str(BTS_URL) +"src:"+ srcpackage)
    report = urllib.urlopen(str(BTS_URL) + package.encode("ascii", "replace"))

    # Parse :/
    bugs = []
    currentStatus = ""
    currentSeverity = ""
    pattern = re.compile(BUG_RE)
    status_severity_re = re.compile("<h2.*?><a.*?></a>(.*) bugs -- (.*?) .*</h2>", re.IGNORECASE)
    for line in report:
        match = status_severity_re.match(line)
        if match:
            currentStatus = match.groups()[0]
            currentSeverity = match.groups()[1]
        
        
        match = pattern.findall(line)
        if match:
              for line in match:
                  nr = re.findall("#([0-9]*):\ .*", line)
                  summary = re.findall("#[0-9]*:\ (.*)", line)

                  bug = Bugreport(unicode(nr[0], "utf-8"))
                  bug.summary = unicode(summary[0], "utf-8")
        
                  bug.status = unicode(currentStatus, "utf-8")
                  bug.severity = unicode(currentSeverity, "utf-8")
                  # don't fetch the fulltext yet in order to improve execution speed
                  #bug.fulltext = self.getFullText(bugnr)
        
                  bugs.append(bug)
        
    return bugs


def getSummary(bugnr):
    """Returns the summary of the bugreport"""
    
    report = urllib.urlopen(str(BTS_URL) + str(bugnr))
    pattern = re.compile(BUG_SUMMARY_RE, re.IGNORECASE)
    tmp = []
    for line in report:
        match = pattern.findall(line)
        if match:
            return match[0]

    return None
    
def getFullText(bugnr):
    """Returns the full bugreport"""
    report = urllib.urlopen(str(BTS_URL) + str(bugnr))

    parser = HTMLStripper()
    parser.feed(unicode(report.read(), "utf-8"))
    parser.close()
    return parser.result


class HTMLStripper(HTMLParser):
    """Strips all unwanted tags from given HTML/XML String"""
    
    invalid_tags = ('img')
   
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = ""
  
    def handle_data(self, data):
        self.result = self.result + data
    
    def handle_starttag(self, tag, attrs):
        if not tag in self.invalid_tags:       
            self.result += '<' + tag
            for k, v in attrs:
                self.result += ' %s="%s"' % (k, v)
            self.result += '>'
        else:
            self.result += "<p>[ %s-tag removed by reportbug-ng ]</p>" % tag
            
    def handle_endtag(self, tag):
        if not tag in self.invalid_tags:
            self.result = "%s</%s>" % (self.result, tag)
