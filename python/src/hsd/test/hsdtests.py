#from collections import OrderedDict

# Action flags
OPEN = 1
CLOSE = 2
TEXT = 3
ERROR = 4

##
# HSD input examples = List of pair tuples.
# First element: List of alternative HSD inputs which should result in the
# same parser event chain. The first must be as printed by HSDFormatter.
# Second element: List of HSD-parser event generated by the HSD-inputs.
#

# Input without options.
hsdtests_simple = [
    # Tag without value
    ([ "test {}", "test{}", "test { }",  "test{\n}",  "test {\n\n }" ],
     [ (OPEN, "test", {}), (CLOSE, "test") ]),     
    # Tag with bracketed value 
    ([ "test {\n12\n}", "test{12}", "test{\n12}" ],
     [ (OPEN, "test", {}), (TEXT, "12"), (CLOSE, "test") ]),     
    # Tag with equaled value
    ([ "test = 12", "test=12", " test =   12" ],
     [ (OPEN, "test", {"_hsd_equal": "1"}), (TEXT, "12"), (CLOSE, "test") ]),     
    # Tag with text         
    ([ """Geometry = GenFormat {
2  S
  Ga As
  1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
}"""],
     [ (OPEN, "Geometry", {"_hsd_equal": "1"}), (OPEN, "GenFormat", {}),
       (TEXT, """2  S
  Ga As
  1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00"""),
       (CLOSE, "GenFormat"), (CLOSE, "Geometry") ]),
    ]

# Input with default attributes
hsdtests_defattr = [
    # Tag with default option
    ([ "test [value] {}" ],
     [ (OPEN, "test", {"unit": "value"}), (CLOSE, "test") ]),     
    # Tag with default option and value
    ([ "test [value] {\n12\n}", "test [value] { 12 }" ],
     [ (OPEN, "test", {"unit": "value"}), (TEXT, "12"), (CLOSE, "test") ]),          
    # Simple tag with option and value
    ([ "temperature [kelvin] = 300" ],
     [ (OPEN, "temperature", {"unit": "kelvin", "_hsd_equal": "1"}),
       (TEXT, "300"), (CLOSE, "temperature")]),      
    ([ "test [unit=Kelvin, dimension=3] {}", "test [unit=Kelvin, \n dimension=3] {}" ],
     [ (OPEN, "test", {"unit": "Kelvin","dimension":"3"}), (CLOSE, "test") ]),
    ([ "test [unit=Kelvin, dimension=3] {}" ],
     [ (OPEN, "test", {"unit": "Kelvin","dimension":"3"}), (CLOSE, "test") ]),
    ([ "test [unit=Kelvin, dimension=3] {\n}" ],
     [ (OPEN, "test", {"unit": "Kelvin","dimension":"3"}), (CLOSE, "test") ]),
    ]

# Explicit attributes
hsdtests_expattr = [                    
    # Tag with explicit option 
    ([ "test [option=value] {}" ],
     [ (OPEN, "test", {"option": "value"}), (CLOSE, "test") ]),
    # Two tags with options
    ([ "test [option=value] {}\ntemperature [kelvin] = 300" ],
     [ (OPEN, "test", {"option": "value",}), (CLOSE, "test"),
       (OPEN, "temperature", {"default": "kelvin", "_hsd_equal": "1"}),
       (TEXT, "300"), (CLOSE, "temperature")]),
    ]
