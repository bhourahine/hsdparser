from hsd.common import HSDException

__all__ = [ "HSDParserError", "HSDParser"]

class HSDParserError(HSDException):
    pass


class HSDParser:
    """Event based parser for the Human-readable Structred data format.
    
    The methods start_handler, close_handler, text_handler and error_handler
    should be overriden by the actual application.
    """
    
    def __init__(self, defattrib="default"):
        """Intializes a HSDParser instance.
        """
        self._defattrib = defattrib
        self._checkstr = "={};#[]'\"" 
        self._currenttags = []
        self._currenttags_flags = []
        self._brackets = 0
        self._argument = []
        self._options = {}
        self._key = ""
        self._quote = []
        #Flags
        self._flag_equalsign = False
        self._flag_options = False
        self._flag_quote = False
        
    def feed(self, fileobj):
        """Feeds the parser with data.
        
        Args:
            fileobj: File like object or name of a file containing the data.
        """
        isfilename = isinstance(fileobj, str)
        if isfilename:
            fp = open(fileobj, "r")
        else:
            fp = fileobj
        for line in fp.readlines():
            self._parse(line)
        if isfilename:
            fp.close()
        self._error()
        
    def start_handler(self, tagname, options):
        """Handler which is called when a tag is opened.
        
        The default implementation is to print the tag name and the attributes.
        It should be overriden in the application to handle the event in a
        customized way.
        
        Args:
            tagname: Name of the tag which had been opened.
            options: Dictionary of the options (attributes) of the tag. 
        """
        pass
    
    def close_handler(self, tagname):
        """Handler which is called when a tag is closed.
        
        The default implementation is to print the tag name which had been
        closed. It should be overriden in the application to handle the
        event in a customized way.
        
        Args:
            tagname: Name of the tag which had been closed.
        """ 
        pass
    
    def text_handler(self, text):
        """Handler which is called with the text found inside a tag.
        
        The default implementation is to print the text. It should be overriden
        in the application to handle the event in a customized way.
        
        Args:
           text: Text in the current tag.
        """
        pass
        
    def error_handler(self, error_code):
        """Handler which is called if an error was detected during parsing.
        
        The default implementation throws a HSDException or a descendant of it.
        
        Args:
            error_code: Code for signalizing the type of the error. Currently
                following codes are implemented:
                1: Tag-Error
                2: Quotation-Error
                3: Bracket-Error
        """
        raise HSDParserError("Parsing error (%d)" % error_code)        
                    
    def _parse(self, current):
        sign, current = find_first_occurrence(current, self._checkstr)
        if self._flag_options:
            self._flag_options = False
            if type(current) != str:
                current[0] = self.buffer
            else:
                current = self.buffer
                
        if sign == "=":
            #Start a new tag
            self._options["_hsd_equal"] = "1"
            self._starttag(current[0])
            #Set flag
            self._flag_equalsign = True
            #Continue parsing
            self._parse(current[1])
            
        elif sign == "{":
            #Start a new tag
            if self._flag_equalsign:
                self._flag_equalsign = False
                self._starttag(current[0], True)
            else:
                self._starttag(current[0])
            #Count bracket
            self._brackets += 1
            #Continue parsing
            self._parse(current[1])
            
        elif sign == "}":
            #Display _text
            if self._argument:
                self._text("".join(self._argument).strip())
            else:
                stripped = current[0].strip()
                if stripped:
                    self._text(stripped)
            #Close tag
            self._closetag()
            #Count bracket
            self._brackets -= 1
            #Continue parsing
            self._parse(current[1])
            
        elif sign == ";":
            self._flag_equalsign = False
            stripped = current[0].strip() 
            if stripped:
                self._text(stripped)
            self._closetag()
            self._parse(current[1])
            
        elif sign == "#":
            pass
        
        elif sign == "[":
            self.buffer = current[0]
            self._checkstr = "]"
            self._parse(current[1])
            
        elif sign == "]":
            self._parseoption(current[0])
            self._checkstr = "={};#[]'\""
            self._flag_options = True
            self._parse(current[1])
            
        elif sign == "'":
            if self._flag_quote:
                self._checkstr = "={};#[]'\""
                self._flag_quote = False
                self._quote.append(current[0])
                self._parse(current[1])
            else:
                self._checkstr = "'"
                self._flag_quote = True
                self._parse(current[1])
                
        elif sign == '"':
            if self._flag_quote:
                self._checkstr = "={};#[]'\""
                self._flag_quote = False
                self._quote.append(current[0])
                self._parse(current[1])
                
            else:
                self._checkstr = '"'
                self._flag_quote = True
                self._parse(current[1])
                
        else:
            if self._flag_equalsign:
                self._flag_equalsign = False
                stripped = current.strip()
                if stripped or self._quote:
                    self._text(stripped)
                self._closetag()
            elif self._brackets:
                self._argument.append(current)
            if self._flag_quote:
                self._quote.append(current)

    def _text(self, text):
        if self._quote:
            # Call event handler
            self.text_handler("".join(self._quote))
            self._quote = []
        else:
            # Call event handler
            self.text_handler(text)
            
    def _starttag(self, tagname, flag_tag=False):
        # Reset self._argument
        self._argument = []
        tagname_stripped = tagname.strip()
        # Call event handler
        self.start_handler(tagname_stripped, self._options)
        self._options = {}
        self._currenttags.append(tagname_stripped)
        self._currenttags_flags.append(flag_tag)
        
    def _closetag(self):
        #Reset self._argument
        self._argument = []
        #Call event handler
        self.close_handler(self._currenttags[-1])
        del self._currenttags[-1]
        if self._currenttags_flags[-1]:
            del self._currenttags_flags[-1]
            self._closetag()
        else:
            del self._currenttags_flags[-1]
            
    def _error(self):
        if len(self._currenttags) != 0:
            self.error_handler(1)
        elif self._flag_quote:
            self.error_handler(2)
        elif self._brackets != 0:
            self.error_handler(3)
                        
    def _parseoption(self, option):
        self._checkstr = "=,"
        sign, current = find_first_occurrence(option, self._checkstr)
        if sign == "=":
            self._key = current[0]
            self._parseoption(current[1])
        elif sign == ",":
            self._options[self._key] = current[0]
            self._key = ""
            self._parseoption(current[1])
        else:
            if self._key != "":
                self._options[self._key] = current
            else:
                self._options[self._defattrib] = current
            self._checkstr = "={};#[]'\""
            
            
def find_first_occurrence(txt, chars):
    """Finds the first occurrence of given characters in a text.
    
    Args:
        txt: Text to be searched.
        chars: Chars to look for (specified as a string).
        
    Returns:
        (None, txt) if none of the characters was found in text or
        (char, (before, after)), where char is the character which has been
        found, before is the string before, after is the string after.
    """
    for firstpos, char in enumerate(txt):
        if char in chars:
            break
    else:
        return None, txt
    return txt[firstpos], [ txt[:firstpos], txt[firstpos+1:] ]

            

if __name__ == "__main__":
    from io import StringIO
    from hsd.formatter import HSDStreamFormatter, HSDFormatter
    formatter = HSDFormatter(closecomments=True)
    parser = HSDParser(defattrib="unit")
    streamformatter = HSDStreamFormatter(parser, formatter)
    stream = StringIO("""Geometry = GenFormat {
2  S
Ga As
1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
2    2    0.13567730000E+01   0.13567730000E+01   0.13567730000E+01
0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
0.27135460000E+01   0.27135460000E+01   0.00000000000E+00
0.00000000000E+00   0.27135460000E+01   0.27135460000E+01
0.27135460000E+01   0.00000000000E+00   0.27135460000E+01
}

Hamiltonian = DFTB {
  SCC = Yes
  SCCTolerance = 1.0E-007
  MaxSCCIterations = 1000
  Mixer = Broyden {}
  MaxAngularMomentum {
    Ga = "d"
    As = "p"
  }
  Filling = Fermi {
    Temperature [Kelvin] = 1.0E-006
  }
  SlaterKosterFiles [format=old] {
    Ga-Ga = "./Ga-Ga.skf"
    Ga-As = "./Ga-As.skf"
    As-Ga = "./As-Ga.skf"
    As-As = "./As-As.skf"
  }
  KPointsAndWeights {
    0.0 0.0 0.0   1.0
  }
}

Options {
  AtomResolvedEnergies = No
  RestartFrequency = 20
  RandomSeed = 0
  WriteHS = No
}""")
    streamformatter.feed(stream)
    