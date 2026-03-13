"""
GUI for the Python Obfuscator using PySide6
"""
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLineEdit, QLabel, QFileDialog, QCheckBox,
                               QTextEdit, QGroupBox, QFormLayout, QMessageBox, QComboBox,
                               QTabWidget, QScrollArea, QRadioButton)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QCursor

from pylockware.core.obfuscator import PyObfuscator
from pylockware.modules.import_obf_module import ImportObfuscateModule
from pylockware.modules.nuitka_builder_module import NuitkaBuilderModule


class ObfuscatorWorker(QThread):
    """
    Worker thread for running the obfuscator to prevent GUI freezing
    """
    progress_signal = Signal(str)
    finished_signal = Signal(bool, str)  # success, message
    
    def __init__(self, obfuscator_params):
        super().__init__()
        self.obfuscator_params = obfuscator_params
        
    def run(self):
        try:
            # Create and run the obfuscator
            obfuscator = PyObfuscator(**self.obfuscator_params)
            obfuscator.run_obfuscation()
            self.finished_signal.emit(True, "Obfuscation completed successfully!")
        except Exception as e:
            self.finished_signal.emit(False, f"Error during obfuscation: {str(e)}")


class ObfuscatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyLockWare Python Obfuscator")
        self.setGeometry(100, 100, 900, 800)
        
        # Set up the central widget and tab widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("PyLockWare Python Obfuscator")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Project Configuration Tab
        self.project_tab = self.create_project_tab()
        self.tab_widget.addTab(self.project_tab, "Project Configuration")
        
        # Obfuscation Settings Tab
        self.obfuscation_tab = self.create_obfuscation_tab()
        self.tab_widget.addTab(self.obfuscation_tab, "Obfuscation")

        # Control Flow Obfuscation Tab
        self.control_flow_tab = self.create_control_flow_tab()
        self.tab_widget.addTab(self.control_flow_tab, "Control Flow Obf")

        # Runtime Protection Tab
        self.protection_tab = self.create_protection_tab()
        self.tab_widget.addTab(self.protection_tab, "Runtime Protection")
        
        # Additional Settings Tab
        self.additional_tab = self.create_additional_tab()
        self.tab_widget.addTab(self.additional_tab, "Additional Settings")

        # Nuitka EXE Packaging Tab
        self.nuitka_tab = self.create_nuitka_tab()
        self.tab_widget.addTab(self.nuitka_tab, "Nuitka EXE")

        main_layout.addWidget(self.tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Obfuscation")
        self.start_btn.clicked.connect(self.start_obfuscation)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)
        
        # Log output
        log_group = QGroupBox("Log Output")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Initialize worker
        self.worker = None

    def create_help_button(self, tooltip_text):
        """Create a help button with tooltip"""
        btn = QPushButton("?")
        btn.setFixedSize(20, 20)
        btn.setToolTip(tooltip_text)
        btn.setCursor(QCursor(Qt.WhatsThisCursor))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border-radius: 10px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        return btn

    def create_project_tab(self):
        """Create the project configuration tab"""
        tab = QWidget()
        layout = QFormLayout()
        
        # Project path
        project_hbox = QHBoxLayout()
        self.project_path_edit = QLineEdit()
        self.project_path_edit.setPlaceholderText("Select the project directory to obfuscate")
        project_select_btn = QPushButton("Browse...")
        project_select_btn.clicked.connect(self.select_project_path)
        project_hbox.addWidget(self.project_path_edit)
        project_hbox.addWidget(project_select_btn)
        layout.addRow("Project Path:", project_hbox)
        
        # Entry point
        entry_point_hbox = QHBoxLayout()
        self.entry_point_edit = QLineEdit()
        self.entry_point_edit.setPlaceholderText("e.g., main.py or app/main.py")
        entry_point_hbox.addWidget(self.entry_point_edit)
        entry_point_hbox.addWidget(self.create_help_button("The entry point is the main Python file that starts your application."))
        layout.addRow("Entry Point:", entry_point_hbox)
        
        # Entry function
        entry_func_hbox = QHBoxLayout()
        self.entry_function_edit = QLineEdit("main")
        entry_func_hbox.addWidget(self.entry_function_edit)
        entry_func_hbox.addWidget(self.create_help_button("The entry function is the main function to call when the application starts."))
        layout.addRow("Entry Function:", entry_func_hbox)
        
        # Output directory
        output_dir_hbox = QHBoxLayout()
        self.output_dir_edit = QLineEdit("dist")
        output_dir_hbox.addWidget(self.output_dir_edit)
        output_dir_hbox.addWidget(self.create_help_button("Directory where obfuscated files will be saved."))
        layout.addRow("Output Directory:", output_dir_hbox)
        
        tab.setLayout(layout)
        return tab
    
    def create_obfuscation_tab(self):
        """Create the obfuscation settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Remap option
        remap_layout = QHBoxLayout()
        self.remap_checkbox = QCheckBox("Remap(rename identifiers)")
        self.remap_checkbox.setToolTip("Enable renaming of functions, variables, etc. to random names")
        remap_layout.addWidget(self.remap_checkbox)
        remap_layout.addWidget(self.create_help_button("Remapping renames all functions, variables, classes, and other identifiers to random names, making the code harder to understand and reverse engineer."))
        remap_layout.addStretch()
        layout.addLayout(remap_layout)

        # String protection option
        string_prot_layout = QHBoxLayout()
        self.string_prot_checkbox = QCheckBox("String protection")
        self.string_prot_checkbox.setToolTip("Enable string protection using base64 and zlib encoding")
        string_prot_layout.addWidget(self.string_prot_checkbox)
        string_prot_layout.addWidget(self.create_help_button("String protection encodes string literals in your code using base64 and zlib, making it harder to identify sensitive strings in your application."))
        string_prot_layout.addStretch()
        layout.addLayout(string_prot_layout)

        # Boolean obfuscation option
        bool_obf_layout = QHBoxLayout()
        self.bool_obf_checkbox = QCheckBox("Boolean obfuscation")
        self.bool_obf_checkbox.setToolTip("Enable boolean obfuscation using arithmetic expressions")
        bool_obf_layout.addWidget(self.bool_obf_checkbox)
        bool_obf_layout.addWidget(self.create_help_button("Boolean obfuscation replaces boolean literals (True/False) with equivalent arithmetic expressions, making it harder to understand the logic flow."))
        bool_obf_layout.addStretch()
        layout.addLayout(bool_obf_layout)

        # Disable traceback option
        traceback_layout = QHBoxLayout()
        self.disable_traceback_checkbox = QCheckBox("Disable traceback")
        self.disable_traceback_checkbox.setToolTip("Disable traceback by setting sys.tracebacklimit = 0")
        traceback_layout.addWidget(self.disable_traceback_checkbox)
        traceback_layout.addWidget(self.create_help_button("Disables Python traceback output by setting sys.tracebacklimit = 0 at the start of each obfuscated file. This prevents error details from being shown."))
        traceback_layout.addStretch()
        layout.addLayout(traceback_layout)

        # Metadata stripper option
        metadata_strip_layout = QHBoxLayout()
        self.metadata_strip_checkbox = QCheckBox("Strip metadata")
        self.metadata_strip_checkbox.setToolTip("Remove docstrings and other metadata from obfuscated code")
        metadata_strip_layout.addWidget(self.metadata_strip_checkbox)
        metadata_strip_layout.addWidget(self.create_help_button("Removes docstrings, comments, and other metadata from the code to reduce file size and remove potentially sensitive information."))
        metadata_strip_layout.addStretch()
        layout.addLayout(metadata_strip_layout)

        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_protection_tab(self):
        """Create the runtime protection tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Anti-debug option
        anti_debug_layout = QHBoxLayout()
        self.anti_debug_checkbox = QCheckBox("Anti-debug")
        self.anti_debug_checkbox.setToolTip("Enable anti-debug and anti-injection protection")
        self.anti_debug_checkbox.clicked.connect(self.on_anti_debug_clicked)
        anti_debug_layout.addWidget(self.anti_debug_checkbox)
        anti_debug_layout.addWidget(self.create_help_button("Anti-debug protection adds code to detect and prevent debugging attempts, making it harder for attackers to analyze your application."))
        anti_debug_layout.addStretch()
        layout.addLayout(anti_debug_layout)

        # Anti-debug mode selection
        anti_debug_mode_layout = QHBoxLayout()
        anti_debug_mode_label = QLabel("Protection Level:")
        self.anti_debug_combo = QComboBox()
        self.anti_debug_combo.addItems([
            "Strict (with thread checking, breaks pyside, pyqt, numpy and most of other native libs)",
            "Normal (without thread checking)",
            "Native (high-performance protection using native DLL implementation)"
        ])
        self.anti_debug_combo.setCurrentIndex(0)
        self.anti_debug_combo.setEnabled(True)
        self.anti_debug_combo.setToolTip("Select the anti-debug protection level")

        anti_debug_mode_layout.addWidget(anti_debug_mode_label)
        anti_debug_mode_layout.addWidget(self.anti_debug_combo)
        anti_debug_mode_layout.addWidget(self.create_help_button("Strict: Full protection but breaks native libs. Normal: Safer for GUI apps. Native: High-performance using native DLL."))
        anti_debug_mode_layout.addStretch()
        layout.addLayout(anti_debug_mode_layout)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_control_flow_tab(self):
        """Create the control flow obfuscation tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Number obfuscation option
        num_obf_layout = QHBoxLayout()
        self.num_obf_checkbox = QCheckBox("Number obfuscation")
        self.num_obf_checkbox.setToolTip("Enable number obfuscation using arithmetic expressions")
        num_obf_layout.addWidget(self.num_obf_checkbox)
        num_obf_layout.addWidget(self.create_help_button("Number obfuscation replaces numeric literals with equivalent arithmetic expressions, making it harder to understand the meaning of numeric values in your code."))
        num_obf_layout.addStretch()
        layout.addLayout(num_obf_layout)

        # Import obfuscation option
        import_obf_layout = QHBoxLayout()
        self.import_obf_checkbox = QCheckBox("Import obfuscation")
        self.import_obf_checkbox.setToolTip("Enable import obfuscation using dynamic execution techniques")
        self.import_obf_checkbox.clicked.connect(self.on_importobf_clicked)
        import_obf_layout.addWidget(self.import_obf_checkbox)
        import_obf_layout.addWidget(self.create_help_button("Import obfuscation hides import statements using dynamic execution methods like __import__() and exec(), making dependencies harder to identify."))
        import_obf_layout.addStretch()
        layout.addLayout(import_obf_layout)

        # State machine obfuscation option
        state_machine_layout = QHBoxLayout()
        self.state_machine_checkbox = QCheckBox("State machine obfuscation")
        self.state_machine_checkbox.setToolTip("Enable state machine obfuscation to transform functions into state machines")
        state_machine_layout.addWidget(self.state_machine_checkbox)
        state_machine_layout.addWidget(self.create_help_button("State machine obfuscation transforms functions into state machines, making control flow harder to analyze and understand."))
        state_machine_layout.addStretch()
        layout.addLayout(state_machine_layout)

        # Builtin dispatcher obfuscation option
        builtin_dispatcher_layout = QHBoxLayout()
        self.builtin_dispatcher_checkbox = QCheckBox("Builtin dispatcher")
        self.builtin_dispatcher_checkbox.setToolTip("Enable builtin dispatcher obfuscation to replace built-in calls with dispatcher calls")
        builtin_dispatcher_layout.addWidget(self.builtin_dispatcher_checkbox)
        builtin_dispatcher_layout.addWidget(self.create_help_button("Builtin dispatcher replaces built-in function calls (print(), len(), etc.) with calls via a dispatcher class, making it harder to identify built-in function usage."))
        builtin_dispatcher_layout.addStretch()
        layout.addLayout(builtin_dispatcher_layout)

        # Junk code generation option
        junk_code_layout = QHBoxLayout()
        self.junk_code_checkbox = QCheckBox("Junk code generation")
        self.junk_code_checkbox.setToolTip("Enable junk code generation with fake if/elif branches")
        junk_code_layout.addWidget(self.junk_code_checkbox)
        junk_code_layout.addWidget(self.create_help_button("Junk code generation adds fake if/elif branches with opaque predicates that always evaluate to True or False, making code analysis harder."))
        junk_code_layout.addStretch()
        layout.addLayout(junk_code_layout)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def create_additional_tab(self):
        """Create the additional settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Banner text
        banner_layout = QHBoxLayout()
        banner_label = QLabel("Banner text:")
        self.banner_edit = QLineEdit("Obfuscated by PyLockWare Obfuscator")
        banner_layout.addWidget(banner_label)
        banner_layout.addWidget(self.banner_edit)
        banner_layout.addWidget(self.create_help_button("The banner text will be added to the beginning of each obfuscated Python file."))
        layout.addLayout(banner_layout)

        # Name generator settings
        name_gen_layout = QHBoxLayout()
        name_gen_label = QLabel("Name generator:")
        self.name_gen_combo = QComboBox()
        self.name_gen_combo.addItems([
            "English letters and digits",
            "Chinese characters",
            "Mixed (English + Chinese)",
            "Numbers only",
            "Hexadecimal"
        ])
        self.name_gen_combo.setCurrentIndex(0)
        name_gen_layout.addWidget(name_gen_label)
        name_gen_layout.addWidget(self.name_gen_combo)
        name_gen_layout.addWidget(self.create_help_button("Character set used for generating random names during obfuscation."))
        layout.addLayout(name_gen_layout)

        # Opaque complexity settings
        opaque_complexity_layout = QHBoxLayout()
        opaque_complexity_label = QLabel("Opaque complexity:")
        self.opaque_complexity_combo = QComboBox()
        self.opaque_complexity_combo.addItems(["Low", "Medium", "High"])
        self.opaque_complexity_combo.setCurrentIndex(2)  # Default to High
        opaque_complexity_layout.addWidget(opaque_complexity_label)
        opaque_complexity_layout.addWidget(self.opaque_complexity_combo)
        opaque_complexity_layout.addWidget(self.create_help_button("Complexity level of opaque predicates in junk code. Higher complexity makes conditions harder to analyze."))
        layout.addLayout(opaque_complexity_layout)

        # Junk density slider
        junk_density_layout = QHBoxLayout()
        junk_density_label = QLabel("Junk density:")
        self.junk_density_combo = QComboBox()
        self.junk_density_combo.addItems(["0.3 (Low)", "0.5 (Medium)", "0.7 (High)", "0.9 (Very High)"])
        self.junk_density_combo.setCurrentIndex(1)  # Default to 0.5
        junk_density_layout.addWidget(junk_density_label)
        junk_density_layout.addWidget(self.junk_density_combo)
        junk_density_layout.addWidget(self.create_help_button("Higher density adds more junk code but increases file size and may impact performance."))
        layout.addLayout(junk_density_layout)

        layout.addStretch()
        tab.setLayout(layout)
        return tab
        
    def select_project_path(self):
        """Open a dialog to select the project directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Project Directory", 
            os.path.expanduser("~"),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self.project_path_edit.setText(directory)
    
    def start_obfuscation(self):
        from PySide6.QtWidgets import QMessageBox
        """Start the obfuscation process"""
        # Validate inputs
        if not self.project_path_edit.text().strip():
            QMessageBox.warning(self, "Input Error", "Please select a project path.")
            return

        if not self.entry_point_edit.text().strip():
            QMessageBox.warning(self, "Input Error", "Please specify an entry point file.")
            return

        # Prepare parameters for the obfuscator
        params = {
            'project_path': self.project_path_edit.text().strip(),
            'entry_point': self.entry_point_edit.text().strip(),
            'entry_function': self.entry_function_edit.text().strip(),
            'output_dir': self.output_dir_edit.text().strip(),
            'remap': self.remap_checkbox.isChecked(),
            'string_prot': self.string_prot_checkbox.isChecked(),
            'num_obf': self.num_obf_checkbox.isChecked(),
            'import_obf': self.import_obf_checkbox.isChecked(),
            'state_machine': self.state_machine_checkbox.isChecked(),
            'builtin_dispatcher': self.builtin_dispatcher_checkbox.isChecked(),
            'junk_code': self.junk_code_checkbox.isChecked(),
            'junk_density': self._get_junk_density(),
            'opaque_complexity': self._get_opaque_complexity(),
            'name_gen': self._get_name_gen_setting(),
            'disable_traceback': self.disable_traceback_checkbox.isChecked(),
            'metadata_strip': self.metadata_strip_checkbox.isChecked(),
            'bool_obf': self.bool_obf_checkbox.isChecked(),
        }

        # Set anti-debug option
        if self.anti_debug_checkbox.isChecked():
            import platform
            import sys
            # Check if running on Windows AMD64
            if not (sys.platform == 'win32' and platform.machine().lower() in ['amd64', 'x86_64']):
                # Show warning and disable anti-debug
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Platform Warning",
                                    "Anti-debug protection is only available for Windows AMD64. Option will be disabled.")
                params['anti_debug'] = None
            else:
                anti_debug_choice = self.anti_debug_combo.currentText()
                if "Normal" in anti_debug_choice:
                    params['anti_debug'] = 'normal'
                elif "Native" in anti_debug_choice:
                    params['anti_debug'] = 'native'
                else:  # Strict
                    params['anti_debug'] = 'strict'
        else:
            params['anti_debug'] = None

        # Set Nuitka options
        params['enable_nuitka'] = self.nuitka_enable_checkbox.isChecked()
        params['nuitka_onefile'] = self.nuitka_onefile_checkbox.isChecked()
        params['nuitka_standalone'] = self.nuitka_standalone_checkbox.isChecked()
        params['nuitka_output_name'] = self.nuitka_output_name_edit.text().strip() or None
        params['nuitka_disable_console'] = self.nuitka_disable_console_checkbox.isChecked()
        params['nuitka_icon'] = self.nuitka_icon_edit.text().strip() or None
        params['nuitka_admin'] = self.nuitka_admin_checkbox.isChecked()

        # Collect selected plugins
        nuitka_plugins = []
        if self.nuitka_plugin_tkinter.isChecked():
            nuitka_plugins.append('tk-inter')
        if self.nuitka_plugin_pyside6.isChecked():
            nuitka_plugins.append('pyside6')
        if self.nuitka_plugin_pyqt5.isChecked():
            nuitka_plugins.append('pyqt5')
        if self.nuitka_plugin_numpy.isChecked():
            nuitka_plugins.append('numpy')
        if self.nuitka_plugin_multiprocessing.isChecked():
            nuitka_plugins.append('multiprocessing')
        params['nuitka_plugins'] = nuitka_plugins

        # Extra imports
        extra_imports_str = self.nuitka_extra_imports_edit.text().strip()
        params['nuitka_extra_imports'] = [x.strip() for x in extra_imports_str.split(',') if x.strip()] if extra_imports_str else []

        # Custom options
        custom_options_str = self.nuitka_custom_options_edit.text().strip()
        params['nuitka_options'] = custom_options_str.split() if custom_options_str else []

        # Disable UI during processing
        self.start_btn.setEnabled(False)
        self.log_text.clear()
        self.log_text.append("Starting obfuscation process...\n")

        # Create and start the worker thread
        self.worker = ObfuscatorWorker(params)
        self.worker.progress_signal.connect(self.update_log)
        self.worker.finished_signal.connect(self.obfuscation_finished)
        self.worker.start()
    
    def update_log(self, message):
        """Update the log text with a message"""
        self.log_text.append(message)

    def on_nuitka_clicked(self, checked):
        """Handle Nuitka checkbox click - warn about incompatible options"""
        if checked:  # Checkbox was just checked
            # Warn about import obfuscation incompatibility and disable it
            if self.import_obf_checkbox.isChecked():
                QMessageBox.warning(
                    self, "Nuitka Compatibility Warning",
                    "Import obfuscation is incompatible with Nuitka EXE packaging.\n\n"
                    "Import obfuscation has been disabled."
                )
                self.import_obf_checkbox.setChecked(False)

    def on_importobf_clicked(self, checked):
        """Handle import obfuscation checkbox click - warn if Nuitka is enabled"""
        if checked and self.nuitka_enable_checkbox.isChecked():
            QMessageBox.warning(
                self, "Nuitka Compatibility Warning",
                "Import obfuscation is incompatible with Nuitka EXE packaging.\n\n"
                "Import obfuscation has been disabled."
            )
            self.import_obf_checkbox.setChecked(False)

    def on_anti_debug_clicked(self, checked):
        """Handle anti-debug checkbox click - warn if Nuitka is enabled"""
        if checked:
            QMessageBox.warning(
                self, "Anti-Debug Protection Warning",
                "Anti-debug protection is not a complete security solution.\n\n"
                "• It may be incompatible with other obfuscation modules\n"
                "• It can be bypassed by experienced reverse engineers\n"
                "• For production protection, use dedicated protectors like\n"
                "  Themida, VMProtect after obfuscation.\n\n"
                "Are you sure you want to enable anti-debug protection?"
            )
    
    def obfuscation_finished(self, success, message):
        """Handle the completion of the obfuscation process"""
        self.log_text.append(message)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
        
        # Re-enable UI
        self.start_btn.setEnabled(True)
        
        # Clean up the worker
        self.worker = None

    def _get_name_gen_setting(self):
        """Get the selected name generator setting from the combo box."""
        index = self.name_gen_combo.currentIndex()
        name_gen_options = ['english', 'chinese', 'mixed', 'numbers', 'hex']
        return name_gen_options[index] if 0 <= index < len(name_gen_options) else 'english'

    def _get_junk_density(self):
        """Get the selected junk density value."""
        index = self.junk_density_combo.currentIndex()
        density_options = [0.3, 0.5, 0.7, 0.9]
        return density_options[index] if 0 <= index < len(density_options) else 0.5

    def _get_opaque_complexity(self):
        """Get the selected opaque complexity setting from the combo box."""
        index = self.opaque_complexity_combo.currentIndex()
        complexity_options = ['low', 'medium', 'high']
        return complexity_options[index] if 0 <= index < len(complexity_options) else 'high'

    def select_icon_file(self):
        """Open a dialog to select the icon file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Icon File",
            os.path.expanduser("~"),
            "Icon Files (*.ico);;All Files (*)"
        )
        if file_path:
            self.nuitka_icon_edit.setText(file_path)

    def auto_detect_plugins(self):
        """Auto-detect required plugins based on project imports"""
        project_path = self.project_path_edit.text().strip()
        if not project_path:
            QMessageBox.warning(self, "Input Error", "Please select a project path first.")
            return

        # Create an analyzer and detect frameworks
        analyzer = NuitkaBuilderModule().import_analyzer
        all_imports = analyzer.analyze_directory(Path(project_path))
        frameworks = analyzer.detect_frameworks(all_imports)

        # Update checkboxes based on detected frameworks
        self.nuitka_plugin_tkinter.setChecked(frameworks.get('tkinter', False))
        self.nuitka_plugin_pyside6.setChecked(frameworks.get('pyside6', False))
        self.nuitka_plugin_pyqt5.setChecked(frameworks.get('pyqt5', False))
        self.nuitka_plugin_numpy.setChecked(frameworks.get('numpy', False))
        self.nuitka_plugin_multiprocessing.setChecked(frameworks.get('multiprocessing', False))

        detected = [k for k, v in frameworks.items() if v]
        if detected:
            self.log_text.append(f"Auto-detected frameworks: {', '.join(detected)}")
        else:
            self.log_text.append("No specific frameworks detected")

    def create_nuitka_tab(self):
        """Create the Nuitka EXE packaging tab"""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Enable Nuitka checkbox
        nuitka_enable_layout = QHBoxLayout()
        self.nuitka_enable_checkbox = QCheckBox("Enable EXE packaging with Nuitka")
        self.nuitka_enable_checkbox.clicked.connect(self.on_nuitka_clicked)
        nuitka_enable_layout.addWidget(self.nuitka_enable_checkbox)
        nuitka_enable_layout.addWidget(self.create_help_button("Nuitka compiles Python code to C/C++ and creates a standalone executable file."))
        nuitka_enable_layout.addStretch()
        layout.addLayout(nuitka_enable_layout)

        # Description
        nuitka_desc = QLabel("Nuitka compiles Python code to C/C++ and packages it into a standalone executable.\nThis makes reverse engineering significantly harder.")
        nuitka_desc.setWordWrap(True)
        nuitka_desc.setStyleSheet("color: gray;")
        layout.addWidget(nuitka_desc)

        # Output name
        output_name_layout = QHBoxLayout()
        output_name_label = QLabel("Output EXE name:")
        self.nuitka_output_name_edit = QLineEdit()
        self.nuitka_output_name_edit.setPlaceholderText("e.g., MyApplication.exe (optional)")
        output_name_layout.addWidget(output_name_label)
        output_name_layout.addWidget(self.nuitka_output_name_edit)
        output_name_layout.addWidget(self.create_help_button("The name of the output executable file. If not specified, Nuitka will use the entry point name."))
        layout.addLayout(output_name_layout)

        # Build mode options (both can be enabled)
        build_mode_group = QGroupBox("Build Mode")
        build_mode_layout = QVBoxLayout()

        onefile_layout = QHBoxLayout()
        self.nuitka_onefile_checkbox = QCheckBox("--onefile (create single executable file)")
        self.nuitka_onefile_checkbox.setChecked(True)
        onefile_layout.addWidget(self.nuitka_onefile_checkbox)
        onefile_layout.addWidget(self.create_help_button("Creates a single .exe file containing all dependencies."))
        onefile_layout.addStretch()
        build_mode_layout.addLayout(onefile_layout)

        standalone_layout = QHBoxLayout()
        self.nuitka_standalone_checkbox = QCheckBox("--standalone (create standalone distribution)")
        self.nuitka_standalone_checkbox.setChecked(True)
        standalone_layout.addWidget(self.nuitka_standalone_checkbox)
        standalone_layout.addWidget(self.create_help_button("Includes all dependencies in the output directory."))
        standalone_layout.addStretch()
        build_mode_layout.addLayout(standalone_layout)

        build_mode_desc = QLabel("Note: Both options can be enabled together. --onefile creates a single .exe,\n--standalone ensures all dependencies are included.")
        build_mode_desc.setWordWrap(True)
        build_mode_desc.setStyleSheet("color: gray;")
        build_mode_layout.addWidget(build_mode_desc)

        build_mode_group.setLayout(build_mode_layout)
        layout.addWidget(build_mode_group)

        # Windows options
        windows_group = QGroupBox("Windows Options")
        windows_layout = QVBoxLayout()

        disable_console_layout = QHBoxLayout()
        self.nuitka_disable_console_checkbox = QCheckBox("Disable console window (GUI applications)")
        self.nuitka_disable_console_checkbox.setChecked(True)
        disable_console_layout.addWidget(self.nuitka_disable_console_checkbox)
        disable_console_layout.addWidget(self.create_help_button("Hides the console window when running the application. Use for GUI apps."))
        disable_console_layout.addStretch()
        windows_layout.addLayout(disable_console_layout)

        admin_layout = QHBoxLayout()
        self.nuitka_admin_checkbox = QCheckBox("Request administrator privileges (UAC)")
        admin_layout.addWidget(self.nuitka_admin_checkbox)
        admin_layout.addWidget(self.create_help_button("Requests administrator privileges when running the executable."))
        admin_layout.addStretch()
        windows_layout.addLayout(admin_layout)

        # Icon file
        icon_layout = QHBoxLayout()
        icon_label = QLabel("Icon file (.ico):")
        self.nuitka_icon_edit = QLineEdit()
        self.nuitka_icon_edit.setPlaceholderText("Path to .ico file (optional)")
        icon_browse_btn = QPushButton("Browse...")
        icon_browse_btn.clicked.connect(self.select_icon_file)
        icon_layout.addWidget(icon_label)
        icon_layout.addWidget(self.nuitka_icon_edit)
        icon_layout.addWidget(icon_browse_btn)
        icon_layout.addWidget(self.create_help_button("Custom icon for the executable file."))
        windows_layout.addLayout(icon_layout)

        windows_group.setLayout(windows_layout)
        layout.addWidget(windows_group)

        # Plugins selection
        plugins_group = QGroupBox("Nuitka Plugins")
        plugins_layout = QVBoxLayout()

        tkinter_layout = QHBoxLayout()
        self.nuitka_plugin_tkinter = QCheckBox("tk-inter (Tkinter GUI)")
        tkinter_layout.addWidget(self.nuitka_plugin_tkinter)
        tkinter_layout.addWidget(self.create_help_button("Enable support for Tkinter GUI applications."))
        tkinter_layout.addStretch()
        plugins_layout.addLayout(tkinter_layout)

        pyside6_layout = QHBoxLayout()
        self.nuitka_plugin_pyside6 = QCheckBox("pyside6 (PySide6 GUI)")
        pyside6_layout.addWidget(self.nuitka_plugin_pyside6)
        pyside6_layout.addWidget(self.create_help_button("Enable support for PySide6 GUI applications."))
        pyside6_layout.addStretch()
        plugins_layout.addLayout(pyside6_layout)

        pyqt5_layout = QHBoxLayout()
        self.nuitka_plugin_pyqt5 = QCheckBox("pyqt5 (PyQt5 GUI)")
        pyqt5_layout.addWidget(self.nuitka_plugin_pyqt5)
        pyqt5_layout.addWidget(self.create_help_button("Enable support for PyQt5 GUI applications."))
        pyqt5_layout.addStretch()
        plugins_layout.addLayout(pyqt5_layout)

        numpy_layout = QHBoxLayout()
        self.nuitka_plugin_numpy = QCheckBox("numpy (NumPy support)")
        numpy_layout.addWidget(self.nuitka_plugin_numpy)
        numpy_layout.addWidget(self.create_help_button("Enable support for NumPy library."))
        numpy_layout.addStretch()
        plugins_layout.addLayout(numpy_layout)

        multiprocessing_layout = QHBoxLayout()
        self.nuitka_plugin_multiprocessing = QCheckBox("multiprocessing")
        multiprocessing_layout.addWidget(self.nuitka_plugin_multiprocessing)
        multiprocessing_layout.addWidget(self.create_help_button("Enable support for Python multiprocessing module."))
        multiprocessing_layout.addStretch()
        plugins_layout.addLayout(multiprocessing_layout)

        # Auto-detect button
        auto_detect_btn = QPushButton("Auto-detect required plugins")
        auto_detect_btn.clicked.connect(self.auto_detect_plugins)
        plugins_layout.addWidget(auto_detect_btn)

        plugins_group.setLayout(plugins_layout)
        layout.addWidget(plugins_group)

        # Extra imports
        extra_imports_layout = QVBoxLayout()
        extra_imports_label_layout = QHBoxLayout()
        extra_imports_label = QLabel("Extra imports (comma-separated):")
        extra_imports_label_layout.addWidget(extra_imports_label)
        extra_imports_label_layout.addWidget(self.create_help_button("Additional Python modules to include in the executable that Nuitka might not detect automatically."))
        extra_imports_label_layout.addStretch()
        extra_imports_layout.addLayout(extra_imports_label_layout)
        
        self.nuitka_extra_imports_edit = QLineEdit()
        self.nuitka_extra_imports_edit.setPlaceholderText("e.g., requests, PIL, custom_module")
        extra_imports_layout.addWidget(self.nuitka_extra_imports_edit)
        layout.addLayout(extra_imports_layout)

        # Custom options
        custom_options_layout = QVBoxLayout()
        custom_options_label_layout = QHBoxLayout()
        custom_options_label = QLabel("Custom Nuitka options (space-separated):")
        custom_options_label_layout.addWidget(custom_options_label)
        custom_options_label_layout.addWidget(self.create_help_button("Additional command-line options to pass to Nuitka."))
        custom_options_label_layout.addStretch()
        custom_options_layout.addLayout(custom_options_label_layout)
        
        self.nuitka_custom_options_edit = QLineEdit()
        self.nuitka_custom_options_edit.setPlaceholderText("e.g., --nofollow-imports --assume-yes-for-downloads")
        custom_options_layout.addWidget(self.nuitka_custom_options_edit)
        layout.addLayout(custom_options_layout)

        # Warning note
        warning_note = QLabel("Note: Nuitka must be installed separately: pip install nuitka")
        warning_note.setWordWrap(True)
        warning_note.setStyleSheet("color: orange;")
        layout.addWidget(warning_note)

        layout.addStretch()
        scroll.setWidget(scroll_content)

        nuitka_main_layout = QVBoxLayout(tab)
        nuitka_main_layout.addWidget(scroll)

        return tab


def main():
    app = QApplication(sys.argv)
    window = ObfuscatorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()