; PS  Installer Script
; Created with NSIS

!include "MUI2.nsh"

; General
Name "PS "
OutFile "PSSetup.exe"
InstallDir "$PROGRAMFILES\PS "
InstallDirRegKey HKCU "Software\PS " ""

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "PS Gamers.png"
!define MUI_UNICON "PS Gamers.png"
!define MUI_WELCOMEFINISHPAGE_BITMAP "PS Gamers.png"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "PS Gamers.png"
!define MUI_HEADERIMAGE_RIGHT

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Add files
  File "dist\PS .exe"
  File "PS Gamers.png"
  
  ; Create QR codes directory
  CreateDirectory "$INSTDIR\qr_codes"
  
  ; Create Start Menu shortcut
  CreateDirectory "$SMPROGRAMS\PS "
  CreateShortCut "$SMPROGRAMS\PS \PS .lnk" "$INSTDIR\PS .exe" "" "$INSTDIR\PS Gamers.png"
  CreateShortCut "$SMPROGRAMS\PS \Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Create Desktop shortcut
  CreateShortCut "$DESKTOP\PS .lnk" "$INSTDIR\PS .exe" "" "$INSTDIR\PS Gamers.png"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
  ; Write registry keys for uninstall
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PS " "DisplayName" "PS "
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PS " "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PS " "DisplayIcon" "$INSTDIR\PS Gamers.png"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PS " "Publisher" "PS "
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PS " "DisplayVersion" "1.0.0"
SectionEnd

; Uninstaller Section
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\PS .exe"
  Delete "$INSTDIR\PS Gamers.png"
  Delete "$INSTDIR\uninstall.exe"
  
  ; Remove QR codes directory and contents
  RMDir /r "$INSTDIR\qr_codes"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\PS \PS .lnk"
  Delete "$SMPROGRAMS\PS \Uninstall.lnk"
  Delete "$DESKTOP\PS .lnk"
  
  ; Remove directories
  RMDir "$SMPROGRAMS\PS "
  RMDir "$INSTDIR"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PS "
  DeleteRegKey HKCU "Software\PS "
SectionEnd
