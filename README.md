# **pluscoder**
<img src="https://github.com/user-attachments/assets/27e399e1-2ed8-4584-8b43-a2790cef1dc4" alt="logo" width="200"/> 

Yet another FFmpeg front-end, written in Python, with focus on the essentials.

### Note
> **This was one of my first bigger Python projects, It's in a working state, but it's a mess and could use a complete rewrite, so this serves as a more of an archive.**

### Running the app
+ Create a new virtual enviroment and run `pip install -r requirements.txt` to install dependecies.
+ Download FFmpeg binaries and put them in `\pluscoder\ffmpeg\`.
+ Make sure your working directory is in `\pluscoder\`.
+ Run `python ..\run.py`

Alternatively you can download binaries from releases but they only work on Windows 10. I also included a .spec file that I used to pack the binaries with pyinstaller if you want to do it yourself.

**To make sure everything works properly you will also need to install LAVFilters. You can get them [here](https://github.com/Nevcairiel/LAVFilters/releases).** You don't need to do this if you have the K-Lite Codec pack installed for example.

### Presets
You can save and load presets using the two lower button on the right panel. This saves Video, Audio and Ouput (except name and destination folder) panels settings into an .ini file.

### Screenshot of the main window
![Screenshot_2024-07-17_17-24-52](https://github.com/user-attachments/assets/fedc37d8-d325-43cb-ba62-e622ec30ff78)



