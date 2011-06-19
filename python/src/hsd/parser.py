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
        self._signs = ["=", "{", "}", ";", "#", "[", "]", "'", '"', ","]
        self._checksigns = [ True, True, True, True, True, True, True, True,
                            True, False ]
        self._currenttags = []
        self._currenttags_flags = []
        self._brackets = 0
        self._argument = ""
        self._options = {}
        self._key = ""
        self._quote = ""
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
        if len(options) > 0:
            print("Start Tag: ", tagname, " with options: ", options)
        else:
            print("Start Tag: ", tagname)
    
    def close_handler(self, tagname):
        """Handler which is called when a tag is closed.
        
        The default implementation is to print the tag name which had been
        closed. It should be overriden in the application to handle the
        event in a customized way.
        
        Args:
            tagname: Name of the tag which had been closed.
        """ 
        print("Close Tag: ", tagname)
    
    def text_handler(self, text):
        """Handler which is called with the text found inside a tag.
        
        The default implementation is to print the text. It should be overriden
        in the application to handle the event in a customized way.
        
        Args:
           text: Text in the current tag.
        """
        print("Text: ", text)
        
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
        sign, current = find_first_occurrence(current, self._signs,
                                              self._checksigns)
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
                self._starttag(current[0],True)
            else:
                self._starttag(current[0])
            #Count bracket
            self._brackets += 1
            #Continue parsing
            self._parse(current[1])
            
        elif sign == "}":
            #Display _text
            if self._argument != "":
                self._text(self._argument)
            elif len(current[0].strip())>0:
                self._text(current[0])
            #Close tag
            self._closetag()
            #Count bracket
            self._brackets -= 1
            #Continue parsing
            self._parse(current[1])
            
        elif sign == ";":
            self._flag_equalsign = False
            if len(current[0].strip()) > 0:
                self._text(current[0])
            self._closetag()
            self._parse(current[1])
            
        elif sign == "#":
            pass
        
        elif sign == "[":
            self.buffer = current[0]
            self._altersigns([ False, False, False, False, False, False, True,
                              False, False, False ])
            self._parse(current[1])
            
        elif sign == "]":
            self._parseoption(current[0])
            self._altersigns([ True, True, True, True, True, True, True, True,
                              True, False ])
            self._flag_options = True
            self._parse(current[1])
            
        elif sign == "'":
            if self._flag_quote:
                self._altersigns([ True, True, True, True, True, True, True,
                                  True, True, False ])
                self._flag_quote = False
                self._quote += current[0]
                self._parse(current[1])
            else:
                self._altersigns([ False, False, False, False, False, False,
                                  False, True, False, False ])
                self._flag_quote = True
                self._parse(current[1])
                
        elif sign == '"':
            if self._flag_quote:
                self._altersigns([ True, True, True, True, True, True, True,
                                  True, True, False ])
                self._flag_quote = False
                self._quote += current[0]
                self._parse(current[1])
                
            else:
                self._altersigns([ False, False, False, False, False, False, 
                                  False, False, True, False ])
                self._flag_quote = True
                self._parse(current[1])
                
        else:
            if self._flag_equalsign:
                self._flag_equalsign = False
                if(len(current.strip())>0) or self._quote != "":
                    self._text(current)
                self._closetag()
            elif self._brackets != 0:
                self._argument += current
            if self._flag_quote:
                self._quote += current

    def _altersigns(self, new_values):
        for jj in range(len(new_values)):
            self._checksigns[jj] = new_values[jj]
            
    def _text(self, text):
        if self._quote != "":
            #Call event handler
            self.text_handler(self._quote)
            self._quote = ""
        else:
            text = text.strip()
            #Call event handler
            self.text_handler(text)
            
    def _starttag(self, tagname, flag_tag=False):
        #Reset self._argument
        self._argument = ""
        tagname = tagname.strip()
        #Call event handler
        self.start_handler(tagname, self._options)
        if len(self._options) > 0:
            self._options = {}
        self._currenttags.append(tagname)
        self._currenttags_flags.append(flag_tag)
        
    def _closetag(self):
        #Reset self._argument
        self._argument = ""
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
        self._altersigns([ True, False, False, False, False, False, False,
                          False, False, True ])
        sign, current = find_first_occurrence(option,
                                              self._signs, self._checksigns)
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
            self._altersigns([ True, True, True, True, True, True, True, True,
                              True, False ])            
            
            
def find_first_occurrence(current, signs, check_signs):
    """Finds the first occurance of given symbols."""
    pos = []
    sign = None
    minpos = len(current)
    for aa in range(len(signs)):
        if check_signs[aa]:
            pos.append(current.find(signs[aa]))
    for aa in range(len(pos)):
        if pos[aa] != -1 and pos[aa] < minpos:
            minpos = pos[aa]
    if minpos == len(current):
        return None, current
    else:
        sign = current[minpos]
        current = current.split(sign,1)
        return sign, current


if __name__ == "__main__":
    pass