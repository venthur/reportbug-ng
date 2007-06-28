import unittest

from lib import DebianBTS

class DebianBTSTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    

    def test_length_of_get_bugs_by_maintainer(self):
        """Soap answer should equal html answer for bugs by maintainer."""
        query = "venthur@debian.org"
        htmllist = DebianBTS.getBugsByQuery(query, 'html')
        soaplist = DebianBTS.getBugsByQuery(query, 'soap')
        self.failUnless(len(htmllist) == len(soaplist))


    def test_length_of_get_bugs_by_submitter(self):
        """Soap answer should equal html answer for bugs by submitter."""
        query = "from:venthur@debian.org"
        htmllist = DebianBTS.getBugsByQuery(query, 'html')
        soaplist = DebianBTS.getBugsByQuery(query, 'soap')
        self.failUnless(len(htmllist) == len(soaplist))


    def test_length_of_get_bugs_by_package(self):
        """Soap answer should equal html answer for bugs by package."""
        query = "reportbug-ng"
        htmllist = DebianBTS.getBugsByQuery(query, 'html')
        soaplist = DebianBTS.getBugsByQuery(query, 'soap')
        self.failUnless(len(htmllist) == len(soaplist))
    
    
    def test_length_of_get_bugs_by_srcpackage(self):
        """Soap answer should equal html answer for bugs by src-package."""
        query = "src:reportbug-ng"
        htmllist = DebianBTS.getBugsByQuery(query, 'html')
        soaplist = DebianBTS.getBugsByQuery(query, 'soap')
        self.failUnless(len(htmllist) == len(soaplist))

    
    def test_soap_equals_html_status(self):
        """Soap answer should be the same as the html answer."""
        hbug = DebianBTS.getBugsByQuery("224422", 'html')[0]
        sbug = DebianBTS.getBugsByQuery("224422", 'soap')[0]
        self.failUnlessEqual(hbug.nr, sbug.nr)
        self.failUnlessEqual(hbug.summary, sbug.summary)
        
        
    def test_none_soap_bug(self):
        """Should return an empty list for query against nonexistent package."""
        sbug = DebianBTS.getBugsByQuery('AABBCC')
        self.failUnlessEqual(len(sbug), 0)
        
    
    def test_get_one_soap_bug(self):
        """Should return a list with one Bugreport."""
        l = DebianBTS.getBugsByQuery("224422", "soap")
        self.failUnlessEqual(len(l), 1)


#    def test_get_two_soap_bugs(self):
#        """Should return a list with two Bugreports."""
#        l = DebianBTS.getBugsByQuery("224422, 112211", "soap")
#        self.failUnlessEqual(len(l), 2)
        
    
    def testRegression421866(self):
        """When getting all bugs for package 'foo', then all returned bugs 
        should belong to package 'foo'."""
        bugs = DebianBTS.getBugsByQuery("k3b")
        for bug in bugs:
            self.failUnless(bug.package == 'k3b', bug.package+" doesn't match k3b. Bugnr: "+bug.nr)
        

suite = unittest.makeSuite(DebianBTSTestCase)
