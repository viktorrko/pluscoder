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


class libx264(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(libx264, self).__init__()
        uic.loadUi('ui/H264.ui', self)

        ui_def(self)  # loads the generic options

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    @qtc.pyqtSlot()
    def confirm(self):
        if self.tune_combo.currentText() == 'none':
            submit = f"-preset {self.preset_combo.currentText()}"
        else:
            submit = f"-preset {self.preset_combo.currentText()} " \
                     f"-tune {self.tune_combo.currentText()}"  # gets the preset/tune values

        if self.crf_radio.isChecked():
            submit = f"-crf {self.crf_spinbox.value()} {submit}"

        elif self.cbr_radio.isChecked():
            value = int(self.cbr_input.text()[:-1])  # gets value and converts to int for math operations
            unit = self.cbr_input.text()[-1:]  # gets unit

            submit = f"-x264-params 'nal-hrd=cbr' " \
                     f"-b:v {self.cbr_input.text()} " \
                     f"-minrate {self.cbr_input.text()} " \
                     f"-maxrate {self.cbr_input.text()} " \
                     f"-bufsize {str(value * 2) + str(unit)} " \
                     f"{submit}"  # bufsize should be 2 times as big as the requested bitrate

        elif self.vbv_radio.isChecked():
            value = int(self.vbv_input.text()[:-1])  # gets value and converts to int for math operations
            unit = self.vbv_input.text()[-1:]  # gets unit

            submit = f"-b:v {self.vbv_input.text()} " \
                     f"-maxrate {self.vbv_input.text()} " \
                     f"-bufsize {str(value * 2) + str(unit)} " \
                     f"{submit}"  # bufsize should be 2 times as big as the requested bitrate
        self.submitted.emit(submit)
        self.close()


class libx265(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(libx265, self).__init__()
        uic.loadUi('ui/H265.ui', self)

        ui_def(self)  # loads the generic options

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    @qtc.pyqtSlot()
    def confirm(self):
        if self.tune_combo.currentText() == 'none':
            submit = f"-preset {self.preset_combo.currentText()}"
        else:
            submit = f"-preset {self.preset_combo.currentText()} " \
                     f"-tune {self.tune_combo.currentText()}"  # gets the preset/tune values

        if self.lossless_chk.isChecked():
            submit = f"-x265-params lossless=1 " \
                     f"{submit}"

        elif self.crf_radio.isChecked():
            submit = f"-crf {self.crf_spinbox.value()} {submit}"

        elif self.cbr_radio.isChecked():
            value = int(self.cbr_input.text()[:-1])  # gets value and converts to int for math operations
            unit = self.cbr_input.text()[-1:]  # gets unit

            submit = f"-b:v {self.cbr_input.text()} " \
                     f"-minrate {self.cbr_input.text()} " \
                     f"-maxrate {self.cbr_input.text()} " \
                     f"-bufsize {str(value * 2) + str(unit)} " \
                     f"{submit}"  # bufsize should be 2 times as big as the requested bitrate

        self.submitted.emit(submit)
        self.close()


class libvpx_vp9(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(libvpx_vp9, self).__init__()
        uic.loadUi('ui/VP9.ui', self)

        ui_def(self)  # loads the generic options

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    @qtc.pyqtSlot()
    def confirm(self):
        submit = f"-deadline {self.deadline_combo.currentText()} " \
                 f"-cpu-used {self.cpu_spinbox.value()}"  # gets the deadline/cpu util values

        if self.lossless_chk.isChecked():
            submit = f"-lossless 1 " \
                     f"{submit}"

        elif self.cq_radio.isChecked() and self.cq_input.text() == '':  # Constant Quality mode, nothing in input
            submit = f"-crf {self.cq_spinbox.value()} -b:v 0 {submit}"

        elif self.cq_radio.isChecked():  # Constrained Quality mode
            submit = f"-crf {self.cq_spinbox.value()} -b:v {self.cq_input.text()} {submit}"

        elif self.abr_radio.isChecked():  # Average Bitrate mode
            submit = f"-b:v {self.abr_input.text()} {submit}"

        elif self.cbr_radio.isChecked():  # Constant bitrate
            submit = f"-minrate {self.cbr_input.text()} " \
                     f"-maxrate {self.cbr_input.text()} " \
                     f"-b:v {self.cbr_input.text()} " \
                     f"{submit}"

        self.submitted.emit(submit)
        self.close()