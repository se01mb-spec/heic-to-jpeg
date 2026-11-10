#define MyAppName "ARJSOFT HEIC Converter"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ARJSOFT"
#define MyAppExeName "ARJSOFT-HEIC-Converter.exe"

[Setup]
AppId={{A9B54F10-2E6D-4A3D-9D31-ARJHEIC10001}
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
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayName={#MyAppName}

[Files]
Source: "dist\ARJSOFT-HEIC-Converter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"
