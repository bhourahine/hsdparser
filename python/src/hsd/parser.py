from hsd.common import HSDParserError, HSDATTR_EQUAL, HSDATTR_LINE
from collections import OrderedDict


__all__ = [ "HSDParserError", "HSDParser",
           "SYNTAX_ERROR", "TAG_ERROR", "QUOTATION_ERROR", "BRACKET_ERROR" ]

SYNTAX_ERROR = 1
TAG_ERROR = 2
QUOTATION_ERROR = 3
BRACKET_ERROR = 4


class HSDParser:
    """Event based parser for the Human-readable Structured Data format.
    
    The methods start_handler, close_handler, text_handler and error_handler
    should be overridden by the actual application.
    """
    
    def __init__(self, defattrib="default"):
        """Intializes a HSDParser instance.
        """
        self._defattrib = defattrib        # def. attribute name
        self._checkstr = "={};#[]'\""      # characters to look for
        self._currenttags = []             # 
        self._currenttags_flags = []
        self._brackets = 0
        self._argument = []
        self._options = OrderedDict()
        self._hsdoptions = OrderedDict()
        self._key = ""
        self._quote = []
        self._curr_line = 0
        self._option_text = []
        #Flags
        self._flag_equalsign = False
        self._flag_options = False
        self._flag_options_text = False
        self._flag_quote = False
        self._flag_syntax = False
        
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
            self._curr_line += 1
        if isfilename:
            fp.close()
        self._error()
        
    def start_handler(self, tagname, options, hsdoptions):
        """Handler which is called when a tag is opened.
        
        The default implementation is to print the tag name and the attributes.
        It should be overriden in the application to handle the event in a
        customized way.
        
        Args:
            tagname: Name of the tag which had been opened.
            options: Dictionary of the options (attributes) of the tag.
            hsdoptions: Dictionary of the options created during the processing
                in the hsd-parser. 
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
        
    def error_handler(self, error_code, error_line=(-1,-1)):
        """Handler which is called if an error was detected during parsing.
        
        The default implementation throws a HSDException or a descendant of it.
        
        Args:
            error_code: Code for signalizing the type of the error. Currently
                implemented codes are:
                    TAG_ERROR: Tag-Error
                    QUOTATION_ERROR: Quotation-Error
                    BRACKET_ERROR: Bracket-Error
            error_line: Lines between the error occurred. Default is (-1,-1)
        """
        error_msg = "Parsing error ({}) between lines {} - {}.".format(
            error_code, error_line[0] + 1, error_line[1] + 1)
        raise HSDParserError(error_msg)
                    
    def _parse(self, current):
        sign, before, after = splitbycharset(current, self._checkstr)
        if self._flag_options:
            self._flag_options = False
            before = self.buffer
    
        if not sign:
            if self._flag_quote:
                self._quote.append(before)
            elif self._flag_equalsign:
                self._flag_equalsign = False
                stripped = before.strip()
                if stripped or self._quote:
                    self._text(stripped)
                self._closetag()
            elif self._brackets:
                if before.strip():
                    self._argument.append(before)
#            if self._flag_quote:
#                self._quote.append(before)
            if self._flag_options_text:
                self._option_text.append(before.strip())
                            
        elif sign == "=":
            # Start a new tag
            self._hsdoptions[HSDATTR_EQUAL] = True
            self._starttag(before)
            # Set flag
            self._flag_equalsign = True
            # Continue parsing
            self._parse(after)
            
        elif sign == "{":
            # Start a new tag
            if self._flag_equalsign:
                self._flag_equalsign = False
                self._starttag(before, True)
            else:
                self._starttag(before)
            # Count bracket
            self._brackets += 1
            # Continue parsing
            self._parse(after)
            
        elif sign == "}":
            # Display _text
            if self._argument:
                self._text("".join(self._argument).strip())
            else:
                stripped = before.strip()
                if stripped or self._quote:
                    self._text(stripped)
            # Close tag
            self._closetag()
            # Count bracket
            self._brackets -= 1
            # Continue parsing
            self._parse(after)
            
        elif sign == ";":
            self._flag_equalsign = False
            stripped = before.strip() 
            if stripped:
                self._text(stripped)
            self._closetag()
            self._parse(after)
            
        elif sign == "#":
            self._text(before)
            self._closetag()
        
        elif sign == "[":
            self._flag_options_text = True
            self.buffer = before
            self._checkstr = "]"
            self._parse(after)
            
        elif sign == "]":
            self._flag_options_text = False
            self._option_text.append(before.strip())
            self._parseoption("".join(self._option_text))
            self._option_text = []
            self._checkstr = "={};#[]'\""
            self._flag_options = True
            self._parse(after)
            
        elif sign == "'":
            if self._flag_quote:
                self._checkstr = "={};#[]'\""
                self._flag_quote = False
                self._quote.append(before)
                self._quote.append("'")
                self._parse(after)
            else:
                self._checkstr = "'"
                self._flag_quote = True
                self._quote = "'"
                self._parse(after)
                
        elif sign == '"':
            if self._flag_quote:
                self._checkstr = "={};#[]'\""
                self._flag_quote = False
                self._quote.append(before)
                self._quote.append('"')
                self._parse(after)
                
            else:
                self._checkstr = '"'
                self._flag_quote = True
                self._quote.append('"')
                self._parse(after)
                            
    def _text(self, text):
        if self._quote:
            # Call event handler
            self.text_handler("".join(self._quote))
            self._quote = []
        else:
            # Call event handler
            self.text_handler(text.strip())
            
    def _starttag(self, tagname, flag_tag=False):
        if(len(tagname.split()) > 1):
            self._flag_syntax = True
            self._error()
        # Reset self._argument
        self._argument = []
        tagname_stripped = tagname.strip()
        # Call event handler
        self._hsdoptions[HSDATTR_LINE] = self._curr_line
        self.start_handler(tagname_stripped, self._options, self._hsdoptions)
        self._options = OrderedDict()
        self._hsdoptions = OrderedDict()
        self._currenttags.append((tagname_stripped, self._curr_line))
        self._currenttags_flags.append(flag_tag)
        
    def _closetag(self):
        if not self._currenttags:
            self.error_handler(1, (0,self._curr_line))
        # Reset self._argument
        self._argument = []
        # Call event handler
        self.close_handler(self._currenttags[-1][0])
        del self._currenttags[-1]
        if self._currenttags_flags[-1]:
            del self._currenttags_flags[-1]
            self._closetag()
        else:
            del self._currenttags_flags[-1]
            
    def _error(self):
        if self._currenttags:
            self.error_handler(TAG_ERROR,
                               (self._currenttags[-1][1], self._curr_line))
        elif self._flag_quote:
            self.error_handler(QUOTATION_ERROR)
        elif self._brackets != 0:
            self.error_handler(BRACKET_ERROR)
        elif self._flag_syntax:
            self.error_handler(SYNTAX_ERROR)
                        
    def _parseoption(self, option):
        self._checkstr = "=,"
        sign, before, after = splitbycharset(option, self._checkstr)
        if not sign:
            if self._key:
                self._key = self._key.strip()
                self._options[self._key] = before
                self._key = ""
            else:
                self._options[self._defattrib] = before
            self._checkstr = "={};#[]'\""  
        elif sign == "=":
            self._key = before
            self._parseoption(after)
        elif sign == ",":
            self._key = self._key.strip()
            self._options[self._key] = before
            self._key = ""
            self._parseoption(after)
            
            
def splitbycharset(txt, charset):
    """Splits a string at the first occurrence of a character in a set.
    
    Args:
        txt: Text to split.
        chars: Chars to look for (specified as string).
        
    Returns:
        (char, before, after) where char is the character from the character
        set which has been found as first; before and after are the substrings
        before and after it. If none of the characters had been found in the
        text, char and after are set to the empty string and before to the 
        entrire string.
    """
    for firstpos, char in enumerate(txt):
        if char in charset:
            break
    else:
        return '',  txt, '' 
    return txt[firstpos], txt[:firstpos], txt[firstpos+1:]

            
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
Test[unit=1,
    dim=3]{}
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
    