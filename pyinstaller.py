import PyInstaller.__main__

PyInstaller.__main__.run([
    'main.py', # python file where code is
    '--windowed',
    '--noconsole',
    '--icon=tape.icns' # locations of icon
])