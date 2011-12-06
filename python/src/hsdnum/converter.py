from hsd.converter import HSDConverter, ATTR_UNIT
from hsd.common import *
from hsd.tree import Element
import numpy as np

__all__ = [ "HSDArray", "HSDArrayUnit",
            "hsdfloatarray", "hsdintarray" ]

###########################################################################
# Converter
###########################################################################
class HSDArray(HSDConverter):
    """Converter for numpy arrays of arbitrary type."""
    
    def __init__(self, dtype, shape=(-1,)):
        """Initialized HSDArrays.
        
        Args:
            dtype: Numpy data type.
            shape: Tuple representing the shape of the resulting array.
        """
        self.dtype = dtype
        self.shape = shape
        self.setallowedattribs([])

    def fromhsd(self, node):
        self.checkattributes(node)
        return np.array(node.text.split(), dtype=self.dtype).reshape(self.shape)

    def tohsd(self, tag, value, attrib):
        node = Element(tag, attrib)
        tmp = np.array(value)
        tmp2 = tmp.reshape(( tmp.shape[0], -1))
        lines = []       
        for arrayline in tmp2:
            lines.append(" ".join([ str(val) for val in arrayline ]))
        node.text = "\n".join(lines)
        return node

       
class HSDArrayUnit(HSDArray):
    """Converter for numpy arrays with units."""
    
    def __init__(self, dtype, converter, shape=(-1,), unitattrib=ATTR_UNIT):
        """Initializes a list converter.
        
        Args:
            dtype: Numpy data type.
            converter: Converter to use to convert the obtained values.
            shape: Tuple representing the shape of the desired array.
            unitattrib: Name of the attribute carrying the conversion unit
                name.
        """
        super().__init__(dtype, shape)
        self.converter = converter
        self.unitattrib = unitattrib
        self.setallowedattribs([ unitattrib, ])
        
    def fromhsd(self, node):
        array = super().fromhsd(self, node)
        unit = node.get(self.unitattrib, None)
        if unit:
            return self.unitconverter(array, unit)
        else:
            return array

        
###########################################################################
# Convenience functions
###########################################################################

def hsdfloatarray(shape=(-1,)):
    return HSDArray(float, shape)

def hsdintarray(shape=(-1,)):
    return HSDArray(int, shape)
