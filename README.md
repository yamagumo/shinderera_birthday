# 誕生日通知アプリ 🎉

アイドルマスターシンデレラガールズのキャラクターの誕生日をカウントダウンし、誕生日が近づいたら通知してくれるアプリです。

## 機能

✅ **アイドル選択**: UIから好きなキャラクターを選択  
✅ **誕生日カウントダウン**: 誕生日までの日数を表示  
✅ **Windows通知**: 誕生日当日や期日前に通知  
✅ **スタートアップ登録**: PC起動時に自動実行  
✅ **バックグラウンド動作**: 常時監視で見落とさない  

## インストール方法（どの環境からでも再現できるように）

このリポジトリは Python で動作します。共通の手順は仮想環境（venv）を作成し、`requirements.txt` を使って依存をインストールすることです。

### Windows (推奨)

1. リポジトリをクローンまたは ZIP を展開
2. プロジェクトルートで `install.bat` をダブルクリックまたは実行

`install.bat` は以下を自動で行います：
- `.venv` 仮想環境作成
- 仮想環境を有効化して `requirements.txt` をインストール

手動で行う場合（PowerShell や cmd）:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

GUI を起動するには:

```powershell
.\.venv\Scripts\python.exe birthday_notifier.py
```

サイレント（バックグラウンド）実行:

```powershell
.\.venv\Scripts\python.exe birthday_notifier.py --silent
```

### macOS / Linux

1. ターミナルでプロジェクトルートへ移動
2. `install.sh` を実行（または手動コマンド）

```bash
./install.sh
# または手動
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

起動:

```bash
.venv/bin/python birthday_notifier.py
```

注意: Windows のトースト通知（`win10toast` や Windows API）は Windows 専用です。macOS/Linux では GUI ダイアログや他の通知手段にフォールバックします。

## 使い方

### 初回起動時
1. アプリが起動し、設定ウィンドウが表示されます
2. 通知対象のキャラクターをチェックボックスで選択
3. 「保存」ボタンで設定を保存

### 通常起動時
1. 選択したキャラクターの誕生日カウントダウンが表示されます
2. 「⚙️ アイドルを選択」で選択内容を変更
3. 「🔔 通知確認」で手動で通知を確認

### スタートアップ登録
1. 「💾 スタートアップに登録」ボタンをクリック
2. PC起動時に自動的にアプリが実行されます
3. バックグラウンドで1時間ごとに通知をチェック

## ファイル構成

```
shinderera_birthday/
├── birthday_notifier.py    # メインアプリケーション
├── dere.json               # キャラクター誕生日データ
├── settings.json           # ユーザー設定（自動生成）
├── requirements.txt        # Python依存ライブラリ
├── setup.py                # 依存をインストールする簡易スクリプト
├── install.bat             # Windows 用セットアップスクリプト（仮想環境作成 + pip）
├── install.sh              # Unix 系セットアップスクリプト
├── run_notifications_once.py# ワンショットで通知を出すヘルパースクリプト
└── birthday_notifier.bat   # スタートアップ用バッチ（自動生成）
```

## 通知のタイミング

- **7日前**: 📅 誕生日が近づいていることを通知
- **1日前**: 🎂 明日が誕生日であることを通知  
- **当日（0日）**: 🎉 誕生日を祝う通知を表示

各通知は1日1回のみ表示されます（重複はありません）

## トラブルシューティング

### 通知が表示されない場合
1. Pythonの再インストール
2. `pip install --upgrade win10toast` で最新版をインストール
3. Windows 10以上を使用しているか確認

### スタートアップに登録できない場合
1. 管理者権限でコマンドプロンプトを実行
2. `python birthday_notifier.py` でアプリを起動
3. 「💾 スタートアップに登録」をクリック

### settings.jsonが見当たらない場合
1. アプリを初回起動して、キャラクターを選択して保存してください
2. `settings.json`が自動生成されます

## カスタマイズ

### 通知タイミングの変更

[birthday_notifier.py](birthday_notifier.py)の以下の行を編集：

```python
if days == 0 or days == 1 or days == 7:  # この部分を変更
    show_notification(idol["name"], days)
```

例：当日のみ通知
```python
if days == 0:
    show_notification(idol["name"], days)
```

### 誕生日データの更新

[dere.json](dere.json)を編集して、キャラクターのデータを追加・変更できます。

## ライセンス

このプロジェクトは個人利用を想定しています。

## 作成者

山雲＆AI

---

**楽しいアイドル生活を！** 🌟

---

