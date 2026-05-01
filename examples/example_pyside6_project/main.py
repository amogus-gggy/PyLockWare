import sys
import re
import os
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSplitter,
)
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import (
    QFont,
    QTextCharFormat,
    QColor,
    QSyntaxHighlighter,
    QTextCursor,
)
from qfluentwidgets import (
    FluentIcon,
    NavigationInterface,
    NavigationItemPosition,
    FluentWindow,
    PushButton,
    ComboBox,
    LineEdit,
    TextEdit,
    MessageBox,
    InfoBar,
    InfoBarPosition,
    TabWidget,
)
from file_panel import FilePanel
# Set dark theme to avoid system contrast colors
from qfluentwidgets import setTheme, Theme


class PythonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Define syntax highlighting rules
        self.highlighting_rules = []

        # Python keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Blue
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "and",
            "as",
            "assert",
            "break",
            "class",
            "continue",
            "def",
            "del",
            "elif",
            "else",
            "except",
            "exec",
            "finally",
            "for",
            "from",
            "global",
            "if",
            "import",
            "in",
            "is",
            "lambda",
            "not",
            "or",
            "pass",
            "print",
            "raise",
            "return",
            "try",
            "while",
            "with",
            "yield",
            "async",
            "await",
            "nonlocal",
            "True",
            "False",
            "None",
        ]
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Orange
        self.highlighting_rules.append((re.compile(r'".*?"'), string_format))
        self.highlighting_rules.append((re.compile(r"'.*?'"), string_format))
        self.highlighting_rules.append(
            (re.compile(r'""".*?"""', re.DOTALL), string_format)
        )
        self.highlighting_rules.append(
            (re.compile(r"'''.*?'''", re.DOTALL), string_format)
        )

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Green
        self.highlighting_rules.append((re.compile(r"#.*$"), comment_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Light green
        self.highlighting_rules.append((re.compile(r"\b\d+\.?\d*\b"), number_format))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#DCDCAA"))  # Yellow
        self.highlighting_rules.append((re.compile(r"\bdef\s+(\w+)"), function_format))

        # Classes
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4EC9B0"))  # Cyan
        self.highlighting_rules.append((re.compile(r"\bclass\s+(\w+)"), class_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class CodeEditor(TextEdit):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Consolas", 11))
        self.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
        self.highlighter = PythonSyntaxHighlighter(self.document())

        # Set tab width to 4 spaces
        self.setTabStopDistance(40)


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Code Editor")
        self.resize(1000, 700)

        # Initialize interface
        self.initNavigation()
        self.initUI()

        self.current_file = None
        self.tab_files = {}  # Dictionary to track file paths by tab index

        # Add initial tab after UI is set up
        self.add_new_tab()

    def initNavigation(self):
        # Add navigation items
        self.navigationInterface.addItem(
            routeKey="editor",
            icon=FluentIcon.EDIT,
            text="Editor",
            onClick=lambda: self.stackedWidget.setCurrentWidget(self.main_container),
        )

        self.navigationInterface.addItem(
            routeKey="settings",
            icon=FluentIcon.SETTING,
            text="Settings",
            onClick=lambda: self.stackedWidget.setCurrentWidget(self.settings_widget),
        )

    def initUI(self):
        # Create main splitter
        from qfluentwidgets import PushButton, FluentIcon

        main_splitter = QSplitter(Qt.Horizontal)

        # Create file panel
        self.file_panel = FilePanel()
        self.file_panel.setMaximumWidth(300)
        self.file_panel.setMinimumWidth(200)
        self.file_panel.file_selected.connect(self.open_file_from_panel)
        main_splitter.addWidget(self.file_panel)

        # Create editor widget container
        self.editor_widget = QWidget()
        editor_layout = QVBoxLayout(self.editor_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.new_button = PushButton(FluentIcon.ADD, "New")
        self.new_button.clicked.connect(lambda: self.add_new_tab())
        toolbar_layout.addWidget(self.new_button)

        self.open_button = PushButton(FluentIcon.FOLDER, "Open")
        self.open_button.clicked.connect(self.open_file)
        toolbar_layout.addWidget(self.open_button)

        self.save_button = PushButton(FluentIcon.SAVE, "Save")
        self.save_button.clicked.connect(self.save_file)
        toolbar_layout.addWidget(self.save_button)

        self.save_as_button = PushButton(FluentIcon.SAVE, "Save As")
        self.save_as_button.clicked.connect(self.save_file_as)
        toolbar_layout.addWidget(self.save_as_button)

        toolbar_layout.addStretch()

        editor_layout.addLayout(toolbar_layout)

        # Create tab widget for multiple files using Fluent TabWidget
        self.tab_widget = TabWidget()
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.tabAddRequested.connect(lambda: self.add_new_tab())

        editor_layout.addWidget(self.tab_widget)

        main_splitter.addWidget(self.editor_widget)

        # Set splitter sizes (30% for file panel, 70% for editor)
        main_splitter.setSizes([300, 700])

        # Create main container widget
        self.main_container = QWidget()
        main_layout = QVBoxLayout(self.main_container)
        main_layout.addWidget(main_splitter)

        # Create settings widget
        self.settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.settings_widget)

        # Font size setting
        font_layout = QHBoxLayout()

        font_layout.addWidget(QLabel("Font Size:"))

        self.font_size_combo = ComboBox()
        self.font_size_combo.addItems(
            ["8", "9", "10", "11", "12", "14", "16", "18", "20"]
        )
        self.font_size_combo.setCurrentText("11")
        self.font_size_combo.currentTextChanged.connect(self.change_font_size)
        font_layout.addWidget(self.font_size_combo)

        settings_layout.addLayout(font_layout)
        settings_layout.addStretch()

        # Add widgets to stacked widget
        self.stackedWidget.addWidget(self.main_container)
        self.stackedWidget.addWidget(self.settings_widget)

        # Set editor as default
        self.stackedWidget.setCurrentWidget(self.main_container)

    def add_new_tab(self, file_path=None):
        """Add a new tab with code editor"""
        editor = CodeEditor()

        if file_path:
            # Load file content
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    editor.setPlainText(file.read())
                # Set tab title to filename
                filename = os.path.basename(file_path)
                tab_index = self.tab_widget.addTab(editor, filename)
                # Track file path
                self.tab_files[tab_index] = file_path
            except Exception as e:
                MessageBox(
                    "Error", f"Could not open file: {str(e)}", parent=self
                ).exec()
                return None
        else:
            # Add new file tab
            tab_index = self.tab_widget.addTab(editor, "New File")
            # Track as new file
            self.tab_files[tab_index] = None

        # Switch to new tab
        self.tab_widget.setCurrentIndex(tab_index)

        return editor

    def close_tab(self, index):
        """Close a tab"""
        # Remove from tracking
        if index in self.tab_files:
            del self.tab_files[index]

        # Update indices for remaining tabs
        new_tab_files = {}
        for i in range(self.tab_widget.count()):
            if i != index:
                old_index = i if i < index else i - 1
                if old_index in self.tab_files:
                    new_tab_files[i] = self.tab_files[old_index]
        self.tab_files = new_tab_files

        # Remove the tab
        self.tab_widget.removeTab(index)

    def get_current_editor(self):
        """Get the current code editor"""
        current_widget = self.tab_widget.currentWidget()
        if isinstance(current_widget, CodeEditor):
            return current_widget
        return None

    def get_current_file_path(self):
        """Get the file path for current tab"""
        current_index = self.tab_widget.currentIndex()
        return self.tab_files.get(current_index)

    def set_current_file_path(self, file_path):
        """Set the file path for current tab"""
        current_index = self.tab_widget.currentIndex()
        self.tab_files[current_index] = file_path
        # Update tab title
        if file_path:
            filename = os.path.basename(file_path)
            self.tab_widget.setTabText(current_index, filename)
        else:
            self.tab_widget.setTabText(current_index, "New File")

    def open_file_from_panel(self, file_path):
        """Open file selected from file panel"""
        # Check if file is already open
        for tab_index, tab_file_path in self.tab_files.items():
            if tab_file_path == file_path:
                # Switch to existing tab
                self.tab_widget.setCurrentIndex(tab_index)
                return

        # Open in new tab
        self.add_new_tab(file_path)

        InfoBar.success(
            title="File Opened",
            content=f"Successfully opened {file_path}",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )

    def new_file(self):
        self.add_new_tab()
        InfoBar.success(
            title="New File",
            content="Created new file",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.open_file_from_panel(file_path)

    def save_file(self):
        current_file = self.get_current_file_path()
        if current_file:
            self.save_to_file(current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.save_to_file(file_path)

    def save_to_file(self, file_path):
        editor = self.get_current_editor()
        if not editor:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(editor.toPlainText())
            self.set_current_file_path(file_path)
            InfoBar.success(
                title="File Saved",
                content=f"Successfully saved to {file_path}",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self,
            )
        except Exception as e:
            MessageBox("Error", f"Could not save file: {str(e)}", parent=self).exec()

    def change_font_size(self, size):
        try:
            font_size = int(size)
            for i in range(self.tab_widget.count()):
                editor = self.tab_widget.widget(i)
                if isinstance(editor, CodeEditor):
                    font = editor.font()
                    font.setPointSize(font_size)
                    editor.setFont(font)
        except ValueError:
            pass


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    

    setTheme(Theme.DARK)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
