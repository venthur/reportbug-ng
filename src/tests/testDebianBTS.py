import unittest

import SOAPpy

from lib import DebianBTS

class DebianBTSTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testGetBugsByQuery(self):
        """getBugsByQuery should find all bugs from query."""

        url = 'http://bugs.donarmstrong.com/cgi-bin/soap.cgi'
        ns = 'Debbugs/SOAP'
        server = SOAPpy.SOAPProxy(url, ns)
        server.soapaction = '%s#get_bugs' % ns

        for package in "reportbug-ng", 'gtk-qt-engine', 'debbugs':
            htmllist = DebianBTS.getBugsByQuery(package)
            soaplist = server.get_bugs("package", package) 
        
            self.failUnless(len(htmllist) == len(soaplist))

suite = unittest.makeSuite(DebianBTSTestCase)
