import unittest

from lib import DebianBTS

class DebianBTSTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testGetBugsByQuery(self):
        """getBugsByQuery should find all bugs from query."""

        # Check a few packages
        for package in "reportbug-ng", 'gtk-qt-engine', 'debbugs':
            htmllist = DebianBTS.getBugsByQuery(package)
            soaplist = DebianBTS.getBugsBySoapQuery("package", package)
            self.failUnless(len(htmllist) == len(soaplist))

            htmllist = DebianBTS.getBugsByQuery("src:"+package)
            soaplist = DebianBTS.getBugsBySoapQuery("src", package) 
            self.failUnless(len(htmllist) == len(soaplist))

        #
        query = "venthur@debian.org"
        htmllist = DebianBTS.getBugsByQuery(query)
        soaplist = DebianBTS.getBugsBySoapQuery("maint", query) 
        self.failUnless(len(htmllist) == len(soaplist))

        htmllist = DebianBTS.getBugsByQuery("from:"+query)
        soaplist = DebianBTS.getBugsBySoapQuery("submitter", query) 
        self.failUnless(len(htmllist) == len(soaplist))
    
    def testRegression421866(self):
        """When getting all bugs for package 'foo', then all returned bugs should belong to package 'foo'."""
        
        bugs = DebianBTS.getBugsByQuery("k3b")
        for bug in bugs:
            self.failUnless(bug.package == 'k3b', bug.package+" doesn't match k3b. Bugnr: "+bug.nr)
        

suite = unittest.makeSuite(DebianBTSTestCase)
