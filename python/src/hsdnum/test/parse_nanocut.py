###########################################################################
# Demonstrates HSDQuery capabilities on an example inpout for nanocut
###########################################################################
import sys
from io import StringIO
import numpy as np
from hsd.common import *
from hsd.tree import HSDTree
from hsd.treebuilder import HSDTreeBuilder
from hsd.parser import HSDParser
from hsd.converter import *
from hsdnum.converter import *
from hsd.query import HSDQuery
from hsd.formatter import HSDFormatter

ATTR_UNIT = "unit"


###########################################################################
# Converter for some complex datatypes in the input
###########################################################################

class HSDGeometry(HSDConverter):
    """Converts geometry from HSD to (types, coords) tuple.
    
    The tuple returned contains the (-1,) shaped array types, with the chemical
    symbol of every atom, and the (-1, 3) shaped array coords with the
    corresponding coordinates.
    
    Does not implement its own tohsd(), so do not use to produce HSD output. 
    """

    def __init__(self, basis):
        """Initializes HSDGeometry instance.
        
        Args:
            basis: Basis vectors of the lattice to used for conversion from
                fractional coordinates into cartesian.
        """
        self.basis = basis
        self.setallowedattribs([ ATTR_UNIT, ])
        
    def fromhsd(self, node):
        self.checkattributes(node)
        unit = node.get(ATTR_UNIT, "fractional")
        isfractional = (unit == "fractional")
        if not isfractional and unit != "cartesian":
            raise HSDInvalidAttributeValueException() 
        words = node.text.split()
        nn = len(words)
        if nn % 4:
            raise HSDInvalidTagValueException()
        types = [ words[ii] for ii in range(0, nn, 4) ]
        tmp = [ (float(words[ii]), float(words[ii+1]), float(words[ii+2])) 
               for ii in range(1, nn, 4) ]
        coords = np.array(tmp, dtype=float)
        if isfractional:
            coords = np.dot(coords, self.basis)
        return types, coords
    

class HSDCoordVector(HSDArray):
    """Converter for a 3 component coordinate vector.
    
    The vector can be given in cartesian or fractional coordinates, the
    converted (3,) array is in cartesian coordinates.
    """
     
    def __init__(self, basis):
        super().__init__(float, (3,))
        self.basis = basis
        self.setallowedattribs([ ATTR_UNIT, ])
         
    def fromhsd(self, node):
        coords = super().fromhsd(node)
        unit = node.get(ATTR_UNIT, "fractional")
        isfractional = (unit == "fractional")
        if not isfractional and unit != "cartesian":
            raise HSDInvalidAttributeValueException()
        if isfractional:
            coords = np.dot(coords, self.basis)
        return types, coords


class HSDPlanesAndDistances(HSDArray):
    """Converts PlanesAndDistances.
    
    Converted format is a tuple (planevecs, dists) containing
    the (-1, 3) array planevecs with the normal vectors of the planes and
    the (-1,) array dists with the distances of the planes from the origin.
    """
    
    def __init__(self, basis):
        super().__init__(float, (-1, 4))
        self.basis = basis
        self.setallowedattribs([ ATTR_UNIT, ])
        
    def fromhsd(self, node):
        array = super().fromhsd(node)
        directions = array[:,0:3]
        distances = array[:,3]
        if np.any(np.abs(directions - directions.astype(int)) > 1e-12):
            raise HSDInvalidTagValueException()
        return (directions, distances) 
               
###########################################################################
# The input
###########################################################################
stream = StringIO("""
crystal3 {
  lattice_vectors {
    -0.189997466000E+01   0.189997466000E+01   0.485580074000E+01
     0.189997466000E+01  -0.189997466000E+01   0.485580074000E+01
     0.189997466000E+01   0.189997466000E+01  -0.485580074000E+01
  }
# basis [fractional|cartesian] {
  basis {
    Ti    0.00000000e+00   0.00000000e+00   0.50000000e+00
    Ti   -2.50000000e-01  -7.50000000e-01   0.00000000e+00
    O     2.05199515e-01   2.05199515e-01   0.50000000e+00
    O    -4.55199515e-01   4.48004847e-02   0.00000000e+00
    O    -2.05199515e-01  -2.05199515e-01   0.50000000e+00
    O    -4.48004847e-02  -5.44800485e-01   0.00000000e+00
  }  
}

periodicity = D1 {
  axis [fractional] = 1 1 0
}

# Those options will not be parsed.
unknown_option = 12
unknown_option2 = uo3 {
  uo4 = 42
}

cuts {
  convex_prism {
    order = 1
    # planes_and_distances [cartesian|fractional]
    planes_and_distances [cartesian] {
      1  0  0   7.0
      0  1  0   7.0
     -1  0  0   7.0
      0 -1  0   7.0
    }
  }
}
    """)

###########################################################################
# Parsing the input
###########################################################################

# Building the tree using customized parser
parser = HSDParser(defattrib=ATTR_UNIT)
builder = HSDTreeBuilder(parser=parser)
root = builder.build(stream)

# Query object should mark all queried object as "processed" 
qy = HSDQuery(markprocessed=True)
crystal = qy.getchild(root, "crystal")
latvecs = qy.getvalue(crystal, "lattice_vectors", hsdfloatarray((3,3)))
# This option is not present in the output, default value will be set.
l2 = qy.getvalue(crystal, "latvecs2", hsdfloatarray((3,3)), 
                 defvalue=np.identity(3, dtype=float), hsdblock=True)
types, coords = qy.getvalue(crystal, "basis", HSDGeometry(latvecs))
periodicity = qy.getchild(root, "periodicity")
pertype = qy.getonlychild(periodicity)
if pertype.tag == "D1":
    axis = qy.getvalue(pertype, "axis", HSDCoordVector(latvecs))
elif pertype.tag == "D2":
    pass
else:
    raise HSDInvalidTagException()

cuts = qy.getchild(root, "cuts")
for cutmethod in qy.findchildren(cuts, "*"):
    order = qy.getvalue(cutmethod, "order", hsdint)
    if cutmethod.tag == "convex_prism":
        planenormvecs, dists = qy.getvalue(cutmethod, "planes_and_distances",
                                           HSDPlanesAndDistances(latvecs))
    elif cutmethod.tag == "whatever":
        pass
    else:
        raise HSDInvalidTagException()

# Write out tree, which contains now all defaults explicitly set.
tree = HSDTree(root)
tree.writehsd(HSDFormatter(target=sys.stdout, closecomments=True))

# Give warning, if unprocessed nodes present.
unprocessed = qy.findunprocessednodes(root)
if unprocessed:
    print("\nWARNING: UNPROCESSED NODES:")
    for node in unprocessed:
        print(node.tag)
    
    
