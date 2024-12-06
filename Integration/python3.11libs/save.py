import sys
import os
from pprint import pprint
import common
import json

qtpy_imported = False
# Attempt to import qtpy modules
# try:
#     from qtpy.QtCore import QObject, QEvent
#     from qtpy.QtGui import QIcon, QPixmap
#     from qtpy.QtWidgets import QApplication, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QTextEdit, QCheckBox, QComboBox
#     qtpy_imported = True
# except ImportError as e:
#     qtpy_imported = False
#     qtpy_import_error = e

print(f"QTPY IMPORTED: {qtpy_imported}")
# Setup imports for standalone execution
# We need this so that Qtpy is imported dynamically at runtime
# Then the class can inherit from QDialog
# Then finally we can run the script as a standalone script
# What would probably make more sense is splitting the interface into a separate file
if __name__ == "__main__":
    print("RUNNING SAVE.PY AS MAIN")
    common.setup_imports()
    # Connect to Prism
    pcore = common.connect_prism(app="Standalone", prismArgs=["noUI"])

    try:
        from qtpy.QtCore import QObject, QEvent
        from qtpy.QtGui import QIcon, QPixmap
        from qtpy.QtWidgets import QApplication, QDialog,QInputDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QHBoxLayout, QTextEdit, QCheckBox, QComboBox
        qtpy_imported = True
    except ImportError as e:    
        print(f"Failed to import Qt modules: {e}")
        qtpy_imported = False
else:
    # when running through houdini mplay    
    try:
        # import PySide2 as qtpy
        from PySide2.QtCore import QObject, QEvent
        from PySide2.QtGui import QIcon, QPixmap
        from PySide2.QtWidgets import QApplication,QInputDialog, QDialog, QPushButton, QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QHBoxLayout, QTextEdit, QCheckBox, QComboBox
        qtpy_imported = True
    except ImportError as e:    
        print(f"During MPlay Failed to import Qt modules: {e}")
        qtpy_imported = False


# Default settings stored as a JSON string
default_settings_json = '''
{
    "identifier": "",
    "frame_range_start": "$FSTART",
    "frame_range_end": "$FEND",
    "comment": "",
    "autoversion": false,
    "version": 1,
    "output_path": "",
    "resolution": "1920x1080",
    "format": "avif"
}
'''

def load_settings():
    settings = json.loads(default_settings_json)
    return settings

def save_settings(settings):
    global default_settings_json
    default_settings_json = json.dumps(settings, indent=4)


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
            'identifier': self.identifier_text.text(),
            'frame_range_start': self.frame_range_start.text(),
            'frame_range_end': self.frame_range_end.text(),
            'comment': self.comment_text.toPlainText(),
            'autoversion': self.autoversion_checkbox.isChecked(),
            'version': self.version_spinbox.value(),
            'output_path': self.output_path_text.text(),
            'resolution': self.resolution_text.text(),
            'format': self.format_combo.currentText()
        }
        save_settings(new_settings)
        self.accept()

def run(kwargs=None):  
    # Connect to Prism
    pprint("START OF SAVE.PY")
    common.setup_imports()    
    # Connect to Prism
    # Prepare Prism arguments, no UI for hython
    prismArgs = []
    if "hython" in os.path.basename(sys.executable).lower():
        if "noUI" not in prismArgs:
            prismArgs.append("noUI")
    pcore = common.connect_prism(app="Houdini", prismArgs=prismArgs)

    if not pcore:
        return
    
    # Ensure QApplication is initialized
    if qtpy_imported:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        settings = load_settings()
        dialog = SaveDialog(settings, pcore)
        dialog.exec_()
    else:
        print("QtPy modules could not be imported. Ensure that the Prism connection is established first.")
        print(f"ImportError: {qtpy_import_error}")
    
    # Implement the save functionality here
    print("Save action executed")

if __name__ == "__main__":
    '''Run our qt interface with basic prism'''
    # Ensure QApplication is initialized
    if qtpy_imported:
        app = QApplication.instance()
        if app is None and hasattr(pcore, 'qapp'):
            app = pcore.qapp
        elif app is None:
            app = QApplication([])

        settings = load_settings()
        dialog = SaveDialog(settings, pcore)
        dialog.exec_()
