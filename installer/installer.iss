; Inno Setup script for RealSense Lab Video Capture
; Compile with: ISCC.exe installer\installer.iss
; (Run from project root after PyInstaller has built dist\RealSenseCapture\)

#define AppName      "RealSense Lab Capture"
#define AppVersion   "1.0.0"
#define AppPublisher "Lab"
#define AppExeName   "RealSenseCapture.exe"
#define BuildDir     "..\dist\RealSenseCapture"

[Setup]
AppId={{A3F2B8C1-4D7E-4F2A-9B3C-8E1D5F6A2C4B}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=..\installer\output
OutputBaseFilename=RealSenseCapture_Setup_v{#AppVersion}
SetupIconFile=..\assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
; Create uninstaller
Uninstallable=yes
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon";   Description: "Create a &desktop shortcut";   GroupDescription: "Additional icons:"; Flags: checked
Name: "startmenuicon"; Description: "Create a &Start Menu shortcut"; GroupDescription: "Additional icons:"; Flags: checked

[Files]
; The entire PyInstaller output folder
Source: "{#BuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#AppName}";       Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}"; Filename: "{uninstallexe}"

; Desktop shortcut (only if task selected)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
; Offer to launch immediately after install
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up the database and logs when uninstalling (optional — comment out to keep data)
; Type: filesandordirs; Name: "{app}\data"
; Type: filesandordirs; Name: "{app}\logs"
