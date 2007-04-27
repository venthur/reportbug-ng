import unittest

from datetime import date

from lib import ReportbugNG

class ReportbugNGTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

    def testVersion(self):
        """RNG's Version should match current date."""
        (crap, year, month, day) = ReportbugNG.VERSION.split(".")
        self.failUnless(date.today().isoformat() == year+"-"+month+"-"+day)

suite = unittest.makeSuite(ReportbugNGTestCase)
