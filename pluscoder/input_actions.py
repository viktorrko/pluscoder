import os
import subprocess
import tempfile as tf

from PyQt5 import QtGui as qtg
from pymediainfo import MediaInfo

ffmpeg = './ffmpeg/ffmpeg.exe'
ffprobe = './ffmpeg/ffprobe.exe'

class input_actions:
    def __init__(self):
        super(input_actions, self).__init__()

        self.i_parameters = []
        self.i_parameters_g = []
        self.i_parameters_v = []
        self.i_parameters_a = []

    def input_validation(self, file):
        # CHECKS IF FFPROBE CAN HANDLE THE FILE
        bad_ext = ('.jpg', '.jpeg', '.jfif', '.png', '.tif', '.tiff', '.bmp', '.gif', '.eps', '.raw', '.dng', '.cr2',
                   '.wav', '.mp3', '.flac',
                   '.svg')
        input_check = subprocess.run(f'{ffprobe} -hide_banner "{file}"', stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        filename = os.path.split(file)

        if os.path.splitext(filename[1])[1] not in bad_ext and input_check.returncode == 0:
            return 0
        else:
            return 1

    def input_parameters(self, file):
        # PARSE FFPROBE DATA
        self.i_parameters = MediaInfo.parse(file)

        return self.i_parameters

    def input_thumbnail(self, file, frame_count, frame_rate):
        # CREATES THE THUMBNAIL AND STORES IT IN THE DEFAULT TEMP FOLDER OF THE OS

        if self.i_parameters.video_tracks:
            # creates a temporary folder
            thumb_dir = tf.TemporaryDirectory(prefix='pluscoder-', dir=tf.gettempdir())
            thumb_path = thumb_dir.name + r'\thumb.jpg'

            # calculates time
            thumbnail_time = (float(frame_count) * 0.25) / float(frame_rate)
            # print(round(thumbnail_time, 2))

            # runs ffmpeg to extract 1 frame and saves it to the temp folder
            subprocess.run(
                f'{ffmpeg} -hide_banner -ss {thumbnail_time} '
                f'-i "{file}" -vframes 1 '
                f'-vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1" '
                f'"{thumb_path}"', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # feeds the frame into the GUI and purges the temp dir
            thumb_pixmap = qtg.QPixmap(thumb_path)
            self.i_preview.setPixmap(thumb_pixmap)
            thumb_dir.cleanup()
