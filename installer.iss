#define MyAppName "ARJSOFT HEIC Converter"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ARJSOFT"
#define MyAppExeName "ARJSOFT-HEIC-Converter.exe"

[Setup]
AppId={{A9B54F10-2E6D-4A3D-9D31-A9A1E1C10001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\ARJSOFT\ARJSOFT HEIC Converter
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=ARJSOFT-HEIC-Converter-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\\arjsoft-icon.ico
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayName={#MyAppName}

[Files]
Source: "dist\ARJSOFT-HEIC-Converter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\arjsoft-icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\arjsoft-icon.ico"; IconIndex: 0
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\assets\arjsoft-icon.ico"; IconIndex: 0
