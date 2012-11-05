import unittest
import io
from hsd.parser import HSDParser
import hsdtests


class ParserTestCase(unittest.TestCase):
    """Base class for unit tester testing parser events.
    
    Launches a parser, feeds the texts in _tests into the parser and
    looks whether the handlers where called in the right order with the right
    arguments. The class variable _tests contains list of pair-tuples. Each
    tuple contains a list of the equivalent texts to be feeded into the parser,
    and a list of tuples as returned by the customized handlers representing the
    expected outcome.
    """
    _tests = []
    
    def _start_handler(self, tagname, options, hsdoptions):
        hsdoptions.pop("lines")
        self._result.append((hsdtests.OPEN, tagname, options, hsdoptions))
        
    def _close_handler(self, tagname):
        self._result.append((hsdtests.CLOSE, tagname))
        
    def _text_handler(self, txt):
        self._result.append((hsdtests.TEXT, txt))
        
    def _error_handler(self, errorcode, errorpos):
        self._result.append((hsdtests.ERROR, errorcode))
        
    def _launch_parser(self):
        return HSDParser()
    
    def setUp(self):
        self._parser = self._launch_parser()
        self._parser.start_handler = self._start_handler
        self._parser.close_handler = self._close_handler
        self._parser.text_handler = self._text_handler
        self._parser.error_handler = self._error_handler
        self._result = []
        
    def testTags(self):
        for contents, refres in self._tests:
            for content in contents:
                self._result = []
                self._parser.feed(io.StringIO(content))
                self.assertEqual(self._result, refres,
                    self._geterrormsg(content, self._result, refres))
                
    def _geterrormsg(self, content, result, refres):
        return "\n".join([ "Failed!", "Parsed text::", content,
                          "Expected events::", str(refres),
                          "Obtained events::", str(result) ])

                                             
class SimpleTestCase(ParserTestCase):
    _tests = hsdtests.hsdtests_simple

    
class DefaultAttribTestCase(ParserTestCase):

    _tests = hsdtests.hsdtests_defattr

    def _launch_parser(self):
        return HSDParser(defattrib="unit")
    
    
class ExpAttribTestCase(ParserTestCase):
    _tests = hsdtests.hsdtests_expattr
    
class ErrorTestCase(ParserTestCase):
    _tests = hsdtests.hsdtests_error


def getsuites():
    """Returns the test suites defined in the module."""
    return [ unittest.makeSuite(SimpleTestCase, 'test'),
            unittest.makeSuite(DefaultAttribTestCase, 'test'),
            unittest.makeSuite(ExpAttribTestCase, 'test'),
            unittest.makeSuite(ErrorTestCase, 'test')
            ]

if __name__ == "__main__": 
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite(getsuites()))
