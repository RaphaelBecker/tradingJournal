@ECHO off &setlocal

python --version 2>&1 | findstr "3.7 3.8 3.9"
IF NOT ERRORLEVEL 0 (
	ECHO Error: Please make sure you have Python 3.7, 3.8 or 3.9 in PATH
) ELSE (
	IF NOT EXIST ".\venv\" (
		ECHO Creating virtual environment...
		python -m venv venv
		ECHO Creation OK
	)
	ECHO Installing packages
	CALL venv\Scripts\activate.bat
	python -m pip install --upgrade pip setuptools wheel
	python -m pip install -r requirements.txt
	ECHO Installation OK
)
PAUSE
GOTO :eof

:HInput [ByRef_VarName]
:: inspired by Carlos @ www.DosTips.com
if "%__HI__%" neq "__HI__" (
  setlocal DisableDelayedExpansion
  set "S=" &set "N=0" &set "__HI__=__HI__"
  for /f %%i in ('"prompt;$h&for %%i in (1) do rem"') do set "BS=%%i"
)
set "C="
for /f "delims=" %%i in ('2^>nul xcopy /lw "%~f0" "%~f0"') do if not defined C set "C=%%i"
set "C=%C:~-1%"
setlocal EnableDelayedExpansion
if not defined C (
  echo(
  if "%~1"=="" (
    echo(!S!
    endlocal &endlocal &exit /b %N%
  ) else (
    if defined S (
      for /f delims^=^ eol^= %%i in ("!S!") do endlocal &endlocal &set "%~1=%%i" &exit /b %N%
    ) else endlocal &endlocal &set "%~1=" &exit /b 0
  )
)
if "!BS!"=="!C!" (
  set "C="
  if defined S set /a "N -= 1" &set "S=!S:~,-1!" &<nul set /p "=%BS% %BS%"
) else set /a "N += 1" &<nul set /p "=*"
if not defined S (
  endlocal &set "N=%N%" &set "S=%C%"
) else for /f delims^=^ eol^= %%i in ("!S!") do endlocal &set "N=%N%" &set "S=%%i%C%"
goto HInput
