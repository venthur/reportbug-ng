import unittest

import tests.testBugreport
import tests.testDebianBTS
import tests.testReportbugNG


allTests = unittest.TestSuite()
allTests.addTest(tests.testBugreport.suite)
allTests.addTest(tests.testDebianBTS.suite)
allTests.addTest(tests.testReportbugNG.suite)

unittest.TextTestRunner(verbosity=2).run(allTests)
