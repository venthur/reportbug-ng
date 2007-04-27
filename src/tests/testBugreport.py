import unittest

from lib.Bugreport import Bugreport

class BugreportTestCase(unittest.TestCase):
    
    def setUp(self):
        self.nr = "12345"
        self.summary="my summary"
        self.submitter="my submitter"
        self.status="my status"
        self.severity="my severity"
        self.fulltext="my fulltext"
        self.package="my package"
        
        self.bugreport = Bugreport(self.nr, self.summary, self.submitter, self.status, self.severity, self.fulltext, self.package)

    def testInit(self):
        """Initializing Bugreport with parameters must assign the correct values."""
        
        self.failUnless(self.bugreport.nr == self.nr and 
                        self.bugreport.summary == self.summary and
                        self.bugreport.submitter == self.submitter and
                        self.bugreport.status == self.status and
                        self.bugreport.severity == self.severity and
                        self.bugreport.fulltext == self.fulltext and
                        self.bugreport.package == self.package
                        )

    def testStr(self):
        """Bugreport.__str__ must have defined form."""
        s = self.package+" #"+self.nr +": "+ self.summary+" --- "+self.status+", "+self.severity+""
        self.failUnless(s == str(self.bugreport))


suite = unittest.makeSuite(BugreportTestCase)
