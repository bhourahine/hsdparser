import unittest
import io
from hsd.formatter import HSDFormatter
import hsdtests


class FormatterTestCase(unittest.TestCase):
    """Launches a formatter, invokes various formatter events and checks whether
    the produced text equals the reference. The class variable _tests contains 
    list of pair-tuples. Each tuple contains a list of the equivalent texts
    (the first one is taken as refence) and a list of events which should
    produce the text in the reference.
    """ 
    _tests = []
        
    def _process(self, commands):
        """Processes the commands and returns the resulting string."""
        stream = io.StringIO()
        formatter = self._launch_formatter(stream)
        for commandtuple in commands:
            if commandtuple[0] == hsdtests.OPEN:
                formatter.start_tag(commandtuple[1], commandtuple[2])
            elif commandtuple[0] == hsdtests.TEXT:
                formatter.text(commandtuple[1])
            else:
                formatter.close_tag(commandtuple[1])
        return stream.getvalue()
    
    def _launch_formatter(self, stream):
        """Launches HSD formatters with given output stream for the tests."""
        return HSDFormatter(target=stream)
                
    def testTags(self):
        """Produces formatted outputs and testing against reference."""
        for reftxts, commands in self._tests:
            reftxt = reftxts[0]
            txt = self._process(commands)
            self.assertEqual(txt, reftxt,
                             self._geterrormsg(commands, reftxt, txt))
    
    def _geterrormsg(self, commands, reftxt, txt):
        """Creates formatted error message."""
        return "\n".join([ "Failed!", "Command::", str(commands),
                          "Expected text::", reftxt,
                          "Obtained text::", txt])
        
        
class SimpleTestCase(FormatterTestCase):
    _tests = hsdtests.hsdtests_simple

    
class DefaultAttribTestCase(FormatterTestCase):
    
    _tests = hsdtests.hsdtests_defattr
    
    def _launch_formatter(self, stream):
        return HSDFormatter(target=stream, defattrib="unit")
    
    
class ExpAttribTestCase(FormatterTestCase):

    _tests = hsdtests.hsdtests_expattr

    def _launch_formatter(self, stream):
        return HSDFormatter(target=stream, defattrib="default")


def getsuites():
    """Returns the test suites defined in the module."""
    return [ unittest.makeSuite(SimpleTestCase, 'test'),
            unittest.makeSuite(DefaultAttribTestCase, 'test'),
            unittest.makeSuite(ExpAttribTestCase, 'test'),
            ]


if __name__ == "__main__": 
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite(getsuites()))
