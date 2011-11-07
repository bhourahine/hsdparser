"""Contains various converters for the query module."""
from hsd.common import *
from hsd.tree import Element

class HSDConverter:
    """General class for HSD converters"""
    
    def fromhsd(self, node):
        """Creates the value from a hsd node.
        
        Args:
            node: HSD node containing the value and the attributes.
        
        Returns:
            The value converted to a given type.
            
        Raises:
            Any of the HSD exceptions on error. 
        """
        pass
    
    def tohsd(self, tag, value, attrib):
        """Converts a given value to a hsd node with given tag name.
        
        Args:
            tag: Name of the node to create.
            value: The value which should converted to text.
            attrib: Attributes for the node.
            
        Returns:
            A hsd node representing the value.
            
        Raises:
            Anyi fo the HSD exceptions on error.
        """
        pass

    
class HSDNode(HSDConverter):
    """Returns a HSD node as it is, but raises an exception if attributes
    are present or the node has any children."""
    
    def fromhsd(self, node):
        if node.attrib:
            raise HSDInvalidAttributeException()
        if len(node) != 1:
            raise HSDInvalidChildException()
        if node[0].attrib:
            raise HSDInvalidAttributeException()
        return node[0]
    
    def tohsd(self, tag, value, attrib):
        node = Element(tag, attrib)
        node.append(value)
        return node

        
class TxtFloat:
    """Helper class for conversion between text and float."""
    
    def __init__(self, formstr="{:.12E}"):
        self.formstr = formstr
    
    def fromtxt(self, txt):
        return float(txt)

    def totxt(self, value):
        return self.formstr.format(value)

    
class TxtInt:
    """Helper class for conversion between text and float."""
    
    def __init__(self, formstr="{:d}"):
        self.formstr = formstr
    
    def fromtxt(self, txt):
        return int(txt)
    
    def totxt(self, value):
        return self.formstr.format(value)
    

class TxtBool:
    """Helper class for conversion between text and float."""
    
    def __init__(self, trueval="yes", falseval="no"):
        self.reprdict = {True: trueval, False: falseval}
        self.rreprdict = {trueval: True, falseval: False}
        
    def fromtxt(self, txt):
        return self.rreprdict[txt.lower()]
    
    def totxt(self, value):
        return self.reprdict[value]

    
class TxtStr:
    """Helper class for conversion between text and string."""
    
    def fromtxt(self, txt):
        return txt
    
    def totxt(self, value):
        return str(value)


def checkattributes(node, attribs):
    """Checks whether the attributes of the node corresponds to a given set.
    
    Args:
        node: Node to be checked.
        attribs: A set of attribute names.
    
    Raises:
        HSDInvalidAttributeExeption: if node has any attributes not in attribs.
    """
    if not attribs >= frozenset(node.keys()):
        raise HSDInvalidAttributeException()


class HSDScalar(HSDConverter):
    """General conversion class for various scalar quantities.
    
    It accepts node without attributes, or with one specific attribute only
    containing the unit of the scalar value. In latter case it tries to
    convert the scalar value to the desired unit.
    """
    
    def __init__(self, valuetype, unitconverter=None, unitattrib="unit"):
        """Initializes a scalar converter.
        
        Args:
            valuetype: Object with methods fromtxt() and totxt() representing
                the conversion between text and the desired type.
            unitconverter: Optional callable object accepting a value and a
                string representing a unit. It should return the converted
                value.
            unitattrib: Optional string with the name of the attribute 
                which contains the unit of the scalar.
        """
        self.type = valuetype
        self.unitconverter = unitconverter
        self.unitattrib = unitattrib
        self.allowedattribs = frozenset([ unitattrib ])
    
    def fromhsd(self, node):
        if self.unitconverter:
            checkattributes(node, self.allowedattribs)
            unit = node.get(self.unitattrib, None)
        elif node.attrib:
            raise HSDInvalidAttributeException()
        try:
            elem = self.type.fromtxt(node.text.strip())
        except ValueError:
            raise HSDInvalidValueException()
        if self.unitconverter:
            return self.unitconverter(elem, unit)
        else:
            return elem 
    
    def tohsd(self, tag, value, attrib):
        node = Element(tag, attrib)
        node.text = self.type.totxt(value)
        return node
        
    
class HSDList(HSDConverter):
    """General conversion class for various lists of scalars.
    
    It accepts node without attributes, or with one specific attribute only
    containing the unit of the values. In latter case it tries to
    convert the values in the list to the desired unit. Additionally, it can
    check, whether the number of elements is equal to a certain number.
    """
    
    def __init__(self, valuetype, nitem=-1, unitconverter=None,
                 unitattrib="unit"):
        """Initializes a list converter.
        
        Args:
            valuetype: Object with methods fromtxt() and totxt() representing
                the conversion between text and the desired type.
            nitem: Number of items the list should contains. If set to -1, the
                size of the list will be dynamical depending on the content.
            unitconverter: Optional callable object accepting a value and a
                string representing a unit. It should return the converted
                value.
            unitattrib: Optional string with the name of the attribute 
                which contains the unit of the scalar.        
        """
        self.type = valuetype
        self.nitem = nitem
        self.unitconverter = unitconverter
        self.unitattrib = unitattrib
        self.allowedattribs = frozenset([ unitattrib ])
        
    def fromhsd(self, node):
        if self.unitconverter:
            checkattributes(node, self.allowedattribs)
            unit = node.get(self.unitattrib, None)
        elif node.attrib:
            raise HSDInvalidAttributeException()
        try:
            elems = [ self.type.fromtxt(ss) for ss in node.text.split() ]
        except ValueError:
            raise HSDInvalidValueException()
        if self.nitem != -1 and len(elems) != self.nitem:
            raise HSDInvalidValueException() 
        if self.unitconverter:
            return [ self.unitconverter(elem, unit) for elem in elems ]
        else:
            return elems
    
    def tohsd(self, tag, value, attrib):
        strs = [ self.type.totxt(vv) for vv in value ]
        return Element(" ".join(strs), attrib)

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


class MultiplicativeUnitConverter:
    
    def __init__(self, units):
        self.units = units
        
    def __call__(self, value, unit):
        factor = self.units[unit]
        return value * factor
    
class TemperatureConverter:
    
    def __call__(self, value, unit):
        unit = unit.lower()
        if unit == "k" or unit == "kelvin":
            return value
        elif unit == "c" or unit == "celsius":
            return value - 273.15
        elif unit == "f" or unit == "fahrenheit":
            return (value - 32.0) / 1.8 - 273.15
            
    
force_units = { "eV/AA": 2e-2
               }
    
hsdforce = HSDScalar(TxtFloat(), MultiplicativeUnitConverter(force_units))
hsdtemperature = HSDScalar(TxtFloat(), TemperatureConverter())

def hsdforcelist(nitem=-1):
    return HSDList(TxtFloat(), nitem, MultiplicativeUnitConverter(force_units))

def hsdtemperaturelist(nitem=-1):
    return HSDList(TxtFloat(), nitem, TemperatureConverter())
