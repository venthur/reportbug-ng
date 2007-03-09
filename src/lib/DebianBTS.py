from Bugreport import Bugreport

import urllib
import re

BTS_URL = "http://bugs.debian.org/"
#BUG_RE = "<a href=\"bugreport.cgi\?bug=([0-9]*)\">"
BUG_RE = "<a href=\"bugreport.cgi\?bug=[0-9]*\">(.*)</a>"

BUG_SUMMARY_RE = "<br>(.*)</h1>"

def getBugsByPackage(package):
    """Returns a list of bugs belonging to the package."""
 
        # Get all bugs
    report = urllib.urlopen(str(BTS_URL) + package.encode("ascii", "replace"))

    # Parse :/
    pattern = re.compile(BUG_RE)
    tmp = []
    for line in report:
        match = pattern.findall(line)
        if match:
            tmp.extend(match)
    
    bugs = []
    for line in tmp:
        nr = re.findall("#([0-9]*):\ .*", line)
        summary = re.findall("#[0-9]*:\ (.*)", line)

        bug = Bugreport(nr[0])
        bug.summary = summary[0]
        
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
    return report.read()
        