# FILE: Integration/python3.11libs/quicksave.py
import os
import sys
from pprint import pprint

import common

def run(kwargs=None):
    # Connect to Prism
    # next add PYTHONPATH to PYTHONPATh..
    # need to ensure our mplay_prism package goes last
    common.connect_prism()
    # move logic to common.py
    # link from houdini session using os.environ

    # Implement the quicksave functionality here
    # pprint(kwargs)
    print("Quicksave action executed")
    # pprint(sys.path)


    pprint(dict(os.environ))

if __name__ == "__main__":
    run()