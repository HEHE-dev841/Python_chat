@echo off
setlocal

rem Set paths
set "PYTHON_PATH=C:\path\to\your\python\python.exe"
set "SCRIPT_PATH=C:\path\to\your\script\chat_application.py"
set "VLC_PATH=C:\Program Files\VideoLAN\VLC\vlc.exe"

rem Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python from https://www.python.org/downloads/
    exit /b
)

rem Check if VLC is installed
if not exist "%VLC_PATH%" (
    echo VLC Media Player is not installed. Please install VLC from https://www.videolan.org/vlc/
    exit /b
)

rem Install required Python packages
echo Installing required Python packages...
pip install python-vlc

rem Run the Python script
echo Running the chat application...
"%PYTHON_PATH%" "%SCRIPT_PATH%"

pause
endlocal
