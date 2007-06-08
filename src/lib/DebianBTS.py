
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
import htmlentitydefs
import SOAPpy


BTS_URL = "http://bugs.debian.org/"
BTS_CGIBIN_URL = BTS_URL + "cgi-bin/"

SOAP_URL = 'http://bugs.donarmstrong.com/cgi-bin/soap.cgi'
SOAP_NAMESPACE = 'Debbugs/SOAP'
soapServer = SOAPpy.SOAPProxy(SOAP_URL, SOAP_NAMESPACE)


# Some regular expressions to get some info from the html
cluster_re = re.compile("(<H2.*?><a.*?></a>.* bugs -- .*? .*</H2>)")
status_severity_re = re.compile("<H2.*?><a.*?></a>(.*) bugs -- (.*?) .*</H2>")
number_summary_package_re = re.compile("""^<li><a href=\"bugreport.cgi\?bug=[0-9]*\">#([0-9]*): (.*)</a>$
^<br>Package: <a class=\"submitter\" href=\"pkgreport.cgi\?pkg=.*?\">(.*?)</a>.*;$""", re.MULTILINE)


def getBugsByQuery(query):
    """Returns a list of bugs belonging to the query."""

    # First check if the query is just for a single bug, which needs special care:
    if re.match("^[0-9]*$", query):
        return [getSingleBug(query)]

    report = urllib.urlopen(str(BTS_URL) + query.encode("ascii", "replace"))
    s = report.read()
    
    # Parse :/
    bugs = []
     
    cluster = cluster_re.split(s)

    last = None
    for i in cluster:
        match = number_summary_package_re.findall(i)
        if match:
            (status, severity) = status_severity_re.findall(last)[0]
            status = htmlUnescape(status)
            severity = htmlUnescape(severity)
            
            for j in match:
                bug = Bugreport(htmlUnescape(j[0]))
                bug.summary = htmlUnescape(j[1])
                bug.package = htmlUnescape(j[2])
        
                (bug.status, bug.severity) = status, severity
        
                bugs.append(bug)
        last = i
    return bugs


def getSingleBug(bugnr):
    """Returns a single bug"""

    bug = Bugreport(bugnr)
    
    # If no other info is given, the bug is Oustanding/Normal
    bug.status = u"Outstanding"
    bug.severity = u"Normal"
    
    report = urllib.urlopen(str(BTS_URL) + str(bugnr))
    s = report.read()
    
    match = re.findall("<BODY>(.*)</h3>", s, re.DOTALL)
    if match:
        block = match[0]
        
        # Mandatory
        summary = re.findall("^<H1>Debian Bug report logs - .*<BR>(.*)</H1>$", block, re.MULTILINE)
        package = re.findall("^Package: <a class=\"submitter\" href=\"pkgreport.cgi\?pkg=.*\">(.*)</a>;$", block, re.MULTILINE)
        bug.summary = htmlUnescape(summary[0])
        bug.package = htmlUnescape(package[0])
 
        # Optional
        severity = re.findall("^<h3>Severity: (.*);$", block, re.MULTILINE)
        done = re.findall("^<br><strong>Done:</strong>.*$", block, re.MULTILINE)
        if severity:
            # sometimes severity is enclosed by <em></em>, strip it if present
            tmp = severity[0]
            severity = re.findall("^<em .*>(.*)</em>$", tmp, re.MULTILINE)
            if severity:
                bug.severity = htmlUnescape(severity[0])
            else:
                bug.severity = htmlUnescape(tmp)
        if done:
            bug.status = u"Resolved"

    # Get the fulltext 
    parser = HTMLStripper()
    parser.feed(unicode(s, "utf-8"))
    parser.close()
    bug.fulltext = parser.result
    
    return bug


def getFullText(bugnr):
    """Returns the full bugreport"""
    report = urllib.urlopen(str(BTS_URL) + str(bugnr))

    parser = HTMLStripper()
    parser.feed(unicode(report.read(), "utf-8"))
    parser.close()
    return parser.result


def getBugsBySoapQuery(*arg):
    
    bugs = []
    soapServer.soapaction = '%s#get_bugs' % SOAP_NAMESPACE
    list = soapServer.get_bugs(*arg)
    for elem in list:
        bugs.append(Bugreport(elem))
        
    return bugs


class HTMLStripper(HTMLParser):
    """Strips all unwanted tags from given HTML/XML String"""
    
    invalid_tags = ('img')
   
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = ""
  
    def handle_data(self, data):
        self.result += data

    def handle_entityref(self, name):
        self.result += "&"+name+";"

    def handle_charref(self, name):
        self.result += "&#"+name+";"
    
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


htmlquotesre = re.compile('&(' + '|'.join(htmlentitydefs.name2codepoint.keys()) + ');')
def htmlUnescape(s):
    """Unescapes HTML-quotes and returns unicode"""
    return unicode(re.sub(htmlquotesre, lambda m: chr(htmlentitydefs.name2codepoint[m.group(1)]), s), "utf-8")
    