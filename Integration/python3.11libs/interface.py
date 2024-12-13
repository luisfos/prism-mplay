import sys
import os
from pprint import pprint, pformat
import json
import logging


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

# 
try:
    import hou
    LOG.debug("Successfully imported Houdini modules")
except ImportError as e:
    LOG.warning(f"Failed to import Houdini modules: {e}")
    # Mock Houdini module placeholder for local development
    class MockHou:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
        
        class text:
            @staticmethod
            def expandString(expr):
                return expr
    hou = MockHou()

'''Import qtpy modules dynamically'''
try:            
    from qtpy.QtCore import QObject, QEvent, Qt
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
        from qtpy.QtCore import QObject, QEvent, Qt
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
DEFAULT_SETTINGS = {
    "identifier": "my_identifier",
    "frame_range_start": "$FSTART",
    "frame_range_end": "$FEND",
    "comment": "my comment",
    "autoversion": True,
    "version": 1,
    "output_path": "",
    "resolution": "1920x1080",
    "format": ".jpg"
}

# def load_settings():
#     settings = json.loads(DEFAULT_SETTINGS)
#     return settings

# def save_settings(settings):
#     """
#     Save the given settings as a JSON string with indentation and update the global DEFAULT_SETTINGS.

#     Args:
#         settings (dict): A dictionary containing the settings to be saved.

#     Returns:
#         None
#     """
#     global DEFAULT_SETTINGS
#     DEFAULT_SETTINGS = json.dumps(settings, indent=4)


class SaveDialog(QDialog):    
    def __init__(self, settings, pcore, logic, hou, parent=None):
        super(SaveDialog, self).__init__(parent)
        self.settings = settings
        self.hou = hou
        self.logic = logic
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
            return self.hou.text.expandString(expr)            

        def change_identifier():
            text, ok = QInputDialog.getText(self, "Change Identifier Expression", "Identifier Expression:", QLineEdit.Normal, self.identifier)
            if ok and text:
                self.identifier = text
            self.identifier_preview.setText(expand_identifier(self.identifier))

        change_identifier_button.clicked.connect(change_identifier)
        self.identifier_preview.setText(expand_identifier(self.identifier)) # init

        
        frame_range_label = QLabel("Frame Range:")
        frame_range_layout = QHBoxLayout()
        frame_range_layout.addWidget(frame_range_label)
        
        self.frame_range_combo = QComboBox()
        self.frame_range_combo.addItems(["Full Range", "Custom", "Single Frame"])
        self.frame_range_combo.setCurrentText("Full Range")
        frame_range_layout.addWidget(self.frame_range_combo)

        frame_range_preview_layout = QHBoxLayout()        
        self.frame_range_start = QLineEdit(self.settings['frame_range_start'])
        self.frame_range_end = QLineEdit(self.settings['frame_range_end'])
        # Add a spacer item to ensure the layout takes up space even when widgets are hidden
        frame_range_preview_layout.addStretch() # like adding empty label in houdini
        frame_range_preview_layout.addWidget(self.frame_range_start)
        frame_range_preview_layout.addWidget(self.frame_range_end)        

        layout.addLayout(frame_range_layout)
        layout.addLayout(frame_range_preview_layout)

        def update_frame_range_inputs():
            mode = self.frame_range_combo.currentText()
            if mode == "Full Range":
                self.frame_range_start.setHidden(True)
                self.frame_range_end.setHidden(True)
            elif mode == "Custom":
                self.frame_range_start.setHidden(False)
                self.frame_range_end.setHidden(False)
            elif mode == "Single Frame":
                self.frame_range_start.setHidden(False)
                self.frame_range_end.setHidden(True)

        self.frame_range_combo.currentTextChanged.connect(update_frame_range_inputs)
        update_frame_range_inputs()  # Initialize the state

        comment_label = QLabel("Comment:")
        self.comment_text = QTextEdit(self.settings['comment'])        
        self.comment_text.setFixedHeight(50)  # Set the height to make the comment box smaller
        layout.addWidget(comment_label)
        layout.addWidget(self.comment_text)        

        self.autoversion_checkbox = QCheckBox("Auto Version")
        self.autoversion_checkbox.setChecked(self.settings['autoversion'])
        
        version_label = QLabel("Version:")
        self.version_spinbox = QSpinBox()
        self.version_spinbox.setValue(self.settings['version'])
        
        autoversion_layout = QHBoxLayout()
        autoversion_layout.addWidget(self.autoversion_checkbox)
        autoversion_layout.addWidget(version_label)
        autoversion_layout.addWidget(self.version_spinbox)
        
        layout.addLayout(autoversion_layout)

        def update_version_input():
            self.version_spinbox.setEnabled(not self.autoversion_checkbox.isChecked())

        self.autoversion_checkbox.stateChanged.connect(update_version_input)
        update_version_input()  # Initialize the state

        output_path_label = QLabel("Preview Path:")
        self.output_path_text = QLabel("test output path")
        self.output_path_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(output_path_label)
        layout.addWidget(self.output_path_text)

        resolution_label = QLabel("Resolution:")
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["as is", "stretch"])
        self.resolution_combo.setCurrentText(self.settings['resolution'])
        
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.resolution_combo)
        
        layout.addLayout(resolution_layout)

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
            'identifier': self.identifier,
            'frame_range_start': self.frame_range_start.text(),
            'frame_range_end': self.frame_range_end.text(),
            'comment': self.comment_text.toPlainText(),
            'autoversion': self.autoversion_checkbox.isChecked(),
            'version': self.version_spinbox.value(),
            'output_path': self.output_path_text.text(),
            'resolution': self.resolution_combo.currentText(),
            'image_format': self.format_combo.currentText()
        }
        
        self.settings = new_settings
        self.accept()
        
    def get_settings(self):
        return self.settings


class ProgressDialog(QDialog):
    def __init__(self, exporter, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle("Export Progress")
        self.setModal(True)
        self.exporter = exporter

        layout = QVBoxLayout(self)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, len(self.exporter.queue))
        layout.addWidget(self.progress_bar)

        self.job_label = QLabel(self)
        layout.addWidget(self.job_label)

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

    def set_progress(self, value, job_description):
        self.progress_bar.setValue(value)
        self.job_label.setText(f"Job {value} of {self.progress_bar.maximum()}: {job_description}")
        if value >= self.progress_bar.maximum():
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def run_exporter(self):
        for i, job in enumerate(self.exporter.queue):
            if self.canceled:
                break
            job_description = f"Exporting {job.identifier}"
            self.set_progress(i + 1, job_description)
            self.exporter.execute()
            QApplication.processEvents()


if __name__ == "__main__":
    '''Run our qt interface with basic prism'''
    # Ensure QApplication is initialized    
    app = QApplication.instance()
    if app is None and hasattr(pcore, 'qapp'):
        app = pcore.qapp
    elif app is None:
        app = QApplication([])

    settings = DEFAULT_SETTINGS

    # from logic import Exporter, Logic
    import logic
    brains = logic.Logic()
    dialog = SaveDialog(settings, pcore, logic=logic, hou=hou)

    result = dialog.exec_()
    if result == QDialog.Accepted:
        # The dialog was accepted, get the modified settings
        modified_settings = dialog.get_settings()
        print("Dialog accepted")
        print(modified_settings)

        exporter = logic.Exporter(settings, brains, dryrun=True)

        progress_dialog = ProgressDialog(exporter)
        progress_dialog.show()
        progress_dialog.run_exporter()
        QApplication.processEvents()

        progress_dialog.set_progress(len(exporter.queue), "All jobs completed")
        progress_dialog.accept()
    else:
        print("Dialog rejected or closed without saving")