import logic
from pathlib import Path
from pprint import pprint

if __name__ == "__main__":
    '''Run our qt interface with basic prism'''
    # Ensure QApplication is initialized    

    import common
    common.setup_imports()   

    # Connect to Prism
    pcore = common.connect_prism(app="Standalone", prismArgs=["noUI"])

    from qtpy.QtCore import QObject, QEvent
    from qtpy.QtGui import QIcon, QPixmap
    from qtpy.QtWidgets import *

    import interface

    app = QApplication.instance()
    if app is None and hasattr(pcore, 'qapp'):
        app = pcore.qapp
    elif app is None:
        app = QApplication([])

    settings = interface.DEFAULT_SETTINGS
    pprint(settings)
    # settings = json.loads(settings)
    # show dialog

    brain = logic.Logic()
    dialog = interface.SaveDialog(settings, pcore, brain)
    result = dialog.exec_()       
      

    if result == QDialog.Accepted:
        # The dialog was accepted, get the modified settings
        modified_settings = dialog.get_settings()
        print("Dialog accepted")
        print(modified_settings)

        folder = Path(r"C:\Users\luisf\flipbook\my_identifier\v0001")
        inputpath = folder / "my_identifier_v0001.$F4.jpg"
        outputpath = folder / "my_identifier_v0001.webm"
        vid_test_job = logic.Job(inputpath=str(inputpath),outputpath=str(outputpath), type="ffmpeg", framerate=24)

        # from logic import Exporter, Logic
        exporter = logic.Exporter(modified_settings, brain, dryrun=False)                  
        
        exporter.queue.append(vid_test_job)
    
        exporter.execute()
        print("Exporter executed")
        

        # project.folderStructure.ShotPlayblastsfiles(playblastversion_path="my_path",
        #                                             sequence="my_sequence",
        #                                             shot="my_shot",
        #                                             identifier="my_identifier",
        #                                             version=1,
        #                                             extension=".jpg",
        # )