import unittest
import io
from hsd.parser import HSDParser

OPEN = 1
CLOSE = 2
TEXT = 3
ERROR = 4

class EventTestCase(unittest.TestCase):
    """Base class for unit tester testing parser events.
    
    Object launches a parser, feeds the texts in tagtests into the parser and
    looks whether the handlers where called in the right order with the right
    arguments. The class variable tagtests contains list of pair-tuples. Each
    tuple contains the text to be feeded into the parser, and a list of
    tuples as returned by the customized handlers which representing the
    expected outcome.
    """

    tagtests = []
    
    def start_handler(self, tagname, options):
        self.result.append((OPEN, tagname, options))
        
    def close_handler(self, tagname):
        self.result.append((CLOSE, tagname))
        
    def text_handler(self, txt):
        self.result.append((TEXT, txt))
        
    def error_handler(self, errorcode):
        self.result.append((ERROR, errorcode))
        
    def launch_parser(self):
        return HSDParser()
    
    def setUp(self):
        self.parser = self.launch_parser()
        self.parser.start_handler = self.start_handler
        self.parser.close_handler = self.close_handler
        self.parser.text_handler = self.text_handler
        self.parser.error_handler = self.error_handler
        self.result = []
        
    def testTags(self):
        for content, refres in self.tagtests:
            self.result = []
            self.parser.feed(io.StringIO(content))
            self.assertEqual(self.result, refres)
            
class ValidInputTestCase(EventTestCase):
    """Contains valid input examples"""
    
    tagtests = [
        # Tag without value
        ("test {}",
         [(OPEN, "test", {}), (CLOSE, "test") ]),
        # Tag with bracketed value 
        ("test { 12 }",
         [(OPEN, "test", {}), (TEXT, "12"), (CLOSE, "test") ]),
        # Tag with equaled value
        ("test = 12",
         [(OPEN, "test", {}), (TEXT, "12"), (CLOSE, "test") ]),
        # Tag with default option
        ("test [value] {}",
         [(OPEN, "test", {"default": "value"}), (CLOSE, "test") ]),         
        # Tag with explicit option 
        #("test [option=value] {}",
        # [(OPEN, "test", {"option": "value"}), (CLOSE, "test") ]),
        # Two tags with options
        #("""test [option=value] {}
#temperature [kelvin] = 300""",
        # [ (OPEN, "test", {"option": "value"}), (CLOSE, "test"),
        #   (OPEN, "temperature", {"default": "kelvin"}), (TEXT, "300"),
        #   (CLOSE, "temperature")]),
        # Simple tag with option and value
        ("temperature [kelvin] = 300",
         [(OPEN, "temperature", {"default": "kelvin"}),
          (TEXT, "300"), (CLOSE, "temperature")]),
        # Tag with text         
        ("""Geometry = GenFormat {
              2  S
Ga As
  1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
}
            """,
         [(OPEN, "Geometry", {}), (OPEN, "GenFormat", {}),
          (TEXT, """2  S
Ga As
  1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00"""),
          (CLOSE, "GenFormat"), (CLOSE, "Geometry") ]),
        ]
    
class DefaultAttribTestCase(EventTestCase):
    """Valid input examples with changed default attribute name."""
    
    tagtests = [
        # Tag with default option
        ("test [value] {}",
         [(OPEN, "test", {"unit": "value"}), (CLOSE, "test") ]),
        # Tag with default option and value
        ("test [value] { 12 }",
         [(OPEN, "test", {"unit": "value"}), (TEXT, "12"), (CLOSE, "test") ]),
        # Tag with default option and value (=)
        #("test [value] = 12 }",
        # [(OPEN, "test", {"unit": "value"}), (TEXT, "12"), (CLOSE, "test") ]),
        ]
    
    def launch_parser(self):
        return HSDParser(defattrib="unit")


if __name__ == "__main__":
    suites = ( unittest.makeSuite(ValidInputTestCase, 'test'),
               unittest.makeSuite(DefaultAttribTestCase, 'test') )
    runner = unittest.TextTestRunner()
    runner.run(unittest.TestSuite(suites))
