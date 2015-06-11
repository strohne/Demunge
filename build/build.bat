cd ../src
rmdir /S /Q build

python build.py build

cd build
copy Demunge.exe exe.win32-2.7
copy python27.dll exe.win32-2.7
copy ..\..\build\setupscript-version_1_0.nsi exe.win32-2.7\setupscript-version_1_0.nsi

"C:\Program Files (x86)\NSIS\makensis.exe" exe.win32-2.7\setupscript-version_1_0.nsi

copy exe.win32-2.7\Demunge_Setup_1_0.exe ..\..\build\Demunge_Setup_1_0.exe 
 
cd../../build

pause