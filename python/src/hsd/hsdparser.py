import common_functions as functions

class HSDParser:
    
    def __init__(self):
        """Intializes a HSDParser instance.
        """
        self.signs = ["=", "{", "}", ";", "#", "[", "]", "'", '"', ","]
        self.check_signs = [True, True, True, True, True, True, True, True, True, False]
        self.current_tags = []
        self.current_tags_flags = []
        self.brackets = 0
        self.argument = ""
        self.options = {}
        self.key = ""
        self.quote = ""
        #Flags
        self.flag_equalsign = False
        self.flag_options = False
        self.flag_quote = False
        
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
                    
    def _parse(self, current):
        sign, current = functions.find_first_occurence(current, self.signs,
                                                       self.check_signs)
        if self.flag_options:
            self.flag_options = False
            if type(current) != str:
                current[0] = self.buffer
            else:
                current = self.buffer
                
        if sign == "=":
            #Start a new tag
            self._starttag(current[0])
            #Set flag
            self.flag_equalsign = True
            #Continue parsing
            self._parse(current[1])
            
        elif sign == "{":
            #Start a new tag
            if self.flag_equalsign:
                self.flag_equalsign = False
                self._starttag(current[0],True)
            else:
                self._starttag(current[0])
            #Count bracket
            self.brackets += 1
            #Continue parsing
            self._parse(current[1])
            
        elif sign == "}":
            #Display _text
            if self.argument != "":
                self._text(self.argument)
            elif len(current[0].strip())>0:
                self._text(current[0])
            #Close tag
            self._closetag()
            #Count bracket
            self.brackets -= 1
            #Continue parsing
            self._parse(current[1])
            
        elif sign == ";":
            self.flag_equalsign = False
            if len(current[0].strip()) > 0:
                self._text(current[0])
            self._closetag()
            self._parse(current[1])
            
        elif sign == "#":
            pass
        
        elif sign == "[":
            self.buffer = current[0]
            self._altersigns([False, False, False, False, False, False, True, False, False, False])
            self._parse(current[1])
            
        elif sign == "]":
            self._parseoption(current[0])
            self._altersigns([True, True, True, True, True, True, True, True, True, False])
            self.flag_options = True
            self._parse(current[1])
            
        elif sign == "'":
            if self.flag_quote:
                self._altersigns([True, True, True, True, True, True, True, True, True, False])
                self.flag_quote = False
                self.quote += current[0]
                self._parse(current[1])
            else:
                self._altersigns([False, False, False, False, False, False, False, True, False, False])
                self.flag_quote = True
                self._parse(current[1])
                
        elif sign == '"':
            if self.flag_quote:
                self._altersigns([True, True, True, True, True, True, True, True, True, False])
                self.flag_quote = False
                self.quote += current[0]
                self._parse(current[1])
                
            else:
                self._altersigns([False, False, False, False, False, False, False, False, True, False])
                self.flag_quote = True
                self._parse(current[1])
                
        else:
            if self.flag_equalsign:
                self.flag_equalsign = False
                if(len(current.strip())>0) or self.quote != "":
                    self._text(current)
                self._closetag()
            elif self.brackets != 0:
                self.argument += current
            if self.flag_quote:
                self.quote += current

    def _altersigns(self, new_values):
        for jj in range(len(new_values)):
            self.check_signs[jj] = new_values[jj]
            
    def _text(self, text):
        if self.quote != "":
            #Call event handler
            self.text_handler(self.quote)
            self.quote = ""
        else:
            text = text.strip()
            #Call event handler
            self.text_handler(text)
            
    def _starttag(self, tagname, flag_tag=False):
        #Reset self.argument
        self.argument = ""
        tagname = tagname.strip()
        #Call event handler
        self.start_handler(tagname.strip(),self.options)
        if len(self.options) > 0:
            self.options = {}
        self.current_tags.append(tagname)
        self.current_tags_flags.append(flag_tag)
        
    def _closetag(self):
        #Reset self.argument
        self.argument = ""
        #Call event handler
        self.close_handler(self.current_tags[-1])
        del self.current_tags[-1]
        if self.current_tags_flags[-1]:
            del self.current_tags_flags[-1]
            self._closetag()
        else:
            del self.current_tags_flags[-1]
            
    def _error(self):
        if len(self.current_tags) != 0:
            self.error_handler(1)
        elif self.flag_quote:
            self.error_handler(2)
        elif self.brackets != 0:
            self.error_handler(3)
        else:
            self.error_handler(0)
            
    def error_handler(self,error_code):
        #Errorcode 0: Success
        #Errorcode 1: Tag-Error
        #Errorcode 2: Quotation-Error
        #Errorcode 3: Bracket-Error
        if error_code == 0:
            print("Success")
        else:
            print("Error ", error_code)
            
    def _parseoption(self, option):
        self._altersigns([True, False, False, False, False, False, False, False, False, True])
        sign, current = functions.find_first_occurence(option,self.signs, self.check_signs)
        if sign == "=":
            self.key = current[0]
            self._parseoption(current[1])
        elif sign == ",":
            self.options[self.key] = current[0]
            self.key = ""
            self._parseoption(current[1])
        else:
            if self.key != "":
                self.options[self.key] = current
            else:
                self.options["default"] = current
            self._altersigns([True, True, True, True, True, True, True, True, True, False])


if __name__ == "__main__":
        
    fp = open("dftb_pin.hsd", "r")
    parser = HSDParser()
    parser.feed(fp)
    fp.close()
