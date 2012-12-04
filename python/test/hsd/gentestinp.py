import sys

testinputs = [
    ("typical", ("", """
Geometry = GenFormat {
2  S
Ga As
1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
2    2    0.13567730000E+01   0.13567730000E+01   0.13567730000E+01
0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
0.27135460000E+01   0.27135460000E+01   0.00000000000E+00
0.00000000000E+00   0.27135460000E+01   0.27135460000E+01
0.27135460000E+01   0.00000000000E+00   0.27135460000E+01
}

Hamiltonian = DFTB {
  SCC[unit=Kelvin,dim=3] = Yes
  SCCTolerance[dimension=10] = 1.0E-007
  MaxSCCIterations = 1000
  Mixer = Broyden {
    MixingParameter = 0.200000000000000
    CachedIterations = -1
    InverseJacobiWeight = 1.000000000000000E-002
    MinimalWeight = 1.00000000000000
    MaximalWeight = 100000.000000000
    WeightFactor = 1.000000000000000E-002
  }
  MaxAngularMomentum {
    Ga = "d"
    As = "p"
  }
  Filling = Fermi {
    Temperature = 1.0E-006
    IndependentKFilling = No
  }
  SlaterKosterFiles {
    Ga-Ga = "./Ga-Ga.skf"
    Ga-As = "./Ga-As.skf"
    As-Ga = "./As-Ga.skf"
    As-As = "./As-As.skf"
  }
  KPointsAndWeights {
0.000000000000000E+000 0.000000000000000E+000 0.000000000000000E+000 1.00000000000000
  }
  OldRepulsiveSum = No
  OrbitalResolvedSCC = No
  OldSKInterpolation = No
  Charge = 0.000000000000000E+000
  ReadInitialCharges = No
  DampXH = No
  EwaldParameter = 0.000000000000000E+000
  Eigensolver = DivideAndConquer {}
  ThirdOrder = No
}
""", "")),

    ("data", ("Geometry = GenFormat {\n", """2  S
Ga As
1    1    0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
2    2    0.13567730000E+01   0.13567730000E+01   0.13567730000E+01
0.00000000000E+00   0.00000000000E+00   0.00000000000E+00
0.27135460000E+01   0.27135460000E+01   0.00000000000E+00
0.00000000000E+00   0.27135460000E+01   0.27135460000E+01
0.27135460000E+01   0.00000000000E+00   0.27135460000E+01
""", "}"))
    ]


def main():
    outsize = int(sys.argv[1])
    for inputname, content in testinputs:
        nrep = ((outsize * 1024 - len(content[0]) - len(content[2])) 
                // len(content[1]) + 1) 
        fp = open("{}-{}k.hsd".format(inputname, outsize), "w")
        fp.write(content[0])
        for ii in range(nrep):
            fp.write(content[1])
        fp.write(content[2])
        fp.close()


if __name__ == "__main__":
    main()