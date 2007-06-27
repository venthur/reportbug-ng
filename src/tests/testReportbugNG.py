import unittest

from datetime import date

from lib import ReportbugNG

class ReportbugNGTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

suite = unittest.makeSuite(ReportbugNGTestCase)
