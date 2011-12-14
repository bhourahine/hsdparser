from hsd.common import *
from hsd.tree import Element

__all__ = [ "HSDQueryError", "HSDMissingTagException", "HSDInvalidTagException",
           "HSDInvalidTagValueException", "HSDMissingAttributeException",
           "HSDInvalidAttributeException", "HSDInvalidAttributeValueException",
           "HSDQuery"]


class HSDQuery:
    """Class providing methods for querying a HSD-tree."""
    
    def __init__(self, chkuniqueness=False, markprocessed=False):
        """Initializes a query object.
        
        Args:
            chkuniqueness: If True, all query methods except findchildren()
                checks, whether the child found is unique. (Default: False)
            markprocessed: If True, nodes which have been queried are marked
                as processed. 
        """ 
        self.chkunique = chkuniqueness
        self.mark = markprocessed
    
    def findchild(self, node, name, optional=False):
        """Finds a child of a node with a given name.
        
        Args:
            node: Parent node.
            name: Name of the child to look for.
            optional: Flags, whether the child is optional only.
            
        Returns:
            A hsd node if child has been found or None.
            
        Raises:
            HSDMissingTagException: if child was not found and the optional
                flag was False.
            HSDInvalidTagException: if there are duplicates of the child
                and the query object was initialized with chkuniqueness=True.
        """
        if self.chkunique:
            children = node.findall(name)
            if len(children > 1):
                raise HSDInvalidTagException(node=children[1],
                    msg="Double occurance of unique tag '{}'.".format(name))
            child = children[0] if children else None
        else:
            child = node.find(name)
        if child is None and not optional:
            raise HSDMissingTagException(
                msg="Required tag '{}' not found.".format(name), node=node)
        self.markprocessed(child)
        return child
    
    def findchildren(self, node, name, optional=False):
        """Finds children of a node with given name.
        
        Args:
            node: Parent node.
            name: Name of the children to look for.
            optional: Flags, whether the presence of at least one child is
                optional or not.
                
        Returns:
            List of child nodes or empty list.
            
        Raises:
            HSDMissingTagException: if no children were not found and the
                optional flag was False.
        """
        children = node.findall(name)
        if not children and not optional:
            raise HSDMissingTagException(node=node, msg="No occurrence of "
                "required tag '{}' found.".format(name))
        self.markprocessed(*children)
        return children
    
    def getonlychild(self, node, defchild=None, hsdblock=False):
        """Returns the first child of a node, which must be the only child.
        
        Args:
            node: Parent node.
            defchild: Default value for the child. If specified and no child is
                found, the default is appended to the tree and returned.
            hsdblock: If True, the the given value is added in hsd block
                notation (enclosed in curly braces) instead of an assignment. 
                
        Returns:
            The only child of the node.
            
        Raises:
            HSDInvalidTagException: If tag has more than one child.
            HSDMissingTagException: If tag has no child.
        """ 
        if len(node) > 1:
            raise HSDInvalidTagException(msg="Tag '{}' is only allowed to "
                "have one child.".format(node.tag), node=node)
        elif len(node) == 1:
            child = node[0]
        elif defchild is None:
            raise HSDMissingTagException(msg="Tag '{}' must have exactly one "
                "child.".format(node.tag), node=node)
        else:
            child = defchild
            node.append(child)
            if not hsdblock:
                node.hsdattrib[HSDATTR_EQUAL] = True
        self.markprocessed(child)
        return child
                              
    def getchild(self, node, name, deftext=None, defattribs=None):
        """Returns a child with a given name or sets a default if not found and
        default values had been specified.
        
        Args:
            node: Parent node.
            name: Name of the child to look for.
            deftext: Default text value for the child.
            defattribs: Default attribute dictionary for the child.
            
        Returns:
            The child with the given name. Either from the original hsd-tree
            or the one, which had been created using the provided default
            values. In latter case, the appropriate child is inserted into
            the tree.
            
        Raises:
            HSDMissingTagException: if the child was not found and no default
                value had been specified.
        """
        optional = deftext is not None
        child = self.findchild(node, name, optional)
        # findchild only returns if child has been found or optional is True.
        if child is None:
            child = Element(name, defattribs or {})
            child.text = deftext
            self.markprocessed(child)
            node.append(child)
        return child
                
    def getvalue(self, node, name, converter, defvalue=None, defattribs=None,
                 hsdblock=False):
        """Returns the value (text) stored in a child with a given name. The 
        value is converted using the provided converter.
        
        Args:
            node: Parent node.
            name: Name of the child to look for.
            converter: Object with methods fromhsd() and tohsd() which can
                convert between the hsd element and the desired type. See
                converters in hsd.converter for examples.
            defvalue: Optional default value used if child has not been found.
            defattribs: Optional default attribute dictionary used if child
                has not been found.
            hsdblock: If True, the the given value is added in hsd block
                notation (enclosed in curly braces) instead of an assignment. 
                
        Returns:
            The converted value of the child node's text or the default value
            if the child had not been found. In latter case, an appropriate
            node with the appropriate text representation of the default
            value is inserted into the tree.
                
        Raises:
            HSDMissingTagException: if child was not found and no default
                value had been specified.
            Any other excepction raised by the converter.
        """
        optional = defvalue is not None
        child = self.findchild(node, name, optional)
        if child is not None:
            return converter.fromhsd(child)
        else:
            child = converter.tohsd(name, defvalue, defattribs or {})
            self.markprocessed(child)
            if not hsdblock:
                child.hsdattrib[HSDATTR_EQUAL] = True
            node.append(child)
            return defvalue
        
    def getvaluenode(self, node, name, converter, defvalue=None,
                     defattribs=None, hsdblock=False):
        """Returns the child node of a child with a given name. The child node
        can have only one child. This is converted via the provided converter.
        
        Args:
            node: Parent node.
            name: Name of the child to look for.
            converter: Object with methods fromhsd() and tohsd() which can
                convert between the hsd element and the desired type. See
                converters in hsd.converter for examples.
            defvalue: Optional default value used if child has not been found.
            defattribs: Optional default attribute dictionary used if child
                has not been found.
            hsdblock: If True, the the given value is added in hsd block
                notation (enclosed in curly braces) instead of an assignment. 
                
        Returns:
            The converted node of the child node's first child or the default
            value if the child had not been found. In latter case, an appropriate
            node with the provided default subnode is inserted into the tree.
                
        Raises:
            HSDMissingTagException: if child was not found and no default
                value had been specified.
            HSDInvalidTagException: If child has more than one child.
        """
        optional = defvalue is not None
        child = self.findchild(node, name, optional)
        if child is not None:
            if len(child) > 1:
                raise HSDInvalidTagException("Tag '{}' is not allowed to have"
                    " more than one child".format(child.tag), node=child)
            self.markprocessed(child, child[0])
            return converter.fromhsd(child)
        else:
            child = converter.tohsd(name, defvalue, defattribs or {})
            if not hsdblock:
                child.hsdattrib[HSDATTR_EQUAL] = True
            self.markprocessed(child, child[0])
            node.append(child)
            return defvalue
        
    def markprocessed(self, *nodes):
        """Marks nodes as having been processed, if the query object had been
        initialized with the appropriate option.
        
        Args:
            *nodes: List of nodes to mark as processed.
        """ 
        if self.mark:
            for node in nodes:
                if node is not None:
                    node.hsdattrib[HSDATTR_PROC] = True
        
    def findunprocessednodes(self, node, allnodes=False):
        """Returns list of all nodes which had been not marked as processed.
        
        Args:
            node: Parent node.
            
        Returns:
            List of all nodes, which have not been queried by a HSDQuery
            instance.
        """
        unprocessed = []
        for child in node:
            if child.hsdattrib.get(HSDATTR_PROC, None) is None:
                unprocessed.append(child)
                if not allnodes:
                    continue
            unprocessed += self.findunprocessednodes(child, allnodes)
        return unprocessed


if __name__ == "__main__":
    from io import StringIO
    from hsd.treebuilder import HSDTreeBuilder
    from hsd.parser import HSDParser
    from hsd.tree import HSDTree
    from hsd.converter import *
    parser = HSDParser(defattrib="unit")
    builder = HSDTreeBuilder(parser=parser)
    
    # Defining force type (scalar, list)
    force_units = { "eV/AA": 0.0194469050555 }
    hsdforce = HSDScalarUnit(TxtFloat(),
                             MultiplicativeUnitConverter(force_units))
    def hsdforcelist(nitem=-1):
        return HSDListUnit(TxtFloat(), MultiplicativeUnitConverter(force_units),
                       nitem)
    
    stream = StringIO("""
Driver {}
# Driver = None
#Driver = ConjugateGradient {
#    MaxForceComponent [eV/AA] = 1e-2
#}
Hamiltonian = DFTB {
  # SCC = True
  # SCCTolerance = 1e-4
  # MaxSCCIterations = 100
  MaxAngularMomentum {
    O = "p"
    H = "s"
  }
  Mixer = Broyden {
    MixingParameter [dfd] = 0.2
  }
  #ReadInitialCharges = No
  KPointsAndWeights {
     0.0   0.0  0.0   0.25
     0.25 0.25 0.25   0.75
  }
}

Options {
  WriteAutotestTag = Yes
  UnknownOption = No
}

#ParserOptions {
#  ParserVersion = 4
#}
""")
    root = builder.build(stream)
    qy = HSDQuery(markprocessed=True)
    # Driver can be either a node or the text None. Default is the latter.
    driver = qy.getchild(root, "Driver", "None")
    if driver.text == "None":
        dtype = None
    else:
        # Driver not set to "None": query all possibilities:
        dtype = qy.getonlychild(driver, Element("ConjugateGradient"))
        if dtype.tag == "ConjugateGradient":
            forcetol = qy.getvalue(dtype, "MaxForceComponent", hsdforce, 1e-4)
        elif dtype.tag == "SteepestDescent":
            forcetol = qy.getvalue(dtype, "MaxForceComponent", hsdforce, 1e-4)
            stepsize = qy.getvalue(dtype, "StepSize", hsdfloat, 40.0)
        else:
            raise HSDInvalidTagException(node=dtype, msg="Unknown driver type "
                                         "'{}'.".format(dtype.tag))
    print("DTYPE:", dtype)    
    ham = qy.getchild(root, "Hamiltonian")
    dftb = qy.getchild(ham, "DFTB")
    scc = qy.getvalue(dftb, "SCC", hsdbool, defvalue=True)
    scctol = qy.getvalue(dftb, "SCCTolerance", hsdfloat, defvalue=1e-4)
    scciter = qy.getvalue(dftb, "MaxSCCIterations", hsdint, 100)
    mangmom = qy.getchild(dftb, "MaxAngularMomentum")
    maxangs = [ qy.getvalue(mangmom, species, hsdstr)
                for species in ["O", "H"] ]
    mixer = qy.getvaluenode(dftb, "Mixer", hsdnode, Element("Broyden"))
    if mixer.tag == "Broyden":
        mixparam = qy.getvalue(mixer, "MixingParameter", hsdfloat, 0.2)
    else:
        raise HSDInvalidTagException(node=mixer,
            msg="Unknown mixer type '{}'.".format(mixer.tag))
    readcharges = qy.getvalue(dftb, "ReadInitalCharges", hsdbool, False)
    kpoints = qy.getvalue(dftb, "KPointsAndWeights", hsdfloatlist())
    options = qy.getchild(root, "Options", "")
    autotest = qy.getvalue(options, "WriteAutotestTag", hsdbool, False)
    parseroptions = qy.getchild(root, "ParserOptions", "")
    parserversion = qy.getvalue(parseroptions, "ParserVersion", hsdint, 4)
    tree = HSDTree(root)
    tree.writehsd()
    print("\nUnprocessed: ", qy.findunprocessednodes(root))
    
