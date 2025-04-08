; ------------------------------------------------------------------------------
; ITR2 Mod Manager Installer Script
; This script installs the complete Fomod and temp folders, ITR2ModManager.exe, and ITR2MM.ico 
; into %appdata%\ITR2ModManager, and creates shortcuts with the custom icon.
; ------------------------------------------------------------------------------

[Setup]
AppName=ITR2 Mod Manager
AppVersion=1.0
DefaultDirName={userappdata}\ITR2ModManager
DefaultGroupName=ITR2 Mod Manager
OutputBaseFilename=ITR2ModManager_Installer
Compression=lzma
SolidCompression=yes

[Files]
; Copy all files and folders under C:\source\Fomod (including subdirectories)
Source: "C:\source\Fomod\*"; DestDir: "{app}\Fomod"; Flags: recursesubdirs createallsubdirs

; Copy all files and folders under C:\source\temp (including subdirectories)
Source: "C:\source\temp"; DestDir: "{app}\temp"; Flags: recursesubdirs createallsubdirs

; Copy the main executable to the installation folder
Source: "C:\source\ITR2ModManager.exe"; DestDir: "{app}"; Flags: ignoreversion

; Copy the icon file for shortcut customizations
Source: "C:\source\ITR2MM.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create a Start Menu shortcut with the custom icon
Name: "{group}\ITR2 Mod Manager"; Filename: "{app}\ITR2ModManager.exe"; IconFilename: "{app}\ITR2MM.ico"; WorkingDir: "{app}"

; Create a Desktop shortcut with the custom icon
Name: "{userdesktop}\ITR2 Mod Manager"; Filename: "{app}\ITR2ModManager.exe"; IconFilename: "{app}\ITR2MM.ico"; WorkingDir: "{app}"

[Run]
; Optionally, launch the application after installation.
Filename: "{app}\ITR2ModManager.exe"; Description: "Launch ITR2 Mod Manager"; Flags: nowait postinstall skipifsilent
