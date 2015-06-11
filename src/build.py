#on command line: python build.py build

import sys
from cx_Freeze import setup, Executable

exe = Executable(
        script="Demunge.py",
        base="Win32GUI",
        #icon="../icons/icon_demunge.ico",
        copyDependentFiles = True,
        compress = True,
        targetDir="build",
        appendScriptToExe=True,
        appendScriptToLibrary=False        
        )



buildoptions = {
  #'includes': ["atexit","sys"],
  #"packages":["numpy","pandas"],
  'excludes':["collections.abc",                
              'lxml','bs4','email','OpenSSL','requests','sqlalchemy','zmq','multiprocessing',
              'Tkinter',
              "PySide.QtSvg","PySide.QtNetwork",
              "PyQt4.QtSql", "sqlite3",
              "libsodium"],
  'include_files':[]
}

setup(
        name = "Demunge",
        version = "1.0",
        description = "Demunge data files",
        options = {'build_exe': buildoptions},
        executables = [exe]
        )


