; Start

Name "Demunge 1"
CRCCheck On

;General

OutFile "Demunge_Setup_1_0.exe"
ShowInstDetails "nevershow"
ShowUninstDetails "nevershow"

;覧覧覧覧覧�
;Include Modern UI

!include "MUI2.nsh"
;!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\icon_facepager.ico"

;覧覧覧覧覧�
;Interface Settings

!define MUI_ABORTWARNING

;覧覧覧覧覧�
;Pages


;!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\Demunge.exe"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

;覧覧覧覧覧�
;Languages

!insertmacro MUI_LANGUAGE "English"

;覧覧覧覧覧�
;Folder selection page

InstallDir "$PROGRAMFILES\Demunge"

;覧覧覧覧覧�
;Data

;覧覧覧覧覧�
;Unistall Previous Section
; The "" makes the section hidden.
Section "" SecUninstallPrevious

    Call UninstallPrevious

SectionEnd

Function UninstallPrevious
    DetailPrint "Removing previous installation."    
    ; Run the uninstaller silently.
    ExecWait '"$INSTDIR\Uninstall.exe" /S _?=$INSTDIR'

FunctionEnd

;覧覧覧覧覧�
;Installer Sections
Section "Demunge" Install

;Add files
SetOutPath "$INSTDIR"

File "Demunge.exe"
File "library.zip"
File "*.dll"
File "*.pyd"
File /r "mpl-data"
;File /r "tcl"
;File /r "tk"

;SetOutPath "$INSTDIR\docs"
;File "docs\"

;CreateDirectory "$INSTDIR\docs"


;create desktop shortcut
CreateShortCut "$DESKTOP\Demunge.lnk" "$INSTDIR\Demunge.exe" ""

;create start-menu items
CreateDirectory "$SMPROGRAMS\Demunge"
CreateShortCut "$SMPROGRAMS\Demunge\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
CreateShortCut "$SMPROGRAMS\Demunge\Facepager.lnk" "$INSTDIR\Demunge.exe" "" "$INSTDIR\Demunge.exe" 0

;write uninstall information to the registry
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Demunge" "DisplayName" "Demunge (remove only)"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Demunge" "UninstallString" "$INSTDIR\Uninstall.exe"

WriteUninstaller "$INSTDIR\Uninstall.exe"

SectionEnd

;覧覧覧覧覧�
;Uninstaller Section
Section "Uninstall"

;Delete Files
RMDir /r "$INSTDIR\*.*"

;Remove the installation directory
RMDir "$INSTDIR"

;Delete Start Menu Shortcuts
Delete "$DESKTOP\Demunge.lnk"
Delete "$SMPROGRAMS\Demunge\*.*"
RmDir  "$SMPROGRAMS\Demunge"

;Delete Uninstaller And Unistall Registry Entries
DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Demunge"
DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Demunge"

SectionEnd
