; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Object Creator"
#define MyAppVersion "0.1.10"
#define MyAppPublisher "Daniel Meinert (Tolsimir)"
#define MyAppURL "https://github.com/danielmeinert/objectcreator"
#define MyAppExeName "Object Creator.exe"
#define MyAppAssocName "OpenRCT2 Object File"
#define MyAppAssocExt ".parkobj"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt
#define MyAppAssocExt2 ".DAT"
#define MyAppAssocKey2 StringChange(MyAppAssocName, " ", "") + MyAppAssocExt2
#define License ExtractFilePath(ExtractFilePath(SourcePath)) + "\licence.txt"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{E83D2150-E472-4DFC-A76E-B93F6A876373}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile={#License}
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#SourcePath}\output\installer
OutputBaseFilename=ObjectCreatorInstaller-windows-v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "mypAssociation"; Description: "{cm:AssocFileExtension,{#MyAppName},{#MyAppAssocExt}}"; GroupDescription: "File Associations"; Flags: unchecked
Name: "mypAssociation2"; Description: "{cm:AssocFileExtension,{#MyAppName},{#MyAppAssocExt2}}"; GroupDescription: "File Associations"; Flags: unchecked


[Files]
Source: "{#SourcePath}\output\Object Creator\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#SourcePath}\output\Object Creator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: mypAssociation
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey; Tasks: mypAssociation
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: mypAssociation
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: mypAssociation
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Tasks: mypAssociation

Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt2}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey2}"; ValueData: ""; Flags: uninsdeletevalue; Tasks: mypAssociation2
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey2}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey; Tasks: mypAssociation2
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey2}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: mypAssociation2
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey2}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: mypAssociation2
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: "{#MyAppAssocKey2}"; ValueData: ""; Tasks: mypAssociation2


[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall 

