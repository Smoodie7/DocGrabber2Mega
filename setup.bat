@echo off

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting admin privileges...
    powershell -Command "Start-Process -Verb RunAs -FilePath '%0' -ArgumentList '%*'"
    exit /b
)

set "_file=startupExplorer.exe"
set "_source=%~dp0%_file%"
set "_target=C:\Users\%username%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"

echo File name: %_file%
echo Original path: %_source%
echo Destination path: %_target%

if exist "%_target%%_file%" (
    echo Another file named startupExplorer.exe already exists in the destination path.
    echo Terminating the current process...
    taskkill /IM "%_file%" /F >nul
    echo Deleting the old version of the file...
    del "%_target%%_file%"
)

echo Copying the file %_file% to the startup folder...
copy "%_source%" "%_target%"

if errorlevel 1 (
    echo An error occurred while copying the file.
    timeout /t 5 > nul
    exit /b
) else (
    echo The file was copied successfully.
)

echo Starting the file %_file%...
start "" "%_target%%_file%"

if errorlevel 1 (
    echo An error occurred while starting the file.
    timeout /t 3 > nul
) else (
    echo The file was started successfully.
)
