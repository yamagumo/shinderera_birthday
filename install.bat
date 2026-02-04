@echo off
REM Windows 用簡単セットアップ：仮想環境作成と依存インストール
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.
echo インストール完了。GUIを起動するには:
echo    .venv\Scripts\python.exe birthday_notifier.py
pause
