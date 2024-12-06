import sys
import os
from pprint import pprint, pformat
import json
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

'''Import qtpy modules dynamically'''
try:        
    from qtpy.QtCore import QObject, QEvent
    from qtpy.QtGui import QIcon, QPixmap
    from qtpy.QtWidgets import (
        QApplication, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QProgressBar,
        QLineEdit, QSpinBox, QHBoxLayout, QTextEdit, QCheckBox, QComboBox, QInputDialog, QProgressBar
    )
    LOG.debug("Successfully imported qtpy modules")    
except ImportError as e:          
    LOG.warning(f"Failed to import Qt modules: {e}")       



# Setup imports for standalone execution
# We need this so that Qtpy is imported dynamically at runtime
if __name__ == "__main__":
    LOG.debug("RUNNING SAVE.PY AS MAIN")        

    # temp common imports while testing
    import common
    common.setup_imports()    
    # Connect to Prism
    pcore = common.connect_prism(app="Standalone", prismArgs=["noUI"])

    print("Importing qtmodules")
    # Attempt to import qtpy modules
    '''Import qtpy modules dynamically'''
    try:        
        from qtpy.QtCore import QObject, QEvent
        from qtpy.QtGui import QIcon, QPixmap
        from qtpy.QtWidgets import (
            QApplication, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QProgressBar,
            QLineEdit, QSpinBox, QHBoxLayout, QTextEdit, QCheckBox, QComboBox, QInputDialog, QProgressBar
        )
        LOG.debug("Successfully imported qtpy modules")    
    except ImportError as e:          
        LOG.warning(f"Failed to import Qt modules: {e}")    
    
    print("after qt import")



# Default settings stored as a JSON string
DEFAULT_SETTINGS = '''
{
    "identifier": "my_identifier",
    "frame_range_start": "$FSTART",
    "frame_range_end": "$FEND",
    "comment": "my comment",
    "autoversion": false,
    "version": 1,
    "output_path": "",
    "resolution": "1920x1080",
    "format": "avif"
}
'''

def load_settings():
    settings = json.loads(DEFAULT_SETTINGS)
    return settings

def save_settings(settings):
    """
    Save the given settings as a JSON string with indentation and update the global DEFAULT_SETTINGS.

    Args:
        settings (dict): A dictionary containing the settings to be saved.

    Returns:
        None
    """
    global DEFAULT_SETTINGS
    DEFAULT_SETTINGS = json.dumps(settings, indent=4)


class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle("Export Progress")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Cancel", self)
        layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("Ok", self)
        self.ok_button.setEnabled(False)
        layout.addWidget(self.ok_button)
        
        self.cancel_button.clicked.connect(self.on_cancel)
        self.ok_button.clicked.connect(self.on_ok)
        
        self.canceled = False

    def on_cancel(self):
        self.canceled = True
        self.reject()

    def on_ok(self):
        self.accept()

    def set_progress(self, value):
        self.progress_bar.setValue(value)
        if value >= 100:
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(False)


class SaveDialog(QDialog):    
    def __init__(self, settings, pcore, parent=None):
        super(SaveDialog, self).__init__(parent)
        self.settings = settings
        self.initUI()
        self.core = pcore
        # self.plugin = pcore.get_plugin("Save")

    def initUI(self):
        self.setWindowTitle("Save Interface")

        layout = QVBoxLayout(self)

        ## Identifier
        identifier_layout = QHBoxLayout()
        identifier_label = QLabel("Identifier:")
        identifier_layout.addWidget(identifier_label) 
        self.identifier = "my_identifier"#self.settings['identifier'] # this is an expression 
        self.identifier_preview = QLabel("testo")
        identifier_layout.addWidget(self.identifier_preview)
        
        change_identifier_button = QPushButton("Change")
        identifier_layout.addWidget(change_identifier_button)     
        layout.addLayout(identifier_layout)   

        def expand_identifier(expr):
            # to do eventually with hou.expandString()
            return expr            

        def change_identifier():
            text, ok = QInputDialog.getText(self, "Change Identifier Expression", "Identifier Expression:", QLineEdit.Normal, self.identifier)
            if ok and text:
                self.identifier = text
            self.identifier_preview.setText(expand_identifier(self.identifier))

        change_identifier_button.clicked.connect(change_identifier)
        self.identifier_preview.setText(expand_identifier(self.identifier)) # init


        # Frame Range
        frame_range_label = QLabel("Frame Range:")
        self.frame_range_start = QLineEdit(self.settings['frame_range_start'])
        self.frame_range_end = QLineEdit(self.settings['frame_range_end'])
        frame_range_layout = QHBoxLayout()
        frame_range_layout.addWidget(self.frame_range_start)
        frame_range_layout.addWidget(self.frame_range_end)
        layout.addWidget(frame_range_label)
        layout.addLayout(frame_range_layout)

        comment_label = QLabel("Comment:")
        self.comment_text = QTextEdit(self.settings['comment'])        
        self.comment_text.setFixedHeight(50)  # Set the height to make the comment box smaller
        layout.addWidget(comment_label)
        layout.addWidget(self.comment_text)        

        self.autoversion_checkbox = QCheckBox("Auto Version")
        self.autoversion_checkbox.setChecked(self.settings['autoversion'])
        layout.addWidget(self.autoversion_checkbox)

        version_label = QLabel("Version:")
        self.version_spinbox = QSpinBox()
        self.version_spinbox.setValue(self.settings['version'])
        layout.addWidget(version_label)
        layout.addWidget(self.version_spinbox)

        output_path_label = QLabel("Output Path:")
        self.output_path_text = QLineEdit(self.settings['output_path'])
        layout.addWidget(output_path_label)
        layout.addWidget(self.output_path_text)

        resolution_label = QLabel("Resolution:")
        self.resolution_text = QLineEdit(self.settings['resolution'])
        layout.addWidget(resolution_label)
        layout.addWidget(self.resolution_text)

        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["avif", "png", "jpg"])
        self.format_combo.setCurrentText(self.settings['format'])
        layout.addWidget(format_label)
        layout.addWidget(self.format_combo)

        export_video_button = QPushButton("Export Video")
        layout.addWidget(export_video_button)

        export_video_button.clicked.connect(self.on_exit)

    def on_exit(self):
        new_settings = {
            'identifier': self.identifier.text(),
            'frame_range_start': self.frame_range_start.text(),
            'frame_range_end': self.frame_range_end.text(),
            'comment': self.comment_text.toPlainText(),
            'autoversion': self.autoversion_checkbox.isChecked(),
            'version': self.version_spinbox.value(),
            'output_path': self.output_path_text.text(),
            'resolution': self.resolution_text.text(),
            'format': self.format_combo.currentText()
        }        
        self.settings = new_settings
        self.accept()
        
    def get_settings(self):
        return self.settings


if __name__ == "__main__":
    '''Run our qt interface with basic prism'''
    # Ensure QApplication is initialized    
    app = QApplication.instance()
    if app is None and hasattr(pcore, 'qapp'):
        app = pcore.qapp
    elif app is None:
        app = QApplication([])

    settings = load_settings()
    dialog = SaveDialog(settings, pcore)        

    result = dialog.exec_()
    if result == QDialog.Accepted:
        # The dialog was accepted, get the modified settings
        modified_settings = dialog.get_settings()
        print("Dialog accepted")
        print(modified_settings)
        # Save the modified settings or run the exporter
    else:
        print("Dialog rejected or closed without saving")