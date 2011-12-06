
class HSDException(Exception):
    """Base class for exceptions in the HSD packages."""
    pass


class HSDMissingChildException(HSDException): pass
class HSDInvalidChildException(HSDException): pass
class HSDInvalidValueException(HSDException): pass
class HSDMissingAttributeException(HSDException): pass
class HSDInvalidAttributeException(HSDException): pass
class HSDInvalidAttributeValueException(HSDException): pass


HSDATTR_PROC = "processed"
HSDATTR_EQUAL = "equal"

