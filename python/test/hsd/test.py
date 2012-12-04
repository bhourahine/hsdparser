import unittest
import test_parser
import test_formatter

runner = unittest.TextTestRunner()
runner.run(unittest.TestSuite(test_parser.getsuites()
                              + test_formatter.getsuites()))
