#!/usr/bin/env bash
set -euo pipefail

# Script location: application/scripts
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root"

# Create python venv in server/.venv
if [ ! -d "server/.venv" ]; then
  python -m venv server/.venv
fi

# activate and install deps
. server/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r server/requirements.txt pyinstaller

# build exe
python -m PyInstaller --onefile server/blink.py --distpath server/dist --workpath server/build --specpath server/build

# copy
mkdir -p application/src-tauri/bin
cp server/dist/blink.exe application/src-tauri/bin/blink.exe || true

echo "Python exe built and copied to src-tauri/bin/blink.exe"
