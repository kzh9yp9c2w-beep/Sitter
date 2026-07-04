@echo off
:: 1. Launch Sitter invisibly using the pythonw engine
start "" pythonw "%~dp0desktop_sitter.py"

:: 2. Dynamically locate your REAL desktop path
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop') do set "REAL_DESKTOP=%%b"
call set "FINAL_DESKTOP=%REAL_DESKTOP%"

:: 3. Wipe any glitched old shortcuts to clear the path
if exist "%FINAL_DESKTOP%\Sitter.lnk" del "%FINAL_DESKTOP%\Sitter.lnk"

:: 4. Write the bulletproof shortcut configuration with precise nesting quotes
echo set WshShell = CreateObject("WScript.Shell") > "%temp%\sitter_make.vbs"
echo set oShellLink = WshShell.CreateShortcut("%FINAL_DESKTOP%\Sitter.lnk") >> "%temp%\sitter_make.vbs"
echo oShellLink.TargetPath = "pythonw.exe" >> "%temp%\sitter_make.vbs"
echo oShellLink.Arguments = """%~dp0desktop_sitter.py""" >> "%temp%\sitter_make.vbs"
echo oShellLink.WorkingDirectory = "%~dp0" >> "%temp%\sitter_make.vbs"
echo oShellLink.IconLocation = "%~dp0sitter_icon.ico,0" >> "%temp%\sitter_make.vbs"
echo oShellLink.Save >> "%temp%\sitter_make.vbs"

:: 5. Execute and cleanup
cscript //nologo "%temp%\sitter_make.vbs"
del "%temp%\sitter_make.vbs"
exit