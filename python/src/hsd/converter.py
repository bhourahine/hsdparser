"""Contains various converters for the query module."""
from hsd.common import *
from hsd.tree import Element

__all__ = [ "HSDConverter", "HSDNode", "HSDScalar", "HSDScalarUnit", "HSDList",
            "HSDListUnit", "MultiplicativeUnitConverter",
            "TxtConverter", "TxtFloat", "TxtInt", "TxtBool", "TxtStr",
            "hsdnode", "hsdfloat", "hsdint", "hsdbool", "hsdstr",
            "hsdfloatlist", "hsdintlist", "hsdboollist", "hsdstrlist"]

# Standard name of the attribute used for units 
ATTR_UNIT = "unit"            


class HSDConverter:
    """Trivial base implementation of a HSD converter.
    
    It returns the text value of the node. It allows no attributes.
    """
    
    def __init__(self):
        self.setallowedattribs([])
    
    def fromhsd(self, node):
        """Creates the value from a hsd node.
        
        Args:
            node: HSD node containing the value and the attributes.
        
        Returns:
            The value converted to a given type.
            
        Raises:
            Any of the HSD exceptions on error. 
        """
        self.checkattributes(node)
        return node.text
    
    def tohsd(self, tag, value, attrib):
        """Converts a given value to a hsd node with given tag name.
        
        Args:
            tag: Name of the node to create.
            value: The value which should be converted to text.
            attrib: Attributes for the node.
            
        Returns:
            A hsd node representing the value.
            
        Raises:
            Anything derived from the HSD exceptions on error.
        """
        node = Element(tag, attrib)
        node.text = str(value)
        return node
    
    def setallowedattribs(self, attribs):
        """Sets the list of allowed attributes, which the converter is able
        to process.
        
        Args:
            attribs: List of allowed attribute names.
        """
        self.allowedattribs = frozenset(attribs)

    def checkattributes(self, node):
        """Checks the attributes of the node against the set of allowed ones.
        
        Args:
            node:  Node to check.
            allowedattribs: Set of allowed attributes. Can be None if no
                attributes are allowed.
                
        Raises:
            HSDInvalidAttributeException if any attributes appear which are not
                part of the specified set.
        """
        nodekeys = frozenset(node.keys())
        if not self.allowedattribs >= nodekeys:
            tmp = "', '".join(list(nodekeys - self.allowedattribs))
            raise HSDInvalidAttributeException(node=node, msg="Tag '{}' "
                "contains invalid attribute(s) '{}'.".format(node.tag, tmp))

    
class HSDNode(HSDConverter):
    """Returns a HSD node as it is, but raises an exception if attributes
    are present or the value node has any children."""
    
    def fromhsd(self, node):
        self.checkattributes(node)
        if len(node) != 1:
            raise HSDInvalidTagException(msg="Tag '{}' must have exactly one "
                "child.".format(node.tag), node=node)
        if node[0].attrib:
            raise HSDInvalidAttributeException(msg="Tag '{}' can not have any "
                "attributes.".format(node[0].tag), node=node[0])
        return node[0]
    
    def tohsd(self, tag, value, attrib):
        node = Element(tag, attrib)
        node.append(value)
        return node
        

class HSDScalar(HSDConverter):
    """General conversion class for various scalar quantities.
    
    It only accepts nodes without attributes.
    """
    
    def __init__(self, valuetype):
        """Initializes a scalar converter.
        
        Args:
            valuetype: Object with methods fromtxt() and totxt() representing
                the conversion between text and the desired type.
        """
        self.setallowedattribs([])
        self.type = valuetype
    
    def fromhsd(self, node):
        self.checkattributes(node)
        try:
            elem = self.type.fromtxt(node.text.strip())
        except ValueError:
            raise HSDInvalidTagValueException(msg="The value of tag '{}' could "
                "not be converted.".format(node.tag), node=node)
        return elem 
    
    def tohsd(self, tag, value, attrib):
        node = Element(tag, attrib)
        node.text = self.type.totxt(value)
        return node
    

class HSDScalarUnit(HSDScalar):
    """Conversion class for scalar values with unit.
    
    It accepts nodes without attributes or with one attribute (ATTR_UNIT) only.
    """
    
    def __init__(self, valuetype, unitconverter, unitattrib=ATTR_UNIT):
        """Initializes converter for scalars with unit.
         
        Args:
            valuetype: Object with methods fromtxt() and totxt() representing
                the conversion between text and the desired type.
            unitconverter: Callable accepting value and unit (as string) and
                returning the converted value.
            unitattrib: Name of the attribute containing the conversion units
                name.
        """
        super().__init__(valuetype)
        self.unitconverter = unitconverter
        self.unitattrib = unitattrib
        self.setallowedattribs([ unitattrib, ])
     
    def fromhsd(self, node):
        elem = super().fromhsd(node)
        unit = node.get(self.unitattrib, None)
        if unit:
            return self.unitconverter(elem, unit)
        else:
            return elem
         
    
class HSDList(HSDConverter):
    """General conversion class for various lists of scalars.
    
    It only accepts nodes without attributes.
    """
    
    def __init__(self, valuetype, nitem=-1):
        """Initializes a list converter.
        
        Args:
            valuetype: Object with methods fromtxt() and totxt() representing
                the conversion between text and the desired type.
            nitem: Number of items the list should contain. If set to -1, the
                list will contain as many entries as specified. If set to
                any other value, exception is raised, if the number of entries
                specified differs from it.
        """
        self.setallowedattribs([])
        self.type = valuetype
        self.nitem = nitem
        
    def fromhsd(self, node):
        self.checkattributes(node)
        try:
            elems = [ self.type.fromtxt(ss) for ss in node.text.split() ]
        except ValueError:
            raise HSDInvalidTagValueException(node=node, msg="One of the "
                "values of tag '{}' could not be converted.".format(node.tag))
        if self.nitem != -1 and len(elems) != self.nitem:
            raise HSDInvalidTagValueException(node=node, msg="Tag '{}' contains"
                " {} elements instead of {}.".format(node.tag, len(elems), 
                                                     self.nitem)) 
    
    def tohsd(self, tag, value, attrib):
        strs = [ self.type.totxt(vv) for vv in value ]
        return Element(" ".join(strs), attrib)
    
    
class HSDListUnit(HSDList):
    """General conversion class for lists of scalars with unit specification.
    
    It accepts nodes without attributes, or with one specific attribute
    (ATTR_UNIT) only containing the unit of the values. In latter case it tries
    to convert the values in the list to the desired unit.
    """
    
    def __init__(self, valuetype, unitconverter, nitem=-1,
                 unitattrib=ATTR_UNIT):
        """Initializes a list converter.
        
        Args:
            valuetype: Object with methods fromtxt() and totxt() representing
                the conversion between text and the desired type.
            unitconverter: Converter to use to convert the obtained values.
            nitem: Number of items the list should contains. If set to -1, the
                size of the list will be dynamical depending on the content.
            unitattrib: Name of the attribute containing the name of the
                conversion unit.
        """
        super().__init__(valuetype, nitem)
        self.unitconverter = unitconverter
        self.unitattrib = unitattrib
        self.setallowedattribs(unitattrib)
        
    def fromhsd(self, node):
        elems = super().fromhsd(self, node)
        unit = node.get(self.unitattrib, None)
        if unit:
            return [ self.unitconverter(elem, unit) for elem in elems ]
        else:
            return elem


#########################################################################
# Helper objects
#########################################################################
class TxtConverter:
    
    def fromtxt(self, txt):
        pass
    
    def totxt(self, value):
        pass
    
class TxtFloat(TxtConverter):
    """Helper class for conversion between text and float."""
    
    def __init__(self, formstr="{:.12E}"):
        self.formstr = formstr
    
    def fromtxt(self, txt):
        return float(txt)

    def totxt(self, value):
        return self.formstr.format(value)

    
class TxtInt(TxtConverter):
    """Helper class for conversion between text and float."""
    
    def __init__(self, formstr="{:d}"):
        self.formstr = formstr
    
    def fromtxt(self, txt):
        return int(txt)
    
    def totxt(self, value):
        return self.formstr.format(value)
    

class TxtBool(TxtConverter):
    """Helper class for conversion between text and float."""
    
    def __init__(self, trueval="yes", falseval="no"):
        self.reprdict = {True: trueval, False: falseval}
        self.rreprdict = {trueval: True, falseval: False}
        
    def fromtxt(self, txt):
        return self.rreprdict[txt.lower()]
    
    def totxt(self, value):
        return self.reprdict[value]

    
class TxtStr(TxtConverter):
    """Helper class for conversion between text and string."""
    
    def fromtxt(self, txt):
        return txt
    
    def totxt(self, value):
        return str(value)


class MultiplicativeUnitConverter:
    """Implements a conversion by multiplication with a conversion factor."""
    
    def __init__(self, units):
        """Initializes the converter.
        
        Args:
            units: Dictionary. Key contain the name of the unist in text form,
                values contain the corresponding float conversion factor.
        """
        self.units = units
        
    def __call__(self, value, unit):
        """Does the conversion.
        
        Args:
            value: Value in a given unit.
            unit: Name of the unit.
            
        Returns:
            Converted value.        
        """
        factor = self.units[unit]
        return value * factor
    

###########################################################################
# Convenience functions, abbreviations
###########################################################################
hsdnode = HSDNode()
hsdfloat = HSDScalar(TxtFloat())
hsdint = HSDScalar(TxtInt())
hsdbool = HSDScalar(TxtBool())
hsdstr = HSDScalar(TxtStr())

def hsdfloatlist(nitem=-1):
    return HSDList(TxtFloat(), nitem)

def hsdintlist(nitem=-1):
    return HSDList(TxtInt(), nitem)

def hsdboollist(nitem=-1):
    return HSDList(TxtInt(), nitem)

def hsdstrlist(nitem=-1):
    return HSDList(TxtStr(), nitem)
