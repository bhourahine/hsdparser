import common_functions as functions

class HSDParser:
    
    def __init__(self):
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
        
    def read(self, fileobject):
        if type(fileobject) == str:
            newFile = open(fileobject,"r")
            self.content = self.newFile.readlines()
            newFile.close()
        else:
            self.content = fileobject.readlines()
            
    def feed(self):
        for ii in self.content:
            self.parse(ii)
        self.error()
        
    def parse(self, current):
        sign, current = functions.find_first_occurence(current, self.signs, self.check_signs)
        if self.flag_options:
            self.flag_options = False
            if type(current) != str:
                current[0] = self.buffer
            else:
                current = self.buffer
                
        if sign == "=":
            #Start a new tag
            self.start_tag(current[0])
            #Set flag
            self.flag_equalsign = True
            #Continue parsing
            self.parse(current[1])
            
        elif sign == "{":
            #Start a new tag
            if self.flag_equalsign:
                self.flag_equalsign = False
                self.start_tag(current[0],True)
            else:
                self.start_tag(current[0])
            #Count bracket
            self.brackets += 1
            #Continue parsing
            self.parse(current[1])
            
        elif sign == "}":
            #Display text
            if self.argument != "":
                self.text(self.argument)
            elif len(current[0].strip())>0:
                self.text(current[0])
            #Close tag
            self.close_tag()
            #Count bracket
            self.brackets -= 1
            #Continue parsing
            self.parse(current[1])
            
        elif sign == ";":
            self.flag_equalsign = False
            if len(current[0].strip()) > 0:
                self.text(current[0])
            self.close_tag()
            self.parse(current[1])
            
        elif sign == "#":
            pass
        
        elif sign == "[":
            self.buffer = current[0]
            self.alter_signs([False, False, False, False, False, False, True, False, False, False])
            self.parse(current[1])
            
        elif sign == "]":
            self.parse_option(current[0])
            self.alter_signs([True, True, True, True, True, True, True, True, True, False])
            self.flag_options = True
            self.parse(current[1])
            
        elif sign == "'":
            if self.flag_quote:
                self.alter_signs([True, True, True, True, True, True, True, True, True, False])
                self.flag_quote = False
                self.quote += current[0]
                self.parse(current[1])
            else:
                self.alter_signs([False, False, False, False, False, False, False, True, False, False])
                self.flag_quote = True
                self.parse(current[1])
                
        elif sign == '"':
            if self.flag_quote:
                self.alter_signs([True, True, True, True, True, True, True, True, True, False])
                self.flag_quote = False
                self.quote += current[0]
                self.parse(current[1])
                
            else:
                self.alter_signs([False, False, False, False, False, False, False, False, True, False])
                self.flag_quote = True
                self.parse(current[1])
                
        else:
            if self.flag_equalsign:
                self.flag_equalsign = False
                if(len(current.strip())>0) or self.quote != "":
                    self.text(current)
                self.close_tag()
            elif self.brackets != 0:
                self.argument += current
            if self.flag_quote:
                self.quote += current

    def alter_signs(self, new_values):
        for jj in range(len(new_values)):
            self.check_signs[jj] = new_values[jj]
            
    def text(self, text):
        if self.quote != "":
            #Call event handler
            self.text_handler(self.quote)
            self.quote = ""
        else:
            text = text.strip()
            #Call event handler
            self.text_handler(text)
            
    def start_tag(self, tagname, flag_tag=False):
        #Reset self.argument
        self.argument = ""
        tagname = tagname.strip()
        #Call event handler
        self.start_handler(tagname.strip(),self.options)
        if len(self.options) > 0:
            self.options = {}
        self.current_tags.append(tagname)
        self.current_tags_flags.append(flag_tag)
        
    def close_tag(self):
        #Reset self.argument
        self.argument = ""
        #Call event handler
        self.close_handler(self.current_tags[-1])
        del self.current_tags[-1]
        if self.current_tags_flags[-1]:
            del self.current_tags_flags[-1]
            self.close_tag()
        else:
            del self.current_tags_flags[-1]
            
    def start_handler(self,tagname,option):
        if len(option) > 0:
            print("Start Tag: ", tagname, " with options: ", option)
        else:
            print("Start Tag: ", tagname)
    
    def close_handler(self,tagname):
        print("Close Tag: ", tagname)
    
    def text_handler(self,text):
        print("Text: ", text)
    
    def error(self):
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
            
    def parse_option(self, option):
        self.alter_signs([True, False, False, False, False, False, False, False, False, True])
        sign, current = functions.find_first_occurence(option,self.signs, self.check_signs)
        if sign == "=":
            self.key = current[0]
            self.parse_option(current[1])
        elif sign == ",":
            self.options[self.key] = current[0]
            self.key = ""
            self.parse_option(current[1])
        else:
            if self.key != "":
                self.options[self.key] = current
            else:
                self.options["default"] = current
            self.alter_signs([True, True, True, True, True, True, True, True, True, False])


if __name__ == "__main__":
        
    Datei = open("dftb_pin.hsd", "r")
    #Datei = open("test.dat","r")
    newParser = HSDParser()
    newParser.read(Datei)
    Datei.close()
    newParser.feed()
