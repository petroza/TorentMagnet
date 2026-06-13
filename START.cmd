@echo off
setlocal
cd /d "%~dp0"
title TorrentMagnet

echo ============================================================
echo   TorrentMagnet - spoustim aplikaci
echo ============================================================
echo.

REM --- najdi Python ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo CHYBA: Python nebyl nalezen.
  echo Nainstaluj Python 3.9 az 3.12 z https://www.python.org/downloads/
  echo Pri instalaci ZASKRTNI "Add python.exe to PATH".
  echo.
  pause
  exit /b 1
)

REM --- vytvor izolovane prostredi (.venv) pokud chybi ---
if not exist ".venv\Scripts\python.exe" (
  echo Pripravuji izolovane prostredi ... pockej chvili.
  %PY% -m venv ".venv"
  if errorlevel 1 (
    echo CHYBA: nepodarilo se vytvorit prostredi .venv
    pause
    exit /b 1
  )
)

set "VPY=.venv\Scripts\python.exe"

REM --- pokud je .venv rozbity (napr. po presunu slozky), vytvor ho znovu ---
"%VPY%" -c "import sys" 2>nul
if errorlevel 1 (
  echo Prostredi .venv je nefunkcni, vytvarim ho znovu ...
  rmdir /s /q ".venv"
  %PY% -m venv ".venv"
  if errorlevel 1 (
    echo CHYBA: nepodarilo se vytvorit prostredi .venv
    pause
    exit /b 1
  )
)

REM --- zkontroluj a pripadne nainstaluj torrent engine libtorrent ---
"%VPY%" -c "import libtorrent" 2>nul
if errorlevel 1 (
  echo.
  echo Instaluji torrent engine libtorrent ...
  echo  ^(jen pri prvnim spusteni, muze to chvili trvat^)
  echo.
  "%VPY%" -m pip install --upgrade pip
  "%VPY%" -m pip install libtorrent
)

"%VPY%" -c "import libtorrent" 2>nul
if errorlevel 1 (
  echo.
  echo CHYBA: torrent engine libtorrent se nepodarilo nainstalovat.
  echo Zkontroluj pripojeni k internetu a spust START.cmd znovu.
  echo.
  pause
  exit /b 1
)

echo.
echo Vse pripraveno. Spoustim aplikaci a otviram prohlizec.
echo Aplikaci ukoncis zavrenim tohoto okna nebo klavesami Ctrl+C.
echo.

"%VPY%" "app\server.py"

echo.
echo Aplikace byla ukoncena.
pause
