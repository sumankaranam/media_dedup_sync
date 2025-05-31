import os
import sys
from PyQt5.QtWidgets import QApplication
from ui.app_ui import AppUI

def main():
    app = QApplication(sys.argv)
    window = AppUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()