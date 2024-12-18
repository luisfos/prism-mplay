"""
this is an interface for Prism to navigate the file structure easier

this is the tree structure of a prism project:
.
└── Prism Project/    
    ├── 03_Production/
    │   ├── Assets/
    │   │   └── Asset_name/
    │   │       ├── Scenefiles/
    │   │       │   └── Departments/
    │   │       │       └── Tasks/
    │   │       │           └── Versions
    │   │       ├── Products/
    │   │       │   └── Caches/
    │   │       │       └── Versions
    │   │       └── Media/
    │   │           ├── Playblasts/
    │   │           │   └── Versions
    │   │           └── Renders/
    │   │               └── Versions
    │   └── Shots/
    │       └── Sequences/
    │           └── Shot_name/
    │               ├── Scenefiles/
    │               │   └── Departments/
    │               │       └── Tasks/
    │               │           └── Versions
    │               ├── Products/
    │               │   └── Caches/
    │               │       └── Versions
    │               └── Media/
    │                   ├── Playblasts/
    │                   │   └── Versions
    │                   └── Renders/
    │                       └── Versions
    └── 04_Resources/
        ├── custom_folder01
        └── custom_folder02

our goal is to create a object oriented heirarchical interface
that will allow us to navigate the structure of a prism project

if we call each step along the tree a "node", 
we must define carefully the relationships between nodes
for example 1 to many relationships, 1 to 1 relationships, etc
"""

import os
from pathlib import Path
from abc import ABC, abstractmethod

# vocabulary:
'''
entity == shot or asset
entityfolder == sequence or assetfolder

'''

# relationships
# {'entity': ['Export', 'Playblasts', 'Renders', 'Scenefiles'],}
# everything should be lowercase
relationships = {
    "project": ["assetfolder", "sequences"],
    "entity": ["scenefiles","products", "media"],
    "media": ["identifier"], # do we treat folder playblasts renders as a property of media?
    "scenefiles": ["departments"],
    "departments": ["tasks"],
}

def read_file_structure(root_path):
    """
    Reads the entire file structure into a nested dictionary.
    """
    file_tree = {}

    # modifies file_tree in place due to the mutable nature of dictionaries
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Create a reference to the current directory
        current_dir = Path(dirpath).relative_to(root_path)
        current_node = file_tree
        
        for part in current_dir.parts:            
            current_node = current_node.setdefault(part, {"_files": []})

        # Add files and directories        
        current_node.setdefault("_files", []).extend(filenames)        
        # for dirname in dirnames:
        #     current_node.setdefault(dirname, {"_files": []})

    return file_tree

class Node:
    def __init__(self, path=None):
        self.diskpath = Path(path) # path to the file/folder on disk
        self.path = None # file/folder path relative to Project
        self.name = None # name of folder/file       
        self.pcore = None # original link to prism
        self.below = None # children nodes
        self.above = None # parent node

    @abstractmethod
    def getParent(self):
        pass

    @abstractmethod
    def getChildren(self):
        pass

    def __str__(self):
        return f"Node: {self.name}"
    
class Leaf(Node):
    '''
    a leaf is a node that has no children
    it is a file
    '''
    def __init__(self, filepath):
        super().__init__(filepath)
        
        # self.file = self.diskpath.name
        self.extension = self.diskpath.suffix        
        self.above = None    
        del self.below    

    def filesize(self):
        pass
    

class Project:
    '''
    Root object which holds the cached structure of the project
    Every object should hold a refernce to this project object?
    '''
    def __init__(self, path: str, prismcore=None):
        self.pcore = prismcore
        self.path = "/" # relative path

        self.diskpath = Path(path)
        self.name = self.diskpath.name      
        
        # store key value pair as object.name, object
        self._assetFolders = {}  
        self._sequences = {}
        self._assets = {}
        self._shots = {}

    def parse_structure(self):
        '''
        write logic to walk through the project structure and create objects for each node found
        use the tree structure as a guide 
        '''
        self._load_assets()
        self._load_shots()

    def get_shots(self):
        if not self._shots:
            self._load_assets()
        return self._shots
    
    def get_assets(self):
        if not self._assets:
            self._load_assets()
        return self._assets

    def _load_assets(self, fs):
        '''
        Parses the filestructure dict to create asset objects
        '''
        assert '00_Pipeline' in fs, "Project path does not exist"           

        start_path = Path('03_Production', 'Assets')
        assets_path = fs['03_Production']['Assets']
        # print("assets_path", assets_path)
        # any folder with the following is a shot or asset
        lookfor = ["Export", "Playblasts", "Renders", "Scenefiles"]
        shotOrAssets = []
        seqOrFolder = []
        
        for folder in assets_path.keys():   
            if folder == '_files':
                continue         
            
            _is_shotOrAsset = False
            _temp_folders= []
            _temp_assets = []
            for subfolder in assets_path[folder].keys():               
                if subfolder == '_files':
                    continue         
                if subfolder in lookfor: 
                    # if we hit lookfor already, then we are in a shallow shot without a sequence
                    _is_shotOrAsset = True                        
                    _temp_assets.append(folder)
                    break
                else:
                    # otherwise we are in a sequence or assetfolder
                    _temp_assets.append(f"{folder}/{subfolder}")
            
            if not _is_shotOrAsset:
                _temp_folders.append(folder) # we only want to add this sequence once

            seqOrFolder.extend(_temp_folders)
            shotOrAssets.extend(_temp_assets)
            print("aaa", _temp_assets, _temp_folders)

        # now we have this list, do we make an object per list?
        # doesnt this mean another pointless loop?

        # next we need to create the objects
        # and look at what each object needs to be useful as an object with this fs
        # the filepath can be inferred on request 
        # we want to limit any IO calls to a minimum
        # we want to cache as much as possible

        # do we need objects for both AssetFolders and Assets
        # do we want objects for every single thing that is visible in the prism browser?

        print("seqOrFolder", seqOrFolder)
        print("shotOrAssets", shotOrAssets)
                

    def _load_assets_disk(self):
        # maybe these should be generators?
        assert self.diskpath.exists(), "Project path does not exist"
        assert isinstance(self.diskpath, Path), "diskpath must be a Path object"

        assets_path = self.diskpath.joinpath("03_Production","Assets")
        assert assets_path.exists(), "Assets path does not exist"   

        # any folder with the following is a shot or asset
        lookfor = ["Export", "Playblasts", "Renders", "Scenefiles"]
        shotOrAssets = []
        seqOrFolder = []
        if assets_path.exists():
            for folder in assets_path.iterdir():
                if folder.is_dir():
                    is_shotOrAsset = False
                    _temp_assets = []
                    for subfolder in folder.iterdir():                        
                        if subfolder.name in lookfor:
                            is_shotOrAsset = True
                            break
                        else:
                            _temp_assets.append(subfolder)
                    
                    if is_shotOrAsset:                    
                        shotOrAssets.append(folder)
                    else:
                        # folder is seq/assetfolder
                        # subfolder is shot/asset

                        # we need to add the shots with the sequence as parent
                        seqOrFolder.append(folder)
                        shotOrAssets
                        
                        
                        
            

            return [
                ShotOrAsset(asset_path, self.pcore)
                for asset_path in assets_path.iterdir()
                if asset_path.is_dir()
            ]
        

    def get_sequences(self):
        if self._sequences is None:
            self._sequences = self._load_sequences()
        return self._sequences

    def _load_shots(self):
        sequences_path = self.path / "03_Production" / "Shots" / "Sequences"
        if sequences_path.exists():
            return [
                Sequence(sequence_path, self.pcore)
                for sequence_path in sequences_path.iterdir()
                if sequence_path.is_dir()
            ]
        return [] 

    def __str__(self):
        return f"Project: {self.name}"

class Sequence(Node):
    def __init__(self, path: str, prismcore):
        super().__init__(path, prismcore)
        self.name = self.path.name        
        self.pcore = prismcore

    def getShots(self):
        pass    

    def __str__(self):
        return f"Sequence: {self.name}"


class ShotOrAsset(Node): # also known as entity?
    def __init__(self, path: str, type: str=""):        
        super().__init__(path)
        self.name = self.path.name
        self.fullname = self.name
        if self.above: # if we have a parent
            self.fullname = f"{self.above.name}/{self.name}"  # parent/child
            
        self.type = type

    def getSequence(self):
        if self.type == "shot":
            return self.getParent()
        
    def getParent(self):
        return super().getParent()
    
    def getDepartments(self):
        pass
         

class SequenceOrAssetFolder(Node): # also known as entity?
    def __init__(self, path: str, type: str=""):        
        super().__init__(path)
        self.name = self.path.name
        self.fullname = self.name
        if self.above: # if we have a parent
            self.fullname = f"{self.above.name}/{self.name}"  # parent/child
            
        assert type in ["sequence", "assetfolder"], "type must be sequence or assetfolder"
        self.type = type


'''
expected usage:

path_to_scenefile = r"e:\Projects\TOPHE\03_Production\Assets\Tophe\Scenefiles\rig\apex\apex_v0001.hiplc"
scenefile = elPapi.from_path(path_to_scenefile) # returns papi Scenefile object

project = scenefile.getProject()
first_asset = project.get_assets()[0] # returns list of assets

here's a tree view of the project 3 folders deep
├── Assets
│   ├── RnD
│   │   ├── Export
│   │   ├── Playblasts
│   │   ├── Renders
│   │   ├── Scenefiles
│   │   └── Textures
│   ├── Tank
│   │   ├── Export
│   │   ├── Playblasts
│   │   ├── Renders
│   │   └── Scenefiles
│   ├── Tophe
│   │   ├── Export
│   │   ├── Playblasts
│   │   ├── Renders
│   │   ├── Scenefiles
│   │   └── Textures
│   └── assetfolder
│       └── inside
└── Shots
    ├── sq_010
    │   ├── _sequence
    │   ├── sh_010
    │   └── sh_020
    └── sq_020
        ├── _sequence
        └── sh_010

'''

if __name__ == "__main__":
    # temp prism core setup
    # tmp_path = r"E:\Projects\TOPHE\03_Production\Assets\Tophe\Scenefiles\luis"
    # tmp_path = r"E:\Projects\TOPHE"
    tmp_path = r"S:\Demo"
    # ft = read_file_structure(r"e:\Projects\TOPHE")
    ft = read_file_structure(tmp_path)
    
    from pprint import pprint
    pprint(ft, width=80, depth=3)

    project = Project(tmp_path)
    project._load_assets(ft)



    
    # import common
    # common.setup_imports() 
    # import PrismCore  
    # pcore = PrismCore.create(app="Standalone", prismArgs=["noUI"])


    # project = Project(r"e:\Projects\TOPHE", pcore) 
    # project.parse_structure() # this will load all the assets and sequences, and cache them

    # shots = project.get_shots() # returns a list of shot objects
    # assets = project.get_assets() # returns a list of asset objects
