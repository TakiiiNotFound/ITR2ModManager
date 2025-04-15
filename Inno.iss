; ITR2ModManagerInstaller.iss
; This script installs ITR2ModManager and its media files to %appdata%\ITR2ModManager.
; It first checks if a folder named "Fomod" exists in that folder and, if so, clears out all content.
; Finally, it creates Start Menu and Desktop shortcuts for ITR2ModManager.exe.

[Setup]
AppName=ITR2ModManager
AppVersion=1.0
; Set the default installation directory to %appdata%\ITR2ModManager
DefaultDirName={userappdata}\ITR2ModManager
; The name of the Start Menu folder
DefaultGroupName=ITR2ModManager
OutputBaseFilename=ITR2ModManagerSetup
Compression=lzma
SolidCompression=yes

[Files]
; Install the main executable.
Source: "C:\source\ITR2ModManager.exe"; DestDir: "{userappdata}\ITR2ModManager"; DestName: "ITR2ModManager.exe"; Flags: ignoreversion
; Install banner and icon files into a Media subfolder.
Source: "C:\source\Media\banner.png"; DestDir: "{userappdata}\ITR2ModManager\Media"; Flags: ignoreversion
Source: "C:\source\Media\icon.ico"; DestDir: "{userappdata}\ITR2ModManager\Media"; Flags: ignoreversion

[Icons]
; Create a Start Menu shortcut.
Name: "{group}\ITR2ModManager"; Filename: "{userappdata}\ITR2ModManager\ITR2ModManager.exe"
; Create a Desktop shortcut.
Name: "{userdesktop}\ITR2ModManager"; Filename: "{userappdata}\ITR2ModManager\ITR2ModManager.exe"

[Code]
{*
  ClearDirectoryContents
  ----------------------
  This procedure deletes all files and subdirectories under the specified directory (Dir),
  without deleting the directory itself.

  It enumerates each item. For files, it calls DeleteFile, and for directories, it
  first calls itself recursively to delete all contents, then removes the directory via RemoveDir.
*}
procedure ClearDirectoryContents(const Dir: string);
var
  FindRec: TFindRec;
  FullPath: string;
begin
  if FindFirst(Dir + '\*', FindRec) then
  begin
    try
      repeat
        if (FindRec.Name <> '.') and (FindRec.Name <> '..') then
        begin
          FullPath := Dir + '\' + FindRec.Name;
          if (FindRec.Attributes and FILE_ATTRIBUTE_DIRECTORY) <> 0 then
          begin
            { Recursively clear the contents of the subdirectory }
            ClearDirectoryContents(FullPath);
            { Remove the (now empty) directory }
            if not RemoveDir(FullPath) then
              MsgBox('Error deleting directory: ' + FullPath, mbError, MB_OK);
          end else
          begin
            if not DeleteFile(FullPath) then
              MsgBox('Error deleting file: ' + FullPath, mbError, MB_OK);
          end;
        end;
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

{*
  ClearAppDataDir
  ---------------
  This procedure checks if the folder %appdata%\ITR2ModManager\Fomod exists.
  If it exists, it calls ClearDirectoryContents on the entire %appdata%\ITR2ModManager folder.
*}
procedure ClearAppDataDir;
var
  AppDataDir: string;
begin
  AppDataDir := ExpandConstant('{userappdata}\ITR2ModManager');
  if DirExists(AppDataDir + '\Fomod') then
  begin
    ClearDirectoryContents(AppDataDir);
  end;
end;

{*
  CurStepChanged
  --------------
  This event function is called as the install process changes steps.
  When the current step is ssInstall (immediately before files are installed),
  the script calls ClearAppDataDir to clear out the destination folder if needed.
*}
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then 
  begin
    ClearAppDataDir;
  end;
end;
