# Tree File Manager

A modern, lightweight file manager with tree view designed specifically for Linux systems, particularly Arch Linux. Features a clean interface with directory tree navigation on the left and file operations on the right.

![Tree File Manager](./icon/tree_file_manager)

## Features

### Core Functionality
- **Dual-pane interface**: Directory tree on the left, file list on the right
- **Device monitoring**: Automatically detects and displays connected USB drives, SD cards, and other removable media
- **Full file operations**: Copy, cut, paste, delete, rename, and create new folders
- **Multiple open methods**: Double-click to open, right-click for "Open With" options
- **File properties**: Detailed information including size, type, permissions, and modification date
- **Keyboard shortcuts**: Standard shortcuts for common operations (Ctrl+C, Ctrl+V, etc.)

### Advanced Features
- **Threaded operations**: File operations run in background threads to prevent UI freezing
- **Context menus**: Right-click context menus for quick access to operations
- **Address bar navigation**: Type paths directly or navigate using the tree
- **Device auto-detection**: Real-time monitoring of mounted devices
- **Permission handling**: Graceful handling of permission errors
- **Modern UI**: Clean, modern interface using Qt5

## Installation

### Prerequisites
- Python 3.7 or higher
- PyQt5
- Linux operating system (tested on Arch Linux)

### From Source

1. Clone the repository:
```bash
git clone https://github.com/rishibaghel25/tree-file-manager.git
cd tree-file-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python tree_file_manager.py
```

### System Installation

1. Install using pip:
```bash
pip install .
```

2. Run from anywhere:
```bash
tree-file-manager
```

### Arch Linux Package

You can create an AUR package or install manually:

```bash
# Create a PKGBUILD (see PKGBUILD file in repository)
makepkg -si
```

## Usage

### Basic Navigation
- **Tree View**: Click on folders in the left pane to navigate
- **File List**: Double-click files to open, folders to navigate
- **Address Bar**: Type paths directly and press Enter
- **Toolbar**: Use Back, Forward, Up, and Refresh buttons

### File Operations
- **Copy**: Select file(s) and press Ctrl+C or right-click → Copy
- **Cut**: Select file(s) and press Ctrl+X or right-click → Cut  
- **Paste**: Press Ctrl+V or right-click → Paste in destination folder
- **Delete**: Select file(s) and press Delete key or right-click → Delete
- **Rename**: Right-click → Rename or select and press F2
- **New Folder**: Right-click in empty space → New Folder or Ctrl+Shift+N

### Device Management
- Connected USB drives, SD cards appear in the "Devices" section
- Click on any device to navigate to its mount point
- Automatic detection when devices are plugged/unplugged

### Keyboard Shortcuts
- `Ctrl+C` - Copy selected files
- `Ctrl+X` - Cut selected files
- `Ctrl+V` - Paste files
- `Ctrl+Shift+N` - Create new folder
- `Delete` - Delete selected files
- `F5` - Refresh current view
- `Ctrl+Q` - Quit application

## Screenshots

### Main Interface
The main window shows the directory tree on the left and file list on the right:

### Context Menu
Right-click on files for quick access to operations:

### Properties Dialog
View detailed file information:

## Configuration

The application stores its configuration in:
- Linux: `~/.config/tree-file-manager/`

## Development

### Project Structure
```
tree-file-manager/
├── tree_file_manager.py     # Main application file
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
├── README.md               # This file
├── LICENSE                 # MIT License
├── PKGBUILD               # Arch Linux package build
├── tree-file-manager.desktop # Desktop entry
└── icons/                 # Application icons
    └── tree-file-manager.png
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Building from Source
```bash
# Clone repository
git clone https://github.com/rishibaghel25/tree-file-manager.git
cd tree-file-manager

# Install development dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest tests/

# Build package
python setup.py sdist bdist_wheel
```

## Architecture

### Core Components
- **TreeFileManager**: Main application window and coordinator
- **FileOperationThread**: Handles file operations in background
- **DeviceMonitor**: Monitors connected devices in real-time
- **PropertiesDialog**: Shows detailed file/folder information

### Threading Model
- UI runs on main thread
- File operations (copy, move, delete) run on worker threads
- Device monitoring runs on separate thread
- All threads communicate via Qt signals/slots for thread safety

## Troubleshooting

### Common Issues

**Permission Denied Errors**
- The application respects system permissions
- Run with appropriate privileges if needed
- Some system directories may not be accessible

**Device Not Detected**
- Ensure device is properly mounted
- Check `/proc/mounts` for mount points
- Device must be mounted under `/media/`, `/mnt/`, or `/run/media/`

**Application Won't Start**
- Verify PyQt5 is installed: `pip list | grep PyQt5`
- Check Python version: `python --version` (3.7+ required)
- Install missing dependencies: `pip install -r requirements.txt`

### Performance Tips
- Large directories may take time to load
- File operations on network drives will be slower
- Use refresh (F5) if directory contents don't update

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with PyQt5 for cross-platform GUI
- Inspired by traditional file managers like Nautilus and Dolphin
- Designed specifically for Linux desktop environments

## Roadmap

### Planned Features
- [ ] Tabbed interface for multiple locations
- [ ] Search functionality
- [ ] Bookmarks/favorites
- [ ] Archive support (zip, tar, etc.)
- [ ] Network location support
- [ ] Thumbnail previews for images
- [ ] Bulk rename operations
- [ ] Custom themes and icon sets
- [ ] Plugin system for extensions

### Version History
- **v1.0.0** - Initial release with core functionality
  - Dual-pane interface
  - Basic file operations
  - Device monitoring
  - Context menus and shortcuts

## Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/rishibaghel25/tree-file-manager/issues)
- **Discussions**: Join discussions on [GitHub Discussions](https://github.com/rishibaghel25/tree-file-manager/discussions)
- **Email**: Contact the maintainer at rishinamansingh@gmail.com

[![PyPI](https://img.shields.io/pypi/v/tree-file-manager)](https://pypi.org/project/tree-file-manager/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**Note**: This file manager is designed for Linux systems. While it may work on other Unix-like systems, it's optimized for Linux desktop environments.
