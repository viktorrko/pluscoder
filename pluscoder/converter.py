import os
import datetime as dt
from pluscoder import resources  # dont delete!!!

from pathlib import Path
from shlex import split as xsplit
from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw
from PyQt5 import uic
from hurry.filesize import size, alternative

from .acodec_configs import aac, libfdk_aac, libmp3lame, pcm, flac
from .console import Console
from .crop import Crop
from .input_actions import input_actions as ia
from .input_info import input_info
from .preset_actions import save_preset, load_preset
from .trim import Trim
from .vcodec_configs import libx264, libx265, libvpx_vp9

# ffmpeg globals
ffmpeg = './ffmpeg/ffmpeg.exe'
ffprobe = './ffmpeg/ffprobe.exe'


class Converter(qtw.QMainWindow):
    def __init__(self):
        super(Converter, self).__init__()
        uic.loadUi('ui/main.ui', self)

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

        # TITLE BAR SETUP #
        # handles window moving
        def move_window(event):
            # IF LEFT CLICK MOVE WINDOW
            delta = qtc.QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()

        self.title_bar.mouseMoveEvent = move_window  # assigns window moving

        # handles close/minimize buttons
        self.close_btn.clicked.connect(qtw.QApplication.quit)
        self.minimize_btn.clicked.connect(self.showMinimized)

        # SIDEBAR SETUP #
        self.console_btn.clicked.connect(self.run_prepare)
        self.open_btn.clicked.connect(self.open_file)
        self.preset_save_btn.clicked.connect(self.save_preset)
        self.preset_load_btn.clicked.connect(self.load_preset)

        self.console_instance = Console()

        # INPUT WINDOW SETUP #
        self.trim = ''  # populates the value with the generic value
        self.crop = ''  # populates the value with the generic value

        # button assign
        self.i_icon.mousePressEvent = self.open_file
        self.i_info.clicked.connect(self.call_input_info)
        self.i_trim.clicked.connect(self.call_trim)
        self.i_crop.clicked.connect(self.call_crop)

        # window instances
        self.input_info_instance = input_info()
        self.trim_instance = Trim()
        self.crop_instance = Crop()

        # VIDEO WINDOW SETUP #
        self.o_parameters_v = '-crf 17'  # populates the value with the generic value
        self.vcodec_config_helper.setText(self.o_parameters_v)  # updates the helper on startup

        self.vcodec_combo.addItem('Copy', 'copy')
        self.vcodec_combo.addItem('Custom', 'custom')
        self.vcodec_combo.addItem('H264', 'libx264')
        self.vcodec_combo.addItem('H265', 'libx265')
        self.vcodec_combo.addItem('VP9', 'libvpx-vp9')

        self.vcodec_combo.setCurrentIndex(2)
        self.vcodec_combo.currentIndexChanged.connect(self.vcodec_combo_update)  # live updating

        # populate resolution combobox
        supported_res = ("3840:2160", "2560:1440", "1920:1080", "1280:720", "640:480")
        self.v_res_combo.addItem("Keep", 'keep')
        self.v_res_combo.addItem("Custom", 'custom')
        for i in supported_res:
            self.v_res_combo.addItem(f'{i}')
        self.v_res_combo.currentTextChanged.connect(self.v_res_combo_update)  # live updating

        # populate fps combobox
        self.v_fps_combo.addItem("Keep", 'keep')
        self.v_fps_combo.setCurrentIndex(10)

        # video codec config button setup
        self.libx264_instance = libx264()
        self.libx265_instance = libx265()
        self.libvpx_vp9_instance = libvpx_vp9()
        self.vcodec_config_btn.clicked.connect(self.vcodec_config)

        # AUDIO WINDOW SETUP #
        # populate codec combobox
        self.o_parameters_a = '-b:a 128k'  # populates the value with the generic value
        self.acodec_config_helper.setText(self.o_parameters_a)  # updates the helper on launch
        self.acodec_combo.addItem('Copy', 'copy')
        self.acodec_combo.addItem('Custom', 'custom')
        self.acodec_combo.addItem('AAC', 'aac')
        self.acodec_combo.addItem('MP3', 'libmp3lame')
        self.acodec_combo.addItem('PCM', 'pcm')
        self.acodec_combo.addItem('FLAC', 'flac')
        self.acodec_combo.setCurrentIndex(2)
        self.acodec_combo.currentTextChanged.connect(self.acodec_combo_update)  # live updating

        # audio codec config button setup
        self.aac_instance = aac()
        self.libfdk_aac_instance = libfdk_aac()
        self.libmp3lame_instance = libmp3lame()
        self.pcm_instance = pcm()
        self.flac_instance = flac()

        self.acodec_config_btn.clicked.connect(self.acodec_config)

        # OUTPUT SECTION SETUP #
        # path
        self.output_dir = os.path.expanduser(r"~\Videos")

        # updated the path indicator
        self.o_destination_path.setText(self.output_dir)

        # destination button
        self.o_destination_btn.clicked.connect(self.get_output_path)

        # populate extension combobox
        self.o_container_combo.addItem('Custom', 'custom')
        self.o_container_combo.addItem('MP4', 'mp4')
        self.o_container_combo.addItem('AVI', 'avi')
        self.o_container_combo.addItem('MOV', 'mov')
        self.o_container_combo.addItem('MKV', 'mkv')
        self.o_container_combo.addItem('WAV', 'wav')
        self.o_container_combo.addItem('MP3', 'mp3')
        self.o_container_combo.setCurrentIndex(1)
        self.o_container_combo.currentTextChanged.connect(self.o_container_combo_update)  # live updating

        # SHOW THE WINDOW
        self.show()

        print('pluscoder 1.0')
        print('Import a file to start.')

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    # SIDEBAR #

    def open_file(self, event):
        # echo
        print('\nSelecting a file...')

        # opens the file dialog
        new_file, _ = qtw.QFileDialog.getOpenFileName(self, "Open File")

        # checks if user didnt cancel the input dialog
        if new_file != '':
            # echo
            print('File selected.')
            print('\nChecking compatibility...')

            # checks if ffmpeg can handle the file
            if ia.input_validation(self, new_file) == 0:
                self.file = Path(new_file)
                new_file = ''

                # echo
                print('File compatible.')
                print(f'\nImporting file "{self.file}" ...')

                # SETTING QUICK ATTRIBUTES #
                # gets name and extension for passing to the GUI
                filename = os.path.split(self.file)
                self.i_title.setText(os.path.splitext(filename[1])[0])
                self.i_ext.setText(os.path.splitext(filename[1])[1])

                # calls the input_parameters function and stores the data
                i_parameters = ia.input_parameters(self, self.file)
                i_parameters_g = i_parameters.general_tracks[0]
                if i_parameters.video_tracks:
                    i_parameters_v = i_parameters.video_tracks[0]
                if i_parameters.audio_tracks:
                    i_parameters_a = i_parameters.audio_tracks[0]

                self.frame_count = i_parameters_v.frame_count
                self.frame_rate = i_parameters_v.frame_rate

                # gets duration in ms and converts it to time code
                raw_duration = str(dt.timedelta(milliseconds=i_parameters_g.duration))
                self.i_duration.setText(raw_duration[:-3])  # cuts off the last 3 digits
                self.i_size.setText(str(size(i_parameters_g.file_size, system=alternative)))
                try:
                    self.i_resolution.setText(str(f"{i_parameters_v.width}x{i_parameters_v.height}"))
                except:
                    self.i_resolution.setText('(none)')

                try:
                    self.i_framerate.setText(str(f"{i_parameters_v.frame_rate} fps"))
                except:
                    self.i_framerate.setText('(none)')

                try:
                    self.i_pix_format.setText(str(f"{i_parameters_v.color_space} {i_parameters_v.chroma_subsampling}"))
                except:
                    self.i_pix_format.setText('(none)')

                try:
                    self.i_vcodec.setText(str(f"{i_parameters_v.format} ({size(i_parameters_v.bit_rate)}B/s)"))
                except:
                    self.i_vcodec.setText('(none)')

                try:
                    self.i_acodec.setText(str(f"{i_parameters_a.format} ({size(i_parameters_a.bit_rate)}B/s)"))
                except:
                    self.i_acodec.setText('(none)')

                # call the thumbnail generation function
                ia.input_thumbnail(self, self.file, self.frame_count, self.frame_rate)

                # echo
                print('File attributes set...')

                # set output name
                self.o_name_input.setText(os.path.splitext(filename[1])[0])

                # enable start button
                self.console_btn.setEnabled(True)

                # enables other inputs
                self.i_contents_frame.setEnabled(True)

                print('\nFile imported succesfully.')
            else:
                msg_box = qtw.QMessageBox()
                msg_box.setWindowTitle(' ')
                msg_box.setText('File could not be imported.')
                msg_box.setIcon(qtw.QMessageBox.Warning)
                msg_box.exec()
                print('\nFile could not be imported.')
        else:
            print("\nFile import canceled.")

    def save_preset(self):
        arg_dict = {
            'vcodec': self.vcodec_combo.currentIndex(),
            'vcodec_custom': self.vcodec_input.text(),
            'vcodec_param': self.o_parameters_v,
            'v_res': self.v_res_combo.currentIndex(),
            'v_res_custom': self.v_res_input.text(),
            'v_fps': self.v_fps_combo.currentIndex(),
            'v_custom': self.v_custom_input.text(),
            'yuv420': self.v_yuv420_chk.isChecked(),
            'faststart': self.v_faststart_chk.isChecked(),

            'acodec': self.acodec_combo.currentIndex(),
            'acodec_custom': self.acodec_input.text(),
            'acodec_param': self.o_parameters_a,
            'a_sample': self.a_sample_combo.currentIndex(),
            'a_custom': self.a_custom_input.text(),

            'o_ext': self.o_container_combo.currentIndex(),
            'o_ext_custom': self.o_container_input.text(),
            'o_vn': self.o_vn_chk.isChecked(),
            'o_an': self.o_an_chk.isChecked(),
        }

        save_preset(arg_dict)

    def load_preset(self):
        # LOADS THE PRESET

        config = load_preset()
        if config:
            # echo
            print('Loading the preset...')

            # mutates the configparser object
            video = config['VIDEO']
            audio = config['AUDIO']
            output = config['OUTPUT']

            # VIDEO
            self.vcodec_combo.setCurrentIndex(video.getint('vcodec'))
            self.vcodec_input.setText(video['vcodec_custom'])
            self.o_parameters_v = video['vcodec_param']
            self.vcodec_config_helper.setText(self.o_parameters_v)
            self.v_res_combo.setCurrentIndex(video.getint('v_res'))
            self.v_res_input.setText(video['v_res_custom'])
            self.v_fps_combo.setCurrentIndex(video.getint('v_fps'))
            self.v_custom_input.setText(video['v_custom'])
            self.v_yuv420_chk.setChecked(video.getboolean('yuv420'))
            self.v_faststart_chk.setChecked(video.getboolean('faststart'))

            # AUDIO
            self.acodec_combo.setCurrentIndex(audio.getint('acodec'))
            self.acodec_input.setText(audio['acodec_custom'])
            self.o_parameters_a = audio['acodec_param']
            self.acodec_config_helper.setText(self.o_parameters_a)
            self.a_sample_combo.setCurrentIndex(audio.getint('a_sample'))
            self.a_custom_input.setText(audio['a_custom'])

            # OUTPUT
            self.o_container_combo.setCurrentIndex(output.getint('o_ext'))
            self.o_container_input.setText(output['o_ext_custom'])
            self.o_vn_chk.setChecked(output.getboolean('o_vn'))
            self.o_an_chk.setChecked(output.getboolean('o_an'))

            print('\nPreset loaded.')
            msg_box = qtw.QMessageBox()
            msg_box.setWindowTitle(' ')
            msg_box.setText('Preset loaded.')
            msg_box.setIcon(qtw.QMessageBox.Information)
            msg_box.exec()

    # INPUT #

    def call_input_info(self):
        self.input_info_instance.show()
        # echo
        print('\nInfo window opened.')

        self.input_info_instance.get_info(self.file)

    def call_trim(self):
        # calls the trim function
        self.trim_instance.show()
        # echo
        print('\nTrim window opened.')

        self.trim_instance.load_video(str(self.file))

        try:
            self.trim_instance.submitted.connect(self.get_trim, qtc.Qt.UniqueConnection)
        except TypeError:
            pass

    def get_trim(self, trim):
        # collects the trim arguments from the trim window
        if trim == 'cancel':
            print('\nNo changes were made to the trim parameters.')
            print(self.trim)
        else:
            self.trim = trim
            if self.trim == '':
                print('\nNo trimming will be applied.')
            else:
                print('\nNew trim parameters:')
                print(self.trim)

    def call_crop(self):
        # echo
        print('\nCrop window opened.')

        # calls the crop function
        self.crop_instance.get_info(self.file, self.frame_count, self.frame_rate)
        self.crop_instance.show()

        # connect the submitted signal
        try:
            self.crop_instance.submitted.connect(self.get_crop, qtc.Qt.UniqueConnection)
        except TypeError:
            pass

    def get_crop(self, crop):
        if crop == 'cancel':
            print('\nNo changes were made to the crop parameters.')
            print(self.crop)
        else:
            self.crop = crop
            if self.crop == '':
                print('\nNo cropping will be applied.')
            else:
                print('\nNew crop parameters:')
                print(self.crop)

    # VIDEO #

    def vcodec_combo_update(self):
        # handles updates each time the combo value is changed
        # enables/disabled inputs based on the type of codec
        if self.vcodec_combo.currentData() == 'custom':
            self.vcodec_input.setEnabled(True)
            self.vcodec_config_btn.setEnabled(False)
            self.v_res_combo.setEnabled(True)
            self.v_res_input.setEnabled(False)
            self.v_fps_combo.setEnabled(True)
            self.vcodec_config_helper.setText('(custom)')
        elif self.vcodec_combo.currentData() == 'copy':
            self.vcodec_input.setEnabled(False)
            self.vcodec_config_btn.setEnabled(False)
            self.v_res_combo.setEnabled(False)
            self.v_res_input.setEnabled(False)
            self.v_fps_combo.setEnabled(False)
        else:
            self.vcodec_input.setEnabled(False)
            self.vcodec_config_btn.setEnabled(True)
            self.v_res_combo.setEnabled(True)
            self.v_res_input.setEnabled(False)
            self.v_fps_combo.setEnabled(True)

        # sets the default parameters for each codec
        if self.vcodec_combo.currentData() == 'copy' or self.vcodec_combo.currentData() == 'custom':
            self.o_parameters_v = ''
        elif self.vcodec_combo.currentData() == 'libx264' or self.vcodec_combo.currentData() == 'libx265':
            self.o_parameters_v = '-crf 17'
        elif self.vcodec_combo.currentData() == 'libvpx-vp9':
            self.o_parameters_v = '-crf 31'

        # updates the helper text
        self.vcodec_config_helper.setText(self.o_parameters_v)

        # echo
        print(f'Changed the current video codec to: {self.vcodec_combo.currentData()}')

    def v_res_combo_update(self):
        # enables custom input for resolution
        if self.v_res_combo.currentData() == 'custom':
            self.v_res_input.setEnabled(True)
        else:
            self.v_res_input.setEnabled(False)

    def vcodec_config(self):
        # makes sure to open the right settings windows

        # H264 check
        if self.vcodec_combo.currentData() == 'libx264':
            try:
                self.libx264_instance.submitted.connect(self.vcodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.libx264_instance.show()

        # H265 check
        elif self.vcodec_combo.currentData() == 'libx265':
            try:
                self.libx265_instance.submitted.connect(self.vcodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.libx265_instance.show()

        # VP9 check
        elif self.vcodec_combo.currentData() == 'libvpx-vp9':
            try:
                self.libvpx_vp9_instance.submitted.connect(self.vcodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.libvpx_vp9_instance.show()

    def vcodec_config_get(self, v_submit):
        # used to get the parameters from the popup window
        self.o_parameters_v = v_submit
        self.vcodec_config_helper.setText(self.o_parameters_v)

        # echo
        print('\nNew video codec config parameters:')
        print(self.o_parameters_v)

    # AUDIO #

    def acodec_combo_update(self):
        # enables/disabled buttons based on codec choice
        if self.acodec_combo.currentData() == 'custom':
            self.acodec_input.setEnabled(True)
            self.acodec_config_btn.setEnabled(False)
            self.acodec_config_helper.setText('(custom)')
        elif self.acodec_combo.currentData() == 'copy':
            self.acodec_input.setEnabled(False)
            self.acodec_config_btn.setEnabled(False)
            self.acodec_input.setEnabled(False)
            self.a_sample_combo.setEnabled(False)
            self.acodec_config_helper.setText('')
        else:
            self.acodec_input.setEnabled(False)
            self.acodec_input.setEnabled(False)
            self.acodec_config_btn.setEnabled(True)
            self.a_sample_combo.setEnabled(True)

        if self.acodec_combo.currentData() == 'aac' or self.acodec_combo.currentData() == 'libfdk_aac' or self.acodec_combo.currentData() == 'libmp3lame':
            self.o_parameters_a = '-b:a 128k'
            self.acodec_config_helper.setText(self.o_parameters_a)
        elif self.acodec_combo.currentData() == 'pcm':
            self.o_parameters_a = 'pcm_s16le'
            self.acodec_config_helper.setText(self.o_parameters_a)
        elif self.acodec_combo.currentData() == 'flac':
            self.o_parameters_a = '-compression_level 6'
            self.acodec_config_helper.setText(self.o_parameters_a)

        # echo
        print(f'\nChanged the current video codec to: {self.acodec_combo.currentData()}')

    def acodec_config(self):
        # makes sure to open the right config windows
        if self.acodec_combo.currentData() == 'aac':
            try:
                self.aac_instance.submitted.connect(self.acodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.aac_instance.show()

        elif self.acodec_combo.currentData() == 'libfdk_aac':
            try:
                self.libfdk_aac_instance.submitted.connect(self.acodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.libfdk_aac_instance.show()

        elif self.acodec_combo.currentData() == 'libmp3lame':
            try:
                self.libmp3lame_instance.submitted.connect(self.acodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.libmp3lame_instance.show()

        elif self.acodec_combo.currentData() == 'pcm':
            try:
                self.pcm_instance.submitted.connect(self.acodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.pcm_instance.show()

        elif self.acodec_combo.currentData() == 'flac':
            try:
                self.flac_instance.submitted.connect(self.acodec_config_get, qtc.Qt.UniqueConnection)
            except TypeError:
                pass
            self.flac_instance.show()

    def acodec_config_get(self, a_submit):
        # used to get the parameters from the popup window
        self.o_parameters_a = a_submit
        self.acodec_config_helper.setText(self.o_parameters_a)

        # echo
        print('\nNew video codec config parameters:')
        print(self.o_parameters_a)

    # OUTPUT #

    def o_container_combo_update(self):
        # enables custom inputs
        if self.o_container_combo.currentData() == 'custom':
            self.o_container_input.setEnabled(True)
        else:
            self.o_container_input.setEnabled(False)

    def get_output_path(self):
        # echo
        print('\nSelecting a new output path...')

        new_output_path = qtw.QFileDialog.getExistingDirectory(self, "Select a destination path")

        if new_output_path != '':
            self.output_dir = new_output_path
            self.o_destination_path.setText(self.output_dir)

            # echo
            print('New output path selected:')
            print(self.output_dir)
        else:
            # echo
            print('Output path selection canceled.')

    # RUN PREPARE #

    def run_prepare(self):
        # VIDEO COMPILE #
        if self.vcodec_combo.currentData() == 'copy':
            vcodec = 'copy'
        elif self.vcodec_combo.currentData() == 'custom':
            vcodec = self.vcodec_input.text()
        else:
            vcodec = self.vcodec_combo.currentData()

        # video resolution handle
        if self.v_res_combo.currentData() == 'keep':
            res = ''
        elif self.v_res_combo.currentData() == 'custom':
            res = 'scale=' + self.v_res_input.text()
        else:
            res = 'scale=' + self.v_res_combo.currentText()

        # crop handle
        crop = self.crop

        # video filter handle
        if self.vcodec_combo.currentData() == 'copy':
            vf = ''
        elif res == '' and crop == '':  # NO res and NO crop
            vf = ''
        elif res != '' and crop == '':  # YES res and NO crop
            vf = f'-vf {res}'
        elif res == '' and crop != '':  # NO res and YES crop
            vf = f'-vf {crop}'
        elif res != '' and crop != '':  # YES res and YES crop
            vf = f'-vf {crop},{res}'

        # framerate handle
        if self.v_fps_combo.currentData() == 'keep' or self.vcodec_combo.currentData() == 'copy':
            framerate = ''
        else:
            framerate = f"-r {self.v_fps_combo.currentText()}"

        # final compile
        v_cmd = f"-y -hide_banner " \
                f"{self.i_preinput_input.text()} " \
                f"""-i "{self.file}" """ \
                f"-c:v {vcodec} " \
                f"{self.o_parameters_v} " \
                f"{vf} " \
                f"{framerate} " \
                f"{self.v_custom_input.text()} " \
                f"{self.trim}"

        # checks for yuv420p
        if self.v_yuv420_chk.isChecked():
            v_cmd = f"{v_cmd} -pix_fmt yuv420p"

        # checks for faststart flag
        if self.v_faststart_chk.isChecked():
            v_cmd = f"{v_cmd} -movflags +faststart"

        # AUDIO COMPILE #
        if self.acodec_combo.currentData() == 'custom':  # checks for custom codec
            acodec = self.vcodec_input.text()
            self.o_parameters_a = ''
        elif self.acodec_combo.currentData() == 'copy':  # checks for copy
            acodec = 'copy'
            self.o_parameters_a = ''
        elif self.acodec_combo.currentData() == 'pcm':
            acodec = ''
        else:
            acodec = self.acodec_combo.currentData()

        if self.a_sample_combo.currentText() == 'Keep':
            sample_rate = ''
        else:
            sample_rate = f"-ar {self.a_sample_combo.currentText()[:-2]}"

        # final compile
        a_cmd = f"-c:a {acodec} " \
                f"{self.o_parameters_a} " \
                f"{sample_rate} " \
                f"{self.a_custom_input.text()} "

        # OUTPUT COMPILE #
        if self.o_container_combo.currentData() == 'custom':
            o_ext = self.o_container_input.text()
            if o_ext[0] == '.':
                o_ext = o_ext[1:]
        else:
            o_ext = self.o_container_combo.currentData()

        output_path = Path(f""" "{self.output_dir}/{self.o_name_input.text()}.{o_ext}" """)

        o_cmd = ''
        if self.o_vn_chk.isChecked():
            o_cmd = f"-vn"
        if self.o_an_chk.isChecked():
            o_cmd = f"{o_cmd} -an"

        o_cmd = f"{o_cmd} {output_path}"

        # builds the final command
        cmd = (' '.join(v_cmd.split()) + ' ' + ' '.join(a_cmd.split()) + ' ' + ' '.join(o_cmd.split()))
        cmd = xsplit(cmd)

        # handles disabling the main window
        try:
            self.console_instance.disable_call.connect(self.disable_ui, qtc.Qt.UniqueConnection)
        except TypeError:
            pass

        # passes the data to console
        self.console_instance.pass_data(cmd, self.frame_count)
        self.console_instance.show()
        self.console_instance.handle_disable_call(1)

        # echo
        print('Output console opened.')
        print('\nComplete command:')
        print(f"ffmpeg {' '.join(cmd)}")

    def disable_ui(self, disable_call):
        if disable_call == 1:
            self.main_frame.setEnabled(False)
            # echo
            print('Main window locked.')
        else:
            self.main_frame.setEnabled(True)
            # echo
            print('\nMain window unlocked.')
