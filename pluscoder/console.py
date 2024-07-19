import re

from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from PyQt5 import uic

ffmpeg = './ffmpeg/ffmpeg.exe'
ffprobe = './ffmpeg/ffprobe.exe'

class Console(qtw.QWidget):
    disable_call = qtc.pyqtSignal(int)

    def __init__(self):
        super(Console, self).__init__()
        uic.loadUi('ui/console.ui', self)

        # handles close/minimize buttons
        self.close_btn.clicked.connect(self.close_console)

        # DISABLE THE DEFAULT WINDOW FRAME/BACKGROUND
        self.setAttribute(qtc.Qt.WA_TranslucentBackground)
        self.setWindowFlag(qtc.Qt.FramelessWindowHint)

        # SHADOW SETUP
        shadow = qtw.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(qtg.QColor(0, 0, 0, 200))
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

        # BUTTON SETUP
        self.run_btn.clicked.connect(self.process)

        # DEFAULT EMPTY VALUES
        self.p = None
        self.cmd = ''
        self.frame_count = 1

    def mousePressEvent(self, event):
        # for window moving
        self.old_position = event.globalPos()

    def close_console(self):
        # closes the window and enables the main window UI
        self.close()
        self.handle_disable_call(0)

    def reset_progress_bar(self):
        self.progress_bar.setFormat('%p%')
        self.progress_bar.setStyleSheet("""
                            QProgressBar {
                                background-color: #262626;
                                border: 1px solid #7f7f7f;
                                border-radius: 5px;
                                text-align: center;
                                padding: 1px;
                                }                               
                            QProgressBar::chunk {
                               margin: 1px;
                            }
                            """)
        self.progress_bar.setValue(0)

    def pass_data(self, cmd, frames):
        # gets cmd from the main window
        self.cmd = cmd
        self.frame_count = frames

    # ACTIONS
    def process(self):
        if self.p is None:
            # reset progress bar
            self.reset_progress_bar()

            # prepare process and connect functions
            self.p = qtc.QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.stop_btn.clicked.connect(self.process_stop)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)

            # start the process
            self.message(f'ffmpeg {" ".join(self.cmd)}')
            self.p.start(ffmpeg, self.cmd)

            # echo
            print('\nConverting process started.')

            # enable stop button
            self.stop_btn.setEnabled(True)

    def message(self, s):
        self.console.append(s)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def process_finished(self):
        if self.p.exitCode() == 62097:
            self.progress_bar.setFormat('CANCELED')
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #262626;
                    border: 1px solid #7f7f7f;
                    border-radius: 5px;
                    text-align: center;
                    padding: 1px;
                }

                QProgressBar::chunk {
                margin: 1px;
                background-color: red;
                }
                """)
            self.progress_bar.setValue(100)
            self.message('[PROCESS CANCELED BY USER]')

            # echo
            print('\nConverting process canceled by user.')

        elif self.p.exitCode() != 0:
            self.progress_bar.setFormat('ERROR')
            self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        background-color: #262626;
                        border: 1px solid #7f7f7f;
                        border-radius: 5px;
                        text-align: center;
                        padding: 1px;
                    }

                    QProgressBar::chunk {
                    margin: 1px;
                    background-color: red;
                    }
                    """)
            self.message('[PROCESS ERROR]')

            # echo
            print('\nConverting process returned an error.')

        else:
            self.message('[PROCESS FINISHED]')
            # echo
            print('\nConverting process succesfully finished')

        self.p = None
        self.progress_bar.setValue(100)
        self.stop_btn.setEnabled(False)

    def process_stop(self):
        self.p.kill()

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if 'frame=' in stderr:
            stderr = stderr.strip()
            self.handle_progress_bar(stderr)
            self.message(stderr)
        else:
            self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        if 'frame=' in stdout:
            stdout = stdout.strip()
            self.message(stdout)
        else:
            self.message(stdout)

        self.message(stdout)

    def handle_state(self, state):
        states = {
            qtc.QProcess.NotRunning: 'NOT RUNNING',
            qtc.QProcess.Starting: 'STARTING',
            qtc.QProcess.Running: 'RUNNING',
        }
        state_name = states[state]
        self.message(f"[PROCESS STATE: {state_name}]")

    def handle_progress_bar(self, s):
        frame_regex = re.compile(r'(\d{1,20}) fps=')
        mo = frame_regex.search(s)

        percent = (int(mo.group(1)) / int(self.frame_count)) * 100
        print(f'Current progress: {str(round(percent, 0))}% / frame {mo.group(1)}')

        # print('Percent done: ' + str(round(percent, 0)) + '%')

        self.progress_bar.setValue(int(round(percent, 0)))

    def handle_disable_call(self, value):
        self.disable_call.emit(value)
