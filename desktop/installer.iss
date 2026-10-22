; Inno Setup script for PROWEB HR (built by desktop/build.ps1).
; Per-user install: no administrator rights needed.
; User data stays in %LOCALAPPDATA%\ProwebHR and survives updates/uninstall.

#define AppName "PROWEB HR"
#define AppVersion "2.1.0"
#define AppExe "ProwebHR.exe"

[Setup]
AppId={{E4E417E6-9DCF-47FC-801F-A8974C306550}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=PROWEB
DefaultDirName={localappdata}\Programs\ProwebHR
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=ProwebHR-Setup-{#AppVersion}
SetupIconFile=prowebhr.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\ProwebHR\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\{#AppName} - ma'lumotlar papkasi"; Filename: "{localappdata}\ProwebHR"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent
