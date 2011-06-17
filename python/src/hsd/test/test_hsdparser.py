import unittest
import io
from hsd.hsdparser import HSDParser

OPEN = 1
CLOSE = 2
TEXT = 3

class ValidInputTestCase(unittest.TestCase):
    
    tests = [
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
        ("test [option=value] {}",
         [(OPEN, "test", {"option": "value"}), (CLOSE, "test") ]),
        # Simple tag with option and value
        ("temperature [kelvin] = 300",
         [(OPEN, "temperature", {"default": "kelvin"}),
          (TEXT, "300"), (CLOSE, "temperature")]),
        # Simple tag         
        ("""Geometry = GenFormat {
              2  S
Ga As
  1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
  2    2    0.13567730000E+01   0.13567730000E+01   0.13567730000E+01
0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
0.27135460000E+01   0.27135460000E+01   0.00000000000E+00
0.00000000000E+00   0.27135460000E+01   0.27135460000E+01
0.27135460000E+01   0.00000000000E+00   0.27135460000E+01
}
            """,
         [(OPEN, "Geometry", {}), (OPEN, "GenFormat", {}),
          (TEXT, """2  S
Ga As
  1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
  2    2    0.13567730000E+01   0.13567730000E+01   0.13567730000E+01
0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
0.27135460000E+01   0.27135460000E+01   0.00000000000E+00
0.00000000000E+00   0.27135460000E+01   0.27135460000E+01
0.27135460000E+01   0.00000000000E+00   0.27135460000E+01"""),
          (CLOSE, "GenFormat"), (CLOSE, "Geometry") ]),
        
        ]
    
    def start_handler(self, tagname, options):
        self.result.append((OPEN, tagname, options))
        
    def close_handler(self, tagname):
        self.result.append((CLOSE, tagname))
        
    def text_handler(self, txt):
        self.result.append((TEXT, txt))
    
    def setUp(self):
        self.parser = HSDParser()
        self.parser.start_handler = self.start_handler
        self.parser.close_handler = self.close_handler
        self.parser.text_handler = self.text_handler
        self.result = []
        
    def testTags(self):
        for content, refres in self.tests:
            self.result = []
            self.parser.feed(io.StringIO(content))
            self.assertEqual(self.result, refres)
                

if __name__ == "__main__":
    unittest.main()
