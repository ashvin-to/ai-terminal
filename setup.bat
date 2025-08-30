@echo off
setlocal enabledelayedexpansion

echo 🚀 Setting up AI Terminal Assistant for Windows...
echo.

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.8 or later from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Check if pip is installed
where pip >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ pip is not found. Please ensure Python installation includes pip.
    pause
    exit /b 1
)

:: Check if Git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Git is not installed.
    echo Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

:: Create and activate virtual environment
echo Creating Python virtual environment...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to create virtual environment.
    pause
    exit /b 1
)

call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install requirements
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies.
    pause
    exit /b 1
)

:: Create config directory
mkdir "%APPDATA%\ai_terminal" 2>nul

:: Get API key
set /p API_KEY=🔑 Enter your OpenRouter API key (get it from https://openrouter.ai/keys): 
if "!API_KEY!"=="" (
    echo ❌ No API key provided. Setup incomplete.
    pause
    exit /b 1
)

:: Save API key
echo OPENROUTER_API_KEY=!API_KEY!> "%APPDATA%\ai_terminal\.env"

:: Create batch file in user's PATH
echo Creating launcher...
mkdir "%USERPROFILE%\bin" 2>nul

echo @echo off > "%USERPROFILE%\bin\ai.bat"
echo setlocal enabledelayedexpansion >> "%USERPROFILE%\bin\ai.bat"
echo set "SCRIPT_DIR=%~dp0\..\ai-terminal" >> "%USERPROFILE%\bin\ai.bat"
echo if not exist "!SCRIPT_DIR!\venv\Scripts\activate.bat" ( >> "%USERPROFILE%\bin\ai.bat"
echo     echo AI Terminal is not installed in the expected location. >> "%USERPROFILE%\bin\ai.bat"
echo     echo Please run setup.bat from the ai-terminal directory. >> "%USERPROFILE%\bin\ai.bat"
echo     pause >> "%USERPROFILE%\bin\ai.bat"
echo     exit /b 1 >> "%USERPROFILE%\bin\ai.bat"
echo ) >> "%USERPROFILE%\bin\ai.bat"
echo call "!SCRIPT_DIR!\venv\Scripts\activate.bat" >> "%USERPROFILE%\bin\ai.bat"
echo python "!SCRIPT_DIR!\ai.py" %%* >> "%USERPROFILE%\bin\ai.bat"

:: Add to PATH if not already present
setx PATH "%PATH%;%USERPROFILE%\bin" >nul 2>&1

echo.
echo ✅ Setup complete!
echo.
echo You can now use the AI Terminal Assistant by typing:
echo    ai "your question here"
echo or just 'ai' for interactive mode.
echo.
echo Please restart your terminal for the changes to take effect.
pause
