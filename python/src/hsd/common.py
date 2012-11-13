HSDATTR_PROC = "processed"
HSDATTR_EQUAL = "equal"
HSDATTR_FILE = "file"
HSDATTR_LINE = "lines"

class HSDException(Exception):
    """Base class for exceptions in the HSD packages."""
    pass

    
class HSDQueryError(HSDException):
    """Base class for errors detected by the HSDQuery object.
    
    Attributes:
        filename: Name of the file where error occured (or empty string).
        line: Line where the error occurred (or None).
        tagname: Name of the tag with the error (or empty string).    
    """
    
    def __init__(self, msg="", node=None):
        super().__init__(msg)
        hsdattrib = node.hsdattrib if node is not None else {}
        self.tag = node.tag if node is not None else None
        self.file = hsdattrib.get(HSDATTR_FILE, "")
        self.line = hsdattrib.get(HSDATTR_LINE, None)

class HSDMissingTagException(HSDQueryError): pass
class HSDInvalidTagException(HSDQueryError): pass
class HSDInvalidTagValueException(HSDQueryError): pass
class HSDMissingAttributeException(HSDQueryError): pass
class HSDInvalidAttributeException(HSDQueryError): pass
class HSDInvalidAttributeValueException(HSDQueryError): pass


class HSDParserError(HSDException):
    """Base class for parser related errors."""
    pass


def unquote(txt):
    """Giving string without quotes if enclosed in those."""
    if len(txt) >= 2 and (txt[0] in "\"'") and txt[-1] == txt[0]:
        return txt[1:-1]
    else:
        return txt


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

