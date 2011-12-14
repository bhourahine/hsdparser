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
