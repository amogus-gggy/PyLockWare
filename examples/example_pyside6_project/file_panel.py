import os
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from qfluentwidgets import TreeWidget, PushButton, FluentIcon


class FilePanel(QWidget):
    file_selected = Signal(str)  # Signal emitted when a file is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.current_path = os.getcwd()
        self.load_directory(self.current_path)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Add folder selection button
        button_layout = QHBoxLayout()
        self.folder_button = PushButton(FluentIcon.FOLDER, "Select Folder")
        self.folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.folder_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Create tree widget for file system using Fluent TreeWidget
        self.file_tree = TreeWidget()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setRootIsDecorated(True)
        self.file_tree.setAlternatingRowColors(True)
        self.file_tree.setSortingEnabled(True)

        # Connect signals
        self.file_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.file_tree.itemExpanded.connect(self.on_item_expanded)

        layout.addWidget(self.file_tree)

    def load_directory(self, path):
        """Load directory contents into the tree widget"""
        self.current_path = path
        self.file_tree.clear()

        try:
            # Add parent directory option (except for root)
            if os.path.dirname(path) != path:
                parent_item = QTreeWidgetItem(self.file_tree)
                parent_item.setText(0, "..")
                parent_item.setIcon(0, QIcon.fromTheme("folder"))
                parent_item.setData(0, Qt.UserRole, os.path.dirname(path))
                parent_item.setData(1, Qt.UserRole, "folder")

            # Load directories first
            try:
                items = os.listdir(path)
                items.sort(
                    key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower())
                )
            except PermissionError:
                return

            for item_name in items:
                item_path = os.path.join(path, item_name)

                # Skip hidden files and directories
                if item_name.startswith("."):
                    continue

                tree_item = QTreeWidgetItem(self.file_tree)
                tree_item.setText(0, item_name)

                if os.path.isdir(item_path):
                    # Directory
                    tree_item.setIcon(0, QIcon.fromTheme("folder"))
                    tree_item.setData(0, Qt.UserRole, item_path)
                    tree_item.setData(1, Qt.UserRole, "folder")

                    # Add dummy child to show expand arrow
                    dummy = QTreeWidgetItem(tree_item)
                    dummy.setText(0, "Loading...")

                else:
                    # File
                    tree_item.setIcon(0, QIcon.fromTheme("text-x-generic"))
                    tree_item.setData(0, Qt.UserRole, item_path)
                    tree_item.setData(1, Qt.UserRole, "file")

        except Exception as e:
            print(f"Error loading directory {path}: {e}")

    def on_item_double_clicked(self, item, column):
        """Handle double click on tree item"""
        item_path = item.data(0, Qt.UserRole)
        item_type = item.data(1, Qt.UserRole)

        if item_type == "folder":
            # Expand/collapse folder instead of navigating
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        elif item_type == "file":
            # Emit signal for file selection
            self.file_selected.emit(item_path)

    def select_folder(self):
        """Open folder selection dialog"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder", self.current_path
        )
        if folder_path:
            self.load_directory(folder_path)

    def on_item_expanded(self, item):
        """Handle item expansion to load subdirectories"""
        item_path = item.data(0, Qt.UserRole)
        item_type = item.data(1, Qt.UserRole)

        if item_type == "folder":
            # Remove dummy child
            item.takeChild(0)

            try:
                # Load subdirectory contents
                items = os.listdir(item_path)
                items.sort(
                    key=lambda x: (
                        not os.path.isdir(os.path.join(item_path, x)),
                        x.lower(),
                    )
                )

                for sub_item_name in items:
                    if sub_item_name.startswith("."):
                        continue

                    sub_item_path = os.path.join(item_path, sub_item_name)
                    sub_tree_item = QTreeWidgetItem(item)
                    sub_tree_item.setText(0, sub_item_name)

                    if os.path.isdir(sub_item_path):
                        sub_tree_item.setIcon(0, QIcon.fromTheme("folder"))
                        sub_tree_item.setData(0, Qt.UserRole, sub_item_path)
                        sub_tree_item.setData(1, Qt.UserRole, "folder")

                        # Add dummy child for expandable directories
                        dummy = QTreeWidgetItem(sub_tree_item)
                        dummy.setText(0, "Loading...")
                    else:
                        sub_tree_item.setIcon(0, QIcon.fromTheme("text-x-generic"))
                        sub_tree_item.setData(0, Qt.UserRole, sub_item_path)
                        sub_tree_item.setData(1, Qt.UserRole, "file")

            except Exception as e:
                print(f"Error expanding directory {item_path}: {e}")

    def refresh(self):
        """Refresh current directory"""
        self.load_directory(self.current_path)

    def navigate_to_path(self, path):
        """Navigate to specific path"""
        if os.path.exists(path) and os.path.isdir(path):
            self.load_directory(path)
