import xml.etree.ElementTree as etree
from hsd.formatter import HSDFormatter

class HSDTree(etree.ElementTree):
    """Wrapper around an entire tree."""  

    def writehsd(self, formatter=None):
        """Writes the tree in HSD format.
        
        Args:
            formatter: Optional formatter object. (default: HSDFormatter(), 
                writing to sys.stdout)
        """
        if formatter is None:
            formatter = HSDFormatter()
        self._writehsd(self.getroot(), formatter)
        
    def _writehsd(self, parent, formatter):
        """Private helper routine for writehsd."""
        if parent.text:
            formatter.text(parent.text)
        else:
            for child in parent:
                formatter.start_tag(child.tag, child.attrib,
                                         child.hsdattrib)
                self._writehsd(child, formatter)
                formatter.close_tag(child.tag)
        

class _ElementInterface(etree._ElementInterface):
    """Element Interface containing extra dictionary with hsd attributes."""
    
    hsdattrib = None
    
    def __init__(self, tag, attrib, hsdattrib=None):
        super().__init__(tag, attrib)
        self.hsdattrib = hsdattrib
        
    def sethsdattribs(self, hsdattrib):
        self.hsdattrib = hsdattrib
        
    def makeelement(self, tag, attrib, hsdattrib):
        return Element(tag, attrib, hsdattrib)
    
    def clear(self):
        super().clear()
        self.hsdattrib.clear()
        

def Element(tag, attrib={}, hsdattrib={}):
    """Element factory with extra hsd attributes."""
    attrib = attrib.copy()
    hsdattrib = hsdattrib.copy()
    return _ElementInterface(tag, attrib, hsdattrib)


def SubElement(parent, tag, attrib={}, hsdattrib={}):
    """Subelement factory with extra hsd attributes."""
    attrib = attrib.copy()
    hsdattrib = hsdattrib.copy()
    element = parent.makeelement(tag, attrib, hsdattrib)
    parent.append(element)
    return element


class TreeBuilder(etree.TreeBuilder):
    """Treebuilder able to cope with extra hsd attributes."""
    
    def __init__(self, element_factory=None):
        if element_factory is None:
            element_factory = _ElementInterface
        super().__init__(element_factory)
        
    def start(self, tag, attrs, hsdattrs):
        elem = super().start(tag, attrs)
        elem.sethsdattribs(hsdattrs)
        return elem
