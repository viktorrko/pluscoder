from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic
from pymediainfo import MediaInfo
from pyperclip import copy
import sys

global file


class input_info(qtw.QWidget):
    def __init__(self):
        super(input_info, self).__init__()
        uic.loadUi('ui/info.ui', self)

        # DISABLE THE DEFAULT WINDOW FRAME/BACKGROUND
        self.setAttribute(qtc.Qt.WA_TranslucentBackground)
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)

        # SHADOW SETUP
        shadow = qtw.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(qtg.QColor(0, 0, 0, 230))
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        self.base_frame.setGraphicsEffect(shadow)

        # WINDOW MOVING
        def move_window(event):
            # IF LEFT CLICK MOVE WINDOW
            delta = qtc.QPoint(event.globalPos() - self.old_position)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

        self.title_bar.mouseMoveEvent = move_window  # assigns window moving

        # SIZEGRIP
        sizegrip = qtw.QSizeGrip(self.main_frame)
        self.base_layout.addWidget(sizegrip, qtc.Qt.AlignBottom, qtc.Qt.AlignRight)

        # BUTTONS ASSIGN
        self.copy_btn.clicked.connect(self.copy_info)
        self.close_btn.clicked.connect(self.close)

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    def get_info(self, file):
        # runs media info in plain text mode and passes it into the textedit window
        self.i_info = MediaInfo.parse(filename=file, output="")
        self.params_text.setPlainText(self.i_info)

        # echo
        print(f'Parsed info from "{file}"')

    def copy_info(self):
        # copies the whole text into the clipboard
        copy(self.i_info)

        # echo
        print('Copied info to clipboard.')


def main():
    app = qtw.QApplication(sys.argv)
    MainWindow = input_info()
    app.exec_()


if __name__ == '__main__':
    main()
