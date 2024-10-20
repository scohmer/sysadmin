@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python and try again.
    exit /b 1
)

REM Create a Python virtual environment in the current directory
echo Creating virtual environment...
python -m venv venv

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install dependencies from requirements.txt
if exist requirements.txt (
    echo Installing requirements from requirements.txt...
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Skipping dependency installation.
)

REM Create a bcrypt salt based upon the word in SALT_GEN
echo Generating bcrypt salt...
python3 generate_salt.py

REM Check if PyInstaller is installed, install if not
pip show pyinstaller >nul 2>&1
IF ERRORLEVEL 1 (
    echo PyInstaller is not installed. Installing PyInstaller...
    pip install pyinstaller
)

REM Create the executable using PyInstaller
echo Creating the executable...
pyinstaller --onefile --windowed maintenance_logger.py

REM Clean up PyInstaller build files
echo Cleaning up build files...
rmdir /S /Q build
rmdir /S /Q __pycache__
del /Q *.spec

REM Deactivate the virtual environment
echo Deactivating virtual environment...
deactivate

REM Cleanup the virtual environment folder (optional)
echo Cleaning up virtual environment...
rmdir /S /Q venv

echo Installation and setup complete. Executable is located in the dist folder.
