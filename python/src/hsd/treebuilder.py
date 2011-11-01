import hsd.parser as hsdparser
import hsd.tree as hsdtree
    
class HsdTreeBuilder:
    
    def __init__(self, roottag="hsd", parser=None):
        if parser:
            self.parser = parser
        else:
            self.parser = hsdparser.HSDParser()
        self.roottag = roottag
        self.target = hsdtree.TreeBuilder()
        self.parser.start_handler = self.start
        self.parser.close_handler = self.close
        self.parser.text_handler = self.data
        
    def start(self, tagname, options, hsdoptions):
        return self.target.start(tagname, options, hsdoptions)
    
    def data(self, text):
        return self.target.data(text)
    
    def close(self, tagname):
        return self.target.end(tagname)
    
    def build(self, fileobj):
        self.target.start(self.roottag, {}, {})
        self.parser.feed(fileobj)
        self.target.end(self.roottag)
        return self.target.close()

if __name__ == "__main__":
    from io import StringIO
    import sys
    newBuilder = HsdTreeBuilder()
    stream = StringIO("""Geometry = GenFormat {
2  S
Ga As
1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
2    2    0.13567730000E+01   0.13567730000E+01   0.13567730000E+01
0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
0.27135460000E+01   0.27135460000E+01   0.00000000000E+00
0.00000000000E+00   0.27135460000E+01   0.27135460000E+01
0.27135460000E+01   0.00000000000E+00   0.27135460000E+01
}
Test[unit=1,
    dim=3]{}
Hamiltonian = DFTB {
  SCC = Yes
  SCCTolerance = 1.0E-007
  MaxSCCIterations = 1000
  Mixer = Broyden {}
  MaxAngularMomentum {
    Ga = "d"
    As = "p"
  }
  Filling = Fermi {
    Temperature [Kelvin] = 1.0E-006
  }
  SlaterKosterFiles [format=old] {
    Ga-Ga = "./Ga-Ga.skf"
    Ga-As = "./Ga-As.skf"
    As-Ga = "./As-Ga.skf"
    As-As = "./As-As.skf"
  }
  KPointsAndWeights {
    0.0 0.0 0.0   1.0
  }
}

Options {
  AtomResolvedEnergies = No
  RestartFrequency = 20
  RandomSeed = 0
  WriteHS = No
}""")
    tree = newBuilder.build(stream)
    newTree = hsdtree.ElementTree(tree)
    newTree.write(sys.stdout)
