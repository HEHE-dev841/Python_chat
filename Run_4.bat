@echo off
echo Welcome to App Chat!
echo.

:: Get the directory of the batch script
set "script_dir=%~dp0"

:: Construct the full path to the Python script
set "python_script=%script_dir%App_chat.py"

:: Check if the Python script exists
if exist "%python_script%" (
    echo Starting App Chat...
    python "%python_script%"
) else (
    echo Error: Could not find App_chat.py in the same directory as this batch file.
    echo Expected location: %python_script%
    echo Please make sure the Python script is in the correct location.
)

echo.
echo App Chat has closed. Press any key to exit.
pause > nul