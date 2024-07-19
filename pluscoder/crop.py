import re
import subprocess
import tempfile as tf

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import uic

ffmpeg = './ffmpeg/ffmpeg.exe'
ffprobe = './ffmpeg/ffprobe.exe'


class Crop(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(Crop, self).__init__()
        uic.loadUi('ui/crop.ui', self)

        self.setWindowFlag(qtc.Qt.FramelessWindowHint)

        # WINDOW MOVING
        def move_window(event):
            # IF LEFT CLICK MOVE WINDOW
            delta = qtc.QPoint(event.globalPos() - self.old_position)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

        self.title_bar.mouseMoveEvent = move_window

        # DEFAULT EMPTY VALUES
        self.p = None
        self.file = ''
        self.frame_time = 1.0
        self.rect = qtc.QRect(0, 0, 1, 1)

        # GENREAL BUTTON SETUP
        self.discard_btn.clicked.connect(lambda: self.close_handle('discard'))
        self.cancel_btn.clicked.connect(lambda: self.close_handle('cancel'))
        self.confirm_btn.clicked.connect(lambda: self.close_handle('confirm'))

        # creates a label with the frame frame as a parent
        self.crop_guide = qtw.QLabel(self.frame_label)
        self.crop_guide.setStyleSheet("""
                        QLabel {
                            background-color: none;
                            border: 2px solid #00ff00;
                        }
                        """)

        # self.crop_guide.setGeometry(50, 50, 100, 100)
        self.crop_guide.show()

        # calls the rubberband update function
        self.update_crop_guide()

        # connects the signals for the top left
        self.top_x_spin.valueChanged.connect(self.top_left_changed)
        self.top_y_spin.valueChanged.connect(self.top_left_changed)
        self.bottom_x_spin.valueChanged.connect(self.bottom_right_changed)
        self.bottom_y_spin.valueChanged.connect(self.bottom_right_changed)

        # connects buttons
        self.cropdetect_btn.clicked.connect(self.auto_crop)
        self.get_frame_btn.clicked.connect(lambda: self.generate_frame(self.get_frame_input.text()))
        self.background_combo.currentIndexChanged.connect(self.change_bg)

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    # OTHERS #

    def get_info(self, file, frame_count, frame_rate):
        self.file = file
        frame_time = round((float(frame_count) * 0.25) / float(frame_rate), 2)

        self.generate_frame(frame_time)

    def set_frame(self, frame_file):
        # loads the frame, then scales it
        self.frame = qtg.QImage(frame_file)
        self.frame_scaled = self.frame.scaled(640, 360, aspectRatioMode=qtc.Qt.KeepAspectRatio)

        if self.frame.width() != 0:
            # calculates the scale ratio
            self.scale_ratio = float(self.frame_scaled.width() / self.frame.width())

            # sets the frame label geometry based on scaled frame
            self.frame_label.setFixedSize(self.frame_scaled.width(), 360)

            # sets the pixmap and shows it on the label
            pix_map = qtg.QPixmap(self.frame_scaled)
            self.frame_label.setPixmap(pix_map)

            # sets the maximum for the top right corner
            self.top_x_spin.setMaximum(self.frame.width())
            self.top_y_spin.setMaximum(self.frame.height())

            # sets the maximum for the bottom right corner
            self.bottom_x_spin.setValue(self.frame.width())
            self.bottom_x_spin.setMaximum(self.frame.width())
            self.bottom_y_spin.setValue(self.frame.height())
            self.bottom_y_spin.setMaximum(self.frame.height())

            # first rect setup for crop guide
            self.rect = qtc.QRect(0, 0,
                                  self.frame_scaled.width(),
                                  self.frame_scaled.height())
        else:
            print('Frame time not valid.')
            # info box
            msg_box = qtw.QMessageBox()
            msg_box.setWindowTitle(' ')
            msg_box.setText('Frame time not valid.')
            msg_box.setIcon(qtw.QMessageBox.Warning)
            msg_box.exec()

    def change_bg(self):
        # changes the bg of the frame
        if self.background_combo.currentText() == 'black':
            self.frame_space.setStyleSheet("""
                                    QFrame {
                                        background-color: black;
                                        border-radius: 0px;
                                    }
                                    """)

            # echo
            print('Changed the background color to black.')
        else:
            self.frame_space.setStyleSheet("""
                                    QFrame {
                                        background-color: #ededed;
                                        border-radius: 0px;
                                    }
                                    """)

            # echo
            print('Changed the background color to white.')

    def generate_frame(self, frame_time):
        thumb_dir = tf.TemporaryDirectory(prefix='pluscoder-', dir=tf.gettempdir())
        thumb_path = thumb_dir.name + r'\crop_thumb.jpg'

        # echo
        print(f'\nChanging the frame time to: {frame_time}')

        p = subprocess.run(
            f'{ffmpeg} -hide_banner -ss {frame_time} '
            f'-i "{self.file}" -vframes 1 '
            f'"{thumb_path}"',
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # print(str(p.args))

        self.set_frame(thumb_path)
        thumb_dir.cleanup()

    def close_handle(self, arg):
        switch = {
            'cancel': 'cancel',
            'discard': '',
            'confirm': f'crop='
                       f'{int(self.bottom_x_spin.value()) - int(self.top_x_spin.value())}:'
                       f'{self.bottom_y_spin.value() - self.top_y_spin.value()}:'
                       f'{self.top_x_spin.value()}:'
                       f'{self.top_y_spin.value()}'
        }

        self.submitted.emit(switch[arg])

        self.close()

    # CROP GUIDE #

    def calculate_rect(self, value):
        # calculates the value for the rubberband rect
        new_value = round(value * self.scale_ratio)

        return new_value

    def top_left_changed(self):
        # checks for valid values
        if self.top_x_spin.value() < self.bottom_x_spin.value():
            new_x = self.top_x_spin.value()
        else:
            new_x = (self.bottom_x_spin.value() - 1)
            self.top_x_spin.setValue((self.bottom_x_spin.value() - 1))

        if self.top_y_spin.value() < self.bottom_y_spin.value():
            new_y = self.top_y_spin.value()
        else:
            new_y = (self.bottom_y_spin.value() - 1)
            self.top_y_spin.setValue((self.bottom_y_spin.value() - 1))

        # creates a point for the top left corner while already converting the values
        point = qtc.QPoint(self.calculate_rect(new_x), self.calculate_rect(new_y))

        # sets the new top left corner position
        self.rect.setTopLeft(point)

        # updates the rubberband rect and calls the rubberband update function
        self.update_crop_guide()

        # sets the minimum value for the bottom spinbox so they dont interfere
        self.bottom_x_spin.setMinimum(new_x + 1)
        self.bottom_y_spin.setMinimum(new_y + 1)

        # calls the update info fucntion
        self.update_info()

        # debug
        # print(f'calculated new rubberband top-left: {point.x()}, {point.y()}')

    def bottom_right_changed(self):
        # checks for valid values
        if self.bottom_x_spin.value() > self.top_x_spin.value():
            new_x = self.bottom_x_spin.value()
        else:
            new_x = (self.top_x_spin.value() + 1)
            self.bottom_x_spin.setValue((self.top_x_spin.value() + 1))

        if self.bottom_y_spin.value() > self.top_y_spin.value():
            new_y = self.bottom_y_spin.value()
        else:
            new_y = (self.top_y_spin.value() - 1)
            self.bottom_y_spin.setValue((self.top_y_spin.value() + 1))

        # creates a point for the bottom right corner with converted values
        point = qtc.QPoint(self.calculate_rect(new_x), self.calculate_rect(new_y))

        # sets the new bottom right corner position
        self.rect.setBottomRight(point)

        # updates the rubberband rect and calls the rubberband update function
        self.update_crop_guide()

        # sets the minimum value for the top spinbox so they dont interfere
        self.top_x_spin.setMaximum(new_x - 1)
        self.top_y_spin.setMaximum(new_y - 1)

        # calls the update info fucntion
        self.update_info()

        # debug
        # print(f'calculated new rubberband bottom-right: {point.x()}, {point.y()}')

    def update_info(self):
        self.width_value.setText(f'{int(self.bottom_x_spin.value()) - int(self.top_x_spin.value())}')
        self.height_value.setText(f'{self.bottom_y_spin.value() - self.top_y_spin.value()}')

    def update_crop_guide(self):
        self.crop_guide.setGeometry(self.rect)

    def reset_crop(self):
        self.top_x_spin.setValue(0)
        self.top_y_spin.setValue(0)

        # bottom left corner reset
        self.bottom_x_spin.setValue(self.frame.width())
        self.bottom_x_spin.setMaximum(self.frame.width())
        self.bottom_y_spin.setValue(self.frame.height())
        self.bottom_y_spin.setMaximum(self.frame.height())

    # AUTO CROP #

    def auto_crop(self):
        if self.p is None:
            # sets cmd
            file = self.file
            cropdetect = f'cropdetect={self.cd_limit_spin.value()}:' \
                         f'{self.cd_round_spin.value()}:' \
                         f'{self.cd_skip_spin.value()}:' \
                         f'{self.cd_reset_spin.value()}'
            cmd = ['-hide_banner', '-i', str(self.file), '-vf', cropdetect, '-f', 'null', 'NUL']

            # prepare process and connect functions
            self.p = qtc.QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            # self.stop_btn.clicked.connect(self.process_stop)
            # self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)

            # start the process
            # echo
            print('Cropdetect running.')
            self.p.start(ffmpeg, cmd)

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if 'crop=' in stderr:
            stderr = stderr.strip()
            self.handle_crop_output(stderr)
            # self.message(stderr)
        else:
            # self.message(stderr)
            pass

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")

        # self.message(stdout)

    def handle_crop_output(self, s):
        crop_regex = re.compile(r'crop=(\d{1,20}):(\d{1,20}):(\d{1,20}):(\d{1,20})')
        self.mo = crop_regex.search(s)

    def process_finished(self):

        self.p = None
        # print(f'{self.mo.group(1)}:{self.mo.group(2)}:{self.mo.group(3)}:{self.mo.group(4)}')
        w, h, x, y = int(self.mo.group(1)), int(self.mo.group(2)), int(self.mo.group(3)), int(self.mo.group(4))

        # resets the crop before setting new values
        self.reset_crop()

        # sets the cropdetect values
        self.top_x_spin.setValue(x)
        self.top_y_spin.setValue(y)
        self.bottom_x_spin.setValue(x + w)
        self.bottom_y_spin.setValue(y + h)

        # echo
        print('\nCropdetect finished and returned the following values:')
        print(f'crop={w}:{h}:{x}:{y}')

    def message(self, s):
        print(s)
