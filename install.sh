#!/usr/bin/env bash
# Unix系(OSX/Linux)向けセットアップスクリプト
set -e
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "インストール完了。GUIを起動するには:"
echo "  .venv/bin/python birthday_notifier.py"
