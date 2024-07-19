from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic


def ui_def(self):
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

    # TITLE BAR SETUP #
    self.confirm_btn.clicked.connect(self.confirm)  # assigns confirm button

    def move_window(event):
        # IF LEFT CLICK MOVE WINDOW
        delta = qtc.QPoint(event.globalPos() - self.old_position)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_position = event.globalPos()

    self.title_bar.mouseMoveEvent = move_window  # assigns window moving


class aac(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(aac, self).__init__()
        uic.loadUi('ui/AAC.ui', self)

        ui_def(self)  # loads the generic options

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    @qtc.pyqtSlot()
    def confirm(self):
        if self.cbr_radio.isChecked():
            submit = f"-b:a {self.cbr_input.text()} "

        elif self.vbr_radio.isChecked():
            submit = f"-q:a {self.vbr_spinbox.value()} "

        self.submitted.emit(submit)
        self.close()


class libfdk_aac(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(libfdk_aac, self).__init__()
        uic.loadUi('ui/FDK_AAC.ui', self)

        ui_def(self)  # loads the generic options

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    @qtc.pyqtSlot()
    def confirm(self):
        if self.cbr_radio.isChecked():
            submit = f"-b:a {self.cbr_input.text()} "

        elif self.vbr_radio.isChecked():
            submit = f"-q:a {self.vbr_spinbox.value()} "

        self.submitted.emit(submit)
        self.close()


class libmp3lame(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    def __init__(self):
        super(libmp3lame, self).__init__()
        uic.loadUi('ui/MP3.ui', self)

        ui_def(self)  # loads the generic options

    @qtc.pyqtSlot()
    def confirm(self):
        if self.cbr_radio.isChecked():
            submit = f"-b:a {self.cbr_combo.currentText()} "

        elif self.vbr_radio.isChecked():
            submit = f"-q:a {self.vbr_spinbox.value()} "

        self.submitted.emit(submit)
        self.close()


class pcm(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    def __init__(self):
        super(pcm, self).__init__()
        uic.loadUi('ui/PCM.ui', self)

        ui_def(self)  # loads the generic options

        sample_formats = ('pcm_alaw', 'pcm_f32be', 'pcm_f32le', 'pcm_f64be', 'pcm_f64le', 'pcm_mulaw', 'pcm_s16be',
                          'pcm_s16le', 'pcm_s24be', 'pcm_s24le', 'pcm_s32be', 'pcm_s32le', 'pcm_s8', 'pcm_u16be',
                          'pcm_u16le', 'pcm_u24be', 'pcm_u24le', 'pcm_u32be', 'pcm_u32le', 'pcm_u8')
        for i in sample_formats:
            self.format_combo.addItem(i)

        self.format_combo.setCurrentIndex(7)


    @qtc.pyqtSlot()
    def confirm(self):
        submit = self.format_combo.currentText()

        self.submitted.emit(submit)
        self.close()


class flac(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    def __init__(self):
        super(flac, self).__init__()
        uic.loadUi('ui/FLAC.ui', self)

        ui_def(self)  # loads the generic options

    @qtc.pyqtSlot()
    def confirm(self):
        submit = f'-compression_level {self.comp_spinbox.value()}'

        self.submitted.emit(submit)
        self.close()