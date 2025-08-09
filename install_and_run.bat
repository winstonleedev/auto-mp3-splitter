@echo off
echo FFmpeg-based MP3 Splitter Installation and Runner
echo ================================================
echo.

echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo FFmpeg found! ✓
    goto :run_splitter
)

echo FFmpeg not found. Attempting to install with winget...
echo.

winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: winget not found!
    echo Please install FFmpeg manually from https://ffmpeg.org/download.html
    echo Or install winget from Microsoft Store and try again.
    pause
    exit /b 1
)

echo Installing FFmpeg via winget...
winget install --id=Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements

if %errorlevel% neq 0 (
    echo.
    echo FFmpeg installation failed!
    echo Please install FFmpeg manually:
    echo 1. Download from https://ffmpeg.org/download.html
    echo 2. Extract to a folder (e.g., C:\ffmpeg)
    echo 3. Add the bin folder to your PATH environment variable
    echo 4. Restart this script
    pause
    exit /b 1
)

echo.
echo FFmpeg installed successfully! ✓
echo You may need to restart your command prompt for PATH changes to take effect.
echo.

:run_splitter
echo.
echo ================================================
echo MP3 Splitter Configuration
echo ================================================
echo.

REM Get first MP3 file in current directory
set "input_file="
if "%~1"=="" (
    echo Available MP3 files in current directory:
    echo.
    dir /b *.mp3 2>nul
    echo.
    
    REM Get first MP3 file automatically
    for %%f in (*.mp3) do (
        set "input_file=%%f"
        goto :found_first
    )
    :found_first
    
    if "%input_file%"=="" (
        echo No MP3 files found in current directory!
        pause
        exit /b 1
    )
    
    echo Using first MP3 file found: %input_file%
    echo.
) else (
    set "input_file=%~1"
    echo Using provided file: %input_file%
)

REM Get silence threshold
set "threshold=-48"
echo.
set /p threshold_input="Silence threshold in dB (default: -48, more negative = more sensitive): "
if not "%threshold_input%"=="" set "threshold=%threshold_input%"

REM Get minimum silence duration
set "duration=1.5"
echo.
set /p duration_input="Minimum silence duration in seconds (default: 1.5): "
if not "%duration_input%"=="" set "duration=%duration_input%"

REM Get output directory
set "output_dir=splits"
echo.
set /p output_input="Output directory (default: splits): "
if not "%output_input%"=="" set "output_dir=%output_input%"

echo.
echo ================================================
echo Configuration Summary:
echo ================================================
if "%input_file%"=="" (
    echo Input file: Auto-detect
) else (
    echo Input file: %input_file%
)
echo Silence threshold: %threshold% dB
echo Min silence duration: %duration% seconds
echo Output directory: %output_dir%
echo.
echo Press any key to start splitting, or Ctrl+C to cancel...
pause >nul

echo.
echo Running MP3 splitter...

REM Run the splitter with the detected MP3 file
python split_ost.py "%input_file%" -o "%output_dir%" -t %threshold% -d %duration%

echo.
echo Done! Check the '%output_dir%' folder for the split tracks.
pause