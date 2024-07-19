import os
import configparser as cp

from PyQt5 import QtWidgets as qtw


def save_preset(value_dict):
    d = value_dict

    # echo
    print('\nSelecting a preset location...')

    save_file, _ = qtw.QFileDialog.getSaveFileName(None, 'Save a Prest File',
                                                   os.path.expanduser(r'~\Documents'),
                                                   "Preset *.ini")

    if save_file:
        # echo
        print(f'Saving preset to "{save_file}" ...')

        config = cp.ConfigParser()
        config['PLUSCODER'] = {}
        config['PLUSCODER']['version'] = str(1)
        config['VIDEO'] = {}
        video = config['VIDEO']
        video['vcodec'] = str(d['vcodec'])
        video['vcodec_custom'] = d['vcodec_custom']
        video['vcodec_param'] = d['vcodec_param']
        video['v_res'] = str(d['v_res'])
        video['v_res_custom'] = str(d['v_res_custom'])
        video['v_fps'] = str(d['v_fps'])
        video['v_custom'] = str(d['v_custom'])
        video['yuv420'] = str(d['yuv420'])
        video['faststart'] = str(d['faststart'])

        config['AUDIO'] = {}
        audio = config['AUDIO']
        audio['acodec'] = str(d['acodec'])
        audio['acodec_custom'] = str(d['acodec_custom'])
        audio['acodec_param'] = str(d['acodec_param'])
        audio['a_sample'] = str(d['a_sample'])
        audio['a_custom'] = str(d['a_custom'])

        config['OUTPUT'] = {}
        output = config['OUTPUT']
        output['o_ext'] = str(d['o_ext'])
        output['o_ext_custom'] = str(d['o_ext_custom'])
        output['o_vn'] = str(d['o_vn'])
        output['o_an'] = str(d['o_an'])

        with open(save_file, 'w') as configfile:
            config.write(configfile)

        # echo
        print(f'\nPreset saved.')

        # info box
        msg_box = qtw.QMessageBox()
        msg_box.setWindowTitle(' ')
        msg_box.setText('Preset saved.')
        msg_box.setIcon(qtw.QMessageBox.Information)
        msg_box.exec()
    else:
        print('\nSaving preset canceled.')


def load_preset():
    # echo
    print('\nSelecting a preset file...')

    open_file, _ = qtw.QFileDialog.getOpenFileName(None, "Open a Preset File",
                                                   os.path.expanduser(r'~\Documents'),
                                                   "Preset *.ini")

    # checks if user didn't cancel the file input
    while open_file != '':
        # echo
        print(f'Checking the preset file "{open_file}" ...')
        config = cp.ConfigParser()
        # checks if the ini file has a header
        try:
            config.read(open_file)
        except cp.MissingSectionHeaderError:
            print('\nInvalid preset file.')
            msg_box = qtw.QMessageBox()
            msg_box.setWindowTitle(' ')
            msg_box.setText('Invalid preset file.')
            msg_box.setIcon(qtw.QMessageBox.Warning)
            msg_box.exec()
            break

        # checks if the ini file has been created by the program and if the version is compatible
        if 'PLUSCODER' in config.sections():
            if config['PLUSCODER'].getint('version') == 1:
                print('\nPreset file valid.')
                return config
            else:
                print('\nPreset file version incompatible.')
                msg_box = qtw.QMessageBox()
                msg_box.setWindowTitle(' ')
                msg_box.setText('Preset file version incompatible.')
                msg_box.setIcon(qtw.QMessageBox.Warning)
                msg_box.exec()
                break
        else:
            msg_box = qtw.QMessageBox()
            msg_box.setWindowTitle(' ')
            msg_box.setText('Invalid preset file.')
            msg_box.setIcon(qtw.QMessageBox.Warning)
            msg_box.exec()
            print('\nInvalid preset file.')
            break
