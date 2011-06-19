import cProfile
import sys
from hsd.parser import HSDParser

def main():
    parser = HSDParser()
    fp = open(sys.argv[1], "r")
    parser.feed(fp)
    fp.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Script needs at least one argument (the input file to"
                         " be used for profiling)!\n")
        sys.exit()
    if len(sys.argv) > 2:
        sort = sys.argv[2]
    else:
        sort = 'cumulative'        
    cProfile.run('main()', sort=sort) 
