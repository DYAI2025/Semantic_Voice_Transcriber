; NSIS installer template for SVT Lite
!include "MUI2.nsh"

Name "SVT Lite"
OutFile "SVT-Lite-Setup.exe"
InstallDir "$PROGRAMFILES\SVT"
RequestExecutionLevel admin

Page directory
Page instfiles

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "..\..\*.*"
  ExecWait '"$INSTDIR\svt_env\Scripts\python.exe" "$INSTDIR\scripts\setup_local_stack.py" --env "$INSTDIR\.env" --overwrite-env'
  CreateShortCut "$DESKTOP\SVT.lnk" "$INSTDIR\svt_env\Scripts\python.exe" "$INSTDIR\svt.py"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\SVT.lnk"
  RMDir /r "$INSTDIR"
SectionEnd
