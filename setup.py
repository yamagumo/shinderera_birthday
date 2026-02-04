#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
誕生日通知アプリ - セットアップスクリプト
必要なライブラリをインストールします
"""

import subprocess
import sys
from pathlib import Path


def install_requirements():
    """requirements.txtから依存ライブラリをインストールする汎用インストーラ"""
    print("=" * 60)
    print("誕生日通知アプリ - セットアップ")
    print("=" * 60)
    print()

    req_file = Path(__file__).resolve().parent / "requirements.txt"
    if not req_file.exists():
        print("requirements.txt が見つかりません。手動で必要パッケージをインストールしてください。")
        return

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
        print()
        print("✅ インストール完了！")
        print()
        print("使い方:")
        print("  1. python birthday_notifier.py を実行してGUIを起動")
        print("  2. --silent オプションでバックグラウンド実行")
        print("     python birthday_notifier.py --silent")
        print()
    except subprocess.CalledProcessError as e:
        print(f"❌ インストールに失敗しました: {e}")
        print("管理者権限でコマンドプロンプトを開いて実行してください")
        sys.exit(1)


if __name__ == "__main__":
    install_requirements()
    input("Enterキーを押して終了...")
