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
relationships ={
    "project": ["assetfolder", "sequences"],
    "entity": ["scenefiles","products", "media"],
    "media": ["identifier"], # do we treat folder playblasts renders as a property of media?
    "scenefiles": ["departments"],
    "departments": ["tasks"],
}


class Node:
    def __init__(self):
        self.path = None # file/folder path on disk
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
    def __init__(self):
        super().__init__()
        self.file = self.path.name
        self.extension = self.path.suffix        
        self.above = None    
        del self.below    

    def getFilesize(self):
        return self.path.stat().st_size
    

class Project:
    def __init__(self, path: str, prismcore):
        self.path = Path(path)
        self.name = self.path.name        
        self.pcore = prismcore
        self._assets = None        
        self._sequences = None

    def get_assets(self):
        if self._assets is None:
            self._assets = self._load_assets()
        return self._assets

    def _load_assets(self):
        # maybe these should be generators?
        assets_path = self.path / "03_Production" / "Assets"
        if assets_path.exists():
            return [
                ShotOrAsset(asset_path, self.pcore)
                for asset_path in assets_path.iterdir()
                if asset_path.is_dir()
            ]
        return []

    def get_sequences(self):
        if self._sequences is None:
            self._sequences = self._load_sequences()
        return self._sequences

    def _load_sequences(self):
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
        self.type = type

    def getSequence(self):
        if self.type == "shot":
            return self.getParent()
        
    def getParent(self):
        return super().getParent()
    
    def getDepartments(self):
        pass
         
        

'''
expected usage:

path_to_scenefile = r"e:\Projects\TOPHE\03_Production\Assets\Tophe\Scenefiles\rig\apex\apex_v0001.hiplc"
scenefile = elPapi.from_path(path_to_scenefile) # returns papi Scenefile object

project = scenefile.getProject()
first_asset = project.get_assets()[0] # returns list of assets
'''
