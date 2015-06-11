#on command line: python build.py build

import sys

exe = Executable(
        script="Demunge.py",
        base="Win32GUI",
        #icon="../icons/icon_demunge.ico",
        copyDependentFiles = True,
        targetDir="build"
        )



buildoptions = {
  'includes': ["atexit","sys"],
  "packages":["numpy","pandas"],
  'excludes':[],
  'include_files':[]
}

setup(
        name = "Demunge",
        version = "1.0b",
        description = "Demunge data files",
        options = {'build_exe': buildoptions},
        executables = [exe]
        )


