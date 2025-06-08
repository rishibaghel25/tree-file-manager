#!/usr/bin/env python3
"""
Tree File Manager
A modern file manager with tree view for Linux systems

Author: Rishi
License: MIT
Repository: https://github.com/rishibaghel25/tree-file-manager
"""

import sys
import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime
import mimetypes
import tempfile
import stat

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QSplitter, QMenuBar, QMenu, QAction, QStatusBar,
    QMessageBox, QInputDialog, QFileDialog, QDialog, QLabel,
    QTextEdit, QPushButton, QProgressBar, QTabWidget, QLineEdit,
    QComboBox, QCheckBox, QGroupBox, QFormLayout, QDialogButtonBox,
    QFileIconProvider,
    QStyle
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QMimeData, QUrl, QSettings, QFileInfo
from PyQt5.QtGui import QIcon, QFont, QPixmap, QDrag, QCursor, QPalette, QColor

class FileOperationThread(QThread):
    """Thread for handling file operations to prevent UI freezing"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, operation, source, destination=None):
        super().__init__()
        self.operation = operation
        self.source = source
        self.destination = destination

    def run(self):
        try:
            if self.operation == 'copy':
                if os.path.isdir(self.source):
                    shutil.copytree(self.source, self.destination)
                else:
                    shutil.copy2(self.source, self.destination)
            elif self.operation == 'move':
                shutil.move(self.source, self.destination)
            elif self.operation == 'delete':
                if os.path.isdir(self.source):
                    shutil.rmtree(self.source)
                else:
                    os.remove(self.source)

            self.finished.emit(True, "Operation completed successfully")
        except Exception as e:
            self.finished.emit(False, str(e))

class DeviceMonitor(QThread):
    """Monitor connected devices like USB drives, SD cards"""
    devices_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            devices = self.get_mounted_devices()
            self.devices_changed.emit(devices)
            self.msleep(2000)  # Check every 2 seconds

    def get_mounted_devices(self):
        devices = []
        try:
            # Get mounted filesystems
            with open('/proc/mounts', 'r') as f:
                mounts = f.readlines()

            for mount in mounts:
                parts = mount.split()
                if len(parts) >= 2:
                    device = parts[0]
                    mountpoint = parts[1]

                    # Filter for removable devices
                    if ('/media/' in mountpoint or '/mnt/' in mountpoint or
                        '/run/media/' in mountpoint):
                        device_name = os.path.basename(mountpoint)
                        devices.append({
                            'name': device_name,
                            'path': mountpoint,
                            'device': device
                        })
        except:
            pass

        return devices

    def stop(self):
        self.running = False

class PropertiesDialog(QDialog):
    """File/Folder properties dialog"""

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setWindowTitle("Properties")
        self.setModal(True)
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # File info
        info_group = QGroupBox("File Information")
        info_layout = QFormLayout(info_group)

        stat_info = os.stat(self.file_path)

        info_layout.addRow("Name:", QLabel(os.path.basename(self.file_path)))
        info_layout.addRow("Path:", QLabel(self.file_path))
        info_layout.addRow("Size:", QLabel(self.format_size(stat_info.st_size)))
        info_layout.addRow("Type:", QLabel(self.get_file_type()))
        info_layout.addRow("Modified:", QLabel(
            datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        ))
        info_layout.addRow("Permissions:", QLabel(self.get_permissions()))

        layout.addWidget(info_group)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def get_file_type(self):
        if os.path.isdir(self.file_path):
            return "Folder"
        mime_type, _ = mimetypes.guess_type(self.file_path)
        return mime_type or "Unknown"

    def get_permissions(self):
        mode = os.stat(self.file_path).st_mode
        return stat.filemode(mode)

class TreeFileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_path = os.path.expanduser("~")
        self.clipboard = None
        self.clipboard_operation = None  # 'copy' or 'cut'
        self.settings = QSettings("YourOrganization", "TreeFileManager")
        self.current_font_size = 10
        self.icon_provider = QFileIconProvider()
        
        # Navigation history
        self.history = [self.current_path]
        self.history_index = 0

        self.setWindowTitle("Tree File Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('tree_file_manager.png'))

        # Setup UI
        self.setup_ui()
        self.setup_menus()
        self.setup_statusbar()

        # Start device monitoring
        self.device_monitor = DeviceMonitor()
        self.device_monitor.devices_changed.connect(self.update_devices)
        self.device_monitor.start()

        # Load initial data
        self.load_tree()
        self.load_files()

        # Load saved theme and font size
        saved_theme = self.settings.value("theme", "light")
        self.set_theme(saved_theme)

        saved_font_size = self.settings.value("font_size", 10, type=int)
        self.current_font_size = saved_font_size
        self.apply_font_size()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Tree view
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Devices section
        self.devices_tree = QTreeWidget()
        self.devices_tree.setHeaderLabel("Devices")
        self.devices_tree.setMaximumHeight(150)
        self.devices_tree.itemClicked.connect(self.on_device_clicked)
        left_layout.addWidget(self.devices_tree)

        # Directory tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Directories")
        self.tree_widget.itemExpanded.connect(self.on_tree_expanded)
        self.tree_widget.itemClicked.connect(self.on_tree_clicked)
        left_layout.addWidget(self.tree_widget)

        # Right panel - File list
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Navigation and search bar
        nav_layout = QHBoxLayout()
        
        # Back button
        self.back_btn = QPushButton("←")
        self.back_btn.setMaximumWidth(30)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        # Forward button
        self.forward_btn = QPushButton("→")
        self.forward_btn.setMaximumWidth(30)
        self.forward_btn.clicked.connect(self.go_forward)
        self.forward_btn.setEnabled(False)
        nav_layout.addWidget(self.forward_btn)

        # Address bar
        self.address_bar = QLineEdit()
        self.address_bar.setText(self.current_path)
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        nav_layout.addWidget(self.address_bar)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search files...")
        self.search_bar.textChanged.connect(self.filter_files)
        self.search_bar.setMaximumWidth(200)
        nav_layout.addWidget(self.search_bar)

        right_layout.addLayout(nav_layout)

        # File list
        self.file_list = QListWidget()
        self.file_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        self.file_list.setDragDropMode(QListWidget.DragDrop)
        right_layout.addWidget(self.file_list)

        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])

        # Store original items for search filtering
        self.all_file_items = []

    def setup_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_folder_action = QAction("New Folder", self)
        new_folder_action.setShortcut("Ctrl+Shift+N")
        new_folder_action.triggered.connect(self.create_new_folder)
        new_folder_action.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        file_menu.addAction(new_folder_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        exit_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy_file)
        copy_action.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        edit_menu.addAction(copy_action)

        cut_action = QAction("Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut_file)
        cut_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        edit_menu.addAction(cut_action)

        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_file)
        paste_action.setIcon(self.style().standardIcon(QStyle.SP_DialogOkButton))
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        delete_action = QAction("Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_file)
        delete_action.setIcon(self.style().standardIcon(QStyle.SP_DialogDiscardButton))
        edit_menu.addAction(delete_action)

        # View menu
        view_menu = menubar.addMenu("View")

        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_view)
        refresh_action.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        view_menu.addAction(refresh_action)

        view_menu.addSeparator()

        # Zoom actions
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        view_menu.addSeparator()

        # Theme menu
        theme_menu = view_menu.addMenu("Theme")

        light_mode_action = QAction("Light Mode", self)
        light_mode_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_mode_action)

        dark_mode_action = QAction("Dark Mode", self)
        dark_mode_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_mode_action)

    def setup_statusbar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

    def set_theme(self, theme_name):
        if theme_name == "dark":
            self.set_dark_mode()
        else:
            self.set_light_mode()
        self.settings.setValue("theme", theme_name)

    def set_light_mode(self):
        # Reset to default light theme
        self.setStyleSheet("")
        
        # Apply light selection colors
        light_style = '''
            QTreeWidget::item:selected {
                background-color: #90EE90;
                color: black;
            }
            QTreeWidget::item:selected:active {
                background-color: #98FB98;
            }
            QListWidget::item:selected {
                background-color: #90EE90;
                color: black;
            }
            QListWidget::item:selected:active {
                background-color: #98FB98;
            }
        '''
        self.setStyleSheet(light_style)
        
        # Reset palette to default
        QApplication.instance().setPalette(QApplication.instance().style().standardPalette())

    def set_dark_mode(self):
        dark_style = '''
            QMainWindow, QWidget, QSplitter {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTreeWidget, QListWidget, QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QTreeWidget::item:selected, QListWidget::item:selected {
                background-color: #4a4a4a; 
                color: #ffffff;
            }
            QTreeWidget::item:selected:active, QListWidget::item:selected:active {
                background-color: #5a5a5a;
            }
            QMenuBar, QStatusBar {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QMenu::item:selected {
                background-color: #4a4a4a;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
            }
        '''
        self.setStyleSheet(dark_style)

    def zoom_in(self):
        self.current_font_size += 1
        self.apply_font_size()

    def zoom_out(self):
        if self.current_font_size > 5:
            self.current_font_size -= 1
            self.apply_font_size()

    def apply_font_size(self):
        font = self.file_list.font()
        font.setPointSize(self.current_font_size)
        self.file_list.setFont(font)
        self.tree_widget.setFont(font)
        self.devices_tree.setFont(font)

    def add_to_history(self, path):
        """Add path to navigation history"""
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        if not self.history or self.history[-1] != path:
            self.history.append(path)
            self.history_index = len(self.history) - 1
        
        self.update_nav_buttons()

    def update_nav_buttons(self):
        """Update back/forward button states"""
        self.back_btn.setEnabled(self.history_index > 0)
        self.forward_btn.setEnabled(self.history_index < len(self.history) - 1)

    def go_back(self):
        """Go to previous directory in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.address_bar.setText(self.current_path)
            self.load_files()
            self.update_nav_buttons()

    def go_forward(self):
        """Go to next directory in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.address_bar.setText(self.current_path)
            self.load_files()
            self.update_nav_buttons()

    def filter_files(self):
        """Filter files based on search text"""
        search_text = self.search_bar.text().lower()
        
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def load_tree(self):
        """Load directory tree starting from root"""
        self.tree_widget.clear()

        # Add root directories
        root_dirs = ["/", os.path.expanduser("~")]

        for root_dir in root_dirs:
            if os.path.exists(root_dir):
                root_item = QTreeWidgetItem(self.tree_widget)
                root_item.setText(0, "Home" if root_dir.startswith("/home") else "Root")
                root_item.setData(0, Qt.UserRole, root_dir)
                self.load_tree_children(root_item, root_dir)

    def load_tree_children(self, parent_item, path):
        """Load children for a tree item"""
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, item)
                    child_item.setData(0, Qt.UserRole, item_path)

                    # Add placeholder for lazy loading
                    placeholder = QTreeWidgetItem(child_item)
                    placeholder.setText(0, "Loading...")
        except PermissionError:
            pass

    def on_tree_expanded(self, item):
        """Handle tree item expansion for lazy loading"""
        path = item.data(0, Qt.UserRole)
        if path:
            # Remove placeholder
            for i in range(item.childCount()):
                child = item.child(i)
                if child.text(0) == "Loading...":
                    item.removeChild(child)
                    break

            # Load actual children if not already loaded
            if item.childCount() == 0:
                self.load_tree_children(item, path)

    def on_tree_clicked(self, item):
        """Handle tree item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.add_to_history(path)
            self.current_path = path
            self.address_bar.setText(path)
            self.load_files()

    def on_device_clicked(self, item):
        """Handle device item click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self.add_to_history(path)
            self.current_path = path
            self.address_bar.setText(path)
            self.load_files()

    def update_devices(self, devices):
        """Update devices tree"""
        self.devices_tree.clear()

        for device in devices:
            item = QTreeWidgetItem(self.devices_tree)
            item.setText(0, f"{device['name']} ({device['device']})")
            item.setData(0, Qt.UserRole, device['path'])

    def load_files(self):
        """Load files in current directory"""
        self.file_list.clear()
        self.search_bar.clear()

        try:
            items = os.listdir(self.current_path)

            # Sort: directories first, then files
            dirs = [item for item in items if os.path.isdir(os.path.join(self.current_path, item))]
            files = [item for item in items if os.path.isfile(os.path.join(self.current_path, item))]

            for item_name in sorted(dirs) + sorted(files):
                item_path = os.path.join(self.current_path, item_name)
                list_item = QListWidgetItem(item_name)
                list_item.setData(Qt.UserRole, item_path)

                # Set icon based on type using QFileIconProvider
                file_info = QFileInfo(item_path)
                icon = self.icon_provider.icon(file_info)
                list_item.setIcon(icon)

                self.file_list.addItem(list_item)

            self.statusbar.showMessage(f"{len(dirs)} folders, {len(files)} files")

        except PermissionError:
            QMessageBox.warning(self, "Permission Error", "Access denied to this directory")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load directory: {str(e)}")

    def navigate_to_address(self):
        """Navigate to address bar path"""
        path = self.address_bar.text()
        if os.path.exists(path) and os.path.isdir(path):
            self.add_to_history(path)
            self.current_path = path
            self.load_files()
        else:
            QMessageBox.warning(self, "Invalid Path", "The specified path does not exist")
            self.address_bar.setText(self.current_path)

    def on_file_double_clicked(self, item):
        """Handle file double click"""
        file_path = item.data(Qt.UserRole)

        if os.path.isdir(file_path):
            self.add_to_history(file_path)
            self.current_path = file_path
            self.address_bar.setText(file_path)
            self.load_files()
        else:
            # Open file with default application
            try:
                subprocess.run(['xdg-open', file_path])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file: {str(e)}")

    def show_context_menu(self, position):
        """Show context menu for file list"""
        item = self.file_list.itemAt(position)

        menu = QMenu(self)

        if item:
            # File/folder specific actions
            open_action = menu.addAction("Open")
            open_action.triggered.connect(lambda: self.on_file_double_clicked(item))

            open_with_action = menu.addAction("Open With...")
            open_with_action.triggered.connect(lambda: self.open_with(item))

            menu.addSeparator()

            copy_action = menu.addAction("Copy")
            copy_action.triggered.connect(self.copy_file)

            cut_action = menu.addAction("Cut")
            cut_action.triggered.connect(self.cut_file)

            menu.addSeparator()

            rename_action = menu.addAction("Rename")
            rename_action.triggered.connect(lambda: self.rename_file(item))

            delete_action = menu.addAction("Delete")
            delete_action.triggered.connect(self.delete_file)

            menu.addSeparator()

            properties_action = menu.addAction("Properties")
            properties_action.triggered.connect(lambda: self.show_properties(item))

        # General actions
        if self.clipboard:
            paste_action = menu.addAction("Paste")
            paste_action.triggered.connect(self.paste_file)
            menu.addSeparator()

        new_folder_action = menu.addAction("New Folder")
        new_folder_action.triggered.connect(self.create_new_folder)

        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_view)

        menu.exec_(self.file_list.mapToGlobal(position))

    def copy_file(self):
        """Copy selected file/folder"""
        current_item = self.file_list.currentItem()
        if current_item:
            self.clipboard = current_item.data(Qt.UserRole)
            self.clipboard_operation = 'copy'
            self.statusbar.showMessage(f"Copied: {os.path.basename(self.clipboard)}")

    def cut_file(self):
        """Cut selected file/folder"""
        current_item = self.file_list.currentItem()
        if current_item:
            self.clipboard = current_item.data(Qt.UserRole)
            self.clipboard_operation = 'cut'
            self.statusbar.showMessage(f"Cut: {os.path.basename(self.clipboard)}")

    def paste_file(self):
        """Paste file/folder from clipboard"""
        if not self.clipboard:
            return

        source = self.clipboard
        filename = os.path.basename(source)
        destination = os.path.join(self.current_path, filename)

        if os.path.exists(destination):
            reply = QMessageBox.question(
                self, "File Exists",
                f"'{filename}' already exists. Replace it?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        # Start file operation in thread
        operation = 'move' if self.clipboard_operation == 'cut' else 'copy'
        self.file_thread = FileOperationThread(operation, source, destination)
        self.file_thread.finished.connect(self.on_file_operation_finished)
        self.file_thread.start()

        self.statusbar.showMessage("Processing...")

    def delete_file(self):
        """Delete selected file/folder"""
        current_item = self.file_list.currentItem()
        if not current_item:
            return

        file_path = current_item.data(Qt.UserRole)
        filename = os.path.basename(file_path)

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{filename}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.file_thread = FileOperationThread('delete', file_path)
            self.file_thread.finished.connect(self.on_file_operation_finished)
            self.file_thread.start()

            self.statusbar.showMessage("Deleting...")

    def rename_file(self, item):
        """Rename file/folder"""
        old_path = item.data(Qt.UserRole)
        old_name = os.path.basename(old_path)

        new_name, ok = QInputDialog.getText(
            self, "Rename", "Enter new name:", text=old_name
        )

        if ok and new_name and new_name != old_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                self.load_files()
                self.statusbar.showMessage(f"Renamed to: {new_name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename: {str(e)}")

    def create_new_folder(self):
        """Create new folder"""
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")

        if ok and name:
            folder_path = os.path.join(self.current_path, name)
            try:
                os.makedirs(folder_path)
                self.load_files()
                self.statusbar.showMessage(f"Created folder: {name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder: {str(e)}")

    def open_with(self, item):
        """Open file with specific application"""
       
        file_path = item.data(Qt.UserRole)

        apps = [
            ("Text Editor", "gedit"),
            ("Terminal", "gnome-terminal"),
            ("File Manager", "nautilus"),
            ("Custom...", None)
        ]

        app_names = [name for name, _ in apps]
        choice, ok = QInputDialog.getItem(self, "Open With", "Select application:", app_names, 0, False)
        if ok and choice:
            cmd = None
            for name, executable in apps:
                if name == choice:
                    cmd = executable
                    break

            if cmd:
                try:
                    subprocess.Popen([cmd, file_path])
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to open with {choice}: {e}")
            else:
                custom_cmd, ok2 = QInputDialog.getText(self, "Custom Command", "Enter command:")
                if ok2 and custom_cmd:
                    try:
                        subprocess.Popen(custom_cmd.split() + [file_path])
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to run custom command: {e}")

    def show_properties(self, item):
        """Display properties dialog for selected file/folder"""
        file_path = item.data(Qt.UserRole)
        dialog = PropertiesDialog(file_path, self)
        dialog.exec_()

    def on_file_operation_finished(self, success, message):
        """Handle completion of copy/move/delete operations"""
        self.statusbar.showMessage(message, 5000)
        self.load_files()
        # Clear clipboard on move
        if success and self.clipboard_operation == 'cut':
            self.clipboard = None
            self.clipboard_operation = None

    def refresh_view(self):
        """Refresh both tree and file list"""
        self.load_tree()
        self.load_files()
        self.statusbar.showMessage("Refreshed", 2000)

    def closeEvent(self, event):
        """Cleanup on close"""
        self.device_monitor.stop()
        self.device_monitor.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TreeFileManager()
    window.show()
    sys.exit(app.exec_())
