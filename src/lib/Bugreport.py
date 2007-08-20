# Bugreport.py - Represents a Bugreport from Debian's BTS.
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


class Bugreport:
    """Represents a Bugreport from Debian's BTS."""
    
    NR = 1
    SUMMARY = 2
    STATUS = 3
    SEVERITY = 4
    LASTACTION = 5
    
    STATUS_VALUE = {u'outstanding' : 90,
                    u'resolved' : 50,
                    u'archived' : 10}
    
    SEVERITY_VALUE = {u"critical" : 7,
                      u"grave" : 6,
                      u"serious" : 5,
                      u"important" : 4,
                      u"normal" : 3,
                      u"minor" : 2,
                      u"wishlist" : 1
                      }
    
    def __init__(self, nr, summary="", submitter="", status="", severity="", fulltext="", package=""):
        self.nr = unicode(nr)
        self.summary = summary
        self.submitter = submitter
        self.status = status
        self.severity = severity
        self.fulltext = fulltext
        self.package = package
        self.firstaction = "0" # When was the bug reported (in seconds)
        self.lastaction = "0"  # When dit the bug received the last mail

    def __str__(self):
        return self.package+" #"+self.nr +": "+ self.summary+" --- "+self.status+", "+self.severity
    
    def value(self):
        """Returns an 'urgency value', the higher the number, the more urgent
        the bug is. Open bugs generally have higher urgencies than closed ones.
        """
        return self.STATUS_VALUE.get(self.status.lower(), 200) + self.SEVERITY_VALUE.get(self.severity.lower(), 20)
        
    