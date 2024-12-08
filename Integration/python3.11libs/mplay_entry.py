'''
This file is our entry point for MPlay.
The MPlay plugin buttons will call these functions as defined in the MainMenuMPlay.xml
'''

import sys
import os
import logging
import time
import logic
from pprint import pprint, pformat

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)

def setup_imports() -> None:
    # Add PrismCore to sys.path
    # This will also add Qt
    prism_root = os.environ.get('PRISM_ROOT')    
    if prism_root:
        scripts_path = os.path.join(prism_root, "Scripts")
        if scripts_path not in sys.path:
            sys.path.append(scripts_path)
            LOG.info(f"Added {scripts_path} to sys.path")
    else:
        LOG.warning("PRISM_ROOT not found in environment variables")

    houdini_path = os.environ.get('HOUDINI_PATH')
    if houdini_path:
        houdini_path = houdini_path.split(";")
        for path in houdini_path:
            scripts_path = os.path.join(path, "python3.11libs")
            if scripts_path not in sys.path:
                sys.path.append(scripts_path)
                LOG.info(f"Added {scripts_path} to sys.path")
    else:
        LOG.warning("HOUDINI_PATH not found in environment variables")

    LOG.info(pformat(sys.path))


def quicksave(kwargs=None) -> None:
    # connect to Prism
    setup_imports() # setting up imports is faster than relying on PrismInit
    import PrismInit    
    pcore = PrismInit.prismInit()

    # load settings
    import interface
    settings = interface.DEFAULT_SETTINGS
    # settings = json.loads(settings)        
    # modify settings    
    # save settings
    # run exporter
    pass

def save(kwargs=None):
    # connect to Prism
    setup_imports() # setting up imports is faster than relying on PrismInit
    import PrismInit    
    pcore = PrismInit.prismInit()

    # load settings
    import interface
    settings = interface.DEFAULT_SETTINGS
    # settings = json.loads(settings)    
    # show dialog
    dialog = interface.SaveDialog(settings, pcore) 
    dialog.exec_() # modifies settings
    # save settings
    # run exporter
    pass

def debug(kwargs=None):      
    LOG.setLevel(logging.DEBUG)
    LOG.debug("Start of debug function")
    start_time = time.time()
    
    setup_imports() # setting up imports is faster than relying on PrismInit
    import PrismInit    
    pcore = PrismInit.prismInit()    

    end_time = time.time()
    LOG.debug(f"End of debug, duration: {end_time - start_time:.3f} seconds")

    import interface
    settings = interface.DEFAULT_SETTINGS

    brain = logic.Logic()
    dialog = interface.SaveDialog(settings, pcore, brain)
    result = dialog.exec_()

    if result:
        # The dialog was accepted, get the modified settings
        modified_settings = dialog.get_settings()
        print("Dialog accepted")
        print(modified_settings)

        # from logic import Exporter, Logic
        exporter = logic.Exporter(modified_settings, brain, dryrun=False)

        test_job = logic.Job(
            location="$HIP/flipbook/",
            identifier="my_identifier",
            frames=[],
            version=1,
            format=".jpg",
        )
        exporter.queue.append(test_job)

        result = exporter.execute()
        print("result of execute", result)



if __name__ == "__main__":
    setup_imports()
    # Import via houdini
    # import PrismInit    
    # pcore = PrismInit.prismInit()

    # Import via standalone
    import PrismCore    
    pcore = PrismCore.create(app="Standalone", prismArgs=["noUI"])    
    try:
        from qtpy.QtCore import QObject, QEvent
        from qtpy.QtGui import QIcon, QPixmap
        from qtpy.QtWidgets import QApplication, QDialog,QInputDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QHBoxLayout, QTextEdit, QCheckBox, QComboBox

        qtpy_imported = True
    except ImportError as e:    
        print(f"Failed to import Qt modules: {e}")
        qtpy_imported = False