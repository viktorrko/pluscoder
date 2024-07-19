# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['run.py'],
             pathex=[],
             binaries=[
                ('pluscoder/ffmpeg/ffmpeg.exe', 'ffmpeg'),
                ('pluscoder/ffmpeg/ffprobe.exe', 'ffmpeg')
             ],
             datas=[
                ('pluscoder/resources.py', '.'),
                ('pluscoder/ui/*.ui', 'ui')
             ],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='pluscoder',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon='icon.ico',
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='pluscoder')
