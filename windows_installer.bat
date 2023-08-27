@echo off
setlocal enabledelayedexpansion

REM Check if the first argument is provided
echo.
if "%~1" == "" (
    set "python_path=python"
) else (
    set "python_path=%~1"
)

REM Check if the specified directory exists
if "!python_path!" neq "python" (
    if not exist "!python_path!" (
        echo ERROR: The path "!python_path!" does not exist.
        echo.
		pause
		exit /b 1
    )
)

REM Capture and echo the Python version
for /f "tokens=*" %%i in ('!python_path! --version 2^>^&1') do (
    set python_version=%%i
)

REM Check if the python version is correct
if "!python_version:~0,6!"=="Python" (
	set "version=!python_version:~7,1!"
	set release=
	for /f "tokens=2 delims=." %%a in ("!python_version!") do (
		set release=%%a
	)
	if "!version!" lss "3" (
		echo ERROR: Python version provided "!python_version!" is not compatible
			echo.
			pause
			exit /b 1
	) else (
		if "!release!" lss "11" (
			echo ERROR: Python release provided "!python_version! < Python 3.11.*"  is not compatible
			echo.
			pause
			exit /b 1
		) else (
			echo INFO: Correct version of Python found "!python_version!"
		)
	)
) else (
	if "!python_path!" == "python" (
		echo ERROR: Could not open the Python3.11 interpreter from the system path
		echo        please provide the full path to this script as a parameter or
		echo        set Python3.11.exe to "python" in the system environment variables
	) else (
		echo ERROR: Could not open the Python3.11 executable provided "!python_path!"
		echo        as a Python3.11 interpreter; please check if the path is correct.
    )
	echo.
	pause
	exit /b 1
)

REM Variables
set "directory=%CD%"
set "app_root=%directory%\SnakeAI"
set "env_dir=%app_root%\env"
set "launcher=%app_root%\launcher.vbs"
set "config_dir=%app_root%\config"
set "config_file=%config_dir%\setup_init.bat"


REM Create python environment and install snakeAI package
echo INFO: Creating Python environment:
echo.
mkdir "!env_dir!"
!python_path! -m venv "!env_dir!"
call "!env_dir!\Scripts\activate"
pip install "!directory!\dist\snakeAI-0.0.1-py3-none-any.whl"
echo.
echo INFO: Python environment created

REM Create a launching script
echo INFO: Creating setup_init
mkdir "!config_dir!"
echo @echo off > "!config_file!"
echo call "!env_dir!\Scripts\activate" >> "!config_file!"
echo python -m snake_ai.main >> "!config_file!"
echo INFO: Setup_init created

REM Create launcher that avoids prompt displaying
echo INFO: creating launcher
echo Set WshShell = CreateObject("WScript.Shell") > "!launcher!"
echo WshShell.Run "!config_dir!\setup_init.bat", 0, False >> "!launcher!"
echo Set WshShell = Nothing >> "!launcher!"
echo INFO: Launcher created
echo.
echo INFO: Installation completed under the folder ./SnakeAI, please close this window
echo       and execute "./SnakeAI/launcher.vbs" to start
echo.
pause