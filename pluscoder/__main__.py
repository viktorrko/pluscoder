import sys
from PyQt5.QtWidgets import QApplication
from .converter import Converter


def main():
    app = QApplication(sys.argv)
    mainwindow = Converter()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
