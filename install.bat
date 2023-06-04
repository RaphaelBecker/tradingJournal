@ECHO off &setlocal

:: First check for python version 3.7, 3.8 or 3.9 in PATH
python --version 2>&1 | findstr "3.7 3.8 3.9"
IF NOT ERRORLEVEL 0 (
    ECHO Error: Please make sure you have Python 3.7, 3.8 or 3.9 in PATH
) ELSE (
    :: Now check for 64-bit version of Python
    python -c "import platform; exit(1 if platform.architecture()[0] != '64bit' else 0)"
    IF ERRORLEVEL 1 (
        ECHO Error: Please make sure you have a 64-bit version of Python in PATH
    ) ELSE (
        IF NOT EXIST ".\venv\" (
            ECHO Creating virtual environment...
            python -m venv venv
            ECHO Creation OK
        )
        ECHO Installing packages
        CALL venv\Scripts\activate.bat
        python -m pip install --upgrade pip
        python -m pip install --upgrade pip setuptools wheel
        python -m pip install -r requirements.txt
        ECHO Installation OK
    )
)

