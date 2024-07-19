import subprocess

from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtMultimediaWidgets as qtmw   # dont delete!!!
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic

# ffmpeg globals
ffmpeg = './ffmpeg/ffmpeg.exe'
ffprobe = './ffmpeg/ffprobe.exe'


class Trim(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)

    def __init__(self):
        super(Trim, self).__init__()
        uic.loadUi('ui/trim.ui', self)

        self.setWindowFlag(qtc.Qt.FramelessWindowHint)

        # WINDOW MOVING
        def move_window(event):
            # IF LEFT CLICK MOVE WINDOW
            delta = qtc.QPoint(event.globalPos() - self.old_position)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

        self.title_bar.mouseMoveEvent = move_window

        # GENREAL BUTTON SETUP
        self.discard_btn.clicked.connect(lambda: self.close_handle('discard'))
        self.cancel_btn.clicked.connect(lambda: self.close_handle('cancel'))
        self.confirm_btn.clicked.connect(lambda: self.close_handle('confirm'))

        # DEFAULT VALUES
        self.file = ''
        self.ss = 0
        self.ss_time.setText(self.time_convert(0))
        self.increment = 100

        # MEDIA PLAYER SETUP
        self.media_player = qtmm.QMediaPlayer(None, qtmm.QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.error.connect(self.handle_error)

        # EVENTS ASSIGN
        self.media_player.durationChanged.connect(self.duration_change)
        self.media_player.positionChanged.connect(self.position_change)
        self.slider.valueChanged.connect(self.slider_move)
        self.increment_spinbox.valueChanged.connect(self.increment_change)

        # BUTTONS ASSIGN
        self.play_btn.clicked.connect(self.play)

        self.set_ss_btn.clicked.connect(self.set_ss)
        self.set_to_btn.clicked.connect(self.set_to)

        self.ss_minus_btn.clicked.connect(lambda: self.increment_move('minus_ss'))
        self.ss_plus_btn.clicked.connect(lambda: self.increment_move('plus_ss'))

        self.to_minus_btn.clicked.connect(lambda: self.increment_move('minus_to'))
        self.to_plus_btn.clicked.connect(lambda: self.increment_move('plus_to'))

    # def resizeEvent(self, event):
    #     # alternative way to disable background
    #     path = qtg.QPainterPath()
    #     path.addRoundedRect(qtc.QRectF(self.rect()), 20, 20)
    #     reg = qtg.QRegion(path.toFillPolygon().toPolygon())
    #     self.setMask(reg)

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    def load_video(self, file):
        # gets video path from main window
        self.file = file

        # loads the video into the mediaplayer object
        self.media_player.setMedia(
            qtmm.QMediaContent(qtc.QUrl.fromLocalFile(self.file)))

        # calls the function to get duration
        self.get_first_duration(self.file)

        self.play()
        self.play()

        # echo
        print('Video loaded.')

    def play(self):
        if self.media_player.state() == qtmm.QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def increment_change(self):
        self.increment = self.increment_spinbox.value()

        # echo
        print(f'Changed the increment to: {self.increment}ms')

    def increment_move(self, arg):
        if arg == 'minus_ss':
            if (self.ss - self.increment) > 0:
                self.ss -= self.increment
                self.ss_time.setText(self.time_convert(self.ss))
                self.media_player.pause()
                self.media_player.setPosition(self.ss)
            else:
                self.ss = 0
                self.ss_time.setText(self.time_convert(self.ss))
                self.media_player.pause()
                self.media_player.setPosition(self.ss)

        elif arg == 'plus_ss':
            if (self.ss + self.increment) < self.duration:
                self.ss += self.increment
                self.ss_time.setText(self.time_convert(self.ss))
                self.media_player.pause()
                self.media_player.setPosition(self.ss)
            else:
                self.ss = self.duration
                self.ss_time.setText(self.time_convert(self.ss))
                self.media_player.pause()
                self.media_player.setPosition(self.ss)

        elif arg == 'minus_to':
            if (self.to - self.increment) > 0:
                self.to -= self.increment
                self.to_time.setText(self.time_convert(self.to))
                self.media_player.pause()
                self.media_player.setPosition(self.to)
            else:
                self.to = 0
                self.to_time.setText(self.time_convert(self.to))
                self.media_player.pause()
                self.media_player.setPosition(self.to)

        elif arg == 'plus_to':
            if (self.to + self.increment) < self.duration:
                self.to += self.increment
                self.to_time.setText(self.time_convert(self.to))
                self.media_player.pause()
                self.media_player.setPosition(self.to)
            else:
                self.to = self.duration
                self.to_time.setText(self.time_convert(self.to))
                self.media_player.pause()
                self.media_player.setPosition(self.to)

    def time_convert(self, pos):
        minutes, seconds = divmod(pos / 1000, 60)
        timecode = f'{minutes:0>2.0f}:{seconds:.2f}'

        return timecode

    def get_first_duration(self, filename):
        result = subprocess.run([ffprobe, "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1", filename],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        self.to = float(result.stdout) * 1000
        self.to = int(self.to)
        self.to_time.setText(self.time_convert(self.to))

        self.duration = self.to

    def duration_change(self, dur):
        self.slider.setRange(0, dur)
        self.duration = dur

    def position_change(self, pos):
        self.slider.setValue(pos)
        self.current_time.setText(self.time_convert(self.media_player.position()))

    def slider_move(self):
        self.media_player.setPosition(self.slider.value())

    def set_to(self):
        self.to = self.media_player.position()
        self.to_time.setText(self.time_convert(self.to))
        print(f'Set to from current playback position to: {str(self.to)}ms')

    def set_ss(self):
        self.ss = self.media_player.position()
        self.ss_time.setText(self.time_convert(self.ss))
        print(f'Set ss from current playback position to: {str(self.ss)}ms')

    def close_handle(self, arg):
        switch = {
            'cancel': 'cancel',
            'discard': '',
            'confirm': f'-ss {round(self.ss / 1000, 2)} -to {round(self.to / 1000, 2)}'
        }

        self.submitted.emit(switch[arg])
        self.media_player.stop()
        self.media_player

        self.close()

    def handle_error(self):
        # self.playButton.setEnabled(False)
        print(self.mediaPlayer.errorString())
