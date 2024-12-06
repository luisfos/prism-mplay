# FILE: Integration/python3.11libs/common.py
import os
import sys
from pprint import pprint

def setup_imports() -> None:
    # Add PrismCore to sys.path
    # This will also add Qt
    prism_root = os.environ.get('PRISM_ROOT')    
    if prism_root:
        scripts_path = os.path.join(prism_root, "Scripts")
        if scripts_path not in sys.path:
            sys.path.append(scripts_path)
            print(f"Added {scripts_path} to sys.path")
    else:
        print("PRISM_ROOT not found in environment variables")

    houdini_path = os.environ.get('HOUDINI_PATH')
    if houdini_path:
        houdini_path = houdini_path.split(";")
        for path in houdini_path:
            scripts_path = os.path.join(path, "python3.11libs")
            if scripts_path not in sys.path:
                sys.path.append(scripts_path)
                print(f"Added {scripts_path} to sys.path")
    else:
        print("HOUDINI_PATH not found in environment variables")

    pprint(sys.path)

def connect_prism(app="Houdini", prismArgs=[]) -> object:
    import PrismCore    
    # pcore = PrismCore.PrismCore(app=app, prismArgs=prismArgs)
    pcore = PrismCore.create(app=app, prismArgs=prismArgs)
    print("returning pcore")
    return pcore
        
if __name__ == "__main__":
    pcore = connect_prism(app="Standalone", prismArgs=["noUI"])
    # print(pcore.projects)

    # project from path
    # context from path
