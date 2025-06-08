#!/bin/bash

# Tree File Manager Installation Script
# For Arch Linux and other Linux distributions

set -e

echo "🌳 Tree File Manager Installation Script"
echo "========================================"

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is designed for Linux systems only."
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python 3
if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 first:"
    echo "  Arch Linux: sudo pacman -S python"
    echo "  Ubuntu/Debian: sudo apt install python3"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version found"

# Check for pip
if ! command_exists pip3 && ! command_exists pip; then
    echo "❌ pip is required but not installed."
    echo "Please install pip first:"
    echo "  Arch Linux: sudo pacman -S python-pip"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

PIP_CMD="pip3"
if ! command_exists pip3; then
    PIP_CMD="pip"
fi

echo "✅ pip found"

# Detect package manager for system dependencies
if command_exists pacman; then
    DISTRO="arch"
    echo "📦 Detected Arch Linux"
elif command_exists apt; then
    DISTRO="debian"
    echo "📦 Detected Debian/Ubuntu"
elif command_exists dnf; then
    DISTRO="fedora"
    echo "📦 Detected Fedora"
elif command_exists zypper; then
    DISTRO="opensuse"
    echo "📦 Detected openSUSE"
else
    DISTRO="unknown"
    echo "⚠️  Unknown distribution - will attempt generic installation"
fi

# Install system dependencies
echo ""
echo "📦 Installing system dependencies..."

case $DISTRO in
    "arch")
        echo "Installing PyQt5 and psutil via pacman..."
        sudo pacman -S --needed python-pyqt5 python-psutil
        ;;
    "debian")
        echo "Installing PyQt5 and psutil via apt..."
        sudo apt update
        sudo apt install -y python3-pyqt5 python3-psutil
        ;;
    "fedora")
        echo "Installing PyQt5 and psutil via dnf..."
        sudo dnf install -y python3-qt5 python3-psutil
        ;;
    "opensuse")
        echo "Installing PyQt5 and psutil via zypper..."
        sudo zypper install -y python3-qt5 python3-psutil
        ;;
    *)
        echo "Installing via pip (fallback)..."
        $PIP_CMD install --user PyQt5 psutil
        ;;
esac

# Install Tree File Manager
echo ""
echo "🌳 Installing Tree File Manager..."

if [[ -f "setup.py" ]]; then
    # Install from local source
    echo "Installing from local source..."
    $PIP_CMD install --user .
else
    # Install from PyPI (when published)
    echo "Installing from PyPI..."
    $PIP_CMD install --user tree-file-manager
fi

# Create desktop entry
echo ""
echo "🖥️  Creating desktop entry..."

DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/tree-file-manager.desktop" << EOF
[Desktop Entry]
Name=Tree File Manager
Comment=A modern file manager with tree view
Exec=tree-file-manager
Icon=tree-file-manager
Terminal=false
Type=Application
Categories=System;FileManager;
StartupNotify=true
MimeType=inode/directory;
Keywords=file;manager;explorer;folder;tree;
EOF

# Update desktop database
if command_exists update-desktop-database; then
    update-desktop-database "$DESKTOP_DIR"
fi

# Add to PATH if needed
PYTHON_BIN_DIR="$HOME/.local/bin"
if [[ ":$PATH:" != *":$PYTHON_BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  Adding $PYTHON_BIN_DIR to PATH"
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "export PATH=\"\$PATH:$PYTHON_BIN_DIR\""
    echo ""
    echo "Or run: echo 'export PATH=\"\$PATH:$PYTHON_BIN_DIR\"' >> ~/.bashrc"
    echo "Then restart your terminal or run: source ~/.bashrc"
fi

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To run Tree File Manager:"
echo "   • From terminal: tree-file-manager"
echo "   • From desktop: Look for 'Tree File Manager' in your applications menu"
echo ""
echo "📚 For more information, visit:"
echo "   https://github.com/rishibaghel25/tree-file-manager"
echo ""
echo "🐛 Report issues at:"
echo "   https://github.com/rishibaghel25/tree-file-manager/issues"
