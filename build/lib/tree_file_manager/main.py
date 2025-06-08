from tree_file_manager.app import TreeFileManager
from PyQt5.QtWidgets import QApplication
import sys

def main():
    app = QApplication(sys.argv)
    window = TreeFileManager()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 