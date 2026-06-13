#!/bin/bash
# TorrentMagnet - spouštěč pro macOS / Linux
cd "$(dirname "$0")"
echo "============================================================"
echo "  TorrentMagnet - spoustim aplikaci (macOS)"
echo "============================================================"
echo

# --- najdi Python 3 ---
PY=""
if command -v python3 >/dev/null 2>&1; then PY="python3"; fi
if [ -z "$PY" ] && command -v python >/dev/null 2>&1; then PY="python"; fi
if [ -z "$PY" ]; then
  echo "CHYBA: Python 3 nebyl nalezen."
  echo "Nainstaluj ho z https://www.python.org/downloads/  nebo prikazem:  brew install python"
  echo
  read -r -p "Stiskni Enter pro zavreni..."
  exit 1
fi

# --- vytvor izolovane prostredi (.venv) pokud chybi ---
if [ ! -x ".venv/bin/python" ]; then
  echo "Pripravuji izolovane prostredi ... pockej chvili."
  "$PY" -m venv ".venv" || { echo "CHYBA: nepodarilo se vytvorit .venv"; read -r -p "Enter..."; exit 1; }
fi
VPY=".venv/bin/python"

# --- pokud je .venv rozbity (napr. po presunu), vytvor ho znovu ---
if ! "$VPY" -c "import sys" >/dev/null 2>&1; then
  echo "Prostredi .venv je nefunkcni, vytvarim ho znovu ..."
  rm -rf ".venv"
  "$PY" -m venv ".venv" || { echo "CHYBA: nepodarilo se vytvorit .venv"; read -r -p "Enter..."; exit 1; }
fi

# --- nainstaluj torrent engine libtorrent (jen poprve) ---
if ! "$VPY" -c "import libtorrent" >/dev/null 2>&1; then
  echo
  echo "Instaluji torrent engine libtorrent ... (jen pri prvnim spusteni, potreba internet)"
  echo
  "$VPY" -m pip install --upgrade pip
  "$VPY" -m pip install libtorrent
fi
if ! "$VPY" -c "import libtorrent" >/dev/null 2>&1; then
  echo
  echo "CHYBA: torrent engine libtorrent se nepodarilo nainstalovat."
  echo "Zkontroluj internet a spust START.command znovu."
  echo "(Pripadne: '$VPY' -m pip install libtorrent)"
  echo
  read -r -p "Stiskni Enter pro zavreni..."
  exit 1
fi

echo
echo "Vse pripraveno. Spoustim aplikaci a otviram prohlizec."
echo "Aplikaci ukoncis zavrenim tohoto okna nebo klavesami Ctrl+C."
echo
"$VPY" "app/server.py"
echo
echo "Aplikace byla ukoncena."
read -r -p "Stiskni Enter pro zavreni..."
